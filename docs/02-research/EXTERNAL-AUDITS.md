# External implementation audits

Status: research; EA-01 (ai-memory), EA-02 (RTK) and EA-03 (MCP) complete; others pending
Last reviewed: 2026-07-21

This file holds implementation-level audits of external projects that could
become a Koquetel dependency or adapter base. It complements the local-source
audit in [`SCRIPT-INVENTORY.md`](SCRIPT-INVENTORY.md) and obeys the same evidence
rules: pinned commit, verified license, structural files read fully with digests,
and every claim carrying exact file and line references.

No audit below authorizes reuse; reuse still passes [`../11-legal/REUSE-POLICY.md`](../11-legal/REUSE-POLICY.md)
and the attribution plan (Q-02 selected Apache-2.0 in
[`../adr/ADR-0006-FOUNDATION-OWNER-DECISIONS.md`](../adr/ADR-0006-FOUNDATION-OWNER-DECISIONS.md);
G-02 attribution plan still open). A README claim is never implementation
evidence (governance MP-2).

## Audit template (each `EA-xx` must fill all fields)

1. **Pin & license** — commit/tag, license file verified at that commit.
2. **Inventory** — tracked file count, dominant language, test count, module map.
3. **Files read fully** — path, line count, SHA-256.
4. **Positive patterns** — behavior with `file:line`.
5. **Weaknesses / adoption constraints** — behavior with `file:line`, mapped to a
   Koquetel requirement or a prototype gate.
6. **Reuse recommendation** — adapter / concept / reject, and the blocking gaps.

## Audit status

| Project | Pin | License (verified) | Audit |
|---|---|---|---|
| ai-memory | `2a85950` | MIT (root `LICENSE`, © 2026 Fabio Akita) | **EA-01 complete (this pass)** |
| RTK | `66e09cb` | Apache-2.0 | **EA-02 complete (this pass)** |
| MCP | `88191b9` | MIT/Apache-2.0 (transition), docs CC-BY-4.0 | **EA-03 complete (this pass)** |
| LiteLLM | `212a921` | MIT outside `enterprise/` | pending — read router/budget core, exclude `enterprise/` |
| OpenHands | `a1547a9` | MIT outside `enterprise/` | pending — read runtime/sandbox core, exclude `enterprise/` |
| Letta | `b76da90` | Apache-2.0 | pending — read memory-tier model |
| Mem0 | `dd5f7e3` | Apache-2.0 | pending — read vector/graph store |

Pending rows carry no score. They stay unscored until an equivalent EA audit
attaches implementation evidence (`G-03`).

---

## EA-01 — ai-memory `2a85950`

### Pin & license

- Cloned read-only at `2a85950ce8fa5c309fdc3adc481e98a02d824a9f` (equal to the
  observation pin in [`SOURCE-REPOSITORIES.md`](SOURCE-REPOSITORIES.md); the remote
  HEAD matched this commit at audit time).
- Root `LICENSE` is MIT, `Copyright (c) 2026 Fabio Akita` — consistent with
  [`../11-legal/LICENSE-MATRIX.md`](../11-legal/LICENSE-MATRIX.md).

### Inventory

- 480 tracked files. Dominant language **Rust** (180 `.rs`), plus 74 shell, 68
  PowerShell, 57 markdown, 32 `.sql`, 17 `.toml`. A Cargo workspace of crates:
  `ai-memory-cli`, `-consolidate`, `-hooks`, `-llm`, `-mcp`, `-store`, `-web`,
  `-wiki`, `-core`. 32 test paths (Rust integration tests plus shell e2e).
- Persistence is SQLite via `rusqlite`, schema migrations via `refinery`
  (`crates/ai-memory-store/migrations/V01..V20+`). This is directly relevant: the
  memory-backend candidate is itself Rust + SQLite, aligning with the direction of
  proposed [`../adr/ADR-0002-RUST-CORE.md`](../adr/ADR-0002-RUST-CORE.md).

### Files read fully

| Path | Lines | SHA-256 |
|---|---:|---|
| `crates/ai-memory-store/src/migrations.rs` | 144 | `2be282a3138526f279c47ddd7d0adb8aa1cf53a0718eab84092fbbc44db13488` |
| `crates/ai-memory-store/src/maintenance.rs` | 48 | `f1db36884c6dfa72d7ce49f8026c5ae20b007e7f27eda248cf402cc509c97a24` |

