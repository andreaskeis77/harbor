# Project State

## Current phase

T1.3A — Project registry stabilization fix

## Confirmed completed

- A0 baseline accepted
- T1.0 runtime bootstrap
- T1.1 runtime configuration and local operator surface
- T1.2 persistence foundation and Postgres baseline
- T1.3 first vertical slice for project registration
- T1.3A stabilization fix for project-slice smoke and route/style compliance

## Current runtime posture

Harbor now has:

- running FastAPI runtime
- local operator commands
- DB status surface
- persistence foundation with SQLAlchemy + Alembic baseline
- first persisted product entity: project registry
- first create/list/get project API
- stabilized smoke command for the project slice

## Confirmed local proof for T1.3A

Expected green proof after apply:

- `python .\tools\task_runner.py quality-gates`
- `python .\tools\task_runner.py db-status`
- `python .\tools\task_runner.py smoke-project-slice`
- `/api/v1/projects` works when a DB URL is configured

## Current recommended next step

T1.4 — Handbook persistence baseline

## Notes

The first real Harbor product object is now in place: `Project`.

This is intentionally still narrow:
- no handbook persistence yet
- no sources yet
- no UI yet
- no GPT integration yet
