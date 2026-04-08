# Harbor – Alpha Operator Runbook v0.1

Audience: local operator  
Release target: `v0.1.0-alpha`

## 1. Start local environment
```powershell
Set-Location 'C:\projekte\Harbor'
.\.venv\Scripts\Activate.ps1
python -m alembic upgrade head
python .\tools\task_runner.py quality-gates
```

## 2. Optional smoke verification
```powershell
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
```

## 3. Run the API
```powershell
python .\tools\task_runner.py run-dev
```

## 4. Manual workflow
1. Create a project
2. Create a search campaign inside the project
3. Create one or more search runs
4. Add search result candidates to each run
5. Promote chosen candidates to the review queue
6. Promote accepted review-queue items to sources
7. Read the workflow summary to confirm current counts and lineage

## 5. Core endpoints
- `POST /api/v1/projects`
- `POST /api/v1/projects/{project_id}/search-campaigns`
- `POST /api/v1/projects/{project_id}/search-campaigns/{search_campaign_id}/runs`
- `POST /api/v1/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/{search_run_id}/result-candidates`
- `POST /api/v1/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/{search_run_id}/result-candidates/{search_result_candidate_id}/promote-to-review`
- `POST /api/v1/projects/{project_id}/review-queue-items/{review_queue_item_id}/promote-to-source`
- `GET /api/v1/projects/{project_id}/workflow-summary`

## 6. Expected operator behavior
- do not create duplicate candidates with the same intent unless deliberately testing alternative runs
- use promotion endpoints instead of creating review/source records manually
- use workflow summary as the main control view before and after promotion actions

## 7. Known non-goals in alpha
- no real web-search execution
- no scheduling
- no agentic workflow automation
- no advanced deduplication merge logic
