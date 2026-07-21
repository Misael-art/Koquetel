# Vision and principles

Status: normative draft  
Last reviewed: 2026-07-21

## Vision

Koquetel makes AI coding environments capable by default: durable memory,
efficient context, model economy, governed tools, recoverable automation and a
consistent experience across supported IDEs and CLIs.

The product is not another coding agent. It is the local operational layer that
allows independently evolving agents to work with shared capabilities without
receiving uncontrolled access to the host or trapping user state in one vendor.

## Outcome statement

After one reviewed installation, a developer can enter a repository with a
supported agent and receive project-aware memory, context, tools, cost controls,
diagnostics and safe automation. Removing Koquetel restores the prior environment
and preserves user-owned data according to explicit retention choices.

## Principles

- **P-01 Local-first ownership.** User state is local by default. Every remote
  transmission is attributable to an enabled backend and visible in policy.
- **P-02 One capability, one authority.** Style, memory, context compression,
  model routing, tool access and privilege each have one canonical contract.
- **P-03 Automatic means bounded.** Reversible, in-workspace actions may be
  automatic. External, privileged or destructive effects require explicit
  delegated authority.
- **P-04 Plan before mutation.** Every managed mutation is previewable,
  attributable, verifiable and recoverable.
- **P-05 Fail degraded.** An unavailable optional component reduces capability;
  it does not prevent the user from opening an IDE or using the underlying CLI.
- **P-06 Replaceable dependencies.** Memory, model, gateway, sandbox and client
  implementations sit behind versioned adapters and exportable state.
- **P-07 Evidence over confidence.** Completion requires tests and artifacts;
  agent assertions are not proof.
- **P-08 Economy preserves outcomes.** Token or monetary reduction only counts
  when acceptance quality and safety do not regress.
- **P-09 Least context and least authority.** Agents receive only the information
  and capabilities justified by the active task.
- **P-10 Learning is governed.** Automatic memory may propose facts and
  procedures, but cannot rewrite policy or security authority.
- **P-11 Interoperability without lowest-common-denominator design.** Koquetel
  exposes a canonical model and uses client adapters for weaker surfaces.
- **P-12 Removal is a product feature.** Ownership, uninstall, data export and
  rollback are designed alongside installation.
- **P-13 Operational independence.** Koquetel builds, tests, installs, runs,
  updates, repairs, recovers, exports and uninstalls with PhaseZero and SteamZero
  absent. They are historical research inputs only, never operational components.

## Non-goals

- **NG-01:** create or train a foundation model.
- **NG-02:** replace Codex, Claude Code, OpenCode, Gemini CLI or supported IDEs.
- **NG-03:** provide unrestricted autonomous host administration.
- **NG-04:** bypass provider terms, subscriptions, quotas or security controls.
- **NG-05:** collect prompts or source code for centralized analytics by default.
- **NG-06:** guarantee correctness from semantic memory retrieval alone.
- **NG-07:** become a general desktop provisioning or gaming platform.
- **NG-08:** support every client in v1 at the cost of untested adapters.
- **NG-09:** silently modify user-authored configuration outside managed blocks.
- **NG-10:** make cloud connectivity mandatory for core diagnostics and removal.
