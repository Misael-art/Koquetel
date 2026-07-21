# Schema registry

Status: normative draft
Last reviewed: 2026-07-21

This registry is the canonical index of Koquetel's versioned data contracts. Each
schema is a *documented contract example* under the foundation gate
(`AGENTS.md` allows "schemas as documented examples"); no runtime, generator or
package is implied or authorized by this directory.

The schemas realize existing requirements; they do not introduce product
behavior. Every normative rule below is traced in
[`../../TRACEABILITY.md`](../../TRACEABILITY.md) and exercised by the `SC-xx`
schema-contract test family in [`../../08-testing/TEST-STRATEGY.md`](../../08-testing/TEST-STRATEGY.md).

## 1. Identifier namespace

- `SCH-xx`: a normative schema (one logical record contract). Stable, never
  renumbered, never reused after retirement.
- `SC-xx`: a schema-contract test obligation (golden validate/reject/compatibility).

## 2. Files and logical schemas

Related contracts are grouped into eight files that mirror the eight foundation
schema families. Within a file the primary entity is the schema `root`; secondary
entities are `$defs` referenced by `$ref`.

| File | Logical schemas |
|---|---|
| `plan-confirmation.schema.json` | SCH-01 Plan (root), SCH-02 Confirmation |
| `transaction.schema.json` | SCH-03 TransactionRecord (root), SCH-04 JournalEntry, SCH-05 RecoveryRecord, SCH-06 OwnershipFingerprint |
| `profile-adapter.schema.json` | SCH-07 ProfileProbe (root), SCH-08 AdapterDescriptor |
| `memory.schema.json` | SCH-09 MemoryEnvelope (root), SCH-10 MemoryExport |
| `tool-policy.schema.json` | SCH-11 ToolManifest (root), SCH-12 CapabilityRequest, SCH-13 PolicyDecision |
| `delegation-task.schema.json` | SCH-14 Delegation (root), SCH-15 Budget, SCH-16 TaskCheckpoint |
| `event-support.schema.json` | SCH-17 EventRecord (root), SCH-18 SupportBundleManifest |
| `model-routing.schema.json` | SCH-19 ModelRoute (root), SCH-20 UsageRecord |

## 3. Versioning and compatibility

Koquetel does **not** rely on implicit forward tolerance. A single schema with
`additionalProperties: false` is *not* forward-tolerant, and this document does
not claim it is. Two explicit modes exist, and a record is bound to the mode of
the operation consuming it, not to the schema alone.

### 3.1 Strict-write mode (canonical, default)

Applies to every record used for **mutation, authority, persistence or admission**
— i.e. all of `SCH-01..SCH-20`, whose files live in this directory.

- `schemaVersion` is `const: 1` for the v1 contracts; a value other than `1`
  fails closed.
- Unknown fields are **rejected** (`additionalProperties: false`).
- An additive change (a new *optional* field) is a new **documented minor**: it
  requires a registry changelog entry and a corresponding schema revision. A
  strict producer/consumer validates against the exact current revision — it does
  not accept fields from a minor it does not know.
- A **breaking change** (removing/renaming/retyping a field, or adding a required
  field) is a new **major**: a new schema retained under a new `SCH-xx` history
  entry; the prior major is `superseded`, never deleted.
- **Fail-closed (NFR-08):** an unknown major on a mutating record is refused
  (`E-6002`/`E-1001`), leaving prior state usable; the record is never coerced.

### 3.2 Tolerant-read mode (opt-in, read-only)

Applies only to **read-only consumers** (dashboards, exporters, diagnostics) that
never mutate, never grant authority and never rewrite the record.

- The **known major is required**: `schemaVersion` must be an enumerated known
  major; an unknown major is still rejected.
- Unknown *optional* fields are **preserved/ignored** (`additionalProperties:
  true`) so a reader survives a newer minor.
- A tolerant-validated record **MUST NOT** be routed to any mutating, authority or
  admission operation. That is a runtime invariant JSON Schema cannot express; it
  is asserted by `SC-09` sub-test 5.

Where a record class is consumed read-only, its tolerant profile is modelled as a
**separate** schema — see [`tolerant-read/event.tolerant.schema.json`](tolerant-read/event.tolerant.schema.json)
for `EventRecord` (SCH-17). The tolerant profile shares the field shapes but sets
`additionalProperties: true` and a `schemaVersion` enum; it does not weaken the
strict schema, which remains the only contract accepted for writes.

- **Offline resolution (P-13, NFR-13):** every `$id` uses the `urn:koquetel:schema:*`
  form, not an `https://` URL, so schema identity never requires a network host or
  any PhaseZero/SteamZero path to resolve. `$ref` values are file- or fragment-local.

