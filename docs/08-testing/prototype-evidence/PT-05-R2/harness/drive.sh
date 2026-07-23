#!/usr/bin/env bash
# Build outside the clean runtime image, copy only the binary, execute, remove image.
set -euo pipefail
HARNESS_DIR="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:?output directory}"
RUN="${2:?temporary run directory}"
mkdir -p "$OUT" "$RUN/build/src" "$RUN/context"
cp "$HARNESS_DIR/Cargo.toml" "$RUN/build/Cargo.toml"
if test -f "$HARNESS_DIR/Cargo.lock"; then cp "$HARNESS_DIR/Cargo.lock" "$RUN/build/Cargo.lock"; fi
cp "$HARNESS_DIR/main.rs" "$RUN/build/src/main.rs"
(cd "$RUN/build" && cargo build --release)
BIN="$RUN/build/target/release/pt05_core_r2"
sha256sum "$BIN" > "$OUT/binary-sha256.txt"
file "$BIN" > "$OUT/binary-inspection.txt"
ldd "$BIN" >> "$OUT/binary-inspection.txt"
cp "$BIN" "$RUN/context/pt05_core_r2"
cp "$HARNESS_DIR/Dockerfile" "$RUN/context/Dockerfile"
cp "$HARNESS_DIR/container-run.sh" "$RUN/context/container-run.sh"
IMAGE="koquetel-pt05-r2:$(date -u +%Y%m%d%H%M%S)-$$"
cleanup() { docker image rm "$IMAGE" >/dev/null 2>&1 || true; }
trap cleanup EXIT
docker build --pull -t "$IMAGE" "$RUN/context"
printf '%s\n' "$IMAGE" > "$OUT/container-image.txt"
docker run --rm --network=none --tmpfs /work:rw,nosuid,nodev,size=128m \
  -v "$OUT:/evidence" "$IMAGE"
python3 "$HARNESS_DIR/derive.py" "$OUT"
docker image rm "$IMAGE"
trap - EXIT
