# PT-06 R2 canonical bundle

Verdict: **PASS** for the v1 local model. `kill-reclaim.csv` records 20 holder
SIGKILLs and reclaims; the maximum observed recovery was 7,581 µs. SQLite
persisted epoch=20 and transactional counter=20 with `synchronous=FULL`.

The retained `journal.jsonl` was physically appended and fsynced. Its recovery
reader re-derived exactly one `Preserve`, one `Quarantine`, one `Escalate`, and
one `Valid`; the ambiguous cross-domain ordering produced `FAIL_CLOSED`.
`ofd-lifecycle.json` shows acquisition after exec+CLOEXEC, blocking while a dup
remained open, and acquisition after the duplicate closed.

No failed canonical attempt was mixed into stderr. Distributed/NFS G-13 remains
out of v1 and was not simulated. Verify with `sha256sum -c SHA256SUMS`.
