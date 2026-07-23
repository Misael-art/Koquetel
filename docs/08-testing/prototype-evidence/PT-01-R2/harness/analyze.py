#!/usr/bin/env python3
"""Derive PT-01 machine reports from the complete CSV acquisition logs."""
import csv
import json
import pathlib
import sys

source = pathlib.Path(sys.argv[1])
report = pathlib.Path(sys.argv[2])
expected_variant = sys.argv[3]
rows = list(csv.DictReader(source.open(encoding="utf-8", newline="")))
rows.sort(key=lambda row: int(row["start_ns"]))
overlaps = 0
last_end = -1
bad_intervals = 0
for row in rows:
    start, end = int(row["start_ns"]), int(row["end_ns"])
    if end <= start:
        bad_intervals += 1
    if start < last_end:
        overlaps += 1
    last_end = max(last_end, end)
holders = {row["holder"] for row in rows}
sequences = {(row["holder"], int(row["sequence"])) for row in rows}
paths = {row["lease_path"] for row in rows}
variants = {row["variant"] for row in rows}
result = {
    "source": source.name,
    "variant": expected_variant,
    "rows": len(rows),
    "distinctHolders": len(holders),
    "distinctHolderSequences": len(sequences),
    "leasePaths": sorted(paths),
    "temporalOverlaps": overlaps,
    "invalidIntervals": bad_intervals,
    "pass": (
        variants == {expected_variant}
        and len(rows) == 10000
        and len(holders) == 100
        and len(sequences) == 10000
        and len(paths) == 1
        and overlaps == 0
        and bad_intervals == 0
    ),
}
report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, sort_keys=True))
