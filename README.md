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

T1.2 — Persistence foundation and Postgres baseline

## Repository posture

Harbor is now in the early runtime bootstrap phase.

The repository currently contains:

- accepted A0 documentation baseline
- runtime configuration baseline
- local operator surface
- FastAPI bootstrap runtime
- persistence foundation and Postgres baseline
- quality gates and local smoke paths

## Local repository root

Canonical local path:

`C:\projekte\Harbor`

## Initial navigation

Read these files in this order:

1. `docs/MASTERPLAN.md`
2. `docs/PROJECT_STATE.md`
3. `docs/INDEX.md`
4. `docs/PERSISTENCE_FOUNDATION_v0_1.md`
5. `docs/POSTGRES_BASELINE_v0_1.md`

## Dev quickstart

```powershell
.\.venv\Scripts\Activate.ps1
python .\tools\task_runner.py show-settings
python .\tools\task_runner.py show-db-settings
python .\tools\task_runner.py quality-gates
python .\tools\task_runner.py run-dev
```
