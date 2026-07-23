# Foundation readiness report

Date: 2026-07-21  
Classification: **NOT READY — FOUNDATION IN PROGRESS (decisions closed)**

## Executive assessment

Koquetel now has an initial normative skeleton covering vision, product outcomes,
architecture, transaction recovery, security, data/memory, public contracts,
interaction, testing, operations, migration, legal constraints and roadmap. The
documents establish strong boundaries and prevent premature implementation. The
local reference sources now also have pinned evidence, structural inventories,
capability comparison, numerical robustness scoring and named anti-requirements.

All eight owner decisions `Q-01..Q-08` are now closed in
[`docs/adr/ADR-0006-FOUNDATION-OWNER-DECISIONS.md`](docs/adr/ADR-0006-FOUNDATION-OWNER-DECISIONS.md);
`G-01` is closed and `G-02` is narrowed (license selected; attribution plan
still open). `ADR-0003` is accepted via Q-04 = Balanced.

This is not yet an implementation-ready foundation. All six prototype gates are
executed: **PT-01, PT-02, PT-03, PT-05 and PT-06 PASS** (five gates), and **PT-04
is PARTIAL** — rootless containment was shown via bwrap/userns, but the Podman
backend and the network-allowlist arm are a coverage gap, so **`G-05` stays open
(high)**. The traceability matrix is **structurally** complete (one row per
requirement), but its rows are not yet **proven** (the approval rule requires an
independent reviewer).

Remaining before `READY`: (1) a passing independent adversarial review — the first
review (pin `5db0244`) returned **FAIL** with RF-01..RF-04 (all high); those are
**remediated on this branch but awaiting independent re-validation** (`G-09` stays
open — see "Independent review status" below); (2) explicit implementation approval;
and (3) owner
ratification of the still-**proposed** decisions `ADR-0002` (Rust core),
`ADR-0010` (session lifecycle) and `ADR-0011` (local OFD lease) — the §5
"architecture boundaries and transaction model accepted" item depends on that
ratification. It is therefore **not** true that only two items remain while those
ADRs are proposed. A ratification packet is prepared in
[`docs/OWNER-RATIFICATION-PACKET.md`](docs/OWNER-RATIFICATION-PACKET.md).

## What is established

- implementation gate and document precedence;
- stable requirement/error/risk/test identifiers;
- 13 principles and 10 non-goals;
- 26 functional and 13 non-functional requirements;
- 17 product acceptance criteria;
- component boundaries and one-writer/one-executor rules;
- journaled transaction model and 23 initial failure modes;
- 16 security requirements and threat/control seed matrix;
- governed, backend-independent memory envelope;
- initial CLI/API and stable error catalog;
- failure-injection and rollback test seeds;
- lifecycle, removal and PhaseZero migration boundaries;
- staged milestones and quantified risk register.
- pinned local and priority remote source identities;
- local structural audit with exact files/lines and dirty-state exclusion;
- weighted local robustness comparison: PhaseZero 45.25, SteamZero 85.00;
- license matrix and explicit PhaseZero no-license finding;
- ten anti-requirements and ten cross-source synthesis gaps.
- owner-confirmed complete operational independence from PhaseZero and SteamZero,
  specified by P-13/NFR-13/AC-17 and eight release-blocking independence tests.
- twenty-one versioned record schemas `SCH-01..SCH-21` with classification, retention
  and export rules, valid/invalid examples, an explicit strict-write/tolerant-read
  compatibility policy, and an `SC-01..SC-11` test family;
- an implementation-level external audit of ai-memory (`EA-01`) with line-exact
  evidence at its pin, and an audit framework for the remaining candidates;
- six disposable prototype gates `PT-01..PT-06` executed with retained evidence in
  `docs/08-testing/prototype-evidence/`: PT-01, PT-02, PT-03, PT-05, PT-06 **PASS**;
  PT-04 **partial** (rootless containment shown via bwrap/userns, but the Podman
  backend and network-allowlist arms are a coverage gap);
