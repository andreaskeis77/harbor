# HANDOFF — T1.2 Persistence Foundation and Postgres Baseline

Date: 2026-04-07  
Status: Ready for handoff

## What this tranche adds

This tranche moves Harbor from pure runtime bootstrap into persistence readiness.

Added:

- Postgres settings in runtime config
- persistence package boundary
- SQLAlchemy base
- engine / session bootstrap
- DB status service
- `/db/status` route
- Alembic baseline files
- DB-oriented operator commands
- tests for runtime DB settings and DB status behavior
- persistence baseline documentation

## What this tranche does not yet add

Not yet included:

- Harbor domain tables
- project persistence
- handbook persistence
- source persistence
- vector-store/runtime use

## Current verified success criteria

Expected local proof after apply:

- `python .\tools\task_runner.py show-db-settings` works
- `python .\tools\task_runner.py db-status` works
- `python .\tools\task_runner.py quality-gates` is green
- `/db/status` is reachable when the dev server is running

## Recommended next step

T1.3 — Project registry vertical slice
