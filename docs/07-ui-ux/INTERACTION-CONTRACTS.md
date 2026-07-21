# Interaction contracts

Status: normative draft  
Last reviewed: 2026-07-21

## Surfaces

v1 is CLI-first. IDE notifications and a future local dashboard consume the same
typed status, plan, policy and event contracts. No surface implements independent
mutation logic.

## Plan and confirmation

A mutation preview shows:

- exact scope and owned targets;
- created, changed and preserved items;
- requested authority class;
- remote destinations and data classification;
- estimated budget where model calls are involved;
- verification and rollback plan;
- immutable plan ID/hash and expiry.

Confirmation language distinguishes `workspace-write`, `external-write`,
`host-admin` and `destructive`. Severity is expressed by text and icon, not color
alone. Batch delegation always shows scope and expiry.

## Degraded behavior

Unavailable optional capabilities produce one non-blocking notice per state
change and an actionable `doctor` reference. Clients must still open. The product
does not repeatedly prompt to install or enable a paid/cloud backend.

## Explainability

Users can ask why a memory was retrieved, why a model was selected, why a tool was
denied, why confirmation is required and which document/policy controls the
decision. Explanations cite structured factors; they are not generated guesses.

## Accessibility and automation

- commands work without TTY using JSON and explicit plan hashes;
- prompts never become the only route to recover or export;
- keyboard and screen-reader order follows visual order;
- progress reports stable phase IDs and terminal result;
- secret input uses provider/system mechanisms and never command arguments where
  process listing could expose it.

