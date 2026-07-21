# Foundation traceability matrix

Status: normative draft — one row per requirement
Last reviewed: 2026-07-21

This matrix is the canonical index connecting product intent to verification. Every
functional, non-functional, security and acceptance identifier has its own row
mapping it to its main risk, failure mode, acceptance criterion and a verification
family. Verification families are the test layers in
[`08-testing/TEST-STRATEGY.md`](08-testing/TEST-STRATEGY.md): failure-injection
`FI-xx`, rollback `RT-xx`, independence `IT-xx`, schema-contract `SC-xx`, prototype
gates `PT-xx`, plus property, golden-contract, corpus/benchmark and fixture tests.

The `foundation_lint.py` checker (`tools/`) fails if any `FR/NFR/SR/AC` lacks a row
here or a row cites no verification. Rows become `proven` only under the approval
rule at the bottom; today all rows are `specified` (foundation phase).

## Functional requirements

| FR | Main risk | Failure mode | Acceptance | Verification | Status |
|---|---|---|---|---|---|
| FR-01 | R-03 | FM-04, FM-11 | AC-01, AC-13 | SC-03, non-mutation property | specified |
| FR-02 | R-01 | FM-03 | AC-01, AC-07 | SC-01, FI-03 | specified |
| FR-03 | R-10 | FM-01, FM-17..21 | AC-01, AC-04 | SC-02, FI-01, RT-01..05, PT-06 | specified |
| FR-04 | R-10 | FM-01, FM-18 | AC-03 | FI-01, RT-02, RT-03, PT-02 | specified |
| FR-05 | R-11 | FM-20 | AC-04, AC-05 | SC-04, golden export, PT-03 | specified |
| FR-06 | R-03 | FM-03, FM-04 | AC-02 | SC-03, adapter round-trip fixture, FI-12 | specified |
| FR-07 | R-03 | FM-03, FM-04 | AC-02, AC-16 | round-trip fixture, FI-12 | specified |
| FR-08 | R-05 | FM-04 | AC-15 | client fixture, FI-12 | specified |
| FR-09 | R-02 | FM-05 | AC-05, AC-07 | retrieval property, SC-04 | specified |
| FR-10 | R-02 | FM-06 | AC-05, AC-06 | SC-04, FI-04 | specified |
| FR-11 | R-02 | FM-06 | AC-05 | SC-04, scope property, SR-11 suite | specified |
| FR-12 | R-02 | FM-05 | AC-07 | budget property, golden, FI-05 | specified |
| FR-13 | R-02 | FM-06 | AC-05, AC-06 | SC-04, RT-06 | specified |
| FR-14 | R-04 | FM-07 | AC-08 | SC-08, corpus benchmark | specified |
| FR-15 | R-12 | FM-08 | AC-09 | SC-06, ceiling property | specified |
| FR-16 | R-12 | FM-08 | AC-08, AC-14 | SC-08, golden | specified |
| FR-17 | R-11 | FM-07 | AC-08 | adapter fixture, SC-08 | specified |
| FR-18 | R-01 | FM-09, FM-17 | AC-10 | SC-05, manifest-swap suite | specified |
| FR-19 | R-01 | FM-16 | AC-10 | SC-05, authority property, SR-01 suite | specified |
| FR-20 | R-01, R-08 | FM-11, FM-12 | AC-11 | PT-04, FI-09, FI-10 | specified |
| FR-21 | R-01 | FM-16 | AC-10 | SC-01 confirmation, SR-04 suite | specified |
| FR-22 | R-09 | FM-14 | AC-13 | SC-07, seeded-secret canary | specified |
| FR-23 | R-10 | FM-08 | AC-09, AC-14 | SC-06 checkpoint, interrupted E2E suite | specified |
| FR-24 | R-12 | FM-16 | AC-12 | SC-06 delegation, attenuation property | specified |
| FR-25 | R-13 | FM-15 | AC-14 | SC-07, golden evidence chain | specified |
| FR-26 | R-07 | FM-15 | AC-13 | SC-07, offline E2E suite | specified |

## Non-functional requirements

| NFR | Main risk | Failure mode | Acceptance | Verification | Status |
|---|---|---|---|---|---|
| NFR-01 | R-11 | FM-17 | AC-01 | golden provenance, PT-05 | specified |
| NFR-02 | R-10 | FM-01 | AC-02 | idempotency property, FI-01, RT-03 | specified |
| NFR-03 | R-10 | FM-01, FM-21, FM-22 | AC-03 | FI-01, RT-03, PT-02, PT-05, PT-06 | specified |
| NFR-04 | R-05 | FM-05, FM-11 | AC-13, AC-15 | offline E2E suite, FI-09 | specified |
| NFR-05 | R-08 | FM-05 | AC-15 | startup benchmark | specified |
| NFR-06 | R-09 | FM-14 | AC-13 | SC-08, redaction canary, default-off property | specified |
| NFR-07 | R-11 | FM-20 | AC-04 | SC-10 classification, golden export round-trip | specified |
| NFR-08 | R-03 | FM-04 | AC-16 | SC-09 version guard, SC-03, FI-12 | specified |
| NFR-09 | R-13 | FM-15 | AC-14 | SC-07, correlation golden | specified |
| NFR-10 | R-05 | FM-13 | AC-01 (architecture) | boundary-lint suite, import property | specified |
| NFR-11 | R-13 | FM-04 | AC-15 | accessibility fixture, keyboard property | specified |
| NFR-12 | R-08 | FM-12 | AC-11 | PT-04 benchmark, FI-10 | specified |
| NFR-13 | R-05, R-06 | FM-17, FM-19 | AC-17 | IT-01..08 packaged independence | owner-confirmed |

