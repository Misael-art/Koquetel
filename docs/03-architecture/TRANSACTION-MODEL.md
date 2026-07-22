# Transaction and recovery model

Status: normative draft  
Last reviewed: 2026-07-21

## State machine

`discovered → planned → confirmed → staged → applied → verified → committed`

Failure from `staged` onward transitions to `compensating`, then either
`rolled_back` or `recovery_required`. A killed process leaves `interrupted`; the
next mutating command must recover before accepting new mutation.

## Required transaction record

- transaction ID and schema version;
- operation, scope and initiating actor;
- source/target version and source commit where applicable;
- normalized plan hash and required confirmation class;
- ordered steps with precondition, intent, result and compensation;
- owned paths and pre-mutation fingerprints;
- backup references and integrity digests;
- verification evidence;
- terminal state and timestamps.

## Mutation protocol

1. Discover current state without mutation.
2. Validate supported versions and ownership markers.
3. Build canonical plan and hash it.
4. Obtain confirmation required for that exact hash.
5. Acquire scoped lease and revalidate preconditions.
6. Persist transaction intent and fsync it.
7. Build staged artifacts in a private same-filesystem directory.
8. Verify staged artifacts before activation.
9. Back up changed user files and register compensation.
10. Activate using atomic rename/symlink exchange where possible.
11. Verify behavior and ownership.
12. Commit journal state, release lease and prune backups by policy.

## Invariants

- A confirmation cannot authorize a changed plan.
- No compensation removes a path not proven Koquetel-owned or created by the
  active transaction.
- Recovery never guesses between conflicting user and managed state; it stops
  with evidence and a safe manual action.
- Backups are never the sole canonical copy of user-owned data.
- Repeating recovery is idempotent.

## Lease model (v1 local)

The scoped lease (mutation-protocol step 5) is, in v1, a **local single-host
cooperative OFD advisory lock** (`F_OFD_SETLK`) on the lease file — the scope
confirmed by Q-08 (NFS/multi-host excluded from v1). Per `ADR-0011` **Decision A**:
on one host a holder is either alive (keeps the lock) or dead (cannot write), so
split-brain has no local instantiation and **no distributed fence (`G-13`) is
required** for v1. The one residual is a paused/stuck holder (`FM-23`) — a liveness
stall surfaced by `status`/`doctor`, never two concurrent writers.
Distributed/NFS/multi-host fencing (`ADR-0011` **Decision B**) is deferred to a
potential v2 and remains blocked by `G-13`.

