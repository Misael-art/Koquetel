#!/usr/bin/env python3
"""PT-06 persisted-journal and OFD recovery harness (NON-PRODUCTION)."""
from __future__ import annotations

import csv
import fcntl
import hashlib
import json
import os
import signal
import sqlite3
import struct
import subprocess
import sys
import time
from pathlib import Path

LOCK_FMT = "hhqqi"
F_WRLCK = 1
F_UNLCK = 2


def ofd(fd: int, blocking: bool) -> bool:
    cmd = fcntl.F_OFD_SETLKW if blocking else fcntl.F_OFD_SETLK
    flock = struct.pack(LOCK_FMT, F_WRLCK, os.SEEK_SET, 0, 0, 0)
    try:
        fcntl.fcntl(fd, cmd, flock)
        return True
    except BlockingIOError:
        return False


def unlock(fd: int) -> None:
    flock = struct.pack(LOCK_FMT, F_UNLCK, os.SEEK_SET, 0, 0, 0)
    fcntl.fcntl(fd, fcntl.F_OFD_SETLK, flock)


def append_record(path: Path, record: dict, previous: str | None) -> str:
    core = dict(record, previousDigest=previous)
    encoded = json.dumps(core, sort_keys=True, separators=(",", ":")).encode()
    digest = hashlib.sha256(encoded).hexdigest()
    line = json.dumps(dict(core, entryDigest=digest), sort_keys=True, separators=(",", ":"))
    with path.open("ab", buffering=0) as handle:
        handle.write(line.encode() + b"\n")
        os.fsync(handle.fileno())
    return digest


def read_journal(path: Path) -> list[dict]:
    records: list[dict] = []
    previous = None
    with path.open("rb") as handle:
        for line_number, raw in enumerate(handle, 1):
            try:
                record = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"FAIL_CLOSED invalid JSON at line {line_number}") from exc
            digest = record.pop("entryDigest")
            encoded = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
            if hashlib.sha256(encoded).hexdigest() != digest:
                raise RuntimeError(f"FAIL_CLOSED digest mismatch at line {line_number}")
            if record["previousDigest"] != previous:
                raise RuntimeError(f"FAIL_CLOSED chain mismatch at line {line_number}")
            record["entryDigest"] = digest
            records.append(record)
            previous = digest
    return records


def recover(journal: Path, current_epoch: int) -> dict:
    records = read_journal(journal)
    revocations: dict[int, int] = {
        row["revokedEpoch"]: row["sequence"]
        for row in records if row["kind"] == "revocation"
    }
    classes = []
    for row in records:
        if row["kind"] != "mutation":
            continue
        if row["epoch"] == current_epoch:
            classification = "Valid"
        elif row["epoch"] < current_epoch and row.get("orderingDomain") != "journal":
            classification = "Escalate"
        elif row["epoch"] in revocations and row["sequence"] > revocations[row["epoch"]]:
            classification = "Quarantine"
        elif row["epoch"] in revocations and row["sequence"] < revocations[row["epoch"]]:
            classification = "Preserve"
        else:
            classification = "Escalate"
        classes.append({
            "sequence": row["sequence"],
            "epoch": row["epoch"],
            "payload": row["payload"],
            "classification": classification,
        })
    counts = {name: sum(item["classification"] == name for item in classes)
              for name in ("Preserve", "Quarantine", "Escalate", "Valid")}
    return {
        "currentEpoch": current_epoch,
        "recordCount": len(records),
        "classifications": classes,
        "counts": counts,
        "recoveryDisposition": "FAIL_CLOSED" if counts["Escalate"] else "CONTINUE",
    }


def initialize(db: Path) -> None:
    with sqlite3.connect(db) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=FULL")
        conn.execute("CREATE TABLE state(id INTEGER PRIMARY KEY CHECK(id=1), current_epoch INTEGER NOT NULL, counter INTEGER NOT NULL)")
        conn.execute("INSERT INTO state VALUES(1, 0, 0)")


def takeover(db: Path) -> tuple[int, int]:
    with sqlite3.connect(db, isolation_level=None) as conn:
        conn.execute("PRAGMA synchronous=FULL")
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("UPDATE state SET current_epoch=current_epoch+1, counter=counter+1 WHERE id=1")
        epoch, counter = conn.execute("SELECT current_epoch, counter FROM state WHERE id=1").fetchone()
        conn.execute("COMMIT")
        return epoch, counter


def holder_mode(lease: Path, ready: Path) -> None:
    fd = os.open(lease, os.O_RDWR | os.O_CREAT, 0o600)
    ofd(fd, True)
    ready.write_text(str(os.getpid()))
    with ready.open("rb") as handle:
        os.fsync(handle.fileno())
    while True:
        signal.pause()


def try_mode(lease: Path) -> int:
    fd = os.open(lease, os.O_RDWR | os.O_CREAT, 0o600)
    acquired = ofd(fd, False)
    if acquired:
        unlock(fd)
    os.close(fd)
    print("ACQUIRED" if acquired else "BLOCKED")
    return 0 if acquired else 3


