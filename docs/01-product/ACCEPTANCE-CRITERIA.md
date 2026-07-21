# Product acceptance criteria

Status: normative draft  
Last reviewed: 2026-07-21

These criteria define product outcomes. Detailed test IDs live in the testing
area and must cite these identifiers.

- **AC-01 Clean install:** Given a supported clean user account, when the balanced
  profile is applied, then all planned owned artifacts verify, supported clients
  remain launchable and no unplanned path changes.
- **AC-02 Existing configuration:** Given populated supported-client config, when
  integration is applied twice, then unrelated content remains byte-equivalent,
  managed content appears once and the second run reports no mutation.
- **AC-03 Failed activation:** Given an injected failure after new state is staged,
  when activation or verification fails, then the previous state is restored and
  the next `doctor` explains the failure without exposing secrets.
- **AC-04 Removal:** Given a working installation, when Koquetel is removed, then
  only owned integration is removed, underlying clients still launch and retained
  user data matches the selected retention policy.
- **AC-05 Memory provenance:** Given a recalled memory, then the user can inspect
  its scope, source, timestamps, confidence, retention and originating task.
- **AC-06 Memory correction:** Given an incorrect memory, when it is corrected or
  quarantined, then subsequent retrieval does not return the superseded claim as
  current and the audit history remains available.
- **AC-07 Context bound:** Given a task and configured token budget, when a context
  pack is compiled, then required policy is present, excluded secrets are absent,
  provenance is preserved and the pack stays within budget or reports a stable
  insufficiency error.
- **AC-08 Economic routing:** Given equivalent representative tasks, when automatic
  routing is enabled, then accepted-task rate does not regress beyond the approved
  threshold while median cost improves against the pinned baseline.
- **AC-09 Provider failure:** Given an unavailable selected provider, when retry
  and fallback policy is exhausted, then execution terminates within its ceiling,
  cost remains bounded and a resumable state is retained.
- **AC-10 Tool denial:** Given a tool asks for a capability outside active policy,
  when it is invoked by any agent, then execution is denied before side effect and
  the decision is audited.
- **AC-11 Sandbox containment:** Given hostile test code, when run in the default
  sandbox, then it cannot access non-mounted user paths, host credentials, the
  container engine socket or unauthorized network targets.
- **AC-12 Delegation confinement:** Given a child agent, when it receives a task,
  then its tools, memory and budget are no broader than the explicitly delegated
  subset.
- **AC-13 Offline diagnostics:** Given network and model providers are unavailable,
  when `status`, `doctor`, export or uninstall is called, then each completes using
  local state.
- **AC-14 Evidence chain:** Given a completed automated coding task, then its report
  links request, plan, authority decisions, changes, verification, cost and memory
  candidates through stable correlation identifiers.
- **AC-15 Degraded backend:** Given memory, router or telemetry backend is down,
  when a supported client starts, then the client remains usable and the missing
  capability is visible without repeated blocking prompts.
- **AC-16 Unknown client version:** Given an adapter encounters an untested
  mutating config schema, then it performs no write, reports a compatibility error
  and provides an exportable diagnostic fixture.
- **AC-17 Complete independence:** Given a clean supported host on which PhaseZero
  and SteamZero are absent and their paths are unreachable, when Koquetel is built,
  tested, installed, operated, updated, recovered, exported and removed, then all
  default capabilities and lifecycle tests pass without downloading, importing,
  invoking or discovering either source project.
