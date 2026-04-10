# Harbor Validation Protocol

## Goal
Validation distinguishes discussion, preparation, local confirmation, and accepted repository state.

## Validation levels

### Discussed
An idea exists, but no artifact baseline exists.

### Prepared
Files exist, but they have not yet been applied onto a branch cut from a freshly fast-forwarded `main`.

### Applied
Files were applied onto a local branch that was cut from verified `main`.

### Validated
The applied branch passed the relevant local checks.

Minimum expectation:
- targeted `pytest`
- relevant smoke slices
- `python .\tools\task_runner.py quality-gates`

### Accepted
The validated branch is merged into `origin/main`.

## Canonical-state rule
For Harbor, accepted state means:
- merged into GitHub `origin/main`

A local branch with green checks is not yet accepted.
A discussed plan is not yet prepared.
A prepared artifact is not yet validated.

## Failure rule
If `quality-gates` is red, the bolt is not merge-ready even if:
- targeted tests are green
- smoke slices are green

In that case:
- isolate the exact blocker
- fix the smallest possible surface
- rerun the same validation chain
- only then continue

## T4 expected checks
For current Harbor chat/operator work, typical validation is:

```powershell
python -m pytest tests\test_operator_web_shell.py tests\test_openai_adapter_api.py
python .\tools\task_runner.py smoke-chat-surface-slice
python .\tools\task_runner.py smoke-openai-chat-session-slice
python .\tools\task_runner.py quality-gates
```
