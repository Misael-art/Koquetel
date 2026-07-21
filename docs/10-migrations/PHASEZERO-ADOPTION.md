# PhaseZero adoption strategy

Status: research  
Last reviewed: 2026-07-21

PhaseZero is a research source, not a Koquetel runtime, build, test, install,
update, recovery or removal dependency. SteamZero is likewise research-only and
has no migration role. Koquetel must retain every capability when both projects,
their repositories, commands, services and data directories are absent.

## Candidate concepts

- checksum-verified RTK installation and degraded fallback;
- marked-block projection into multiple client rule formats;
- ai-memory service and client wiring;
- multi-client MCP config projection, backups and doctor output;
- user-scoped services and status JSON;
- explicit admin bridge without stored password;
- OpenCode CLI/desktop version-skew detection;
- local gateway health, budgets and wrapper-based client injection.

These are behavioral research candidates, not permission to copy code.

## Migration tool boundary

A future optional importer reads an offline snapshot, emits a plan, and copies only
selected user state into Koquetel schemas. The importer is a separate removable
package, excluded from the default build/runtime dependency graph. It must:

- work without importing PhaseZero modules or executing PhaseZero scripts;
- work without a PhaseZero checkout, service or command installed;
- never mutate the source;
- identify unknown/secret fields and exclude them by default;
- preserve original source path/version and content digest;
- support dry-run, selective import and repeatability;
- leave source data intact after success;
- be removable without affecting Koquetel runtime.
- never make a migrated Koquetel installation depend on the source snapshot after
  import commit.
