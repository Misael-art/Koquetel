# ADR-0004 — Koquetel memory envelope over replaceable backends

Status: accepted 2026-07-22 (proposed 2026-07-21) — envelope-over-backends decision; ai-memory adapter conditional

## Acceptance

Accepted under the owner's M-00 authorization now that the "prototype required"
gate is met: **PT-03** (`prototype-evidence/PT-03-evidence.md`) ran ai-memory's
real store tests (180 pass at pin `2a85950`) and fault-injected cross-process
concurrency (10,000 ops, 0 lost/torn), byte corruption (detected fail-closed) and
export round-trip (digest match). `G-04` closes on this evidence.

The **envelope-over-replaceable-backends decision is accepted**. ai-memory as the
**initial adapter** remains **conditional** on three requirements PT-03 pinned:

1. the adapter issues writes as `BEGIN IMMEDIATE` (or one serialized writer) — not
   ai-memory's DEFERRED default (EA-01 AC-CONC);
2. Koquetel owns the SCH-10 envelope export/import (ai-memory's transcript export
   is not the governance export — EA-01 AC-EXP);
3. governance/ownership metadata lives in Koquetel's own `synchronous=FULL` store,
   not at ai-memory's `synchronous=NORMAL` (EA-01 AC-DUR).

These are M-03 adapter obligations, not blockers to the envelope decision.

## Context

ai-memory offers immediate continuity, while Letta and Mem0 demonstrate other
memory organizations. Hard-coding one backend would couple governance, migration
and client integration to external semantics.

## Decision

Koquetel owns metadata, scopes, provenance, lifecycle and policy in a canonical
memory envelope. Backends store/search content through adapters. ai-memory is the
initial adapter, contingent on durability, concurrency, export and recovery tests.

## Consequences

Some backend-native features require explicit capability discovery. Koquetel can
quarantine or export records even when switching search implementations.