Structural sections were also read in `ai-memory-store/src/lib.rs` (store open /
pragmas / migration wiring, lines 60–116) and `writer.rs` (purge/delete surface,
lines 660–700), and the intent header of the concurrency stress test
`crates/ai-memory-mcp/tests/autoscope_stress.rs:1-40`.

### Positive patterns

- **WAL with tuned durability pragmas.** `lib.rs:91-93` sets `journal_mode=WAL`,
  `synchronous=NORMAL`, `busy_timeout=5000` on open — concurrent readers with a
  single writer, and a bounded wait under cross-process contention.
- **Single-writer actor + read-only pool.** The `Store` exposes a `WriterHandle`
  and a `ReaderPool` (`lib.rs:69-73`); `open()` spawns one writer thread that owns
  the write connection (`lib.rs:102-103`), and mutations are messages
  (`writer.rs` `WriteCmd::PurgeProject` over a `oneshot` channel, `writer.rs:667-685`).
  All in-process writes are serialized by construction, so write–write races cannot
  occur within a process.
- **Foreign-key discipline across migrations.** FKs are disabled only inside the
  migration window and re-enabled for runtime (`lib.rs:98-100`).
- **Fail-closed on a store newer than the binary.** When an applied migration is
  above the embedded ceiling, `migrations.rs:31-42` remaps refinery's misleading
  "missing from the filesystem" into an actionable `DataSchemaAhead` error naming
  the offending version; two tests pin the behavior and message
  (`migrations.rs:61-113`). This is exactly the fail-closed-on-unknown-schema
  posture Koquetel requires (NFR-08), demonstrated in a candidate backend.
- **Migration data-preservation is tested.** `migrations.rs:115-143` proves rows
  survive a version step and the new table appears.
- **Deletion transparency.** `purge_project` returns a `PurgeSummary` with
  pre-delete row counts and the on-disk page paths the caller must still remove
  (`writer.rs:660-685`); `delete_workspace` refuses a non-empty workspace unless
  `force` (`writer.rs:690-700`). Purge is audited (`ops.rs` test
  `audit_log_records_purge_project_with_author`, `ops.rs:3950`).
- **Completion recorded only after success.** Maintenance cadence writes
  `last_success_at` after the work, via upsert (`maintenance.rs:40-48`).

### Weaknesses / adoption constraints for Koquetel

- **AC-DUR — memory-content durability tier is not governance-grade.**
  `synchronous=NORMAL` in WAL (`lib.rs:92`) is durable across an application crash
  but can lose the last committed transaction(s) on OS/power loss (SQLite
  semantics). Acceptable for memory *content*, but Koquetel governance/ownership
  and transaction-journal records must not inherit this tier — they need
  `synchronous=FULL`/explicit fsync, which Koquetel already specifies
  (`TRANSACTION-MODEL.md` step 6). Reinforces ADR-0004: Koquetel owns the envelope
  in its own store; ai-memory holds content only.
