# Owner ratification packet

Status: **awaiting owner decision** — nothing here is accepted yet
Prepared: 2026-07-22 · Branch: `foundation/m00-closure`

This packet asks the project owner to ratify a small set of decisions that the
author has **prepared but not accepted**. The author does not decide these on the
owner's behalf. Each item states the recommendation, the evidence, and exactly
what ratifying does and does **not** unlock. Approving this packet does **not**
create `APPROVED_TO_IMPLEMENT` and does **not** exit M-00.

## Decisions requested

| # | Decision | Author recommendation | Evidence | Owner: approve / modify / reject |
|---|---|---|---|---|
| R-1 | **ADR-0002** — core language | **Accept Rust** for the core, CLI and transaction engine | PT-05: 2.2 MB glibc-only static binary, bundled SQLite, idempotent migrations, `SO_PEERCRED` owner-only, kill-9 recovery | ☐ |
| R-2 | **ADR-0010** — session lifecycle + id format | **Accept** the lightweight session token; **id = random 128-bit** for v1 (privacy + simplicity), UUIDv7 only after a benchmark, format schema-substitutable | PT-01/PT-02/PT-06 (recovery with no lost mutations); id analysis in ADR-0010 §Identifier | ☐ |
| R-3 | **ADR-0011** — lease model | **Accept Decision A only** (v1 local single-host cooperative OFD lease); **defer Decision B** (distributed/NFS/multi-host) to a potential v2 | PT-01 (0 overlaps/10k), PT-06 (20/20 reclaims); local-model analysis: dead holder cannot race | ☐ |
| R-4 | **G-13** scope | **Defer to v2** (NFS/multi-host fencing); it does **not** block v1-local | ADR-0011 Decision A analysis; `FM-23` (liveness) is the only v1-local residual | ☐ |
| R-5 | **G-05 / sandbox** | Acknowledge: **blocks M-04 and any sandbox-declared release**, **not** the start of M-01/M-02 under phased implementation; Podman is the primary backend, approved only after a real Podman test | PT-04 PARTIAL (rootless bwrap/userns passes; Podman absent, allowlist untested) | ☐ |
| R-6 | Phasing | If implementation is later approved, release **milestone by milestone** (M-01 → M-07), each behind its own exit gate | ROADMAP M-00..M-07 | ☐ |

## What each ratification unlocks (and does not)

- **R-1 (Rust):** lets M-01 be built in Rust. Does **not** prove Podman invocation
  (M-04/PT-04) or atomic config projection (M-01 exit) — those are separate gates.
- **R-2 (session lifecycle):** fixes the session model and id format for M-06/M-03
  work. The id format stays schema-substitutable, so a later benchmark can switch
  to UUIDv7 without reopening the ADR.
- **R-3 + R-4 (local lease / G-13):** accepts the v1 transactional-lease model,
  which is the §5 "transaction model accepted" item for the **local** scope. It
  does **not** claim any distributed/NFS capability; that stays a v2 gap (G-13).
- **R-5 (sandbox):** clarifies phasing. No release may declare a sandbox until
  G-05 closes on a real Podman host.
- **R-6 (phasing):** governance for a future implementation phase.

## What is still required to reach `READY FOR IMPLEMENTATION`

Even with this packet approved, M-00 does **not** exit. Still required:

1. the **independent adversarial review** (`G-09`, charter in
   `docs/08-testing/INDEPENDENT-REVIEW-CHARTER.md`) — run by a non-author;
2. **explicit implementation approval** (`APPROVED_TO_IMPLEMENT`), which only the
   owner may create, and only after (1);
3. TRACEABILITY rows reaching `proven` (needs the reviewer from (1)).

## Recording the decision

When the owner responds, record the outcome in `docs/OPEN-QUESTIONS.md` (new
`Q-xx` if a decision changes) and flip the relevant ADR `Status:` to `accepted`
with the owner-ratification date, in a **separate** commit. Until then, all ADRs
above remain `proposed`.
