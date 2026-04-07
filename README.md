# Harbor

Harbor is a project-partitioned research and monitoring system.

It is designed to support:

- clearly separated research projects
- versioned research handbooks and scope definitions
- controlled source collection and evidence storage
- review and resume workflows
- refresh and later monitoring/agentic update flows
- search campaign registry baseline
- one canonical backend for website and Custom GPT

## Current phase

T1.5 — Source and project-source first slice

## Repository posture

Harbor is now beyond documentation-only bootstrap.

The current repository contains:

- accepted A0 product and architecture baseline
- runtime bootstrap and local operator surface
- persistence foundation and Postgres baseline
- first real vertical product slice for project registration
- second real vertical product slice for handbook persistence and version history
- first global source + project-source attachment slice

## Local repository root

Canonical local path:

`C:\projekte\Harbor`

## Initial navigation

Read these files in this order:

1. `docs/MASTERPLAN.md`
2. `docs/PROJECT_STATE.md`
3. `docs/INDEX.md`
4. `docs/SOURCE_SLICE_v0_1.md`
5. `docs/_handoff/HANDOFF_T1_5_source_and_project_source_first_slice_2026-04-07.md`

## Local commands

```powershell
.\.venv\Scripts\Activate.ps1
python .	ools	ask_runner.py show-settings
python .	ools	ask_runner.py show-db-settings
python .	ools	ask_runner.py quality-gates
python .	ools	ask_runner.py smoke-project-slice
python .	ools	ask_runner.py smoke-handbook-slice
python .	ools	ask_runner.py smoke-source-slice
python .	ools	ask_runner.py run-dev
```

## Current proof points

- `/healthz`
- `/runtime`
- `/db/status`
- `/api/v1/projects` (when a DB URL is configured)
- `/api/v1/projects/{project_id}/handbook` (when a DB URL is configured)
- `/api/v1/sources` (when a DB URL is configured)
- `/api/v1/projects/{project_id}/sources` (when a DB URL is configured)
