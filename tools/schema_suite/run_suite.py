#!/usr/bin/env python3
"""Foundation schema-contract suite (SC-01..SC-11) for Koquetel.

FOUNDATION-ONLY, isolated from the product runtime. It uses a pinned Draft
2020-12 validator (`jsonschema`, see requirements.txt) that must NOT enter the
Koquetel runtime dependency graph. It reads the schemas and examples read-only,
proves the contracts, and writes an evidence file `RESULT.json` that
`tools/foundation_lint.py` verifies against the current schema digest.

Run it with the foundation venv's python:
    tools/schema_suite/.venv/bin/python tools/schema_suite/run_suite.py

Exit 0 = all SC tests pass; 1 = a SC test failed; 2 = validator unavailable.
Import-safe: helpers are reused by tools/tests/test_foundation_lint.py.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except Exception as exc:  # noqa: BLE001
    print(f"FATAL: pinned validator unavailable ({exc}). Create the foundation venv: "
          f"python3 -m venv tools/schema_suite/.venv && "
          f"tools/schema_suite/.venv/bin/pip install -r tools/schema_suite/requirements.txt")
    sys.exit(2)

REPO = Path(__file__).resolve().parents[2]
SDIR = REPO / "docs/05-data/schemas"
SCHEMA_FILES = [
    "plan-confirmation.schema.json", "transaction.schema.json",
    "profile-adapter.schema.json", "memory.schema.json",
    "tool-policy.schema.json", "delegation-task.schema.json",
    "event-support.schema.json", "model-routing.schema.json",
    "session.schema.json",
]
TOLERANT = "tolerant-read/event.tolerant.schema.json"
NEEDS_RE = {"host-scoped", "sensitive", "secret-ref", "content"}
ORDER = ["META", "SC-01", "SC-02", "SC-03", "SC-04", "SC-05", "SC-06", "SC-07",
         "SC-08", "SC-09", "SC-10", "SC-11", "SEM"]


def load(p: Path):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def sub_validator(doc: dict, pointer: str) -> Draft202012Validator:
    if not pointer:
        return Draft202012Validator(doc)
    sub = {"$schema": doc["$schema"], "$defs": doc.get("$defs", {}), "$ref": "#" + pointer}
    return Draft202012Validator(sub)


def loci(errors) -> set:
    """The distinct (property-path, keyword) locations an instance violates."""
    return {(tuple(p for p in e.absolute_path if isinstance(p, str)), e.validator)
            for e in errors}


def parse_time(value: str) -> datetime:
    """Parse the RFC 3339 examples into timezone-aware datetimes."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def session_time_order(session: dict) -> bool:
    """SCH-21 temporal ordering, which JSON Schema cannot express."""
    created = parse_time(session["createdAt"])
    activity = parse_time(session["lastActivityAt"])
    expires = parse_time(session["expiresAt"])
    if not created <= activity <= expires:
        return False
    return "endedAt" not in session or parse_time(session["endedAt"]) >= activity


def session_transition(before: dict, after: dict) -> tuple[bool, str]:
    """Check the tested SCH-21 lifecycle/identity invariants only."""
    if before["sessionId"] != after["sessionId"]:
        return False, "sessionId changed"
    if before["actorRef"] != after["actorRef"]:
        return False, "actorRef changed"
    allowed = {
        "active": {"active", "ending", "ended", "expired"},
        "ending": {"ending", "ended", "expired"},
        "ended": {"ended"},
        "expired": {"expired"},
    }
    if after["state"] not in allowed[before["state"]]:
        return False, f"terminal/invalid transition {before['state']} -> {after['state']}"
    if not session_time_order(before) or not session_time_order(after):
        return False, "timestamp order invalid"
    return True, ""


