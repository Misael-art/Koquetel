# PT-05 R2 canonical bundle

Verdict: **PASS**. The host-built binary ran in a fresh Ubuntu 24.04 container
where `rustc` and `cargo` were absent. The canonical service socket was mode
0600 and the real uid=1002 outsider could not connect. A separate disposable
0666 transport arm allowed uid=1002 to reach the process and receive
`DENIED peer_uid=1002 owner_uid=1001` from `SO_PEERCRED`. Both migration runs
reported version 1; SIGKILL before commit recovered `<absent>/rolled_back`, and
SIGKILL after commit recovered `value/committed`. Cold start was 23 ms against
the 500 ms ceiling.

`attempts/attempt-1-derivation/` retains the first, non-canonical report
serialization failure. The container behavior passed, but multiline stderr made
the metrics parser reject the transcript; the canonical second run encodes that
field on one line. Only root `stdout.log`/`stderr.log` feed the verdict.

No binary or image is retained. Verify with `sha256sum -c SHA256SUMS`.
