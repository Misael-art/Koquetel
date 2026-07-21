# Source license matrix

Status: research; verified at observation pins on 2026-07-21  
Last reviewed: 2026-07-21

This is engineering provenance, not legal advice. Verification used the license
file at the exact commit where available. Compatibility remains unresolved until
Q-02 selects Koquetel's license and component-level review is complete.

| Source/pin | Observed license | Qualification | Reuse state |
|---|---|---|---|
| PhaseZero `a0468ba` | **no root license found in tracked tree** | nested Gemini CLI license does not license PhaseZero | behavior research only; no copying |
| SteamZero `10f3510` | GPL-3.0 | root `LICENSE`; source SPDX matches | concepts only until Q-02; copying would impose GPL obligations |
| ai-memory `2a85950` | MIT | root `LICENSE` | potentially compatible; audit/attribution still required |
| RTK `66e09cb` | Apache-2.0 | root `LICENSE` | external binary preferred; notices required if distributed |
| MCP `88191b9` | transitional MIT/Apache-2.0; docs CC-BY-4.0 | license says contribution-level transition; specification/docs scope differs | protocol conformance; avoid copying text/code without per-file check |
| Letta `b76da90` | Apache-2.0 | root `LICENSE` | concepts/adapters; component review required |
| Mem0 `dd5f7e3` | Apache-2.0 | root `LICENSE` | concepts/adapters; component review required |
| LiteLLM `212a921` | MIT outside `enterprise/` | enterprise directory uses separate license | adapter to OSS interface; exclude enterprise code |
| OpenHands `a1547a9` | MIT outside `enterprise/` | enterprise directory uses separate license | sandbox concepts; exclude enterprise code |
| OpenTelemetry SemConv `421dda7` | Apache-2.0 | root `LICENSE` | standards-compatible field use/notices as required |
| A2A `cfc9d34` | Apache-2.0 | root `LICENSE` | future protocol adapter |

## Decision impact

- Apache-2.0 Koquetel would permit broad integration but cannot incorporate
  GPL-3.0 SteamZero code without changing distribution obligations.
- GPL-3.0-or-later Koquetel could reuse compatible GPL concepts/code with notices,
  but may reduce adoption as an embedding/integration layer.
- Either choice still requires attribution, NOTICE handling where applicable,
  enterprise-directory exclusions and dependency license scanning.

The active no-copy block in `REUSE-POLICY.md` remains in force.

