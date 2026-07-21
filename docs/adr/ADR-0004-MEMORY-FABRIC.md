# ADR-0004 — Koquetel memory envelope over replaceable backends

Status: proposed; prototype required  
Date: 2026-07-21

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

