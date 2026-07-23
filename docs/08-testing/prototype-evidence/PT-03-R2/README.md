# PT-03 R2 canonical bundle

Verdict: **PASS** against the retained real-backend arms. The harness imports
`ai-memory-store` from the read-only checkout at
`2a85950ce8fa5c309fdc3adc481e98a02d824a9f`; it does not create a substitute
SQLite schema.

The two 10,000-operation ledgers were re-read through public Store APIs with
zero missing or wrong-digest bodies. Cross-process clients required 2,769
bounded retries (maximum 49/100), which is an explicit M-03 adapter requirement.
The killed batch resumed to 1,000/1,000. Independent main-DB and live-WAL faults
both failed closed. The 128-record SCH-10 envelope round-tripped with digest
`4477319edb1a30c07d87b6110faf5329a30f68dd9398223d4642066bde517466`.
Purge deleted 128 rows and left zero queryable residue; shared backend files and
the retained export are listed in `residue-inventory.json`.

`attempts/` keeps non-canonical failures separate: the first cross-process run
exposed unhandled `SQLITE_BUSY` before bounded adapter retries were added; the
first WAL fault touched only one non-targeted byte and was rejected as
insufficient. Neither attempt contributes to `pass-fail.json`.

Verify every retained file with `sha256sum -c SHA256SUMS`.