- a one-row-per-requirement traceability matrix (every FR/NFR/SR/AC mapped to a
  verification family) guarded by a documentation linter that currently reports
  zero ID, reference, link, traceability or schema-well-formedness errors.

## Blocking work

1. ~~Resolve Q-01 through Q-05 with the project owner (G-01, critical).~~
   **Done 2026-07-21 — ADR-0006 closes Q-01..Q-08; G-01 closed.**
2. ~~Complete the remaining implementation-level audits (`EXTERNAL-AUDITS.md`):
   ai-memory (`EA-01`), RTK (`EA-02`) and MCP (`EA-03`) are done; LiteLLM,
   OpenHands, Letta and Mem0 remain, and no observed remote HEAD is a release
   pin. Caveman identity/license must also be verified before it is treated as
   a component.~~ **Done 2026-07-21 — EA-04..EA-07 complete; G-03 closed;
   Caveman identity confirmed (`JuliusBrussee/caveman`, claimed MIT); pin +
   full EA for Caveman deferred to M-02 adapter work.**
3. ~~Complete the attribution plan now that Q-02 selected Apache-2.0 (NOTICE,
   SBOM/source-offer format, per-file review)~~ — **Done 2026-07-21
   (`docs/11-legal/ATTRIBUTION-PLAN.md`)**; G-02 narrowed to "ledger/matrix
   created on first reuse". PhaseZero remains behavior-research-only because it
   has no tracked root license.
4. **Owner ratification** of `ADR-0002` (Rust core), `ADR-0010` (session lifecycle
   + random-128-bit id) and `ADR-0011` (local OFD lease — Decision A only) — all
   **prepared for ratification** in `docs/OWNER-RATIFICATION-PACKET.md`, **not**
   self-accepted. (`ADR-0001/0003/0004/0005/0006` already accepted.) `G-13` is
   reclassified to block only the v2 distributed/NFS path, not v1-local.
5. Schemas `SCH-01..SCH-21` are defined with examples; the `SC-01..SC-11`
   golden/version/classification tests are **executed** against a pinned
   Draft 2020-12 validator (`tools/schema_suite/run_suite.py`), isolated from
   the product runtime. All 13 checks pass (META, SC-01..SC-11, SEM).
6. Traceability now carries one row per requirement; rows remain `specified` and
   must reach `proven` with retained evidence under the approval rule.
7. ~~Prototype gates~~ **All six executed 2026-07-22.** PT-01, PT-02, PT-03,
   PT-05, PT-06 PASS; PT-04 partial (rootless containment shown; Podman-backend and
   network-allowlist arms are a coverage gap, so PT-04 and G-05 stay open). The §5
   "three high-risk prototypes pass" requirement is met (five pass).
8. Obtain an independent adversarial foundation review. The review is now
   **organized** (`docs/08-testing/INDEPENDENT-REVIEW-CHARTER.md`) but not
   performed; `G-09` closes only when the review report is attached.

## M-00 exit checklist (`FOUNDATION-GOVERNANCE.md §5`)

Honest per-item status. Items that require executed evidence cannot be closed on
paper; they are marked as blockers, not narrated as done.

