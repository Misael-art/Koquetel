#!/usr/bin/env bash
# PT-01 canonical R2 rerun. Outputs are generated from the run, never hand-authored.
set -euo pipefail
HARNESS_DIR="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:?output directory}"
RUN_ROOT="${2:?tmpfs run root}"
mkdir -p "$OUT" "$RUN_ROOT/work"
BUILD_ROOT="$RUN_ROOT/build"
mkdir -p "$BUILD_ROOT/src"
cp "$HARNESS_DIR/Cargo.toml" "$BUILD_ROOT/Cargo.toml"
cp "$HARNESS_DIR/main.rs" "$BUILD_ROOT/src/main.rs"
(cd "$BUILD_ROOT" && cargo build --release)
BIN="$BUILD_ROOT/target/release/pt01_r2"
sha256sum "$BIN" > "$OUT/binary-sha256.txt"

run_variant() {
  local variant="$1"
  local final="$2"
  local lease="$RUN_ROOT/work/$variant.lease"
  local logs="$RUN_ROOT/work/$variant-logs"
  mkdir -p "$logs"
  : > "$lease"
  local pids=()
  for holder in $(seq -w 1 100); do
    "$BIN" contend "$variant" "$lease" "$holder" 100 "$logs/$holder.csv" &
    pids+=("$!")
  done
  local pid
  for pid in "${pids[@]}"; do wait "$pid"; done
  {
    echo "variant,holder,sequence,start_ns,end_ns,lease_path"
    find "$logs" -type f -name '*.csv' -print0 | sort -z | xargs -0 cat
  } > "$OUT/$final"
}

run_variant main acquisition-log.csv
run_variant fork-a fork-a.csv
run_variant fork-b fork-b.csv
{
  head -n 1 "$OUT/fork-a.csv"
  tail -n +2 "$OUT/fork-a.csv"
  tail -n +2 "$OUT/fork-b.csv"
} > "$OUT/fork-variants.csv"
python3 "$HARNESS_DIR/analyze.py" "$OUT/acquisition-log.csv" "$OUT/overlap-report.json" main
python3 "$HARNESS_DIR/analyze.py" "$OUT/fork-a.csv" "$OUT/fork-a-overlap-report.json" fork-a
python3 "$HARNESS_DIR/analyze.py" "$OUT/fork-b.csv" "$OUT/fork-b-overlap-report.json" fork-b
python3 "$HARNESS_DIR/derive.py" "$OUT"
