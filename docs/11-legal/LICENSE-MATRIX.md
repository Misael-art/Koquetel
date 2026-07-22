# Source license matrix

Status: research; verified at observation pins on 2026-07-21  
Last reviewed: 2026-07-21

This is engineering provenance, not legal advice. Verification used the license
file at the exact commit where available. Koquetel's license is now Apache-2.0
([ADR-0006](../adr/ADR-0006-FOUNDATION-OWNER-DECISIONS.md), Q-02). Component-level
attribution and NOTICE/SBOM formats remain open under G-02 (narrowed).

| Source/pin | Observed license | Qualification | Reuse state |
|---|---|---|---|
| PhaseZero `a0468ba` | **no root license found in tracked tree** | nested Gemini CLI license does not license PhaseZero | behavior research only; no copying (no license = all-rights-reserved) |
| SteamZero `10f3510` | GPL-3.0 | root `LICENSE`; source SPDX matches | concepts only; GPL-3.0 code cannot be copied into Apache-2.0 Koquetel without changing distribution obligations |
| ai-memory `2a85950` | MIT | root `LICENSE` | compatible with Apache-2.0; per-file attribution still required if any code is reused |
| RTK `66e09cb` | Apache-2.0 | root `LICENSE` | compatible; external binary preferred, notices required if distributed |
| MCP `88191b9` | transitional MIT/Apache-2.0; docs CC-BY-4.0 | license says contribution-level transition; specification/docs scope differs | protocol conformance; avoid copying text/code without per-file check |
| Letta `b76da90` | Apache-2.0 | root `LICENSE` | compatible; concepts/adapters; component review required |
| Mem0 `dd5f7e3` | Apache-2.0 | root `LICENSE` | compatible; concepts/adapters; component review required |
| LiteLLM `212a921` | MIT outside `enterprise/` | enterprise directory uses separate license | compatible (OSS part only); exclude `enterprise/` code |
| OpenHands `a1547a9` | MIT outside `enterprise/` | enterprise directory uses separate license | compatible (OSS part only); exclude `enterprise/` code |
| OpenTelemetry SemConv `421dda7` | Apache-2.0 | root `LICENSE` | compatible; standards-compatible field use/notices as required |
| A2A `cfc9d34` | Apache-2.0 | root `LICENSE` | compatible; future protocol adapter |

## Decision impact (post Q-02 = Apache-2.0)

- Apache-2.0 Koquetel permits integration with MIT (ai-memory, LiteLLM-OSS,
  OpenHands-OSS) and Apache-2.0 (RTK, Letta, Mem0, MCP, SemConv, A2A) sources.
- GPL-3.0 SteamZero code **cannot** be copied into Apache-2.0 Koquetel without
  imposing GPL obligations on the whole; SteamZero remains concepts-only.
- PhaseZero remains blocked from any copying because it has no tracked license
  (all-rights-reserved for reuse planning).
- All compatible reuse still requires: pin, per-file license check, attribution,
  NOTICE handling, `enterprise/` exclusions and dependency license scanning.

The active no-copy block in `REUSE-POLICY.md` remains in force until the
attribution plan (G-02 narrowed) is written; this matrix records compatibility,
it does not authorize copying.

