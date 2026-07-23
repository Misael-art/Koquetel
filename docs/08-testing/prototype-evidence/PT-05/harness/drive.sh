#!/usr/bin/env bash
# PT-05 arms. Synthetic inputs only; no secrets. BIN and D set by the caller.
set -u
BIN="${BIN:?}"; D="${D:?}"; UID_ME=$(id -u)
wait_ready(){ for _ in $(seq 1 300); do grep -q READY "$1" 2>/dev/null && return 0; sleep 0.01; done; return 1; }

echo "## A cold_start"; LOG="$D/a.log"; S=$(date +%s%N)
"$BIN" serve "$D/a.db" "$D/a.sock" "$UID_ME" >"$LOG" 2>&1 & P=$!; wait_ready "$LOG"; E=$(date +%s%N)
echo "cold_start_ms=$(((E-S)/1000000))"; kill "$P" 2>/dev/null; wait "$P" 2>/dev/null

echo "## B migration_idempotency"
"$BIN" serve "$D/b.db" "$D/b.sock" "$UID_ME" >"$D/b1.log" 2>&1 & P=$!; wait_ready "$D/b1.log"
V1=$("$BIN" client "$D/b.sock" version); kill "$P" 2>/dev/null; wait "$P" 2>/dev/null
"$BIN" serve "$D/b.db" "$D/b.sock" "$UID_ME" >"$D/b2.log" 2>&1 & P=$!; wait_ready "$D/b2.log"
V2=$("$BIN" client "$D/b.sock" version); kill "$P" 2>/dev/null; wait "$P" 2>/dev/null
echo "version_run1=$V1 version_run2=$V2"

echo "## C peercred_reject (owner=me+1)"
"$BIN" serve "$D/c.db" "$D/c.sock" "$((UID_ME+1))" >"$D/c.log" 2>&1 & P=$!; wait_ready "$D/c.log"
echo -n "peercred="; "$BIN" client "$D/c.sock" get x; kill "$P" 2>/dev/null; wait "$P" 2>/dev/null

echo "## D1 kill_before_commit"
"$BIN" serve "$D/d.db" "$D/d.sock" "$UID_ME" >"$D/d1.log" 2>&1 & P=$!; wait_ready "$D/d1.log"
"$BIN" client "$D/d.sock" killbefore foo bar >/dev/null; wait "$P" 2>/dev/null
"$BIN" serve "$D/d.db" "$D/d.sock" "$UID_ME" >"$D/d2.log" 2>&1 & P=$!; wait_ready "$D/d2.log"
echo "killbefore_get=$("$BIN" client "$D/d.sock" get foo) killbefore_jstate=$("$BIN" client "$D/d.sock" jstate foo)"
kill "$P" 2>/dev/null; wait "$P" 2>/dev/null

echo "## D2 kill_after_commit"
"$BIN" serve "$D/e.db" "$D/e.sock" "$UID_ME" >"$D/e1.log" 2>&1 & P=$!; wait_ready "$D/e1.log"
"$BIN" client "$D/e.sock" killafter foo bar >/dev/null; wait "$P" 2>/dev/null
"$BIN" serve "$D/e.db" "$D/e.sock" "$UID_ME" >"$D/e2.log" 2>&1 & P=$!; wait_ready "$D/e2.log"
echo "killafter_get=$("$BIN" client "$D/e.sock" get foo) killafter_jstate=$("$BIN" client "$D/e.sock" jstate foo)"
kill "$P" 2>/dev/null; wait "$P" 2>/dev/null

echo "## E socket_mode"
"$BIN" serve "$D/f.db" "$D/f.sock" "$UID_ME" >"$D/f.log" 2>&1 & P=$!; wait_ready "$D/f.log"
echo "socket_mode=$(stat -c '%a' "$D/f.sock")"; kill "$P" 2>/dev/null; wait "$P" 2>/dev/null
echo "DONE"
