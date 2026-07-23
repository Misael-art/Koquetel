#!/usr/bin/env python3
# PT-01 overlap detector (NON-PRODUCTION). Reads per-holder acquisition logs
# ("<holder> <acquire_ns> <release_ns>") and reports temporal overlaps. Any
# overlap = a mutual-exclusion violation. Emits machine-readable JSON.
import glob, json, sys
rows = []
for f in glob.glob(sys.argv[1] + "/log.*"):
    for ln in open(f):
        h, a, r = ln.split()
        rows.append((int(a), int(r), h))
rows.sort()
overlaps = 0
max_rel = -1
prev = None
for a, r, h in rows:
    if a < max_rel:
        overlaps += 1
    max_rel = max(max_rel, r)
    prev = (a, r, h)
holders = sorted({h for _, _, h in rows})
print(json.dumps({
    "total_acquisitions": len(rows),
    "distinct_holders": len(holders),
    "temporal_overlaps": overlaps,
    "pass": overlaps == 0,
}))
