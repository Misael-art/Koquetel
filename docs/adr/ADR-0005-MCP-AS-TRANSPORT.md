# ADR-0005 — MCP is a transport, not the authority boundary

Status: accepted (proposed 2026-07-21, accepted 2026-07-22)

## Acceptance

Accepted under the owner's M-00 authorization to accept pending ADRs whose gates
are met. ADR-0005 has **no prototype gate**: it is a boundary/policy decision, not
a mechanism whose feasibility a prototype must prove. It is internally consistent
with ADR-0001 (independent core), the threat model (SR-01 authority separation,
SR-03 tool admission) and the architecture (Tool Gateway, Policy Engine). Its
mechanisms (admission, schema validation, policy, secrets, sandbox, audit) are
each already required elsewhere, so acceptance adds no unproven obligation. The
EA-03 audit confirmed MCP is a stateless transport that self-reports `clientInfo`
and explicitly leaves authorization to the host — precisely the premise of this
ADR.

## Context

MCP standardizes tool discovery/invocation but cannot guarantee that a server is
safe, unchanged or authorized for the current user intent.

## Decision

All MCP servers and calls pass Koquetel tool admission, schema validation, Policy
Engine, Secrets Broker, sandbox/executor and audit. Client-side MCP projection
does not grant broader host access. Remote authorization complements but does not
replace local policy.

## Consequences

Some direct client MCP features may be unavailable until Koquetel can mediate them
safely. This is an intentional least-authority tradeoff.

