# Project State

## Current phase
T5.0A — enriched source context in chat prompt

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
- T1.12 docs + runbook + release hygiene
- T1.13 `v0.1.0-alpha` release cut
- T2.0A operator web shell read surface
- T2.1A operator action buttons
- T2.1B manual create actions
- T2.2A operator UX/API hardening
- T3.0A OpenAI adapter baseline
- T3.0B OpenAI project dry-run surface
- T3.1A operator web shell OpenAI dry-run panel
- T3.1B persisted OpenAI dry-run log history
- T4.0A chat surface baseline
- T4.0B persisted chat sessions and chat turns
- T4.1A multi-turn context hardening
- T4.1B chat turn context inspection panel
- T4.2A chat session title/status UX hardening
- T4.2B chat error/retry UX hardening
- T4.3A chat composer/instructions UX split
- T4.3B chat instructions preset/default UX hardening
- T4.4A chat turn rendering density/readability hardening
- T4.4B selected-turn diff/compare readability hardening
- T4.5A project-source-grounded chat baseline
- T4.5B source attribution / source visibility in chat

## Current runtime posture

Harbor now has:

- FastAPI runtime
- DB status surface
- canonical persistence layer with SQLAlchemy + Alembic
- **consolidated linear migration chain** (10 migrations, single `migrations/` path)
- **structured request logging with request-id propagation**
- **global exception handler with traceable error responses**
- manual operator research workflow
- operator web shell under `/operator/...`
- OpenAI runtime/probe adapter surface
- project dry-run surface
- persisted dry-run logs
- chat surface under `/chat`
- persisted project-scoped chat sessions and turns
- bounded multi-turn project-grounded context
- selected-turn inspection and compare readability surface
- richer chat UX for session state, retry behavior, composer/instructions handling, and density/readability
- **centralized test fixtures in `tests/conftest.py`**
- **migration integrity tests (chain linearity, table completeness, ORM parity)**
- **typed domain exception hierarchy (`HarborError` → `NotFoundError`, `DuplicateError`, `NotPromotableError`, `InvalidPayloadError`)**
- **middleware-based exception-to-HTTP-status translation (no HTTPException in routes)**
- **request-scoped transaction middleware (commit-on-success, rollback-on-error)**
- **pytest-cov coverage quality gate (70% minimum threshold)**
- **coverage excludes CLI-only operator surfaces**
- **expanded Ruff lint rules: E, F, I, B, UP, SIM, PIE, LOG, RUF**
- **observability verification: structured log output tests, error log tests**
- **error-path tests: 503 DatabaseNotConfigured, config redaction, connectivity errors**
- **alembic fileConfig fix: `disable_existing_loggers=False`**
- **82 tests, 95% coverage** (H3)
- **116 tests, 96% coverage** (H4)
- **117 tests, 96% coverage** (T4.5B)
- **119 tests, 96% coverage** (T5.0A)
- **validation edge-case tests for all review-queue registry branches**
- **Pydantic input-constraint boundary tests (422 rejection)**
- **E2E workflow lifecycle test (project → campaign → run → candidate → review → source)**
- **source_attribution persisted per chat turn** (JSON: source_id, project_source_id, title, URL, note)
- **source attribution visible in chat UI** (compact badge in history, collapsible detail in inspector)
- **enriched source context in chat prompt** (relevance, trust_tier, review_status rendered per source)

## Current proof surfaces

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

## Validation rule

A Harbor bolt is not merge-ready until:

- targeted pytest is green
- relevant smoke slices are green
- `python .\tools\task_runner.py quality-gates` is green

Green tests without green quality gates are not enough.

## Historical release baseline

- `v0.1.0-alpha` remains the last explicitly documented alpha release baseline
- current `main` is substantially ahead of that point

## Active next implementation slice

T5.0A — enriched source context in chat prompt (in progress)

Scope:

- `_prepare_project_sources()` now extracts `relevance`, `trust_tier`, `review_status` from project-source and source data
- `_project_sources_lines()` renders structured metadata bracket `[relevance=..., trust=..., review=...]` per source
- `source_attribution` entries include enriched metadata fields
- backend-only change: no UI, no persistence, no migration
- 2 new unit tests, enriched assertions on existing integration test
- 119 tests, 96% coverage, quality gates green

## Intentionally not yet in scope

- autonomous tool orchestration
- automated search execution
- handbook synthesis without explicit operator action
- vector retrieval subsystem
- multi-user features

## 2026-04-10 validated branch state

Validated branch: `bolt/t4-5a-project-source-grounded-chat-baseline-v2`

Confirmed completed on this branch:
- T4.5A — project-source-grounded chat baseline

Delivered in T4.5A:
- accepted project sources are injected into chat turn grounding
- rendered input now includes a dedicated `Project sources` prompt section
- request metadata now records `project_source_count_available` and `project_source_count_included`
- no-source cases are rendered explicitly as `(no accepted project sources available)`
- the existing prior-turn compaction behavior remains intact

Validated locally with:
- `python -m pytest tests/test_openai_adapter_api.py -q`
- `python .\tools\task_runner.py smoke-source-slice`
- `python .\tools\task_runner.py smoke-openai-adapter-slice`
- `python .\tools\task_runner.py smoke-openai-chat-session-slice`
- `python .\tools\task_runner.py smoke-chat-surface-slice`
- `python .\tools\task_runner.py quality-gates`

Documented follow-up from this bolt:
- lessons learned captured
- delivery and validation protocols hardened
- next product bolt remains `T4.5B` after merge
