#!/usr/bin/env python3
"""Negative tests for foundation_lint.py — unittest format.

Each test creates a temporary repo, runs foundation_lint as a subprocess for
full isolation, and asserts the expected exit code.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LINT = REPO / "tools/foundation_lint.py"
SUITE = REPO / "tools/schema_suite"
VENV_PY = Path(__import__("os").environ.get("SCHEMA_VENV_PY", str(SUITE / ".venv/bin/python")))

SCHEMA_FILES = [   # must mirror tools/foundation_lint.py SCHEMA_FILES (order matters)
    "plan-confirmation.schema.json", "transaction.schema.json",
    "profile-adapter.schema.json", "memory.schema.json",
    "tool-policy.schema.json", "delegation-task.schema.json",
    "event-support.schema.json", "model-routing.schema.json",
    "session.schema.json",
    "tolerant-read/event.tolerant.schema.json",
]


def _write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _schema_stub() -> str:
    return json.dumps({
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {"schemaVersion": {"const": 1}},
        "additionalProperties": False,
    })


def _setup(root: Path):
    _write(root / "docs/00-vision/VISION.md",
           "# Vision\n\n| ID | Principle |\n|---|---|\n| **P-01** | first |\n")
    _write(root / "docs/01-product/PRD.md",
           "# PRD\n\n- **FR-01** first\n- **FR-02** second\n"
           "- **NFR-01** first\n- **NFR-02** second\n")
    _write(root / "docs/01-product/ACCEPTANCE-CRITERIA.md",
           "# Acceptance\n\n- **AC-01** first\n- **AC-02** second\n")
    _write(root / "docs/04-security/THREAT-MODEL.md",
           "# Threat model\n\n- **SR-01** first\n- **SR-02** second\n")
    _write(root / "docs/03-architecture/FAILURE-MODES.md",
           "# Failure modes\n\n- **FM-01** first\n- **FM-02** second\n")
    _write(root / "docs/08-testing/TEST-STRATEGY.md",
           "# Test strategy\n\n- **FI-01** first\n- **RT-01** first\n")
    _write(root / "docs/08-testing/INDEPENDENCE-TESTS.md",
           "# Independence\n\n- **IT-01** first\n")
    _write(root / "docs/08-testing/PROTOTYPE-GATES.md",
           "# Gates\n\n- **PT-01** first\n")
    _write(root / "docs/05-data/schemas/SCHEMA-REGISTRY.md",
           "# Schema registry\n\n- **SC-01** first\n- **SC-02** first\n"
           "- **SCH-01** first\n- **SCH-02** first\n")
    _write(root / "docs/06-api/CONTRACTS.md",
           "# Contracts\n\n- **E-0001** first\n")
    _write(root / "docs/12-roadmap/RISKS.md",
           "# Risks\n\n- **R-01** first\n- **R-02** second\n")
    _write(root / "docs/12-roadmap/ROADMAP.md",
           "# Roadmap\n\n- **M-01** first\n")
    _write(root / "docs/KNOWN-GAPS.md",
           "# Known gaps\n\n- **G-01** first\n- **G-02** second\n")
    _write(root / "docs/OPEN-QUESTIONS.md",
           "# Open questions\n\n| ID | Question |\n|---|---|\n| Q-01 | test |\n")
    _write(root / "docs/ASSUMPTIONS.md",
           "# Assumptions\n\n- **A-01** first\n")
    _write(root / "docs/02-research/SCRIPT-INVENTORY.md",
           "# Script inventory\n\n- **AR-01** first\n")
    _write(root / "docs/02-research/GAP-ANALYSIS.md",
           "# Gap analysis\n\n- **GA-01** first\n")
    _write(root / "docs/02-research/EXTERNAL-AUDITS.md",
           "# External audits\n\n- **EA-01** first\n")
    _write(root / "docs/TRACEABILITY.md",
           "| FR | Main risk | Failure mode | Acceptance | Verification | Status |\n"
           "|---|---|---|---|---|---|\n"
           "| FR-01 | R-01 | FM-01 | AC-01 | SC-01 | specified |\n"
           "| FR-02 | R-02 | FM-02 | AC-02 | SC-02 | specified |\n"
           "\n"
           "| NFR | Main risk | Failure mode | Acceptance | Verification | Status |\n"
           "|---|---|---|---|---|---|\n"
           "| NFR-01 | R-01 | FM-01 | AC-01 | SC-01 | specified |\n"
           "| NFR-02 | R-02 | FM-02 | AC-02 | SC-02 | specified |\n"
           "\n"
           "| SR | Main risk | Failure mode | Acceptance | Verification | Status |\n"
           "|---|---|---|---|---|---|\n"
           "| SR-01 | R-01 | FM-01 | AC-01 | SC-01 | specified |\n"
           "| SR-02 | R-02 | FM-02 | AC-02 | SC-02 | specified |\n"
           "\n"
           "| AC | Main risk | Failure mode | Verification | Status |\n"
           "|---|---|---|---|---|\n"
           "| AC-01 | R-01 | FM-01 | SC-01 | specified |\n"
           "| AC-02 | R-02 | FM-02 | SC-02 | specified |\n")
    _write(root / "FOUNDATION-READINESS-REPORT.md",
           "# Readiness\n\n"
           "* 1 principles\n"
           "* 2 non-functional\n"
           "* 2 functional\n"
           "* 2 product acceptance criteria\n"
           "* 2 security requirements\n"
           "* 2 failure modes\n")
    _write(root / "docs/adr/ADR-0001.md", "# ADR-0001\n\nAccepted.\n")
    sdir = root / "docs/05-data/schemas"
    for name in SCHEMA_FILES:
        _write(sdir / name, _schema_stub())
    _write(root / "tools/schema_suite/RESULT.json",
           json.dumps({"passed": True, "schemaSha256": hashlib.sha256(
               b"".join((sdir / n).read_bytes() for n in SCHEMA_FILES)
           ).hexdigest(), "failures": []}))


def _lint(root: Path) -> int:
    r = subprocess.run(
        [sys.executable, str(LINT), str(root)],
        capture_output=True, text=True, timeout=15,
    )
    return r.returncode


class TestFoundationLintNegative(unittest.TestCase):
    """Each test builds a temporary repo with a deliberate fault."""

    def test_id_mentioned_without_definition(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _setup(root)
            _write(root / "docs/some-file.md", "Mentions G-99 but not defined")
            rc = _lint(root)
            self.assertNotEqual(rc, 0)

    def test_duplicate_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _setup(root)
            _write(root / "docs/KNOWN-GAPS.md",
                   "# Known gaps\n\n"
                   "| ID | Severity | Gap |\n"
                   "|---|---|---|\n"
                   "| G-01 | high | gap one |\n"
                   "| G-01 | high | gap two |\n")
            rc = _lint(root)
            self.assertNotEqual(rc, 0)

    def test_requirement_on_wrong_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _setup(root)
            _write(root / "docs/TRACEABILITY.md",
                   "| FR | Main risk | Failure mode | Acceptance | Verification | Status |\n"
                   "|---|---|---|---|---|---|\n"
                   "| FR-01 | R-01 | FM-01 | AC-01 | SC-01 | specified |\n"
                   "| FR-02 | R-02 | FM-02 | AC-02 | SC-02 (FR-01) | specified |\n")
            _write(root / "docs/01-product/PRD.md",
                   "# PRD\n\n"
                   "- **FR-01** first\n"
                   "- **FR-02** second\n"
                   "- **FR-03** third (no row)\n")
            rc = _lint(root)
            self.assertNotEqual(rc, 0)

    def test_link_with_nonexistent_anchor(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _setup(root)
            _write(root / "docs/linking.md",
                   "See [anchor](target.md#missing-heading)")
            _write(root / "docs/target.md",
                   "# Real heading\n\nContent.")
            rc = _lint(root)
            self.assertNotEqual(rc, 0)

    def test_invalid_schema_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _setup(root)
            _write(root / "docs/05-data/schemas/examples/broken.json",
                   '{ "unclosed": true ')
            rc = _lint(root)
            self.assertNotEqual(rc, 0)

    def test_clean_repo_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _setup(root)
            rc = _lint(root)
            self.assertEqual(rc, 0)

    def test_stale_schema_suite_rejected(self):
        """Alter a schema after RESULT.json was generated — lint rejects stale."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _setup(root)
            # RESULT.json was written by _setup with a valid digest
            # Now change one schema to make the digest stale
            sdir = root / "docs/05-data/schemas"
            altered = json.loads((sdir / "event-support.schema.json").read_text())
            altered["title"] = "tampered"
            (sdir / "event-support.schema.json").write_text(json.dumps(altered))
            rc = _lint(root)
            self.assertNotEqual(rc, 0)

    def test_missing_required_classification_schema_suite(self):
        """Removing x-classification from a $defs property makes SC-10 fail."""
        with tempfile.TemporaryDirectory() as tmp:
            sdir = Path(tmp) / "schemas"
            shutil.copytree(REPO / "docs/05-data/schemas", sdir)
            target = sdir / "plan-confirmation.schema.json"
            doc = json.loads(target.read_text())
            for dn in list(doc.get("$defs", {}).keys()):
                defs_entry = doc["$defs"][dn]
                props = defs_entry.get("properties", {})
                for k in list(props.keys()):
                    sub = props[k]
                    if isinstance(sub, dict) and "x-classification" in sub:
                        del sub["x-classification"]
                        target.write_text(json.dumps(doc, indent=2))
                        break
                if any("x-classification" not in p for p in props.values()
                       if isinstance(p, dict)):
                    break
            wrapper = Path(tmp) / "check_sc10.py"
            wrapper.write_text(
                'import sys; sys.path.insert(0, "' + str(SUITE) + '")\n'
                "from run_suite import run\n"
                's, f = run(sdir="' + str(sdir) + '")\n'
                "print('SC-10:', s.get('SC-10'))\n"
                "sys.exit(1 if f else 0)\n"
            )
            r = subprocess.run(
                [str(VENV_PY), str(wrapper)],
                capture_output=True, text=True, timeout=30,
            )
            stdout = r.stdout
            self.assertIn("SC-10: False", stdout)
            self.assertNotEqual(r.returncode, 0)
