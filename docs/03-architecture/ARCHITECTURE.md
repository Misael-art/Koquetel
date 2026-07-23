# System architecture

Status: normative draft  
Last reviewed: 2026-07-21

## 1. Architectural shape

Koquetel is a local control plane with client adapters and replaceable capability
providers. The core owns policy and state. Adapters translate; they do not decide
authority or mutate canonical state directly.

```text
Clients (CLI/IDE)
       │
       ▼
Client Bridge ─── Context Compiler ─── Memory Port
       │                 │
       ▼                 ▼
Workflow Engine ─── Model Router Port
       │
       ▼
Tool Gateway ─── Policy Engine ─── Sandbox / Privileged Helper
       │                 │
       └──── Event Journal / OpenTelemetry Export
                         │
                  Transaction Engine
                         │
                   Canonical State DB
```

## 2. Components and ownership

### Core service

Owns canonical configuration, state machine, transaction journal, locks, policy
decisions, event IDs and adapter lifecycle. Exposes a versioned local API over a
Unix socket. Must not require an AI provider to start.

### CLI

Thin client for the local API with an offline recovery path limited to inspection,
service restart instructions and transaction recovery. Human output and JSON are
derived from the same typed response.

### Client Bridge

Detects clients and invokes an adapter for config projection, hooks and lifecycle
events. Adapters produce intended documents/diffs; only the Transaction Engine
writes them.

### Context Compiler

Builds a bounded, provenance-preserving context pack. Policy is inserted before
retrieved memory. Secrets and ignored paths are filtered before ranking. It never
grants authority based on retrieved text.

### Memory Port

Defines search, candidate write, promote, supersede, quarantine, export and health.
The canonical metadata envelope remains Koquetel-owned even when content resides
in an external backend.

### Model Router Port

Normalizes capability, health, privacy class, budget, usage and outcome. Provider
credentials are requested from the Secrets Broker at invocation time.

### Tool Gateway

Validates tool manifest and input schema, obtains a policy decision, prepares the
execution envelope and records sanitized results. MCP is one transport adapter.

### Policy Engine

Evaluates declarative rules against actor, project, task, tool, requested
capabilities, target, time and active delegation. Model output is untrusted input.

### Sandbox

Runs bounded commands with explicit mounts, environment, network and resource
limits. Backends implement Podman rootless, Docker and restricted local process.

### Privileged Helper

Optional, narrow executable with an allowlisted typed command protocol. It cannot
accept an arbitrary shell string and never stores elevation credentials.

### Event Journal

Append-only local audit metadata. Content capture is separately opt-in. Exporters
consume events asynchronously and cannot block mutation completion.

## 3. Dependency boundaries

- `domain` imports no adapter, database, network, process or UI implementation.
- `application` depends on domain ports and transaction abstractions.
- `adapters` depend inward and cannot import another adapter directly.
- all filesystem writes go through Transaction Engine primitives;
- all process execution goes through Executor/Sandbox ports;
- all credentials go through Secrets Broker references;
- all external model/tool calls pass policy and budget checks;
- UI and client configuration never become canonical state.

These boundaries must be enforced by compilation structure and a custom boundary
lint, satisfying NFR-10.

## 4. Trust boundaries

1. User ↔ Koquetel UI/CLI.
2. Client agent ↔ Client Bridge.
3. Core ↔ memory/model/tool backend.
4. Host ↔ sandbox.
5. Unprivileged core ↔ privileged helper.
6. Local system ↔ remote providers/exporters.

Data crossing a boundary carries classification and correlation metadata. No
boundary inherits trust from localhost, same user, MCP, TLS or containerization
alone.

## 5. Concurrency

- One mutation lease per installation scope.
- One workspace mutation lease per repository and worktree.
- v1 implements the lease as a **local single-host cooperative OFD advisory lock**
  (`ADR-0011` Decision A). PT-06 recovery passes, but PT-01 remains partial until
  its ext4/XFS arm runs (`G-11`); this is specified, not yet proven on the target
  filesystem. Distributed/NFS/multi-host fencing is deferred to v2
  (`ADR-0011` Decision B, `G-13`).
- Read-only status and event streaming remain available during mutation.
- Transaction steps are idempotent and journal their intent before side effect.
- Memory candidates use immutable IDs; promotion uses optimistic version checks.
- Shared mutable context uses compare-and-swap or append-only records, not
  last-write-wins blocks.
