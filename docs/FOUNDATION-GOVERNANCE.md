# Foundation governance

Status: normative draft  
Last reviewed: 2026-07-21

## 1. Purpose

This document defines how Koquetel moves from idea to an implementation-safe
specification. The foundation is the source of truth; code will be an executable
projection of approved requirements, not a substitute for missing decisions.

## 2. Authority order

When documents conflict, precedence is:

1. explicit project-owner decision recorded in an accepted ADR;
2. `AGENTS.md` safety and gate rules;
3. accepted ADRs;
4. security and data requirements;
5. API and architecture contracts;
6. product requirements and acceptance criteria;
7. roadmap and explanatory research.

Conflicts must not be resolved by silently following the higher document. Open a
gap, repair all affected documents, and record the change in the worklog.

## 3. Document states

- `research`: evidence collection is incomplete;
- `normative draft`: intended contract, but contains unresolved blockers;
- `accepted`: owner-approved and internally consistent;
- `superseded`: retained for history with replacement link;
- `retired`: no longer applicable; identifiers remain reserved.

Only accepted documents can authorize implementation behavior.

## 4. Traceability contract

Every implementation milestone must provide a matrix:

`requirement → threat/failure mode → acceptance criterion → test → evidence`

Minimum traceability rules:

- each `FR` maps to at least one `AC`;
- each critical `SR` maps to a security test and at least one failure mode;
- each mutable workflow maps to rollback and kill-point tests;
- each public CLI/API field maps to a golden contract test;
- each roadmap exit gate cites objective evidence, never percentages alone.

## 5. Foundation completion gate

`READY FOR IMPLEMENTATION` requires all of the following:

- source inventory and capability matrix complete enough to support decisions;
- product owner decisions Q-01 through Q-05 resolved
  (**done 2026-07-21 — ADR-0006 records Q-01..Q-08**);
- license and clean-room reuse policy accepted (Q-02 selected Apache-2.0;
  attribution plan still open under G-02 narrowed);
- architecture boundaries and transaction model accepted;
- state, memory, permission, secrets, and event schemas versioned;
- failure modes cover install, update, tool execution, memory and routing;
- acceptance, failure-injection, rollback and security matrices complete;
- installer and removal ownership rules specified;
- three high-risk prototypes pass their documented gates;
- independent foundation review finds no unresolved critical contradiction;
- explicit implementation approval exists.

## 6. Prohibited shortcuts

- Declaring “automatic” without defining consent and rollback.
- Declaring “secure” without a threat, control and verification mapping.
- Treating MCP, containers, localhost, or encryption as security boundaries by
  themselves.
- Treating semantic similarity as sufficient memory correctness.
- Treating installation success as readiness without uninstall and recovery.
- Using latest/unpinned dependencies in a reproducible release design.

