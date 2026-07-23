#!/usr/bin/env bash
set -euo pipefail
BIN=/usr/local/bin/pt05_core_r2
WORK=/work
RESULT=/evidence/container-results.txt
mkdir -p "$WORK"
chmod 0777 "$WORK"
: > "$RESULT"
record() { printf '%s=%s\n' "$1" "$2" | tee -a "$RESULT"; }
wait_ready() {
  local log="$1"
  for _ in $(seq 1 500); do
    grep -q READY "$log" 2>/dev/null && return 0
    sleep 0.01
  done
  return 1
}
stop_server() {
  local pid="$1"
  kill "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
}

record rustc_present "$(command -v rustc >/dev/null 2>&1 && echo yes || echo no)"
record cargo_present "$(command -v cargo >/dev/null 2>&1 && echo yes || echo no)"
record owner_uid "$(id -u owner)"
record outsider_uid "$(id -u outsider)"
ldd "$BIN" | tee /evidence/container-ldd.txt

START=$(date +%s%N)
runuser -u owner -- "$BIN" serve "$WORK/cold.db" "$WORK/cold.sock" 1001 600 > /evidence/cold-server.log 2>&1 &
SERVER=$!
wait_ready /evidence/cold-server.log
END=$(date +%s%N)
record cold_start_ms "$(((END-START)/1000000))"
record socket_mode "$(stat -c %a "$WORK/cold.sock")"
record owner_client "$(runuser -u owner -- "$BIN" client "$WORK/cold.sock" mutate owner-key owner-value)"
set +e
OUTSIDER_KERNEL=$(runuser -u outsider -- "$BIN" client "$WORK/cold.sock" get owner-key 2>&1)
OUTSIDER_KERNEL_RC=$?
set -e
record outsider_0600_rc "$OUTSIDER_KERNEL_RC"
record outsider_0600_output "$(printf '%s' "$OUTSIDER_KERNEL" | tr '\n' '|')"
stop_server "$SERVER"

# Separate permissive transport arm reaches the server so SO_PEERCRED itself,
# rather than the filesystem mode, rejects the real uid=1002 peer.
runuser -u owner -- "$BIN" serve "$WORK/peer.db" "$WORK/peer.sock" 1001 666 > /evidence/peer-server.log 2>&1 &
SERVER=$!
wait_ready /evidence/peer-server.log
record peercred_outsider "$(runuser -u outsider -- "$BIN" client "$WORK/peer.sock" get owner-key)"
stop_server "$SERVER"

runuser -u owner -- "$BIN" serve "$WORK/migrate.db" "$WORK/migrate.sock" 1001 600 > /evidence/migrate-1.log 2>&1 &
SERVER=$!
wait_ready /evidence/migrate-1.log
record migration_version_1 "$(runuser -u owner -- "$BIN" client "$WORK/migrate.sock" version)"
stop_server "$SERVER"
runuser -u owner -- "$BIN" serve "$WORK/migrate.db" "$WORK/migrate.sock" 1001 600 > /evidence/migrate-2.log 2>&1 &
SERVER=$!
wait_ready /evidence/migrate-2.log
record migration_version_2 "$(runuser -u owner -- "$BIN" client "$WORK/migrate.sock" version)"
stop_server "$SERVER"

runuser -u owner -- "$BIN" serve "$WORK/before.db" "$WORK/before.sock" 1001 600 > /evidence/kill-before-1.log 2>&1 &
SERVER=$!
wait_ready /evidence/kill-before-1.log
set +e
runuser -u owner -- "$BIN" client "$WORK/before.sock" killbefore synthetic value >> /evidence/kill-before-client.log 2>&1
wait "$SERVER"
set -e
runuser -u owner -- "$BIN" serve "$WORK/before.db" "$WORK/before.sock" 1001 600 > /evidence/kill-before-2.log 2>&1 &
SERVER=$!
wait_ready /evidence/kill-before-2.log
record kill_before_get "$(runuser -u owner -- "$BIN" client "$WORK/before.sock" get synthetic)"
record kill_before_state "$(runuser -u owner -- "$BIN" client "$WORK/before.sock" jstate synthetic)"
stop_server "$SERVER"

runuser -u owner -- "$BIN" serve "$WORK/after.db" "$WORK/after.sock" 1001 600 > /evidence/kill-after-1.log 2>&1 &
SERVER=$!
wait_ready /evidence/kill-after-1.log
set +e
runuser -u owner -- "$BIN" client "$WORK/after.sock" killafter synthetic value >> /evidence/kill-after-client.log 2>&1
wait "$SERVER"
set -e
runuser -u owner -- "$BIN" serve "$WORK/after.db" "$WORK/after.sock" 1001 600 > /evidence/kill-after-2.log 2>&1 &
SERVER=$!
wait_ready /evidence/kill-after-2.log
record kill_after_get "$(runuser -u owner -- "$BIN" client "$WORK/after.sock" get synthetic)"
record kill_after_state "$(runuser -u owner -- "$BIN" client "$WORK/after.sock" jstate synthetic)"
stop_server "$SERVER"
echo DONE
