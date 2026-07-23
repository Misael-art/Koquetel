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
executed. Canonical verdicts are **PT-02, PT-03, PT-05 and PT-06 PASS**;
**PT-01 PARTIAL** because ext4/XFS is blocked despite passing tmpfs and both
contended fork variants; and **PT-04 PARTIAL** because Podman/network
allowlisting are missing. Thus `G-11` is reopened and `G-05` remains high and
release-blocking. The traceability matrix is **structurally** complete (one row per
requirement), but its rows are not yet **proven** (the approval rule requires an
independent reviewer).

Remaining before `READY`: (1) PT-01 on ext4/XFS (`G-11`); (2) a passing R3
independent review after R2 returned **FAIL**; (3) explicit implementation approval;
and (4) owner
ratification of the still-**proposed** decisions `ADR-0002` (Rust core),
`ADR-0010` (session lifecycle) and `ADR-0011` (local OFD lease). ADR-0010/0011
cannot be ratified until G-11 closes. The decision packet remains in
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
- six disposable prototype gates `PT-01..PT-06` executed with retained evidence:
  PT-02/PT-03/PT-05/PT-06 **PASS**; PT-01 **partial** (ext4/XFS blocked);
  PT-04 **partial** (Podman/network allowlist missing);
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
4. **Owner ratification** of `ADR-0002`, `ADR-0010` and `ADR-0011`. None is
   self-accepted; ADR-0010/0011 additionally wait for PT-01 on ext4/XFS
   (`G-11`). `G-13` continues to block distributed/NFS Decision B.
5. Schemas `SCH-01..SCH-21` are defined with examples; the `SC-01..SC-11`
   golden/version/classification tests are **executed** against a pinned
   Draft 2020-12 validator (`tools/schema_suite/run_suite.py`), isolated from
   the product runtime. All 13 checks pass (META, SC-01..SC-11, SEM).
6. Traceability now carries one row per requirement; rows remain `specified` and
   must reach `proven` with retained evidence under the approval rule.
7. **Prototype gates:** all six executed. PT-02/PT-03/PT-05/PT-06 pass;
   PT-01/PT-04 are partial. Four independent complete passes exist, but the
   governance-named PT-01/PT-02/PT-03 set remains incomplete; another gate
   cannot substitute for PT-01's missing filesystem arm.
8. Obtain a passing R3 independent adversarial review; G-09 remains open.

## M-00 exit checklist (`FOUNDATION-GOVERNANCE.md §5`)

Honest per-item status. Items that require executed evidence cannot be closed on
paper; they are marked as blockers, not narrated as done.

| §5 requirement | Status | Evidence / blocker |
|---|---|---|
| source inventory + capability matrix | ✅ done | research docs, EA-01..EA-07, robustness/capability matrices |
| owner decisions Q-01..Q-05 resolved | ✅ done | ADR-0006, owner-ratified 2026-07-22 |
| license + clean-room reuse policy accepted | 🟡 partial | Apache-2.0 (Q-02); ATTRIBUTION-PLAN written; per-file ledger due on first reuse (G-02) |
| architecture boundaries + transaction model accepted | ❌ evidence blocker | ADR-0011 Decision A remains proposed; PT-06 passes but PT-01 is partial until ext4/XFS runs (G-11). G-13 separately remains v2-only |
| state/memory/permission/secrets/event schemas versioned | ✅ done | SCH-01..SCH-21; schema suite 13/13 |
| failure modes cover install/update/tool/memory/routing | ✅ done | FM-01..FM-23 |
| acceptance/failure-injection/rollback/security matrices complete | 🟡 specified | TRACEABILITY one row/req; rows `specified`, not `proven` (needs tests + G-09) |
| installer + removal ownership rules specified | ✅ done | LIFECYCLE; ownership markers |
| three high-risk prototypes pass their gates | 🟡 incomplete named set | four complete passes exist (PT-02/03/05/06), but PT-01/02/03 is not complete because PT-01 is partial |
| independent review, no unresolved critical contradiction | ❌ **blocker** | R2 at `f086ed7` = FAIL; RF-03/RF-04 high and RF-05 medium await R3 validation |
| explicit implementation approval exists | ❌ **blocker** | no `APPROVED_TO_IMPLEMENT` |

ADR status: `ADR-0001/0003/0004/0005/0006` **accepted**. `ADR-0002` (Rust core),
`ADR-0010` (session lifecycle + random-128-bit id) and `ADR-0011` (local OFD lease
— Decision A) are **proposed**, **not** self-accepted; ADR-0010/0011 are blocked
by G-11 target-filesystem evidence. The language decision
(ADR-0002) is decoupled from Podman (M-04) and atomic config projection (M-01);
ADR-0011 splits Decision A (v1 local, evidence-blocked) from Decision B (v2 distributed,
blocked by `G-13`).

**Conclusion:** M-00 remains **NOT READY**. Remaining work includes PT-01 on
ext4/XFS (`G-11`), owner ratification after prerequisites, a passing R3 review,
and explicit implementation approval.

## Independent review status

Independent review R2 (branch `review/m00-independent-r2`, report commit
`30b0038`, reviewed pin `f086ed7`) returned **FAIL**: RF-03/RF-04 open high and
RF-05 open medium; RF-01/RF-02 closed. The author does not self-close findings;
the dispositions below are **awaiting R3 validation**.

| Finding | Class | Remediation (this branch) | Status |
|---|---|---|---|
| RF-01 | contradiction | Closed by R2; unchanged. | **closed by R2** |
| RF-02 | contradiction | Closed by R2; random-128 remains the sole v1 proposal. | **closed by R2** |
| RF-03 | evidence-gap | Literal PT-01/03/05/06 reruns in adjacent immutable R2 bundles; PT-01 downgraded and G-11 reopened. | **awaiting R3 validation** |
| RF-04 | traceability | SCH-21 ended pair, enum and versioned SessionRef; executable SC-11 schema/transition/negative tests; bounded API claims. | **awaiting R3 validation** |
| RF-05 | summary drift | Every PT report has one bundle-derived current section and a superseded-history boundary; PT-04 uses 8 ms and no fork-storm/cgroup claim. | **awaiting R3 validation** |

Neither this branch nor this report closes `G-09`; only a passing independent
re-review does.

## Gate decision

Production code, installers, packages, services and host changes remain forbidden.
No `APPROVED_TO_IMPLEMENT` marker should be created. The next valid phase is
evidence research and decision closure, followed by prototype gates explicitly
marked non-production.
