#!/usr/bin/env python3
"""Derive PT-05 metrics and verdict from the container transcript."""
import json
import pathlib
import sys

out = pathlib.Path(sys.argv[1])
values = {}
for line in (out / "container-results.txt").read_text().splitlines():
    if "=" not in line:
        continue
    key, value = line.split("=", 1)
    values[key] = value
metrics = {
    "rustcPresent": values["rustc_present"] == "yes",
    "cargoPresent": values["cargo_present"] == "yes",
    "ownerUid": int(values["owner_uid"]),
    "outsiderUid": int(values["outsider_uid"]),
    "coldStartMs": int(values["cold_start_ms"]),
    "coldStartCeilingMs": 500,
    "socketMode": values["socket_mode"],
    "ownerClient": values["owner_client"],
    "outsider0600ExitCode": int(values["outsider_0600_rc"]),
    "outsider0600Output": values["outsider_0600_output"],
    "peercredOutsider": values["peercred_outsider"],
    "migrationVersions": [
        int(values["migration_version_1"]), int(values["migration_version_2"])
    ],
    "killBefore": {
        "get": values["kill_before_get"],
        "journalState": values["kill_before_state"],
    },
    "killAfter": {
        "get": values["kill_after_get"],
        "journalState": values["kill_after_state"],
    },
    "binarySha256": (out / "binary-sha256.txt").read_text().split()[0],
    "containerImage": (out / "container-image.txt").read_text().strip(),
}
(out / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
arms = [
    {"name": "clean-container-no-rust", "verdict": "PASS"
     if not metrics["rustcPresent"] and not metrics["cargoPresent"] else "FAIL",
     "metricRef": "metrics.json#rustcPresent"},
    {"name": "migration-idempotency", "verdict": "PASS"
     if metrics["migrationVersions"] == [1, 1] else "FAIL",
     "metricRef": "metrics.json#migrationVersions"},
    {"name": "socket-0600-owner", "verdict": "PASS"
     if metrics["socketMode"] == "600" and metrics["outsider0600ExitCode"] != 0 else "FAIL",
     "metricRef": "metrics.json#socketMode"},
    {"name": "real-second-user-peercred", "verdict": "PASS"
     if metrics["ownerUid"] != metrics["outsiderUid"]
     and metrics["peercredOutsider"] == "DENIED peer_uid=1002 owner_uid=1001" else "FAIL",
     "metricRef": "metrics.json#peercredOutsider"},
    {"name": "kill-before-recovery", "verdict": "PASS"
     if metrics["killBefore"] == {"get": "<absent>", "journalState": "rolled_back"} else "FAIL",
     "metricRef": "metrics.json#killBefore"},
    {"name": "kill-after-recovery", "verdict": "PASS"
     if metrics["killAfter"] == {"get": "value", "journalState": "committed"} else "FAIL",
     "metricRef": "metrics.json#killAfter"},
    {"name": "cold-start", "verdict": "PASS"
     if metrics["coldStartMs"] <= metrics["coldStartCeilingMs"] else "FAIL",
     "metricRef": "metrics.json#coldStartMs"},
]
overall = "PASS" if all(arm["verdict"] == "PASS" for arm in arms) else "FAIL"
result = {
    "pt": "PT-05",
    "overall": overall,
    "arms": arms,
    "criteria": [
        "host-built artifact runs in a fresh Ubuntu container with no rustc/cargo",
        "bundled SQLite migration is idempotent",
        "production socket mode is 0600 and non-owner connection fails",
        "distinct uid=1002 reaches a permissive test socket and is denied by SO_PEERCRED",
        "SIGKILL before/after commit converges to old/completed state",
        "cold start remains below the 500 ms ADR threshold",
    ],
}
(out / "pass-fail.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, sort_keys=True))
