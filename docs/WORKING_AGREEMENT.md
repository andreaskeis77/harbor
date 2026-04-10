# Harbor Working Agreement

## Basic mode
Harbor is developed with:

- one clear recommendation rather than many weak options
- explicit execution context
- repeatable commands
- visible transition between phases
- as little context as necessary in the chat
- direct instructions instead of broad option trees

## Single source of truth
For Harbor work, the canonical baseline is:

- `origin/main` on GitHub

Operational rule:

1. start every new bolt from local `main`
2. fast-forward local `main` with:
   - `git checkout main`
   - `git pull --ff-only origin main`
3. cut the new branch only after that

If direct GitHub inspection is unavailable, the freshly fast-forwarded local `main` is the working copy of the GitHub source of truth.

Do not continue from:
- reconstructed partial file sets
- stale artifacts
- remembered intermediate states

## Execution contexts
Commands should identify where they belong:

- DEV-LAPTOP
- GitHub in browser
- VPS-USER
- VPS-ADMIN

## Chat to repo rule
The chat may help think, package, and explain.
The repository is the canonical memory.
The repository state outranks chat memory.

## Preferred delivery style
For meaningful changes:

- downloadable ZIP artifact
- unique artifact filename
- canonical repository paths inside the artifact
- exact PowerShell apply commands
- exact git commands
- exact cleanup commands

## Command hygiene
Avoid interactive or ambiguous commands when a non-interactive equivalent exists.

Prefer:
- `git --no-pager diff --stat`
- explicit file-targeted commands
- explicit cleanup commands

Avoid:
- commands that can unexpectedly open pagers
- broad commands that hide which files are affected

## Validation rule
Do not present a bolt as merge-ready until:

- targeted tests are green
- relevant smoke slices are green
- `quality-gates` is green

If any gate is red:
- stop
- isolate the blocker
- fix only that blocker
- rerun validation

## Documentation rule
Docs are part of the system.
If Harbor changes, the docs must move with it.

Minimum update set for a meaningful bolt:
- `README.md`
- `docs/MASTERPLAN.md`
- `docs/PROJECT_STATE.md`
- `docs/INDEX.md`
- one `docs/_handoff/HANDOFF_*.md` when handing over a phase or chat
