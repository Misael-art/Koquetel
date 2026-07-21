# ADR-0003 — Balanced, capability-based automation

Status: proposed; owner decision Q-04 required  
Date: 2026-07-21

## Context

The product aims for automation, but IDE agents process untrusted repositories
and can invoke tools with real side effects. A global approve/deny switch cannot
express useful safe automation.

## Proposed decision

Classify effects as observe, workspace-write, external-write, host-admin and
destructive. Reversible scoped workspace writes may be automatically delegated by
profile. External, privileged and destructive operations require plan-bound user
confirmation unless a narrower expiring delegation already exists. Child agents
receive attenuated subsets only.

## Consequences

Policy and confirmation become core domain features. “Autonomous” means fewer
interruptions inside granted bounds, never unrestricted host authority.

