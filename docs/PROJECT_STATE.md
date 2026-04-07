# Project State

## Current phase

T1.6B — Review queue baseline

## Confirmed completed

- A0 baseline accepted
- T1.0 runtime bootstrap
- T1.1 runtime configuration and local operator surface
- T1.2 persistence foundation and Postgres baseline
- T1.3 project registry vertical slice
- T1.4 handbook persistence baseline
- T1.5 first global source + project-source slice
- T1.6A search campaign registry baseline
- T1.6B review queue baseline

## Current runtime posture

Harbor now has:

- running FastAPI runtime
- local operator commands
- DB status surface
- persistence foundation with SQLAlchemy + Alembic baseline
- project registry
- handbook version registry
- source registry
- project-source attachment registry
- live project and handbook APIs
- live source attach/list APIs
- live search campaign APIs
- live review queue APIs

## Confirmed local proof for T1.6B

Expected green proof after apply:

- `python .\tools\task_runner.py smoke-project-slice`
- `python .\tools\task_runner.py smoke-handbook-slice`
- `python .\tools\task_runner.py smoke-source-slice`
- `python .\tools\task_runner.py smoke-search-campaign-slice`
- `python .\tools\task_runner.py smoke-review-queue-slice`
- `python .\tools\task_runner.py quality-gates`
- `python -m alembic upgrade head`
- `/api/v1/projects/{project_id}/review-queue-items` works when a DB URL is configured

## Recommended next step

T1.7A — Search run registry baseline


Recommended next step

T1.7A — Search Run Registry Baseline
