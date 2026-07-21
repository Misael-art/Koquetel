# Installation, update and recovery operations

Status: normative draft  
Last reviewed: 2026-07-21

## Installation scopes

The default is per-user. System-wide installation and privileged helper are
separate plan items with separate confirmation. Repository initialization is
always explicit per path and never recursively enrolls projects.

## Profiles

- `essential`: core, client bridge, RTK, Caveman, memory adapter and safe local
  MCP projection;
- `balanced`: essential plus context compiler, router, budget, event journal and
  rootless sandbox; recommended provisional default;
- `autonomous`: balanced plus background workflows and multiagent delegation;
  never enables broader authority automatically.

Profiles select components, not security bypasses. Missing optional components
produce a degraded result; missing required containment or ownership proof blocks
the affected action.

## Updates

Discovery is automatic only when enabled; activation is a transaction. Each
release records source commit, dependency lock, artifact digest, schema range and
rollback compatibility. Core, DB migration and required adapters activate as one
compatibility set.

## Doctor and support bundle

`doctor` validates ownership, versions, socket/service, DB/schema, transactions,
adapter drift, memory health, router health, sandbox, policy, disk space and
rollback availability. Support bundles contain manifest, redacted states, recent
metadata events and chosen diagnostics. Content is excluded unless explicitly
requested and previewed.

## Recovery runbook order

1. Stop new mutations; preserve read-only status.
2. Inspect incomplete transaction and ownership evidence.
3. Validate backup and target fingerprints.
4. Replay safe pending verification or run recorded compensation.
5. If user state conflicts, stop and produce exact manual alternatives.
6. Re-run doctor and export evidence.
7. Never delete the journal before a terminal recovery record exists.

## Removal

Removal supports `preserve-data` default, `export-then-remove`, and explicit
`purge-owned-data`. It remains offline, does not uninstall third-party agents and
does not delete configurations lacking Koquetel ownership proof.

