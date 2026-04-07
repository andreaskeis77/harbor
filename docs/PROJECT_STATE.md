# Project State

## Current phase

T1.4 — Handbook persistence baseline

## Confirmed completed

- A0 baseline accepted
- T1.0 runtime bootstrap
- T1.1 runtime configuration and local operator surface
- T1.2 persistence foundation and Postgres baseline
- T1.3 first vertical slice for project registration
- T1.3A stabilization fix for project-slice smoke and route/style compliance
- T1.4 handbook persistence baseline

## Current runtime posture

Harbor now has:

- running FastAPI runtime
- local operator commands
- DB status surface
- persistence foundation with SQLAlchemy + Alembic baseline
- first persisted product entity: project registry
- second persisted product entity: handbook version registry
- create/list/get project API
- read/write current handbook API
- handbook version history API
- stabilized smoke commands for project and handbook slices

## Confirmed local proof for T1.4

Expected green proof after apply:

- `python .\tools\task_runner.py quality-gates`
- `python .\tools\task_runner.py smoke-project-slice`
- `python .\tools\task_runner.py smoke-handbook-slice`
- `/api/v1/projects/{project_id}/handbook` works when a DB URL is configured
- `/api/v1/projects/{project_id}/handbook/versions` works when a DB URL is configured

## Current recommended next step

T1.5 — Source and project-source first slice

## Notes

Harbor now persists the two central foundation objects needed before broader workflow work:
- `Project`
- handbook versions per project

This is intentionally still narrow:
- no sources yet
- no search campaigns yet
- no UI yet
- no GPT integration yet
