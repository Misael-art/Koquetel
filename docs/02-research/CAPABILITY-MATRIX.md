# Capability matrix

Status: local-source evidence complete; external implementations pending  
Last reviewed: 2026-07-21

Legend: `✔` systematic; `◐` partial/ad hoc; `✖` not evidenced at pinned commit.
Evidence references use the audit in `SCRIPT-INVENTORY.md`.

| Capability | PhaseZero `a0468ba` | SteamZero `10f3510` | Strongest research evidence | Required independent Koquetel implementation |
|---|---|---|---|---|
| host/client discovery | ✔ broad status inventory | ◐ domain host probes | PhaseZero | typed probes with tested versions |
| multi-IDE/CLI projection | ✔ 7+ rule and 12 MCP targets | ✖ | PhaseZero | canonical round-trip adapters |
| RTK integration | ✔ verified release checksum | ✖ | PhaseZero/RTK | pinned manifest + degraded mode |
| style/frugality rules | ✔ Caveman + generated skeleton | ✖ | PhaseZero | optional roles; no silent truncation |
| durable memory install | ◐ AUR/Docker/source fallbacks | ✖ | PhaseZero/ai-memory | immutable supply chain and least mounts |
| memory governance | ✖ backend delegated | ✖ | external research | Koquetel-owned envelope and lifecycle |
| context compilation | ◐ first-500 file skeleton | ✖ | new capability | relevance, precedence and budget evidence |
| MCP definition registry | ✔ schemas, safe sync, doctor | ✖ | PhaseZero/MCP | admission, integrity and policy |
| tool authority policy | ◐ safe flag and explicit install | ◐ privileged allowlists in domain | new central engine | typed capabilities and plan-bound consent |
| sandboxed AI execution | ✖ full-home Docker fallback is not containment | ✖ AI-specific sandbox absent | OpenHands/containers | rootless default with limits |
| privilege boundary | ◐ wrapper, but arbitrary command | ✔ domain-specific typed helper patterns | SteamZero concept | minimal protocol; no shell passthrough |
| model gateway/routing | ✔ multiple managers and wrappers | ✖ | PhaseZero/external gateways | one router port and compatibility set |
| budgets/cost attribution | ◐ usage tools/gateway data | ✖ | LiteLLM + new evaluation | task outcome tied to cost |
| structured diagnostics | ✔ large aggregated status/doctor | ✔ typed status/errors/journal | combine | semantic health and stable errors |
| atomic file mutation | ◐ temp+move per config | ✔ centralized fsync+rename | SteamZero | transaction-owned projection writes |
| plan/precondition model | ◐ dry-run summaries vary by script | ✔ plan token, fingerprint, expiry | SteamZero | exact hash-bound authority |
| backup integrity | ◐ plain copies | ✔ source/copy hash verification | SteamZero | portable manifest and retention |
| crash recovery | ◐ tool-local rollback registration | ✔ intent journal and kill recovery | SteamZero | atomic lock and torn-tail correction |
| path containment | ◐ inconsistent across scripts | ✔ centralized realpath/component checks | SteamZero | descriptor-relative race-safe operations |
| failure injection | ◐ selected AI tests | ✔ explicit kill and rollback tests | SteamZero | apply to every AI capability |
| update provenance | ◐ strong for RTK, weak/unpinned elsewhere | ✔ release source controls | SteamZero + RTK | uniform manifest/SBOM/provenance |
| uninstall/removal | ◐ per-tool and preservation conventions | ✔ ownership-aware lifecycle patterns | SteamZero | offline global remove/export |
| cross-agent delegation | ◐ tool-specific orchestration | ✖ | new/A2A research | authority/budget/memory attenuation |
| interoperable telemetry | ◐ custom JSON | ◐ custom journal/events | OpenTelemetry | GenAI semconv with privacy defaults |

## Conclusion

No single source satisfies Koquetel. PhaseZero demonstrates integration coverage;
SteamZero demonstrates execution rigor; external standards/projects demonstrate
specialized interfaces. These are research observations, not dependency choices.
Koquetel independently implements its accepted contracts and remains fully
functional when every research source is absent.
