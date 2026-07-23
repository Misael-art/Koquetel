# PT-05 evidence — Rust distribution: binary, SQLite, Unix socket, recovery after kill

## Current canonical rerun

The canonical R2 rerun is [`PT-05-R2/`](PT-05-R2/) with integrity index
[`PT-05-R2/SHA256SUMS`](PT-05-R2/SHA256SUMS). Its derived verdict is **PASS**:
the host-built binary ran in a fresh Ubuntu 24.04 container with no rustc/cargo;
migrations returned 1 then 1; the production socket was 0600; real uid 1002 was
denied both by filesystem mode and, on a separate permissive test transport, by
`SO_PEERCRED` against owner uid 1001; kill-before recovered
`<absent>/rolled_back`; kill-after recovered `value/committed`; cold start was
23 ms under 500 ms. These values come only from
[`metrics.json`](PT-05-R2/metrics.json) and
[`pass-fail.json`](PT-05-R2/pass-fail.json).

## Historical record

> **HISTORICAL — SUPERSEDED; NOT CANONICAL FOR CURRENT VERDICT.** Everything
> below includes the earlier same-user peer simulation and is not current
> evidence.

> **Verification rerun after RF-03 (2026-07-23).** A fresh ephemeral rerun with a retained, hash-pinned evidence bundle is in `PT-05/` — see [`PT-05/SHA256SUMS`](PT-05/SHA256SUMS), [`PT-05/manifest.json`](PT-05/manifest.json) and [`PT-05/pass-fail.json`](PT-05/pass-fail.json). Rerun verdict: **PASS**. The bundle (raw logs, metrics, per-arm pass/fail, harness source) is the gate-required evidence per [`../PROTOTYPE-EVIDENCE-POLICY.md`](../PROTOTYPE-EVIDENCE-POLICY.md); the summary below is retained.


Gate: [`../PROTOTYPE-GATES.md`](../PROTOTYPE-GATES.md) PT-05
Date executed: 2026-07-22
Branch: `foundation/m00-closure`
Prototype location: `/tmp/koquetel-prototypes/pt05/` (ephemeral, deleted after evidence capture)

## Verdict

**PASS** for the PT-05 gate as written (distribution binary, SQLite migration,
Unix-socket peer credentials, recovery after kill).

> **Superseded by RF-01 remediation (2026-07-22).** The historical sentence below
> treated Podman invocation and atomic config projection as *ADR-0002 gate arms*.
> Under the RF-01 authoritative interpretation, **ADR-0002's acceptance predicate
> is PT-05 (core language + distribution) only**; Podman invocation belongs to
> PT-04/M-04 and G-05, and atomic config projection is an M-01 exit criterion —
> neither is part of the ADR-0002 language decision. History preserved, struck.

~~Note: ADR-0002's own gate lists two further arms — Podman invocation and atomic
config projection — that PT-05 does not cover, so ADR-0002 is not fully accepted
here.~~

## Environment

| Item | Value |
|---|---|
| Kernel | Linux 6.18.38-1-MANJARO x86_64 |
| Filesystem under test | `tmpfs` (`/tmp`) |
| Rust (build only) | rustc 1.97.0 / cargo 1.97.0 |
| SQLite | statically bundled via `rusqlite 0.31` + `libsqlite3-sys 0.28` (feature `bundled`) |
| Binary SHA-256 | `41ea36e1678ce832d6dd3c8cd55d648ea158e112cb29298a21c0dfb6ab27fbf4` |
| Binary size | 2,203,536 bytes (single file) |
| Runtime deps (`ldd`) | `libgcc_s`, `libm`, `libc` (glibc) only — **no Rust runtime, no libsqlite3** |

### Declared ceilings (fixed before running, per the gate)

- **Cold-start ceiling:** 500 ms (launch → socket READY, including DB open +
  migration). Also compared against NFR-05's 250 ms client-integration budget.
- **Distribution-friction threshold (ADR-0002):** a single self-contained
  executable that runs on any glibc Linux with **no runtime install** (no Rust
  toolchain, no system SQLite). Exceeding this (e.g. needing a language runtime)
  would reopen ADR-0002 toward the Python-with-runtime option.

## Reproducible commands

```bash
cd /tmp/koquetel-prototypes/pt05
cargo build --release            # 1m23s cold (build-time only needs Rust)
ldd target/release/pt05_core     # self-containedness
bash drive.sh                    # full matrix
```

## Results

