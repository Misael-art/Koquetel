#!/usr/bin/env python3
"""Foundation documentation linter for Koquetel.

NON-PRODUCT, READ-ONLY foundation tooling. It only reads Markdown and JSON under
the repository and reports inconsistencies; it never mutates files, the host, or
any release artifact, and it is not part of the product runtime (it does not
conflict with ADR-0002). It has no third-party dependencies (Python stdlib only).

Checks (see docs/FOUNDATION-GOVERNANCE.md and the F4 lint requirement):
  1. duplicate ID definitions inside an ID's owning file;
  2. broken references: an ID used somewhere but absent from its owning file,
     and Markdown links to local files that do not exist;
  3. requirements without a test: FR/NFR/SR/AC ids missing a traceability row or
     whose traceability row cites no test family;
  4. accepted owner decisions still listed as open in OPEN-QUESTIONS;
  5. (bonus) every schema example JSON is well-formed and each *.valid.json
     carries a schemaVersion field.

Exit status: 0 when no errors (warnings allowed), 1 when any error is found.
Usage: python3 tools/foundation_lint.py [repo_root]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# ID prefixes, longest-first so "NFR" wins over "FR", "SCH" over "SC", etc.
PREFIXES = [
    "NFR", "SCH", "ADR", "NG", "FR", "AC", "SR", "FM", "FI", "RT",
    "GA", "IT", "AR", "PT", "EA", "SC", "P", "E", "R", "M", "G", "Q", "A",
]
ID_RE = re.compile(r"\b(" + "|".join(PREFIXES) + r")-(\d{2,4})\b")

# Owning file(s) per namespace, relative to repo root. ADR is any file in adr/.
OWNERS = {
    "P": ["docs/00-vision/VISION.md"], "NG": ["docs/00-vision/VISION.md"],
    "FR": ["docs/01-product/PRD.md"], "NFR": ["docs/01-product/PRD.md"],
    "AC": ["docs/01-product/ACCEPTANCE-CRITERIA.md"],
    "SR": ["docs/04-security/THREAT-MODEL.md"],
    "FM": ["docs/03-architecture/FAILURE-MODES.md"],
    "FI": ["docs/08-testing/TEST-STRATEGY.md"], "RT": ["docs/08-testing/TEST-STRATEGY.md"],
    "IT": ["docs/08-testing/INDEPENDENCE-TESTS.md"],
    "SC": ["docs/05-data/schemas/SCHEMA-REGISTRY.md"],
    "SCH": ["docs/05-data/schemas/SCHEMA-REGISTRY.md"],
    "PT": ["docs/08-testing/PROTOTYPE-GATES.md"],
    "E": ["docs/06-api/CONTRACTS.md"],
    "R": ["docs/12-roadmap/RISKS.md"], "M": ["docs/12-roadmap/ROADMAP.md"],
    "G": ["docs/KNOWN-GAPS.md"], "Q": ["docs/OPEN-QUESTIONS.md"],
    "A": ["docs/ASSUMPTIONS.md"],
    "AR": ["docs/02-research/SCRIPT-INVENTORY.md"],
    "GA": ["docs/02-research/GAP-ANALYSIS.md"],
    "EA": ["docs/02-research/EXTERNAL-AUDITS.md"],
}
# A requirement is "tested" if its traceability row cites a test-family id or a
# named verification kind (property/golden/corpus/etc.) — governance §4 accepts
# property, golden-contract, corpus/benchmark and fixture evidence, not only
# failure-injection/rollback ids.
TEST_FAMILIES = (
    "FI-", "RT-", "IT-", "SC-", "SCH-", "PT-",
    "property", "properties", "golden", "corpus", "benchmark", "fixture",
    "round-trip", "canary", "suite",
)
TRACE = "docs/TRACEABILITY.md"
OPEN_Q = "docs/OPEN-QUESTIONS.md"
ACCEPTED_WORDS = ("accepted", "resolved", "decided", "closed")

errors: list[str] = []
warnings: list[str] = []


def iter_files(root: Path, suffixes: tuple[str, ...]):
    for p in sorted(root.rglob("*")):
        if ".git" in p.parts or "/.worktrees/" in str(p):
            continue
        if p.is_file() and p.suffix in suffixes:
            yield p


def rel(root: Path, p: Path) -> str:
    return str(p.relative_to(root))


def is_definition_line(line: str, ident: str) -> bool:
    """A canonical definition site: bold list item or leading table cell.

    Headings are deliberately NOT definitions: a summary/ledger table row plus a
    detail section heading for the same id is normal cross-referencing, not a
    duplicate assignment. A true duplicate is the same id used as a bold list
    definition or a leading table cell more than once.
    """
    s = line.rstrip("\n")
    pat = re.escape(ident)
    return bool(
        re.match(rf"^\s*[-*]\s+\*\*{pat}\b", s)          # - **FR-01 ...**
        or re.match(rf"^\s*\|\s*\*?\*?{pat}\*?\*?\s*\|", s)  # | FR-01 | ...
        or re.match(rf"^\s*[-*]\s+\[.*\b{pat}\b.*\]\(", s)  # - [FR-01](...)
    )


def owners_for(prefix: str, root: Path) -> list[Path]:
    if prefix == "ADR":
        return sorted((root / "docs/adr").glob("*.md"))
    return [root / o for o in OWNERS.get(prefix, [])]


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    md_files = list(iter_files(root, (".md",)))
    ref_files = list(iter_files(root, (".md", ".json")))

    # Gather every ID occurrence (references) across md + json.
    refs: dict[str, set[str]] = {}
    for p in ref_files:
        text = p.read_text(encoding="utf-8", errors="replace")
        for m in ID_RE.finditer(text):
            refs.setdefault(f"{m.group(1)}-{m.group(2)}", set()).add(rel(root, p))

    # Build owning-file content once.
    owner_text: dict[str, str] = {}
    for p in md_files:
        owner_text[rel(root, p)] = p.read_text(encoding="utf-8", errors="replace")

    # --- Check 1 & 2a: duplicate definitions and broken (undefined) references.
    for ident, where in sorted(refs.items()):
        prefix = ident.split("-")[0]
        owner_paths = owners_for(prefix, root)
        if not owner_paths:
            continue  # unknown namespace: skip silently
        def_count = 0
        defined_anywhere = False
        for op in owner_paths:
            key = rel(root, op) if op.exists() else None
            if key is None or key not in owner_text:
                continue
            for line in owner_text[key].splitlines():
                if ident in line:
                    defined_anywhere = True
                    if is_definition_line(line, ident):
                        def_count += 1
        if not defined_anywhere:
            errors.append(
                f"[broken-ref] {ident} is referenced ({', '.join(sorted(where))}) "
                f"but never appears in its owning file(s) "
                f"{[rel(root, o) for o in owner_paths]}"
            )
        elif def_count > 1:
            errors.append(
                f"[duplicate-id] {ident} has {def_count} definition sites in its "
                f"owning file {[rel(root, o) for o in owner_paths if o.exists()]}"
            )

    # --- Check 2b: broken local Markdown links.
    link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for p in md_files:
        for m in link_re.finditer(p.read_text(encoding="utf-8", errors="replace")):
            target = m.group(1).split("#", 1)[0].strip()
            if not target or re.match(r"^[a-z]+://", target) or target.startswith("mailto:"):
                continue
            resolved = (p.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"[broken-link] {rel(root, p)} -> {target} (missing)")

    # --- Check 3: requirements without a test (via TRACEABILITY).
    trace_text = (root / TRACE).read_text(encoding="utf-8", errors="replace")
    trace_lines = trace_text.splitlines()
    for prefix in ("FR", "NFR", "SR", "AC"):
        for op in owners_for(prefix, root):
            key = rel(root, op)
            for line in owner_text.get(key, "").splitlines():
                m = re.match(rf"^\s*[-*]\s+\*\*({prefix}-\d+)\b", line) or re.match(
                    rf"^\s*\|\s*\*?\*?({prefix}-\d+)\b", line
                )
                if not m:
                    continue
                ident = m.group(1)
                rows = [ln for ln in trace_lines if ident in ln]
                if not rows:
                    errors.append(f"[untraced] {ident} has no row in {TRACE}")
                elif not any(fam in ln for ln in rows for fam in TEST_FAMILIES):
                    errors.append(
                        f"[no-test] {ident} appears in {TRACE} but cites no test "
                        f"family ({', '.join(TEST_FAMILIES)})"
                    )

    # --- Check 4: accepted decisions still listed as open.
    open_ids = set()
    for line in owner_text.get(OPEN_Q, "").splitlines():
        m = re.match(r"^\s*\|\s*(Q-\d+)\b", line)
        if m:
            open_ids.add(m.group(1))
    for p in md_files:
        key = rel(root, p)
        if key == OPEN_Q:
            continue
        for line in owner_text.get(key, "").splitlines():
            low = line.lower()
            # Skip range/futurity/negation phrasing ("until Q-05 is accepted",
            # "Q-01 through Q-05 resolved", "not owner-decided") — those are not
            # assertions that a specific decision is already accepted.
            if any(cue in low for cue in ("until", "through", "not ", "pending", "require", "when ", "undecided")):
                continue
            for qid in open_ids:
                if qid in line and any(w in low for w in ACCEPTED_WORDS):
                    warnings.append(
                        f"[maybe-accepted] {qid} is open in {OPEN_Q} but {key} says: "
                        f"\"{line.strip()[:90]}\""
                    )

    # --- Check 5: schema example JSON well-formedness.
    ex_dir = root / "docs/05-data/schemas/examples"
    for p in sorted(ex_dir.glob("*.json")) if ex_dir.exists() else []:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"[bad-json] {rel(root, p)}: {exc}")
            continue
        if p.name.endswith(".valid.json") and "schemaVersion" not in data:
            errors.append(f"[schema] {rel(root, p)} valid example lacks schemaVersion")

    for w in warnings:
        print("WARN  " + w)
    for e in errors:
        print("ERROR " + e)
    print(f"\nfoundation-lint: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
