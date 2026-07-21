# ADR-0005 — MCP is a transport, not the authority boundary

Status: proposed  
Date: 2026-07-21

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

