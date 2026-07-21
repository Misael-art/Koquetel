# Koquetel

Koquetel is a local-first operational layer for AI coding agents. It is intended
to install and integrate memory, context economy, model routing, governed tools,
sandboxed execution, observability, and IDE/CLI adapters as one resilient system.

## Current phase

**Foundation only — implementation is not approved.**

The repository currently contains normative planning documents. Production code,
installers, generated packages, and host mutations are forbidden until the
foundation reaches `READY FOR IMPLEMENTATION` and the project owner creates an
`APPROVED_TO_IMPLEMENT` file or gives equivalent explicit approval.

Start with:

1. [`docs/FOUNDATION-GOVERNANCE.md`](docs/FOUNDATION-GOVERNANCE.md)
2. [`docs/00-vision/VISION.md`](docs/00-vision/VISION.md)
3. [`docs/01-product/PRD.md`](docs/01-product/PRD.md)
4. [`docs/03-architecture/ARCHITECTURE.md`](docs/03-architecture/ARCHITECTURE.md)
5. [`FOUNDATION-READINESS-REPORT.md`](FOUNDATION-READINESS-REPORT.md)

## Foundation map

| Area | Purpose |
|---|---|
| `docs/00-vision` | vision, principles, non-goals |
| `docs/01-product` | product requirements and acceptance criteria |
| `docs/02-research` | sources, evidence, capability comparison |
| `docs/03-architecture` | boundaries, transactions, failure modes, ADRs |
| `docs/04-security` | threat model, permissions, secrets, supply chain |
| `docs/05-data` | state, memory, schemas, migrations and retention |
| `docs/06-api` | CLI, local API, events and stable errors |
| `docs/07-ui-ux` | CLI/IDE/dashboard interaction contracts |
| `docs/08-testing` | tests, failure injection and acceptance evidence |
| `docs/09-operations` | install, update, recovery and support bundles |
| `docs/10-migrations` | safe adoption from PhaseZero and other tools |
| `docs/11-legal` | licenses, provenance and reuse policy |
| `docs/12-roadmap` | phases, gates, dependencies and risks |
| `docs/adr` | architectural decisions |
| `docs/glossary` | canonical vocabulary and forbidden ambiguities |

Cross-cutting traceability is maintained in
[`docs/TRACEABILITY.md`](docs/TRACEABILITY.md).
