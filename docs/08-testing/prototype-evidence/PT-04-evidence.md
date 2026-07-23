# PT-04 evidence — Rootless sandbox containment (PARTIAL)

> **Verification rerun after RF-03 (2026-07-23).** A fresh ephemeral rerun with a retained, hash-pinned evidence bundle is in `PT-04/` — see [`PT-04/SHA256SUMS`](PT-04/SHA256SUMS), [`PT-04/manifest.json`](PT-04/manifest.json) and [`PT-04/pass-fail.json`](PT-04/pass-fail.json). Rerun verdict: **PARTIAL**. The bundle (raw logs, metrics, per-arm pass/fail, harness source) is the gate-required evidence per [`../PROTOTYPE-EVIDENCE-POLICY.md`](../PROTOTYPE-EVIDENCE-POLICY.md); the summary below is retained.


Gate: [`../PROTOTYPE-GATES.md`](../PROTOTYPE-GATES.md) PT-04
Date executed: 2026-07-22
Branch: `foundation/m00-closure`
Prototype location: `/tmp/koquetel-prototypes/pt04/` (ephemeral)

## Verdict

**PARTIAL PASS.** Every containment property the gate lists was demonstrated with
**0 escapes** and low overhead — but via **rootless bubblewrap + user namespaces**,
not the gate's named **Podman rootless** backend (absent on this host), and the
**network-allowlist** arm could not be tested (no `slirp4netns`/`pasta`). The gate
is therefore **not fully closed**; two arms remain a coverage gap. `G-05` is
substantially de-risked but stays open.

## Why not the named backends

| Backend | State | Decision |
|---|---|---|
| Podman rootless (gate primary) | **absent** (`podman: command not found`) | cannot run; coverage gap |
| Docker (gate fallback) | present but **rootful** (root daemon; `Rootless=` empty), user in `docker` group | **not used** — rootful Docker / docker-group is root-equivalent privilege, which the rootless gate and the no-host-mutation rule forbid |
| bubblewrap + userns | present; `kernel.unprivileged_userns_clone=1`; cgroups v2 | **used as a rootless proxy** — bwrap/userns is the same primitive layer Podman rootless builds on |

## Sandbox definition

```
bwrap --unshare-all --die-with-parent --clearenv \
  --ro-bind /usr /usr --symlink usr/lib /lib --symlink usr/lib64 /lib64 \
  --symlink usr/bin /bin --symlink usr/sbin /sbin \
  --proc /proc --dev /dev --tmpfs /work --chdir /work
```

## Results

### Containment matrix (each attempt must be DENIED)

| Attempt | Result |
|---|---|
| read a non-mounted host secret file | **denied** |
| read host SSH keys (`~/.ssh`, `/root/.ssh`) | **denied** |
| read `/etc/shadow` | **denied** |
| list `/home` | **denied** |
| reach the docker engine socket (`/run/docker.sock`) | **denied** |
| read a leaked secret env var (`--clearenv`) | **denied** |
| network egress to `1.1.1.1:53` (full net isolation) | **denied** |

0 escapes across the matrix.

### Resource limits and lifecycle

| Check | Result |
|---|---|
| address-space cap (`ulimit -v 200MB`, try 500 MB alloc) | alloc **killed/failed** by rlimit |
| process cap (`ulimit -u`, fork storm) | fork storm **blocked** (see caveat) |
| process-tree kill (`--die-with-parent`) | descendants before=1, after=0 → **tree reaped** |

### Performance overhead

| Workload | Bare | Sandboxed | Overhead |
|---|---|---|---|
| sha256 of 20 MB (median of 11) | 44 ms | 56 ms | **12 ms** (ceiling 200 ms) |

## Honest coverage gaps (do NOT count as pass)

- **Podman-backed arm not executed** — Podman is absent. The named production
  backend (rootless Podman, Docker fallback) must be exercised on a host that has
  it before PT-04 is closed and before ADR-0002's "Podman invocation" arm is met.
- **Network allowlist not tested** — only *full* network isolation was possible
  (`--unshare-all`); demonstrating "only allowlisted destinations reached" needs a
  userspace network stack (`slirp4netns`/`pasta`), both absent. The gate's
  allowlist requirement is unproven.
- **Resource limits used rlimits, not cgroup delegation** — `RLIMIT_AS` proves the
  memory cap cleanly; `RLIMIT_NPROC` is per-real-uid host-wide, so the process-cap
  result is indicative, not a clean per-sandbox `pids.max`. CPU/wall-clock caps
  (`RLIMIT_CPU`) were not separately exercised. A production sandbox should use
  cgroup v2 `memory.max`/`pids.max`/`cpu.max` under systemd-user delegation.
- Filesystem tmpfs; single host.

## Disposal

Bubblewrap invocations and the benign data file live only under
`/tmp/koquetel-prototypes/pt04/` and are removed after evidence capture.

## Gaps / ADRs affected

- **G-05** (sandbox performance + containment): mount/credential/socket/full-network
  isolation, memory rlimit and process-tree kill demonstrated rootless with 12 ms
  overhead. **Stays open** pending the Podman-backed run and the network-allowlist
  arm on a suitable host.
- **ADR-0002 (Rust core) — corrected by RF-01:** Podman invocation is **not** an
  ADR-0002 gate arm; it is a PT-04/M-04 sandbox capability and blocks **G-05**, not
  the Rust language decision. PT-04's PARTIAL verdict blocks **M-04 and any
  sandbox-declared release**, not ADR-0002 and not the start of M-01/M-02.
  ~~Original: ADR-0002's "Podman invocation" arm remains unmet, so ADR-0002 stays
  proposed even though PT-05 cleared its distribution/SQLite/socket/recovery
  arms.~~
