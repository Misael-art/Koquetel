# Independent M-00 adversarial review report

Review date: 2026-07-22  
Reviewer identity: Codex, operating under the separate independent-review mandate.  
Independence declaration: this reviewer did not author, amend, or approve any
foundation document, schema, prototype, tool, or owner decision reviewed here.
This report is the reviewer's only change.

## Reviewed pin and scope

The reviewed object is commit
`5db024445451c59a0f2f9d18abb3860df7e9fc21`
(`docs(m00): reconcile ADR scope and independent review entry`), obtained from
`origin/foundation/m00-closure`. The worktree was clean before review and the
review branch was created directly from that object. No
`APPROVED_TO_IMPLEMENT` file exists at the reviewed pin.

I read `AGENTS.md`, `/home/misael/.codex/RTK.md`, and the complete
`INDEPENDENT-REVIEW-CHARTER.md`, then reviewed the charter's listed governance,
product, architecture, safety, data/schema, decision, evidence, legal,
traceability, honesty, owner-packet, and tooling artifacts. This is a
documentation-only adversarial review; it neither authorizes implementation nor
alters a foundation contract to make a result pass.

## Method

The pin was exported with `git archive` to a fresh temporary directory. Gates
were executed there, not in the review worktree. The schema-suite virtual
environment was made available to the export solely for validation: the
negative unittest itself resolves
`tools/schema_suite/.venv/bin/python`. No prototype was rerun, because their
own disposal rules require destructive/ephemeral artifacts to have been removed.

I also searched for approval bypasses, PhaseZero/SteamZero runtime references,
MCP-as-authority claims, unqualified normative language, session-id contracts,
stale-writer paths, secret/memory/removal rules, and stale readiness claims. I
cross-checked the stated prototype and external-audit status with their retained
reports, commands, environments, hashes, stated limitations, and gate criteria.

## Reproduced deterministic gates

| Check | Result | Evidence / limitation |
|---|---|---|
| clean reviewed source | PASS | `git status --porcelain` was empty before review; pin above is exact. |
| foundation lint | PASS | `python3 tools/foundation_lint.py`: 0 errors, 0 warnings, both before and after the schema-suite run. |
| schema suite | PASS | `run_suite.py`: META, SC-01..SC-10 and SEM all PASS (12/12). |
| linter unittest | PASS | `python3 -m unittest tools/tests/test_foundation_lint.py`: 8 tests, OK. A pristine archive lacks the ignored venv, so the test initially cannot locate its declared interpreter; supplying the already-configured validation venv made the documented test run. |
| diff check | PASS | `git diff --check origin/foundation/m00-closure...HEAD` had no output. |
| schema digest | PASS | recomputed SHA-256 `acf63a9476a0d4401eb7557908e4b14d7d9e02d1d0b5de2391bb2868abcebbd1` equals `RESULT.json`; suite result is `passed: true`. |
| PT-01..PT-06 evidence | FAIL as independent evidence | Reports consistently label PT-01/02/03/05/06 PASS and PT-04 PARTIAL, and retain commands/environments/digests/limitations. They do not retain the gate-required raw logs, traces, matrices, or prototype inputs; see RF-03. PT-04's partial verdict itself matches its gate. |
| EA-01..EA-07 pins | PASS, documentary only | `EXTERNAL-AUDITS.md` identifies all seven pins and license/provenance findings. These audits do not repair RF-01..RF-04. |

The audit found no path in the reviewed tree that creates implementation
authority without the owner-only marker; no production dependency on
PhaseZero/SteamZero; and no assertion that MCP supplies an authority boundary.
The documents instead assign authority to policy/confirmation and describe MCP
as transport. The schema suite also rejects tolerant-only records for a write.
Those observations do not overcome the open findings below.

## Findings

### RF-01 — high — contradiction

- **Location:** `docs/adr/ADR-0002-RUST-CORE.md:24-46`;
  `docs/08-testing/prototype-evidence/PT-05-evidence.md:10-13,90-108`;
  `docs/08-testing/prototype-evidence/PT-04-evidence.md:64-72,91-93`.
- **Concrete failure path:** an owner can ratify Rust from PT-05 because
  ADR-0002 says its language gate is PT-05 and explicitly excludes Podman and
  atomic config projection. The retained PT-05/PT-04 evidence says the exact
  opposite: both are outstanding arms of *ADR-0002* and it stays proposed until
  they are proven. Thus the same owner packet can legitimately treat an unmet
  sandbox/projection arm as irrelevant or required.
