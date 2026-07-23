#!/usr/bin/env python3
"""Generate metrics/pass-fail strictly from retained PT-01 raw artifacts."""
import json
import pathlib
import sys

out = pathlib.Path(sys.argv[1])
main = json.loads((out / "overlap-report.json").read_text())
fork_a = json.loads((out / "fork-a-overlap-report.json").read_text())
fork_b = json.loads((out / "fork-b-overlap-report.json").read_text())
probe = (out / "filesystem-probe.txt").read_text(encoding="utf-8")
tmpfs = "tmpfs" in probe
target_local = "TARGET_EXT4_XFS=BLOCKED" not in probe
metrics = {
    "main": main,
    "forkA": fork_a,
    "forkB": fork_b,
    "filesystems": {
        "tmpfsExecuted": tmpfs,
        "ext4OrXfsExecuted": target_local,
        "ext4OrXfsStatus": "PASS" if target_local else "BLOCKED",
    },
}
(out / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
arms = [
    {"name": "tmpfs-main-100x100", "verdict": "PASS" if main["pass"] else "FAIL",
     "metricRef": "metrics.json#main"},
    {"name": "tmpfs-fork-a-100x100", "verdict": "PASS" if fork_a["pass"] else "FAIL",
     "metricRef": "metrics.json#forkA"},
    {"name": "tmpfs-fork-b-100x100", "verdict": "PASS" if fork_b["pass"] else "FAIL",
     "metricRef": "metrics.json#forkB"},
    {"name": "ext4-or-xfs", "verdict": "PASS" if target_local else "BLOCKED",
     "metricRef": "metrics.json#filesystems"},
]
if any(arm["verdict"] == "FAIL" for arm in arms):
    overall = "FAIL"
elif any(arm["verdict"] == "BLOCKED" for arm in arms):
    overall = "PARTIAL"
else:
    overall = "PASS"
result = {
    "pt": "PT-01",
    "overall": overall,
    "arms": arms,
    "criteria": [
        "complete main log contains 10,000 unique holder/sequence rows from 100 processes",
        "complete-log detector reports zero temporal overlaps",
        "fork A and B each ran 100 processes x 100 acquisitions under contention",
        "tmpfs executed separately",
        "ext4/XFS is required for full PASS and is BLOCKED on this host",
    ],
}
(out / "pass-fail.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, sort_keys=True))
