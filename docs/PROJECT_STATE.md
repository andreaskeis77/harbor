# Project State

## Current phase
T1.12 — Docs + Runbook + Release Hygiene

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
- T1.7A search run registry baseline
- T1.7B search result candidate baseline
- T1.8 candidate-to-review promotion
- T1.9 review-queue-to-source promotion
- T1.10 duplicate guards for promotion flow
- T1.11 workflow summary and lineage surface

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
- search campaign registry
- search run registry
- search result candidate registry
- review queue registry
- candidate-to-review promotion path
- review-queue-to-source promotion path
- duplicate-guard behavior for promotion flow
- project workflow summary and lineage API

## Confirmed proof for T1.11
- `python -m alembic upgrade head`
- `python .\tools\task_runner.py smoke-project-slice`
- `python .\tools\task_runner.py smoke-handbook-slice`
- `python .\tools\task_runner.py smoke-source-slice`
- `python .\tools\task_runner.py smoke-search-campaign-slice`
- `python .\tools\task_runner.py smoke-search-run-slice`
- `python .\tools\task_runner.py smoke-search-result-candidate-slice`
- `python .\tools\task_runner.py smoke-review-queue-slice`
- `python .\tools\task_runner.py smoke-candidate-review-promotion-slice`
- `python .\tools\task_runner.py smoke-review-queue-source-promotion-slice`
- `python .\tools\task_runner.py smoke-promotion-duplicate-guard-slice`
- `python .\tools\task_runner.py smoke-workflow-summary-slice`
- `python .\tools\task_runner.py quality-gates`

## Release target
`v0.1.0-alpha` — manual operator release

## Intentionally not yet in release scope
- real web search execution
- deduplication merge logic
- scheduling / recurring refresh
- agentic workflows
- UI beyond API/operator surface

## Recommended next step
T1.13 — v0.1.0-alpha release cut
