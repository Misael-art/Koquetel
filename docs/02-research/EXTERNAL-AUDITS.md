# External implementation audits

Status: research; EA-01 (ai-memory) complete, others pending
Last reviewed: 2026-07-21

This file holds implementation-level audits of external projects that could
become a Koquetel dependency or adapter base. It complements the local-source
audit in [`SCRIPT-INVENTORY.md`](SCRIPT-INVENTORY.md) and obeys the same evidence
rules: pinned commit, verified license, structural files read fully with digests,
and every claim carrying exact file and line references.

No audit below authorizes reuse; reuse still passes [`../11-legal/REUSE-POLICY.md`](../11-legal/REUSE-POLICY.md)
and Q-02. A README claim is never implementation evidence (governance MP-2).

## Audit template (each `EA-xx` must fill all fields)

1. **Pin & license** — commit/tag, license file verified at that commit.
2. **Inventory** — tracked file count, dominant language, test count, module map.
3. **Files read fully** — path, line count, SHA-256.
4. **Positive patterns** — behavior with `file:line`.
5. **Weaknesses / adoption constraints** — behavior with `file:line`, mapped to a
   Koquetel requirement or a prototype gate.
6. **Reuse recommendation** — adapter / concept / reject, and the blocking gaps.

## Audit status

| Project | Pin | License (verified) | Audit |
|---|---|---|---|
| ai-memory | `2a85950` | MIT (root `LICENSE`, © 2026 Fabio Akita) | **EA-01 complete (this pass)** |
| RTK | `66e09cb` | Apache-2.0 | pending — clone at pin, read `src` entry + one filter path |
| MCP | `88191b9` | MIT/Apache-2.0 (transition), docs CC-BY-4.0 | pending — spec conformance read, no code copy |
| LiteLLM | `212a921` | MIT outside `enterprise/` | pending — read router/budget core, exclude `enterprise/` |
| OpenHands | `a1547a9` | MIT outside `enterprise/` | pending — read runtime/sandbox core, exclude `enterprise/` |
| Letta | `b76da90` | Apache-2.0 | pending — read memory-tier model |
| Mem0 | `dd5f7e3` | Apache-2.0 | pending — read vector/graph store |

The pending rows carry no score. They stay unscored until an equivalent EA audit
attaches implementation evidence (`G-03`).

---

## EA-01 — ai-memory `2a85950`

### Pin & license

- Cloned read-only at `2a85950ce8fa5c309fdc3adc481e98a02d824a9f` (equal to the
  observation pin in [`SOURCE-REPOSITORIES.md`](SOURCE-REPOSITORIES.md); the remote
  HEAD matched this commit at audit time).
- Root `LICENSE` is MIT, `Copyright (c) 2026 Fabio Akita` — consistent with
  [`../11-legal/LICENSE-MATRIX.md`](../11-legal/LICENSE-MATRIX.md).

### Inventory

- 480 tracked files. Dominant language **Rust** (180 `.rs`), plus 74 shell, 68
  PowerShell, 57 markdown, 32 `.sql`, 17 `.toml`. A Cargo workspace of crates:
  `ai-memory-cli`, `-consolidate`, `-hooks`, `-llm`, `-mcp`, `-store`, `-web`,
  `-wiki`, `-core`. 32 test paths (Rust integration tests plus shell e2e).
- Persistence is SQLite via `rusqlite`, schema migrations via `refinery`
  (`crates/ai-memory-store/migrations/V01..V20+`). This is directly relevant: the
  memory-backend candidate is itself Rust + SQLite, aligning with the direction of
  proposed [`../adr/ADR-0002-RUST-CORE.md`](../adr/ADR-0002-RUST-CORE.md).

### Files read fully

| Path | Lines | SHA-256 |
|---|---:|---|
| `crates/ai-memory-store/src/migrations.rs` | 144 | `2be282a3138526f279c47ddd7d0adb8aa1cf53a0718eab84092fbbc44db13488` |
| `crates/ai-memory-store/src/maintenance.rs` | 48 | `f1db36884c6dfa72d7ce49f8026c5ae20b007e7f27eda248cf402cc509c97a24` |

Structural sections were also read in `ai-memory-store/src/lib.rs` (store open /
pragmas / migration wiring, lines 60–116) and `writer.rs` (purge/delete surface,
lines 660–700), and the intent header of the concurrency stress test
`crates/ai-memory-mcp/tests/autoscope_stress.rs:1-40`.

