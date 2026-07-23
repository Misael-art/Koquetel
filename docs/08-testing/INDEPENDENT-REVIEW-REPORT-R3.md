# M-00 adversarial review — R3

Review date: 2026-07-23  
Reviewed pin: `e67710ba9647b619ff5ee4f0a639501b4d4a1b1d`  
Review branch: `review/m00-independent-r3`

## Identity, independence and scope

The requested reviewer identity cannot be asserted truthfully. The active Codex
task that performed this review also produced the immediately preceding
remediation commits `a227009`, `d2cd633` and `e67710b`. Therefore this report is
an adversarial technical audit of the requested pin, but it is **not valid
independent closure evidence for G-09**. A separate reviewer that did not author
those changes is still required.

The R1 report remains at commit
`34f8febdf642fd5a60e0dcb2a0d39d5f9f47e233` (report SHA-256
`3ca5e0fcfb8565c8f98e27dee760616038ea3057fb58b51bb72e64f3ab67ebab`).
The R2 report remains at commit
`30b0038dd3ca3c494c9414be6e8c33fe77ce195c` (report SHA-256
`2eb0b4e8d23248cc0bef9806f2dc2ea7dacb76a30ab2ac58e14deb0475007e3c`).

The source worktree was clean before branching from the exact reviewed pin.
`APPROVED_TO_IMPLEMENT` was absent. No contract, schema, harness, evidence
bundle, prototype verdict or prior report was changed during this audit. This
report does not implement product and does not authorize implementation.

## Method and deterministic gates

The reviewed pin was attached as a detached Git worktree below a fresh
`mktemp` directory. Validation used the existing external foundation virtual
environment; generated schema-suite state and Python caches existed only in the
temporary snapshot and were removed with it.

| Check | Result | Reproduced evidence |
|---|---|---|
| source state | PASS | exact pin above; clean source worktree; approval marker absent |
| `git diff --check` | PASS | `5db024445451c59a0f2f9d18abb3860df7e9fc21..e67710b`: literal output was zero lines; snapshot worktree check also zero lines |
| foundation lint | PASS | 0 errors, 0 warnings |
| schema suite | PASS | META, SC-01..SC-11 and SEM: 13/13 |
| linter unittest | PASS | 9/9, `OK` |
| isolated SC-11 mutation unittest | PASS | 1/1, `OK` |
| schema digest | PASS | computed and recorded `54a81cf7a0c1559871625f5ebfa96795cfe792ae47d7d8d743e56e6c636c857f` |
| JSON parsing | PASS | 122/122 tracked JSON files parsed |
| prototype hashes | PASS | all ten `SHA256SUMS` files (the original six plus four R2 bundles) verified |
| hash coverage | PASS | PT-01 13/13; PT-01-R2 20/20; PT-02 10/10; PT-03 10/10; PT-03-R2 80/80; PT-04 9/9; PT-05 12/12; PT-05-R2 34/34; PT-06 13/13; PT-06-R2 16/16; no missing or stale path |
| secrets | PASS | zero private-key/common-token signature matches; bundle manifests declare synthetic/no-secret inputs |
| binaries/caches/DBs | PASS | 366 tracked files, zero NUL-containing files, caches, virtual environments, build targets, SQLite/DB/WAL/SHM artifacts; test-created temporary caches removed |
| source-project independence | PASS for the foundation tree | zero PhaseZero/SteamZero references in Rust, Python, shell, Cargo or Docker harness sources; no product runtime exists to execute IT-05..IT-08 |

All four retained derivation scripts were executed over their bundle data:
PT-01-R2 re-derived `PARTIAL`, and PT-03-R2/PT-05-R2/PT-06-R2 re-derived
`PASS`. The regenerated `metrics.json` and `pass-fail.json` files were byte-for-
byte identical to the tracked versions; only the schema suite's timestamped
temporary `RESULT.json` differed in the snapshot.

Mechanical validity and derivation reproducibility do not prove that a
derivator encodes every normative gate criterion. That distinction controls
RF-03 and RF-04 below.

## Prior finding dispositions

| Finding | R2 state | R3 disposition | R3 severity |
|---|---|---|---|
| RF-01 | closed | **closed** — no predicate regression | closed |
| RF-02 | closed | **closed** — no identifier-choice regression | closed |
| RF-03 | open high | **open** — PT-06 is declared PASS without the gate's 10,000-operation transactional contention arm or a machine-enforced recovery bound | high |
| RF-04 | open high | **open** — SCH-21/API shape is repaired, but SC-11 accepts `expiresAt == createdAt` although the contract requires `expiresAt > createdAt` | high |
| RF-05 | open medium | **closed** — every PT report now separates the current canonical section from superseded history | closed |

