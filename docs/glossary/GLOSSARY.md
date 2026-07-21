# Canonical glossary

Status: normative draft  
Last reviewed: 2026-07-21

- **Adapter:** translation layer between a Koquetel port and one external client
  or backend. It does not own canonical policy.
- **Authority:** permission to create an effect. Information, model confidence and
  tool availability are not authority.
- **Backend:** replaceable implementation of memory, routing, sandbox, secrets or
  telemetry capabilities.
- **Capability:** typed permission such as workspace read/write, network target,
  external write, host administration or destruction.
- **Candidate memory:** captured learning not yet eligible for automatic current
  context.
- **Client:** supported IDE or agent CLI consuming Koquetel integration.
- **Confirmation:** single-use approval bound to an exact plan hash.
- **Context pack:** bounded, ordered, provenance-bearing task input compiled by
  Koquetel; not a dump of repository or conversation history.
- **Delegation:** expiring authority grant with actor, scope, budget and capability
  limits. Child delegations must be narrower.
- **Degraded mode:** usable operation with one or more optional capabilities
  unavailable and explicitly reported.
- **Memory Fabric:** Koquetel's governed memory model plus replaceable storage and
  retrieval backends.
- **Owned artifact:** path or record whose creation and current identity are
  provably managed by Koquetel. Location alone does not prove ownership.
- **Plan:** immutable description of intended effects, verification and rollback.
- **Policy:** declarative rule evaluated by the Policy Engine. Retrieved content
  and prompts are never policy.
- **Projection:** client-specific representation generated from canonical state.
- **Recovery:** deterministic convergence of an interrupted transaction to a
  verified old or new state.
- **Tool admission:** decision that a pinned tool manifest may be considered for
  invocation; it is not blanket permission to run it.
- **Transaction:** journaled mutation with preconditions, ordered effects,
  verification, compensation and terminal state.

Avoid ambiguous use of “safe”, “automatic”, “memory”, “local”, “rollback” and
“installed”. Qualify each with the applicable scope and verified property.

