#!/usr/bin/env python3
"""Flip a deterministic byte in a real ai-memory main DB or live WAL."""
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
kind = sys.argv[2]
data = bytearray(path.read_bytes())
offsets = []
if kind == "main":
    offsets = [0]
else:
    if len(data) < 200:
        raise SystemExit("WAL too small to fault")
    page_size = int.from_bytes(data[8:12], "big")
    if page_size == 1:
        page_size = 65536
    frame_size = 24 + page_size
    frame_count = (len(data) - 32) // frame_size
    offsets = [32 + frame * frame_size + 24 for frame in range(frame_count)]
before = [data[offset] for offset in offsets]
for offset in offsets:
    data[offset] ^= 0x5A
path.write_bytes(data)
print(json.dumps({
    "kind": kind,
    "path": path.name,
    "size": len(data),
    "offsets": offsets,
    "before": before,
    "after": [data[offset] for offset in offsets],
}))
