# External implementation audits

Status: research; EA-01 (ai-memory), EA-02 (RTK), EA-03 (MCP), EA-04 (LiteLLM),
EA-05 (OpenHands), EA-06 (Letta), EA-07 (Mem0) complete
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
| ai-memory | `2a85950` | MIT (root `LICENSE`, © 2026 Fabio Akita) | **EA-01 complete** |
| RTK | `66e09cb` | Apache-2.0 | **EA-02 complete** |
| MCP | `88191b9` | MIT/Apache-2.0 (transition), docs CC-BY-4.0 | **EA-03 complete** |
| LiteLLM | `212a921` | MIT outside `enterprise/`; commercial inside `enterprise/` | **EA-04 complete** |
| OpenHands | `a1547a9` | MIT outside `enterprise/`; PolyForm Free Trial inside `enterprise/` | **EA-05 complete** |
| Letta | `b76da90` | Apache-2.0 (repo in maintenance mode) | **EA-06 complete** |
| Mem0 | `dd5f7e3` | Apache-2.0 | **EA-07 complete** |
| Caveman | (not yet pinned) | (claimed MIT, unverified) | identity confirmed; pin + audit deferred to M-02 adapter work |

Pending rows carry no score. They stay unscored until an equivalent EA audit
attaches implementation evidence (`G-03` — now closed for the four priority
candidates).

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

---

## EA-04 — LiteLLM `212a9213c4997a4957dfb9337d3f7a94ca138fba`

### Pin & license

- Cloned read-only (`--filter=blob:none`) and checked out
  `212a9213c4997a4957dfb9337d3f7a94ca138fba` — equal to the observation pin in
  [`SOURCE-REPOSITORIES.md`](SOURCE-REPOSITORIES.md). Remote HEAD matched the
  pin at audit time (2026-07-21).
- `git log -1`: commit `212a9213c4997a4957dfb9337d3f7a94ca138fba`, committed
  **2026-07-21 10:28:49 -0700**, `refactor(ui): migrate agents table onto the
  shared DataTable (#34089)`. `pyproject.toml:3` declares `version = "1.94.0"`.
- **Dual-license regime** — root `LICENSE` is itself the demarcation file: lines
  1–4 state "All content that resides under the `enterprise/` directory ... is
  licensed under the license defined in `enterprise/LICENSE`. Content outside
  ... is available under the MIT license." The MIT block follows (lines 6–26),
  `Copyright (c) 2023 Berri AI`. `pyproject.toml:6` declares `license = "MIT"`
  with `license-files = ["LICENSE"]`.
- `enterprise/LICENSE.md` (lines 5–25) is the BerriAI Enterprise License:
  production use requires a paid subscription and a valid seat count; copying,
  merging, publishing, distributing, sublicensing or selling the Software is
  **forbidden** (line 24). 200 tracked files live under `enterprise/`; they
  are out of scope for Koquetel reuse.

### Inventory

- **8,839 tracked files.** Dominant language **Python**: 5,011 `.py` (4,872
  outside `enterprise/`, 139 inside). Frontend is TypeScript/React: 1,093 `.tsx`,
  353 `.ts`, 249 `.js`, 162 `.md`, 141 `.sql`, 113 `.rs` (the experimental
  `litellm-rust/` crate, 142 files).
- **Test suite is very large:** 2,637 `.py` files under `tests/` (2,263 matching
  `test_*.py`).
- Module map (top-level, outside `enterprise/`):
  - `litellm/` (3,165 files) — SDK core: provider adapters (`litellm/llms/`),
    the router (`litellm/router.py`, 11,576 lines), `litellm_core_utils/` (75
    files: logging, tokenizers, redaction, duration parsing), `router_strategy/`
    (routing strategies + `budget_limiter.py`), `router_utils/` (cooldown,
    fallback, retry, pre-call checks), `integrations/` (telemetry/loggers),
    `proxy/` (the gateway server), `types/` (pydantic models).
  - `litellm-proxy-extras/` (329 files), `litellm-rust/` (142 files), `ui/`
    (1,627 files), `tests/` (2,879 files), `docker/`, `helm/`, `terraform/`,
    `cookbook/`, `examples/`, `migrations/`.
- `model_prices_and_context_window.json` (45,966 lines) is the bundled
  pricing/context table that drives `response_cost` calculation.

### Files read fully

| Path | Lines | SHA-256 |
|---|---:|---|
| `litellm/router_strategy/budget_limiter.py` | 840 | `51025b2958ecf05fe244a689f1130864713e1017c7a6917ca39be3b3e33e1112` |
| `litellm/router_utils/cooldown_handlers.py` | 420 | `f8c14e57692db7056d1a3239c89e6ae21ae1119913bbad6cb63f7eec442185b8` |
| `litellm/router_utils/handle_error.py` | 96 | `5c90795ad1c88cc600c576af869860afed9c30e77142c3445e8634d06b34497e` |

Structural sections were also read in the main retry/fallback loop
(`litellm/router.py:6356-6668`), the fallback chain
(`litellm/router.py:6094-6353` and
`litellm/router_utils/fallback_event_handler.py:85-165`), the retry constants
(`litellm/constants.py:326-328`, `26-32`, `75-79`), the global logging defaults
(`litellm/__init__.py:194-214`), and the payload schema
(`litellm/types/utils.py:2941-2980`).

### Positive patterns

- **Retry count is bounded by construction.** `async_function_with_retries`
  iterates a fixed `for current_attempt in range(num_retries)`
  (`litellm/router.py:6555`); if `num_retries` is unset it defaults to 0
  (`litellm/router.py:6465`). No path retries forever.
- **Fallback depth is bounded.** `run_async_fallback` has a hard base case
  `if fallback_depth >= max_fallbacks: raise original_exception`
  (`litellm/router_utils/fallback_event_handler.py:118-119`); `max_fallbacks`
  defaults to `ROUTER_MAX_FALLBACKS = 5` (`litellm/constants.py:9`).
- **Exponential backoff with jitter and a server-provided Retry-After.**
  `_calculate_retry_after` honours the HTTP `Retry-After` header when reasonable
  (`0 < retry_after ≤ 60`), otherwise computes
  `INITIAL_RETRY_DELAY * pow(2, attempt)` boxed to `[min_timeout, MAX_RETRY_DELAY]`
  plus `JITTER * random()` (`litellm/utils.py:6400-6423`).
- **Operator-tunable retry classification.** `RetryPolicy` lets operators set
  per-exception retry counts and per-model-group overrides
  (`litellm/router_utils/get_retry_from_policy.py:34-54`).
- **Explicit provider-failure classification.** `_should_retry` retries only on
  408/409/429 and `>= 500`; other 4xx (400/401/403/404) are not retried unless
  additional deployments exist (`litellm/utils.py:6337-6363`).
