# Foundation schema suite (SC-01..SC-10)

Foundation-only tooling. It **proves** the schema contracts in
`docs/05-data/schemas/` — it is not product code, is not installed, does not touch
the host, and its validator dependency is deliberately **isolated** from the
Koquetel runtime (P-13, NFR-13, IT-01..IT-03).

## Why a real validator

`tools/foundation_lint.py` only checks that JSON is well-formed. Well-formed JSON
is not a validated schema. This suite uses a pinned Draft 2020-12 validator
(`jsonschema`, see `requirements.txt`) to actually validate.

## Isolation

The validator lives in a throwaway venv under `.venv/` (git-ignored). It is never
imported by any product module and never appears in a release artifact. Removing
`tools/schema_suite/` removes the entire foundation dependency.

## Run

```bash
python3 -m venv tools/schema_suite/.venv
tools/schema_suite/.venv/bin/pip install -r tools/schema_suite/requirements.txt
tools/schema_suite/.venv/bin/python tools/schema_suite/run_suite.py
```

## What it checks

- **meta**: the eight strict schemas and the tolerant profile conform to the
  Draft 2020-12 meta-schema;
- **SC-01..SC-08**: every `SCH-01..SCH-20` entity (root and `$defs`) — its valid
  example validates and its invalid example is rejected for exactly the rule in
  `docs/05-data/schemas/examples/manifest.json`;
- **SC-09**: the five strict-write / tolerant-read sub-tests;
- **SC-10**: recursive classification completeness and the secret-ref/content
  export invariants;
- **semantic**: `confirmation.planHash` binding (SR-04) and journal torn-tail
  recovery (AR-09).

It writes `RESULT.json` (retained evidence, including the schema SHA-256).
`tools/foundation_lint.py` fails if `RESULT.json` is missing, not `passed`, or its
`schemaSha256` no longer matches the current schema files (staleness guard).
