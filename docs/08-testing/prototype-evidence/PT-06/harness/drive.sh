#!/usr/bin/env bash
# PT-06 arms. Synthetic inputs; no secrets. BIN and D set by the caller.
set -u
BIN="${BIN:?}"; D="${D:?}"
echo "## fence_classifier"; "$BIN" fence
echo "## counter_equality (8x1250=10000 contended, transactional)"
K=8; IT=1250; DB="$D/c.db"; L="$D/c.lease"; : > "$L"
"$BIN" counter "$DB" >/dev/null   # pre-init schema once (avoids concurrent CREATE-TABLE race)
for h in $(seq 1 $K); do "$BIN" acquire-inc "$L" "$DB" "$IT" & done; wait
echo "counter_result=$("$BIN" counter "$DB")  expected=n=$((K*IT)) epoch=$((K*IT))"
echo "## recovery (20 kill/reclaim; CSV -> recovery.csv)"
echo "iter,kill_at_ns,grant_at_ns,recovery_ms" > "$D/recovery.csv"
ok=0; max=0; tot=0
for i in $(seq 1 20); do
  L="$D/r$i.lease"; : > "$L"
  "$BIN" kill-holder "$L" > "$D/kh$i.log" 2>&1 & KH=$!
  while ! grep -q KILL_AT "$D/kh$i.log" 2>/dev/null; do :; done
  "$BIN" acquire-wait "$L" > "$D/aw$i.log" 2>&1 & wait $KH 2>/dev/null; wait
  KA=$(awk '/KILL_AT/{print $2}' "$D/kh$i.log"); GA=$(awk '/GRANT_AT/{print $2}' "$D/aw$i.log")
  if [ -n "$KA" ] && [ -n "$GA" ]; then ms=$(((GA-KA)/1000000)); ok=$((ok+1)); tot=$((tot+ms)); [ $ms -gt $max ] && max=$ms
    echo "$i,$KA,$GA,$ms" >> "$D/recovery.csv"; fi
done
echo "recovery_reclaimed=$ok/20 avg_ms=$((ok>0?tot/ok:-1)) max_ms=$max bound_ms=1000"
echo "## ofd_exec_cloexec"; L="$D/exec.lease"; : > "$L"; echo "exec_then_try=$("$BIN" acquire-exec "$L")"
echo "## ofd_dup_survival"; L="$D/dup.lease"; : > "$L"
"$BIN" acquire-dup "$L" > "$D/dup.log" 2>&1 & DP=$!
while ! grep -q DUP_HOLDING "$D/dup.log" 2>/dev/null; do :; done
echo "dup_holding_try=$("$BIN" try "$L")"; wait $DP
echo "dup_released_try=$("$BIN" try "$L")"
echo "DONE"
