# Harbor

Harbor is a project-partitioned research and monitoring system.

## Current phase
Phase P4 complete — **refresh & error recovery**: manual fetch-now, snapshot history inline, staleness + fetch-error signals on the overview.
Release cut as `v0.3.0-alpha` (VPS-deployment baseline).
Next: VPS deployment (local-on-VPS first, then decide on public reach). Feature bolts (P5 cite-back, cross-project dedup, P6 automated search) deferred until deploy is accepted.

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
- source-grounded chat with enriched metadata and citation extraction
- handbook context injection in chat prompt
- operator action: propose source from chat
- operator action: draft handbook entry from chat
- source-review workflow available inside the operator web shell
- handbook version history surface in the operator web shell
- operator JS and CSS extracted to `src/harbor/static/` (operator.js, chat.js, operator.css)
- **automation task registry + API** (observability baseline for automation-triggered work)
- **side-channel observer pattern** — failures are recorded even when the request transaction rolls back
- **collapsible operator section-cards** with per-operator localStorage persistence
- **automation task log panel** on project-detail (kind / trigger / status / timestamps / result-or-error)

## Release baseline
- `v0.3.0-alpha` — current baseline: snapshot pipeline + scheduler + content activation + refresh/error recovery; VPS-deployment-ready with SQLite
- `v0.2.0-alpha` — scheduler + snapshot baseline (T6/T7 + U1–U6 operator UX primitives)
- `v0.1.0-alpha` — manual operator flow baseline

See [CHANGELOG.md](CHANGELOG.md) for version history and [docs/RELEASE_NOTES_v0_3_0_alpha.md](docs/RELEASE_NOTES_v0_3_0_alpha.md) for current release notes.

## Local repository root
Canonical local path:
- `C:\projekte\Harbor`

## Start here
1. `docs/MASTERPLAN.md`
2. `docs/PROJECT_STATE.md`
3. `docs/STRATEGY_ROADMAP_v0_1.md`
4. `docs/WORKING_AGREEMENT.md`
5. `docs/VALIDATION_PROTOCOL.md`
6. `docs/_handoff/HANDOFF_2026-04-12_P4_to_next.md`

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
- `/api/v1/openai/projects/{project_id}/propose-source`
- `/api/v1/openai/projects/{project_id}/draft-handbook`
- `/api/v1/projects/{project_id}/automation-tasks`
- `/api/v1/automation-tasks/{automation_task_id}`

## Current metrics
- 291 tests, 95.55% coverage (70% gate enforced)
- 14 Alembic migrations (linear chain, integrity-tested)
- 14 ORM models
- typed domain exceptions, middleware exception handlers
- request-scoped transaction middleware (commit-on-success/rollback-on-error)
- side-channel observer pattern for observability across rollback
- structured request logging with request-id propagation
- expanded Ruff lint rules: E, F, I, B, UP, SIM, PIE, LOG, RUF
- 24 permanent engineering manifest rules
