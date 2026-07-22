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

This is not yet an implementation-ready foundation. The current work converts the
idea into testable contracts; it does not complete the evidence-level external
audits, prototype execution or independent review. The traceability matrix is
**structurally** complete (one row per requirement), but its rows are not yet
**proven** with retained execution evidence.

## What is established

- implementation gate and document precedence;
- stable requirement/error/risk/test identifiers;
- 13 principles and 10 non-goals;
- 26 functional and 13 non-functional requirements;
- 17 product acceptance criteria;
- component boundaries and one-writer/one-executor rules;
- journaled transaction model and 22 initial failure modes;
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
- twenty versioned record schemas `SCH-01..SCH-20` with classification, retention
  and export rules, valid/invalid examples, an explicit strict-write/tolerant-read
  compatibility policy, and an `SC-01..SC-10` test family;
- an implementation-level external audit of ai-memory (`EA-01`) with line-exact
  evidence at its pin, and an audit framework for the remaining candidates;
- six disposable prototype gates `PT-01..PT-06` with measurable pass/fail;
- a one-row-per-requirement traceability matrix (every FR/NFR/SR/AC mapped to a
  verification family) guarded by a documentation linter that currently reports
  zero ID, reference, link, traceability or schema-well-formedness errors.

## Blocking work

1. ~~Resolve Q-01 through Q-05 with the project owner (G-01, critical).~~
   **Done 2026-07-21 — ADR-0006 closes Q-01..Q-08; G-01 closed.**
2. Complete the remaining implementation-level audits (`EXTERNAL-AUDITS.md`):
   ai-memory (`EA-01`), RTK (`EA-02`) and MCP (`EA-03`) are done; LiteLLM,
   OpenHands, Letta and Mem0 remain, and no observed remote HEAD is a release
   pin. Caveman identity/license must also be verified before it is treated as
   a component.
3. Complete the attribution plan now that Q-02 selected Apache-2.0 (NOTICE,
   SBOM/source-offer format, per-file review); PhaseZero remains
   behavior-research-only because it has no tracked root license (G-02 narrowed,
   still open).
4. Turn proposed ADRs into accepted decisions after their gates
   (`ADR-0002/0004/0005/0010/0011` still proposed; `ADR-0003` accepted via Q-04).
5. Schemas `SCH-01..SCH-20` are defined with examples; the `SC-01..SC-10`
   golden/version/classification tests are **executed** against a pinned
   Draft 2020-12 validator (`tools/schema_suite/run_suite.py`), isolated from
   the product runtime. All 12 checks pass (META, SC-01..SC-10, SEM).
6. Traceability now carries one row per requirement; rows remain `specified` and
   must reach `proven` with retained evidence under the approval rule.
7. Run the prototype gates `PT-01..PT-06`; all remain specified, none executed.
8. Obtain an independent adversarial foundation review.

## Gate decision

Production code, installers, packages, services and host changes remain forbidden.
No `APPROVED_TO_IMPLEMENT` marker should be created. The next valid phase is
evidence research and decision closure, followed by prototype gates explicitly
marked non-production.