### RF-01 — closed — ADR-0002 has one coherent gate

`docs/adr/ADR-0002-RUST-CORE.md:24-47` makes PT-05 the sole Rust
language-decision gate, assigns atomic projection to the M-01 exit and assigns
Podman to PT-04/M-04. `docs/OWNER-RATIFICATION-PACKET.md:25-26` and
`docs/12-roadmap/ROADMAP.md:39-43` preserve the same split. G-05 remains high
and explicitly blocks M-04, external execution and every sandbox-declared
release (`docs/KNOWN-GAPS.md:12`).

The six evidence reports put contradictory old prose below an explicit
`HISTORICAL — SUPERSEDED; NOT CANONICAL FOR CURRENT VERDICT` boundary. No
canonical evidence reintroduces the former competing ADR-0002 predicate.

### RF-02 — closed — random-128 remains the only v1 proposal

`docs/adr/ADR-0010-SESSION-LIFECYCLE.md:68-121` selects a 128-bit CSPRNG
identifier encoded as 32 lowercase hexadecimal characters and rejects UUIDv7
for v1. `docs/OWNER-RATIFICATION-PACKET.md:27-30`,
`docs/05-data/schemas/session.schema.json`, and
`docs/06-api/CONTRACTS.md:95-102` agree. A future format requires an explicit
schema-version change; UUIDv7 is not a parallel v1 option.

### RF-03 — open high — PT-06 PASS exceeds its executed gate

The remediation closes most of the original evidence defects:

- **PT-01 is honestly PARTIAL.** The retained CSVs contain 10,000 main rows,
  10,000 fork-A rows and 10,000 fork-B rows, each from 100 holders; all three
  detectors report zero overlap. `filesystem-probe.txt` identifies tmpfs and
  records ext4/XFS as blocked without simulation. G-11 is reopened, and
  ADR-0010/ADR-0011 remain unratifiable.
- **PT-02 remains PASS.** Its accepted R2 bundle is unchanged and hashes still
  verify.
- **PT-03 is supported as PASS.** `harness/Cargo.toml` is substituted with the
  real ai-memory checkout, `main.rs` imports `ai_memory_store::Store`, and the
  clean before/after source records both show `2a85950`. The retained ledgers
  contain 10,000 in-process and 10,000 cross-process rows. The bounded
  `0..=100` retry loops return an error at exhaustion; the run used 2,769
  `SQLITE_BUSY`/locked retries with maximum 49, zero missing and zero wrong
  digests. The SIGKILL/resume, independently corrupted main DB and live WAL,
  SCH-10 validation/digest round-trip, purge and physical inventory are retained
  and re-derived.
- **PT-04 remains honestly PARTIAL.** Podman and network allowlisting are absent;
  G-05 remains open. The canonical report claims 8 ms and does not claim a fork
  storm or cgroup `pids.max`.
- **PT-05 is supported as PASS for the gate actually written.** The binary was
  built outside and copied into a fresh Ubuntu 24.04 image. The transcript
  records no `rustc`/`cargo`, real UIDs 1001/1002, mode 0600 denial, a separate
  SO_PEERCRED denial, idempotent migrations, glibc dependencies, kill recovery
  and 23 ms cold start. It has no Podman dependency.

PT-06 does not support its declared full PASS. Its normative input is the
“same N-process contention harness” as PT-01 with a transactional counter
(`docs/08-testing/PROTOTYPE-GATES.md:103-107`); PT-01 defines that input as at
least 100 processes and 10,000 contended acquisitions (`:43-46`). The R3 scope
also expressly requires a 10,000-operation transactional counter.

The canonical harness instead runs 20 sequential holder-kill cycles
(`PT-06-R2/harness/pt06.py:145-177`), increments the SQLite epoch/counter once
per cycle, and writes `expectedCounter: 20` (`:224-267`). Its derivator
hard-codes `counter == 20` as PASS (`harness/derive.py:25-29`). There is no
100-process/10,000-operation transactional contention arm.

The gate also requires recovery against a declared bound and says unbound
recovery fails (`PROTOTYPE-GATES.md:113-120,151-155`). The R2 derivator records
`maxRecoveryUs` but never compares it with the historical 1,000 ms bound.
`docs/KNOWN-GAPS.md:21` candidly admits that the R2 bundle does not claim a
10,000-operation benchmark, yet the bundle, matrix and readiness report still
classify PT-06 as full PASS.

The persisted/fsynced journal, old-epoch write after revocation, preserved
history, quarantine, ambiguity escalation, current write, digest-chain recovery
reader, 20 kill/reclaims, exec+CLOEXEC and dup arms are real. They justify a
partial result, not a full gate PASS. Because a missing mandatory arm must yield
PARTIAL/BLOCKED and readiness must propagate that result, RF-03 remains open
high.