def sc10_walk(node, defs, where, viol):
    """Recursively collect classification violations for one schema subtree."""
    if not isinstance(node, dict):
        return
    for name, sub in (node.get("properties") or {}).items():
        if not isinstance(sub, dict):
            continue
        loc = f"{where}.{name}"
        cls = sub.get("x-classification")
        if cls is None and sub.get("$ref", "").startswith("#/$defs/"):
            cls = defs.get(sub["$ref"].split("/")[-1], {}).get("x-classification")
        if cls is None and "$ref" not in sub:
            viol.append(f"{loc}: missing x-classification")
        elif cls in NEEDS_RE:
            if "x-retention" not in sub:
                viol.append(f"{loc}: {cls} missing x-retention")
            if "x-exportable" not in sub:
                viol.append(f"{loc}: {cls} missing x-exportable")
            if cls == "secret-ref" and sub.get("x-exportable") != "no":
                viol.append(f"{loc}: secret-ref must be x-exportable:no")
            if cls == "content" and sub.get("x-exportable") != "explicit":
                viol.append(f"{loc}: content must be x-exportable:explicit")
        sc10_walk(sub, defs, loc, viol)
    if isinstance(node.get("items"), dict):
        sc10_walk(node["items"], defs, where + "[]", viol)
    for comb in ("oneOf", "anyOf", "allOf"):
        for i, s in enumerate(node.get(comb, []) or []):
            sc10_walk(s, defs, f"{where}({comb}{i})", viol)


