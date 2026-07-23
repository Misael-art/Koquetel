#!/usr/bin/env bash
# PT-03 canonical R2 rerun against an external read-only ai-memory checkout.
set -euo pipefail
HARNESS_DIR="$(cd "$(dirname "$0")" && pwd)"
AI_MEMORY="${1:?ai-memory checkout}"
OUT="${2:?output directory}"
RUN="${3:?temporary run directory}"
SCHEMA_VENV_PY="${4:?foundation schema venv python}"
SCHEMA_FILE="${5:?memory schema path}"
mkdir -p "$OUT" "$RUN/build/src" "$RUN/state"
git -C "$AI_MEMORY" rev-parse HEAD > "$OUT/source-git-before.txt"
git -C "$AI_MEMORY" status --short >> "$OUT/source-git-before.txt"
sed "s|@AI_MEMORY@|$AI_MEMORY|g" "$HARNESS_DIR/Cargo.toml" > "$RUN/build/Cargo.toml"
cp "$HARNESS_DIR/main.rs" "$RUN/build/src/main.rs"
(cd "$RUN/build" && cargo build --release)
BIN="$RUN/build/target/release/pt03_real_ai_memory"
sha256sum "$BIN" > "$OUT/harness-binary-sha256.txt"

"$BIN" in-process "$RUN/state/in-process" "$OUT/in-process-ledger.jsonl"
"$BIN" verify "$RUN/state/in-process" in-process \
  "$OUT/in-process-ledger.jsonl" "$OUT/in-process-report.json"

"$BIN" seed "$RUN/state/cross" cross bootstrap 0
PIDS=()
START_FILE="$RUN/cross.start"
for process in $(seq 0 7); do
  PT03_READY_FILE="$RUN/cross.ready.$process" PT03_START_FILE="$START_FILE" \
  "$BIN" worker "$RUN/state/cross" cross "$process" 1250 \
    "$OUT/cross-process-$process.jsonl" > "$OUT/cross-process-$process.stdout" \
    2> "$OUT/cross-process-$process.stderr" &
  PIDS+=("$!")
done
for process in $(seq 0 7); do
  for _ in $(seq 1 2000); do
    test -f "$RUN/cross.ready.$process" && break
    sleep 0.005
  done
  test -f "$RUN/cross.ready.$process"
done
: > "$START_FILE"
for pid in "${PIDS[@]}"; do wait "$pid"; done
cat "$OUT"/cross-process-?.jsonl > "$OUT/cross-process-ledger.jsonl"
"$BIN" verify "$RUN/state/cross" cross \
  "$OUT/cross-process-ledger.jsonl" "$OUT/cross-process-report.json"

MARKER="$RUN/kill.marker"
"$BIN" worker "$RUN/state/kill" kill-batch 9 1000 \
  "$OUT/kill-process-ledger.jsonl" "$MARKER" > "$OUT/kill-process.stdout" \
  2> "$OUT/kill-process.stderr" &
KILL_PID=$!
for _ in $(seq 1 1000); do test -f "$MARKER" && break; sleep 0.005; done
test -f "$MARKER"
kill -9 "$KILL_PID"
wait "$KILL_PID" 2>/dev/null || true
LEDGER_BEFORE=$(wc -l < "$OUT/kill-process-ledger.jsonl")
"$BIN" worker "$RUN/state/kill" kill-batch 9 1000 \
  "$OUT/kill-resume-ledger.jsonl"
"$BIN" verify "$RUN/state/kill" kill-batch \
  "$OUT/kill-resume-ledger.jsonl" "$OUT/kill-verify.json"
python3 - "$LEDGER_BEFORE" "$OUT/kill-verify.json" "$OUT/kill-recovery-report.json" <<'PY'
import json, pathlib, sys
before = int(sys.argv[1])
verified = json.loads(pathlib.Path(sys.argv[2]).read_text())
result = {
    "committedLedgerRowsBeforeKill": before,
    "resumedRows": verified["ledgerRows"],
    "queryablePagesAfterResume": verified["queryablePages"],
    "wrongDigestAfterResume": verified["wrongDigest"],
    "pass": before >= 100 and verified["pass"] and verified["ledgerRows"] == 1000,
}
pathlib.Path(sys.argv[3]).write_text(json.dumps(result, indent=2) + "\n")
PY

