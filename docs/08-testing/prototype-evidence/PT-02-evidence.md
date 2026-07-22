# PT-02 evidence — Journal recovery with a truncated final write

Gate: [`../PROTOTYPE-GATES.md`](../PROTOTYPE-GATES.md) PT-02  
Date executed: 2026-07-21  
Branch: `foundation/m00-closure`  
Prototype location at execution: `/tmp/koquetel-prototypes/pt02-journal/` (ephemeral, deleted after evidence capture)

## Verdict

**PASS** — across the full truncation sweep, 0 cases where a torn tail makes
earlier records unreadable; 100% converge to a terminal state; repeated recovery
changes nothing; mid-file digest break is detected, not silently accepted.

## Environment

| Item | Value |
|---|---|
| Kernel | Linux 6.18.38-1-MANJARO x86_64 |
| Filesystem under test | `tmpfs` (at `/tmp`) |
| Rust | rustc 1.97.0 (2d8144b78 2026-07-07) |
| Hash | SHA-256 (via `sha2` 0.10 crate) |
| Sync | `fsync`/`sync_data` after every record write |

## Journal record format

One JSON object per line, NL-terminated:

```json
{"seq":<u64>,"digest":"<hex sha256>","prev":"<hex\|null>","body":"<text>"}
```

where `digest = sha256(prev || seq_le_bytes || body)`. A torn tail is a final
line that is not NL-terminated, fails to parse as JSON, or has a digest mismatch.
A mid-file break is any line whose `digest` does not match the recomputed value
OR whose `prev` does not match the previous record's `digest`.

## Reproducible commands

```bash
cd /tmp/koquetel-prototypes/pt02-journal
cargo build --release
PT02=target/release/pt02_journal

# test 1: clean journal
$PT02 gen   journal.journal 1000
$PT02 recover journal.journal

# test 2: torn tail
$PT02 gen   journal.journal 1000
$PT02 append-partial journal.journal "torn-record"
$PT02 recover journal.journal

# test 3: mid-file digest break
$PT02 gen   journal.journal 1000
$PT02 flip-byte journal.journal 500
$PT02 recover journal.journal

# test 4: idempotent replay
$PT02 recover-idempotent journal.journal

# full sweep: truncation offsets 0..partial_len-1
python3 sweep.py
```

## Core test results

### Test 1 — clean journal of 1000 records

```json
{"total_lines":1000,"complete":1000,"incomplete":0,"digest_broken":0,
 "chain_ok":true,"last_committed_seq":999}
```

### Test 2 — torn tail (1000 clean + 1 torn)

```
append-partial: prior_len=181720 partial_len=196 truncated to total=181906
file size after torn append: 181906 bytes; lines: 1000
```

```json
{"total_lines":1001,"complete":1000,"incomplete":1,"digest_broken":0,
 "chain_ok":false,"last_committed_seq":999}
```

The torn final record is isolated as `incomplete`; all 1000 earlier records
remain `complete`; the chain stops cleanly at `last_committed_seq=999`.

### Test 3 — mid-file digest break (byte flipped in record 500)

```json
{"total_lines":1000,"complete":500,"incomplete":0,"digest_broken":500,
 "chain_ok":false,"last_committed_seq":499}
```

The flipped byte makes the digest of record 500 not match. The recovery reader
classifies record 500 (and every subsequent chained record, since `prev` links
now dangle) as `digest_broken` — the break is **detected, not silently
accepted**. The last committed record before the break is 499.

### Test 4 — idempotent replay

```json
{"run1":{"total_lines":1000,"complete":500,"incomplete":0,"digest_broken":500,
         "chain_ok":false,"last_committed_seq":499},
 "run2":{"total_lines":1000,"complete":500,"incomplete":0,"digest_broken":500,
         "chain_ok":false,"last_committed_seq":499},
 "idempotent":true}
```

A second recovery pass produces a byte-identical classification.

## Full truncation sweep result

`sweep.py` truncates the appended partial record at every byte offset `k` in
`[0, partial_len-1]` and recovers. The criteria are:

- offset 0 (no partial bytes): complete=1000, chain_ok=true, idempotent=true.
- offsets 1..partial_len-1 (torn partial tail): complete=1000, incomplete=1,
  digest_broken=0, chain_ok=false, idempotent=true.

Sample results from the sweep (`partial_len=196`):

| offset | complete | incomplete | digest_broken | chain_ok | idempotent | ok |
|---|---|---|---|---|---|---|
| 0   | 1000 | 0 | 0 | true  | true | ok |
| 89  | 1000 | 1 | 0 | false | true | ok |
| 178 | 1000 | 1 | 0 | false | true | ok |

**All 196 offsets pass.** `all_offsets_pass: true`, `first_failure: null`.

## Pass/fail against the gate

| Gate criterion | Result |
|---|---|
| across the whole sweep, 0 cases where a torn tail makes earlier records unreadable | **PASS** — complete=1000 at every offset |
| 100% converge to a terminal state | **PASS** — every recovery terminates with a stable classification |
| repeated recovery changes nothing | **PASS** — idempotent=true at every offset |
| any silent acceptance of a broken mid-file record fails | **PASS** — flipped byte was detected as `digest_broken`, not silently accepted |

## Instrumentation corrections (recorded honestly)

Two bugs in the prototype were found and fixed during execution, both in the
fault-injection helpers (not in the recovery logic itself):

1. **First torn-tail run destroyed earlier records.** `cmd_append_partial`
   originally called `set_len(keep)` after the append, which truncates the file
   to `keep` bytes from the start — destroying the 1000 clean records. Fixed by
   snapshotting `prior_len` before the append and setting length to
   `prior_len + keep_within_partial`. This is a fault-injection helper bug; the
   recovery reader was unchanged.
2. **First mid-file-break run did not flip a byte.** `cmd_flip_byte` originally
   replaced the first 'x' in the line with 'X', but JSON records
   (`{"seq":500,...,"body":"record-500"}`) had no 'x'. Fixed by locating the
   `"body":"..."` value and toggling the case of its last character.

These corrections affected the fault injectors, not the recovery reader. The
gate criteria were not weakened.

## Disposal

Prototype source and binary live in `/tmp/koquetel-prototypes/pt02-journal/`
and will be deleted after this evidence is committed. Only this evidence file
and the sweep summary JSON are retained.

## ADRs affected

- Transaction ADR prerequisite "PT-02 torn-journal recovery" — **satisfied**.
  Together with PT-01, this closes two of the three high-risk prototypes
  governance §5 requires for `READY FOR IMPLEMENTATION`.
- ADR-0011's journal-classification concern 5 (committed vs prepared vs
  quarantined) — **partial coverage**: this prototype proves torn-tail
  isolation and mid-file break detection. Full epoch-based quarantine (G-13)
  remains a separate prototype arm under PT-06.