- **AC-CONC — cross-process write concurrency is unproven for Koquetel's load.**
  The single-writer actor serializes writes *in one process*; across multiple
  ai-memory instances on one DB, isolation relies on `busy_timeout=5000`
  (`lib.rs:93`) with rusqlite's default `DEFERRED` transactions (no `BEGIN
  IMMEDIATE` exists in the workspace source). Under concurrent read-then-write from
  two instances a snapshot conflict can surface as `SQLITE_BUSY` that the busy
  timeout does not resolve. Koquetel's multi-agent memory writes must be validated,
  not assumed — this is the concurrency arm of prototype **PT-03** and gap
  **G-04**.
- **AC-EXP — export is transcript-scoped, not a governed envelope export.** The
  CLI `export_transcript` path (`crates/ai-memory-cli/src/commands/run.rs:782-810`)
  exports session transcripts, not a portable, provenance-bearing memory archive.
  Koquetel must own backend-independent export (FR-05, GA-09, `SCH-10 MemoryExport`).

### Reuse recommendation

- **Adapter, not base or dependency of the core.** ai-memory is a strong first
  memory *content/search* backend behind Koquetel's `MemoryEnvelope` (SCH-09) and
  `AdapterDescriptor` (SCH-08). Its schema-ahead guard and single-writer actor are
  patterns Koquetel independently mirrors; no code is copied pending the
  attribution plan (Q-02 = Apache-2.0 in ADR-0006; G-02 narrowed).
- **Blocking before acceptance:** PT-03 must prove concurrency, corruption
  recovery, export and removal residue with fault injection (G-04). License MIT is
  compatible with likely Koquetel licenses but per-file attribution is still
  required if any code (not just concepts) is ever reused.
- Independence unaffected: ai-memory is an *optional* adapter; its absence must
  degrade to memory-off mode (FM-05), never break lifecycle (P-13, NFR-13).

---

## EA-02 — RTK `66e09cb`

### Pin & license

- Cloned read-only at `66e09cbefe02bf82b159a44278250e45e506810b` (merge PR #2477,
  2026-07-21). Remote HEAD matched the pin.
- Root `LICENSE` is Apache License 2.0, Copyright 2024 rtk-ai and rtk-ai Labs.
  `Cargo.toml:8` declares `license = "Apache 2.0"`.

### Inventory

- 398 tracked files. Dominant language **Rust** (126 `.rs`), plus 111 Markdown,
  65 TOML, 20 shell, 13 JSON, 9 TypeScript, 9 YAML. 6 integration test files
  under `tests/` plus hundreds of inline `#[cfg(test)] mod tests`.

### Files read fully

| Path | Lines | Role |
|---|---|---:|---|
| `src/main.rs` | 3010 | entry point, Clap CLI, `run_fallback()` passthrough |
| `src/core/toml_filter.rs` | 802 | TOML filter pipeline (8 stages) |
| `src/core/filter.rs` | 550 | code comment/body stripping (Minimal/Aggressive) |
| `src/core/stream.rs` | 1131 | streaming exec + stderr preservation |
| `src/core/guard.rs` | 56 | never-worse output guard |
| `src/core/telemetry.rs` | 606 | fire-and-forget usage ping |
| `src/core/tee.rs` | 527 | raw output recovery to disk |
| `src/hooks/hook_cmd.rs` | 641 | PreToolUse hook handlers |
| `src/hooks/rewrite_cmd.rs` | 233 | exit-code protocol for hook |
| `src/hooks/integrity.rs` | 614 | SHA-256 hook tamper detection |
| `src/hooks/permissions.rs` | 1142 | Allow/Ask/Deny rules |
| `src/discover/registry.rs` | 4617 | 400+ regex rewrite rules |
| `install.sh` | 185 | download + SHA-256 checksum |

### Positive patterns

- **Checksum-verified installation.** `install.sh:112-128` downloads
  `checksums.txt`, looks up the asset, calculates SHA-256, aborts on mismatch.
  Bypassable via `RTK_SKIP_CHECKSUM=1` but default is strict.
- **Hook tamper detection.** `integrity.rs:24` stores a SHA-256 sidecar file
  (`.rtk-hook.sha256`); `integrity.rs:280-323` rejects tampered hooks at runtime
  with exit code 1, which makes the agent use the native (unrewritten) command.
- **Never-worse guard.** `guard.rs:6` compares estimated tokens of filtered vs
  raw output — if filtered is larger, raw is emitted. Prevents filter blow-up.
- **Tee recovery.** `tee.rs:1-527` saves raw output to disk on nonzero exit,
  recording a `[full output: ~/path]` message for recovery.
- **Opt-in telemetry, disabled by default.** `telemetry.rs:40-43` requires
  explicit `rtk telemetry enable`; `RTK_TELEMETRY_DISABLED=1` bypasses. The
  binary has no built-in endpoint URL unless compiled with `RTK_TELEMETRY_URL`
  — default build = no telemetry.
- **Exit-code protocol** (`rewrite_cmd.rs:12-37`): `0`=allow rewrite, `1`=no
  RTK equivalent (passthrough), `2`=deny rule matched, `3`=ask rule matched.
  Cleanly separates rewrite from permission decisions.
