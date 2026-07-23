# Independent M-00 adversarial re-review — R2

Review date: 2026-07-22  
Reviewer identity: Codex, operating under the independent-review mandate.  
Reviewed pin: `f086ed7ff5475bf7136e2514b3541388bb82c402` on
`foundation/m00-closure`.  
Review branch: `review/m00-independent-r2`.

## Identity, independence and scope

This reviewer did not author or amend the foundation contracts, schemas,
prototype gates, harnesses, evidence bundles or owner decisions reviewed here.
The reviewer's changes are this R2 report and the append-only WORKLOG entry that
records its result. No contract was changed to obtain a passing result, no product
was implemented and no owner decision was accepted.

The original FAIL report is preserved unchanged at commit
`34f8febdf642fd5a60e0dcb2a0d39d5f9f47e233`; its file content has SHA-256
`3ca5e0fcfb8565c8f98e27dee760616038ea3057fb58b51bb72e64f3ab67ebab`.
This report re-evaluates RF-01..RF-04 independently rather than treating the
author's “remediated” labels as closure.

## Method and reproduced gates

The reviewed pin was exported with `git archive` to a fresh temporary directory.
The validation venv was created outside the repository and installed exactly
`tools/schema_suite/requirements.txt`. The snapshot and venv were deleted after
the run.

| Check | Result | Reproduced evidence |
|---|---|---|
| reviewed source | PASS | clean source worktree; exact pin above |
| `git diff --check` | PASS | `5db024445451c59a0f2f9d18abb3860df7e9fc21..f086ed7ff5475bf7136e2514b3541388bb82c402`: zero output lines |
| foundation lint | PASS | 0 errors, 0 warnings |
| schema suite | PASS | META, SC-01..SC-11 and SEM: 13/13 |
| linter unittest | PASS | 8/8, `OK`; external venv selected through `SCHEMA_VENV_PY` |
| schema digest | PASS | computed and recorded: `74582ae2c147be1e7a7d9fbd5b80fd9ea705e74e907fb51edc07dcf47735590c` |
| JSON parsing | PASS | 78/78 tracked snapshot JSON files parsed |
| prototype hashes | PASS | PT-01..PT-06 `sha256sum -c SHA256SUMS`: every listed file `OK` |
| hash coverage | PASS | actual/covered files: PT-01 13/13, PT-02 10/10, PT-03 10/10, PT-04 9/9, PT-05 12/12, PT-06 13/13; no unlisted or stale path |
| secrets | PASS | no private-key/common-token signatures; six manifests declare `secrets: none` |
| binaries/caches | PASS | no NUL-containing file and no cache, venv, build target or DB artifact in the snapshot |
| implementation gate | PASS | `APPROVED_TO_IMPLEMENT` absent |

These mechanical passes establish syntax, internal hash integrity and the files
that are present. They do not establish that an omitted artifact was retained or
that a harness exercised every criterion claimed by its gate.

## Disposition of prior findings

| Finding | Prior severity | R2 disposition | R2 severity |
|---|---:|---|---:|
| RF-01 | high | **closed** — the acceptance predicate is now unique and coherent | closed |
| RF-02 | high | **closed** — random-128 is the sole v1 proposal; UUIDv7 is rejected/deferred | closed |
| RF-03 | high | **open** — bundles are hash-complete, but retained evidence/harnesses do not satisfy several normative gate criteria | high |
| RF-04 | high | **open** — SCH-21 exists, but its API/version relationship is inconsistent and SC-11 overclaims semantic coverage | high |

### RF-01 — closed — single ADR-0002 predicate

`docs/adr/ADR-0002-RUST-CORE.md:24-47` now defines PT-05 as the sole language
decision predicate and explicitly assigns atomic projection to the M-01 exit and
Podman to PT-04/M-04. The same split appears in
`docs/OWNER-RATIFICATION-PACKET.md:16,25-26`,
`docs/08-testing/prototype-evidence/PT-05-evidence.md:118-125` and
`docs/08-testing/prototype-evidence/PT-04-evidence.md:94-100`. Atomic projection remains in
`docs/12-roadmap/ROADMAP.md:40-44`; G-05 remains an M-04/release block.

The contradiction reported by RF-01 is therefore closed. Whether PT-05 itself
has sufficient evidence is a separate RF-03 question and does not recreate two
competing predicates.

### RF-02 — closed — one v1 identifier proposal

