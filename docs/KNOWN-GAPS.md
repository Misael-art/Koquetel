# Known gaps

Status: living document  
Last reviewed: 2026-07-21

| ID | Severity | Gap | Required closure evidence | Blocks |
|---|---|---|---|---|
| G-01 | critical | Q-01 through Q-05 are not owner-decided | accepted ADRs or signed decision record | implementation approval |
| G-02 | critical | License matrix is pinned, but Koquetel license and component-level compatibility/attribution remain undecided | Q-02 plus per-reused-file/dependency review and accepted attribution plan | any code reuse |
| G-03 | high | ai-memory has an equivalent structural audit (EA-01); RTK, MCP, LiteLLM, OpenHands, Letta and Mem0 remain documentation-level | equivalent pinned structural audits (`EXTERNAL-AUDITS.md`) for each implementation selected as base | final dependency selection |
| G-04 | high | ai-memory structural audit (EA-01) observed WAL/`synchronous=NORMAL` durability, single-writer-actor concurrency, a fail-closed schema-ahead guard and transcript-scoped export; runtime durability, cross-process concurrency, corruption recovery, envelope export and deletion-residue remain unproven | PT-03 fault-injection prototype and recovery report | memory backend acceptance |
| G-05 | high | No sandbox prototype proves workspace performance and containment | Podman/Docker prototype with escape and resource tests | autonomous execution |
| G-06 | high | IDE/CLI config formats and merge semantics are not pinned | adapter fixtures and golden round-trip tests | supported-client commitment |
| G-07 | high | Router quality/cost policy lacks evaluation corpus | representative task corpus and baseline results | automatic model selection |
| G-08 | medium | A2A compatibility value is unvalidated | interoperability spike or explicit deferral ADR | multi-host agents only |
| G-09 | high | Threat model needs independent adversarial review | reviewed threat/control/test matrix | external tool execution |
| G-10 | medium | Branding and trademark availability are unknown | documented search and owner decision | public release |
| G-11 | high | Atomic cross-process lock and torn-tail journal behavior are not prototyped | concurrent acquisition test plus kill-during-append recovery artifact | transaction ADR acceptance |
