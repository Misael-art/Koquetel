# Structural inventory and evidence audit

Status: research; local structural pass 1  
Last reviewed: 2026-07-21

## Reproducible scope

All observations use `git show HEAD:<path>` or `git ls-tree -r HEAD`, not mutable
working-tree content.

| Source | Tracked files | Test paths | Dominant implementation |
|---|---:|---:|---|
| PhaseZero `a0468ba` | 536 | 118 | 170 shell, 101 Python, 92 PowerShell, 13 Rust |
| SteamZero `10f3510` | 345 | 80 | 166 Python files across source/tools/tests; 71 Python test modules |

PhaseZero has 24 committed `linux/ai/*.sh` scripts and all 24 enable
`set -euo pipefail`. The committed AI area includes installers/managers for
memory, MCP, clients, routing, usage, desktop apps, secrets, admin escalation and
status plus AI-specific shell/PowerShell tests.

## Structural files read fully

### PhaseZero

- `linux/ai/setup-memory.sh`, 250 lines, SHA-256
  `74c08087507b3fd9a24f8d56b7218150a82c3c038f694ce31db4efa8948f3219`;
- `linux/ai/status.sh`, 330 lines;
- `linux/ai/setup-admin-bridge.sh`, 230 lines.

Targeted structural sections were also inspected in
`setup-agent-compat.sh` (836 lines) and `mcp-manager.sh` (806 lines).

### SteamZero

- `src/steamzero/core/journal.py`, 109 lines, SHA-256
  `e23008ad289bf42a7e91f9014f71d23683a90f8e7a7ba06f68142c4dfab5e1d7`;
- `src/steamzero/core/lock.py`, 171 lines;
- `src/steamzero/core/fs.py`, 444 lines, SHA-256
  `a6664a42e40cc4833103a1c892be50964c85145d1a10db7b86cf3a26bd1cf950`.

Transaction apply/recovery sections in `core/transaction.py` were inspected as
the callers of those primitives.

## Positive evidence

### PhaseZero breadth and integration

- Every committed Linux AI script uses strict shell mode, providing a consistent
  error baseline.
- RTK installation resolves an architecture-specific release, requires the
  published checksum and rejects a mismatch before installation
  (`setup-agent-compat.sh:47-107`).
- Rule projection uses delimited managed blocks and preserves unrelated client
  content across AGENTS, Claude, Gemini, Copilot, Cursor, Windsurf and Cline
  (`setup-agent-compat.sh:219-359`).
- The frugality pack excludes common generated/cache content while explicitly
  retaining lockfiles and refusing automatic wrappers
  (`setup-agent-compat.sh:395-431`).
- MCP definitions are validated, unsafe defaults are excluded from safe sync, and
  doctor emits structured problems across twelve client targets
  (`mcp-manager.sh:612-780`).
- Status is local, structured and composes CLI, IDE, service, memory, MCP, router,
  workspace and compatibility health (`status.sh:140-328`).

### SteamZero transactional rigor

- Filesystem mutation is centralized and mechanically linted; atomic writes use
  same-directory temporary files, file `fsync`, rename and directory `fsync`
  (`core/fs.py:3-14,61-103`).
- Backups compare source and copied hashes before being accepted
  (`core/fs.py:394-408`).
- The journal records undo intent with `fsync` before mutation and completion
  afterward (`core/journal.py:36-78`; `core/transaction.py:748-796`).
- Apply revalidates preconditions and paths, stages, backs up, activates, verifies
  content hashes, runs smoke tests and rolls back on ordinary exceptions
  (`core/transaction.py:585-642,645-675,678-840`).
- Rollback checks backup and restored hashes, refuses to remove changed targets,
  and crash recovery converges non-terminal operations to rollback
  (`core/transaction.py:862-991`).

## Weaknesses and anti-requirements

- **AR-01 No unpinned executable acquisition.** PhaseZero's ai-memory source
  fallback clones/pulls the current branch and builds it without a recorded commit
  or artifact digest (`setup-memory.sh:82-95`). Koquetel must resolve and verify an
  immutable version before planning activation.
- **AR-02 No `latest` runtime image.** The Docker fallback defaults to
  `akitaonrails/ai-memory:latest` (`setup-memory.sh:56-63`). Koquetel requires an
  image digest and provenance record.
- **AR-03 No full-home mount for a capability backend.** The same fallback uses
  host networking and mounts the complete `$HOME` read-write
  (`setup-memory.sh:67-76`). Memory services receive only their data/config roots.
- **AR-04 No best-effort success for required wiring.** Memory initialization,
  service activation and each client hook can fail with warnings while setup
  continues (`setup-memory.sh:146-157,192-213`). The transaction plan must label
  required versus optional steps and verify the selected profile.
- **AR-05 No arbitrary privileged command bridge.** `phasezero-admin` selects an
  escalation backend then executes the caller's unrestricted arguments
  (`setup-admin-bridge.sh:165-172`). Koquetel's helper accepts only typed,
  allowlisted operations with target validation.
- **AR-06 Backups require integrity and transactional grouping.** PhaseZero's
  marked-block and MCP backups use plain `cp`, ignore some copy failures, retain
  independently and then replace targets per client
  (`setup-agent-compat.sh:209-277`; `mcp-manager.sh:28-45,222-255`). Koquetel must
  hash backups and commit a multi-target projection as one recoverable plan.
- **AR-07 Status must validate semantics, not markers alone.** PhaseZero treats a
  case-insensitive `ai-memory` string in several configs as configured
  (`status.sh:80-100`). Koquetel adapter health parses and validates the exact
  canonical projection.
- **AR-08 Lock acquisition must be atomic.** SteamZero reads an existing lock and
  later replaces the target with an atomic file write; two contenders can both
  pass the check before either replace (`core/lock.py:111-140`). Koquetel uses
  kernel locking or exclusive creation plus owner/lease verification.
- **AR-09 Journal recovery must tolerate a torn tail.** SteamZero parses every
  non-empty JSONL line directly (`core/journal.py:90-100`). A killed final append
  can make all recovery unreadable. Koquetel validates sequence/digest and safely
  isolates only an incomplete final record.
- **AR-10 Context inventory cannot silently truncate.** PhaseZero sorts paths then
  keeps the first 500 (`setup-agent-compat.sh:420-426`), which is deterministic but
  not relevance-aware and can omit critical files without signaling. Koquetel
  reports omitted classes and budget insufficiency.

