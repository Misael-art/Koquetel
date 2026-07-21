# License, provenance and reuse policy

Status: normative draft; license decision blocked by Q-02  
Last reviewed: 2026-07-21

## Operative block

Until Q-02 and G-02 close, no source code, templates, distinctive configuration
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

