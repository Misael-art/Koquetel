# CLI and local API contracts

Status: normative draft  
Last reviewed: 2026-07-21

## CLI surface

```text
koquetel discover [--json]
koquetel init [PATH] [--profile essential|balanced|autonomous] [--dry-run]
koquetel plan <install|update|repair|remove|sync> [--json]
koquetel apply <plan-id> --confirm <plan-hash>
koquetel status [--json]
koquetel doctor [--bundle PATH] [--include-content]
koquetel recover [transaction-id]
koquetel export --output PATH [--scope SCOPE]
koquetel memory <search|inspect|promote|quarantine|supersede|delete|export>
koquetel tools <list|inspect|admit|revoke|doctor>
koquetel policy <explain|list|check>
koquetel budget <status|set|explain>
koquetel adapters <list|status|sync|doctor>
```

Mutation commands do not accept implicit “yes to everything”. Automation uses a
previously issued delegation or exact plan hash.

## Response envelope

All JSON commands return a stable envelope:

```json
{
  "schemaVersion": 1,
  "ok": true,
  "operation": "doctor",
  "correlationId": "01...",
  "result": {},
  "warnings": [],
  "error": null
}
```

Errors contain `code`, `message`, `details`, `retryable`, `nextActions` and an
optional `causeCorrelationId`. Human messages may improve; codes and field
semantics remain compatible within a major schema version.

## Initial stable errors

| Code | Meaning |
|---|---|
| E-1001 | unsupported host or client version |
| E-1002 | managed configuration conflict |
| E-1003 | required capability unavailable |
| E-2001 | plan stale or hash mismatch |
| E-2002 | mutation lease busy |
| E-2003 | recovery required before mutation |
| E-2004 | ownership proof failed |
| E-3001 | policy denied capability |
| E-3002 | confirmation or delegation required |
| E-3003 | delegation expired or broader than parent |
| E-4001 | memory backend unavailable |
| E-4002 | memory conflict or quarantine required |
| E-4003 | context cannot fit mandatory policy budget |
| E-5001 | model/provider unavailable |
| E-5002 | budget or retry ceiling reached |
| E-5003 | no route satisfies privacy/capability policy |
| E-6001 | tool not admitted or manifest changed |
| E-6002 | tool input/output schema invalid |
| E-6003 | sandbox containment requirement unavailable |
| E-7001 | artifact integrity or provenance failure |
| E-7002 | transaction verification failed and rolled back |
| E-7003 | automatic recovery unsafe; operator action required |

## Local API

The socket API mirrors typed application commands, not shell commands. Every
request includes API version, caller identity from peer credentials, correlation
ID and optional active task/delegation. Streaming endpoints expose progress and
events with bounded replay cursors.

No endpoint accepts arbitrary filesystem paths without a declared operation and
policy-resolved root. The privileged helper uses a separate, smaller protocol.

