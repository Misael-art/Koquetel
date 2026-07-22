# ADR-0002 — Rust core, scripts limited to bootstrap shims

Status: proposed — ready for owner ratification. PT-05 (`prototype-evidence/PT-05-evidence.md`) sustains the Rust recommendation. The language decision does **not** depend on Podman (an M-04/PT-04 capability) or on atomic config projection (an M-01 capability); those are not circular blockers for the language choice. Not accepted by the author — see `OWNER-RATIFICATION-PACKET.md`.

## Context

The product mutates configuration, manages concurrent state, parses multiple
formats and enforces security boundaries. PhaseZero's large shell scripts provide
reach but make typed contracts and compositional recovery difficult.

## Options

1. Bash-first: easy host integration, weak typed domain and testing boundaries.
2. Python core: rapid implementation and libraries, runtime/environment burden.
3. Rust core: static binary, strong types and controlled dependencies, higher
   initial development cost.

## Proposed decision

Use Rust for core, CLI, transaction engine and security-critical helpers. Limit
shell/PowerShell to minimal bootstrap launchers whose only purpose is to obtain
and invoke a verified core artifact.

## Language-decision gate (what actually decides Rust vs Python/Bash)

The decision under this ADR is the **language for the core**, not the feature set
of later milestones. What decides it — all demonstrated by **PT-05**:

- **Distributability / self-containment.** A single 2.2 MB binary linking only
  glibc (no Rust runtime, no system SQLite). Sustains Rust; refutes the
  "distribution friction" worry that would favour Python-with-runtime.
- **Typed state + SQLite + recovery.** Bundled SQLite, idempotent migrations,
  `kill -9` recovery to old-or-completed. Sustains Rust.
- **Peer-credentialed local API.** `SO_PEERCRED` owner-only rejection + socket
  mode 600. Sustains Rust.

**Explicitly NOT part of the language decision** (do not use as a circular
blocker for the language choice):

- **Atomic config projection** — a transactional-core capability. It is an **M-01
  exit criterion**, not evidence about the language.
- **Podman invocation** — a sandbox capability. It is a **PT-04 / M-04 exit
  criterion**; PT-04 is partial (Podman absent, `G-05` open).

Accepting Rust does **not** prove those two capabilities — they are proven later
at their own milestones. The author recommends ratifying Rust for the core on the
PT-05 evidence.

