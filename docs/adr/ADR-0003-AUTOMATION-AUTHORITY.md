# ADR-0003 — Balanced, capability-based automation

Status: accepted by project owner (via Q-04 = Balanced, ADR-0006)
Date: 2026-07-21

## Context

The product aims for automation, but IDE agents process untrusted repositories
and can invoke tools with real side effects. A global approve/deny switch cannot
express useful safe automation. Owner decision Q-04 (recorded in
[`ADR-0006-FOUNDATION-OWNER-DECISIONS.md`](ADR-0006-FOUNDATION-OWNER-DECISIONS.md))
selected the **Balanced** policy.

## Decision

Classify effects as observe, workspace-write, external-write, host-admin and
destructive. Reversible scoped workspace writes may be automatically delegated by
profile. External, privileged and destructive operations require plan-bound user
confirmation unless a narrower expiring delegation already exists. Child agents
receive attenuated subsets only.

## Consequences

Policy and confirmation become core domain features. "Autonomous" means fewer
interruptions inside granted bounds, never unrestricted host authority.