`docs/adr/ADR-0010-SESSION-LIFECYCLE.md:57-96` selects exactly random 128 bits,
32 lowercase hexadecimal characters and no timestamp. The UUIDv7 row says
“no — rejected”; future reconsideration requires a schema version change
(`:111-116`). `docs/OWNER-RATIFICATION-PACKET.md:17,27-30`, SCH-21 and the session
API use the same v1 format. The ADR remains proposed, not self-accepted.

The earlier random-vs-UUIDv7 contradiction is closed. The residual wording
“opaque correlation” at ADR-0010:51 is editorial and does not reopen the choice:
the selected random value carries no embedded timestamp and the operative rule
calls it a correlation identifier, not a credential.

### RF-03 — open high — retained bundles do not prove their declared gates

The remediation is materially better: all six bundles contain manifests,
commands, raw stdout/stderr, metrics, pass/fail files, harness source and hashes;
every present non-`SHA256SUMS` file is covered and all checksums verify. That is
not sufficient for closure because the policy itself says a PASS must be
re-derivable from retained data
(`docs/08-testing/PROTOTYPE-EVIDENCE-POLICY.md:61-62,86-98`).

Concrete failures include:

1. **PT-01 omits required raw evidence and a mandatory arm.** The gate requires
   the full per-acquisition log and two OFD-close variants
   (`docs/08-testing/PROTOTYPE-GATES.md:54-68`). The manifest admits the
   10,000-line log is not retained
   (`docs/08-testing/prototype-evidence/PT-01/manifest.json:9`), so the overlap
   result cannot be re-derived
   from the 200-line sample. The harness implements only “child closes, parent
   keeps the OFD” (`docs/08-testing/prototype-evidence/PT-01/harness/main.rs:35-58`); the required parent-closes-first
   variant is absent, and the drive script runs only 100 serial fork iterations
   (`drive.sh:9-10`), not the mandatory fork-injected contention arm. Only tmpfs
   was exercised although the gate separately names ext4/XFS and tmpfs.

2. **PT-03's critical arms test a local fixture, not the required adapter/store
   path.** The gate requires in-process and cross-process clients, corruption of
   both the DB and `-wal`, a kill during a write batch, SCH-10 adapter round-trip
   and a complete physical-residue report (`docs/08-testing/PROTOTYPE-GATES.md:184-205`). The
   retained Python harness creates its own three-column `records` table and uses
   its own `BEGIN IMMEDIATE` operations (`docs/08-testing/prototype-evidence/PT-03/harness/harness.py:8-35`). It
   checkpoints away the WAL and corrupts only the main DB (`:37-51`), has no kill
   arm, performs a raw table copy rather than an SCH-10 envelope (`:53-65`), and
   reports only queryable row count after `DELETE` (`:67-72`). The real ai-memory
   test log proves 180 upstream tests passed, but it does not bind those missing
   fault arms to ai-memory. `commands.txt:4` is shorthand rather than an executable
   orchestration command.

3. **PT-05 declares PASS without its named environment.** The gate requires a
   clean Linux host/container with no Rust toolchain and a connection from a
   non-owner user (`docs/08-testing/PROTOTYPE-GATES.md:236-252`). The manifest explicitly lists
   the fresh-container arm as not executed (`docs/08-testing/prototype-evidence/PT-05/manifest.json:8`). The
   peer-credential arm runs the same user while configuring `owner_uid=me+1`
   (`docs/08-testing/prototype-evidence/PT-05/harness/drive.sh:18-20`); it exercises the mismatch branch but not the
   declared second-user environment.

4. **PT-06 does not perform the normative journal-fencing arm.** The gate requires
   an old-epoch journal write after takeover and recovery-reader behavior for
   provably stale and ambiguous cases (`docs/08-testing/PROTOTYPE-GATES.md:121-150`). The harness
   calls a pure classifier over four in-memory fixtures
   (`docs/08-testing/prototype-evidence/PT-06/harness/main.rs:31-58`); it never writes or recovers a journal entry.
   `kill-holder` acquires the OFD and immediately self-kills without a journal or
   transactional mutation (`:74-77`). The retained stderr also includes a
   `DatabaseBusy` panic
   (`docs/08-testing/prototype-evidence/PT-06/stderr.log:28-30`), honestly attributed to an
   earlier run, but the drive script uses `set -u` and does not machine-bind its
   printed result to `pass-fail.json`.

