# Retained prototype-evidence policy

Status: normative draft
Last reviewed: 2026-07-22
Motivation: independent-review finding **RF-03** (evidence-gap) — the earlier
prototype reports were summaries only; the raw logs, traces and inputs had been
deleted, so a reviewer could not validate that the declared commands produced the
asserted verdicts. This policy defines the *retained, inspectable* evidence every
prototype gate must leave behind, so an independent reviewer can re-derive the
verdict without trusting a summary.

This policy governs evidence retention only. It does **not** authorize
implementation, does not create product code, and prototypes remain
NON-PRODUCTION / DISPOSABLE.

## 1. Required bundle per prototype

Every `PT-NN` retains an immutable evidence bundle under:

```
docs/08-testing/prototype-evidence/PT-NN/
  manifest.json      # machine-readable index (see §2)
  environment.txt    # host, kernel, toolchain + dependency versions, UTC clock
  commands.txt       # the exact commands run, in order, reproducibly
  stdout.log         # raw stdout of the run (born without secrets)
  stderr.log         # raw stderr of the run (born without secrets)
  metrics.json       # or metrics.csv — the measured numbers behind the verdict
  pass-fail.json     # machine-readable per-arm and overall verdict (see §3)
  SHA256SUMS         # sha256 of every other file in the bundle
  harness/           # the disposable harness source + minimal scripts
  README.md          # short human index pointing to the report and listing files
```

When a correction would otherwise edit an immutable raw bundle, the new capture
uses an adjacent run-qualified directory (`PT-NN-R2`, `PT-NN-R3`, …). The
human report identifies exactly one current canonical run. Older directories
remain byte-for-byte unchanged and are historical, never merged into the new
verdict.

The human-readable `PT-NN-evidence.md` report (one level up) MUST reference this
bundle directory and cite its `SHA256SUMS` so a reviewer can verify integrity.

## 2. `manifest.json` required fields

- `pt`: the gate id (e.g. `PT-01`);
- `title`; `verdict` (`PASS` | `PARTIAL` | `FAIL`);
- `runKind`: `"verification rerun after RF-03"` for reruns (never presented as the
  earlier run);
- `generatedAtUtc`: ISO-8601 UTC;
- `environmentRef`, `commandsRef`, `stdoutRef`, `stderrRef`, `metricsRef`,
  `passFailRef`: bundle-relative filenames;
- `externalPins`: pinned commit/release for any external project used (or `[]`);
- `toolchain`: compiler/interpreter + key dependency versions;
- `syntheticData`: `true` — all inputs must be synthetic (see §4);
- `secrets`: `"none"` — explicit no-secrets declaration;
- `armsExecuted` / `armsNotExecuted`: the covered and uncovered arms;
- `limitations`: free-text honest coverage gaps (e.g. Podman absent).

## 3. `pass-fail.json` shape

```json
{ "pt": "PT-01", "overall": "PASS",
  "arms": [ { "name": "...", "verdict": "PASS", "metricRef": "metrics.json#..." } ],
  "criteria": "one line per gate criterion and whether the retained data meets it" }
```

A verdict is only `PASS` if the retained `metrics`/`stdout`/traces in the bundle
themselves satisfy the gate criteria — not merely because the report asserts it.

## 4. Hard rules

- **No binaries.** No compiled artifacts, `target/`, `.venv/`, `node_modules/`,
  caches, or SQLite/DB files are committed. Record a binary's sha256 in
  `metrics.json`/`manifest.json` instead of the binary.
- **No secrets or private data.** No tokens, credentials, secret paths, real user
  home paths beyond what is unavoidable, private prompts, or memory content.
- **Synthetic inputs only.** All inputs are generated (random/synthetic); no real
  user data. `manifest.json.syntheticData` MUST be `true`.
- **Logs born clean.** Logs are produced without secrets in the first place. They
  are **not** silently "sanitized" after the fact; if a redaction step is ever
  needed it is disclosed in `README.md`.
- **Immutability.** After capture, bundle files are not edited; a correction is a
  new run with a new `generatedAtUtc`, and the old bundle is superseded in the
  report (history preserved, not rewritten).
- **Disposable harness.** `harness/` is NON-PRODUCTION, lives outside the product
  build/release graph, is never imported by a product module, and is retained only
  as evidence source — not as a component.
- **External sources read-only.** Any external project (e.g. ai-memory) is used at
  a pinned commit, read-only, outside the repo; the bundle records the pin and a
  before/after cleanliness check.

## 5. Reviewer verifiability

An independent reviewer must be able to, from the bundle alone:

1. read `commands.txt` and `environment.txt` and understand exactly what ran;
2. verify `SHA256SUMS` against the other files;
3. parse every `*.json` and `metrics.*`;
4. confirm `pass-fail.json` matches the gate criteria and the raw logs/metrics;
5. confirm no secrets and only synthetic inputs;
6. re-run the `harness/` if desired (it is retained source).

A gate whose bundle does not permit steps 1–5 is not `PASS`, regardless of the
Markdown summary.

## 6. Relationship to disposal

The earlier "delete the prototype after evidence capture" rule is **superseded by
this policy** for the retained-bundle contents: the *ephemeral working directory*
(temp dirs, build outputs, venvs, DBs) is still deleted, but the *non-secret,
non-binary evidence* enumerated in §1 is retained in-repo. The two are not in
conflict: binaries/caches/DBs are disposed; logs/metrics/traces/harness-source are
kept.

## 7. Raw log byte preservation

Raw logs are preserved byte-for-byte. Whitespace produced by the capturing tool
is evidence and is not reformatted. Any `blank-at-eof` exception is specific to
one file; it does not disable the other whitespace checks. The file-specific
exception for PT-03 leaves `SHA256SUMS` valid because the raw log itself is
unchanged.
