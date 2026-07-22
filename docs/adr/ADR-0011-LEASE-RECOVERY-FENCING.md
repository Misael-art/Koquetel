# ADR-0011 — Lease recovery and fencing

Status: proposed — owner decisions Q-03/Q-08 resolved (ADR-0006); still depends on prototype gates PT-01, PT-06 and gap G-13
Date: 2026-07-21

## Context

`ARCHITECTURE.md §5` defines one mutation lease per installation scope and one
workspace lease per repository. The lease protects the canonical state database
and the journal from concurrent writers. If the lease holder dies (process kill,
machine crash, network partition), the lease must be reclaimed and the new holder
must fence the old one to prevent stale writes from corrupting state.

The current architecture document specifies the lease *existence* but not the
*recovery protocol*. Without an accepted recovery strategy:

- a dead holder can leave the installation permanently locked (manual recovery);
- two holders can simultaneously believe they own the lease if fencing is weak
  (split-brain);
- journal recovery (PT-02) can converge the transaction, but without fencing the
  recovered state can be overwritten by a late-arriving old-holder write.

### Fencing taxonomy

"Fencing" in the lease-recovery literature conflates six distinct concerns that
this ADR separates:

1. **Mutual exclusion** — at most one writer holds the lease.
2. **Lease (liveness) detection** — a contender determines whether the lease is
   alive or stale.
3. **Takeover** — a contender becomes the new lease holder.
4. **Fence the obsolete writer at commit** — the storage layer rejects a write
   from a stale holder.
5. **Journal recovery classification** — classify committed, prepared, aborted
   and quarantined records using revocation/commit evidence.
6. **External side-effect fencing** — side effects outside the journal are
   rendered safe after takeover.

| Concern | OFD (local) | Epoch guard | External mech. |
|---|---|---|---|---|
| 1. Mutual exclusion | cooperative advisory (read/write not prevented) | epoch alone does not prevent concurrent writes | — |
| 2. Lease detection | auto-release on close of last OFD reference | heartbeat epoch polling | — |
| 3. Takeover | last OFD reference must be released first | epoch increment | — |
| 4. Fence at commit | not provided (advisory lock does not prevent I/O) | token validated atomically with commit | — |
| 5. Journal classification | out of scope of lock | `leaseEpoch` as evidence for commit/revocation decision | — |
| 6. External effects | not covered | not covered | idempotency keys / compensation |

OFD is a **cooperative advisory** mechanism. A live process that ignores the
lock protocol can still read and write the protected file. The lock only
prevents another **cooperating** process from acquiring the same lock — it does
not fence I/O. Concern 4 (fence at commit) is NOT provided by OFD; it requires
the epoch guard and even then depends on a conditional atomic commit primitive
the filesystem may not provide (G-13). Concern 5 classifies journal records
using epoch evidence but cannot discard entries based on a simple numeric
comparison (G-13). Concern 6 is **out of scope** for lease fencing — see
*Unfenced external effects* below.

## Options considered

### 1. Cooperative advisory lease (flock / OFD)

Use `flock` (BSD advisory) or `OFD` (open file description, Linux 3.15+) on the
lease file. The kernel releases the lock when the last open reference to the
OFD is closed — process death closes all fds, so the lock is released on death.
The lock is **advisory**: a live process that ignores the protocol can still
read and write the protected resource.

- **Pro:** simple, proven, no fencing token needed for local cooperative processes.
- **Con:** NOT available on NFS (flock is emulated via lockd byte-range locks;
  OFD is local only); cross-machine recovery needs a timeout-based protocol;
  does not prevent I/O from a non-cooperative process.
- **Fencing:** not provided. OFD gives mutual exclusion among cooperating
  processes only; it does not fence reads or writes.

### 2. Lease file with epoch counter

A shared lease file contains an epoch counter. On takeover the new holder
increments the epoch and writes its PID + timestamp. The old holder (if alive)
checks the epoch before any mutation — if its epoch is stale it halts.

- **Claimed advantage (rejected):** "works on any filesystem including NFS" —
  the epoch counter alone does **not** prevent split-brain on NFS because a
  killed holder cannot check, and a live partition-isolated holder ignores the
  counter. Mutual exclusion on NFS requires a kernel or protocol mechanism,
  which the epoch counter does not provide.
- **Claimed advantage (rejected):** "kernel-level I/O error on stale fd" —
  OFD/flock are advisory locks; they do **not** produce I/O errors on a stale
  fd. A process that ignores the lock protocol can read and write freely.
- **Con:** requires old-holder cooperation for the check (a killed holder cannot
  check). Without a kernel I/O error (which does not exist) or a journal-side
  guard, the epoch check is purely cooperative.
- **Fencing:** not provided. The epoch guard is a cooperative checkpoint that
  a stale holder can ignore.

### 3. Hybrid: OFD/flock for local, epoch-fencing journal guard for all

Use OFD lease for local processes (implicit release + fast takeover). Additionally
journal every mutation record with the current epoch.

