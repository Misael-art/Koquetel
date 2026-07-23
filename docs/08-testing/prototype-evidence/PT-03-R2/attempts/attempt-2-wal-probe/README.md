# Non-canonical attempt 2

The first WAL injector flipped one byte that the targeted public read did not
need, so `SILENT_OPEN` did not establish either corruption handling or silent
data loss. It was rejected. The canonical injector invalidates every live WAL
frame checksum and probes the last written path. This attempt is not part of the
canonical verdict.
