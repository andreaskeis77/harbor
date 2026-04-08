# Harbor – Release Checklist Alpha v0.1

Target release: `v0.1.0-alpha`

## Preconditions
- `main` is green
- working tree is clean
- docs are synchronized
- no open schema drift

## Validation block
```powershell
Set-Location 'C:\projekte\Harbor'
.\.venv\Scripts\Activate.ps1
python -m alembic upgrade head
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
python .\tools\task_runner.py quality-gates
git status --short
```

## Release notes should mention
- manual operator flow from project to source
- duplicate guard behavior
- workflow summary surface
- out-of-scope items deferred beyond alpha

## Tagging
Suggested tag:
- `v0.1.0-alpha`

## After release
- create a GitHub release entry
- attach concise release notes
- keep next-step plan pointed at external search execution and/or operator UX improvements
