# ADR-0010 — Session lifecycle

Status: proposed — owner decision Q-04 resolved (ADR-0006, Balanced); PT-01 and PT-02 met (evidence in prototype-evidence/); still blocked on PT-06 and the UUIDv7 benefit justification
Date: 2026-07-21

## Context

Koquetel coordinates AI agent tool execution, memory and state across multiple
requests. MCP (EA-03) is a **stateless protocol**: the `initialize`/`notifications/initialized`
handshake and `Mcp-Session-Id` header were removed in the draft revision; each
request carries its own protocol version and capabilities in `_meta`; `clientInfo`
and `serverInfo` are self-reported and MUST NOT be used for security decisions
(`basic/index.mdx`). There is no built-in session concept — session identity,
timeouts, budgets and rollback scope are entirely Koquetel's concern, layered
on top of MCP transport. The architecture defines a Workflow Engine, Context
Compiler and Memory Port but does not yet specify how agent sessions are created,
identified, maintained or terminated. Without an explicit session boundary the
system cannot:

- correlate tool calls to a single user task or conversation;
- enforce per-session budgets, memory scopes or authority delegations;
- apply session-level rollback or recovery after partial failure;
- distinguish concurrent sessions (same user, same agent type, different tasks).

## Options considered

1. **Stateless per-request (MCP-native).** No session identifier. Each request
   carries all context inline. Simple but loses cross-request correlation, makes
   budgets and conversation-scoped memory expensive to implement, and shifts the
   problem to every adapter independently.

2. **Lightweight session token.** A short-lived opaque token issued by the core
   on first request (or explicit `session/start`), carried as a request header or
   `_meta` field, and expired after inactivity. Session state (budget, memory
   scope, delegation) lives in the core's canonical state. The token is a
   reference, not a bearer credential — authority is re-evaluated per request
   against the actor and task identity.

3. **Process-scoped session.** The stdio transport process lifetime defines the
   session. Simple in a single-client scenario but breaks when clients interleave
   unrelated tasks on the same transport (which MCP explicitly allows) and offers
   no recovery after process restart.

## Decision (proposed)

Option 2: lightweight session token.

- A session is created implicitly on the first authenticated request from a given
  (actor, task identity) pair, or explicitly via `session/start` for long-running
  workflows.
- The session token is a correlation `sessionId` (UUIDv7, time-sortable) returned in
  the response `_meta` under the key `io.koquetel/sessionId` (MCP extension
  namespace convention) and carried by the client on subsequent requests in the
  same field.

### Session-id format: UUIDv7 (RFC 9562) over alternatives

| Property | UUIDv7 (RFC 9562) | Random 128-bit | Separate token + timestamp |
|---|---|---|---|
| DB-index friendly | monotonic within same ms only with specific counter¹ | no (random insert) | depends on layout |
| Clock-skew risk | yes (non-monotonic if clock jumps backwards) | none | none |
| Timestamp bits | 48-bit Unix ms timestamp | none | depends |
| Random bits (typical layout) | 74 bits (`rand_a` 12 + `rand_b` 62)² | 128 bits | depends |
| Opacity | reveals approximate creation time (ms) | does not reveal creation time | timestamp portion reveals time |
| Collision probability (birthday) | for n IDs in same ms: ~n²/2^75 | for n IDs: ~n²/2^129 | depends |
| Single wire value | yes (128-bit total) | yes | two values |
| Chosen (proposed) | **yes** — single wire value, approximate ordering, offline uniqueness³ | no | no — two values increase protocol surface |

¹ UUIDv7 is **not** guaranteed monotonic within the same millisecond without a
monotonicity counter occupying part of `rand_a`/`rand_b` (Section 6.2, RFC 9562).
If a counter is used, the number of random bits decreases correspondingly,
increasing birthday collision probability. The proposed implementation MUST
document whether it uses a counter or pure random for the `rand_a`/`rand_b`
portion and compute the effective collision bound.

² In the standard layout (`uuencode` format, RFC 9562 §5.7): 48-bit Unix
ms timestamp + 4-bit version + 12-bit `rand_a` + 2-bit variant + 62-bit
`rand_b` = 74 bits available for random/counter. If 12 bits are reserved for
a monotonicity counter (4096 values per ms), the random portion drops to
62 bits, changing the birthday bound to ~n²/2^63.

³ UUIDv7 reveals the approximate creation time of the session (ms precision).
This is **not fully opaque** — a UUIDv7 can be used to infer when a session
was created, which is acceptable for an internal correlation handle but must
not be relied upon as a security token or secret. The choice remains
**proposed**; a requirement or benchmark demonstrating that UUIDv7 ordering
provides measurable benefit over a random 128-bit identifier must be produced
before the decision is confirmed.

RFC 9562 primary source: Section 5.7 (UUIDv7 layout).

- Session state lives in core canonical state: memory scope, budget ledger,
  active delegation chain, checkpoint references.
- A session expires after an inactivity timeout (default 30 min, configurable)
  or on explicit `session/end`. Expiry releases the budget hold and flushes any
  un-promoted memory candidates.
- Authority is NOT inherited from the session token — every mutating request
  re-validates actor, capability and policy.

## Consequences

| Positive | Negative / risk |
|---|---|
| Sessions are optional — stateless requests remain valid (FR-07 drift check is per-request) | Requires a new session/end API plus expiry sweep |
| Implicit creation minimises client changes | Session-ID propagation over stdio needs MCP `_meta` extension |
| Budget/correlation can span tool calls without per-request re-auth of the full scope | Inactivity timeout choice affects UX and recovery behaviour — must be prototyped |
| Rollback scope is naturally the session | Session replay / replay-detection need design (deferred to ADR) |

## Prerequisites for acceptance

- ~~Q-04 (autonomy policy) resolved~~ — **closed 2026-07-21 (ADR-0006, Balanced)**.
  Balanced autonomy means session start does not require user confirmation for
  observe/reversible-workspace activity; external/admin/destructive still follow
  ADR-0003 plan-bound confirmation. Q-06 (supported user profile) is **not** a
  prerequisite: session lifecycle semantics are identical for individual and team
  deployments.
- PT-01 proves the lock contract works for session-scoped state.
- Prototype demonstrates timeout → recovery cycle with no lost mutations.

## References

- `ARCHITECTURE.md §2` — Workflow Engine, Core service ownership.
- `docs/08-testing/PROTOTYPE-GATES.md` PT-01 (mutual exclusion), PT-02 (journal
  recovery), PT-06 (lease recovery).
- MCP specification at `88191b9`: stateless protocol, per-request `_meta`.
- `EA-03` §Lifecycle: MCP has no session concept.
