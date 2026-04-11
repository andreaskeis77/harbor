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

## 2026-04-10 method hardening

### Verified base first
Every new bolt or recovery attempt starts from a verified repository base. The default is:
- `git checkout main`
- `git pull --ff-only origin main`

If the work intentionally continues on an unmerged feature branch, that branch must first be reset to its verified pushed state.

### No reconstruction from failed states
Do not continue from guessed intermediate files, partially applied ZIPs, or manually repaired local experiments. Return to the verified base and re-cut the bolt cleanly.

### Small clean bolts, no hidden scope mix
If a bolt is feature-complete but docs/manifests are still missing, finish that documentation work explicitly and visibly. Do not blur a failing product bolt with unrelated local repairs.

### Exact file accountability
Before validation, confirm the artifact changed exactly the intended repository files and no more.

### Existing fixtures before new harnesses
Follow the established test fixture pattern for the relevant surface before adding a new test host or runtime path.
