# PT-04 evidence bundle (verification rerun after RF-03)

Verdict: **PARTIAL** — rootless bwrap/userns proxy: 7/7 containment denied, memory
rlimit + process-tree kill, 8ms overhead. Podman (primary backend) ABSENT (raw
probe in stdout.log); Docker rootful and NOT used; network allowlist untestable
(no slirp4netns/pasta) — these arms are NOT executed and NOT simulated. G-05 stays
open. Generated 2026-07-23T00:38:48Z. Synthetic; no secrets. NON-PRODUCTION/DISPOSABLE.
