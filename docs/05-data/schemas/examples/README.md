# Schema examples

Each schema file has one `*.valid.json` (the file's root entity) and one
`*.invalid.json`. Every invalid example violates **exactly one** documented rule,
so the `SC-01..SC-08` golden tests can pin a single rejection reason.

| Invalid example | Single violated rule |
|---|---|
| `plan-confirmation.invalid.json` | `requiredConfirmationClass: "auto-approve"` is outside `CapabilityClass`; a plan cannot self-authorize (SR-04, ADR-0003) |
| `transaction.invalid.json` | `state: "done"` is outside the transaction state machine enum (`TRANSACTION-MODEL.md`) |
| `profile-adapter.invalid.json` | `profile: "maximum"` is outside the `essential|balanced|autonomous` enum (`LIFECYCLE.md`) |
| `memory.invalid.json` | `confidence: 1.5` exceeds the `0..1` bound |
| `tool-policy.invalid.json` | `transport: "http"` is outside `mcp|process|builtin` (ADR-0005) |
| `delegation-task.invalid.json` | `grantedCapabilities: ["observe","root"]` contains `root`, outside the capability enum (SR-16) |
| `event-support.invalid.json` | `category: "debug"` is outside the audit category enum (SR-10) |
| `model-routing.invalid.json` | `privacyClass: "anywhere"` is outside `local-only|cloud-allowed|policy` (SR-14) |

Two additional inline invalid cases (confirmation hash mismatch and journal torn
tail) are documented in [`../SCHEMA-REGISTRY.md`](../SCHEMA-REGISTRY.md) §7 because
they exercise cross-field and cross-record invariants rather than a single field.

The `x-classification` / `x-retention` / `x-exportable` annotations that appear in
the schema files are custom keywords; a standard JSON Schema validator ignores
them, while the `SC-10` test reads them directly for classification completeness.

## SCH-21 / SC-11 session fixtures

SC-11 uses the `session.*`, `session-ref.*`, and `session-transition.*` fixtures.
They cover the valid handle; malformed, uppercase and unknown-state handles;
missing required fields; each independently missing ended field; the closed
end-reason enum; unknown/malformed SessionRef values; forbidden authority and
capability fields; timestamp ordering; ended and expired terminal transitions;
and immutable `sessionId`/`actorRef` across a transition.

These fixtures test record shape and the documented lifecycle predicate. They do
not simulate or claim runtime authentication or authorization.
