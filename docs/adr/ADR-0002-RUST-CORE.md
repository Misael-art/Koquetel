# ADR-0002 — Rust core, scripts limited to bootstrap shims

Status: proposed; prototype required  
Date: 2026-07-21

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

## Prototype gate

Before acceptance, demonstrate static/user-scoped packaging, SQLite migration,
atomic config projection, Unix peer credentials, Podman invocation and recovery
after kill. If distribution friction exceeds the documented threshold, revisit
Python with a self-contained runtime.