- **Lossiness tracking.** `toml_filter.rs:504` tracks `None/Tail/Whole`; whole-loss
  falls back to raw output.

### Weaknesses / adoption constraints for Koquetel

- **AC-FILTER — filter pipeline can semantically alter agent-critical output.**
  The TOML pipeline (`toml_filter.rs:490-651`) strips lines, truncates,
  replaces via regex, and short-circuits with canned messages. The Aggressive
  code filter (`filter.rs:244-313`) keeps only signatures + imports and replaces
  implementation bodies with `// ... implementation`. While the never-worse
  guard and lossiness tracking mitigate expansion, **a semantically meaningful
  line removal is not detected or reported** — the agent sees a compressed
  version without knowing what was removed. Koquetel integration must classify
  which commands may never be filtered (e.g., `git status`, error output), or
  must log the lossiness chain for agent transparency.
- **AC-DENY — deny rules can block commands without agent awareness.**
  `permissions.rs` supports Allow/Ask/Deny; a Deny match returns exit code 2,
  which the hook interprets as "agent's native deny". The agent never knows RTK
  denied the command. Koquetel's policy layer must be explicit about what can
  be silently denied vs. what requires agent/user visibility.
- **AC-NO-LOCK — no lock or heartbeat mechanism exists in the audited source.**
  A search of all Rust source files at the pinned commit found zero references to
  `flock`, pidfile, lock file, or heartbeat. RTK passes `--no-optional-locks` to
  Git but has no cross-process lease of its own. If Koquetel's RTK adapter ever
  needs to coordinate write access to a shared resource, it must add a locking
  layer independently (see PT-01/PT-06).
- **AC-UPDATE — no self-update in binary.** `install.sh` is the only update
  path; RTK itself has no `rtk self-update` command. Koquetel needs a managed
  update channel with digest verification.
- **AC-TELEMETRY — telemetry is fire-and-forget, no retry.** `telemetry.rs:66-68`
  uses a 2-second timeout and silently ignores errors. Acceptable for optional
  usage stats but not for Koquetel-required audit events.

### Reuse recommendation

- **Optional adapter, not dependency.** RTK is a shell-economy adapter candidate
  (`GAP-ANALYSIS.md`, `CONCEPT-PROVENANCE.md`). Its value is token compression
  for agent command output. Koquetel integration would be via the exit-code
  protocol and the TOML filter pipeline, adapted behind Koquetel's policy layer.
- **Blocking before acceptance:** a Koquetel policy must classify which commands
  are filterable vs. pass-through; the lossiness chain must be surfaced to the
  agent. License Apache-2.0 is compatible with likely Koquetel licenses.
- Independence unaffected: RTK is optional; its absence must degrade to
  no-compression mode, never block lifecycle (P-13, NFR-13).

---

## EA-03 — MCP `88191b9`

### Pin & license

- Repository cloned read-only at `88191b9f574d67d553ea9372278a14e09d762f55`
  (branch `draft`). Remote HEAD matched the pin at audit time (2026-07-21).
- At this commit the spec protocol version string is `"2026-07-28"` (visible in
  the `_meta` field table at `basic/index.mdx`). This is the draft protocol's
  version identifier, not a document publication date — the spec branch is a
  living draft, and the version string represents the next planned protocol
  revision. The commit date itself is on or before 2026-07-21.
- **Three-license transition state** (`LICENSE`):
  - **Apache-2.0**: all new code and specification contributions.
  - **MIT (transitory)**: contributions from authors who originally used MIT
    and have not granted relicensing permission.
  - **CC-BY-4.0**: documentation contributions (excluding specification).
- The `README.md` superficially states MIT, but the `LICENSE` file overrides
  with the tri-license regime. Specification documents under
  `docs/specification/draft/` are Apache-2.0 (or MIT transitory).

### Inventory

No code inventory — MCP is a **specification**, not an implementation.
Implementation inventories apply to SDK implementations (not in scope here).
Tracked files include 90+ MDX spec documents, a TypeScript schema
(`schema/draft/schema.ts`), and community/governance docs.

### Normative documents

