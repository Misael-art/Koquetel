# PT-06 evidence — Lease recovery after holder death (and fencing)

## Current canonical rerun

The canonical R2 rerun is [`PT-06-R2/`](PT-06-R2/) with integrity index
[`PT-06-R2/SHA256SUMS`](PT-06-R2/SHA256SUMS). Its machine-derived verdict is
**PASS** for the v1 local model: 20/20 SIGKILL/OFD reclaims, maximum recovery
7,581 µs, transactional counter=20 and epoch=20, and a physically persisted
journal re-derived `Preserve=1`, `Quarantine=1`, `Escalate=1`, `Valid=1` with
fail-closed ambiguity. Exec+CLOEXEC and dup survival passed. Distributed/NFS
G-13 was not simulated and remains deferred. See
[`metrics.json`](PT-06-R2/metrics.json) and
[`pass-fail.json`](PT-06-R2/pass-fail.json).

## Historical record

> **HISTORICAL — SUPERSEDED; NOT CANONICAL FOR CURRENT VERDICT.** The earlier
> in-memory classifier narrative and its timings below are preserved only for
> history.

> **Verification rerun after RF-03 (2026-07-23).** A fresh ephemeral rerun with a retained, hash-pinned evidence bundle is in `PT-06/` — see [`PT-06/SHA256SUMS`](PT-06/SHA256SUMS), [`PT-06/manifest.json`](PT-06/manifest.json) and [`PT-06/pass-fail.json`](PT-06/pass-fail.json). Rerun verdict: **PASS**. The bundle (raw logs, metrics, per-arm pass/fail, harness source) is the gate-required evidence per [`../PROTOTYPE-EVIDENCE-POLICY.md`](../PROTOTYPE-EVIDENCE-POLICY.md); the summary below is retained.


Gate: [`../PROTOTYPE-GATES.md`](../PROTOTYPE-GATES.md) PT-06
Date executed: 2026-07-22
Branch: `foundation/m00-closure`
Prototype location: `/tmp/koquetel-prototypes/pt06/` (ephemeral, deleted after evidence capture)

## Verdict

**PASS** for the PT-06 gate: OFD-based recovery reclaims every dead lease within
the bound; the OFD lifecycle (exec+CLOEXEC / dup) behaves as specified; and the
epoch journal classifier correctly preserves legitimate prior-epoch history,
quarantines provably-stale writes, and **escalates (fail-closed)** ambiguous ones.
PT-06 validates the classification *logic*; it does **not** close `G-13` (a
revocation-proof / conditional-atomic-commit primitive for the general race), so
`ADR-0011` remains **proposed** (see below).

## Environment

| Item | Value |
|---|---|
| Kernel | Linux 6.18.38-1-MANJARO x86_64 |
| Filesystem under test | `tmpfs` (`/tmp`) — local-kernel OFD semantics (same class as ext4/XFS) |
| Rust (build only) | rustc 1.97.0 |
| Lock primitive | `fcntl(F_OFD_SETLK / F_OFD_SETLKW)` `F_WRLCK`, `l_len=0` (whole file) |
| Binary SHA-256 | `33056b2e89b68de51cbfba66ba3c3efab3908cab33c1fa8d55f5c18f2c25ea0d` |

### Declared bound (fixed before running)

- **Recovery bound:** a dead holder's lease must be reclaimed by a contender in
  **< 1000 ms** without manual cleanup.

## Reproducible commands

```bash
cd /tmp/koquetel-prototypes/pt06
cargo build --release
bash drive.sh
```

## Results

| Arm | Result | Verdict |
|---|---|---|
| Fence classifier — legit prior-epoch history | `Preserve` (not discarded) | **PASS** |
| Fence classifier — provably-stale late write | `Quarantine` | **PASS** |
| Fence classifier — ambiguous concurrent write | `Escalate` (fail-closed) | **PASS** |
| Fence classifier — current-epoch entry | `Valid` | **PASS** |
| Transactional counter equality (8×1250=10,000 contended) | `counter=10000 epoch=10000` (exact) | **PASS** |
| Recovery: dead lease reclaimed | **20/20**, avg 4 ms, max 8 ms (bound 1000 ms) | **PASS** |
| OFD exec + CLOEXEC releases | `try = ACQUIRED` after exec | **PASS** |
| OFD dup survival | held via dup → `BLOCKED`; after last close → `ACQUIRED` | **PASS** |

## The fencing point (ADR-0011 / G-13)

The classifier makes the decision ADR-0011 requires and proves the naive rule is
unsafe:

- A committed entry from a **prior** epoch whose sequence is **before** the
  revocation is *legitimate history* → `Preserve`. The naive `leaseEpoch <
  current` discard would wrongly delete it.
- An entry whose sequence is **after** the epoch's revocation was persisted is
  *provably stale* → `Quarantine`.
- An entry with **no ordering proof** relative to the revocation is *ambiguous* →
  `Escalate` (fail-closed for review), never silently discarded or accepted.

This demonstrates the *decision logic* is sound **given** ordering evidence. It
does **not** produce that evidence atomically under a real distributed race —
that is exactly `G-13` (a conditional atomic commit / revocation-proof protocol,
plus an SCH-04 extension carrying the ordering evidence). PT-06 therefore
validates concern 5 (journal classification) but leaves concern 4 (fence at
commit) open, consistent with ADR-0011's own analysis.

## Fault injection

- `kill-holder`: acquires the OFD write lock, then raises `SIGKILL` on itself
  while holding it. Process death closes all fds → the OFD lock is released by
  the kernel. A concurrent `acquire-wait` (blocking `F_OFD_SETLKW`) is granted.
- 20 independent kill/reclaim cycles measured.

## Honest coverage notes

- **Recovery time includes contender launch overhead** (a few ms); the OFD
  release itself is immediate on process death. The measured max (8 ms) is far
  under the 1000 ms bound; the assertion that matters — *every* dead lease was
  reclaimed with no permanent lock and no manual cleanup — holds 20/20.
- **The fence classifier is a deterministic unit-level test** of the
  classification logic, not a live multi-host race. Proving the ordering evidence
  can be produced atomically on the target filesystems is `G-13`, still open.
- **Filesystem:** tmpfs (local-kernel OFD), identical lock-manager semantics to
  ext4/XFS. NFS not tested (unsupported in v1, Q-08).
- **Epoch allocation:** the prototype uses a serialized DB-backed counter
  (monotonic), matching ADR-0011's rejection of the `(timestamp<<16)|pid` formula.

## Disposal

Prototype source, target/ and `drive.sh` live only in
`/tmp/koquetel-prototypes/pt06/` and are deleted after this evidence is committed.

## ADRs affected

- **ADR-0010 (session lifecycle) — corrected by RF-02:** PT-01, PT-02 and PT-06
  prerequisites are met, and recovery with no lost mutations is shown (counter
  equality). The v1 id is a single **random 128-bit** format (32 lowercase hex);
  UUIDv7 is rejected for v1 — **no UUIDv7-benefit residual**. Ready for owner
  ratification. ~~Original: one residual remains — the UUIDv7-benefit justification
  (ADR-0010 §3).~~
- **ADR-0011 (lease recovery/fencing):** PT-01 and **PT-06** met; the OFD path and
  journal-classification logic are validated. **G-13 remains open** (revocation-proof
  fence at commit), so ADR-0011 stays **proposed** — exactly as its prerequisites state.
