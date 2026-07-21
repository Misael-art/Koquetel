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

## PT-01 — Exclusive cross-process mutual exclusion

- **Gap/req:** G-11, AR-08; concurrency rule in `ARCHITECTURE.md §5`; `E-2002`.
- **Environment:** one Linux host; tested on **local filesystem (ext4/XFS)**,
  **tmpfs** and **network filesystem (NFS)** separately — flock semantics,
  `O_EXCL` atomicity and lease expiry differ across them and Koquetel must
  document which are supported (see §Filesystem semantics below).
- **Input:** N ≥ 100 concurrent processes each attempt to acquire the single
  installation-scope lease via `O_EXCL` creation + `flock` (or equivalent kernel
  mechanism), do a **read-only marked critical section** (read shared counter),
  release, and loop for ≥10,000 total contended acquisitions.
- **Injected fault:** none in this gate — this gate proves **mutual exclusion
  only**; lease recovery is PT-06.
- **Expected result:** at most one holder at any instant; the shared counter is
  used **only as a read oracle** — its value is never asserted after a
  non-transactional update. The acquisition log is **append-only** per
  acquisition: each successful lock logs `(holder_id, timestamp, lease_path)`
  and no two logs overlap temporally.
- **OFD lifecycle arm (new sub-test, mandatory for ext4/XFS):** repeat the
  same N × 10,000 contention with `fork()` injected mid-lease: after acquiring
  the lock, the process forks. The child inherits a reference to the **same**
  OFD. The child MUST close the lease fd immediately (removing its reference;
  the parent's reference keeps the lock alive), and the parent continues.
  **Expected:** no mutual-exclusion violation despite the fork — the lock
  persists because the parent still holds a reference to the OFD.
  A second variant closes the fd in the parent first (parent releases its
  reference; the child's reference keeps the lock alive) and then the child
  closes — the lock must be released only after **both** references are
  closed. **Expected:** no double-release; the lock is released once when the
  last reference is closed.
- **Evidence artifact:** the per-acquisition log with holder id + start/end
  timestamps and the lease-path owner file at each instant. A script that
  detects temporal overlaps in the log.
- **Pass/fail:** 0 mutual-exclusion violations across all acquisitions (no
  temporal overlap in logs, no concurrent lease file owners). Any double-hold
  fails. The mechanism (`O_EXCL`, `flock` or equivalent) must be identified by
  name and kernel syscall, not as a vague "filesystem lease".
- **Disposal:** delete the lease dir and prototype binary; retain only the log.

### Filesystem semantics

| Filesystem | `O_EXCL` (open with O_CREAT\|O_EXCL) | `flock` advisory | Lease owner visibility | Notes |
|---|---|---|---|---|---|
| Local ext4/XFS | **atomic** on the same node¹ | advisory, released on fd close² | immediate | Baseline behaviour; Koquetel production target. |
| tmpfs | **atomic** on the same node¹ | advisory, released on fd close² | immediate | Volatile; reclaimed on unmount³. Acceptable for ephemeral coordinators. |
| NFS v3/v4 | **not atomic** without `O_EXCL` emulation⁴ | `flock` is emulated via `fcntl`-based byte-range lock (lockd); may not release on unexpected disconnect until lockd timeout⁵ | stale lease may persist beyond NFS lockd timeout⁵ | **Unsupported for v1** (Q-08, G-13). PT-01 must fail on NFS. A distributed fencing protocol or conditional atomic commit primitive is required for any future NFS support. |

**Primary sources:**
¹ `open(2)` man page (Linux man-pages 6.x): `O_EXCL` guarantees exclusive creation
  on local filesystems; `O_EXCL` on NFS relies on remote server support and is
  not atomic without workarounds.
² `flock(2)` man page (Linux man-pages 6.x): advisory, released on close.
³ `tmpfs.txt` (kernel.org, kernel 6.x): tmpfs does not survive unmount.
⁴ NFS man page `nfs(5)` (Linux man-pages 6.x): `O_EXCL` on NFS requires
  `O_EXCL` emulation via context-bearing nonce file; without it the open is not
  atomic.
⁵ NFS man page `nfs(5)` and `lockd(8)` documentation: `flock` on NFS is
  emulated via POSIX `fcntl` byte-range locks managed by `lockd`; unlock on
  client crash depends on `lockd` lease (typically 45s grace).

A claim of "network filesystem support" without PT-01 evidence on that filesystem
is invalid.

## PT-06 — Lease recovery after holder death

- **Gap/req:** G-11, AR-08; supplements PT-01 mutual exclusion with recovery.
- **Environment:** same as PT-01 (local fs, repeated on target filesystems).
- **Input:** same N-process contention harness, but now each critical section
  increments a shared counter **using an atomic/transactional update** (e.g.,
  `fsync`-guarded file increment or SQLite row update). If the counter update
  is not transactional, the gate **does not assert equality** — it can only
  assert fencing.
- **Injected fault:** kill `-9` the current holder mid-critical-section after
  the lock is acquired but before release. A second contender must detect the
  stale lease (owner pid no longer alive, or lease expiry elapsed) and take
  over.
- **Expected result:**
  1. A dead holder's lease is reclaimed within the declared timeout without
     manual cleanup.
  2. The new holder **fences against the old holder**: e.g., it writes a
     fencing token (epoch counter) that any late-arriving old-holder write
     would reject, or the lease mechanism itself (kernel-backed) guarantees
     the old holder cannot write after release.
  3. Recovery time (from death to new-holder acquisition) is measured and
     reported against the declared bound.
  4. **Epoch token validation at journal write (arm):** two sub-cases:
     *a)* after takeover, the prototype writes a journal entry with the *old*
     epoch (simulating a stale-holder write that arrives late), where the old
     epoch's revocation is **provable** (e.g., the new holder's epoch
     increment is persisted before the stale write). **Expected:** the journal
     reader quarantines the stale-epoch entry during recovery (concern 5).
     *b)* same scenario but without provable revocation — the stale write
     arrives concurrently with the epoch increment and there is no evidence
     whether the write preceded or followed revocation. **Expected:** the
     journal reader **preserves** the entry (no simple `leaseEpoch < current`
     discard) because the entry may be legitimate history from the prior
     epoch. The implementation must detect the ambiguity and escalate
     (fail-closed) rather than silently discarding or accepting.
     Together these validate that epoch fencing at the journal level requires
     a revocation-proof protocol (G-13), not just a numeric comparison.
  5. **OFD lifecycle arm (ext4/XFS only):** repeat the kill-fault injection
     with two sub-tests:
     *a) exec with CLOEXEC:* the holder sets `FD_CLOEXEC` on the lease fd,
     then calls `exec()` to a no-op helper. **Expected:** `exec()` closes the
     fd (CLOEXEC), releasing the last reference. The helper runs without the
     lease, and a contender acquires the lock.
     *b) dup survival:* the holder calls `dup()` on the lease fd, then closes
     the original fd. **Expected:** the lock **survives** because the
     duplicate fd still references the same OFD. The contender must not be
     able to acquire the lock. When the duplicate is also closed, the lock is
     released and the contender acquires it.
- **Evidence artifact:** the takeover timestamp trace showing death→detection→
  acquisition→fencing; the fenced-out late-write rejection log (if any); the
  recovery-time distribution; the stale-epoch entry rejection attestation; the
  exec/dup survival log.
- **Pass/fail:** stale lease reclaimed within the bound AND fencing prevents
  old-holder writes from being accepted AND stale-epoch journal entries are
  isolated during recovery. Any split-brain, unbound recovery, or acceptance
  of a stale-epoch entry fails. The counter value after recovery is recorded
  but **not** used as a pass/fail criterion unless its update is proven
  transactional.
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
| PT-06 | lease recovery with fencing (AR-08, G-11) | transaction ADR / `M-01` |

`FOUNDATION-GOVERNANCE.md §5` requires the three highest-risk of these (PT-01,
PT-02 and PT-03, or PT-04 where external execution ships first) to pass their
documented gates before `READY FOR IMPLEMENTATION`. PT-01 and PT-06 together
replace the original combined PT-01: mutual exclusion (PT-01) must pass before
lease recovery (PT-06) is run, and both must pass for the lock contract to be
accepted.