Both modes are executed by the `SC-09` sub-tests in §6.

## 4. Sensitivity classification

Every field carries an `x-classification`. Sensitive fields additionally carry
`x-retention` and `x-exportable`. Non-sensitive metadata may omit the latter two
and inherit the family default stated per file.

Classification legend:

| `x-classification` | Meaning | Default `x-exportable` |
|---|---|---|
| `public` | non-identifying constant/enumeration | `yes` |
| `identifier` | correlation/record id, opaque | `yes` |
| `metadata` | operational metric/state, no user content | `yes` |
| `host-scoped` | absolute host path or machine-local value (NFR-07) | `policy` |
| `sensitive` | user-identifying or workspace-derived data | `policy` |
| `secret-ref` | *reference/locator* to a secret; raw secret is prohibited (SR-05) | `no` |
| `content` | user prompt/source/output; capture is opt-in (SR-06, NFR-06) | `explicit` |

`x-retention` values reference the defaults in
[`../DATA-MODEL.md`](../DATA-MODEL.md) (`session-30d`, `candidate-14d`,
`audit-180d`, `procedure-review`, `backup-window`) or `n/a`. `x-exportable`
values: `yes`, `policy` (governed by Q-05 posture), `explicit` (user must select),
`no` (never exported in raw form). Completeness is proven by test `SC-10`.

**Composite/container fields** (objects and arrays) also declare `x-classification`
and carry `metadata` (structural): the container itself holds no sensitivity; the
actual sensitivity is expressed on its leaf fields, which carry their own
classification, retention and export permission. `SC-10` walks the whole tree —
composite fields included — so a missing classification anywhere fails the test.

Invariants enforced by classification:

- No field is `x-classification: secret-ref` with `x-exportable` other than `no`.
- No `content` field is exported without `explicit` selection.
- No `host-scoped` field appears in a portable export unless the destination
  record is itself declared host-scoped (NFR-07).

## 5. Per-schema requirement and test map

| Schema | Realizes | Threat/failure | Acceptance | Test |
|---|---|---|---|---|
| SCH-01 Plan | FR-02, P-04 | R-01 | AC-01, AC-07 | SC-01 |
| SCH-02 Confirmation | SR-04, FR-21 | prompt-injection consent bypass | AC-10 | SC-01 |
| SCH-03 TransactionRecord | FR-03, NFR-02 | FM-01, FM-19 | AC-01, AC-03 | SC-02 |
| SCH-04 JournalEntry | NFR-03, SR-10 | FM-01 (torn tail, AR-09), FM-21 (stale-epoch fence), FM-22 | AC-03 | SC-02, PT-06 |
| SCH-05 RecoveryRecord | FR-04, NFR-03 | FM-18, FM-20 | AC-03, AC-04 | SC-02 |
| SCH-06 OwnershipFingerprint | FR-03, SR-08 | FM-03, FM-20, AR-08 | AC-04 | SC-02 |
| SCH-07 ProfileProbe | FR-01, NFR-04 | FM-11, FM-04 | AC-01, AC-13 | SC-03 |
| SCH-08 AdapterDescriptor | FR-06, NFR-08, NFR-10 | FM-04, AR-07 | AC-16 | SC-03 |
| SCH-09 MemoryEnvelope | FR-10, FR-11, SR-11 | FM-06, R-02 | AC-05, AC-06 | SC-04 |
| SCH-10 MemoryExport | FR-05, FR-13, GA-09 | FM-20 | AC-04, AC-05 | SC-04 |
| SCH-11 ToolManifest | FR-18, SR-03, SR-09 | FM-09, FM-17 | AC-10 | SC-05 |
| SCH-12 CapabilityRequest | FR-19, SR-01 | prompt-injected capability | AC-10 | SC-05 |
| SCH-13 PolicyDecision | FR-19, SR-01, NFR-09 | FM-16 | AC-10, AC-14 | SC-05 |
| SCH-14 Delegation | FR-24, SR-16 | FM-16, R-12 | AC-12 | SC-06 |
| SCH-15 Budget | FR-15, P-08 | FM-08, R-12 | AC-09 | SC-06 |
| SCH-16 TaskCheckpoint | FR-23, NFR-03 | FM-08 | AC-09, AC-14 | SC-06 |
| SCH-17 EventRecord | FR-25, NFR-09, SR-10 | FM-14, FM-15 | AC-14 | SC-07 |
| SCH-18 SupportBundleManifest | FR-26, FR-22, SR-06 | FM-14, R-09 | AC-13 | SC-07 |
| SCH-19 ModelRoute | FR-14, SR-14 | FM-07, R-04 | AC-08 | SC-08 |
| SCH-20 UsageRecord | FR-16, NFR-06 | FM-08, R-12 | AC-08, AC-14 | SC-08 |