| §5 requirement | Status | Evidence / blocker |
|---|---|---|
| source inventory + capability matrix | ✅ done | research docs, EA-01..EA-07, robustness/capability matrices |
| owner decisions Q-01..Q-05 resolved | ✅ done | ADR-0006, owner-ratified 2026-07-22 |
| license + clean-room reuse policy accepted | 🟡 partial | Apache-2.0 (Q-02); ATTRIBUTION-PLAN written; per-file ledger due on first reuse (G-02) |
| architecture boundaries + transaction model accepted | 🟡 awaiting ratification | boundaries acceptable; the v1 transaction/lease model (ADR-0011 Decision A, local OFD) is proven (PT-01/PT-06) and **prepared for owner ratification** — G-13 reclassified to v2-only, so it no longer blocks v1 |
| state/memory/permission/secrets/event schemas versioned | ✅ done | SCH-01..SCH-21; schema suite 13/13 |
| failure modes cover install/update/tool/memory/routing | ✅ done | FM-01..FM-23 |
| acceptance/failure-injection/rollback/security matrices complete | 🟡 specified | TRACEABILITY one row/req; rows `specified`, not `proven` (needs tests + G-09) |
| installer + removal ownership rules specified | ✅ done | LIFECYCLE; ownership markers |
| three high-risk prototypes pass their gates | ✅ done | PT-01/02/03/05/06 PASS (5/6); PT-04 partial (G-05 open). ≥3 high-risk gates pass |
| independent review, no unresolved critical contradiction | ❌ **blocker** | review ran at `5db0244` = **FAIL** (RF-01..04); remediated on this branch, **awaiting re-validation** (G-09) |
| explicit implementation approval exists | ❌ **blocker** | no `APPROVED_TO_IMPLEMENT` |

ADR status: `ADR-0001/0003/0004/0005/0006` **accepted**. `ADR-0002` (Rust core),
`ADR-0010` (session lifecycle + random-128-bit id) and `ADR-0011` (local OFD lease
— Decision A) are **proposed and prepared for owner ratification**
(`docs/OWNER-RATIFICATION-PACKET.md`), **not** self-accepted. The language decision
(ADR-0002) is decoupled from Podman (M-04) and atomic config projection (M-01);
ADR-0011 splits Decision A (v1 local, ready) from Decision B (v2 distributed,
blocked by `G-13`).

**Conclusion:** 6 §5 items done, 3 partial/awaiting-ratification. Remaining M-00
work: (1) **owner ratification** of `ADR-0002/0010/0011` (packet prepared);
(2) a **passing independent adversarial review** (`G-09`) — the first returned FAIL
(RF-01..04), now remediated and awaiting re-validation; and
(3) **explicit implementation approval**. It is therefore **not** true that only
two items remain while those ADRs are proposed. `NOT READY` stands.

## Independent review status

The first independent adversarial review (reviewer: Codex, branch
`review/m00-independent`, pin `5db0244`) returned **FAIL** with four open high
findings. Remediation is on `foundation/m00-closure`. **The author does not close
any finding**; each remains *awaiting independent validation*, and a re-review of
the remediated pin is required.

| Finding | Class | Remediation (this branch) | Status |
|---|---|---|---|
| RF-01 | contradiction | ADR-0002 has one acceptance predicate (PT-05 = language + distribution); Podman=PT-04/M-04/G-05, atomic config projection=M-01 exit. Evidence reports corrected with struck-through history. | **remediated — awaiting independent validation** |
| RF-02 | contradiction | ADR-0010 carries one v1 id format (random 128-bit, 32 lowercase hex `^[0-9a-f]{32}$`, no timestamp); UUIDv7 rejected for v1 (no benchmark). Owner packet R-2 aligned. | **remediated — awaiting independent validation** |
| RF-03 | evidence-gap | `PROTOTYPE-EVIDENCE-POLICY.md` added; PT-01..PT-06 rerun with retained, hash-pinned bundles (`prototype-evidence/PT-NN/`). | **remediated — awaiting independent validation** |
| RF-04 | traceability | `SCH-21 SessionHandle` + `SC-11` + `CONTRACTS.md` §Sessions + examples/manifest/traceability; the schema-fixed format claim is now backed. | **remediated — awaiting independent validation** |

Neither this branch nor this report closes `G-09`; only a passing independent
re-review does.

## Gate decision

Production code, installers, packages, services and host changes remain forbidden.
No `APPROVED_TO_IMPLEMENT` marker should be created. The next valid phase is
evidence research and decision closure, followed by prototype gates explicitly
marked non-production.