- **Affected contract:** ADR-0002; M-01/M-04 gate separation; owner packet R-1.
- **Required resolution:** choose one authoritative acceptance predicate for
  ADR-0002, update the ADR, gate ledger, evidence reports, readiness report and
  owner packet consistently, and preserve PT-04/G-05 as an M-04-only block if
  that is the chosen scope. Re-run independent review after reconciliation.
- **Disposition:** open.

### RF-02 — high — contradiction

- **Location:** `docs/adr/ADR-0010-SESSION-LIFECYCLE.md:3,57-71,73-105,138-140`;
  `docs/OWNER-RATIFICATION-PACKET.md:17,31-33`; PT-06 evidence
  `docs/08-testing/prototype-evidence/PT-06-evidence.md:102-104`.
- **Concrete failure path:** R-2 asks the owner to ratify random 128-bit IDs,
  and the ADR's current recommendation says random 128-bit. Its retained
  UUIDv7 table nevertheless marks UUIDv7 as "Chosen (proposed) = yes" and says
  it must receive a benchmark before confirmation. An implementation can pick
  UUIDv7 from the purported decision table or random IDs from the owner packet;
  neither choice has one unambiguous ratified contract.
- **Affected contract:** ADR-0010 lifecycle and session identifier; R-2.
- **Required resolution:** remove or clearly archive the superseded UUIDv7
  choice, state one selected format and its change/compatibility rule, then
  obtain owner ratification against that single text.
- **Disposition:** open.

### RF-03 — high — evidence-gap

- **Location:** `docs/08-testing/PROTOTYPE-GATES.md:22-26,59-66,140-150,193-200,218-223,240-248`;
  `docs/08-testing/prototype-evidence/PT-01-evidence.md:134-137`;
  `PT-02-evidence.md:160-170`; `PT-03-evidence.md:111-118`;
  `PT-04-evidence.md:80-83`; `PT-05-evidence.md:98-102`;
  `PT-06-evidence.md:95-98`.
- **Concrete failure path:** every gate requires retained, inspectable evidence
  (for example per-acquisition log and overlap detector, raw recovery traces,
  operation ledger, containment matrix/resource trace, and clean-host
  transcripts). The six retained Markdown reports give summaries and selected
  values but state that the prototype directories, sources, scripts, binaries,
  and logs were deleted. The reviewed tree contains only these six reports, not
  the required raw artifacts. A reviewer cannot validate that the declared
  command produced the asserted PASS, especially the PT-06 stale-writer
  classifier or PT-05 clean-host assertion. A summary is not the gate-required
  retained artifact.
- **Affected contract:** PT-01..PT-06 pass/fail evidence, G-04/G-05/G-11/G-13,
  ADR-0002, ADR-0010, ADR-0011, and the M-00 high-risk-prototype gate.
- **Required resolution:** retain non-secret, immutable evidence bundles (raw
  logs/matrices/traces, input/source digests and exact harness revision) outside
  the product graph; bind each report to their hashes; then have an independent
  reviewer validate them. Do not rerun destructive prototypes merely to satisfy
  this report without an authorized evidence plan.
- **Disposition:** open.

### RF-04 — high — traceability

- **Location:** `docs/adr/ADR-0010-SESSION-LIFECYCLE.md:51-55,67-68,138-139`;
  `docs/05-data/schemas/` (all nine schemas searched; no `sessionId` contract);
  `docs/06-api/CONTRACTS.md`.
- **Concrete failure path:** ADR-0010 declares the session ID "normatively
  substitutable via the schema" and puts it in MCP `_meta`, but no reviewed
  schema defines `sessionId`, its format, presence, lifecycle binding, version
  transition, or request/response placement. Therefore a client and core can
  each satisfy a different random/UUID interpretation, or reject the `_meta`
  value, with no schema-contract test able to detect it. This also makes the
  claimed ability to change formats without reopening the ADR false.
- **Affected contract:** ADR-0010; SCH/SC schema suite coverage; owner packet
  R-2.
- **Required resolution:** before ratification, add a versioned, traceable
  session lifecycle/identifier contract and valid/invalid compatibility cases,
  or remove the unsupported schema-substitutability claim and explicitly defer
  the interface. A subsequent independent review must validate the choice.
- **Disposition:** open.

## Disposition and decision

All four findings are open and high severity. In particular, the review cannot
accept a PASS on the basis of prototype summaries that omit the evidence the
normative gates demand, nor can it ratify two internally contradictory decision
predicates.

**Decision: FAIL.** The charter permits PASS only with zero open critical and
zero open high findings. This report does not close G-09, does not advance M-00,
and does not create or imply implementation approval.
