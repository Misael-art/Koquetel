# Test and evidence strategy

Status: normative draft  
Last reviewed: 2026-07-21

## Test layers

1. Domain property tests for policy, budgets, state machines and path safety.
2. Adapter contract tests against version-pinned fixtures.
3. Golden tests for CLI/API/events/config projections.
4. Integration tests using temporary homes and fake providers/backends.
5. Sandbox containment and hostile-repository security tests.
6. Kill-point transaction and rollback tests.
7. End-to-end supported-client tests in clean VMs/containers.
8. Physical-host acceptance only after all earlier gates pass.

## Minimum release gates

- formatting, lint, strict types and boundary lint;
- unit/integration suite green on supported matrix;
- branch coverage threshold decided before implementation, never lowered to ship;
- all critical `SR` tests green;
- every mutable step killed before/after side effect and recovered;
- install→repeat→update→rollback→remove sequence proven;
- golden public contracts reviewed for intentional changes;
- baseline resource, latency, cost and task-quality results attached;
- release provenance and clean source tree verified.
- IT-01 through IT-08 prove complete PhaseZero/SteamZero independence from packaged
  artifacts on a clean host.

## Initial failure injection

- **FI-01:** kill each transaction step around journal fsync and atomic activation.
- **FI-02:** exhaust disk space during stage, backup and event append.
- **FI-03:** modify target after plan and during confirmation window.
- **FI-04:** corrupt memory metadata/content/backend response.
- **FI-05:** return conflicting and prompt-injected memories at top rank.
- **FI-06:** time out, rate-limit and malformed-response every provider hop.
- **FI-07:** change tool manifest between admission and invocation.
- **FI-08:** return tool logical failure over successful transport.
- **FI-09:** remove sandbox backend and attempt untrusted execution.
- **FI-10:** exceed CPU, memory, process, output and execution-time limits.
- **FI-11:** crash telemetry exporter and fill its local queue.
- **FI-12:** present unknown client schema and modified managed blocks.

## Initial rollback tests

- **RT-01:** failed clean install leaves no active integration residue.
- **RT-02:** failed update restores binary, schema and configurations as one
  compatible set.
- **RT-03:** recovery after repeated kill converges and remains idempotent.
- **RT-04:** rollback refuses an artifact whose integrity cannot be proven.
- **RT-05:** removal preserves unowned and user-modified conflicting content.
- **RT-06:** memory adapter migration failure leaves original export usable.
- **RT-07:** client sync failure rolls back only that adapter projection.
- **RT-08:** privileged activation failure leaves unprivileged core diagnosable.

## Acceptance mapping seed

| Criteria | Required evidence families |
|---|---|
| AC-01..04 | end-to-end lifecycle, FI-01..03, RT-01..05 |
| AC-05..07 | memory/context contracts, FI-04..05, RT-06 |
| AC-08..09 | pinned task corpus, provider fault matrix, budget properties |
| AC-10..12 | policy properties, hostile tools, sandbox/delegation tests |
| AC-13..16 | offline E2E, evidence golden files, degraded/client fixture tests |
| AC-17 | IT-01..08 static, packaged-runtime and migrated-state independence gates |