Consequently the PASS claims for PT-01/PT-03/PT-05/PT-06 are not established by
their normative gates. The readiness assertions that the high-risk prototype
item is done (`FOUNDATION-READINESS-REPORT.md:120,125`) and that G-04/G-11 are
closed (`docs/KNOWN-GAPS.md:11,18`) exceed the retained evidence. RF-03 remains
open high.

### RF-04 — open high — session contract/API/test mismatch

SCH-21 is a real strict v1 schema: it requires a 32-lowercase-hex `sessionId`,
state and timestamps; SC-11 has one valid and five invalid examples; the API
documents `_meta["io.koquetel/sessionId"]`, lifecycle errors and stateless
absence. This closes the earlier total absence of a session artifact, but not the
finding as a complete, versioned and tested interface.

Two independently reproduced contradictions remain:

1. `docs/06-api/CONTRACTS.md:104-106` says `session/end` produces `ended` **with both**
   `endedAt` and `endReason`. SCH-21's conditional requires only `endedAt`
   (`docs/05-data/schemas/session.schema.json:24-28`). With the pinned validator,
   an ended handle with
   `endedAt` but no `endReason` is schema-valid (`validator_errors=[]`). The schema
   therefore accepts a state the API excludes.
2. The API transports only a bare `sessionId` in `_meta`
   (`docs/06-api/CONTRACTS.md:100-102`)
   while claiming `SessionHandle.schemaVersion` provides version negotiation
   (`:114-116`). No version accompanies that wire value, and SC-09 tests only the
   EventRecord strict/tolerant pair
   (`docs/05-data/schemas/examples/manifest.json:25-30`), not a session
   wire envelope.

The registry also states that SC-11 asserts expiry ordering, terminal-state
transitions, identifier immutability and “authority never derived from id”
(`docs/05-data/schemas/SCHEMA-REGISTRY.md:175-182`). The executor validates five schema-invalid
fixtures and lexically compares timestamps in the single valid fixture
(`tools/schema_suite/run_suite.py:153-169`); it contains no transition,
immutability or authority test. Nevertheless TRACEABILITY cites SC-11 for the
SR-01 authority property (`docs/TRACEABILITY.md:71`). This is a false-positive
security/test trace, not merely missing product runtime. RF-04 remains open high.

## New findings

### RF-05 — medium — rerun bundles and retained summaries diverge

- **Location:** `docs/08-testing/prototype-evidence/PT-04-evidence.md:53-65,76-80`;
  `docs/08-testing/prototype-evidence/PT-04/manifest.json:6-8`;
  `docs/08-testing/prototype-evidence/PT-04/harness/drive.sh:34-51`.
- **Observed mismatch:** the retained Markdown body says a fork storm was blocked
  and reports 12 ms overhead. The RF-03 rerun manifest says the cgroup/pids arm was
  not executed, its harness has no fork-storm/`RLIMIT_NPROC` arm, and the current
  bundle reports 8 ms. Similar historical/current numeric drift exists in PT-06.
- **Impact:** a reader can cite a historical number or arm as current even though
  the top banner points to the newer bundle. The canonical bundle is present and
  G-05 remains open, so this does not rise to high severity.
- **Required resolution:** label historical result sections explicitly as
  superseded and provide one current summary derived from the hash-pinned bundle;
  do not rewrite the raw bundle.
- **Disposition:** open, medium.

No additional RF was opened for the weak PT-04 direct-child `pgrep` check or for
its absent Podman/allowlist arms: those observations reinforce the already
PARTIAL verdict and open G-05 rather than creating a distinct high-risk failure.

## Readiness and Podman/G-05

The overall classification remains **NOT READY**, which is consistent with the
absence of implementation approval. Podman/G-05 has not been improperly removed:
`docs/KNOWN-GAPS.md:12`, `docs/08-testing/PROTOTYPE-GATES.md:264` and
`OWNER-RATIFICATION-PACKET.md:20,34-35` still block M-04, external tool execution
and any sandbox-declared release until a real rootless Podman plus allowlist run.

## Decision

Open findings after R2:

- RF-03 — high;
- RF-04 — high;
- RF-05 — medium.

RF-01 and RF-02 are closed. PASS requires zero open critical and zero open high
findings. That condition is not met.

**Decision: FAIL.** This review does not close G-09, does not advance M-00, does
not ratify ADR-0002/0010/0011 and does not create or imply implementation
authorization.
