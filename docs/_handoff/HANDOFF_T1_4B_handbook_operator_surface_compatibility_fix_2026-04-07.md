# HANDOFF T1.4B — Handbook operator-surface compatibility fix

Status: Ready for apply  
Date: 2026-04-07  
Phase: T1.4B

## What this fix does

This fix repairs the T1.4A stabilization regression where `tools/task_runner.py` could no longer import
`database_status_for_operator` and `show_db_settings_payload` from `harbor.operator_surface`.

It also keeps the Windows-safe handbook smoke cleanup behavior and stabilizes the db-status test against
an inherited `HARBOR_SQLALCHEMY_DATABASE_URL` environment variable.

## Files included

- `src/harbor/operator_surface.py`
- `tests/test_db_status.py`

## Expected local proof after apply

- `python .\tools\task_runner.py smoke-handbook-slice` works
- `python .\tools\task_runner.py quality-gates` is green
- `python -m alembic upgrade head` works
- live handbook HTTP endpoints work again when the dev server runs with the SQLite dev URL
