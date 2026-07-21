# Threat model and security requirements

Status: normative draft  
Last reviewed: 2026-07-21

## Protected assets

Source code, uncommitted work, credentials, memory, provider budgets, user
identity, client configuration, host integrity, audit evidence and authority
delegations.

## Threat actors and inputs

- malicious repository content and prompt injection;
- compromised MCP/tool server or package;
- untrusted generated code and dependencies;
- compromised or mistaken model/agent;
- local process under the same user;
- remote provider or telemetry destination;
- accidental operator action and configuration drift.

## Security requirements

- **SR-01 Authority separation:** model text, memory and tool output cannot grant
  capabilities. Only Policy Engine and an authenticated user delegation can.
- **SR-02 Least privilege:** default workspace access is read-only until the
  active workflow requires scoped writes; host-admin and destructive are denied.
- **SR-03 Tool admission:** every executable tool version requires provenance,
  integrity, declared capabilities, schema validation and health verification.
- **SR-04 Plan-bound consent:** confirmation binds actor, plan hash, capability,
  target and expiry; it is single-use unless explicitly delegated.
- **SR-05 Secret references:** canonical state stores references, never raw
  secrets. Secrets are materialized only into the authorized child process.
- **SR-06 Output redaction:** persisted/exported events pass structured and
  entropy/pattern redaction; raw content capture is opt-in and separately keyed.
- **SR-07 Sandbox default:** untrusted code receives explicit mounts, environment,
  network allowlist and resource limits; engine sockets are never mounted.
- **SR-08 Path safety:** all target paths are absolute after resolution, confined
  to allowed roots, and checked against symlink traversal and race replacement.
- **SR-09 Supply chain:** release and tool artifacts are pinned, digest verified
  and linked to origin; update discovery never implies automatic activation.
- **SR-10 Audit integrity:** mutation and authority records are append-only with
  chained digests and monotonic sequence within an installation.
- **SR-11 Memory isolation:** memory reads/writes enforce user, project, worktree,
  sensitivity and agent-delegation scopes before semantic ranking.
- **SR-12 Memory governance:** retrieved memory is untrusted data, visibly
  delimited, provenance-bearing and unable to override higher-priority policy.
- **SR-13 Local API protection:** Unix socket permissions restrict the owning user;
  privileged operations use a separate authenticated narrow protocol.
- **SR-14 Network governance:** each remote destination is attributable to a
  configured backend and evaluated against data classification.
- **SR-15 Safe removal:** uninstall removes only proven owned artifacts and never
  requires a remote service or model.
- **SR-16 Delegation attenuation:** child workflows can only receive subsets of
  parent capabilities, budgets, time and memory scopes.

## Threat/control/verification matrix

| Threat | Primary controls | Required verification |
|---|---|---|
| repository prompt asks agent to exfiltrate secrets | SR-01, SR-05, SR-07, SR-14 | malicious-repo security suite |
| tool server changes behavior after approval | SR-03, SR-09 | manifest swap and digest mismatch test |
| symlink redirects managed write | SR-08 | race and traversal tests |
| poisoned memory overrides policy | SR-01, SR-11, SR-12 | adversarial memory retrieval tests |
| runaway agent spends budget | FR-15, SR-16 | retry/fallback/delegation ceiling tests |
| support bundle leaks credential | SR-05, SR-06 | seeded-secret canary tests |
| compromised update replaces core | SR-09, transaction invariants | provenance and rollback tests |
| local process calls privileged helper | SR-04, SR-13 | protocol authentication/replay tests |

## Required independent review

Before external tools or privileged operations ship, a reviewer not responsible
for their implementation must attempt prompt injection, confused-deputy attacks,
manifest substitution, path races, secret leakage and recovery bypass. G-09 stays
open until evidence is attached.