- **Fail-closed on budget exhaustion.** The budget filter raises
  `ValueError(RouterErrors.no_deployments_with_provider_budget_routing)` when
  every deployment is over budget rather than silently falling through
  (`litellm/router_strategy/budget_limiter.py:182-185`); ceiling check at
  provider (line 234), deployment (line 249) and tag (line 264) granularity.
- **Fail-closed on no-deployment.** When no healthy deployment exists,
  `async_raise_no_deployment_exception` raises `RouterRateLimitError`
  (`litellm/router_utils/handle_error.py:71-96`); it does not fabricate or fall
  open.
- **Spend tracked as a rolling window with explicit reset.**
  `_increment_spend_for_key` stores `provider_budget_start_time:{provider}`
  alongside the spend key and resets both when `current_time - budget_start > ttl`
  (`litellm/router_strategy/budget_limiter.py:455-502`).
- **Most-recent-error raised, not first.** The retry loop overwrites
  `original_exception` on each attempt and raises that at the end
  (`litellm/router.py:6573-6575`, `6618-6628`).
- **Tag budgets are gated behind the Enterprise license.** `_init_tag_budgets`
  refuses to initialise unless `premium_user is True`
  (`litellm/router_strategy/budget_limiter.py:821-826`), so the MIT-licensed
  surface stays self-consistent with its license scope.

### Weaknesses / adoption constraints for Koquetel

- **AC-BUDGET-RESERVE — budgets are post-hoc, not reserved.** Spend is
  incremented only inside `async_log_success_event` *after* the call returns
  (`litellm/router_strategy/budget_limiter.py:398-453`); there is no pre-call
  hold/reservation. A burst of concurrent in-flight requests can all pass the
  filter and collectively overshoot the ceiling. Koquetel needs
  reservation/commit semantics (FR-15/FR-16, GA-05, G-07).
- **AC-COST-ATTR — cost is attributed to the call, never to the task outcome.**
  `response_cost` is attached to the `StandardLoggingPayload`
  (`litellm/types/utils.py:2947, 2973-2974`) but nothing ties that cost to
  whether the requesting task ultimately succeeded (GA-05, FR-17).
- **AC-COOLDOWN-SINGLE — cooldowns are suppressed for single-deployment model
  groups.** `_should_cooldown_deployment` returns `False` for single-deployment
  groups unless 100% of ≥1000 requests failed
  (`litellm/router_utils/cooldown_handlers.py:178-179, 206-208, 212`). A lone
  provider can keep failing without isolation (NFR-06, FR-14).
- **AC-NOISY-CLASSIFY — cooldown classification defaults to "yes" on any error
  and uses substring matching.** `_is_cooldown_required` wraps everything in
  `try/except: return True` (`litellm/router_utils/cooldown_handlers.py:91-93`)
  and excludes `APIConnectionError` by substring-searching the exception
  *message* (lines 57-61). Koquetel routing policy must classify on typed
  status/exception, not string content (FR-14).
- **AC-CONTENT-LOGGED — prompt and completion content flows to all logging
  callbacks by default.** `turn_off_message_logging = False` is the global
  default (`litellm/__init__.py:194`); the `StandardLoggingPayload` carries
  full `messages` and `response` text plus `requester_ip_address`, `user_agent`,
  `end_user`, `metadata` (`litellm/types/utils.py:2970-2975`). Direct SR-14 /
  NFR-06 conflict.
- **AC-SECRETS-IN-ALERTS — exception strings and tracebacks are shipped to
  Slack/Teams.** `send_llm_exception_alert` redacts secrets via key-pattern
  masking but appends `str(original_exception)`, `litellm_debug_info`, and a
  truncated traceback (`litellm/router_utils/handle_error.py:54-68`). Koquetel
  SR-14 requires content-classification before any external egress.
- **AC-DEBUG-LEAK — internal wiring is appended to client-facing exceptions by
  default.** `expose_router_debug_in_errors = True` by default
  (`litellm/__init__.py:201-209`); model_group names, fallback model groups,
  deployment timeouts and fallback-failure details are appended to
  `ProxyException.message` sent to clients (`litellm/router.py:6311-6312`,
  `6342-6351`, `6255-6256`, `6291-6292`). SR-14/NFR-06 conflict.
- **AC-ENV-OVERRIDE — retry and budget constants are env-var overridable with
  no upper bound.** `INITIAL_RETRY_DELAY`, `MAX_RETRY_DELAY`, `JITTER`,
  `DEFAULT_COOLDOWN_TIME_SECONDS`, `ROUTER_MAX_FALLBACKS`, etc. are all
  `os.getenv(...)` reads (`litellm/constants.py:9, 26-32, 75-79`). An operator
  (or compromised env) can multiply blast radius (FR-14/FR-15).
- **AC-NO-OUTCOME-AUTHORITY — routing has no concept of plan-bound authority or
  delegation attenuation.** Nothing binds the chosen deployment to a Koquetel
  plan token, capability scope, or parent delegation (FR-16, GA-07, G-07).
- **AC-PROXY-SCOPE — much of the operationally relevant surface (auth, virtual
  keys, spend management UI, RBAC, audit logs) lives in `litellm/proxy/` or
  `enterprise/`.** Koquetel can only reuse the MIT-licensed SDK/router surface.

### Reuse recommendation

- **Concept source for routing/retry/budget mechanics, not a dependency and not
  an adapter base.** Koquetel should re-implement independently: bounded retry
  with exponential backoff + `Retry-After`, bounded fallback depth, typed retry
  classification overridable per model group, rolling-window budget filters with
  fail-closed exhaustion, and cooldown-based deployment isolation.
- **Blocking gaps before any acceptance:**
  1. Koquetel must add pre-call budget **reservation/commit** (AC-BUDGET-RESERVE;
     FR-15/FR-16/G-07).
  2. Koquetel must bind every routing decision to a **plan token / capability
     scope** and enforce parent→child attenuation (FR-14/FR-16, GA-07).
  3. Koquetel must own **cost-to-task-outcome attribution** (GA-05, FR-17).
  4. Koquetel must override LiteLLM's logging defaults — content-off-by-default,
     typed failure classification, no internal-wiring in client exceptions
     (SR-14/NFR-06).
  5. Cooldown policy must not inherit LiteLLM's single-deployment suppression.
- **No code copied.** MIT outside `enterprise/` is license-compatible with
  Apache-2.0 Koquetel; per-file attribution still required if any code is
  reused. The `enterprise/` tree is commercially licensed and excluded from
  every reuse path.
- **Independence unaffected:** LiteLLM is an *optional* external concept source.
  Its absence must degrade to Koquetel's own router/offline mode (P-13, NFR-13).
  The experimental `litellm-rust/` crate is not the router and is not a
  shortcut (ADR-0002).

