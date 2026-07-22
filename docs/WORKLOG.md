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

## 2026-07-21 — Correction pass: PT-01 dedup, EA audits, linter tests, ADRs

Brought the uncommitted corrections from the previous evaluation cycle into a
consistent, validated state:

- **PT-01 deduplication.** `PROTOTYPE-GATES.md` had `### PT-01 Filesystem semantics`
  which `foundation_lint` counted as a second canonical definition for `PT-01`,
  producing a `[duplicate-id]` error. Renamed to `### Filesystem semantics`.
- **PT-01..PT-06 reconciliation.** Five documents referenced the old `PT-01..PT-05`
  set — all updated to `PT-01..PT-06`. Historical WORKLOG entries (e.g. F3) left
  unchanged per append-only rule. ROADMAP.md, READINESS-REPORT.md, TRACEABILITY.md,
  TEST-STRATEGY.md updated.
- **FR-07/SC-05/SC-06 misinterpretation check.** Searched all foundation docs for
  incorrect associations. PRD correctly defines FR-07 as drift detection.
  SCHEMA-REGISTRY correctly maps SC-05 to SCH-11..13 and SC-06 to SCH-14..16
  (TaskCheckpoint = SCH-16 under SC-06). No corrections needed.
- **EA-02 corrected.** The AC-NFS claim "RTK's lock/heartbeat mechanisms rely on
  flock" was false — `rg -n flock` across all RTK `.rs` files at `66e09cb` returned
  zero hits. RTK has no locking of its own. Replaced with AC-NO-LOCK noting the
  absence and that Koquetel must implement its own lease (PT-01/PT-06).
- **EA-03 date clarified.** "spec revision 2026-07-28" changed to note that
  `"2026-07-28"` is the protocol version string embedded in the spec documents at
  the pinned commit, not a document publication date. Verified by fetching the spec
  `basic/index.mdx` at `88191b9` which shows `"2026-07-28"` as the
  `io.modelcontextprotocol/protocolVersion` example.
- **PT-01 filesystem table cited.** Added primary source citations (Linux man-pages,
  kernel tmpfs.txt, nfs(5), lockd(8)) for each claim about O_EXCL, flock and lease
  visibility on ext4/XFS, tmpfs and NFS.
- **Linter tests converted to unittest.** `tools/tests/test_foundation_lint.py`
  rewritten as `unittest.TestCase` — `test_*` methods discoverable by
  `python3 -m unittest discover -s tools/tests -v`. Replaced the no-op
  `test_missing_classification_not_linted` with `test_stale_schema_suite_rejected`
  (proves lint rejects stale RESULT.json) and
  `test_missing_required_classification_schema_suite` (proves removing
  x-classification from a `$defs` property makes SC-10 fail). All 8 tests pass.
- **Schema suite evidence.** Confirmed clean venv install from requirements.txt,
  re-ran suite: 12/12 PASS, digest matches current schemas. Example count verified:
  40 entity examples (20 SCH × 2) + 2 SC-09 extras (tolerant, major2) = 42 example
  files plus manifest.json.
- **ADR-0010 (session lifecycle)** and **ADR-0011 (lease recovery/fencing)**
  produced as proposed. Both reference prototype gates as prerequisites and record
  unresolved owner questions.
- **`.venv`, `__pycache__`, `.pyc`** are gitignored and excluded from tracked content.

No APPROVED_TO_IMPLEMENT created. No production code, package or host change.

## 2026-07-21 — F4 traceability, documentation lint and readiness

- Added `tools/foundation_lint.py` (stdlib only, read-only, non-product): checks
  duplicate ID definitions, broken ID/link references, requirements without a
  traceability row/test, accepted decisions still listed open, and schema-example
  JSON well-formedness. It exits non-zero on any error.
- Expanded `docs/TRACEABILITY.md` to one row per requirement (FR-01..26,
  NFR-01..13, SR-01..16, AC-01..17), each mapped to risk, failure mode, acceptance
  and a verification family; added schema/prototype coverage notes.
- Iterated the linter to remove false positives (section-heading vs ledger-row
  double counting; range/negation phrasing near open Q-ids) until it reports
  `0 error(s), 0 warning(s)`.
- Registered the `EA-xx` namespace in `AGENTS.md`.
- Updated `FOUNDATION-READINESS-REPORT.md` honestly: recorded schemas, EA-01,
  prototype gates and full traceability as established; kept every unresolved
  blocker (owner decisions, license, ADR acceptance, SC/prototype execution,
  independent review) and held the classification at **NOT READY**.
- No `APPROVED_TO_IMPLEMENT` created. No production code, package or host change.

## 2026-07-21 — Corrective review: readiness counts and schema compatibility

Inconsistencies found (verified against canonical docs, not substituted blindly):

