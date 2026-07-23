# R2 prototype criterion-to-evidence matrix

Status: author remediation evidence — awaiting R3 validation
Reviewed base: `f086ed7ff5475bf7136e2514b3541388bb82c402`

This matrix maps each normative criterion to executable retained source, raw
output, the derived assertion, and the author verdict. Line numbers refer to the
retained R2 harness source. `pass-fail.json` remains the machine authority.

## PT-01

| Gate criterion | Harness line | Raw artifact | Assertion | Verdict |
|---|---|---|---|---|
| 100 processes, 10,000 complete main acquisitions | `PT-01-R2/harness/drive.sh:16-36` | `acquisition-log.csv` | 10,000 unique holder/sequence rows; 100 holders | PASS on tmpfs |
| holder, sequence, grant/end and lease path captured after lock | `PT-01-R2/harness/main.rs:52-64` | `acquisition-log.csv` | all required columns populated; positive intervals | PASS |
| complete-log overlap detection | `PT-01-R2/harness/analyze.py:9-45` | `overlap-report.json` | 0 temporal overlaps, 0 invalid intervals | PASS |
| fork A: child closes, parent retains OFD under contention | `PT-01-R2/harness/main.rs:66-81` | `fork-variants.csv`, `fork-a-overlap-report.json` | 10,000 rows / 100 holders / 0 overlaps | PASS on tmpfs |
| fork B: parent closes, child retains until signalled | `PT-01-R2/harness/main.rs:83-119` | `fork-variants.csv`, `fork-b-overlap-report.json` | 10,000 rows / 100 holders / 0 overlaps | PASS on tmpfs |
| tmpfs and ext4/XFS separately | `PT-01-R2/harness/derive.py:8-51` | `filesystem-probe.txt`, `metrics.json` | tmpfs detected; no accessible ext4/XFS | **BLOCKED ext4/XFS; overall PARTIAL** |

## PT-03

| Gate criterion | Harness line | Raw artifact | Assertion | Verdict |
|---|---|---|---|---|
| real pinned source, unchanged | `PT-03-R2/harness/drive.sh:11-17,126-128` | `source-git-before.txt`, `source-git-after.txt`, `source-git-diff.txt` | exact `2a85950`; empty diff/status | PASS |
| real in-process clients, 10,000 operations | `PT-03-R2/harness/main.rs:160-189`; driver `:19-21` | `in-process-ledger.jsonl`, `in-process-report.json` | 10,000 queryable; 0 missing/wrong digest | PASS |
| eight real OS processes, 10,000 operations | `PT-03-R2/harness/drive.sh:23-44` | `cross-process-ledger.jsonl`, process stderr, `cross-process-report.json` | 10,000 queryable; 0 missing/wrong; 0 unhandled busy; max retry 49/100 | PASS with adapter retry requirement |
| kill during write batch and resume | `PT-03-R2/harness/drive.sh:46-72` | `kill-process-ledger.jsonl`, `kill-resume-ledger.jsonl`, `kill-recovery-report.json` | killed after 100 logged commits; resumed 1,000; 0 wrong digest | PASS |
| main DB corruption fails closed | `PT-03-R2/harness/drive.sh:92-99` | `main-corruption-fault.json`, `main-corruption-probe.json` | Store open returns “file is not a database” | PASS |
| still-live WAL corruption fails closed | `PT-03-R2/harness/drive.sh:101-118` | `wal-corruption-fault.json`, `wal-corruption-probe.json` | live frame checksums corrupted; target Store open fails closed | PASS |
| SCH-10 export/import/digest | `PT-03-R2/harness/main.rs:224-299`; driver `:74-90` | `export-envelope.json`, `export-records.jsonl`, `import-records.jsonl`, validation log | schema valid; 128 records; all three digests identical | PASS |
| real purge and complete physical inventory | `PT-03-R2/harness/main.rs:301-332`; driver `:120-124` | `residue-inventory.json` | 128 pages deleted; 0 queryable; DB/WAL/SHM/export/temp/backup/index categories reported | PASS |

## PT-05

| Gate criterion | Harness line | Raw artifact | Assertion | Verdict |
|---|---|---|---|---|
| build outside, copy to fresh container, no runtime Rust | `PT-05-R2/harness/drive.sh:7-25`; `container-run.sh:24-25` | `binary-inspection.txt`, `container-results.txt`, build/container transcript | `rustc=no`, `cargo=no`; digest retained; binary not retained | PASS |
| migrations real and idempotent | `PT-05-R2/harness/container-run.sh:54-63` | `migrate-1.log`, `migrate-2.log`, `container-results.txt` | schema version `[1,1]` | PASS |
| production socket 0600 and real second user | `PT-05-R2/harness/container-run.sh:28-45` | `cold-server.log`, `container-results.txt` | owner uid 1001; outsider uid 1002; mode 600; outsider connection denied | PASS |
| application `SO_PEERCRED` denial | `PT-05-R2/harness/main.rs:36-50,72-77`; `container-run.sh:47-52` | `peer-server.log`, `container-results.txt` | `DENIED peer_uid=1002 owner_uid=1001` | PASS |
| kill-before/kill-after convergence | `PT-05-R2/harness/container-run.sh:65-91` | kill client/server logs, `container-results.txt` | `<absent>/rolled_back` and `value/committed` | PASS |
| cold-start threshold | `PT-05-R2/harness/container-run.sh:28-36` | `container-results.txt` | 23 ms ≤ 500 ms | PASS |

## PT-06

| Gate criterion | Harness line | Raw artifact | Assertion | Verdict |
|---|---|---|---|---|
| 20 holder deaths/reclaims and transactional counter | `PT-06-R2/harness/pt06.py:107-177` | `kill-reclaim.csv`, `state-report.json` | 20 cycles; epoch=counter=20; max 7,581 µs | PASS |
| real fsynced journal and digest-chain reader | `PT-06-R2/harness/pt06.py:38-67` | `journal.jsonl` | every retained line parses and matches digest/previous digest | PASS |
| revocation persisted before physical stale write | `PT-06-R2/harness/pt06.py:233-246` | `journal.jsonl`, `recovery-report.json` | seq2 revokes prior epoch; seq3 stale mutation quarantined | PASS |
| committed history preserved, current valid, ambiguity escalated | `PT-06-R2/harness/pt06.py:70-104,233-255` | `recovery-report.json` | Preserve=1, Quarantine=1, Escalate=1, Valid=1; FAIL_CLOSED | PASS |
| exec+CLOEXEC and dup survival | `PT-06-R2/harness/pt06.py:180-220` | `ofd-lifecycle.json` | acquire after exec; block while dup open; acquire after last close | PASS |
| distributed/NFS | no harness arm by design | `manifest.json` | G-13 retained; no simulation | deferred outside v1 |
