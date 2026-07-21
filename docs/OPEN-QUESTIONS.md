# Open owner decisions

Status: living document  
Last reviewed: 2026-07-21

| ID | Decision | Options | Recommendation | Blocks |
|---|---|---|---|---|
| Q-01 | Final product name and spelling | `Koquetel`, `Coquitel`, another name | Use repository spelling `Koquetel` provisionally; perform trademark/domain review before release | identity, packaging |
| Q-02 | Project license | Apache-2.0; GPL-3.0-or-later; another owner-selected license | Apache-2.0 if broad integration is primary; no copied code before decision | code reuse, distribution |
| Q-03 | First supported hosts | Linux only; Linux+WSL; Linux+Windows+macOS | Linux first, WSL compatibility next; adapters keep other hosts possible | installer, test matrix |
| Q-04 | Default autonomy policy | conservative; balanced; unrestricted | Balanced: reversible workspace actions automatic, external/admin/destructive actions confirmed | permissions, UX |
| Q-05 | Default data posture | fully local; local-first with opt-in cloud; cloud-managed | Local-first with explicit per-backend opt-in | memory, telemetry, routing |
| Q-06 | Supported user profile | individual developer; team; both in v1 | Individual developer v1, schemas team-ready | identity, policy |
| Q-07 | Dashboard commitment | CLI only; CLI+local web UI; native UI | CLI first and local read-only dashboard after contracts stabilize | UI, packaging |

Until resolved, recommendations are planning assumptions, not accepted owner
decisions.

