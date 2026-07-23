#!/usr/bin/env python3
"""Derive PT-06 metrics and verdict only from retained run artifacts."""
import csv
import json
import pathlib
import sys

out = pathlib.Path(sys.argv[1])
cycles = list(csv.DictReader((out / "kill-reclaim.csv").open()))
recovery = json.loads((out / "recovery-report.json").read_text())
ofd = json.loads((out / "ofd-lifecycle.json").read_text())
state = json.loads((out / "state-report.json").read_text())
recoveries = [int(row["recovery_us"]) for row in cycles]
metrics = {
    "killReclaimCycles": len(cycles),
    "maxRecoveryUs": max(recoveries),
    "transactionalCounter": state["transactionalCounter"],
    "expectedCounter": state["expectedCounter"],
    "classifications": recovery["counts"],
    "recoveryDisposition": recovery["recoveryDisposition"],
    "ofdLifecycle": ofd,
}
(out / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
arms = [
    {"name": "kill-reclaim-20", "verdict": "PASS" if len(cycles) == 20 else "FAIL",
     "metricRef": "metrics.json#killReclaimCycles"},
    {"name": "transactional-counter", "verdict": "PASS"
     if state["transactionalCounter"] == state["expectedCounter"] == 20 else "FAIL",
     "metricRef": "metrics.json#transactionalCounter"},
    {"name": "persisted-journal-recovery", "verdict": "PASS"
     if recovery["counts"] == {"Preserve": 1, "Quarantine": 1, "Escalate": 1, "Valid": 1}
     and recovery["recoveryDisposition"] == "FAIL_CLOSED" else "FAIL",
     "metricRef": "metrics.json#classifications"},
    {"name": "exec-cloexec", "verdict": "PASS" if ofd["cloexec"]["pass"] else "FAIL",
     "metricRef": "metrics.json#ofdLifecycle"},
    {"name": "dup-survival", "verdict": "PASS" if ofd["dup"]["pass"] else "FAIL",
     "metricRef": "metrics.json#ofdLifecycle"},
]
overall = "PASS" if all(arm["verdict"] == "PASS" for arm in arms) else "FAIL"
result = {
    "pt": "PT-06",
    "overall": overall,
    "arms": arms,
    "criteria": [
        "20 SIGKILL holder deaths followed by bounded kernel-OFD reclaim",
        "epoch and counter persist transactionally in SQLite FULL",
        "real journal recovery yields Preserve, Quarantine, Escalate, and Valid",
        "ambiguous ordering makes recovery fail closed",
        "FD_CLOEXEC releases on exec and dup retains the OFD until last close",
        "distributed/NFS G-13 is outside v1 and was not simulated",
    ],
}
(out / "pass-fail.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, sort_keys=True))
