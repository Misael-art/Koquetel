# Concept provenance

Status: research draft  
Last reviewed: 2026-07-21

This table records conceptual influence, not copied implementation.

PhaseZero and SteamZero provenance is documentary only. Neither appears in the
default dependency graph, package, service topology or runtime discovery.

| Koquetel capability | Concept sources | Adoption mode | Mandatory correction |
|---|---|---|---|
| transactional lifecycle | SteamZero journal/fs/transaction | independent implementation from Koquetel's accepted behavioral contract; no source/runtime dependency | atomic lock and torn-tail recovery |
| multi-client rules | PhaseZero managed blocks/target map | behavioral reimplementation | semantic parse, hashed backups, all-target transaction |
| memory backend | ai-memory + PhaseZero wiring | external adapter/process | pinning, least mounts, health and export proof |
| memory tiers/sharing | Letta, Mem0 | independent data model informed by public concepts | concurrency, provenance and policy precedence |
| shell economy | RTK | verified external tool adapter | independent failure/degraded behavior |
| model routing/budget | LiteLLM and PhaseZero gateway experiments | replaceable API adapter | outcome quality, privacy routes and retry ceilings |
| tool interoperability | MCP | standards-compatible transport | local admission and authority layer |
| sandbox runtime | OpenHands + rootless container primitives | independent sandbox port | no engine socket, explicit network/mounts/resources |
| telemetry | OpenTelemetry GenAI semconv | standards-compatible events | metadata-only default and redaction |
| agent interoperability | A2A | possible future adapter | authority attenuation remains Koquetel-owned |
