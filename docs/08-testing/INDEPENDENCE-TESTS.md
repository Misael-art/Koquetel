# PhaseZero and SteamZero independence tests

Status: normative draft  
Last reviewed: 2026-07-21

These tests enforce P-13, NFR-13 and AC-17. Research documentation and the
separately packaged offline migration utility are the only allowed references.

## Static gates

- **IT-01 Dependency graph:** default manifests, lockfiles, packages and SBOM have
  no PhaseZero or SteamZero module, package, repository, submodule or path.
- **IT-02 Production literals:** source, templates, services, entrypoints, schemas
  and generated default artifacts contain no imports, executable names, ownership
  markers or required paths belonging to either project.
- **IT-03 Boundary lint:** default production modules cannot import the optional
  migration package; migration cannot be an entrypoint of the core service.
- **IT-04 Release contents:** unpacked release artifacts contain no source-project
  code or live checkout links; provenance notices remain allowed documentation.

## Runtime gates

- **IT-05 Clean-room lifecycle:** build and run the complete install→operate→
  update→recover→export→remove sequence in a clean environment where both source
  names are DNS-blocked and their known paths are absent.
- **IT-06 No discovery:** filesystem and process tracing proves Koquetel never
  probes source-project paths, commands, services or configuration during default
  operation.
- **IT-07 Capability parity:** the supported capability/status matrix is identical
  whether unrelated source checkouts exist elsewhere on the host or not.
- **IT-08 Migrated-state severance:** after optional offline import and removal of
  the importer/snapshot, all imported data uses Koquetel schemas and normal
  lifecycle remains green.

## Release gate

Any failure is release-blocking. Tests run from packaged artifacts, not only the
source tree, because hidden build or runtime coupling can be introduced by
packaging and generated configuration.