| Arm | Result | Verdict |
|---|---|---|
| Cold start (launch → READY) | **12 ms** (ceiling 500 ms) | **PASS** |
| Self-contained binary | glibc-only; no Rust runtime, SQLite static | **PASS** |
| Migration idempotency (2 serve runs, same DB) | `version_run1=1 version_run2=1`, no error | **PASS** |
| Peer-cred owner-only rejection | connect uid=1000 to owner_uid=1001 → `DENIED peer_uid=1000 owner_uid=1001` | **PASS** |
| Socket permission mode | `600` (owner-only, SR-13) | **PASS** |
| Kill **before** commit → recover | `get foo = <absent>`, `jstate foo = rolled_back` (OLD state) | **PASS** |
| Kill **after** commit → recover | `get foo = bar`, `jstate foo = committed` (NEW state) | **PASS** |

Durability posture: the core store opens WAL with `synchronous=FULL` (governance
grade), deliberately stronger than the memory backend's `synchronous=NORMAL`
observed in EA-01 (`lib.rs:92`). The intent journal is persisted+fsynced as its
own committed transaction **before** the mutation is staged (TRANSACTION-MODEL
step 6), so a kill between staging and commit leaves a durable `staged` intent
with no `committed` peer — recovery converges it to `rolled_back`.

## Fault injection

- `killbefore`: after staging the intent (durable) and opening `BEGIN IMMEDIATE`
  with the row inserted but **not committed**, the server raises `SIGKILL` on
  itself. SQLite discards the uncommitted WAL frames on restart; recovery marks
  the orphan `staged` intent `rolled_back`. Converges to OLD.
- `killafter`: the full mutation commits (kv row + `committed` journal, fsynced),
  then the server raises `SIGKILL` before replying. Restart finds the durable
  row. Converges to NEW.
- Both are `kill -9` (SIGKILL) — uncatchable, the strongest kill fault.

## Honest coverage notes

- **"Clean host without a system Rust toolchain":** demonstrated via `ldd`
  (only glibc; no Rust runtime, no libsqlite3) rather than by provisioning a
  fresh container. The compiled binary needs no toolchain at runtime; the build
  needs Rust once (the release pipeline). This proves the *distribution* claim.
- **Non-owner rejection** is exercised by configuring `owner_uid = me+1` and
  connecting as the real uid, so the `SO_PEERCRED` mismatch path runs. A literal
  second OS user was not created (no privilege); the kernel `SO_PEERCRED` value
  and the rejection code path are genuinely exercised. Socket mode `600` is the
  kernel-enforced complement.
- **Filesystem:** tmpfs (local-kernel). SQLite WAL + `synchronous=FULL` durability
  semantics are identical on local filesystems (ext4/XFS/tmpfs); `/home` is btrfs.
  No networked filesystem tested (out of v1 scope, Q-08).

## Gaps found

- **ADR-0002 residual:** ADR-0002's gate also requires **Podman invocation** and
  **atomic config projection**. Podman is unavailable on this host (see PT-04),
  and atomic config projection is an M-01/M-02 concern. PT-05 therefore satisfies
  the *distribution / SQLite / socket / recovery* portion of ADR-0002's gate but
  not the Podman-invocation arm.

## Disposal

Prototype source, `Cargo.lock`, target/ and `drive.sh` live only in
`/tmp/koquetel-prototypes/pt05/` and are deleted after this evidence is committed.
Only this file (with the binary SHA-256 and measured numbers) is retained.

## ADRs affected

- **ADR-0002 (Rust core) — corrected by RF-01:** PT-05 satisfies ADR-0002's
  acceptance predicate (core language + distribution: static binary, bundled
  SQLite, Unix-socket peer credentials, kill-recovery). **Podman invocation
  (PT-04/M-04, G-05) and atomic config projection (M-01 exit) are NOT ADR-0002 gate
  arms.** ADR-0002 is **ready for owner ratification** (not author-accepted).
  ~~Original: distribution/SQLite/socket/recovery satisfied; Podman-invocation and
  atomic-config-projection arms outstanding; ADR-0002 stays proposed until PT-04
  and the config-projection arm are shown.~~
- **ADR-0010 (session lifecycle) — corrected by RF-02:** peer-credential/recovery
  mechanics demonstrated feasible; PT-06 is met and the v1 id is **random 128-bit**
  (no UUIDv7 justification). ~~Original: still gated on PT-06 + UUIDv7
  justification.~~
