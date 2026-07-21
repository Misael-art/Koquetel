# ADR-0001 — Independent core with replaceable adapters

Status: accepted by project owner  
Date: 2026-07-21

## Context

PhaseZero proves breadth and SteamZero proves transactional patterns, but both are
separate products with unrelated lifecycle and domain responsibilities. Koquetel
needs a fully autonomous lifecycle and must survive backend/client replacement.

## Decision

Build a standalone core with inward-facing ports for clients, memory, routing,
tools, sandbox, secrets and telemetry. PhaseZero and SteamZero are research inputs
only; neither is a runtime, build, test, installation, recovery or removal
dependency. No default Koquetel artifact imports their modules, invokes their
commands, requires their paths, consumes their live state or downloads them.

An optional PhaseZero migration utility may consume a user-provided offline
snapshot through Koquetel-owned schemas. It is a separate removable package and is
not installed, imported or exercised by the default runtime.

## Consequences

Initial adapter work is larger, but boundaries, testing, removal and portability
become enforceable. Behavioral concepts are independently reimplemented from
accepted contracts. Research provenance remains documentation, not runtime wiring.
