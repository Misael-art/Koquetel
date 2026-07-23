#!/usr/bin/env bash
# PT-04 disposable harness (NON-PRODUCTION): rootless containment via bubblewrap +
# user namespaces. Podman (gate primary) is absent -> verdict PARTIAL; Docker is
# rootful and NOT used. No network allowlist possible (no slirp4netns/pasta).
# Synthetic inputs; no secrets. D set by caller.
set -u
D="${D:?}"
echo "## backend_probe"
echo "podman: $(command -v podman || echo ABSENT)"
echo "podman_version: $(podman --version 2>&1 | head -1)"
echo "docker_rootless: $(docker info --format '{{.Rootless}}' 2>&1 | head -1) (rootful -> NOT USED)"
echo "bwrap: $(command -v bwrap)"
echo "unpriv_userns: $(sysctl -n kernel.unprivileged_userns_clone 2>/dev/null)"
echo "slirp4netns: $(command -v slirp4netns || echo ABSENT)  pasta: $(command -v pasta || echo ABSENT)"

SECRET="$D/host-secret.txt"; echo "SYNTHETIC-CANARY-NOT-A-REAL-SECRET" > "$SECRET"
export PT04_ENV_CANARY="SYNTHETIC-ENV-CANARY"
SB="bwrap --unshare-all --die-with-parent --clearenv --ro-bind /usr /usr \
  --symlink usr/lib /lib --symlink usr/lib64 /lib64 --symlink usr/bin /bin \
  --symlink usr/sbin /sbin --proc /proc --dev /dev --tmpfs /work --chdir /work"
pass=0; fail=0
check(){ local desc="$1"; shift
  if $SB /usr/bin/sh -c "$*" >/dev/null 2>&1; then echo "[FAIL] $desc (escaped)"; fail=$((fail+1));
  else echo "[PASS] $desc (denied)"; pass=$((pass+1)); fi; }
echo "## containment_matrix"
check "read non-mounted synthetic secret file" "cat $SECRET"
check "read host SSH keys" "cat ~/.ssh/* ; cat /root/.ssh/*"
check "read /etc/shadow" "cat /etc/shadow"
check "list /home" "ls /home"
check "reach docker engine socket" "test -S /run/docker.sock || test -S /var/run/docker.sock"
check "read leaked env canary" "test -n \"\$PT04_ENV_CANARY\""
check "network egress (full net isolation)" "python3 -c 'import socket;s=socket.socket();s.settimeout(3);s.connect((\"1.1.1.1\",53))'"

echo "## resource_limits"
if $SB /usr/bin/sh -c 'ulimit -v 200000; exec python3 -c "x=bytearray(500*1024*1024);print(len(x))"' >/dev/null 2>&1; then
  echo "[FAIL] 500MB alloc under 200MB cap"; fail=$((fail+1)); else echo "[PASS] memory rlimit enforced"; pass=$((pass+1)); fi

echo "## process_tree_kill"
$SB /usr/bin/sh -c 'while true; do :; done' & BW=$!; sleep 0.3
DESC=$(pgrep -P "$BW" | wc -l); kill -9 "$BW" 2>/dev/null; sleep 0.4
ALIVE=$(pgrep -P "$BW" 2>/dev/null | wc -l)
echo "descendants_before=$DESC after=$ALIVE"
[ "$ALIVE" -eq 0 ] && { echo "[PASS] process tree reaped"; pass=$((pass+1)); } || { echo "[FAIL] orphan survived"; fail=$((fail+1)); }

echo "## performance_overhead"
head -c 20000000 /dev/urandom > "$D/data.bin"
med(){ sort -n | awk '{a[NR]=$1} END{print a[int(NR/2)+1]}'; }
BARE=$(for i in $(seq 1 11); do s=$(date +%s%N); sha256sum "$D/data.bin" >/dev/null; e=$(date +%s%N); echo $(((e-s)/1000000)); done | med)
SBX=$(for i in $(seq 1 11); do s=$(date +%s%N); $SB --ro-bind "$D/data.bin" /work/data.bin /usr/bin/sha256sum /work/data.bin >/dev/null 2>&1; e=$(date +%s%N); echo $(((e-s)/1000000)); done | med)
echo "median_bare_ms=$BARE median_sandboxed_ms=$SBX overhead_ms=$((SBX-BARE)) ceiling_ms=200"
echo "RESULT pass=$pass fail=$fail (containment+limits) verdict=PARTIAL (Podman/allowlist arms not executed)"
rm -f "$SECRET" "$D/data.bin"
