# Attribution, NOTICE and SBOM plan

Status: normative draft  
Last reviewed: 2026-07-21

This plan closes the open half of `G-02` after `Q-02` selected Apache-2.0 as
Koquetel's license
([ADR-0006](../adr/ADR-0006-FOUNDATION-OWNER-DECISIONS.md)). It defines the
clean-room policy, the per-reused-file attribution record, the `NOTICE` format,
the SBOM format and the source-offer format. It does **not** authorize any
copying; the no-copy block in [`REUSE-POLICY.md`](REUSE-POLICY.md) remains in
force until each candidate passes this plan.

## 1. Clean-room policy

Koquetel's default is **independent reimplementation from documented contracts**.
Two reuse modes exist; both require this plan to be satisfied first.

| Mode | Meaning | Pre-conditions |
|---|---|---|
| **clean-room** | one party records a behavior-level contract from reading a source; a different party implements without consulting the source | source is research-only; no code copied; contract must not reproduce distinctive text/structure |
| **copy-with-attribution** | verbatim or modified copy of source code/data structures from a compatible-licensed source into a Koquetel file | all of §2..§6 satisfied; license compatibility verified at the exact pin |

Clean-room is the default and the preferred mode. Copy-with-attribution is only
permitted when all of the following hold:

1. the source license at the exact pin is verified compatible with Apache-2.0
   (see [`LICENSE-MATRIX.md`](LICENSE-MATRIX.md));
2. the file is registered in §2 below with provenance;
3. the `NOTICE` obligations of that license are met (§4);
4. the SBOM entry is recorded (§5);
5. a reviewer different from the author signs the reuse record.

**Prohibited sources for copy-with-attribution** (must be clean-room only):

- PhaseZero — no tracked root license (all-rights-reserved).
- SteamZero — GPL-3.0; copying would impose GPL on the whole of Koquetel and is
  incompatible with Apache-2.0.
- Any file under a `enterprise/`, `commercial/` or proprietary subdirectory.
- Any source whose license cannot be verified at the exact pin.

## 2. Per-reused-file attribution record

Every file copied (or structurally derived) from a third-party source gets a row
in `docs/11-legal/REUSE-LEDGER.md` (created on first reuse) with these fields:

| Field | Meaning |
|---|---|
| `koquetel_path` | destination path inside Koquetel |
| `source_repo` | canonical URL (e.g. `https://github.com/akitaonrails/ai-memory`) |
| `source_commit` | exact pin (full SHA) the file was read from |
| `source_path` | path inside the source repo at that commit |
| `source_license_spdx` | SPDX id verified at the pin (e.g. `MIT`, `Apache-2.0`) |
| `source_copyright` | copyright line from the source file or root LICENSE |
| `modifications` | one of: `verbatim`, `modified`, `structural-derivative` |
| `modification_notes` | if modified/derivative: what changed and why |
| `reviewer` | name/handle of a reviewer different from the author |
| `review_date` | ISO date of the review |
| `notice_required` | yes/no — whether the source license requires NOTICE attribution |

Until the first row exists, `REUSE-LEDGER.md` is empty and the no-copy block
applies globally.

## 3. Dependency → license → use → distribution obligation matrix

Each runtime/build dependency (crate, package, vendored library) that ships in a
release artifact gets a row in `docs/11-legal/DEPENDENCY-MATRIX.md` (created on
first dependency) with:

| Field | Meaning |
|---|---|
| `dependency` | name and version (pinned) |
| `source_url` | canonical URL |
| `license_spdx` | effective SPDX (resolved including transitive obligations) |
| `use` | `runtime` / `build-only` / `dev-only` / `vendored` |
| `ships_in_release` | yes/no (dev/build-only = no) |
| `distribution_obligation` | one of: `keep-license-text`, `keep-license+NOTICE`, `keep-license+NOTICE+source-offer`, `none` |
| `sbom_ref` | purl/CPE for the SBOM entry |

The release artifact MUST contain the resolved license texts for every
`ships_in_release=yes` dependency.

## 4. NOTICE format

The repository and each release artifact carry a `NOTICE` file at the root. The
Koquetel `NOTICE`:

```
Koquetel
Copyright (c) 2026 The Koquetel authors.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

================================================================================
THIRD-PARTY NOTICES
================================================================================

<For each reused file/dependency with notice_required=yes, in alphabetical order
by source project:>

<source project name> (<source URL>)
  Used at: <koquetel_path or dependency name@version>
  Pin: <commit SHA>
  License: <SPDX>
  Copyright: <copyright line from source>

<verbatim license text if the source license requires it>
```

Dependencies whose license only requires keeping the license text (e.g. MIT
without a NOTICE clause) appear in `LICENSES/` but not in `NOTICE`. Dependencies
whose license requires a source-offer (e.g. LGPL, GPL-family — incompatible with
Apache-2.0 Koquetel core) MUST NOT be linked.

## 5. SBOM format

Each release publishes an SBOM in **CycloneDX 1.5 JSON** (`koquetel-<version>-sbom.json`)
with:

- `metadata.component` = Koquetel at the released version and commit;
- one `components[]` entry per `ships_in_release=yes` dependency, with `purl`,
  `version`, `licenses[]`, `supplier`;
- one `components[]` entry per vendored file with provenance fields;
- `dependencies[]` reflecting the build graph;
- `properties[]` recording `koquetel:source_commit`, `koquetel:builder`,
  `koquetel:build_timestamp`, `koquetel:reproducible=true|false`.

CycloneDX is chosen over SPDX SBOM because it round-trips the dependency graph
and is tool-supported by the likely Rust/Cargo and Python ecosystems.

## 6. Source-offer format

Koquetel core is Apache-2.0 and ships source at the released commit, so no
source-offer obligation attaches to the core. If any future component is added
under a license requiring written source-offer (LGPL-family, etc.) — which is
discouraged and requires an ADR — the release MUST include:

- `SOURCE-OFFER.md` at the release root stating the offer validity (3 years from
  release), the corresponding source commit, and a no-charge delivery method;
- the source tarball or a reference to the public repository at that commit.

## 7. Prohibited shortcuts

- Copying code before its row exists in `REUSE-LEDGER.md`.
- Recording a `verbatim`/`modified` reuse without a reviewer different from the
  author signing it.
- Bundling a dependency without its license text resolved.
- Stripping copyright or license headers from copied files.
- Treating "compatible license" as sufficient — attribution and NOTICE
  obligations are independent of compatibility.
- Using latest/unpinned dependencies in a release artifact.

## 8. State

- `REUSE-LEDGER.md`: not yet created (no copied code; clean-room is the default
  and has been used so far).
- `DEPENDENCY-MATRIX.md`: not yet created (no implementation dependencies yet).
- `NOTICE`: will be created when the first file is authored (M-01 core); the
  header above is the template.
- This plan narrows and addresses the open half of `G-02`. `G-02` closes fully
  when the first `REUSE-LEDGER.md`/`DEPENDENCY-MATRIX.md` entries exist and
  the `NOTICE` template has been applied to a real release artifact.