- readiness said "12 principles" — VISION defines P-01..P-13 → corrected to 13;
- readiness said "12 non-functional requirements" — PRD defines NFR-01..NFR-13 →
  corrected to 13;
- readiness said "16 product acceptance criteria" — ACCEPTANCE defines AC-01..AC-17
  → corrected to 17;
- readiness executive assessment implied the traceability matrix was incomplete
  while a later bullet claimed one row per requirement → differentiated:
  *structural* coverage complete, *proven* evidence still pending;
- verified the still-accurate counts (10 non-goals, 26 FR, 16 SR, 20 FM, 10 AR,
  10 GA, 8 IT, 20 SCH) and left them unchanged.

Schema compatibility contradiction resolved (strict-write / tolerant-read):

- `SCHEMA-REGISTRY.md` §3 rewritten: strict-write records (all SCH-01..SCH-20) use
  `schemaVersion const: 1` and `additionalProperties: false`; additive change is a
  documented minor with a schema revision; read-only consumers use a *separate*
  tolerant profile that requires a known major, tolerates unknown optional fields,
  and may never feed a mutating/authority operation. The false "a single
  additionalProperties:false schema is forward-tolerant" claim was removed.
- Set `schemaVersion` to `const: 1` in all 19 entity definitions across the eight
  schema files.
- Added an explicit tolerant profile `tolerant-read/event.tolerant.schema.json`
  (SCH-17) plus `examples/event.tolerant.valid.json` carrying an unknown field the
  strict schema rejects but the tolerant profile accepts.
- Rewrote `SC-09` into five sub-tests and made `SC-01..SC-08` individually defined;
  `SC-10` is now recursive. Execution is delivered in the next commit.
- Validated: JSON well-formed, `foundation_lint` 0/0.

## 2026-07-21 — R1 red-team architectural review: ADR-0010 and ADR-0011

Red-team corrections applied to both ADRs and all downstream honesty and
traceability files. Architecture not expanded; only rigor corrections.

### ADR-0011 corrections (rigor pass)

- **H. Howard reference removed**: unverifiable — no DOI, URL or primary-source
  bibliographic confirmation provided. The six-concern taxonomy is now
  explicitly identified as Koquetel's own analytical decomposition.
- **OFD lock claims corrected**: table and prose now state clearly that
  OFD/flock are **cooperative advisory** — they prevent lock acquisition by
  another cooperating process but do **not** prevent I/O from a process that
  ignores the protocol. The old claim "I/O error on stale fd" for concern 4
  (fence at commit) was removed. OFD lifecycle section rewritten with precise
  fork/exec/dup semantics: dup preserves lock across multiple fds until the
  last close; fork shares the same OFD; exec with CLOEXEC closes the fd.
- **"Decision (proposed)" changed to "Candidate direction (blocked by G-13 /
  PT-06)"**: ADR-0011 cannot reach a definitive proposed decision until G-13
  (conditional atomic commit primitive) and PT-06 (kill-fault injection with
  epoch evidence) provide evidence. A blocked status is honest about this.
- **Journal epoch semantics fixed**: the simple `entry.leaseEpoch <
  currentLeaseEpoch` discard rule was rejected — a committed entry from a prior
  epoch is legitimate history. Four conceptual states documented (prepared,
  committed, aborted/quarantined, recovered). An entry may only be rejected
  with evidence it was produced after its epoch was revoked or never reached
  valid commit. Shortfall recorded in G-13.
- **NFS position changed to unsupported/proposed for v1**: NFSv3/lockd vs
  NFSv4 integrated locking distinguished. Heartbeat + epoch counter mechanism
  acknowledged as non-atomic (a live stale holder continues writing). NFS
  v1 support requires G-13 or a distributed fencing protocol. Q-08 created
  for owner decision on future v2 support.
- **Consequences table rewritten**: removed "zero-cost fencing", "fencing
  filesystem-independent", "covers all environments from local dev to NFS-backed
  CI" as inaccurate.
- Epoch journal-scoped isolation assumption removed from ASSUMPTIONS.md —
  not proven; uncertainty remains in G-13.
- **FM-21/FM-22 corrected**: FM-21 guaranteed state changed to "not guaranteed;
  blocks ADR acceptance until G-13"; external effects classified as possibly
  irreversible. FM-22 detection moved to startup-time check; response changed
  to fail-closed + controlled rekey; DB restore epoch regression documented
  as realistic risk.
- **Prerequisites rewritten**: NFS removed as gate requirement; G-13, Q-03,
  Q-08 added.

### ADR-0010 corrections (rigor pass)

- **MCP statelessness made precise**: references draft removal of
  `initialize`/`Mcp-Session-Id`; notes `clientInfo`/`serverInfo` are
  self-reported and MUST NOT be used for security decisions.
- **Extension namespace specified**: `io.koquetel/sessionId` in `_meta`
  (MCP extension convention).