- **Claimed advantage (rejected for v1):** "covers both local and NFS without
  protocol negotiation" — NFS is **unsupported for v1** (Q-08, G-13). The epoch
  guard alone cannot distinguish a legitimate committed entry from a stale write
  (see *Journal entry states* below). A cross-filesystem fencing invariant
  requires a revocation-proof epoch protocol, not a simple numeric comparison.
- **Pro:** journal is the single source of truth for write ordering; epoch in
  entry provides recovery-time evidence (concern 5 candidate).
- **Con:** more complex; requires epoch in every journal entry (adds ~8 bytes per
  record); the simple `leaseEpoch < current` discard rule is invalid.

### 4. No fencing, rely on journal idempotency

The journal uses an exactly-once strategy: all operations are idempotent. A
late-arriving write from a dead holder that somehow executes after takeover will
produce a correct result because the operation is replayed or ignored.

- **Pro:** conceptually simplest.
- **Con:** idempotency is hard to guarantee in the presence of time-of-check to
  time-of-use windows and cross-record constraints; a deleted-then-recreated
  resource may not be idempotent. Real-world idempotency proofs are hard.
  Rejected as insufficiently defensible.

## Candidate direction (blocked by G-13 / PT-06)

Option 3 (hybrid OFD/flock + epoch journal guard) is the most promising
direction, but a definitive decision is **blocked** until G-13 and PT-06
provide evidence that journal-scoped post-hoc isolation (concern 5) is
sufficient for Koquetel's workloads, or that a conditional atomic commit
primitive can be made available.

The conceptual model below is a candidate; each component must be validated
by the corresponding prototype gate before the decision is accepted.

- **Local filesystems (ext4/XFS):** the lease is an OFD lock (`F_OFD_SETLK`,
  Linux 3.15+) on the lease file. The lock is advisory — it prevents
  cooperating processes from acquiring the same lock but does not prevent a
  non-cooperative process from reading or writing. The lock is released when
  the last open file description reference is closed (process death closes all
  fds, releasing the lock). Takeover by a contender requires that the current
  holder's last reference to the OFD has been released; there is no timeout or
  expiry embedded in OFD.
- **Journal entry states (all filesystems):** every journal entry carries a
  `leaseEpoch` field recording the epoch under which it was produced. The
  journal defines four conceptual states:
  1. **prepared** — entry written and fsynced, but commit not yet confirmed;
  2. **committed** — entry confirmed as the final decision for its transaction;
  3. **aborted / quarantined** — entry invalidated (epoch revoked or
     compensating entry written);
  4. **recovered** — entry identified by recovery as the consistent state
     after a crash.
  A committed entry from a prior epoch is **legitimate history** — it must not
  be discarded just because `entry.leaseEpoch < currentLeaseEpoch`. An entry
  may only be rejected during recovery if there is evidence that it was
  produced **after** its epoch was revoked, or that it never reached a valid
  commit state (e.g., torn tail per PT-02). Without such evidence the journal
  must preserve the entry.
- **Journal classification (concern 5):** during recovery, entries whose epoch
  was revoked (proven by a successor epoch counter that the writer could not
  have observed) may be quarantined. This requires a protocol that proves
  the writer's epoch was stale **before** the entry was written — not just
  that the epoch number is lower. The current SCH-04 schema does not carry
  enough information for this proof; a design extension (e.g., a
  `commitTimestamp` or `revocationNonce`) is deferred to the transaction ADR
  and recorded in G-13. Until that proof exists, the simple `leaseEpoch <
  currentEpoch` filter is insufficient and MUST NOT be used to discard entries.
- **NFS position (v1 unsupported/proposed):** NFS is placed as
  **unsupported for v1**. The fallback is documented as research only:
  - On NFSv3, `flock` is emulated via lockd byte-range locks with a
    default grace timeout of approximately 45 seconds. There is no
    kernel-enforced lock release on client disconnect.
  - NFSv4 integrates locking into the protocol with lease-based recovery,
    but the lease period (typically 90 s) is too long for Koquetel's
    takeover latency requirements, and OFD locks are not available.
  - A hybrid heartbeat + epoch counter does not provide mutual exclusion:
    a stale holder that is still alive (network partition, not crash) can
    continue writing despite the new holder's epoch increment. The
    heartbeat and the kernel lock are independent mechanisms; combining
    them does not produce an atomic fencing operation.
  - NFS support for v1 would require either a proven distributed fencing
    protocol (beyond the scope of this ADR) or a conditional atomic
    commit primitive (G-13). **Owner decision Q-08** will determine whether
    NFS commit-level fence is required for a future v2. PT-01 and PT-06
    must not claim NFS coverage until the distributed fencing solution is
    proven (G-13, Q-08).
- **Epoch allocation (replaces formula from ADR-0010 draft):** monotonically
  increasing 64-bit integer sourced from a **serialized counter** stored in the
  authoritative storage (canonical state DB or lease file with an atomic
  compare-and-swap). The old `(timestamp_ms << 16) | (pid & 0xFFFF)` formula
  is **rejected** because PID can wrap, timestamp-ms resolution can collide on
  fast machines, and the hybrid does not guarantee monotonicity — all of which
  invalidate epoch-based fencing (concern 4). The serialized counter is
  incremented on every successful lock acquisition and persists across restarts.
