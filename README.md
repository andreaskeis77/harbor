# Harbor

Harbor is a project-partitioned research and monitoring system.

It is designed to support:

- clearly separated research projects
- versioned research handbooks and scope definitions
- controlled source collection and evidence storage
- review and resume workflows
- refresh and later monitoring/agentic update flows
- one canonical backend for website and Custom GPT

## Current phase

T1.4 — Handbook persistence baseline

## Repository posture

Harbor is now beyond documentation-only bootstrap.

The current repository contains:

- accepted A0 product and architecture baseline
- runtime bootstrap and local operator surface
- persistence foundation and Postgres baseline
- first real vertical product slice for project registration
- second real vertical product slice for handbook persistence and version history

## Local repository root

Canonical local path:

`C:\projekte\Harbor`

## Initial navigation

Read these files in this order:

1. `docs/MASTERPLAN.md`
2. `docs/PROJECT_STATE.md`
3. `docs/INDEX.md`
4. `docs/HANDBOOK_PERSISTENCE_v0_1.md`
5. `docs/_handoff/HANDOFF_T1_4_handbook_persistence_baseline_2026-04-07.md`

## Local commands

```powershell
.\.venv\Scripts\Activate.ps1
python .\tools\task_runner.py show-settings
python .\tools\task_runner.py show-db-settings
python .\tools\task_runner.py quality-gates
python .\tools\task_runner.py smoke-project-slice
python .\tools\task_runner.py smoke-handbook-slice
python .\tools\task_runner.py run-dev
```

## Current proof points

- `/healthz`
- `/runtime`
- `/db/status`
- `/api/v1/projects` (when a DB URL is configured)
- `/api/v1/projects/{project_id}/handbook` (when a DB URL is configured)
