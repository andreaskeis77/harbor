# Harbor

Harbor is a project-partitioned research and monitoring system.

## Current phase
H4 — Phase 4 hardening complete (validation depth, input boundaries, E2E workflow)
Next: T4.5B — source attribution / source visibility in chat

## Repository posture
Harbor currently contains:

- accepted A0 product and architecture baseline
- runtime bootstrap and local operator surface
- persistence foundation and Postgres baseline
- manual operator research workflow:
  - project
  - source / project-source
  - search campaign
  - review queue
  - search run
  - search result candidate
  - candidate/review/source promotion flow
  - duplicate guards
  - workflow summary and lineage
- operator web shell under `/operator/...`
- OpenAI adapter baseline
- project dry-run surface
- persisted OpenAI dry-run log history
- chat surface under `/chat`
- persisted chat sessions and chat turns
- multi-turn chat context hardening
- chat turn inspection and compare readability surfaces
- chat composer / instructions UX split
- chat instructions preset/default UX

## Release baseline
Historical release baseline:
- `v0.1.0-alpha` — manual operator flow baseline

Current `main` is materially ahead of that alpha baseline.

## Local repository root
Canonical local path:
- `C:\projekte\Harbor`

## Start here
1. `docs/MASTERPLAN.md`
2. `docs/PROJECT_STATE.md`
3. `docs/STRATEGY_ROADMAP_v0_1.md`
4. `docs/WORKING_AGREEMENT.md`
5. `docs/VALIDATION_PROTOCOL.md`
6. `docs/_handoff/HANDOFF_2026-04-10_T4_4B_to_T4_5A.md`

## Standard local commands
```powershell
.\.venv\Scripts\Activate.ps1

python .\tools\task_runner.py show-settings
python .\tools\task_runner.py show-db-settings
python .\tools\task_runner.py quality-gates

python .\tools\task_runner.py smoke-project-slice
python .\tools\task_runner.py smoke-source-slice
python .\tools\task_runner.py smoke-search-campaign-slice
python .\tools\task_runner.py smoke-search-run-slice
python .\tools\task_runner.py smoke-search-result-candidate-slice
python .\tools\task_runner.py smoke-review-queue-slice
python .\tools\task_runner.py smoke-candidate-review-promotion-slice
python .\tools\task_runner.py smoke-review-queue-source-promotion-slice
python .\tools\task_runner.py smoke-promotion-duplicate-guard-slice
python .\tools\task_runner.py smoke-workflow-summary-slice
python .\tools\task_runner.py smoke-operator-web-shell-slice
python .\tools\task_runner.py smoke-openai-adapter-slice
python .\tools\task_runner.py smoke-openai-project-dry-run-slice
python .\tools\task_runner.py smoke-openai-chat-session-slice
python .\tools\task_runner.py smoke-chat-surface-slice
```

## Key surfaces
- `/healthz`
- `/runtime`
- `/db/status`
- `/operator/projects`
- `/operator/projects/{project_id}`
- `/chat`
- `/api/v1/openai/runtime`
- `/api/v1/openai/probe`
- `/api/v1/openai/projects/{project_id}/dry-run`
- `/api/v1/openai/projects/{project_id}/dry-run-logs`
- `/api/v1/openai/projects/{project_id}/chat-sessions`
- `/api/v1/openai/projects/{project_id}/chat-sessions/{chat_session_id}/turns`
- `/api/v1/openai/projects/{project_id}/chat-turns`

## Current next step
T4.5B — source attribution / source visibility in chat

## Hardening status (H1–H4, 2026-04-11)
- 116 tests, 96% coverage (70% gate enforced)
- typed domain exceptions, middleware exception handlers
- request-scoped transaction middleware (commit-on-success/rollback-on-error)
- structured request logging with request-id propagation
- consolidated linear migration chain (10 migrations, 3 integrity tests)
- expanded Ruff lint rules: E, F, I, B, UP, SIM, PIE, LOG, RUF
- validation edge-case tests, input boundary tests, E2E workflow lifecycle test
- 24 permanent engineering manifest rules
