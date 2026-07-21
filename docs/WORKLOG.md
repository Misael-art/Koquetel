# Foundation worklog

Append-only evidence log.

## 2026-07-21 — Initial foundation

- Confirmed Koquetel repository had no commits and no tracked project files.
- Read PhaseZero AI tooling overview and structural portions of its memory, MCP,
  compatibility, status and routing scripts.
- Read SteamZero governance and project-synthesis methodology as process input.
- Surveyed primary documentation for MCP authorization, OpenTelemetry GenAI,
  Letta memory, Mem0 graph memory, LiteLLM routing, OpenHands sandboxing and A2A.
- Established documentation-only implementation gate, stable identifier system,
  honesty files and initial readiness blockers.
- No source project was modified. No production code or host change was made.

## 2026-07-21 — E1/E2 local evidence and E3 synthesis pass

- Pinned PhaseZero at `a0468ba92ac7b12aa852691897b27ff210f51fa6`
  and SteamZero at `10f3510681f44db368a2b7a6c332036bb086981d`.
- Recorded dirty/untracked source state and excluded it from committed evidence.
- Pinned observed remote HEADs for ai-memory, RTK, MCP, Letta, Mem0, LiteLLM,
  OpenHands, OpenTelemetry SemConv and A2A.
- Verified root license texts at pins; PhaseZero has no tracked root license.
- Inventoried 536/345 tracked files and 118/80 test paths in local sources.
- Read three structural files fully in each local source and inspected their
  transaction/MCP/rule callers with line-numbered committed content.
- Produced capability matrix, anchored weighted robustness score (45.25
  PhaseZero, 85.00 SteamZero), gap analysis, concept provenance and ten named
  anti-requirements.
- Found two required corrections even in the stronger transaction source:
  non-exclusive lock acquisition and non-tolerant JSONL tail parsing.
- Reconfirmed that no source repository was modified.

## 2026-07-21 — Independence invariant confirmed by owner

- Owner clarified that Koquetel must operate without depending on SteamZero or
  PhaseZero in any lifecycle phase.
- Promoted the rule from assumption to accepted ADR-0001 and added P-13, NFR-13
  and AC-17.
- Defined IT-01..IT-08 to test default dependency graph, production literals,
  package contents, clean-host lifecycle, absence of runtime discovery, capability
  parity and post-migration severance.
- Reworded research matrices to distinguish evidence sources from technical bases
  or dependency choices.
