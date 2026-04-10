# Harbor Handoff — 2026-04-10 — T4.4B to T4.5A

## Purpose
This handoff is the clean restart point for a new Harbor chat after the merged T4.4B state.

## Repo / working root
- GitHub: `https://github.com/andreaskeis77/harbor`
- Local path: `C:\projekte\Harbor`
- Canonical baseline for every new bolt: `origin/main`

## Current accepted state
Merged through:
- T4.4B — selected-turn diff/compare readability hardening

That means Harbor now has:

### Core workflow
- projects
- sources / project-sources
- search campaigns
- search runs
- search result candidates
- review queue
- candidate/review/source promotion flow
- duplicate guards
- workflow summary / lineage

### Operator web shell
- `/operator/projects`
- `/operator/projects/{project_id}`
- read surface
- targeted create/promote actions
- basic operator UX hardening

### OpenAI adapter / dry-run
- runtime/probe
- project dry-run
- persisted dry-run logs
- operator dry-run panel

### Chat surface
- `/chat`
- project selector
- persisted sessions
- persisted turns
- selected-turn inspection
- session metadata UX
- error/retry UX
- message/instructions split
- instructions preset/default UX
- turn density/readability hardening
- selected-turn compare/readability hardening

## Current biggest product gap
Chat is project-grounded and multi-turn aware, but not yet cleanly grounded in Harbor's accepted project sources.

## Next bolt
### T4.5A — project-source-grounded chat baseline

Exact scope:
- load project sources for the chosen project
- include a bounded subset of accepted project sources in adapter-side chat context
- expose source-grounding request metadata
- keep this adapter-side and testable
- no new persistence
- no new automation
- no broad UI expansion

## Working rules for the next chat
1. Treat GitHub `origin/main` as the single source of truth.
2. Start from:
   - `git checkout main`
   - `git pull --ff-only origin main`
3. Only then cut the next branch.
4. Give only the context necessary to execute the next bolt.
5. Prefer one clear recommendation over multiple broad options.
6. Do not continue from reconstructed or remembered partial slices.
7. Do not call a bolt merge-ready unless `quality-gates` is green.

## Standard validation pattern
```powershell
python -m pytest tests\test_operator_web_shell.py tests\test_openai_adapter_api.py
python .\tools\task_runner.py smoke-chat-surface-slice
python .\tools\task_runner.py smoke-openai-chat-session-slice
python .\tools\task_runner.py quality-gates
```

## Suggested new-chat start prompt
```text
Wir machen in Harbor bei T4.5A weiter.
Letzter sauberer Stand: T4.4B ist gemerged.
Nächster Bolt: project-source-grounded chat baseline.

Wichtige Arbeitsregeln:
- GitHub origin/main ist die single source of truth.
- Bitte zuerst den echten Repo-Stand prüfen bzw. lokal main mit origin/main fast-forwarden.
- Danach direkt den kleinsten sauberen Bolt schneiden.
- Bitte nur den nötigen Kontext geben und ansonsten klare Anweisungen, was auf dem DEV-LAPTOP bzw. in GitHub zu tun ist.
- Kein Weiterarbeiten auf rekonstruierten Zwischenständen.
- Kein Merge-Vorschlag ohne grüne quality-gates.

Bitte jetzt T4.5A sauber vorbereiten.
```
