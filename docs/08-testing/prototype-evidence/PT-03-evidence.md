# PT-03 evidence — ai-memory concurrency, corruption, export and removal

Gate: [`../PROTOTYPE-GATES.md`](../PROTOTYPE-GATES.md) PT-03
Date executed: 2026-07-22
Branch: `foundation/m00-closure`
Prototype location: ai-memory clone (read-only) + harness in `/tmp/koquetel-prototypes/pt03/` (ephemeral)

## Verdict

**PASS** across all four arms. ai-memory's real store code passes its full test
suite at the pin (migration safety, purge/removal + audit, schema-ahead
fail-closed); a cross-process fault harness under ai-memory's exact pragmas shows
0 lost/torn records, corruption detected fail-closed, and export round-trip
digest match. Two adoption corrections from EA-01 are confirmed and must be
enforced by the Koquetel adapter (below).

## Environment

| Item | Value |
|---|---|
| ai-memory pin | `2a85950ce8fa5c309fdc3adc481e98a02d824a9f` (re-cloned read-only; source unmodified, 0 tracked changes) |
| Store pragmas (EA-01 `lib.rs:91-93`) | `journal_mode=WAL`, `synchronous=NORMAL`, `busy_timeout=5000` |
| Kernel / fs | Linux 6.18.38 / tmpfs |
| Rust | rustc 1.97.0 (ai-memory build) |
| Harness | Python 3.14 stdlib `sqlite3` (SQLite 3.53) under the pragmas above |

## Arm 1 — real ai-memory code (its own tests at the pin)

```
cargo test -p ai-memory-store   ->   173 + 5 + 2 = 180 passed; 0 failed
```

Relevant passing tests (real code, not a replica):

- `data_ahead_of_binary_reports_schema_ahead_not_raw_refinery`,
  `schema_ahead_message_is_actionable` — **corruption/incompatibility fail-closed**:
  a store newer than the binary is refused with an actionable error (NFR-08).
- `v28_to_v29_preserves_existing_rows`, `session_agent_kind_migrations_preserve_observations`,
  `pages_fts_path_migration_preserves_accent_folding` — **migration safety**.
- `audit_log_records_purge_project_with_author`, `rename_project_after_purge_returns_not_found`
  — **removal**: purge is audited and leaves the project not-found (0 queryable residue).
- `v18_migration_refuses_existing_split_brain_rows` — fail-closed on inconsistent state.

## Arm 2 — cross-process concurrency (the EA-01 AC-CONC concern)

8 separate OS processes, 1,250 transactional inserts each = **10,000 contended**
operations on one DB under ai-memory's pragmas:

```
count=10000  torn_or_wrong_digest_rows=0   (every writer: retries=0)
```

0 lost records, 0 wrong/torn digests, 0 unhandled `SQLITE_BUSY` — `busy_timeout`
absorbed all contention. **Crucial nuance:** the harness uses `BEGIN IMMEDIATE`,
which is exactly the correction EA-01 recommended (AC-CONC) — ai-memory's own
store uses **DEFERRED** transactions, whose read-then-write upgrade can deadlock
across processes. So this arm proves the *fix* works cross-process; it does **not**
retroactively clear ai-memory's shipped DEFERRED behavior. The Koquetel adapter
MUST enforce IMMEDIATE (or a single serialized writer) — recorded below.

## Arm 3 — corruption fail-closed

Flip 8 bytes mid-file after a WAL checkpoint, then reopen:

```
integrity_check='*** in database main *** Tree 2 page 4 cell 162: Extends off ...'
CORRUPTION_DETECTED
```

Corruption is surfaced by `PRAGMA integrity_check`, not returned as a silent wrong
answer. Recovery path is "restore from last export" (arm 4 shows export fidelity).

## Arm 4 — export → import round-trip

Canonical export of the `project` scope, import into an empty store, digest-compare:

```
src rows=10000 digest=92307125aa3530b5   dst rows=10000 digest=92307125aa3530b5
EXPORT_ROUNDTRIP_MATCH
```

Data round-trips with an identical content digest. **Nuance (AC-EXP):** ai-memory
has **no native governed-envelope export** (EA-01: its `export_transcript` is
session-scoped). This arm validates data-level round-trippability; the SCH-10
`MemoryExport` envelope is Koquetel-owned, not ai-memory's.

## Honest coverage notes

- Arms 2–4 exercise **SQLite under ai-memory's exact pragmas**, not ai-memory's
  in-process actor (which is single-writer by construction). Arm 1 exercises
  ai-memory's **real code** via its test suite.
- **Durability (AC-DUR):** `synchronous=NORMAL` can lose the last committed
  transaction on OS/power loss (not simulated here). Acceptable for memory
  *content*; Koquetel's own transaction/ownership store uses `synchronous=FULL`
  (see PT-05). Not a defect in ai-memory as a content backend.
- Filesystem tmpfs (local-kernel); no networked filesystem (out of v1, Q-08).

## Disposal

The ai-memory clone (read-only) and the Python harness live only under the session
scratch area and are deleted after this evidence is committed. Only this file is
retained.

## Adapter requirements this prototype pins (for M-03)

1. The ai-memory adapter MUST issue writes as `BEGIN IMMEDIATE` (or funnel through
   one serialized writer) — do not rely on ai-memory's DEFERRED default under
   multi-process load.
2. Koquetel owns the SCH-10 envelope export/import; ai-memory's transcript export
   is not the governance export.
3. Governance/ownership metadata is not stored at `synchronous=NORMAL`; it lives
   in Koquetel's own `FULL` store.

## Gaps / ADRs affected

- **G-04** (ai-memory durability/concurrency/export/corruption): concurrency,
  corruption-detection, export round-trip and removal are now demonstrated; the
  power-loss durability of `NORMAL` is a documented acceptance, not a tested arm.
  G-04 is **substantially closed** with the three adapter requirements above.
- **ADR-0004 (memory envelope over replaceable backends):** its "prototype
  required" gate is met; the envelope-over-backends decision is now supportable,
  with ai-memory as initial adapter **conditional** on the three requirements above.
