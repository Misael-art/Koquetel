# Product requirements document

Status: normative draft  
Last reviewed: 2026-07-21

## 1. Users and jobs

### Primary persona: individual AI-assisted developer

Needs to enter different repositories, use more than one agent, avoid repeating
context, constrain costs and trust that automation will not damage the host.

### Secondary persona: project maintainer

Needs project policies, approved tools, reproducible environments, audit evidence
and consistent behavior across contributor clients.

### Deferred persona: team administrator

Needs centrally distributed policies, identities and budgets. Schemas must not
preclude this persona, but multi-user control plane is outside v1 under A-06.

## 2. Functional requirements

### Installation and lifecycle

- **FR-01:** Discover the host, supported clients, existing configuration,
  available sandbox backends and conflicts without mutation.
- **FR-02:** Produce a deterministic, human-readable and machine-readable plan
  before every managed mutation.
- **FR-03:** Install, update, repair and remove only owned artifacts through one
  transactional lifecycle.
- **FR-04:** Verify the activated state and automatically recover the previous
  known-good state when activation fails.
- **FR-05:** Export user-owned Koquetel state independently from uninstall.

### Client integration

- **FR-06:** Generate client-specific configuration from one canonical project
  profile without replacing unrelated user configuration.
- **FR-07:** Detect drift and distinguish harmless user changes, managed drift and
  unsafe conflicts.
- **FR-08:** Operate in degraded mode when a client lacks one or more optional
  integration surfaces.

### Memory and context

- **FR-09:** Search task-relevant memory before non-trivial agent work when the
  active client supports lifecycle integration.
- **FR-10:** Capture candidate learnings with provenance and promote them through
  configurable validation and retention policy.
- **FR-11:** Separate session, project, user, organization, episodic, semantic,
  procedural and artifact memory scopes.
- **FR-12:** Compile a bounded task context pack containing applicable policy,
  repository map, relevant evidence, memory and current workspace state.
- **FR-13:** Allow inspection, correction, quarantine, export and deletion of
  memories without requiring the originating agent.

### Models and economy

- **FR-14:** Route model requests using task class, capability, privacy, health,
  budget and owner policy.
- **FR-15:** Enforce budgets and retry ceilings before a request creates an
  uncontrolled cost loop.
- **FR-16:** Attribute tokens, cost, latency, cache and outcome to task, client,
  model and provider without recording content by default.
- **FR-17:** Support direct providers, local models and compatible gateways
  through replaceable adapters.

### Tools, authority and execution

- **FR-18:** Register tools with version, source, integrity, schema, requested
  capabilities and health status.
- **FR-19:** Decide each tool invocation against policy and active delegation,
  independent of the model's request text.
- **FR-20:** Execute untrusted build/test/tool workloads in a resource-bounded
  sandbox by default when a supported backend is available.
- **FR-21:** Require contextual confirmation for external writes, host privilege
  and destructive operations unless a narrower time-bounded delegation exists.
- **FR-22:** Redact secrets from plans, logs, events, diagnostics and support
  bundles.

### Automation and evidence

- **FR-23:** Run restartable workflows with explicit steps, checkpoints,
  deadlines, retry policy and compensation behavior.
- **FR-24:** Support specialist-agent delegation without silently expanding the
  parent's authority or memory scope.
- **FR-25:** Record evidence linking requested outcome, plan, actions, tests,
  result, cost and retained learning.
- **FR-26:** Provide `status`, `doctor` and support bundle interfaces that work
  without a model or cloud connection.

## 3. Non-functional requirements

- **NFR-01 Reproducibility:** released artifacts and dependencies are pinned and
  integrity verified; the source commit is recorded.
- **NFR-02 Idempotency:** repeating a successful operation causes no additional
  mutation beyond timestamps explicitly excluded from state equality.
- **NFR-03 Recovery:** process termination at a documented mutation kill point
  converges to previous-good or completed-new state on next start.
- **NFR-04 Availability:** optional backend loss does not block client launch,
  status, export or uninstall.
- **NFR-05 Performance:** client startup integration adds no more than 250 ms p95
  when no remote call is required; asynchronous enrichment may continue later.
- **NFR-06 Privacy:** content telemetry is off by default; metadata collection is
  documented and locally inspectable.
- **NFR-07 Portability:** canonical profiles and exported memory do not embed
  absolute host paths unless the field is explicitly host-scoped.
- **NFR-08 Compatibility:** client adapters declare tested version ranges and fail
  closed on an unknown mutating schema while leaving the client usable.
- **NFR-09 Observability:** every state mutation and authority decision has a
  correlation ID, actor, policy result and redacted outcome.
- **NFR-10 Maintainability:** architecture boundaries are mechanically checked;
  adapters cannot directly mutate core state.
- **NFR-11 Accessibility:** human prompts and dashboard surfaces remain keyboard
  usable and do not encode severity by color alone.
- **NFR-12 Resource bounds:** background idle footprint and sandbox limits are
  configurable and included in release acceptance measurements.
- **NFR-13 Source-project independence:** default source, package metadata,
  dependency locks, entrypoints, services, schemas and runtime state contain no
  import, command, required path or required data format from PhaseZero or
  SteamZero. Their absence cannot reduce any Koquetel capability.

## 4. v1 capability boundary

Subject to Q-03 and Q-06, v1 targets one Linux user and these first-class clients:
Codex CLI, Claude Code, OpenCode and VS Code. Podman rootless is the preferred
sandbox; Docker is fallback. `ai-memory` is the first memory adapter. An
OpenAI-compatible gateway is the first router adapter.

Cursor, Zed, Gemini CLI, Aider, Cline, Windsurf, Neovim, Hermes, OpenClaw, A2A,
team administration and native UI remain adapter/roadmap work until independently
accepted.