### RF-04 — open high — strict expiry ordering is not tested

The structural remediation is real:

- `ended` requires both `endedAt` and `endReason`, whose enum is bounded;
- `SessionRef` contains only `schemaVersion` and `sessionId`, with
  `additionalProperties: false`;
- `_meta["io.koquetel/session"]` carries the versioned object;
- unknown major fails closed; absent metadata remains stateless;
- fixtures cover malformed/uppercase/size/state/base-required fields, ended
  fields, enum, malformed/versioned refs and authority/capability rejection;
- transition functions execute terminal-state and identity invariants rather
  than performing lexical source checks;
- TRACEABILITY limits SC-11 to shape/lifecycle/no-authority-fields and leaves
  runtime SR-01 authorization to M-04.

One normative invariant is still false-positive. SCH-21 says `expiresAt` “MUST
be later than createdAt” (`session.schema.json:18`), and the R3 criterion is
`expiresAt > createdAt`. `session_time_order` implements
`created <= activity <= expires` (`tools/schema_suite/run_suite.py:57-64`).
An in-memory mutation that set `createdAt`, `lastActivityAt` and `expiresAt` to
the same timestamp reproduced:

```text
SCHEMA_VALID True
SEMANTIC_TIME_ORDER True
```

The SC-11 mutation unittest covers eleven repaired cases but has no equality
boundary case (`tools/tests/test_foundation_lint.py:249-297`). Consequently the
suite can remain 13/13 while accepting a lifecycle state excluded by the
contract and the requested criterion. RF-04 remains open high.

### RF-05 — closed — current and historical PT narratives are separable

Each `PT-01-evidence.md` through `PT-06-evidence.md` begins with a short
“Current canonical rerun” section bound to the current bundle's metrics,
pass/fail file and checksum index. Each then marks all older prose
`HISTORICAL — SUPERSEDED; NOT CANONICAL FOR CURRENT VERDICT`.

The PT-04 current section uses 8 ms and explicitly disclaims fork-storm and
cgroup coverage. PT-06's current section uses counter/epoch 20; its old 10,000
claim is below the superseded boundary. This closes the reader-confusion/drift
finding even though the current PT-06 verdict itself remains invalid under
RF-03.

## New findings

### RF-06 — medium — ADR/owner packet call a dynamically linked artifact “static”

- **Location:** `docs/adr/ADR-0002-RUST-CORE.md:15,29-31`;
  `docs/OWNER-RATIFICATION-PACKET.md:16`;
  `docs/08-testing/prototype-evidence/PT-05-R2/binary-inspection.txt:1-5`;
  `PT-05-R2/manifest.json:37`.
- **Evidence:** the ADR frames Rust as a static binary and says the candidate
  links only glibc; the owner packet calls it a “glibc-only static binary”.
  The retained `file`/`ldd` evidence says it is dynamically linked and requires
  `libgcc_s`, `libm`, `libc` and the dynamic loader. The R2 manifest correctly
  discloses those runtime dependencies.
- **Impact:** this does not negate the clean Ubuntu-container run, so PT-05's
  distribution result is not reopened solely on this wording. It does give the
  owner a materially inaccurate portability/self-containment description for
  ADR-0002.
- **Required resolution / blocker:** either describe the demonstrated
  dynamically linked glibc artifact accurately or retain evidence for a truly
  static candidate. This blocks accurate ADR-0002 owner ratification; it does
  not authorize implementation.
- **Disposition:** open, medium.

No separate RF was opened for PT-03 retry handling, WAL corruption, PT-05 user
identity, PT-06 journal persistence, hash coverage, PT-04 Podman absence or
historical narrative. The retained evidence supports the stated conclusions,
or the limitation is already honestly represented by RF-03/G-05.

## Decision and remaining blockers

Open findings after R3:

- RF-03 — high;
- RF-04 — high;
- RF-06 — medium.

The requested independence condition also failed because the active reviewer
authored the remediation. PASS requires zero open critical/high findings and a
genuinely independent reviewer. Neither condition is met.

**Decision: FAIL.**

G-09 cannot close from this report. M-00 remains **NOT READY**. G-11 still
blocks ADR-0010/ADR-0011 ratification and the M-01 transaction lease; G-05 still
blocks M-04, external execution and every sandbox-declared release. ADR-0002
also needs RF-06's evidence wording reconciled before accurate ratification.
`APPROVED_TO_IMPLEMENT` remains absent, and this review does not create or imply
implementation authorization.
