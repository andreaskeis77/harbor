# Harbor

Harbor is a project-partitioned research and monitoring system.

It is designed to support:

- clearly separated research projects
- versioned research handbooks and scope definitions
- controlled source collection and evidence storage
- review and resume workflows
- refresh and later monitoring/agentic update flows
- one canonical backend for website and Custom GPT

## Current phase

T1.1 — Runtime configuration and local operator surface

## Repository posture

Harbor is moving from documentation baseline into controlled runtime implementation.

The current technical baseline now includes:

- Python package scaffold
- FastAPI bootstrap runtime
- `/healthz` and `/` endpoints
- quality gates
- typed runtime settings
- `.env`-driven configuration
- local operator commands for settings inspection and smoke validation

## Canonical local path

`C:\projekte\Harbor`

## Initial navigation

Read these files in this order:

1. `docs/PROJECT_STATE.md`
2. `docs/MASTERPLAN.md`
3. `docs/INDEX.md`
4. `docs/RUNTIME_CONFIGURATION_v0_1.md`
5. `docs/LOCAL_OPERATOR_SURFACE_v0_1.md`

## Common local commands

Activate the venv first:

```powershell
.\.venv\Scripts\Activate.ps1
```

Show effective runtime settings:

```powershell
python .\tools\task_runner.py show-settings
```

Run local smoke checks without starting a separate shell session:

```powershell
python .\tools\task_runner.py smoke-local
```

Run quality gates:

```powershell
python .\tools\task_runner.py quality-gates
```

Start the local development server:

```powershell
python .\tools\task_runner.py run-dev
```