All specification documents under `docs/specification/draft/` are **normative**:
- `index.mdx` — RFC 2119 keywords, principles, security
- `basic/index.mdx` — message format, error codes, JSON Schema, `$ref`
- `basic/versioning.mdx` — protocol version negotiation
- `basic/authorization/index.mdx` — OAuth 2.1 authorization
- `basic/transports/index.mdx`, `stdio.mdx`, `streamable-http.mdx`
- `server/tools.mdx`, `server/resources.mdx`, `server/prompts.mdx`
- `client/elicitation.mdx`, `client/sampling.mdx` (obsolete)
- `schema.mdx` — derived from `schema.ts`
- `changelog.mdx`, `deprecated.mdx`

Non-normative: `README.md`, `AGENTS.md`, `CLAUDE.md`, `SECURITY.md`,
`CONTRIBUTING.md`, `GOVERNANCE.md`, `blog/`, `docs/community/`.

### Authorization model

Authorization is **optional and transport-level**, specified at
`docs/specification/draft/basic/authorization/index.mdx`:

- **HTTP transport:** implementations SHOULD (draft: SHOULD) use OAuth 2.1
  (draft-ietf-oauth-v2-1-13) with Bearer token (RFC 6750).
- **stdio transport:** MUST NOT follow the OAuth spec; instead "recover
  credentials from the environment".
- **Custom transports:** clients and servers MAY negotiate custom auth strategies.
- **PKCE with S256 is REQUIRED.**
- **Resource indicators (RFC 8707) REQUIRED.**
- **Issuer validation (RFC 9207) REQUIRED.**
- **Token audience validation REQUIRED.**
- **Client credential methods:** Metadata Documents (preferred), pre-registration,
  Dynamic Client Registration (obsolete).

**What MCP leaves to the host:** "The details of the authorization server
implementation are beyond the scope of this specification" (authorization/index.mdx).
Token storage, consent UI, token issuance policy, scope definitions are all
host responsibilities.

### Consent for tool execution

The spec requires consent but **cannot enforce it at the protocol level**:

- `index.mdx` ("Security and Trust and Safety"): "Users should explicitly consent
  to and understand all data access and operations" and "Hosts MUST obtain
  explicit user consent before invoking any tool."
- `server/tools.mdx` ("User Interaction Model"): "There MUST always be a
  human-in-the-loop with the ability to deny tool invocations."
- However, the spec also states: "While the MCP itself cannot enforce these
  security principles at the protocol level" — consent is a **host responsibility**,
  not a protocol invariant.

### Tool result errors

Two distinct error mechanisms (`server/tools.mdx` "Error Handling"):

1. **Protocol errors** (unknown tool, malformed request): standard JSON-RPC error.
2. **Tool execution errors** (business failures): `CallToolResult.isError: boolean`
   flag in the result object. The LLM receives the error content for self-correction.

The `ToolCallResult` schema (`schema.ts`) includes `isError?: boolean` and
`content: (TextContent | ImageContent | AudioContent | ResourceLinkContent | EmbeddedResource)[]`.

### Transports

Two standard transports (`basic/transports/index.mdx`):

1. **stdio** (`transports/stdio.mdx`): newline-delimited JSON-RPC over subprocess
   stdin/stdout; stderr for logs (not errors). Client restarts on unexpected
   termination. No metadata headers — all metadata inline in JSON-RPC body.
2. **Streamable HTTP** (`transports/streamable-http.mdx`): single POST endpoint;
   response is `application/json` or `text/event-stream` (SSE). Metadata mirrored
   as HTTP headers (`MCP-Protocol-Version`, `Mcp-Method`, etc.). Origin header
   validation required.

Obsolete: HTTP+SSE (2024-11-05), deprecated since 2025-03-26.

Custom transports: MAY be implemented, MUST preserve JSON-RPC and per-request
metadata model, MUST document connection establishment and cancellation.

### Lifecycle

MCP is a **stateless protocol** (`basic/index.mdx` "Statelessness"):

- The `initialize`/`notifications/initialized` handshake was removed in the
  draft revision. The `Mcp-Session-Id` header was removed from Streamable HTTP.
- Each request carries its protocol version and capabilities in `_meta`.
- Lifecycle is per-request: client sends version + capabilities in `_meta`,
  server accepts or rejects with `UnsupportedProtocolVersionError` (-32022).