"$BIN" seed "$RUN/state/export-source" export-scope export 128
"$BIN" export "$RUN/state/export-source" export-scope \
  "$OUT/export-envelope.json" "$OUT/export-records.jsonl"
"$SCHEMA_VENV_PY" - "$SCHEMA_FILE" "$OUT/export-envelope.json" > "$OUT/export-schema-validation.txt" <<'PY'
import json, sys
from jsonschema import Draft202012Validator
schema = json.load(open(sys.argv[1]))
doc = json.load(open(sys.argv[2]))
wrapper = {"$schema": schema["$schema"], "$defs": schema["$defs"], "$ref": "#/$defs/MemoryExport"}
errors = list(Draft202012Validator(wrapper).iter_errors(doc))
print("SCH-10 VALID" if not errors else "\n".join(str(error) for error in errors))
raise SystemExit(1 if errors else 0)
PY
"$BIN" import "$RUN/state/import-target" imported \
  "$OUT/export-envelope.json" "$OUT/export-records.jsonl"
"$BIN" export "$RUN/state/import-target" imported \
  "$OUT/import-envelope.json" "$OUT/import-records.jsonl"

cp -a "$RUN/state/export-source" "$RUN/state/main-corrupt"
MAIN_DB="$RUN/state/main-corrupt/db/memory.sqlite"
python3 "$HARNESS_DIR/fault.py" "$MAIN_DB" main > "$OUT/main-corruption-fault.json"
set +e
"$BIN" probe "$RUN/state/main-corrupt" > "$OUT/main-corruption-probe.json" \
  2> "$OUT/main-corruption-probe.stderr"
echo "$?" > "$OUT/main-corruption-probe.exit"
set -e

"$BIN" seed "$RUN/state/wal-corrupt" wal-fault bootstrap 1
WAL_MARKER="$RUN/wal.marker"
"$BIN" wal-holder "$RUN/state/wal-corrupt" "$WAL_MARKER" \
  > "$OUT/wal-holder.stdout" 2> "$OUT/wal-holder.stderr" &
WAL_PID=$!
for _ in $(seq 1 1000); do test -f "$WAL_MARKER" && break; sleep 0.005; done
test -f "$WAL_MARKER"
WAL_PATH=$(sed -n 's/^wal=//p' "$WAL_MARKER")
test -s "$WAL_PATH"
python3 "$HARNESS_DIR/fault.py" "$WAL_PATH" wal > "$OUT/wal-corruption-fault.json"
set +e
"$BIN" probe-path "$RUN/state/wal-corrupt" wal-fault wal/00499.md \
  > "$OUT/wal-corruption-probe.json" \
  2> "$OUT/wal-corruption-probe.stderr"
echo "$?" > "$OUT/wal-corruption-probe.exit"
set -e
kill -9 "$WAL_PID"
wait "$WAL_PID" 2>/dev/null || true

mkdir -p "$RUN/state/export-source/exports" "$RUN/state/export-source/backups" \
  "$RUN/state/export-source/temp"
cp "$OUT/export-envelope.json" "$RUN/state/export-source/exports/"
cp "$OUT/export-records.jsonl" "$RUN/state/export-source/exports/"
"$BIN" purge "$RUN/state/export-source" export-scope "$OUT/residue-inventory.json"

git -C "$AI_MEMORY" rev-parse HEAD > "$OUT/source-git-after.txt"
git -C "$AI_MEMORY" status --short >> "$OUT/source-git-after.txt"
diff -u "$OUT/source-git-before.txt" "$OUT/source-git-after.txt" > "$OUT/source-git-diff.txt"
python3 "$HARNESS_DIR/derive.py" "$OUT"
