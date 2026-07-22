# ADR-0006 — Foundation owner decisions (Q-01..Q-08)

Status: accepted by project owner  
Date: 2026-07-21

## Context

`FOUNDATION-GOVERNANCE.md §5` requires product-owner decisions `Q-01` through
`Q-05` to be resolved before `READY FOR IMPLEMENTATION`, and three further
questions (`Q-06..Q-08`) are referenced by architecture, UX and distribution
contracts. Until this ADR, all eight were open in
[`../OPEN-QUESTIONS.md`](../OPEN-QUESTIONS.md) and blocked `G-01` (critical) and
several downstream gaps.

This ADR records the owner's explicit answers given on 2026-07-21, the option
chosen for each, and the consequence. It does **not** authorize implementation;
the implementation gate still requires the rest of `M-00` (license attribution,
audits, prototypes, independent review) and an explicit
`APPROVED_TO_IMPLEMENT` marker.

## Decisions

| ID | Decision | Option chosen | Consequence |
|---|---|---|---|
| Q-01 | Final product name and spelling | **Koquetel** (repository spelling) | Identity and packaging keep the current name. Trademark/domain availability review remains open under `G-10` and must close before public release; this ADR takes no position on trademark registrability. |
| Q-02 | Project license | **Apache-2.0** | `LICENSE` file to be added as Apache-2.0; `NOTICE` and per-file attribution required for any reused code. Compatible with the verified licenses of `ai-memory` (MIT), RTK (Apache-2.0), MCP (Apache-2.0/MIT transitory), Letta (Apache-2.0) and Mem0 (Apache-2.0). Closes the license-selection half of `G-02`; the component-level attribution plan is still required before any code reuse. |
| Q-03 | First supported hosts | **Linux first, WSL compatibility next** | v1 targets Linux (ext4/XFS/tmpfs). Core is Rust with Unix-domain-socket peer credentials and rootless Podman sandbox; Docker is fallback. Windows-native and macOS are out of v1. Test matrix is Linux-focused. WSL is a follow-on compatibility target, not a v1 release gate. |
| Q-04 | Default autonomy policy | **Balanced** | Reversible scoped workspace writes may be auto-delegated per profile; external writes, host-admin and destructive operations require plan-bound user confirmation unless a narrower expiring delegation already exists. Child agents receive attenuated subsets only. Unblocks `ADR-0003` (now accepted) and the session-start confirmation question in `ADR-0010`. |
| Q-05 | Default data posture | **Local-first with cloud opt-in** | Memory, telemetry and routing operate locally by default. Any cloud/sync/remote-routing path requires explicit per-backend opt-in. Aligns with `NFR-06` and `R-07`. |
| Q-06 | Supported user profile (v1) | **Individual developer** | v1 ships for a single Linux user. Schemas remain team-ready but no multi-user control plane ships in v1; team administrator stays a deferred persona. |
| Q-07 | Interface commitment (v1) | **CLI first** | v1 surface is the CLI plus the offline `status`/`doctor`/export/uninstall paths. A local read-only dashboard may follow after contracts stabilize; native UI is out of v1. |
| Q-08 | NFS commit-level fence requirement | **(a) NFS unsupported in v1** | v1 is restricted to local filesystems (ext4/XFS/tmpfs). Multi-host lease and NFS support are deferred to a potential future v2, which would require resolving `G-13` (conditional atomic commit primitive / revocation-proof epoch). Does not by itself accept `ADR-0011`; `ADR-0011` still requires `PT-01`, `PT-06` and `G-13` closure on the local path. |

## Authority and scope

- This ADR is the canonical owner-decision record for `Q-01..Q-08`. The
  recommendation column in [`../OPEN-QUESTIONS.md`](../OPEN-QUESTIONS.md) is
  superseded by the "Option chosen" column above for these eight IDs.
- Per [`../FOUNDATION-GOVERNANCE.md`](../FOUNDATION-GOVERNANCE.md) §2, an
  accepted owner decision recorded in an accepted ADR takes precedence over
  every lower document. Downstream documents (PRD, ARCHITECTURE, threat model,
  data model, license matrix, reuse policy, ADRs 0002..0005/0010/0011) are
  updated in the same change set to remain consistent with this ADR.
- Identifiers `Q-01..Q-08` are preserved (no renumbering); their state moves
  from open to decided.

## What this ADR does NOT do

- It does not create `APPROVED_TO_IMPLEMENT`.
- It does not accept `ADR-0002` (Rust core), `ADR-0004` (memory envelope) or
  `ADR-0011` (lease recovery/fencing); those still require prototype evidence.
- It does not resolve `G-02` fully (attribution plan still required), `G-09`
  (independent adversarial review), `G-10` (trademark/domain) or `G-13`
  (conditional atomic commit primitive).
- It does not license any third-party code for copying; the clean-room policy
  and per-file attribution plan remain mandatory before any reuse.

## References

- [`../OPEN-QUESTIONS.md`](../OPEN-QUESTIONS.md) — `Q-01..Q-08` rows.
- [`../FOUNDATION-GOVERNANCE.md`](../FOUNDATION-GOVERNANCE.md) §2 (authority),
  §5 (foundation completion gate).
- [`../KNOWN-GAPS.md`](../KNOWN-GAPS.md) — `G-01` (closed by this ADR), `G-02`
  (narrowed), `G-10` (still open), `G-13` (still open).
- [`ADR-0003-AUTOMATION-AUTHORITY.md`](ADR-0003-AUTOMATION-AUTHORITY.md) —
  accepted via Q-04 = Balanced.
- [`ADR-0010-SESSION-LIFECYCLE.md`](ADR-0010-SESSION-LIFECYCLE.md),
  [`ADR-0011-LEASE-RECOVERY-FENCING.md`](ADR-0011-LEASE-RECOVERY-FENCING.md) —
  prerequisites narrowed.