def run(sdir: Path = SDIR) -> tuple[dict, list]:
    sdir = Path(sdir)
    ex = sdir / "examples"
    status: dict[str, bool] = {}
    failures: list[str] = []

    def rec(sc, ok, msg=""):
        status[sc] = status.get(sc, True) and ok
        if not ok:
            failures.append(f"{sc}: {msg}")

    # meta-validation
    for name in SCHEMA_FILES + [TOLERANT]:
        try:
            Draft202012Validator.check_schema(load(sdir / name))
        except Exception as exc:  # noqa: BLE001
            rec("META", False, f"{name} not valid Draft 2020-12: {exc}")
    status.setdefault("META", True)

    # SC-01..SC-08
    manifest = load(ex / "manifest.json")
    for ent in manifest["entities"]:
        sc, doc = ent["sc"], load(sdir / ent["schema"])
        v = sub_validator(doc, ent["pointer"])
        if list(v.iter_errors(load(ex / ent["valid"]))):
            rec(sc, False, f"{ent['name']} valid example rejected")
        errs_i = list(v.iter_errors(load(ex / ent["invalid"])))
        if not errs_i:
            rec(sc, False, f"{ent['name']} invalid example ACCEPTED")
            continue
        got, want = loci(errs_i), (tuple(ent["rule"]["path"]), ent["rule"]["keyword"])
        if want not in got:
            rec(sc, False, f"{ent['name']} invalid violates {sorted(got)}, expected {want}")
        elif len(got) != 1:
            rec(sc, False, f"{ent['name']} invalid violates >1 rule: {sorted(got)}")
        status.setdefault(sc, True)

    # SC-09
    c9 = manifest["sc09"]
    strict = Draft202012Validator(load(sdir / c9["strictSchema"]))
    tolerant = Draft202012Validator(load(sdir / c9["tolerantSchema"]))
    known, unknown, major2 = (load(ex / c9[k]) for k in ("knownV1", "unknownField", "major2"))
    rec("SC-09", strict.is_valid(known), "strict rejected a known v1 instance")
    rec("SC-09", any(e.validator == "additionalProperties" for e in strict.iter_errors(unknown)),
        "strict did not reject unknown field via additionalProperties")
    rec("SC-09", (not strict.is_valid(major2)) and (not tolerant.is_valid(major2)),
        "schemaVersion:2 not rejected by both strict and tolerant")
    rec("SC-09", tolerant.is_valid(unknown), "tolerant rejected an unknown optional field")
    rec("SC-09", (strict.is_valid(unknown) is False) and (strict.is_valid(known) is True),
        "admit-for-write gate did not reject the tolerant-only record")

    # SC-10
    viol: list[str] = []
    for name in SCHEMA_FILES:
        doc = load(sdir / name)
        for dn, ds in doc.get("$defs", {}).items():
            sc10_walk(ds, doc.get("$defs", {}), f"{name}:{dn}", viol)
    rec("SC-10", not viol, f"{len(viol)} classification violation(s): {viol[:5]}")

    # SC-11: session lifecycle/handle contract (SCH-21)
    s = manifest["session"]
    sv = Draft202012Validator(load(sdir / s["schema"]))
    if list(sv.iter_errors(load(ex / s["valid"]))):
        rec("SC-11", False, "session valid example rejected")
    for inv in s["invalids"]:
        errs = list(sv.iter_errors(load(ex / inv["file"])))
        if not errs:
            rec("SC-11", False, f"{inv['file']} ACCEPTED")
            continue
        want = (tuple(inv["rule"].get("path", [])), inv["rule"]["keyword"])
        got = loci(errs)
        if want not in got:
            rec("SC-11", False, f"{inv['file']} violates {sorted(got)}, expected {want}")
    sess = load(ex / s["valid"])
    rec("SC-11", session_time_order(sess),
        "session time order must be createdAt <= lastActivityAt <= expiresAt")

    refv = sub_validator(load(sdir / s["schema"]), "/$defs/SessionRef")
    rec("SC-11", refv.is_valid(load(ex / s["sessionRef"]["valid"])),
        "valid SessionRef rejected")
    for inv in s["sessionRef"]["invalids"]:
        errs = list(refv.iter_errors(load(ex / inv["file"])))
        want = (tuple(inv["rule"].get("path", [])), inv["rule"]["keyword"])
        got = loci(errs)
        rec("SC-11", want in got,
            f"{inv['file']} violates {sorted(got)}, expected {want}")

    rec("SC-11", not session_time_order(load(ex / s["timeOrderInvalid"])),
        "out-of-order session timestamps accepted")
    valid_transition = load(ex / s["transitionValid"])
    ok, why = session_transition(valid_transition["before"], valid_transition["after"])
    rec("SC-11", ok, f"valid transition rejected: {why}")
    for key, expected in (
        ("transitionInvalidTerminal", "terminal/invalid transition"),
        ("transitionInvalidExpired", "terminal/invalid transition"),
        ("transitionInvalidId", "sessionId changed"),
        ("transitionInvalidActor", "actorRef changed"),
    ):
        transition = load(ex / s[key])
        ok, why = session_transition(transition["before"], transition["after"])
        rec("SC-11", (not ok) and expected in why,
            f"{key} not rejected for {expected}: {why}")
    status.setdefault("SC-11", True)

    # semantic invariants
    plan = load(ex / manifest["semantic"]["planValid"])
    conf = load(ex / manifest["semantic"]["confirmationValid"])
    rec("SEM", conf["planHash"] == plan["planHash"] and conf["planId"] == plan["planId"]
        and dict(conf, planHash="0" * 64)["planHash"] != plan["planHash"],
        "confirmation.planHash binding (SR-04) failed")
    jval = sub_validator(load(sdir / "transaction.schema.json"), "/$defs/JournalEntry")
    line = json.dumps(load(ex / "journal-entry.valid.json"))
    jsonl = [line, line, line[: len(line) // 2]]
    recov = iso = 0
    for ln in jsonl:
        try:
            recov += 1 if jval.is_valid(json.loads(ln)) else 0
        except json.JSONDecodeError:
            iso += 1
    rec("SEM", recov == 2 and iso == 1, f"torn-tail recovery recovered={recov} isolated={iso}")

    return status, failures


def main() -> int:
    status, failures = run()
    for k in ORDER:
        print(f"  {k}: {'PASS' if status.get(k, False) else 'FAIL'}")
    for f in failures:
        print("  ! " + f)
    passed = not failures
    print(f"\nschema-suite: {'ALL PASS' if passed else 'FAILURES'} "
          f"({sum(1 for k in ORDER if status.get(k))}/{len(ORDER)} checks)")

    sha = hashlib.sha256()
    for name in SCHEMA_FILES + [TOLERANT]:
        sha.update((SDIR / name).read_bytes())
    result = {
        "passed": passed,
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "validator": {"engine": "jsonschema", "draft": "2020-12"},
        "schemaSha256": sha.hexdigest(),
        "checks": {k: bool(status.get(k, False)) for k in ORDER},
        "exampleCount": len(list((SDIR / "examples").glob("*.json"))) - 1,
        "failures": failures,
    }
    (Path(__file__).resolve().parent / "RESULT.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
