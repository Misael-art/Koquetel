# Robustness score

Status: research; local sources only  
Last reviewed: 2026-07-21

Scale per criterion: `0` absent; `1` ad hoc; `2` partial/repeated; `3` systematic
with meaningful tests or verification; `4` systematic, boundary-enforced and
failure-tested. Weighted result is `Σ(score × weight) / 4` out of 100.

| Criterion | Weight | PhaseZero | SteamZero | Evidence summary |
|---|---:|---:|---:|---|
| error handling | 8 | 3 | 4 | PhaseZero 24/24 strict AI scripts; SteamZero typed errors and verification |
| idempotency/drift | 8 | 2 | 3 | marked blocks versus plan fingerprints/recovery |
| atomicity/durability | 10 | 2 | 4 | per-file temp moves versus centralized file+directory fsync |
| backup/rollback | 12 | 2 | 4 | plain copies/per-target changes versus verified undo journal |
| path safety/least authority | 12 | 1 | 3 | full-home mount/arbitrary admin versus containment; lock race remains |
| supply-chain integrity | 10 | 1 | 3 | RTK strong but memory latest/unpinned; SteamZero release controls broader |
| secrets/privacy | 8 | 2 | 3 | env/0600 conventions versus typed secret and redaction boundaries |
| observability/diagnostics | 7 | 2 | 3 | broad status JSON but marker health; SteamZero operation IDs/journal |
| tests/failure injection | 10 | 2 | 4 | targeted AI tests versus 71 test modules and kill-point suites |
| portability/adapters | 5 | 3 | 2 | PhaseZero's major strength; SteamZero domain/host focused |
| maintainability/boundaries | 5 | 1 | 3 | large shell managers versus enforced core ports |
| uninstall/recovery | 5 | 1 | 4 | tool-specific/best effort versus deterministic transaction recovery |
| **Weighted result** | **100** | **45.25** | **85.00** | local committed pins only |

## Interpretation

SteamZero provides stronger research evidence for execution architecture.
PhaseZero provides stronger research evidence for catalog and client coverage.
Neither becomes a Koquetel dependency, submodule, runtime service or installed
prerequisite. Koquetel independently synthesizes the accepted behaviors while
correcting AR-01 through AR-10. External specialized projects remain unscored
until equivalent structural audits are complete; assigning scores from README
claims would violate MP-2.
