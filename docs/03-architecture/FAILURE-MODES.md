# Failure modes

Status: normative draft  
Last reviewed: 2026-07-21

| ID | Failure | Detection | Required response | Guaranteed final state |
|---|---|---|---|---|
| FM-01 | process killed during config activation | incomplete journal + lease expiry | replay or compensate recorded steps | old or verified new config, never silent mix |
| FM-02 | disk full during stage/journal | write/fsync error | stop before activation; retain diagnostics | active state unchanged |
| FM-03 | user edits managed target after planning | fingerprint mismatch | invalidate plan and confirmation | user edit preserved |
| FM-04 | unknown client config schema | adapter version guard | read-only diagnostic; no projection | client remains launchable |
| FM-05 | memory backend unavailable | health timeout/circuit breaker | local bounded fallback or memory-off mode | task may continue with visible degradation |
| FM-06 | memory corruption or contradictory claim | digest/schema/conflict checks | quarantine; exclude from current retrieval | prior valid memory remains queryable |
| FM-07 | provider unavailable/rate limited | normalized error/timeout | bounded retry then allowed fallback | cost and time ceilings preserved |
| FM-08 | model routing loop | hop/retry budget | terminate and checkpoint | resumable failure with complete usage metadata |
| FM-09 | MCP/tool manifest changes after approval | manifest digest mismatch | deny invocation and require re-admission | no tool side effect |
| FM-10 | tool returns logical error with transport success | typed result validation | record tool failure, never success | workflow chooses retry/compensation explicitly |
| FM-11 | sandbox backend absent | capability probe | deny untrusted execution or request scoped local consent | host not silently exposed |
| FM-12 | sandbox exceeds resources | runtime limit event | terminate process tree and retain bounded logs | host resources recover |
| FM-13 | privileged helper/core version skew | protocol handshake | refuse mutation; keep read-only diagnostics | no privileged action |
| FM-14 | secret appears in output | redaction detector | redact before persistence/export; flag incident | secret not written to managed logs |
| FM-15 | telemetry exporter fails | async queue health | backoff/drop by retention policy | core workflow unaffected |
| FM-16 | child agent exceeds delegation | policy comparison | deny and audit | parent authority unchanged |
| FM-17 | update artifact fails integrity/provenance | signature/digest/source checks | reject before stage | installed version unchanged |
| FM-18 | rollback artifact missing/corrupt | pre-activation rollback validation | block activation | previous version remains active |
| FM-19 | canonical DB migration fails | transactional migration error | rollback DB and binary activation | previous compatible pair active |
| FM-20 | uninstall meets unowned modified file | ownership + fingerprint conflict | preserve file and report residue | user content retained |
| FM-21 | stale-holder write accepted after takeover (TOCTOU) | epoch mismatch between the journal entry's epoch and the current lease epoch, detected during recovery or by a periodic validator | quarantine the affected journal region; fail-closed: no new mutation accepted until reconciliation is complete; external side effects are classified as possibly irreversible and must be reviewed manually (compensation or idempotency key protocol — deferred to future ADR) | not guaranteed while stale writes could have been observed; blocks acceptance of ADR-0011 until G-13 is resolved |
| FM-22 | epoch counter wraparound or reset after DB restore | monotonic counter check at startup: if the persisted epoch is lower than the last checkpointed epoch, detect before any mutation is accepted | fail-closed: refuse mutations and require controlled rekey (migration to a new epoch namespace). DB restore from backup that reduces the epoch is a realistic risk — rollback/restore procedures must preserve epoch monotonicity or trigger the rekey path | all mutations blocked until rekey completes; epoch namespace is migrated |