---

## EA-05 — OpenHands `a1547a9c0d4ef89cfd3161c530b24f6d8cbc5cae`

### Pin & license

- **Source / pin:** `github.com/All-Hands-AI/openhands.git` (the register lists
  `OpenHands/OpenHands`; the org now resolves to `All-Hands-AI/openhands`). Pin
  `a1547a9c0d4ef89cfd3161c530b24f6d8cbc5cae` reached cleanly via
  `--filter=blob:none` and verified.
- **Commit metadata:** `a1547a9c0 2026-07-21 11:28:37 -0500` "fix(app-server):
  support Bitbucket Data Center personal repos as marketplace sources (#15334)".
- **Repo identity note (load-bearing):** the in-tree `README.md` is for
  **`agent-canvas`** (`ghcr.io/openhands/agent-canvas:1`, README:95-125). The
  classic "OpenHands runtime" tree has been refactored: there is **no `runtime/`
  Python package and no in-tree action-execution / bash server** at this pin.
  The container runtime is pulled from an external image
  (`ghcr.io/openhands/agent-server`) and the in-process bash server comes from
  the external PyPI package **`openhands-agent-server==1.36.0`**
  (`pyproject.toml:62, 251, 353`). That code is not in this clone and was not
  auditable here.
- **License — root:** MIT, `Copyright © 2025`, SPDX `MIT`. `LICENSE:1-30`,
  `pyproject.toml:11`. SHA-256 `90bd960a…83e5bb94`.
- **License — `enterprise/`:** **PolyForm Free Trial 1.0.0**
  (`enterprise/LICENSE:1`, `Copyright (c) 2026 All Hands AI`), with a
  30-day-per-year commercial-use cap (`:38-40`), no-distribution clause
  (`:18-19`), and termination-on-violation (`:57-61`). SHA-256
  `de6a0079…ce1ca627`. Root `LICENSE:1-3` carves `enterprise/` out of MIT.
  **585 tracked files under `enterprise/` are excluded from any reuse.**

### Inventory

- **Tracked files:** 2,562 (1,977 ex-`enterprise/`, 585 in `enterprise/`).
- **Dominant languages (ex-.git):** `.py` 910, `.tsx` 754, `.ts` 532, `.svg`
  124, `.md` 77, `.yml` 36, `.j2` 34. ~41% Python, ~50% TS/TSX.
- **Tests:** 110 `test_*.py` under `tests/`. No sandbox-escape / containment
  suites located.
- **Module map (top-level):**
  - `openhands/` — Python backend: `analytics/`, `app_server/` (main package, 21
    submodules incl. `sandbox/`, `secrets/`, `integrations/`, `mcp/`,
    `user_auth/`, `file_store/`, `web_client/`), `db/`, `server/`.
  - `frontend/` (1,375 files) + `openhands-ui/` (81) — React/TS canvases.
  - `containers/{app,dev}/` — Dockerfiles + entrypoint for the **server** image
    (not the sandbox image).
  - `enterprise/` (585, PolyForm-excluded): SaaS server, billing, sync,
    migrations.
- **Key external deps:** `openhands-sdk==1.36.0`, `openhands-agent-server`,
  `openhands-tools` (PyPI, not in tree); `litellm==1.84.1` (`pyproject.toml:163`);
  `posthog` SDK.
- **No `runtime/` package, no Podman code, no `EventStreamRuntime`/
  `action_execution_server` in tree** — confirmed via directory and symbol
  search.

### Files read fully

| Path | Lines | SHA-256 |
|---|---:|---|
| `LICENSE` | 30 | `90bd960a6d24cce8f64f3f2b9be5923d5b33e2650afd6fb683ced4be83e5bb94` |
| `enterprise/LICENSE` | 91 | `de6a0079a9e2ae8a514ab26d541a0a57b10f10b49a1402d99fab62d88ce1ca627` |
| `containers/app/Dockerfile` | 105 | `68df393343c9d456ddbbbf7e22f60469dc86d1bd8fd232f6de9b5a4357a51705` |
| `containers/app/entrypoint.sh` | 61 | `9df6b2de1a689f136f708a041f475176d1ff9494a11563ffe71817910446b1a` |
| `openhands/app_server/sandbox/docker_sandbox_service.py` | 715 | `34bb7f8a81c81cdb99984718fdf6175b99cbc43aca6043b7506c2cfdec5aaca8` |
| `openhands/app_server/sandbox/docker_sandbox_spec_service.py` | 133 | `a663361ce8a0ea937446ae1b4573a6e7d6d0f41ed3eea5e2c5ed1a100dfb2437` |
| `openhands/app_server/sandbox/process_sandbox_service.py` | 477 | `31a1c2cacda2caffe36484196498ba3c55e8f54e5e777eb0c7130620c4056179` |
| `openhands/app_server/sandbox/sandbox_spec_service.py` | 210 | `ff71e0fb45cda438fbd8253425704746d41f2273d8a3d0aff26b43637962b415` |
| `openhands/app_server/secrets/file_secrets_store.py` | 45 | `7bb66f0fbdd5b901d1c83affa82419f5bdfc51b966e66752fabc58624564522d` |
| `openhands/app_server/secrets/secrets_models.py` | 199 | `afbdbcd2cc7920bb7e815451b50566599ef93eeaff31c935daa0581db86e9808` |
| `openhands/app_server/utils/env_var_validation.py` | 24 | `a89947cbc676ad2608c7ca199411c7dcc768c04f6d7c63c7057418f73f789153` |
| `openhands/app_server/server_config/server_config.py` | 56 | `a8fa8e77beffc6209acf7d091ff66ea6e25e2b371c08eca8ebaf8defc3386c15` |
| `openhands/analytics/analytics_service.py` | 575 | `2c857df969e9e91a1226ccfd4680d595e9cd9f23fb2ebb98f0261d286217abf2` |
| `openhands/analytics/oss_install_id.py` | 39 | `180f7c03e787c34d5066cb7dcd39d67f68be66b76b7ac97ef47ef92eb0e9ed74` |

### Positive patterns

- **Session keys are strong random values:** `session_api_key =
  base62.encodebytes(os.urandom(32))` (256 bits) —
  `docker_sandbox_service.py:414`; sandbox ids use `os.urandom(16)` (`:410`).
- **Session keys are scope- and lifetime-bound:** a key is rejected unless the
  sandbox is in `RUNNING` state, so a leaked key cannot reach secrets after
  pause/stop/delete — `session_auth.py:73-87`.
- **Sandbox-scoped secret endpoint requires key↔sandbox match:**
  `sandbox_router.py:127-143` returns 403 on mismatch.
- **Secret *names* listing returns no raw values:** `sandbox_router.py:157-185`.
- **Pydantic serializers default to redacted form:** `secrets_models.py:58-107`
  redacts both provider tokens and custom secrets unless
  `context={'expose_secrets': True}` is passed explicitly.
- **Container uses an init process for zombie reaping:** `init=True` on
  `docker_client.containers.run` — `docker_sandbox_service.py:498`.
- **Sandbox count ceiling:** `max_num_sandboxes` (default 5) —
  `docker_sandbox_service.py:399, 521, 600-603`.
- **Health-check gate before reporting RUNNING:** startup-grace window
  (`STARTUP_GRACE_SECONDS = 15`, `:46`) and `/health` probe —
  `docker_sandbox_service.py:238-285`.
- **Env-var name validation before secret creation:** regex
  `[a-zA-Z_][a-zA-Z0-9_]*` — `env_var_validation.py:6-11`.
- **Telemetry is consent-gated and OSS profiling is off:** `AnalyticsService.capture`
  returns immediately when `ctx.consented=False` (`analytics_service.py:83-84`).

### Weaknesses / adoption constraints for Koquetel

All of these are blockers for direct reuse of the sandbox core as Koquetel's
PT-04 rootless sandbox:

- **W1 — No resource limits whatsoever.** `docker_client.containers.run(...)` at
  `docker_sandbox_service.py:485-509` passes no `mem_limit`, `nano_cpus`/
  `cpu_quota`, `pids_limit`, `ulimits`, or wall-clock (FM-12, AC-11, PT-04(e),
  G-05).
- **W2 — No network allowlist.** Container runs on Docker's default bridge with
  no egress filtering; `network_mode` is either `None` or `'host'`
  (`docker_sandbox_service.py:470, 506`). (SR-07, SR-14, PT-04(d)).
- **W3 — Host-network mode is a single env var away.** `use_host_network`
  defaults from `AGENT_SERVER_USE_HOST_NETWORK` (`docker_sandbox_service.py:49-56,
  660-669, 470, 472-473, 506`) — fail-open by configuration (SR-07, FM-11).
- **W4 — Host gateway route is wired in by default.** `extra_hosts=
  {'host.docker.internal': 'host-gateway'}` (`docker_sandbox_service.py:644-652`,
  applied at `:502-504`) hands every sandbox a route back to the host network
  (SR-07, SR-14).
- **W5 — No capability / userns / seccomp hardening.** No `cap_drop`,
  `security_opt`, `userns_mode`, or `privileged=False` enforcement. **Zero
  `podman`/`rootless` references in the entire tree.** PT-04's primary
  environment (Podman rootless) is unsupported (SR-07, PT-04, G-05).
- **W6 — The Docker engine socket is mounted in the server image.**
  `containers/app/entrypoint.sh:47` does `stat -c '%g' /var/run/docker.sock` and
  joins that group so the in-image user can talk to the engine. SR-07 forbids
  this exact pattern (SR-07, PT-04(c), SR-02).
- **W7 — Sandbox mounts are unvalidated.** `SANDBOX_VOLUMES` is parsed by
  splitting on `,` then `:` and the host path is taken verbatim —
  `config.py:361-385`. No absoluteness check, no symlink resolution, no
  confinement, no race check (SR-07, SR-08, PT-04(a)).
- **W8 — Host environment is wholesale copied into process sandboxes.**
  `process_sandbox_service.py:125` does `env = os.environ.copy()` then layers
  `sandbox_spec.initial_env` and `SESSION_API_KEY` (SR-05, SR-07, PT-04(b)).
- **W9 — Secrets are persisted in cleartext JSON.**
  `file_secrets_store.py:32-34` writes
  `secrets.model_dump_json(context={'expose_secrets': True})` to `secrets.json`
  (SR-05, SR-06, PT-04(b)).
- **W10 — Auto-forwarded host env vars leak into every container.**
  `AUTO_FORWARD_PREFIXES = ('LLM_', 'LMNR_')` (`sandbox_spec_service.py:151`);
  `get_agent_server_env` copies every host var with those prefixes into the
  sandbox env (`:198-210`), including telemetry API keys (SR-05, SR-14, NG-05,
  PT-04(b)).
- **W11 — Webhook callback URL embeds the host port.**
  `env_vars[WEBHOOK_CALLBACK_VARIABLE] = f'http://host.docker.internal:{self.host_port}/api/v1/webhooks'`
  (`docker_sandbox_service.py:419-421`) (SR-07, SR-14).
- **W12 — Telemetry has a persistent install identity and a hardcoded PostHog
  key.** `oss_install_id.py:21-37` writes/reads `analytics_id.txt`;
  `server_config.py:12` hardcodes `posthog_client_key = 'phc_3ESM…'` (NG-05,
  SR-14, G-05).
- **W13 — "Without a Sandbox" is a supported mode.** README:69 ships an option
  that runs the agent directly on the host with full filesystem access; no
  consent gate (FM-11, SR-02, PT-04).
- **W14 — Image is pulled on first use by digest-less tag.**
  `docker_sandbox_spec_service.py:60-66, 78-92` pulls `ghcr.io/openhands/
  agent-server:<bundled>-python` when missing; tag auto-rewrites to match the
  installed SDK. No digest pinning, no signature verification (SR-09).
- **W15 — Sandbox deletion stops with a 10s timeout and ignores archive failure
  by default.** `docker_sandbox_service.py:559-572`; `RUNTIME_FILE_ARCHIVE_REQUIRED`
  defaults to `false` (PT-04 Disposal, SR-10).
- **W16 — Runtime backend is chosen by env var with no capability probe.**
  `RUNTIME` env selects Docker / remote / process (`config.py:388-394`). FM-11
  expects a capability probe that denies untrusted execution when no sandbox is
  fit; absence silently downgrades.
- **W17 — Security-critical runtime code is not in this repository.** The
  in-container action/bash server is the external `openhands-agent-server==1.36.0`
  package and the `ghcr.io/openhands/agent-server` image; this audit cannot see
  the bash execution, file IO, or syscall surface (SR-09, PT-04, G-09).

### Reuse recommendation

**Recommendation: do NOT adopt OpenHands as Koquetel's sandbox runtime; at most
treat it as a reference for an adapter / clean-room concept, and only for the
orchestration layer (lifecycle, ports, session-key auth).**

Blocking gaps (six):

1. Containment defaults are inverted vs SR-07 (no limits W1, no network
   allowlist W2, host-network one env var away W3, `host.docker.internal` route
   by default W4, no cap/userns/seccomp/Podman-rootless support W5, engine
   socket mounted W6). PT-04 would fail every row of its containment matrix.
2. Path safety is absent (W7). SR-08 cannot be patched at the adapter layer.
3. Secret handling violates SR-05 in three independent ways (W8, W9, W10).
4. The actual sandbox runtime is unauditable from this pin (W17).
5. Supply chain (W14). Tag-based, digest-less image pulls with auto-rewrite.
6. Telemetry footprint (W12).

Adapter / clean-room concept worth retaining (positive evidence only): the
`SandboxService` ABC + `DockerSandboxService` shape, the `max_num_sandboxes`
ceiling, the `init=True` zombie-reaping choice, the running-state-bound session
key, the consent-gated metadata-only telemetry vocabulary, the secret-name
listing without values, and the redact-by-default Pydantic serializers. None of
these licenses reuse; each must be reimplemented natively against a rootless
Podman backend.

License: the MIT-licensed portion is referenceable by a documentation-only
foundation; the `enterprise/` PolyForm-Free-Trial subtree (585 files) is
excluded from all reuse. No dependency on OpenHands is proposed or implied.

---

## EA-06 — Letta `b76da9092518cbaa2d09042e52fdcbde69243e18`

### Pin & license

- **Pinned commit:** `b76da9092518cbaa2d09042e52fdcbde69243e18`, committed
  `2026-07-03 11:53:39 -0700`, `docs: update README to Letta Agent SDK, add
  AGENTS.md deprecation notice (#3393)`. Matches the pin in
  [`SOURCE-REPOSITORIES.md`](SOURCE-REPOSITORIES.md).
- **License:** Root `LICENSE` is canonical Apache License 2.0 (`LICENSE:1-4`).
  `pyproject.toml:8` declares `license = {text = "Apache License"}`. SPDX:
  **Apache-2.0**. Copyright `Copyright 2023, Letta authors` (`LICENSE:178`). No
  `NOTICE` file and no per-subdirectory `LICENSE`; a single repo-wide Apache-2.0
  applies.
- **Repository status (load-bearing):** `README.md:9` states "[README claim]
  This repository contains the legacy Letta server ... Active development has
  moved to the letta-ai/letta-code repo." `AGENTS.md:3` states "[README claim]
  This repository is deprecated ... in maintenance mode and is no longer where
  active development happens." Observed behavior at pin confirms this. **This is
  the single biggest adoption constraint.**

### Inventory

- **Tracked file count:** 1156.
- **Dominant language:** Python (878 `.py`, 116 `.json`, 33 `.yml`, 20 `.txt`).
- **LOC:** 248,417 total Python LOC; 137,850 inside `letta/`; 97,808 in `tests/`.
- **Tests:** 93 files matching `tests/**/test_*.py`.
- **Module map (top-level subpackages of `letta/`, by LOC):**
  - `letta/services/` 41,334 (summarizer, block_manager, passage_manager,
    message_manager, archive_manager, agent_serialization_manager, memory_repo/,
    …)
  - `letta/server/` 19,648 (FastAPI REST + WS API)
  - `letta/schemas/` 17,939 (Pydantic models: memory, block, message, passage,
    agent, …)
  - `letta/llm_api/` 9,494, `letta/agents/` 8,050, `letta/local_llm/` 5,471,
    `letta/helpers/` 4,957, `letta/orm/` 4,919 (47 ORM models including
    `passage.py`, `message.py`, `block.py`, `block_history.py`, `source.py`,
    `archive.py`)
  - `letta/functions/` 3,851, `letta/interfaces/` 3,721, `letta/otel/` 2,259,
    `letta/groups/` 1,913, `letta/adapters/` 1,404, `letta/prompts/` 1,111.
- **Memory-tier core:** `letta/schemas/memory.py` (in-context/core memory + tier
  summaries), `letta/schemas/block.py`, `letta/services/block_manager*.py` +
  `letta/services/block_manager_git.py`, `letta/orm/passage.py` (archival),
  `letta/orm/message.py` (recall), `letta/orm/block_history.py` (provenance
  snapshots), `letta/services/summarizer/`, `letta/services/memory_repo/`.

### Files read fully

| Path | Lines | SHA-256 |
|---|---:|---|
| `letta/schemas/memory.py` | 884 | `febcd15fa5bad3e73a40d5229f75f747782f046c5e3f3c26b8f5c557403cc91c` |
| `letta/schemas/block.py` | 209 | `db805da329a276532510d9586c85adb49fb36e550da09584dc70d18a927e8f88` |
| `letta/services/block_manager_git.py` | 596 | `02d181eafbc53a8023fb8a3ff257b6a7bc89612d154e6747ed3a6a47051591bc` |
| `letta/orm/passage.py` | 104 | `bf278435c7d7cfa4a1d7f02514a3b2fb1aa9ed0041d70feda25041be295e8a49` |
| `letta/orm/block_history.py` | 48 | `5cb6dd4e473d19afd6e68a25cd13d1c6bcbbc79ad2f8f1ea5b5d4c2a9071cab0` |
| `letta/services/memory_repo/storage/base.py` | 127 | `ef3d39a001a812a359769b380f6f1ef79f84d2c107c3bef9b7c769847bacc63c` |

Also read fully for cross-reference: `letta/orm/message.py` (265 lines, recall
persistence with monotonic `sequence_id`), `letta/services/summarizer/
summarizer_sliding_window.py` (232 lines, the recall-consolidation algorithm).

### Positive patterns

- **Three explicit memory tiers, separated by persistence table and access
  path.** Core (in-context) memory = `Memory`/`Block` rendered into the system
  prompt (`letta/schemas/memory.py:68-77, 142-203`); archival = `ArchivalPassage`
  table (`letta/orm/passage.py:76-104`); recall = `Message` table
  (`letta/orm/message.py:23-91`). The `ContextWindowOverview` model enumerates
  them as distinct counts (`letta/schemas/memory.py:32-45`). Directly relevant
  to ADR-0004 and FR-09..13.
- **Core-memory edits are bounded by per-block limits.** `Block.limit` defaults
  to `CORE_MEMORY_BLOCK_CHAR_LIMIT = 100000` (`letta/constants.py:435`); the
  renderer surfaces `chars_current`/`chars_limit` to the model
  (`letta/schemas/memory.py:161-166`). Directly relevant to ADR-0004.
- **Recall memory is bounded by a sliding-window summarizer with a configurable
  eviction percentage and a token-budget target.** `summarize_via_sliding_window`
  computes `goal_tokens = (1 - sliding_window_percentage) *
  agent_llm_config.context_window` and walks the cutoff up by 10% until the
  post-summary buffer fits (`summarizer_sliding_window.py:152-191`); proactive
  compaction triggers at 90% of context window (`SUMMARIZATION_TRIGGER_MULTIPLIER
  = 0.9`, `letta/constants.py:82-83`). Satisfies the spirit of SR-11.
- **Archival persistence is pluggable across vector DBs.** `BasePassage`
  switches between pgvector and `CommonVector` based on `settings.database_engine`
  (`letta/orm/passage.py:34-40`); optional extras for `postgres` (pgvector),
  `pinecone`, `sqlite` (sqlite-vec), `redis` (`pyproject.toml:89-98`).
- **Memory edits are versioned two ways.** (1) `BlockHistory` rows with
  monotonic `sequence_number`, unique on `(block_id, sequence_number)`
  (`letta/orm/block_history.py:17-48`), written by `checkpoint_block_async` with
  truncation of "future" entries to keep a linear undo/redo stack
  (`letta/services/block_manager.py:874-901`). (2) Optional git-backed
  source-of-truth via `GitEnabledBlockManager` (writes to git first, Postgres is
  a cache) (`letta/services/block_manager_git.py:1-8, 186-285`). Relevant to
  SR-12.
- **Provenance fields exist on memory snapshots.** `BlockHistory` records
  `actor_type` (`ActorType.LETTA_AGENT` vs `LETTA_USER`) and `actor_id` at
  checkpoint time (`letta/orm/block_history.py:36-37`).
- **Storage backend is abstracted behind an ABC.** `StorageBackend`
  (`letta/services/memory_repo/storage/base.py:7-127`) defines
  `upload_bytes`/`download_bytes`/`exists`/`delete`/`list_files`/`delete_prefix`,
  with concrete `local.py`. The seam Koquetel would reuse for a portable
  envelope store.
- **Agent-definition export to JSON exists** (`AgentFileSchema` at
  `letta/schemas/agent_file.py:431-445`; exporter/importer at
  `letta/services/agent_serialization_manager.py:382-494`).

### Weaknesses / adoption constraints for Koquetel

- **Repository is in maintenance mode / deprecated.** `README.md:9` and
  `AGENTS.md:3-6` state active development moved to `letta-ai/letta-code`.
  Depending on this codebase as a runtime dependency is not viable; only
  concept/spec reuse is on the table (ADR-0004).
- **Tight coupling to specific LLM/embedding providers in the persistence path.**
  `letta/services/passage_manager.py:8` imports `AsyncOpenAI` directly and
  `:35-40` hardcodes an OpenAI embeddings client. 51 files import `openai`, 18
  import `anthropic`. `embedding_config` is serialized per-passage
  (`letta/orm/passage.py:29`), so archival rows are bound to the provider that
  produced them. FR-10/FR-11 and PT-03 (provider lock-in).
- **Summarizer/compaction logic is hard-coded to OpenAI/Anthropic tokenizers and
  contains model-family regex special-casing.**
  `letta/services/summarizer/thresholds.py:11-41` special-cases `gpt-5` family
  via regex. SR-11: bounded-recall behavior is provider-dependent.
- **Memory content is logged at INFO by default and captured into OTEL spans.**
  `block_manager_git.py:196-238` emits `logger.info` lines containing `block_id`,
  `label`, commit SHA, and timings on every memory write. The `@trace_method`
  decorator serializes function parameters into span attributes up to
  `MAX_PARAM_SIZE = 2 MB` per param and `MAX_TOTAL_SIZE = 4 MB` total, with only
  an explicit opt-out list (`SKIP_PARAMS`) protecting large objects
  (`letta/otel/tracing.py:250-277`). SR-12 / G-04 / privacy.
- **Provenance on memory edits is partial and only for core memory.**
  `BlockHistory` only snapshots `Block` state — there is no equivalent history
  table for `ArchivalPassage` or `Message` (recall). SR-12 / ADR-0004.
- **Export/portability does not cover the full memory envelope.** `AgentFileSchema`
  includes blocks, files, sources, tools, MCP servers, skills — but **not**
  archival passages, **not** `BlockHistory` (provenance), and only the currently
  in-context slice of recall messages. G-04 (export/portability).
- **Disable does not delete the backing git store.**
  `disable_git_memory_for_agent` only removes the tag and "keeps the git repo
  for historical reference" (`letta/services/block_manager_git.py:485-506`).
  SR-12 / privacy / right-to-be-forgotten.
- **Heavy dependency surface and Python 3.11–3.13 only.** ~70 runtime deps
  including `anthropic`, `openai[realtime]`, `mistralai`, `google-genai`,
  `llama-index`, `temporalio`, `mcp`, `grpcio`, `sentry-sdk`, `ddtrace`.
  `requires-python = "<3.14,>=3.11"`. PT-03 / G-04.
- **Recall sequence correctness relies on SQLite-specific event listeners with
  hand-rolled sequence tables and `RETURNING` fallbacks.** `letta/orm/
  message.py:130-265` maintains a `message_sequence` table via raw SQL on
  SQLite. SR-11.
- **Core-memory value sanitization is lossy.** `BaseBlock.sanitize_value_null_bytes`
  strips null bytes silently before persistence (`letta/schemas/block.py:51-57`).
  SR-12.

### Reuse recommendation

**Recommendation: clean-room concept reuse only. Reject as a dependency (runtime
or vendored).**

1. The project is explicitly deprecated/maintenance-mode at the pinned commit;
   Koquetel must not adopt it as a dependency, and even adapter reuse would
   inherit an unmaintained codebase with ~70 transitive deps.
2. The memory-tier *concepts* are well worth modeling for ADR-0004 and FR-09..13:
   three-tier split, per-block char limits surfaced to the model, sliding-window
   consolidation with token-budget target, dual versioning scheme.
3. The persistence interface abstraction (`StorageBackend` ABC) is a good
   template for an envelope-store port, but the actual implementation is
   OpenAI/Anthropic-coupled and Postgres/pgvector-leaning.

Blocking gaps Koquetel must close independently (none closeable by adopting
Letta): provider-neutral embedding interface; provenance on **archival** and
**recall** edits; full-envelope export including recall history, archival store,
and edit provenance; default-off content telemetry; first-class forget/purge
that includes object-store git history.

Suggested clean-room deliverables: (a) a memory-envelope spec (ADR-0004) modeled
on Letta's tier separation and per-block limits; (b) a bounded-recall policy spec
(SR-11) modeled on the sliding-window + token-budget algorithm but stated
provider-neutrally; (c) a provenance spec (SR-12) that extends `BlockHistory` to
archival and recall tiers with mandatory `actor_type`/`actor_id`/`source` on
every write.

---

## EA-07 — Mem0 `dd5f7e39a86170dd35c6860c854a2b0ef0293b08`

### Pin & license

- Repository cloned read-only via `git clone --filter=blob:none` into
  `/tmp/koquetel-audits/mem0`. Pin matches
  [`SOURCE-REPOSITORIES.md`](SOURCE-REPOSITORIES.md).
- `git log -1 --format='%H %ci'` → `dd5f7e39a86170dd35c6860c854a2b0ef0293b08
  2026-07-21 21:39:00 +0530` "ci: infer component labels for issues filed
  without the form (#6471)".
- `pyproject.toml:7`: `version = "2.0.12"` (name `mem0ai`).
- **License:** Apache-2.0, single project-wide. Root `LICENSE` (11349 B):
  "Apache License, Version 2.0" (LICENSE:1). SHA-256
  `0bbcbe931c353293a2fafce08326181dfeea0e568c566afd4ce8337a70f5e219`.
  Copyright `Copyright [2023] [Taranjeet Singh]` (LICENSE:190). `pyproject.toml:13`:
  `license = "Apache-2.0"`. All other `LICENSE` files under `skills/*` and
  `integrations/*` are also Apache-2.0. No `enterprise/` directory present at
  this pin.

### Inventory

- **Tracked files at pin:** 1812.
- **Dominant languages:** `.ts` 428, `.py` 384, `.mdx` 243, `.tsx` 227, `.md`
  107, `.svg` 83, `.json` 65. Python package = `mem0/` (384 `.py`). TypeScript
  SDK = `mem0-ts/`.
- **Tests:** 95 `test_*.py` under `tests/`.
- **Module map of `mem0/`:**
  - `mem0/memory/` — `base.py`, `main.py` (3787 lines), `storage.py` (SQLite
    history), `telemetry.py` (PostHog), `notices.py` (in-product upsell),
    `setup.py`, `utils.py`.
  - `mem0/vector_stores/` — `base.py` (interface), 25 backend implementations.
  - `mem0/embeddings/`, `mem0/llms/`, `mem0/reranker/`, `mem0/configs/`.
  - `mem0/utils/factory.py` — provider factories. `mem0/proxy/main.py` —
    wrapper that auto-pip-installs `litellm` and routes between local `Memory`
    and hosted `MemoryClient`.
- **Important structural note:** there is **no `mem0/graph_memory/` module and
  no `mem0/graphs/` module** at this pin. `grep -rn "graph_store\|GraphMemory"
  mem0/` only returns `mem0/exceptions.py:396`. The entire `mem0/graphs/` tree
  was deleted by commit `a488e190`. The current v3 design replaces graph edges
  with an **entity vector store** (a second vector collection keyed by
  normalized entity text, `mem0/memory/main.py:534-555`, `_entity_collection_name`
  at `:397`).

### Files read fully

| Path | Lines | SHA-256 |
| --- | --- | --- |
| `mem0/vector_stores/base.py` | 100 | `c9d7f6a5fd6d74411eec0be17b409f69d377630ab85ba0a70f754a6df6215450` |
| `mem0/memory/base.py` | 63 | `bb093eacbeb409b12b043b7df9b3152b895a00bb5ce30776a1e56c915cf17777` |
| `mem0/utils/factory.py` | 277 | `34698fe69f2fb8c718da3872aca0e35fe2913405a8fd7893283f1a5847e050f5` |
| `mem0/memory/telemetry.py` | 241 | `89f36bd0b87059fa0710adcccfbd9639ab4d5c4a762d875a1caceaf688aca687` |
| `mem0/memory/utils.py` | 320 | `dbeba4f50c499fd486cae2250f0a035ff108420b628ea389adb0bd6e1e8f36b88` |

Also read for cross-reference: `mem0/memory/storage.py` (347 lines, SQLite
history store), `mem0/configs/base.py` (82 lines, `MemoryConfig`),
`mem0/vector_stores/configs.py` (60 lines). `mem0/memory/main.py` (3787 lines,
SHA `7aa1a0026056abaea3b3a7653ea0d1753a461d90b83a66c33c680fdac7cb46e`) read in
full section by section (init, add, get/get_all, search, delete/delete_all,
_create_memory, _update_memory, _delete_memory, reset, _search_vector_store,
entity helpers).

### Positive patterns

- **Vector store abstracted behind `VectorStoreBase`** with a uniform 11-method
  contract (`create_col`, `insert`, `search`, `delete`, `update`, `get`,
  `list_cols`, `delete_col`, `col_info`, `list`, `reset`) plus opt-in
  `keyword_search` and `search_batch` defaults — `mem0/vector_stores/base.py:4-99`.
  The `search` docstring pins a similarity convention so different backends
  produce comparable scores (`mem0/vector_stores/base.py:14-26`).
- **Memory lifecycle abstracted behind `MemoryBase`** (`get`, `get_all`, `update`,
  `delete`, `history`) — `mem0/memory/base.py:6-63`.
- **Provider pluggability via string-keyed factories.** `VectorStoreFactory.
  provider_to_class` enumerates 23 vector backends and resolves them by string
  via `importlib.import_module` (`mem0/utils/factory.py:194-220`). `LlmFactory`
  enumerates 18 LLM providers (`:43-63`), `EmbedderFactory` 11 embedders
  (`:162-175`), `RerankerFactory` 5 rerankers (`:249-258`). `LlmFactory.
  register_provider` exposes an extension point (`:120-130`).
- **Backend swapping is config-driven.** `Memory.__init__` reads
  `self.config.vector_store.provider` and calls `VectorStoreFactory.create(...)`
  (`mem0/memory/main.py:471-473`). Default vector provider is `qdrant`.
- **Add path is a phased pipeline.** `Memory.add` (`mem0/memory/main.py:735-847`)
  validates IDs, normalizes expiration, then dispatches to
  `_add_to_vector_store` (`:849-1056`): Phase 1 retrieves existing memories
  (`:896-901`), Phase 2 calls the LLM once with `ADDITIVE_EXTRACTION_PROMPT`
  (`:912-939`), Phase 3 batch-embeds (`:962-964`), Phase 7+ links entities.
  `infer=False` short-circuits the LLM and stores raw messages (`:850-884`).
- **Search path is multi-signal and fused.** `Memory.search`
  (`mem0/memory/main.py:1349-1492`) enforces at least one of
  `user_id`/`agent_id`/`run_id` (`:1427-1431`), supports an advanced filter DSL,
  then `_search_vector_store` (`:1598-1698`) over-fetches
  (`internal_limit = max(limit * 4, 60)` at `:1611`), runs semantic +
  `keyword_search` (BM25) + entity boosts, and fuses via `score_and_rank`
  (`:1650-1657`).
- **Deletion writes audit history.** `_delete_memory` calls
  `self.vector_store.delete(vector_id=memory_id)` (`:2061`) and immediately
  appends a row to the SQLite history table with `event="DELETE"` and
  `is_deleted=1` (`:2062-2072`), preserving `prev_value`, `created_at`,
  `actor_id`, `role`.
- **Entity cleanup is best-effort and non-fatal.**
  `_remove_memory_from_entity_store` (`mem0/memory/main.py:627-680`) strips the
  memory id from `linked_memory_ids` arrays, deleting orphan entity rows or
  re-embedding survivors, with per-row `try/except`.
- **Reset wipes vector + entity + history stores together.** `Memory.reset`
  (`:2080-2110`) drops SQLite tables, recreates a fresh `SQLiteManager`, calls
  `VectorStoreFactory.reset`, and resets the entity store.

### Weaknesses / adoption constraints for Koquetel

- **No graph memory at this pin (despite task framing).** Entities are stored as
  plain vectors in a second collection (`mem0/memory/main.py:534-555`), not as
  typed graph edges. No Cypher/traversal API, no relationship typing beyond an
  `entity_type` string payload. ADR-0004 (vector/graph memory candidate) — Mem0
  at this pin is **vector-only** with a shallow entity-boost layer.
- **Telemetry is on by default and ships a hardcoded PostHog key.**
  `MEM0_TELEMETRY = os.environ.get("MEM0_TELEMETRY", "True")`
  (`mem0/memory/telemetry.py:15`);
  `PROJECT_API_KEY = "phc_hgJkUVJFYtmaJqrvf6CYN67TIQ8yhXAkWzUn9AMU4y"` and
  `HOST = "https://us.i.posthog.com"` (`:17-18`). Default sample rate for hot-
  path OSS events is `0.1` (`:33`). SR-11, G-04.
- **Vector-store class names and provider choices are sent to PostHog.**
  `capture_event` builds a payload with `vector_store`, `llm`, `embedding_model`
  class names, plus `collection` name and `vector_size`
  (`mem0/memory/telemetry.py:206-216`). `Memory.__init__` fires `mem0.init`
  (`mem0/memory/main.py:527`); `search` fires `mem0.search` with `keys` and
  `encoded_ids` (`:1448-1461`). Mitigation: `process_telemetry_filters`
  (`mem0/memory/utils.py:225-240`) MD5-hashes `user_id`/`agent_id`/`run_id`
  before telemetry — but `vector_size`, `collection_name`, and provider class
  names *are* sent. SR-12.
- **No provenance on memory writes.** `_create_memory` stores only `data`,
  `hash` (MD5 of `data`, `:1926`), `created_at`, `updated_at`,
  `text_lemmatized` (`:1924-1930`) plus whatever the caller passed in
  `metadata`. No `source`, `evidence_ref`, `citation`, or `origin` field.
  FR-09.
- **MD5 used as the memory hash.** `hashlib.md5(data.encode()).hexdigest()` at
  `mem0/memory/main.py:1926, 2013`. MD5 is collision-broken; surfaces in
  `MemoryItem.hash` (`mem0/configs/base.py:21`). SR-11.
- **Deletion is soft at the history layer but hard at the vector layer.**
  `_delete_memory` issues `vector_store.delete(vector_id=memory_id)` with no
  tombstone in the vector store; the `is_deleted=1` flag lives only in SQLite.
  `delete_all` iterates and deletes one-by-one — not transactional; a mid-loop
  failure leaves partial state. FR-13, PT-03.
- **No export / portability primitive.** The only way to extract all memories is
  to call `get_all` repeatedly (capped at `top_k`, default 20 —
  `mem0/memory/main.py:1229`). No schema-stable dump. FR-12, ADR-0004.
- **Per-call LLM dependency on the add path.** When `infer=True` (default),
  every `add()` issues an LLM call (`mem0/memory/main.py:925-939`) and raises
  `LLMError` on failure. FR-10 / FR-11.
- **Provider lock-in via defaults and transitive deps.** Default
  `provider="qdrant"`; `qdrant-client`, `openai`, and `posthog` are unconditional
  runtime deps. The hosted `MemoryClient` is exported from the top-level package;
  `mem0/proxy/main.py:16-24` will **auto-`pip install` `litellm` at import time**
  if it is missing. ADR-0004, G-04.
- **History SQLite DB defaults into the user's home directory.** `history_db_path`
  default is `os.path.join(mem0_dir, "history.db")` where `mem0_dir = ~/.mem0`
  (`mem0/configs/base.py:13, 42-45`). PT-03 (no unscoped host mutation).
- **Notices system surfaces upsell content into the runtime.** `mem0/memory/
  notices.py` (1582 lines) prints to stdout/stderr on `add`/`search`/`delete`
  based on usage patterns. The notices are gated on PostHog feature flag
  `mem0-oss-notices` — runtime behavior influenced by a remote feature flag.
  SR-11/SR-12.
- **`README.md` benchmark table is explicitly a platform claim.** "Scores
  reflect Mem0's managed platform, which includes proprietary optimizations not
  available in the open-source SDK" (README.md:38-46). `[README claim]`.
- **Inconsistent return shape between `add` ({results}), `delete` ({message}),
  `delete_all` ({message}), and `search` ({results}).** Adapter surface concern
  (FR-10..13).

### Reuse recommendation

**Recommendation: Reject as a dependency; adapter / clean-room concept is viable
only for the vector-store interface.**

Blocking gaps (any one sufficient to reject for Koquetel's documentation-only,
no-egress, no-host-mutation phase):

1. Telemetry on by default with a hardcoded PostHog API key and shipment of
   provider class names to a third party (`mem0/memory/telemetry.py:15-18,
   206-216`). SR-11/SR-12/G-04.
2. Auto-`pip install litellm` at import time inside `mem0/proxy/main.py:18-24`.
   G-04.
3. SQLite history DB defaults to `~/.mem0/history.db`. PT-03.
4. No provenance field on writes; MD5 used for memory hash. FR-09.
5. No export/portability primitive and partial/non-atomic deletion.
   FR-12/FR-13/PT-03.
6. No graph memory at this pin. ADR-0004 graph-memory expectation unmet.

Reusable design concepts (for a clean-room Koquetel implementation, *not* an
import):

- The 11-method `VectorStoreBase` contract (`mem0/vector_stores/base.py:4-99`)
  including its similarity-score normalization convention and opt-in
  `keyword_search`/`search_batch` defaults.
- The string-keyed factory pattern with `register_provider`
  (`mem0/utils/factory.py:120-130, 222-234`).
- The phased add pipeline with an explicit `infer=False` escape hatch
  (`mem0/memory/main.py:850-884`).
- The history-table shape (`mem0/memory/storage.py:39-72`: `memory_id`,
  `old_memory`, `new_memory`, `event`, `created_at`, `updated_at`, `is_deleted`,
  `actor_id`, `role`).

No source code from Mem0 should be vendored. If Koquetel later wants a memory
layer, the right move per ADR-0004 is a clean-room implementation that adopts
the `VectorStoreBase` *signature* (re-licensed under Koquetel's own terms,
written from scratch) and explicitly excludes: PostHog telemetry, auto-install
behavior, MD5 hashing, default home-directory state, and any LLM-mandatory
write path.
