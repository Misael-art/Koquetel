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

## 2026-07-21 — F1 normative schemas

- Added `docs/05-data/schemas/` with `SCHEMA-REGISTRY.md` and eight JSON Schema
  files (draft 2020-12) covering the twenty logical contracts `SCH-01..SCH-20`:
  plan/confirmation, transaction/journal/recovery/ownership, profile-probe/adapter,
  memory-envelope/export, tool-manifest/capability-request/policy-decision,
  delegation/budget/task-checkpoint, event/support-bundle, model-route/usage.
- Each field carries `x-classification`; sensitive fields also carry `x-retention`
  and `x-exportable`, per the classification legend in the registry §4.
- Fields were drawn from existing contracts (transaction record, memory envelope,
  API envelope, error catalog, anti-requirements), not invented; every schema maps
  to requirements, threats/failure modes, acceptance and an `SC-xx` test in §5.
- `$id` uses `urn:koquetel:*` (no network host) to keep schema identity resolvable
  offline, consistent with P-13/NFR-13.
- Added 16 `examples/*.{valid,invalid}.json` (one pair per file) plus two inline
  cross-field invalid cases (confirmation hash mismatch, journal torn tail).
- Verified all 24 JSON files are well-formed. `jsonschema` is not installed, so the
  `SC-01..SC-10` golden tests remain specified, not executed; a dependency-free
  structural checker is added under F4.
- Registered namespaces `SCH-xx`, `SC-xx`, `PT-xx` in `AGENTS.md` and back-filled
  the previously published-but-unregistered `IT-xx`, `AR-xx`, `GA-xx`. Additions
  only; no identifier renumbered.
- Cross-referenced schemas from `DATA-MODEL.md` and the `SC` family from
  `TEST-STRATEGY.md`. No production code, package or host change was made.

## 2026-07-21 — F2 external audit (ai-memory, EA-01)

- Cloned `akitaonrails/ai-memory` read-only into the session scratchpad and
  checked out the observation pin `2a85950`; remote HEAD matched the pin.
- Verified root `LICENSE` MIT © 2026 Fabio Akita. Inventoried 480 tracked files;
  found a Rust + SQLite (`rusqlite`/`refinery`) Cargo workspace, not the assumed
  service shape — relevant to ADR-0002.
- Read `store/src/migrations.rs` (144) and `maintenance.rs` (48) fully with
  SHA-256; read the store-open/pragma region of `lib.rs` and the purge/delete
  surface of `writer.rs`.
- Recorded positive patterns with lines: WAL + tuned pragmas (`lib.rs:91-93`),
  single-writer-actor + reader pool (`lib.rs:69-73,102-103`; `writer.rs:667-685`),
  fail-closed schema-ahead guard with tests (`migrations.rs:31-42,61-113`),
  deletion transparency via `PurgeSummary` and non-empty guard (`writer.rs:660-700`).
- Recorded adoption constraints for Koquetel: `synchronous=NORMAL` is not
  governance-grade durability (`lib.rs:92`); cross-process write concurrency is
  unproven (DEFERRED transactions, `busy_timeout` only, no `BEGIN IMMEDIATE`);
  export is transcript-scoped. Mapped each to G-04/PT-03/FR-05.
- Added `docs/02-research/EXTERNAL-AUDITS.md` (audit template + status table + EA-01),
  narrowed G-03 and G-04 honestly (still open — runtime prototype required), updated
  the source register and robustness-score interpretation.
- Verified PhaseZero and SteamZero were not modified; the clone lives only in the
  scratchpad. No dependency on either source was introduced.

## 2026-07-21 — F3 disposable prototype gates

- Added `docs/08-testing/PROTOTYPE-GATES.md` specifying five disposable prototype
  gates `PT-01..PT-05` (exclusive lock, torn-journal recovery, ai-memory
  durability/concurrency/export/removal, rootless sandbox containment, Rust
  distribution + recovery).
- Each gate defines environment, input, injected fault, expected result, evidence
  artifact, measurable pass/fail and disposal; a shared disposability contract
  keeps prototypes out of the product build graph and off the host.
- Wired PT ids into G-05 (PT-04) and G-11 (PT-01/PT-02), cross-referenced the
  gates from `TEST-STRATEGY.md`, and cited them in roadmap `M-00`. Gates are
  specified only; no prototype was run and no product code was written.
