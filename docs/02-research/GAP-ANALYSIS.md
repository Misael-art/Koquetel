# Gap analysis and synthesis

Status: research draft  
Last reviewed: 2026-07-21

## Structural gaps not solved by either local source

- **GA-01 Governed memory quality:** provenance envelopes, contradiction handling,
  quarantine, retention, correction and retrieval evaluation as one contract.
- **GA-02 Context compiler:** relevance-aware, budget-bound context with mandatory
  policy precedence and explicit omission reporting.
- **GA-03 Central authority engine:** typed capability policy independent of client,
  model, memory and MCP transport.
- **GA-04 Default sandbox:** rootless, resource/network/mount-bounded execution
  integrated with tool policy and evidence.
- **GA-05 Outcome-aware economy:** cost/token reduction tied to accepted task
  quality instead of usage counters alone.
- **GA-06 Global AI lifecycle transaction:** install/update/repair/remove across
  memory, MCP, router, rules and clients as one journaled compatibility set.
- **GA-07 Cross-agent attenuation:** child budgets, memory and tools provably no
  broader than the parent delegation.
- **GA-08 Portable evidence chain:** request→plan→authority→action→test→cost→memory
  correlation using interoperable events.
- **GA-09 Backend-independent export:** memory/policy/task evidence remains usable
  after replacing ai-memory, router or client.
- **GA-10 Semantic adapter verification:** client config health based on parsed
  intended state and round-trip fixtures, not file/string presence.

## Duplications to collapse

- Separate installer/status/doctor logic per AI tool becomes one manifest-driven
  lifecycle with adapters.
- Repeated JSON/TOML/YAML client editing becomes one canonical projection engine.
- Multiple gateway managers become one router port and provider/gateway adapters.
- Repeated service and binary detection becomes a typed capability probe registry.
- Caveman, RTK, Headroom and memory remain separate roles under a single profile;
  no wrapper stacking or ambiguous “economy” component.

## Synthesis decision

Use the strongest research evidence per capability, then implement the Koquetel
contract independently:

- transaction, fs safety, recovery and boundary lint: SteamZero concepts;
- client inventory, managed instruction projection and compatibility status:
  PhaseZero concepts;
- shell compression: RTK adapter;
- durable memory bootstrap: ai-memory adapter, conditional on G-04;
- tiered/shared memory semantics: evaluate Letta and Mem0 concepts;
- routing/budgets: evaluate LiteLLM and existing local gateways;
- sandbox: evaluate OpenHands runtime concepts with Podman/Docker primitives;
- telemetry: OpenTelemetry GenAI conventions;
- future inter-agent wire compatibility: A2A, deferred until G-08 closes.

No bullet above authorizes a source, build, package, runtime, service, test or data
dependency on PhaseZero or SteamZero.