- Shutdown: close input stream (stdio) or close SSE stream (HTTP).
- Unexpected termination (stdio): client restarts the process.

### What MCP guarantees

- **Message format:** all messages MUST follow JSON-RPC 2.0.
- **Delivery:** a transport MUST deliver requests/notifications client→server and
  responses/notifications server→client.
- **Statelessness:** servers MUST NOT rely on previous requests on the same
  connection for context (version, capabilities, identity).
- **Version negotiation:** servers MUST respond with `UnsupportedProtocolVersionError`
  if the requested version is not supported.
- **List immutability:** tool/resource sets MUST NOT vary per connection or as
  a side effect of other requests.
- **Token validation:** MCP servers MUST validate access tokens before processing.
- **No token passthrough:** MCP server MUST NOT pass the token received from
  MCP client to any other service.

### What MCP explicitly leaves to the host

1. **Consent and authorization UI** — protocol cannot enforce.
2. **User interaction model for tools** — protocol does not prescribe.
3. **LLM model selection** — client MAY modify/ignore sampling metadata.
4. **Sandboxing and isolation** — host responsibility.
5. **Authorization server implementation** — beyond spec scope.
6. **Secure token storage** — host responsibility.
7. **Disambiguation strategy** for conflicting tool names — host responsibility.
8. **Local error handling** (timeouts, etc.) — not assigned error codes.

### Why MCP is transport, never authority boundary

Evidence across the specification:

1. **Trust model** (`SECURITY.md`): "MCP clients trust MCP servers they connect
   to" — trust is an operator decision, not enforced by protocol.
2. **No authority boundary in stdio** (`SECURITY.md`): "A malicious server already
   has arbitrary code execution by virtue of being run, and a malicious client
   already has full process control."
3. **Self-reported metadata**: `clientInfo` and `serverInfo` are self-reported and
   "MUST NOT be used for security decisions" (basic/index.mdx).
4. **Per-request capabilities**: servers MUST NOT infer capabilities from prior
   requests — no authority establishment.
5. **Transport is a binding**: "a transport defines how messages are framed and
   delivered... It does not define what the messages mean" (transports/index.mdx).
6. **Custom transports**: protocol is transport-agnostic ("The protocol is
   transport-agnostic and can be implemented over any communication channel").
7. **Optional authorization**: only for HTTP, delegated to OAuth 2.1.
8. **`requestState` is attacker-controlled**: "If a client request contains a
   `requestState` field, servers MUST treat `requestState` as attacker-controlled
   input" (MRTR, server requirements).

### Security considerations

Documented across several files:
- Authorization: token binding (RFC 8707), PKCE S256 (required), issuer
  validation (RFC 9207), confused deputy, SSRF on Metadata Documents.
- Tools: input validation, access controls, rate limits, output sanitisation.
- Resources: URI validation, directory traversal prevention.
- Sampling: user approval controls, data validation, iteration limits.
- Elicitation: server identity binding, phishing (URLs must not be pre-fetched,
  no form-mode for passwords/API keys).
- `$ref`: MUST NOT auto-fetch network `$ref`, opt-in only with host allowlist.
- Icons: HTTPS or `data:` URIs only, MIME validation via magic bytes.

### Reuse recommendation

- **Transport standard, not dependency.** MCP is the tool/transport binding
  Koquetel should implement via adapter, not import as a library. Its value is
  the message shape (JSON-RPC), transport bindings (stdio/HTTP), and the
  error/progress/transaction patterns.
- **Koquetel must add its own authority layer.** MCP explicitly does not provide
  one. Koquetel's admission, policy and consent layer (SR-01..SR-16) sits on top
  of MCP transport — MCP models the *mechanism*, Koquetel provides the *policy*.
- **No code copied.** All specification content is Apache-2.0 (or MIT transitory);
  any implementation must be Koquetel's own. License compatibility: Apache-2.0
  and MIT are compatible with likely Koquetel licenses.
- Independence unaffected: MCP is a specification, not a runtime dependency.
  Koquetel can implement MCP-compatible transport without importing any MCP
  code (P-13, IT-01..IT-03).
