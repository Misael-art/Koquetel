#!/usr/bin/env bash
# PT-06 canonical R2 rerun. Canonical stderr belongs to this invocation only.
set -euo pipefail
HARNESS_DIR="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:?output directory}"
RUN="${2:?temporary run directory}"
mkdir -p "$OUT" "$RUN"
export PYTHONDONTWRITEBYTECODE=1
python3 "$HARNESS_DIR/pt06.py" run "$OUT" "$RUN"
python3 "$HARNESS_DIR/derive.py" "$OUT"
