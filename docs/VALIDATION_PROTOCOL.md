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

## 2026-04-10 recovery and apply discipline

### Required sequence after a generated artifact
1. verify the intended git base
2. apply the artifact
3. inspect the changed-file set
4. run the smallest relevant targeted tests
5. run the relevant smokes
6. run `python .\tools\task_runner.py quality-gates`
7. only then commit and push

### Recovery rule after failure
If any of apply, import, tests, smokes, or quality-gates fail, stop and perform root-cause analysis from a verified clean base. The next artifact must be re-cut from that base rather than patched on top of the broken state.

### Merge-ready rule
A bolt is merge-ready only when the changed file set is understood, the relevant checks are green, and the state/documentation have been updated to match reality.