def kill_cycles(script: Path, db: Path, lease: Path, out: Path, run: Path) -> None:
    rows = []
    for cycle in range(1, 21):
        ready = run / f"ready-{cycle}"
        child = subprocess.Popen([sys.executable, str(script), "holder", str(lease), str(ready)])
        deadline = time.monotonic() + 5
        while not ready.exists():
            if time.monotonic() > deadline:
                raise RuntimeError("holder did not report lock acquisition")
            time.sleep(0.001)
        killed_at = time.time_ns()
        os.kill(child.pid, signal.SIGKILL)
        child.wait(timeout=5)
        fd = os.open(lease, os.O_RDWR | os.O_CREAT, 0o600)
        ofd(fd, True)
        acquired_at = time.time_ns()
        epoch, counter = takeover(db)
        unlock(fd)
        os.close(fd)
        rows.append({
            "cycle": cycle,
            "holder_pid": child.pid,
            "exit_code": child.returncode,
            "killed_at_ns": killed_at,
            "reclaimed_at_ns": acquired_at,
            "recovery_us": (acquired_at - killed_at) // 1000,
            "epoch": epoch,
            "counter": counter,
        })
    with out.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def ofd_lifecycle(script: Path, lease: Path) -> dict:
    # CLOEXEC: child inherits the descriptor at fork, then exec closes it. Parent
    # closes its copy immediately, so the lock must be acquirable while sleep runs.
    fd = os.open(lease, os.O_RDWR | os.O_CREAT, 0o600)
    ofd(fd, True)
    os.set_inheritable(fd, False)
    child = subprocess.Popen(["/bin/sleep", "0.2"], close_fds=False)
    os.close(fd)
    time.sleep(0.03)
    cloexec_probe = subprocess.run(
        [sys.executable, str(script), "try", str(lease)],
        capture_output=True, text=True, check=False,
    )
    child.wait()

    # dup: closing the original leaves the same OFD alive through the duplicate.
    fd = os.open(lease, os.O_RDWR | os.O_CREAT, 0o600)
    ofd(fd, True)
    duplicate = os.dup(fd)
    os.close(fd)
    held_probe = subprocess.run(
        [sys.executable, str(script), "try", str(lease)],
        capture_output=True, text=True, check=False,
    )
    os.close(duplicate)
    released_probe = subprocess.run(
        [sys.executable, str(script), "try", str(lease)],
        capture_output=True, text=True, check=False,
    )
    return {
        "cloexec": {
            "probe": cloexec_probe.stdout.strip(),
            "exitCode": cloexec_probe.returncode,
            "pass": cloexec_probe.stdout.strip() == "ACQUIRED",
        },
        "dup": {
            "whileDuplicateOpen": held_probe.stdout.strip(),
            "afterDuplicateClose": released_probe.stdout.strip(),
            "pass": held_probe.stdout.strip() == "BLOCKED"
                    and released_probe.stdout.strip() == "ACQUIRED",
        },
    }


def run(out: Path, run_dir: Path) -> None:
    script = Path(__file__).resolve()
    db, lease, journal = run_dir / "state.db", run_dir / "lease", run_dir / "journal.jsonl"
    initialize(db)
    kill_cycles(script, db, lease, out / "kill-reclaim.csv", run_dir)
    with sqlite3.connect(db) as conn:
        current_epoch, counter = conn.execute(
            "SELECT current_epoch, counter FROM state WHERE id=1").fetchone()

    previous = None
    previous = append_record(journal, {
        "sequence": 1, "kind": "mutation", "epoch": current_epoch - 1,
        "orderingDomain": "journal", "payload": "committed-before-revocation",
    }, previous)
    previous = append_record(journal, {
        "sequence": 2, "kind": "revocation", "epoch": current_epoch,
        "revokedEpoch": current_epoch - 1, "orderingDomain": "journal",
        "payload": "takeover-revokes-prior-epoch",
    }, previous)
    previous = append_record(journal, {
        "sequence": 3, "kind": "mutation", "epoch": current_epoch - 1,
        "orderingDomain": "journal", "payload": "stale-after-revocation",
    }, previous)
    previous = append_record(journal, {
        "sequence": 4, "kind": "mutation", "epoch": current_epoch - 2,
        "orderingDomain": "unproven", "payload": "ambiguous-cross-domain-order",
    }, previous)
    append_record(journal, {
        "sequence": 5, "kind": "mutation", "epoch": current_epoch,
        "orderingDomain": "journal", "payload": "current-epoch-valid",
    }, previous)
    recovery = recover(journal, current_epoch)
    (out / "journal.jsonl").write_bytes(journal.read_bytes())
    (out / "recovery-report.json").write_text(json.dumps(recovery, indent=2) + "\n")
    lifecycle = ofd_lifecycle(script, lease)
    (out / "ofd-lifecycle.json").write_text(json.dumps(lifecycle, indent=2) + "\n")
    state = {
        "currentEpoch": current_epoch,
        "transactionalCounter": counter,
        "expectedCounter": 20,
        "databaseJournalMode": "wal",
        "databaseSynchronous": "FULL",
    }
    (out / "state-report.json").write_text(json.dumps(state, indent=2) + "\n")
    print(json.dumps({"state": state, "recovery": recovery, "ofd": lifecycle}, sort_keys=True))


def main() -> int:
    mode = sys.argv[1]
    if mode == "holder":
        holder_mode(Path(sys.argv[2]), Path(sys.argv[3]))
        return 0
    if mode == "try":
        return try_mode(Path(sys.argv[2]))
    if mode == "run":
        run(Path(sys.argv[2]), Path(sys.argv[3]))
        return 0
    raise SystemExit("usage: pt06.py run OUT RUN | holder LEASE READY | try LEASE")


if __name__ == "__main__":
    raise SystemExit(main())
