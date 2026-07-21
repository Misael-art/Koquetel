# Foundation and implementation roadmap

Status: normative draft  
Last reviewed: 2026-07-21

Implementation phases remain inactive until M-00 exits and approval exists.

## M-00 — Foundation accepted

Deliver source audit, final capability/robustness/gap matrices, owner decisions,
license plan, accepted architecture/security/data/API contracts, the
`PT-01..PT-06` prototype gates (`docs/08-testing/PROTOTYPE-GATES.md`), complete
traceability and independent review.

Exit: every item in `FOUNDATION-GOVERNANCE.md §5` evidenced and readiness report
states `READY FOR IMPLEMENTATION`.

## M-01 — Transactional core

Implement typed domain, state DB, transaction journal, CLI/API, ownership,
install/update/repair/remove, status and doctor. No AI provider required.

Exit: AC-01..04, AC-13 and lifecycle FI/RT suites green in supported Linux matrix.

## M-02 — Essential client capability

Implement canonical profile and first-class Codex, Claude Code, OpenCode and VS
Code adapters; add RTK, Caveman and ai-memory adapter through owned projections.

Exit: AC-02, AC-05, AC-15, AC-16 and adapter round-trip/version fixtures green.

## M-03 — Memory and context fabric

Implement memory envelope, governance, export, conflict/quarantine and bounded
context compiler with retrieval explanations.

Exit: AC-05..07, adversarial memory tests and G-04 recovery prototype green.

## M-04 — Governed tools and sandbox

Implement tool registry, MCP transport, Policy Engine, Secrets Broker, rootless
sandbox and narrow optional privileged helper.

Exit: AC-10..12, all critical SR verification and independent review green.

## M-05 — Economic routing

Implement router adapter, privacy/capability routes, budgets, bounded fallback,
usage/outcome attribution, direct/local provider adapters.

Exit: AC-08..09 meet owner-approved quality/cost thresholds on pinned corpus.

## M-06 — Restartable vibe-coding workflows

Implement task plans, checkpoints, verification, review, child delegations,
evidence reports and governed learning promotion.

Exit: AC-12, AC-14 and representative interrupted end-to-end tasks green.

## M-07 — Expansion

Add adapters only with version fixtures and independent lifecycle evidence. A2A,
team policy and graphical dashboard each require a separate accepted ADR/gate.

