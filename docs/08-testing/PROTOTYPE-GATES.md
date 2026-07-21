# Disposable prototype gates

Status: normative draft — gates specified, prototypes not yet run
Last reviewed: 2026-07-21

Five high-risk assumptions must be proven by *disposable* prototypes before the
matching contracts can be accepted (`FOUNDATION-GOVERNANCE.md §5`). This file
specifies each gate so a prototype can be built, measured and discarded. It does
not implement any prototype and authorizes no product code.

## Disposability contract (applies to every `PT-xx`)

- Runs in an ephemeral directory or container under the session/CI scratch area;
  it never mutates the host, never writes to `/opt`, `/usr`, `/etc` or the user's
  real config, and never installs a service.
- Prototype code is throwaway: it lives outside the default build/runtime graph,
  is never imported by a product module, and never becomes a release artifact
  (`IT-01..IT-04`). It is deleted after evidence capture.
- Only the **evidence** is retained: a dated record (environment, exact commands,
  measured numbers, pass/fail, and the retained artifact path). "It worked" without
  a retained artifact and pinned inputs does not pass (`TRACEABILITY.md` rule).
- A gate `passes` only if every listed criterion is met on the declared
  environment; a single containment or convergence failure fails the gate.
- No PhaseZero/SteamZero path, command or data format is used by any prototype.

## PT-01 — Exclusive cross-process lock under concurrency

- **Gap/req:** G-11, AR-08; concurrency rule in `ARCHITECTURE.md §5`; `E-2002`.
- **Environment:** one Linux host; the local filesystem that will hold the lease
  (and, separately, a repeat on a networked/`tmpfs` filesystem to expose `flock`
  vs `O_EXCL` differences); ≥100 concurrent processes.
- **Input:** N processes each attempt to acquire the single installation-scope
  lease, do a marked critical section (increment a shared counter guarded only by
  the lock), release, and loop for ≥10,000 total contended acquisitions.
- **Injected fault:** kill `-9` the current holder mid-critical-section; a second
  contender must detect the stale lease (owner/pid/lease-expiry) and take over.
- **Expected result:** at most one holder at any instant; the guarded counter
  equals the number of acquisitions exactly; a dead holder's lease is reclaimed
  within the declared timeout without manual cleanup.
- **Evidence artifact:** the run log with per-acquisition holder id, the final
  counter equality assertion, and the takeover timestamp trace.
- **Pass/fail:** 0 mutual-exclusion violations across all acquisitions AND stale
  lease reclaimed within the bound. Any double-hold or lost counter fails.
- **Disposal:** delete the lease dir and prototype binary; retain only the log.

## PT-02 — Journal recovery with a truncated final write

- **Gap/req:** G-11, AR-09; FM-01; `NFR-03`; `SCH-04 JournalEntry`.
- **Environment:** one Linux host; ephemeral journal file; fault harness able to
  truncate the file at an arbitrary byte and to `kill -9` mid-append.
- **Input:** append ≥1,000 well-formed journal entries (sequence + `entryDigest`
  chain), then interrupt an append so the last line is partial; repeat across a
  sweep of truncation offsets (0 bytes … full-record-minus-one).
- **Injected fault:** truncated / partially-flushed final record; also a flipped
  byte in a mid-file record.
- **Expected result:** recovery reads every complete, digest-valid record;
  isolates only the incomplete final record as `incomplete`; converges the
  transaction to old-or-new; a mid-file digest break stops with evidence rather
  than silently continuing. Re-running recovery is idempotent.
- **Evidence artifact:** for each offset, the recovered record count, the isolated
  tail, the terminal state, and a second-run no-op diff.
- **Pass/fail:** across the whole sweep, 0 cases where a torn tail makes earlier
  records unreadable; 100% converge to a terminal state; repeated recovery changes
  nothing. Any silent acceptance of a broken mid-file record fails.
- **Disposal:** delete journals and harness; retain the sweep result table.

## PT-03 — ai-memory concurrency, corruption, export and removal

- **Gap/req:** G-04; EA-01 constraints AC-DUR/AC-CONC/AC-EXP; FM-05, FM-06;
  `SCH-09/SCH-10`; ADR-0004.
- **Environment:** ai-memory at a pinned release, its own data dir under scratch,
  never mounting `$HOME`; a Koquetel-side adapter shim for envelope round-trips.
- **Input & arms:**
  - *Concurrency:* K≥8 concurrent writer clients (in-process and separate
    processes) issue interleaved writes/reads for ≥10,000 operations.
  - *Corruption:* flip bytes in the SQLite file and in the `-wal`, then reopen.
  - *Export:* export a populated scope, import into an empty store, compare.
  - *Removal:* purge a project/scope, then query and inspect on-disk residue.
