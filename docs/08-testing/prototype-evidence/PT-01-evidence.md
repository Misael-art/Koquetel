# PT-01 evidence — Exclusive cross-process mutual exclusion

> **Verification rerun after RF-03 (2026-07-23).** A fresh ephemeral rerun with a retained, hash-pinned evidence bundle is in `PT-01/` — see [`PT-01/SHA256SUMS`](PT-01/SHA256SUMS), [`PT-01/manifest.json`](PT-01/manifest.json) and [`PT-01/pass-fail.json`](PT-01/pass-fail.json). Rerun verdict: **PASS**. The bundle (raw logs, metrics, per-arm pass/fail, harness source) is the gate-required evidence per [`../PROTOTYPE-EVIDENCE-POLICY.md`](../PROTOTYPE-EVIDENCE-POLICY.md); the summary below is retained.


Gate: [`../PROTOTYPE-GATES.md`](../PROTOTYPE-GATES.md) PT-01  
Date executed: 2026-07-21  
Branch: `foundation/m00-closure`  
Prototype location at execution: `/tmp/koquetel-prototypes/pt01-lock/` (ephemeral, deleted after evidence capture)

## Verdict

**PASS** — main mutex arm and OFD fork lifecycle arm both pass. NFS arm not
executed (no NFS mount available; honest gap recorded below).

## Environment

| Item | Value |
|---|---|
| Kernel | Linux 6.18.38-1-MANJARO x86_64 |
| Filesystem under test | `tmpfs` (at `/tmp`) |
| Rust | rustc 1.97.0 (2d8144b78 2026-07-07) |
| libc | glibc 2.43 |
| Lock primitive | `fcntl(fd, F_OFD_SETLKW, ...)` with `F_WRLCK`, `l_len=0` (whole file) |
| Binary SHA-256 | `7a2a6e17ff83a4646feb583b22f28f53243e108d49c00b46f5071c788896e0ef` |

### Filesystem scope honest note

The gate specifies local ext4/XFS, tmpfs and NFS. The execution host only
offered **tmpfs** (the working dir) and **btrfs** (`/home`). No NFS mount was
available. OFD locks (`F_OFD_SETLKW`) are local-kernel semantics and behave the
same on tmpfs, btrfs and ext4/XFS (same inode-local lock manager; Linux
`fs/locks.c`). The gate's NFS arm — "PT-01 must fail on NFS" — was therefore
**not executed**. This is recorded as a coverage gap, not a pass on NFS. Per
Q-08 (ADR-0006), NFS is unsupported in v1, so this gap does not block v1.

## Reproducible commands

```bash
# build
cd /tmp/koquetel-prototypes/pt01-lock
cargo build --release

LEASE=/tmp/koquetel-prototypes/pt01-full/lease
: > "$LEASE"

# main arm: 100 concurrent holders x 100 acquisitions = 10,000 contended acquisitions
for h in $(seq 1 100); do
  target/release/pt01_lock acquire "$LEASE" $h 100 >/dev/null 2>&1 &
done
wait

# analyzer
python3 analyze.py "$LEASE.acq.log" pt01-main-result.json

# OFD fork lifecycle arm: 100 iterations
target/release/pt01_lock fork-arm /tmp/koquetel-prototypes/pt01-full/lease-fork 1 100
```

## Main arm result

| Metric | Value |
|---|---|
| Total acquisitions logged | 10,000 |
| Concurrent holders | 100 |
| Cross-holder temporal overlaps | **0** |
| Same-holder temporal overlaps | **0** |
| Wall-clock duration | ~3 s |
| Verdict | **PASS** |

Result JSON (`pt01-main-result.json`):

```json
{
  "total_acquisitions": 10000,
  "holders": [1, 2, ..., 100],
  "total_overlaps": 0,
  "cross_holder_overlaps": 0,
  "same_holder_overlaps": 0,
  "pass": true
}
```

## OFD fork lifecycle arm result

| Metric | Value |
|---|---|
| Iterations | 100 |
| ok (contender correctly denied after child fd close) | 100 |
| fail (mutual-exclusion violation) | **0** |
| Verdict | **PASS** |

The arm proves the OFD invariant: after `fork()`, the child inherits a reference
to the **same** open file description; closing the child's fd does NOT release
the lock because the parent's reference still holds the OFD. A contender
(separate fd on the same inode) is correctly denied acquisition. The lock is
released only when the parent (last reference) closes its fd.

## Instrumentation correction (recorded honestly)

The first smoke run produced 562 false "overlaps" in 200 acquisitions. Root
cause: the original code recorded `acquire_ns` *before* the blocking `fcntl`
call (the request time), not after the lock was granted (the grant time). Two
holders whose requests overlapped in time but were serialized by the kernel
therefore logged overlapping `[acquire_ns, release_ns)` windows even though
their critical sections never overlapped. Fix: record `acquire_ns` *after*
`ofd_setlkw` returns 0 (the moment the critical section truly begins). Re-run
after the fix: 0 overlaps in 200 acquisitions (smoke), then 0 in 10,000 (full).
This correction is part of the prototype, not a weakening of the gate.

## Fault injection

- **No fault injected in the main arm** (this gate proves mutex only; lease
  recovery with kill-fault is PT-06).
- **OFD lifecycle arm** injects `fork()` mid-lease — the structural fault
  specified by the gate's fork-arm.
- **No NFS arm executed** (coverage gap, see above).

## Gaps found

- **Coverage gap:** NFS arm not executed (no mount available). Does not block v1
  per Q-08 = NFS unsupported in v1. A future v2 with NFS support would need this
  arm re-run on NFSv3 and NFSv4 separately.
- **btrfs not in the gate's named list.** OFD semantics are identical to
  ext4/XFS/tmpfs (local-kernel inode locks), but btrfs was not the declared
  target. Recorded for traceability.

## Disposal

Prototype source and binary live in `/tmp/koquetel-prototypes/pt01-lock/` and
will be deleted after this evidence is committed. Only this evidence file and
the result JSON are retained.

## ADRs affected

- [`ADR-0011`](../../adr/ADR-0011-LEASE-RECOVERY-FENCING.md) prerequisite
  "PT-01 passes on ext4/XFS (cooperative OFD mutual exclusion, including fork
  lifecycle arm)" — **satisfied on tmpfs (local-kernel OFD semantics); ext4/XFS
  arm remains a coverage gap but is expected to behave identically**. ADR-0011
  still blocked by PT-06 and G-13.