- **OFD lifecycle invariants:** an OFD lock (`F_OFD_SETLK`) is bound to the
  **open file description**, not to a specific fd number or process:
  - `fork()` — child inherits a copy of the parent's fd table; both parent and
    child hold references to the **same** OFD. The lock is not duplicated — it
    persists while any reference remains open. The implementation MUST close
    the lease fd in the child immediately after fork so that the child does not
    inadvertently hold the lease open. PT-01 validates that mutual exclusion
    is preserved after fork.
  - `exec()` — if `FD_CLOEXEC` is set (the lease fd MUST set it), the fd is
    closed by the kernel during `exec()`. If no other fd references the same
    OFD, the lock is released. PT-06 validates that the lock does not survive
    across exec when CLOEXEC is set.
  - `dup()` / `dup2()` — creates a new fd referencing the **same** OFD.
    Closing one of the fds does **not** release the lock because the other fd
    still references the OFD. The lock is released only when the **last**
    fd referencing the OFD is closed. The implementation MUST track that a
    single close does not release the lock prematurely.
  - The lock is released on close of the last fd reference to the OFD, not on
    process death per se — death triggers fd closure via exit, which closes
    all fds. The effect is the same for a single-process holder but differs
    when fds are shared via fork or dup.
  - These invariants are explicitly tested by PT-01 (mutex after fork with
    immediate child fd close) and PT-06 (OFD lifecycle arm covering dup
    survival and exec with CLOEXEC).

## Consequences

| Positive | Negative / risk |
|---|---|
| OFD provides zero-cost cooperative mutual exclusion on ext4/XFS (production target) | OFD is advisory only — does not prevent I/O from a non-cooperative process; code path differs on macOS (flock) |
| Epoch in journal provides recovery-time epoch evidence (concern 5 only) | Adds 8 bytes per journal entry; the simple `leaseEpoch < current` filter is rejected (G-13) — a revocation-proof design is needed |
| Cooperative mutual exclusion on local fs is well-understood | NFS is **unsupported for v1** (Q-08, G-13); the NFS fallback documented in this ADR is research only and must not be relied upon without a proven distributed fencing protocol |
| PT-01 + PT-06 validate the candidate direction | Recovery-time bound is prototype-dependent; PT-06 cannot validate NFS fencing until G-13 is resolved |

### Unfenced external effects

The epoch/journal fencing (concern 5) covers only journal entries. It does **not
automatically** cover:

- Direct filesystem writes outside the journal (e.g., writing a config file as
  a side effect).
- External database mutations (e.g., SQLite file that is not part of the
  Koquetel journal).
- Tool invocation side effects (e.g., `git commit` performed by a tool call).
- Remote API invocations (e.g., a provider endpoint).
- IDE / CLI state changes (e.g., VS Code settings written by an adapter).
- Child process output (e.g., stdout from a sandboxed command).

These require a **per-effect idempotency key** or a **compensating transaction**
recorded in the journal before the external call. The lease epoch provides the
authority context for the token, but the fencing invariant itself must be
enforced by the effect receiver (e.g., the remote API must accept and enforce
the idempotency key). Defining the idempotency-key protocol is deferred to a
future ADR; this ADR records the gap.

## Prerequisites for acceptance

- PT-01 passes on ext4/XFS (cooperative OFD mutual exclusion, including fork
  lifecycle arm).
- PT-06 passes with kill-fault injection (local OFD path only; NFS path is
  research-only and must not gate acceptance).
- G-13 resolved: either journal-scoped post-hoc isolation (concern 5) is proven
  sufficient, or a conditional atomic commit primitive (concern 4) is made
  available for the target filesystems.
- ~~Owner decisions on Q-03 (supported hosts) and Q-08 (NFS commit-level fence
  requirement)~~ — **both closed 2026-07-21 (ADR-0006)**: Q-03 = Linux first,
  WSL next; Q-08 = NFS unsupported in v1. The local-fs scope of this ADR is
  therefore confirmed; any future NFS/multi-host support requires reopening
  Q-08 and resolving G-13.

## References

- `ARCHITECTURE.md §5` — concurrency model requiring the lease.
- `docs/08-testing/PROTOTYPE-GATES.md` PT-01 (mutual exclusion) and PT-06 (lease
  recovery / fencing).
- Linux `fcntl(2)` man page: `F_OFD_SETLK` (open file description locks).
- `sch: SCH-04 JournalEntry` schema where `leaseEpoch` would be added
  (backward-compatible optional field).
- `EA-02` AC-NO-LOCK: RTK has no locking; Koquetel implements its own.
- `G-13` — conditional atomic commit primitive for TOCTOU-safe fencing on
  filesystems that do not provide it natively.
- The six-concern fencing taxonomy used in this ADR is Koquetel's own
  analytical decomposition; it is not attributed to an external publication.
