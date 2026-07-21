# Foundation traceability matrix

Status: seed; incomplete by design  
Last reviewed: 2026-07-21

This matrix is the canonical index connecting product intent to verification.
Rows may reference ranges only while the foundation is a draft. Before
implementation approval, every requirement receives its own row with named tests
and evidence location.

| Requirements | Main risks/threats | Failure modes | Acceptance | Verification family | Status |
|---|---|---|---|---|---|
| FR-01..05, NFR-01..04 | R-03, R-10 | FM-01..04, FM-17..20 | AC-01..04, AC-13 | FI-01..03, RT-01..05 | specified, not proven |
| FR-06..08, NFR-08 | R-03, R-05 | FM-03..04, FM-20 | AC-02, AC-15..16 | adapter round-trip + FI-12 + RT-07 | specified, fixtures missing |
| FR-09..13 | R-02, R-07 | FM-05..06, FM-14 | AC-05..07 | FI-04..05, RT-06, SR-11..12 tests | specified, prototype missing |
| FR-14..17 | R-04, R-07, R-11..12 | FM-07..08 | AC-08..09 | provider faults + corpus benchmark | specified, thresholds missing |
| FR-18..22 | R-01, R-07..09 | FM-09..14 | AC-10..11 | FI-07..10 + SR-01..10 tests | specified, review missing |
| FR-23..26 | R-01, R-10, R-12 | FM-08, FM-15..16 | AC-12..15 | delegation properties + interrupted E2E | specified, implementation deferred |
| P-13, NFR-13 | R-05, R-06, R-11 | FM-17, FM-19 | AC-17 | IT-01..08 packaged independence gates | owner-confirmed, not yet proven |

## Approval rule

A row can become `proven` only when its evidence is reproducible from a pinned
source revision and includes environment, command, result artifact and reviewer.
“Test passed” without retained output and contract version is insufficient.
