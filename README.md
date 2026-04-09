# Harbor

Harbor is a project-partitioned research and monitoring system.

## Current phase
T2.0 — Operator Web Shell

## Repository posture
Harbor now contains:
- accepted A0 product and architecture baseline
- runtime bootstrap and local operator surface
- persistence foundation and Postgres baseline
- project registry vertical slice
- handbook persistence baseline
- source and project-source slice
- search campaign registry baseline
- review queue baseline
- search run registry baseline
- search result candidate baseline
- candidate-to-review promotion
- review-queue-to-source promotion
- duplicate guards for promotion flow
- workflow summary and lineage surface
- `v0.1.0-alpha` manual operator release cut

## Local repository root
Canonical local path: `C:\projekte\Harbor`

## Release baseline
`v0.1.0-alpha` — manual operator flow

## Current implementation focus
T2.0 introduces the first thin web shell for the existing backend flow.
The shell must stay read-heavy first and must call Harbor APIs only.

## Initial navigation
1. `docs/MASTERPLAN.md`
2. `docs/PROJECT_STATE.md`
3. `docs/INDEX.md`
4. `docs/STRATEGY_ROADMAP_v0_1.md`
5. `docs/RUNBOOK_ALPHA_OPERATOR_v0_1.md`
6. `docs/RELEASE_CHECKLIST_ALPHA_v0_1.md`

## Local commands
```powershell
.\.venv\Scripts\Activate.ps1
python .\tools\task_runner.py show-settings
python .\tools\task_runner.py show-db-settings
python .\tools\task_runner.py quality-gates
python .\tools\task_runner.py smoke-project-slice
python .\tools\task_runner.py smoke-handbook-slice
python .\tools\task_runner.py smoke-source-slice
python .\tools\task_runner.py smoke-search-campaign-slice
python .\tools\task_runner.py smoke-search-run-slice
python .\tools\task_runner.py smoke-search-result-candidate-slice
python .\tools\task_runner.py smoke-review-queue-slice
python .\tools\task_runner.py smoke-candidate-review-promotion-slice
python .\tools\task_runner.py smoke-review-queue-source-promotion-slice
python .\tools\task_runner.py smoke-promotion-duplicate-guard-slice
python .\tools\task_runner.py smoke-workflow-summary-slice
python .\tools\task_runner.py run-dev
```

## Current proof points
- `/healthz`
- `/runtime`
- `/db/status`
- `/api/v1/projects`
- `/api/v1/projects/{project_id}/handbook`
- `/api/v1/sources`
- `/api/v1/projects/{project_id}/sources`
- `/api/v1/projects/{project_id}/search-campaigns`
- `/api/v1/projects/{project_id}/search-campaigns/{search_campaign_id}/runs`
- `/api/v1/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/{search_run_id}/result-candidates`
- `/api/v1/projects/{project_id}/review-queue-items`
- `/api/v1/projects/{project_id}/workflow-summary`

## Latest validated release baseline
T1.13 — `v0.1.0-alpha` release cut