## 6. Schema-contract tests (`SC-xx`)

These are **executed** by the foundation schema suite
(`tools/schema_suite/run_suite.py`), a foundation-only, pinned Draft 2020-12
validator that is isolated from the product runtime. Each `SC-01..SC-08` covers one schema file and asserts, for every
entity in it (root **and** each `$defs` secondary entity), that the valid example
validates and the invalid example is rejected for exactly its documented rule
(`examples/README.md`).

- **SC-01** `plan-confirmation.schema.json` — Plan (SCH-01), Confirmation (SCH-02).
- **SC-02** `transaction.schema.json` — TransactionRecord (SCH-03), JournalEntry
  (SCH-04), RecoveryRecord (SCH-05), OwnershipFingerprint (SCH-06).
- **SC-03** `profile-adapter.schema.json` — ProfileProbe (SCH-07), AdapterDescriptor
  (SCH-08).
- **SC-04** `memory.schema.json` — MemoryEnvelope (SCH-09), MemoryExport (SCH-10).
- **SC-05** `tool-policy.schema.json` — ToolManifest (SCH-11), CapabilityRequest
  (SCH-12), PolicyDecision (SCH-13).
- **SC-06** `delegation-task.schema.json` — Delegation (SCH-14), Budget (SCH-15),
  TaskCheckpoint (SCH-16).
- **SC-07** `event-support.schema.json` — EventRecord (SCH-17), SupportBundleManifest
  (SCH-18).
- **SC-08** `model-routing.schema.json` — ModelRoute (SCH-19), UsageRecord (SCH-20).

- **SC-09 version guard (strict-write / tolerant-read, §3).** Five independent
  assertions:
  1. strict v1 **accepts** a known v1 instance;
  2. strict v1 **rejects** an unknown field (`additionalProperties: false`);
  3. `schemaVersion: 2` is **rejected** by the strict schema (`const: 1`) and by
     the tolerant profile (major not in its enum);
  4. the tolerant read profile **accepts** an instance with an unknown optional
     field (preserve/ignore);
  5. a record that passes *only* the tolerant profile (strict-invalid) **must not**
     be admitted for a mutating/authority operation — asserted as a semantic gate,
     since JSON Schema cannot express routing.
- **SC-10 classification completeness (recursive).** Walking every `properties`,
  `items`, `oneOf`/`anyOf`/`allOf` branch and `$defs` entry: every field —
  including composite (object/array) fields — declares `x-classification`; every
  field whose classification is `host-scoped`, `sensitive`, `secret-ref` or
  `content` also declares `x-retention` and `x-exportable`; `secret-ref` is never
  exportable in raw form; `content` is `explicit`-only. The test reads the schema
  files themselves, so it cannot drift from the contract.
- **Semantic invariants (beyond JSON Schema).** The suite also asserts cross-field
  invariants a validator cannot: `confirmation.planHash` must equal the referenced
  plan's `planHash` (SR-04), and the journal torn-tail isolation rule (AR-09, §7).

## 7. Critical secondary-entity examples

Standalone `examples/` cover each file's root entity. Two hash/torn-tail cases that
are the reason these contracts exist are documented inline here.

### Confirmation must not authorize a changed plan (SCH-02, SR-04 invariant)

Invalid — `planHash` does not equal the referenced plan's hash:

```json
{
  "schemaVersion": 1,
  "confirmationId": "01J8Z0CNF6CONF0000000000A",
  "planId": "01J8Z0CNF6PLAN0000000000A",
  "planHash": "0000000000000000000000000000000000000000000000000000000000000000",
  "actor": { "type": "user", "id": "local:misael" },
  "grantedCapabilityClass": "workspace-write",
  "issuedAt": "2026-07-21T18:00:00Z",
  "expiresAt": "2026-07-21T18:05:00Z",
  "singleUse": true
}
```

Rejected because a confirmation is bound to the exact normalized `planHash`
produced by SCH-01; a differing or zeroed hash cannot carry consent (transaction
invariant "a confirmation cannot authorize a changed plan").

### Journal recovery must tolerate a torn tail (SCH-04, AR-09)

A killed final append can leave a truncated last line. The reader validates
`sequence` monotonicity and `entryDigest`; a final record failing its digest is
isolated as `incomplete` and never makes the earlier, valid records unreadable.
The `entryDigest` and `sequence` fields exist specifically so recovery is
line-atomic rather than file-atomic.
