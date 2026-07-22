# CLI and local API contracts

Status: normative draft  
Last reviewed: 2026-07-21

## CLI surface

```text
koquetel discover [--json]
koquetel init [PATH] [--profile essential|balanced|autonomous] [--dry-run]
koquetel plan <install|update|repair|remove|sync> [--json]
koquetel apply <plan-id> --confirm <plan-hash>
koquetel status [--json]
koquetel doctor [--bundle PATH] [--include-content]
koquetel recover [transaction-id]
koquetel export --output PATH [--scope SCOPE]
koquetel memory <search|inspect|promote|quarantine|supersede|delete|export>
koquetel tools <list|inspect|admit|revoke|doctor>
koquetel policy <explain|list|check>
koquetel budget <status|set|explain>
koquetel adapters <list|status|sync|doctor>
```

Mutation commands do not accept implicit “yes to everything”. Automation uses a
previously issued delegation or exact plan hash.

## Response envelope

All JSON commands return a stable envelope:

```json
{
  "schemaVersion": 1,
  "ok": true,
  "operation": "doctor",
  "correlationId": "01...",
  "result": {},
  "warnings": [],
  "error": null
}
```

Errors contain `code`, `message`, `details`, `retryable`, `nextActions` and an
optional `causeCorrelationId`. Human messages may improve; codes and field
semantics remain compatible within a major schema version.

## Initial stable errors

| Code | Meaning |
|---|---|
| E-1001 | unsupported host or client version |
| E-1002 | managed configuration conflict |
| E-1003 | required capability unavailable |
| E-2001 | plan stale or hash mismatch |
| E-2002 | mutation lease busy |
| E-2003 | recovery required before mutation |
| E-2004 | ownership proof failed |
| E-3001 | policy denied capability |
| E-3002 | confirmation or delegation required |
| E-3003 | delegation expired or broader than parent |
| E-4001 | memory backend unavailable |
| E-4002 | memory conflict or quarantine required |
| E-4003 | context cannot fit mandatory policy budget |
| E-5001 | model/provider unavailable |
| E-5002 | budget or retry ceiling reached |
| E-5003 | no route satisfies privacy/capability policy |
| E-6001 | tool not admitted or manifest changed |
| E-6002 | tool input/output schema invalid |
| E-6003 | sandbox containment requirement unavailable |
| E-7001 | artifact integrity or provenance failure |
| E-7002 | transaction verification failed and rolled back |
| E-7003 | automatic recovery unsafe; operator action required |
| E-8001 | unknown session id |
| E-8002 | session ended or expired |
| E-8003 | session id format invalid (not 32 lowercase hex) |

## Local API

The socket API mirrors typed application commands, not shell commands. Every
request includes API version, caller identity from peer credentials, correlation
ID and optional active task/delegation. Streaming endpoints expose progress and
events with bounded replay cursors.

No endpoint accepts arbitrary filesystem paths without a declared operation and
policy-resolved root. The privileged helper uses a separate, smaller protocol.

## Sessions

The session contract realizes `ADR-0010` and is fixed by the versioned
`SCH-21 SessionHandle` schema ([`../05-data/schemas/session.schema.json`](../05-data/schemas/session.schema.json));
`SC-11` enforces it. This is a contract, not a runtime.

- **Creation.** A session is created **implicitly** on the first authenticated
  request from an `(actor, task)` pair, or **explicitly** via `session/start`.
- **Identifier.** `sessionId` is a **128-bit CSPRNG** value, canonical wire form
  **32 lowercase hex** (`^[0-9a-f]{32}$`), with **no embedded timestamp**. It is a
  correlation identifier, **not a bearer credential**; authority is revalidated per
  request and never derived from the id. It is **immutable** and **not reused after
  expiry**.
- **Propagation.** The core returns `sessionId` in the response
  `_meta["io.koquetel/sessionId"]`; the client echoes it in the same `_meta` field
  on subsequent requests. Comparison against a stored value uses constant time
  where relevant.
- **Termination.** `session/end` moves the session to `ended` (with `endedAt` and
  `endReason`); inactivity past `expiresAt` moves it to `expired`. Neither returns
  to `active`.
- **Unknown / ended / expired handling.** A request bearing an unknown id → `E-8001`;
  an `ended`/`expired` id → `E-8002`; a malformed id → `E-8003`. These are
  fail-closed: no mutation proceeds on a bad session reference; the request may be
  retried as a fresh (implicit) session where policy allows.
- **Stateless when absent.** When no `sessionId` is present the request is handled
  **statelessly** (all context inline); sessions are optional and never a
  precondition for a single-shot request.
- **Compatibility / version negotiation.** `SessionHandle.schemaVersion` is the
  major; an unknown major fails closed (NFR-08, SC-09). Changing the id format is a
  schema **version change** with compatibility rules — not an open runtime choice.
- **Relation to MCP.** Modern MCP is a **stateless** transport that carries no
  session concept and self-reports `clientInfo` (untrusted for security). The
  Koquetel session lives **above** MCP transport in `_meta`; where a legacy MCP
  `Mcp-Session-Id` exists it is treated as opaque client state, never as Koquetel
  authority. MCP remains transport (ADR-0005), not a session or authority boundary.

