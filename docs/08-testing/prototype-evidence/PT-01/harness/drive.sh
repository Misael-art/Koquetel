#!/usr/bin/env bash
# PT-01 arms. Synthetic; no secrets. BIN, ANALYZE, D set by caller.
set -u
BIN="${BIN:?}"; ANALYZE="${ANALYZE:?}"; D="${D:?}"
echo "## mutual_exclusion (100 holders x 100 = 10000 contended acquisitions)"
L="$D/lease"; : > "$L"; rm -f "$D"/log.*
for h in $(seq 1 100); do "$BIN" contend "$L" "$h" 100 "$D/log.$h" & done; wait
echo -n "overlap_detector="; python3 "$ANALYZE" "$D"
echo "## fork_ofd_lifecycle (100 iterations)"
L2="$D/fork.lease"; : > "$L2"; "$BIN" fork-arm "$L2" 100
echo "DONE"