### Positive patterns

- **WAL with tuned durability pragmas.** `lib.rs:91-93` sets `journal_mode=WAL`,
  `synchronous=NORMAL`, `busy_timeout=5000` on open — concurrent readers with a
  single writer, and a bounded wait under cross-process contention.
- **Single-writer actor + read-only pool.** The `Store` exposes a `WriterHandle`
  and a `ReaderPool` (`lib.rs:69-73`); `open()` spawns one writer thread that owns
  the write connection (`lib.rs:102-103`), and mutations are messages
  (`writer.rs` `WriteCmd::PurgeProject` over a `oneshot` channel, `writer.rs:667-685`).
  All in-process writes are serialized by construction, so write–write races cannot
  occur within a process.
- **Foreign-key discipline across migrations.** FKs are disabled only inside the
  migration window and re-enabled for runtime (`lib.rs:98-100`).
- **Fail-closed on a store newer than the binary.** When an applied migration is
  above the embedded ceiling, `migrations.rs:31-42` remaps refinery's misleading
  "missing from the filesystem" into an actionable `DataSchemaAhead` error naming
  the offending version; two tests pin the behavior and message
  (`migrations.rs:61-113`). This is exactly the fail-closed-on-unknown-schema
  posture Koquetel requires (NFR-08), demonstrated in a candidate backend.
- **Migration data-preservation is tested.** `migrations.rs:115-143` proves rows
  survive a version step and the new table appears.
- **Deletion transparency.** `purge_project` returns a `PurgeSummary` with
  pre-delete row counts and the on-disk page paths the caller must still remove
  (`writer.rs:660-685`); `delete_workspace` refuses a non-empty workspace unless
  `force` (`writer.rs:690-700`). Purge is audited (`ops.rs` test
  `audit_log_records_purge_project_with_author`, `ops.rs:3950`).
- **Completion recorded only after success.** Maintenance cadence writes
  `last_success_at` after the work, via upsert (`maintenance.rs:40-48`).

### Weaknesses / adoption constraints for Koquetel

- **AC-DUR — memory-content durability tier is not governance-grade.**
  `synchronous=NORMAL` in WAL (`lib.rs:92`) is durable across an application crash
  but can lose the last committed transaction(s) on OS/power loss (SQLite
  semantics). Acceptable for memory *content*, but Koquetel governance/ownership
  and transaction-journal records must not inherit this tier — they need
  `synchronous=FULL`/explicit fsync, which Koquetel already specifies
  (`TRANSACTION-MODEL.md` step 6). Reinforces ADR-0004: Koquetel owns the envelope
  in its own store; ai-memory holds content only.
- **AC-CONC — cross-process write concurrency is unproven for Koquetel's load.**
  The single-writer actor serializes writes *in one process*; across multiple
  ai-memory instances on one DB, isolation relies on `busy_timeout=5000`
  (`lib.rs:93`) with rusqlite's default `DEFERRED` transactions (no `BEGIN
  IMMEDIATE` exists in the workspace source). Under concurrent read-then-write from
  two instances a snapshot conflict can surface as `SQLITE_BUSY` that the busy
  timeout does not resolve. Koquetel's multi-agent memory writes must be validated,
  not assumed — this is the concurrency arm of prototype **PT-03** and gap
  **G-04**.
- **AC-EXP — export is transcript-scoped, not a governed envelope export.** The
  CLI `export_transcript` path (`crates/ai-memory-cli/src/commands/run.rs:782-810`)
  exports session transcripts, not a portable, provenance-bearing memory archive.
  Koquetel must own backend-independent export (FR-05, GA-09, `SCH-10 MemoryExport`).

### Reuse recommendation

- **Adapter, not base or dependency of the core.** ai-memory is a strong first
  memory *content/search* backend behind Koquetel's `MemoryEnvelope` (SCH-09) and
  `AdapterDescriptor` (SCH-08). Its schema-ahead guard and single-writer actor are
  patterns Koquetel independently mirrors; no code is copied pending Q-02.
- **Blocking before acceptance:** PT-03 must prove concurrency, corruption
  recovery, export and removal residue with fault injection (G-04). License MIT is
  compatible with likely Koquetel licenses but per-file attribution is still
  required if any code (not just concepts) is ever reused.
- Independence unaffected: ai-memory is an *optional* adapter; its absence must
  degrade to memory-off mode (FM-05), never break lifecycle (P-13, NFR-13).
