# Data and memory model

Status: normative draft  
Last reviewed: 2026-07-21

## Canonical stores

- SQLite: configuration projections, transactions, policies, delegations,
  metadata envelopes, events and adapter state.
- Content store: optional encrypted blobs addressed by digest.
- External backends: memory/model/tool systems referenced by adapter identity;
  never the only location of metadata required for export or governance.

SQLite runs WAL mode where supported. Migrations are ordered, reversible until
activation, checksummed and paired with compatible binary ranges.

## Memory envelope

Every memory record has:

- immutable `memory_id`, `schema_version`, `content_digest`;
- `kind`: session, episodic, semantic, procedural, artifact or policy-reference;
- `scope`: installation, user, project, worktree, task or agent;
- source type/reference, actor and originating correlation ID;
- created, observed, reviewed, expires and superseded timestamps;
- confidence and validation state;
- sensitivity and remote-processing policy;
- backend locator(s), embedding/model provenance if applicable;
- relationship to claims it supersedes, contradicts or derives from.

States: `candidate`, `validated`, `quarantined`, `superseded`, `expired`,
`deleted-tombstone`. Only `validated` records are eligible for automatic current
context unless policy explicitly allows candidates.

## Memory write protocol

1. Classify scope, kind and sensitivity.
2. Normalize and compute digest without losing original provenance.
3. Detect exact duplicate and retrieve semantic/graph conflicts.
4. Store as candidate.
5. Apply deterministic validation where possible.
6. Require user/reviewer confirmation for policy, identity, credential-adjacent or
   low-confidence durable claims.
7. Promote with optimistic version check.
8. Emit redacted event and schedule retention.

## Deletion and export

Deletion follows configured policy and backend capability. Where immediate
physical deletion cannot be proven, Koquetel records a tombstone, excludes the
record and reports backend residue. Export uses a versioned, documented archive
containing metadata, content selected by the user, digests and backend omissions.

## Retention defaults

- raw session events: 30 days;
- candidate memories: 14 days if not promoted;
- validated project procedures: no automatic expiry, periodic review due;
- secrets: prohibited as memory content;
- content-bearing telemetry: disabled;
- transaction/audit metadata: 180 days, configurable;
- backups: last three known-good versions plus age ceiling.

Defaults remain provisional until Q-05 is accepted.

