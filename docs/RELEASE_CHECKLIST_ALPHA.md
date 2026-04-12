# Harbor — Alpha Release Checklist (Template)

Version-agnostic checklist for cutting a new alpha release. Substitute the
target tag (`vX.Y.Z-alpha`) throughout.

## Preconditions

- `main` is green on CI / locally
- working tree is clean
- docs are synchronized with the delivered work
- no open schema drift (`alembic upgrade head` is a no-op after pull)
- the last handoff under `docs/_handoff/` reflects reality

## Release-branch setup

```powershell
git checkout main
git pull
git checkout -b release/vX.Y.Z-alpha
```

## Artefacts to update

1. `pyproject.toml` — bump `version` to the alpha PEP-440 form (e.g. `0.3.0a0`).
2. `README.md` — `Current phase`, `Release baseline`, `Start here`, `Current metrics`.
3. `.env.example` — reflect any new/renamed settings; keep SQLite-on-VPS
   posture documented.
4. `CHANGELOG.md` — new section for the release; follow Keep-a-Changelog
   shape. Group by Added / Changed / Fixed / Engineering notes.
5. `docs/RELEASE_NOTES_vX_Y_Z_alpha.md` — human-readable release notes;
   summarize user-visible changes, call out upgrade notes, list known
   limitations.
6. `docs/PROJECT_STATE.md` — update `Historical release baseline` and the
   `Active next implementation slice` block.

## Validation block

```powershell
Set-Location 'C:\projekte\Harbor'
.\.venv\Scripts\Activate.ps1
python -m alembic upgrade head
python -m pytest -q
python .\tools\task_runner.py quality-gates

# Smoke slices — run the set relevant to the phase being released.
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

git status --short   # must be empty
```

Green pytest without green quality-gates is not enough. Both must pass.

## Commit, tag, release

```powershell
git add -A
git commit -m "Release: vX.Y.Z-alpha (one-line summary)"
git push -u origin release/vX.Y.Z-alpha
# Open PR, squash-merge to main.

# After merge, on main:
git checkout main
git pull
git tag -a vX.Y.Z-alpha -m "Harbor vX.Y.Z-alpha"
git push origin vX.Y.Z-alpha
```

GitHub Release: create an entry for the tag and paste the content of
`docs/RELEASE_NOTES_vX_Y_Z_alpha.md` as the body.

## After release

- Verify a fresh clone at the tag: `pip install -e .[dev]`,
  `alembic upgrade head`, `pytest -q` all green.
- Confirm `CHANGELOG.md` and `README.md` reflect the new release baseline.
- Write the next handoff under `docs/_handoff/` if the release closes a phase.
- Point the next work stream — feature bolts, VPS deployment, or runbooks —
  at the documented next step.
