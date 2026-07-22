# License, provenance and reuse policy

Status: normative draft; Koquetel license selected (Apache-2.0, ADR-0006 / Q-02); attribution plan still open (G-02 narrowed)
Last reviewed: 2026-07-21

## Operative block

Koquetel's license is Apache-2.0 ([ADR-0006](../adr/ADR-0006-FOUNDATION-OWNER-DECISIONS.md),
Q-02). The no-copy block below remains in force until the component-level
attribution plan, NOTICE template and SBOM/source-offer format are written
(`G-02` narrowed). Behavioral observation and independently written contracts are
allowed at all times.

Until G-02 closes, no source code, templates, distinctive configuration
structures or documentation passages from research projects may be copied into
Koquetel. Behavioral observation and independently written contracts are allowed.

## Reuse decision

For every candidate:

1. Pin repository, commit and retrieval date.
2. Verify actual license file and relevant subdirectory/component license.
3. Identify copyright and generated/vendored status.
4. Determine compatibility with Koquetel's accepted license.
5. Evaluate whether reuse satisfies security and architecture requirements.
6. If all pass, record files, SPDX identifiers, attribution and modifications.
7. Otherwise use clean-room behavioral reimplementation: one party records a
   behavior-level contract; implementation does not consult incompatible code.

No license or absent license means all-rights-reserved for reuse planning. Project
names and trademarks are evaluated separately from code licenses.

## Required source register fields

Name, canonical URL, pinned commit/version, date, license file path/digest,
component scope, analyzed paths, adopted concept, reuse mode, attribution need and
reviewer.

