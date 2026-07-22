# Open owner decisions

Status: living document  
Last reviewed: 2026-07-21

## Decided

The eight foundation owner questions `Q-01..Q-08` were answered explicitly by the
project owner on 2026-07-21. The binding record, including the option chosen,
consequence and authority for each, is
[`adr/ADR-0006-FOUNDATION-OWNER-DECISIONS.md`](adr/ADR-0006-FOUNDATION-OWNER-DECISIONS.md).
A short summary:

- **Q-01 — Product name:** Koquetel (trademark/domain review still open, `G-10`).
- **Q-02 — Project license:** Apache-2.0 (component-level attribution plan still
  open, `G-02` narrowed).
- **Q-03 — First supported hosts:** Linux first, WSL compatibility next.
- **Q-04 — Default autonomy policy:** Balanced (accepts `ADR-0003`).
- **Q-05 — Default data posture:** local-first with cloud opt-in.
- **Q-06 — Supported user profile (v1):** individual developer (no multi-user
  control plane in v1).
- **Q-07 — Interface (v1):** CLI first (local read-only dashboard may follow;
  native UI out of v1).
- **Q-08 — NFS commit-level fence:** NFS unsupported in v1 (multi-host lease
  deferred to a potential v2, requires `G-13`).

The recommendation column that previously lived here is superseded by the
"Option chosen" recorded in ADR-0006. Identifiers `Q-01..Q-08` are preserved and
not renumbered.

## Still open

None at this time. New owner decisions will be added here under new `Q-xx`
identifiers (continuing the sequence after Q-08) and resolved through the same
ADR pattern.
