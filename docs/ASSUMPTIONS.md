# Assumptions

Status: living document  
Last reviewed: 2026-07-21

| ID | Assumption | Consequence | Invalidation signal |
|---|---|---|---|
| A-01 | Koquetel begins as a Linux local-first product | Rust core, Unix socket, rootless sandbox and systemd-user integration are viable defaults | owner selects cross-platform v1 |
| A-02 | Existing AI CLIs remain independently installed products | Koquetel uses adapters and does not fork their runtimes | a required client exposes no stable integration surface |
| A-03 | `ai-memory` is an initial backend, not the canonical data model | memory contracts must support replacement and export | owner requires hard dependency |
| A-04 | MCP remains the main tool interoperability protocol | registry and policy wrap MCP rather than replace it | ecosystem moves to an incompatible dominant protocol |
| A-05 | Users value cost reduction only when task quality is preserved | economy metrics include accepted outcomes, not token reduction alone | product goal becomes minimum cost regardless of quality |
| A-06 | Most workspace mutations can run without host privilege | privileged helper remains narrow and optional | required operations routinely need root |
| A-07 | Retired: independence is no longer an assumption | promoted to accepted ADR-0001, P-13, NFR-13 and AC-17 on 2026-07-21 | identifier retained for history |
| A-08 | Normative technical documents use English for protocol and ecosystem consistency | identifiers, schemas and review language remain uniform across international tools | owner selects Portuguese as the normative language |
