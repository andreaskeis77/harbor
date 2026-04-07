# Harbor

Harbor is a project-partitioned research and monitoring system.

It is designed to support:

- clearly separated research projects
- versioned research handbooks and scope definitions
- controlled source collection and evidence storage
- review and resume workflows
- refresh and later monitoring or agentic update flows
- one canonical backend for website and Custom GPT

## Current phase

T1.0 — Repository scaffold and technical bootstrap implementation

## Repository posture

Harbor started documentation-first and now enters the first technical bootstrap phase.

The current implementation goal is intentionally narrow:

- establish the canonical repository scaffold
- provide a minimal FastAPI application
- provide a `/healthz` endpoint
- establish local bootstrap commands
- establish minimal quality gates
- prepare the next vertical slice for Projects plus Handbook

## Local repository root

Canonical local path:

`C:\projekte\Harbor`

## Recommended reading order

1. `docs/MASTERPLAN.md`
2. `docs/PROJECT_STATE.md`
3. `docs/PRODUCT_SCOPE_v0_1.md`
4. `docs/DOMAIN_MODEL_v0_1.md`
5. `docs/SYSTEM_ARCHITECTURE_v0_1.md`
6. `docs/TECHNICAL_BOOTSTRAP_v0_1.md`

## Quickstart

### Create virtual environment

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### Run the quality gates

```powershell
python .\tools\run_quality_gates.py
```

### Start the local API

```powershell
python -m uvicorn harbor.app:app --host 127.0.0.1 --port 8000 --reload
```

### Smoke-check the app

```powershell
Invoke-RestMethod http://127.0.0.1:8000/healthz
```

Expected response includes `status: ok`.

## Canonical directories

- `src/` — application code
- `tests/` — automated checks
- `tools/` — operational helpers and quality-gate tooling
- `config/` — environment examples and config notes
- `docs/` — product, architecture, governance, handoffs
- `data/` — local non-canonical data zone
- `var/` — logs, run artifacts, reports
