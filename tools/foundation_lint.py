#!/usr/bin/env python3
"""Foundation documentation linter for Koquetel.

NON-PRODUCT, READ-ONLY foundation tooling (stdlib only). It reads Markdown and
JSON under the repo and reports inconsistencies; it never mutates files, the host,
or a release artifact, and is not part of the product runtime.

Checks:
  1. every referenced ID has EXACTLY ONE canonical definition in its owning file
     (0 = broken/undefined reference, >1 = duplicate);
  2. broken references: local Markdown links to missing files AND missing anchors;
  3. every FR/NFR/SR/AC has its OWN traceability row (keyed on the first cell), and
     that row has risk, failure-mode/justification, acceptance, verification, status;
  4. accepted owner decisions still listed as open in OPEN-QUESTIONS;
  5. published readiness counts match the canonical documents (no count rot);
  6. the schema suite result (tools/schema_suite/RESULT.json) is present, passed,
     and matches the current schema digest — well-formed JSON is NOT validation.

Exit 0 when no errors (warnings allowed), 1 otherwise.
Usage: python3 tools/foundation_lint.py [repo_root]
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

PREFIXES = ["NFR", "SCH", "ADR", "NG", "FR", "AC", "SR", "FM", "FI", "RT",
            "GA", "IT", "AR", "PT", "EA", "SC", "P", "E", "R", "M", "G", "Q", "A"]
ID_RE = re.compile(r"\b(" + "|".join(PREFIXES) + r")-(\d{2,4})\b")
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
READINESS = "FOUNDATION-READINESS-REPORT.md"
TRACE = "docs/TRACEABILITY.md"
OPEN_Q = "docs/OPEN-QUESTIONS.md"
ACCEPTED_WORDS = ("accepted", "resolved", "decided", "closed")
NEG_CUES = ("until", "through", "not ", "pending", "require", "when ", "undecided")
SCHEMA_FILES = ["plan-confirmation.schema.json", "transaction.schema.json",
                "profile-adapter.schema.json", "memory.schema.json",
                "tool-policy.schema.json", "delegation-task.schema.json",
                "event-support.schema.json", "model-routing.schema.json",
                "tolerant-read/event.tolerant.schema.json"]
# publication phrase -> ID prefix for readiness count reconciliation
COUNT_CLAIMS = [(r"(\d+)\s+principles", "P"), (r"(\d+)\s+non-goals", "NG"),
                (r"(\d+)\s+non-functional", "NFR"), (r"(\d+)\s+functional", "FR"),
                (r"(\d+)\s+product acceptance criteria", "AC"),
                (r"(\d+)\s+security requirements", "SR"),
                (r"(\d+)\s+(?:initial )?failure modes", "FM")]

errors: list[str] = []
warnings: list[str] = []
EXCLUDE = (".git", ".worktrees", ".venv", "__pycache__", "node_modules")


def iter_files(root: Path, suffixes):
    for p in sorted(root.rglob("*")):
        if any(part in EXCLUDE for part in p.parts):
            continue
        if p.is_file() and p.suffix in suffixes:
            yield p


def rel(root: Path, p: Path) -> str:
    return str(p.relative_to(root))


def owners_for(prefix: str, root: Path):
    if prefix == "ADR":
        return sorted((root / "docs/adr").glob("*.md"))
    return [root / o for o in OWNERS.get(prefix, [])]


def canonical_defs(ident: str, owner_texts) -> int:
    """Definition sites of ident, applying priority heading > bold-list > table-cell."""
    pat = re.escape(ident)
    heads, bolds, cells = [], [], []
    for text in owner_texts:
        for ln in text.splitlines():
            if re.match(rf"^#{{1,6}}\s+\**{pat}\b", ln):
                heads.append(ln)
            elif re.match(rf"^\s*[-*]\s+\*\*{pat}\b", ln):
                bolds.append(ln)
            elif re.match(rf"^\s*\|\s*\*?\*?{pat}\b", ln):
                cells.append(ln)
    return len(heads or bolds or cells)


def slug(heading: str) -> str:
    h = re.sub(r"^#{1,6}\s+", "", heading.strip())
    h = h.replace("`", "").replace("*", "")
    h = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", h)  # link text only
    h = h.lower()
    h = re.sub(r"[^a-z0-9 -]", "", h)
    return h.strip().replace(" ", "-")


def anchors_of(text: str) -> set:
    return {slug(ln) for ln in text.splitlines() if re.match(r"^#{1,6}\s+", ln)}


def parse_tables(text: str):
    """Yield (headers, rows) for each Markdown table."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("|") and i + 1 < len(lines) and re.match(
                r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            hdr = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                rows.append([c.strip() for c in lines[j].strip().strip("|").split("|")])
                j += 1
            yield hdr, rows
            i = j
        else:
            i += 1


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    md_files = list(iter_files(root, (".md",)))
    ref_files = list(iter_files(root, (".md", ".json")))
    text_of = {rel(root, p): p.read_text(encoding="utf-8", errors="replace") for p in md_files}

    # references
    refs: dict[str, set] = {}
    for p in ref_files:
        for m in ID_RE.finditer(p.read_text(encoding="utf-8", errors="replace")):
            refs.setdefault(f"{m.group(1)}-{m.group(2)}", set()).add(rel(root, p))

    # Check 1: exactly one canonical definition per referenced id
    for ident, where in sorted(refs.items()):
        prefix = ident.split("-")[0]
        owner_paths = owners_for(prefix, root)
        if not owner_paths:
            continue
        texts = [text_of.get(rel(root, o), "") for o in owner_paths if o.exists()]
        n = canonical_defs(ident, texts)
        if n == 0:
            errors.append(f"[undefined-ref] {ident} referenced ({', '.join(sorted(where))}) "
                          f"but has no canonical definition in {[rel(root, o) for o in owner_paths]}")
        elif n > 1:
            errors.append(f"[duplicate-id] {ident} has {n} canonical definitions in "
                          f"{[rel(root, o) for o in owner_paths if o.exists()]}")

    # Check 2: broken links + anchors
    link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for p in md_files:
        for m in link_re.finditer(text_of[rel(root, p)]):
            raw = m.group(1).strip()
            if re.match(r"^[a-z]+://", raw) or raw.startswith("mailto:"):
                continue
            path, _, frag = raw.partition("#")
            target = p if path == "" else (p.parent / path).resolve()
            if path and not target.exists():
                errors.append(f"[broken-link] {rel(root, p)} -> {raw} (missing file)")
                continue
            if frag:
                ttext = text_of.get(rel(root, target)) if target.suffix == ".md" and \
                    str(target).startswith(str(root)) else None
                if ttext is None and target.exists() and target.suffix == ".md":
                    ttext = target.read_text(encoding="utf-8", errors="replace")
                if ttext is not None and slug("# " + frag) not in anchors_of(ttext):
                    errors.append(f"[broken-anchor] {rel(root, p)} -> {raw} (no heading '#{frag}')")

    # Check 3: traceability — one keyed row per requirement, with full columns
    trace = text_of.get(TRACE, "")
    covered: dict[str, list] = {}
    for hdr, rows in parse_tables(trace):
        head0 = hdr[0].upper()
        if head0 not in ("FR", "NFR", "SR", "AC"):
            continue
        cols = {name: i for i, name in enumerate(h.lower() for h in hdr)}
        def col(*names):
            for n in names:
                for name, i in cols.items():
                    if n in name:
                        return i
            return None
        ci = {"risk": col("risk", "threat"), "fm": col("failure"),
              "acc": col("acceptance"), "ver": col("verification"), "st": col("status")}
        for r in rows:
            key = re.sub(r"[*` ]", "", r[0])
            if not re.match(rf"^{head0}-\d+$", key):
                continue
            covered[key] = r
            need = [("risk", ci["risk"]), ("failure/justification", ci["fm"]),
                    ("verification", ci["ver"]), ("status", ci["st"])]
            if head0 != "AC":
                need.append(("acceptance", ci["acc"]))
            for label, idx in need:
                if idx is None or idx >= len(r) or not r[idx].strip():
                    errors.append(f"[trace-incomplete] {key} row missing {label}")
    for prefix in ("FR", "NFR", "SR", "AC"):
        for o in owners_for(prefix, root):
            for ln in text_of.get(rel(root, o), "").splitlines():
                m = re.match(rf"^\s*[-*]\s+\*\*({prefix}-\d+)\b", ln)
                if m and m.group(1) not in covered:
                    errors.append(f"[untraced] {m.group(1)} has no keyed row in {TRACE}")

    # Check 4: accepted decisions still listed open
    open_ids = {m.group(1) for ln in text_of.get(OPEN_Q, "").splitlines()
                if (m := re.match(r"^\s*\|\s*(Q-\d+)\b", ln))}
    for key, text in text_of.items():
        if key == OPEN_Q:
            continue
        for ln in text.splitlines():
            low = ln.lower()
            if any(c in low for c in NEG_CUES):
                continue
            for qid in open_ids:
                if qid in ln and any(w in low for w in ACCEPTED_WORDS):
                    warnings.append(f"[maybe-accepted] {qid} open in {OPEN_Q} but {key}: "
                                    f"\"{ln.strip()[:80]}\"")

    # Check 5: readiness counts vs canonical documents
    rtext = text_of.get(READINESS, "")
    for pat, prefix in COUNT_CLAIMS:
        m = re.search(pat, rtext)
        if not m:
            continue
        claimed = int(m.group(1))
        ids = set()
        for o in owners_for(prefix, root):
            for ln in text_of.get(rel(root, o), "").splitlines():
                for mm in re.finditer(rf"\b({prefix}-\d+)\b", ln):
                    if re.match(rf"^\s*[-*]\s+\*\*{re.escape(mm.group(1))}\b", ln) or \
                       re.match(rf"^\s*\|\s*\*?\*?{re.escape(mm.group(1))}\b", ln):
                        ids.add(mm.group(1))
        if len(ids) != claimed:
            errors.append(f"[count-rot] {READINESS} says {claimed} for {prefix}, "
                          f"canonical has {len(ids)}")

    # Check 6: schema suite executed, passed, and not stale
    sdir = root / "docs/05-data/schemas"
    result_p = root / "tools/schema_suite/RESULT.json"
    if not result_p.exists():
        errors.append("[schema-suite] tools/schema_suite/RESULT.json missing — run the suite")
    else:
        res = json.loads(result_p.read_text(encoding="utf-8"))
        sha = hashlib.sha256()
        for name in SCHEMA_FILES:
            sha.update((sdir / name).read_bytes())
        if not res.get("passed"):
            errors.append(f"[schema-suite] last run did not pass: {res.get('failures')}")
        if res.get("schemaSha256") != sha.hexdigest():
            errors.append("[schema-suite] RESULT.json is stale — schemas changed since the "
                          "last run; re-run tools/schema_suite/run_suite.py")
    for p in sorted((sdir / "examples").glob("*.json")) if sdir.exists() else []:
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"[bad-json] {rel(root, p)}: {exc}")

    for w in warnings:
        print("WARN  " + w)
    for e in errors:
        print("ERROR " + e)
    print(f"\nfoundation-lint: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