- **UUIDv7 table corrected with RFC 9562**: bit layout (48-bit ts, 74-bit
  random in typical layout), collision probability 2^(-74) per ms (not 2^(-122)),
  monotonicity requires explicit per-ms counter (RFC 9562 §6.2), timestamp
  opacity noted as acceptable for internal correlation handle. Choice kept as
  **proposed** until a requirement/benchmark confirms ordering benefit over
  random 128-bit.
- **ADR prerequisite inconsistency corrected**: the Status header referenced
  Q-06 as a dependency; corrected — session lifecycle semantics are identical
  for individual and team deployments. No owner decision on Q-04 or Q-06 was
  made.

### Honesty / traceability updates

- **KNOWN-GAPS.md**: G-13 (conditional atomic commit primitive / revocation-proof
  epoch design), G-14 (serialized epoch counter measurement).
- **ASSUMPTIONS.md**: stale assumption removed (not proven; uncertainty
  remains in G-13).
- **OPEN-QUESTIONS.md**: Q-08 added (NFS commit-level fence requirement).
- **FAILURE-MODES.md**: FM-21 (TOCTOU stale write — blocks ADR-0011 acceptance,
  fail-closed quarantine, external effects possibly irreversible). FM-22
  (epoch wraparound/restore regression — startup detection, controlled rekey).
- **PROTOTYPE-GATES.md**: PT-01 gains OFD lifecycle arm (fork fd close); PT-06
  gains dup survival and exec CLOEXEC arms.
- **TRACEABILITY.md**: FM-21, FM-22 linked to FR-03, NFR-03.
- **SCHEMA-REGISTRY.md**: SCH-04 references FM-21, FM-22, PT-06.

No `APPROVED_TO_IMPLEMENT` created. No production code, package or host change.

## 2026-07-21 — R2 editorial microcorrections

- **ADR-0010**: "opaque sessionId" → "correlation sessionId" (UUIDv7 is not
  fully opaque; it reveals ms timestamp). Collision table for Random 128-bit
  uses birthday bound ~n²/2^129 for consistency with UUIDv7 row. Choice
  remains proposed.

No `APPROVED_TO_IMPLEMENT` created. No production code, package or host change.

## 2026-07-21 — M-00 owner decisions Q-01..Q-08 (ADR-0006)

The project owner explicitly answered all eight open questions. No recommendation
was auto-converted; each answer came from the owner via the decision packet.

- **ADR-0006** created and marked *accepted by project owner*, recording:
  - Q-01 = Koquetel (trademark/domain review still open under G-10);
  - Q-02 = Apache-2.0 (component-level attribution plan still open, G-02
    narrowed);
  - Q-03 = Linux first, WSL next (Windows/macOS out of v1);
  - Q-04 = Balanced (accepts ADR-0003; unblocks ADR-0010's session-start
    confirmation question);
  - Q-05 = local-first with cloud opt-in;
  - Q-06 = individual developer v1 (no multi-user control plane);
  - Q-07 = CLI first (local read-only dashboard may follow; native UI out);
  - Q-08 = NFS unsupported in v1 (multi-host lease deferred to potential v2,
    requires G-13).
- **OPEN-QUESTIONS.md** rewritten to a "Decided" section (Q-01..Q-08 rows kept
  for history with an "Option chosen" column) + an empty "Still open" section.
  IDs preserved, no renumbering.
- **KNOWN-GAPS.md**: G-01 → closed; G-02 → narrowed (license selected,
  attribution plan open).
- **ADR-0003** → accepted via Q-04 = Balanced.
- **ADR-0010** status: Q-04 prerequisite closed; still proposed on prototype
  evidence (PT-01/PT-02/PT-06).
- **ADR-0011** status: Q-03/Q-08 prerequisites closed (local-fs scope
  confirmed); still proposed on PT-01/PT-06/G-13.
- **LICENSE-MATRIX.md / REUSE-POLICY.md**: updated to Apache-2.0 compatibility
  view; SteamZero GPL-3.0 explicitly excluded from copying; PhaseZero still
  no-license; no-copy block stays until G-02 attribution plan is written.
- **PRD §4, DATA-MODEL, EXTERNAL-AUDITS, FOUNDATION-GOVERNANCE §5,
  FOUNDATION-READINESS-REPORT, ROADMAP M-00**: made consistent with ADR-0006
  (Q-xx references updated from "pending" to "closed" where applicable).
- **Validation**: `foundation_lint.py` re-run → 0 error(s); `unittest` 8/8 OK;
  schema suite 12/12 PASS (created the gitignored
  `tools/schema_suite/.venv` with the pinned validator since it was absent;
  only `RESULT.json` timestamp changed, summary stable).

No `APPROVED_TO_IMPLEMENT` created. No production code, package, service or host
change was made. Work is on branch `foundation/m00-closure`.