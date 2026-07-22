# Source register

Status: research; E1 local identity complete  
Last reviewed: 2026-07-21

No source below is approved for code reuse. Remote HEADs are observation pins from
2026-07-21, not dependency selections or approved release versions.

| Source | Pin | Location | Role / state |
|---|---|---|---|
| PhaseZero | `a0468ba92ac7b12aa852691897b27ff210f51fa6` | `/mnt/sdcard/Projects/PhaseZero`; `Misael-art/PhaseZero` | AI integration baseline; dirty working tree, so committed pin is evidence baseline |
| SteamZero | `10f3510681f44db368a2b7a6c332036bb086981d` | `/mnt/sdcard/Projects/Port_Steam`; `Misael-art/SteamZero` | transaction/governance base; untracked files excluded from evidence baseline |
| ai-memory | `2a85950ce8fa5c309fdc3adc481e98a02d824a9f` | `akitaonrails/ai-memory` | memory backend candidate; Rust+SQLite workspace; structural audit EA-01 complete, runtime PT-03 pending |
| RTK | `66e09cbefe02bf82b159a44278250e45e506810b` | `rtk-ai/rtk` | shell compression candidate; benchmark pending |
| MCP | `88191b9f574d67d553ea9372278a14e09d762f55` | `modelcontextprotocol/modelcontextprotocol` | tool transport/specification |
| Letta | `b76da9092518cbaa2d09042e52fdcbde69243e18` | `letta-ai/letta` | tiered/shared memory concepts; remote reported an additional stale remote HEAD ref, excluded |
| Mem0 | `dd5f7e39a86170dd35c6860c854a2b0ef0293b08` | `mem0ai/mem0` | vector/graph memory candidate |
| LiteLLM | `212a9213c4997a4957dfb9337d3f7a94ca138fba` | `BerriAI/litellm` | routing/budget candidate |
| OpenHands | `a1547a9c0d4ef89cfd3161c530b24f6d8cbc5cae` | `OpenHands/OpenHands` | sandbox/runtime candidate |
| OpenTelemetry SemConv | `421dda788ca3dd9f2537d95dc70e457c1fd52600` | `open-telemetry/semantic-conventions` | GenAI telemetry contract |
| A2A | `cfc9d34bc41e368827eb6446d31f912e44f795c5` | `a2aproject/A2A` | future agent interoperability |
| Caveman | (not yet pinned) | `JuliusBrussee/caveman` | style/frugality role candidate (claimed MIT, unverified); identity confirmed 2026-07-21; pin + EA audit deferred to M-02 adapter work |

## Local source state

PhaseZero pin date is 2026-07-13. Its working tree contained modified `AGENTS.md`,
`linux/ai/proxy-suite.sh`, `linux/pz`, and `linux/ui_native/pages/ai_proxies.py`,
plus untracked files including `linux/ai/omniroute-manager.sh`. These items were
not treated as committed evidence. SteamZero pin date is 2026-07-21; its untracked
`.worktrees/` and roadmap directive were likewise excluded.

## Next evidence pass

Complete external structural audits and select dependency releases rather than
using observed HEADs. Re-check every pin and license at the date of a reuse
decision.