## Security requirements

| SR | Main risk | Failure mode | Acceptance | Verification | Status |
|---|---|---|---|---|---|
| SR-01 | R-01 | FM-16 | AC-10 | SC-05, authority property, malicious-repo suite | specified |
| SR-02 | R-01 | FM-11 | AC-11 | least-privilege property, PT-04 | specified |
| SR-03 | R-01 | FM-09, FM-17 | AC-10 | SC-05, manifest-swap suite | specified |
| SR-04 | R-01 | FM-03 | AC-10 | SC-01, single-use property | specified |
| SR-05 | R-09 | FM-14 | AC-13 | secret-reference property, seeded-secret canary | specified |
| SR-06 | R-09 | FM-14 | AC-13 | redaction canary suite, SC-07 | specified |
| SR-07 | R-01, R-08 | FM-11, FM-12 | AC-11 | PT-04, FI-09, FI-10 | specified |
| SR-08 | R-01 | FM-03 | AC-11 | traversal/race suite, SC-06 ownership property | specified |
| SR-09 | R-11 | FM-17 | AC-01 | golden provenance, SC-05, PT-05 | specified |
| SR-10 | R-13 | FM-15 | AC-14 | SC-07 chained-digest property | specified |
| SR-11 | R-02 | FM-06 | AC-05 | scope property, SC-04, adversarial suite | specified |
| SR-12 | R-02 | FM-06 | AC-05, AC-06 | adversarial memory suite, FI-05 | specified |
| SR-13 | R-01 | FM-13 | AC-13 | PT-05, peer-credential property | specified |
| SR-14 | R-07 | FM-15 | AC-13 | SC-08 destinations, offline suite | specified |
| SR-15 | R-11 | FM-20 | AC-04 | RT-05, PT-03, ownership property | specified |
| SR-16 | R-12 | FM-16 | AC-12 | SC-06, attenuation property | specified |

## Acceptance criteria

| AC | Main risk | Failure mode | Verification | Status |
|---|---|---|---|---|
| AC-01 | R-03, R-10 | FM-01 | FI-01..03, RT-01..05 | specified |
| AC-02 | R-03 | FM-03 | round-trip fixture, FI-12, RT-07 | specified |
| AC-03 | R-10 | FM-01 | FI-01, RT-02, PT-02 | specified |
| AC-04 | R-11 | FM-20 | RT-05, PT-03, SC-10 | specified |
| AC-05 | R-02 | FM-06 | SC-04, provenance property | specified |
| AC-06 | R-02 | FM-06 | SC-04, FI-04, adversarial suite | specified |
| AC-07 | R-02 | FM-05 | budget property, golden, FI-05 | specified |
| AC-08 | R-04 | FM-07 | corpus benchmark, SC-08 | specified |
| AC-09 | R-04 | FM-07, FM-08 | FI-06, ceiling property, SC-06 | specified |
| AC-10 | R-01 | FM-09 | SC-05, hostile-tool suite | specified |
| AC-11 | R-01 | FM-11 | PT-04, FI-09, FI-10 | specified |
| AC-12 | R-12 | FM-16 | SC-06, attenuation property | specified |
| AC-13 | R-07 | FM-15 | offline E2E suite, SC-07 | specified |
| AC-14 | R-13 | FM-15 | SC-07, golden | specified |
| AC-15 | R-05 | FM-05 | client fixture, FI-12, offline suite | specified |
| AC-16 | R-03 | FM-04 | SC-09, client fixture, FI-12 | specified |
| AC-17 | R-05, R-06 | FM-17, FM-19 | IT-01..08 | owner-confirmed |

## Schema and prototype coverage

- Every schema `SCH-01..SCH-20` maps to a requirement, threat/failure mode,
  acceptance and an `SC-xx` test in
  [`05-data/schemas/SCHEMA-REGISTRY.md`](05-data/schemas/SCHEMA-REGISTRY.md) §5.
- Prototype gates `PT-01..PT-06`
  ([`08-testing/PROTOTYPE-GATES.md`](08-testing/PROTOTYPE-GATES.md)) each block a
  named contract/milestone until they pass their documented gate.
- Principles `P-13`/`NFR-13`/`AC-17` share the independence verification family
  `IT-01..IT-08`.

## Approval rule

A row can become `proven` only when its evidence is reproducible from a pinned
source revision and includes environment, command, result artifact and reviewer.
"Test passed" without retained output and contract version is insufficient. A row
whose verification cites a prototype gate cannot be `proven` before that gate
passes.
