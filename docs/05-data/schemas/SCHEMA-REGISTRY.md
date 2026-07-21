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

- Every instance carries an integer `schemaVersion` equal to the schema's major
  version. This mirrors the existing CLI/API envelope (`docs/06-api/CONTRACTS.md`)
  and transaction record (`docs/03-architecture/TRANSACTION-MODEL.md`).
- **Additive-minor rule (same major):** new *optional* fields may be added without
  a major bump. Consumers MUST ignore unknown optional fields within a known major
  (forward tolerance) and MUST NOT treat their absence as an error.
- **Breaking change (new major):** removing a field, renaming it, narrowing its
  type, or adding a *required* field. A new major schema keeps a new `SCH-xx`
  suffix history entry; the prior major is retained as `superseded`, never deleted.
- **Fail-closed rule (NFR-08):** a consumer that encounters an *unknown major* on a
  mutating record MUST refuse to act on it, emit `E-6002`/`E-1001` as applicable,
  and leave prior state usable. It MUST NOT silently coerce the record.
- **Offline resolution (P-13, NFR-13):** every `$id` uses the `urn:koquetel:schema:*`
  form, not an `https://` URL, so schema identity never requires a network host or
  any PhaseZero/SteamZero path to resolve. `$ref` values are file- or fragment-local.

Compatibility is proven by test `SC-09` (version guard) below.

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
| SCH-04 JournalEntry | NFR-03, SR-10 | FM-01 (torn tail, AR-09) | AC-03 | SC-02 |
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

These are *specified*, not yet implemented (foundation phase). Each is a golden
contract obligation.

- **SC-01..SC-08:** for each schema file, every `examples/*.valid.json` validates
  and every `examples/*.invalid.json` is rejected against the declared schema/`$ref`,
  with the rejection reason pinned in a golden fixture.
- **SC-09 version guard:** an instance with an unknown *major* `schemaVersion` is
  rejected fail-closed (NFR-08); an instance with an unknown *optional* field on a
  known major is accepted (additive-minor tolerance).
- **SC-10 classification completeness:** every leaf field declares
  `x-classification`; every sensitive field additionally declares `x-retention`
  and `x-exportable`; the invariants in §4 hold. This test reads the schema files
  themselves, so it cannot silently drift from the contract.

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