- **Injected fault:** cross-process write contention; on-disk corruption; process
  kill during a write batch.
- **Expected result:** no lost or torn records and no unhandled `SQLITE_BUSY`
  beyond the retry budget; corruption is detected and fails closed (no silent wrong
  answer) and remains recoverable from the last export; export→import reproduces an
  identical envelope set by digest; purge leaves 0 queryable residue and *reports*
  any physical residue (matches `writer.rs` `PurgeSummary` behavior observed in
  EA-01).
- **Evidence artifact:** operation ledger with per-record digests, the corruption
  detection log, the export/import digest-equality report, and the purge residue
  report.
- **Pass/fail:** concurrency arm 0 lost/corrupt records; corruption arm 0 silent
  wrong reads; export arm 100% digest match; removal arm 0 queryable residue with a
  complete residue report. Any silent data loss fails the gate and blocks
  ai-memory acceptance.
- **Disposal:** delete the ai-memory data dir and shim; retain the four reports.

## PT-04 — Rootless sandbox: mounts, network, resources, secrets, performance

- **Gap/req:** G-05; SR-07, SR-08; FM-11, FM-12; AC-11.
- **Environment:** Podman rootless (primary) and Docker (fallback) on one Linux
  host; a hostile workload image built from pinned inputs.
- **Input:** run a workload that attempts to (a) read non-mounted user paths, (b)
  read host credentials (`~/.ssh`, cloud/env secrets), (c) reach the container
  engine socket, (d) open network connections outside an allowlist, and (e) exceed
  CPU, memory, PID and wall-clock limits; plus a benign build/test workload for the
  performance measurement.
- **Injected fault:** the hostile attempts above, and a resource-exhaustion loop.
- **Expected result:** every escape attempt fails — no non-mounted path read, no
  host credential access, no engine socket, only allowlisted network reached; on a
  limit breach the process tree is terminated and host resources recover; the
  benign workload's overhead (p95 cold start and throughput vs bare execution) is
  measured against a ceiling fixed before implementation.
- **Evidence artifact:** the containment assertion matrix (one row per attempt,
  all denied), the resource-kill trace, and the overhead measurement table.
- **Pass/fail:** 0 containment escapes across the matrix AND measured overhead
  within the fixed ceiling. Any single escape fails, regardless of performance.
- **Disposal:** remove the container, image and mounts; retain the matrix and
  measurements.

## PT-05 — Rust distribution: binary, SQLite, Unix socket, recovery after kill

- **Gap/req:** ADR-0002 prototype gate; NFR-01, NFR-03; `ARCHITECTURE.md` core
  service; peer-credential rule in `CONTRACTS.md`.
- **Environment:** a clean Linux host/container with no system Rust toolchain and
  no prior Koquetel state; the candidate static/user-scoped build.
- **Input:** build the artifact from a pinned source commit; start it; open the
  SQLite state with migrations applied; serve the local API over a Unix socket that
  authenticates by peer credentials; run a mutating transaction.
- **Injected fault:** `kill -9` during the mutating transaction, then restart; and
  a connection attempt from a non-owner user on the socket.
- **Expected result:** the binary runs on the clean host without a system runtime;
  migrations apply and are idempotent; the socket rejects the non-owner; after the
  kill, the next start recovers to old-or-completed state (no silent mix); cold
  start time is measured against a ceiling fixed before implementation.
- **Evidence artifact:** the clean-host run transcript, the migration idempotency
  check, the non-owner rejection log, the post-kill recovery transcript, and the
  cold-start measurement. If distribution friction exceeds the ADR-0002 threshold,
  the evidence must state it so the ADR can be revisited (Python fallback).
- **Pass/fail:** clean-host run + socket owner-only + post-kill convergence all
  hold AND friction is within the ADR-0002 threshold. Otherwise the gate fails and
  ADR-0002 reopens.
- **Disposal:** delete the container and artifact; retain the transcripts and
  measurements.

## Gate ledger

| Gate | Proves | Blocks until pass |
|---|---|---|
| PT-01 | exclusive lock under concurrency (AR-08) | transaction ADR / `M-01` |
| PT-02 | torn-journal recovery (AR-09) | transaction ADR / `M-01` |
| PT-03 | ai-memory durability/concurrency/export/removal (G-04) | ADR-0004 / `M-03` |
| PT-04 | rootless sandbox containment + cost (G-05) | `M-04`, external tool execution |
| PT-05 | Rust distribution + recovery (ADR-0002) | ADR-0002 acceptance / `M-01` |

`FOUNDATION-GOVERNANCE.md §5` requires the three highest-risk of these (PT-01,
PT-02 and PT-03, or PT-04 where external execution ships first) to pass their
documented gates before `READY FOR IMPLEMENTATION`.
