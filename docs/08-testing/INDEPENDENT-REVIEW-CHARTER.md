# Independent foundation review charter

Status: normative draft — review not yet performed
Last reviewed: 2026-07-22

This charter organizes the independent adversarial foundation review required by
[`../FOUNDATION-GOVERNANCE.md`](../FOUNDATION-GOVERNANCE.md) §5 ("independent
foundation review finds no unresolved critical contradiction") and by
[`../04-security/THREAT-MODEL.md`](../04-security/THREAT-MODEL.md) ("Required
independent review"). It closes the *organization* of gap `G-09`; `G-09` itself
closes only when the review has run and its report is attached.

Writing this charter does not perform the review and does not change readiness.

## 1. Independence requirement (hard)

The reviewer MUST NOT be an author of the foundation. Every agent and author that
produced the documents, schemas, prototypes or tooling to date is **disqualified**
as the reviewer — including the assistant writing this charter. Self-review does
not satisfy §5. The reviewer is either a different human, or an agent operating
under a separate mandate that has not contributed content, and must record their
identity and non-authorship in the report.

## 2. Entry criteria (the reviewer VERIFIES each at the pinned revision)

The reviewer does not assume these — they **verify** each at the pinned commit SHA
(§8) before starting, running the gates on a temporary export of that revision:

- `foundation_lint` reports 0 errors, 0 warnings;
- the schema suite (`tools/schema_suite/run_suite.py`) reports all 13 checks pass;
- the linter unit tests (`tools/tests/test_foundation_lint.py`) pass;
- owner decisions `Q-01..Q-08` are ratified (`ADR-0006`);
- the working tree at the pinned SHA is clean (**verified, not assumed**);
- `ADR-0002`, `ADR-0010` and `ADR-0011` are not marked accepted by an author;
  ADR-0010/0011 honestly expose their G-11 target-filesystem blocker.

## 3. Artifacts in scope

The reviewer reads, at the pinned revision:

- governance and gate: `AGENTS.md`, `FOUNDATION-GOVERNANCE.md`, `FOUNDATION-READINESS-REPORT.md`;
- product intent: `VISION.md`, `PRD.md`, `ACCEPTANCE-CRITERIA.md`;
- architecture and safety: `ARCHITECTURE.md`, `TRANSACTION-MODEL.md`, `FAILURE-MODES.md`, `THREAT-MODEL.md`;
- data and contracts: `DATA-MODEL.md`, `schemas/` (SCH-01..SCH-21 + tolerant profile), `CONTRACTS.md`;
- decisions: `ADR-0001..ADR-0006`, `ADR-0010`, `ADR-0011` (note the ADR-0011
  Decision A / Decision B split and the `G-13` v2 reclassification);
- evidence: `EXTERNAL-AUDITS.md` (**EA-01..EA-07**), all six reports in
  `prototype-evidence/` (**PT-01/PT-04 are PARTIAL**), `RESULT.json`,
  `11-legal/ATTRIBUTION-PLAN.md`;
- traceability and honesty: `TRACEABILITY.md`, `KNOWN-GAPS.md` (incl. the `G-13`
  reclassification), `OPEN-QUESTIONS.md`, `ASSUMPTIONS.md`, `WORKLOG.md`;
- owner packet: `OWNER-RATIFICATION-PACKET.md`;
- tooling: `tools/foundation_lint.py`, `tools/schema_suite/`, `tools/tests/`.

## 4. Adversarial checklist (attempt to break each)

Security attacks (from the threat model — the reviewer tries to construct a path
that the contracts fail to stop):

- **prompt injection** — a repository or memory record instructs an agent to
  exfiltrate secrets or escalate; verify SR-01/SR-05/SR-07/SR-14 deny it.
- **confused deputy** — a low-authority actor induces a high-authority component
  to act; verify SR-01/SR-16 attenuation and PolicyDecision independence (SCH-13).
- **tool manifest substitution** — a server changes behavior after admission;
  verify SR-03/SR-09 + FM-09 (manifest digest re-check).
- **path race / traversal** — symlink or TOCTOU redirects a managed write; verify
  SR-08 + OwnershipFingerprint (SCH-06).
- **secret leakage** — a seeded secret reaches a plan, log, event or support
  bundle; verify SR-05/SR-06 + the secret-ref/content export invariants (SC-10).
- **recovery bypass** — a torn journal, stale lease or unknown-major record drives
  a mutation; verify PT-02, the `ADR-0011` Decision A local-model analysis (a dead
  holder cannot race; `FM-23` liveness is the only residual), and SC-09 sub-test 5
  (tolerant-only record must not be admitted for a write).

Foundation-integrity attacks (the reviewer hunts contradictions):

- **gate integrity** — is there any path to production behavior without
  `APPROVED_TO_IMPLEMENT`? Is any ADR accepted whose gate is unmet?
- **independence invariant** — does any default artifact import, invoke, require a
  path from, or degrade without PhaseZero/SteamZero? Verify P-13/NFR-13/IT-01..08.
- **owner-authority** — is every "accepted by owner" claim backed by a real owner
  statement (ADR-0006 ratification), not by an agent recommendation?
- **evidence honesty** — is any row `proven` without a retained artifact and an
  independent reviewer? Is any count in the readiness report inconsistent with the
  canonical documents (cross-check with `foundation_lint`)?
- **ID and reference integrity** — duplicate definitions, dangling references,
  broken anchors (cross-check with `foundation_lint`).
- **ADR readiness & G-13 scope** — confirm none of `ADR-0002`, `ADR-0010` and
  `ADR-0011` is self-accepted; confirm G-11 blocks v1 target-filesystem
  ratification and `G-13` blocks only the v2 distributed/NFS/multi-host
  path (`ADR-0011` Decision B), not the v1 local OFD model (Decision A), and that
  the reclassification argument holds.

## 5. Findings format

Findings are numbered `RF-NN` (independent-review finding). Each finding records:

| Field | Meaning |
|---|---|
| id | `RF-NN`, stable within the review |
| severity | `critical` \| `high` \| `medium` \| `low` |
| class | `contradiction` \| `security` \| `evidence-gap` \| `traceability` \| `independence` |
| location | file:line or identifier(s) |
| description | the concrete failure path or contradiction |
| required resolution | what must change, and which gap/ADR/test it maps to |

A `critical` finding is any unresolved contradiction that would let implementation
proceed on a false premise (e.g., an accepted gate with no evidence, a broken
independence invariant, a security control with no verification path).

## 6. Exit criterion

The review passes only when **no `critical` and no `high` finding remains open**.
Each `critical`/`high` finding is either fixed at the source (with the fixing
commit referenced) or downgraded with explicit evidence and owner acknowledgement.
The reviewer attaches a dated report listing every `RF-NN`, its disposition and
the pinned revision reviewed.

## 7. What passing this review does and does not unlock

- It closes `G-09` and satisfies one §5 item.
- It is a **precondition** for any `TRACEABILITY.md` row to become `proven` (the
  approval rule requires a reviewer).
- It does **not** by itself exit M-00: the prototype gates (≥3 high-risk passing,
  §5) and the explicit `APPROVED_TO_IMPLEMENT` marker remain independent
  requirements.

## 8. Pinned revision

The review MUST be performed against a single pinned commit SHA — the tip of
`foundation/m00-closure` at or after the reconciliation commit
`docs(m00): reconcile ADR scope and independent review entry`. The reviewer
records that exact SHA in the report and re-runs every §2 entry check against a
temporary export of it (not against a live, possibly-dirty tree). Any commit after
the pinned SHA invalidates the review and requires re-pinning.
