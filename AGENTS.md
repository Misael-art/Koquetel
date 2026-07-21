# AGENTS.md — Koquetel foundation governance

These rules apply to every human or AI agent working in this repository.

## Foundation gate

- The repository is in documentation-only foundation phase.
- Do not add production code, installers, services, packages, generated release
  artifacts, or host mutations before explicit implementation approval.
- Allowed work: research, documentation, schemas as documented examples,
  diagrams, non-production prototypes explicitly marked disposable, and
  read-only validation.
- Absence of an `APPROVED_TO_IMPLEMENT` file means implementation is forbidden.

## Evidence and honesty

- Claims about a source project cite repository, commit/version, path, and the
  observed behavior. A README claim alone is not implementation evidence.
- Do not silently resolve owner decisions. Record them in
  `docs/OPEN-QUESTIONS.md` with options and consequences.
- Record assumptions and invalidation conditions in `docs/ASSUMPTIONS.md`.
- Record incomplete research and missing proof in `docs/KNOWN-GAPS.md`.
- Never mark a requirement complete because a document exists; require evidence
  of consistency, feasibility, testability, and traceability.

## Stable identifiers

Use and preserve these namespaces:

- `P-xx`: principle; `NG-xx`: non-goal; `FR-xx`: functional requirement;
- `NFR-xx`: non-functional requirement; `AC-xx`: acceptance criterion;
- `SR-xx`: security requirement; `FM-xx`: failure mode;
- `FI-xx`: failure-injection test; `RT-xx`: rollback test;
- `E-xxxx`: stable error; `R-xx`: risk; `M-xx`: milestone;
- `G-xx`: known gap; `Q-xx`: owner decision; `A-xx`: assumption;
- `ADR-xxxx`: architectural decision.

Identifiers are never renumbered after publication. Retired identifiers remain
listed as retired. Every normative `MUST`, `SHALL`, or `NEVER` statement needs an
identifier or must be inside an already identified requirement.

## Source and reuse safety

- PhaseZero and SteamZero are read-only research sources, never runtime or build
  dependencies.
- Koquetel must build, test, install, run, update, repair, recover, export and
  uninstall when both source projects and all their paths/services are absent.
- Production imports, commands, required paths, submodules, packages, services or
  live-state reads referencing either project are prohibited.
- No source code is copied until license compatibility and provenance are
  recorded. Unknown license means reimplement behavior without code beside it.
- Secrets, tokens, credentials, raw prompts, and private memory content never
  enter tracked files.

## Change discipline

- Update cross-references when changing a contract.
- Add contradictory or unresolved findings to the honesty files immediately.
- Append evidence to `docs/WORKLOG.md`; never rewrite earlier entries to make the
  history appear cleaner.
- A readiness classification can only improve when its stated blockers have
  objective evidence of resolution.
