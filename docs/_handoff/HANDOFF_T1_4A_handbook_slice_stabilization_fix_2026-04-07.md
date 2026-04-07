# HANDOFF T1.4A — Handbook slice stabilization fix

Status: Ready for apply  
Phase: T1.4A  
Date: 2026-04-07

## Why this fix exists

Two issues were observed during the live validation of T1.4:

1. `smoke-handbook-slice` failed on Windows during temporary SQLite cleanup.
2. `tests/test_db_status.py` inherited `HARBOR_SQLALCHEMY_DATABASE_URL` from the operator shell and therefore asserted the wrong status.

## What changed

- `src/harbor/operator_surface.py`
  - hardened the temporary SQLite smoke flows for Windows
  - switched smoke flows to best-effort temp cleanup
  - ensured runtime modules are reset around temporary DB usage
- `tests/test_db_status.py`
  - explicitly clears `HARBOR_SQLALCHEMY_DATABASE_URL` for the not-configured test

## Expected result after apply

- `python .\tools\task_runner.py smoke-handbook-slice` passes
- `python .\tools\task_runner.py quality-gates` is green
- no more Windows cleanup failure in the handbook smoke path

## Commit recommendation

Apply this fix on top of the current uncommitted T1.4 working tree, then commit T1.4 once the slice is green.
