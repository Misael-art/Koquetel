# Risk register

Status: living document  
Last reviewed: 2026-07-21

Scale: probability and impact 1–5; score is product.

| ID | Risk | P | I | Score | Mitigation / trigger |
|---|---|---:|---:|---:|---|
| R-01 | automation amplifies host damage | 3 | 5 | 15 | central policy, sandbox, plan-bound consent; stop expansion after any containment failure |
| R-02 | poisoned/incorrect memory creates persistent errors | 4 | 5 | 20 | provenance, candidate validation, quarantine, adversarial evaluation |
| R-03 | client config churn breaks adapters | 5 | 4 | 20 | pinned ranges, fixtures, fail-closed mutation, upstream monitoring |
| R-04 | provider routing reduces task quality to save cost | 4 | 4 | 16 | accepted-outcome metric and pinned corpus; disable auto-route on regression |
| R-05 | scope grows into installing every AI product | 5 | 4 | 20 | v1 boundary, capability ports, evidence gate per adapter |
| R-06 | Bash patterns copied before architecture/license review | 3 | 4 | 12 | active legal block and clean-room policy |
| R-07 | local-first promise undermined by hidden remote calls | 3 | 5 | 15 | destination inventory, network policy, offline tests |
| R-08 | sandbox harms performance or developer workflow | 4 | 3 | 12 | benchmark prototype, cached images, explicit trusted-local mode |
| R-09 | telemetry/support evidence leaks code or secrets | 3 | 5 | 15 | metadata-only default, canaries, preview, separate content key |
| R-10 | transaction framework gives false rollback confidence | 3 | 5 | 15 | kill every step, corrupt backups, physical-host validation |
| R-11 | upstream tool abandonment or license change | 4 | 3 | 12 | replaceable adapters, export, pinned versions and source review |
| R-12 | background agents create invisible spend/work | 4 | 4 | 16 | disabled autonomous profile by default, budgets, leases, visible tasks |
| R-13 | documentation becomes contradictory as it grows | 4 | 4 | 16 | precedence, IDs, traceability lint and independent review |
| R-14 | one-user design blocks later teams | 3 | 3 | 9 | explicit identity/scope fields without v1 team control plane |

