# Repository Scaffolding v0.1

Status: Draft baseline for technical bootstrap
Phase: A0.6
Scope: Initial Harbor repository layout before runtime implementation

## 1. Purpose

This document defines the recommended first repository scaffold for Harbor.

It is not a claim that every directory must be fully populated immediately.
It is a statement about the structure the project should grow into from the first implementation bolt onward.

## 2. Recommended top-level layout

```text
Harbor/
├─ docs/
│  ├─ _handoff/
│  ├─ adr/
│  └─ concepts/
├─ src/
├─ tests/
├─ tools/
├─ config/
├─ var/
│  ├─ logs/
│  ├─ runs/
│  ├─ reports/
│  └─ cache/
├─ data/
│  ├─ artifacts/
│  ├─ exports/
│  └─ tmp/
├─ .venv/
├─ README.md
└─ .gitignore
```

## 3. Directory intent

### 3.1 `docs/`

Purpose:
- product definition
- architecture
- runbooks
- handoffs
- ADRs
- concepts

### 3.2 `src/`

Purpose:
- application code
- package modules
- app startup
- config loading
- future domain and service layers

### 3.3 `tests/`

Purpose:
- unit tests
- smoke tests
- contract tests
- later integration tests

### 3.4 `tools/`

Purpose:
- developer helpers
- validation commands
- repo checks
- future bootstrap and operational scripts

### 3.5 `config/`

Purpose:
- tracked config templates
- local/dev config examples
- future runtime config contracts

### 3.6 `var/`

Purpose:
- runtime-generated files that are not canonical product content

Subdirectories:
- `logs/`
- `runs/`
- `reports/`
- `cache/`

### 3.7 `data/`

Purpose:
- local development artifact storage and exports where required

Subdirectories:
- `artifacts/`
- `exports/`
- `tmp/`

Note:
Longer-term artifact storage may later move partly outside the repo root by environment policy, but the scaffold should document the contract clearly from the beginning.

## 4. Minimum files expected in the first implementation bolt

The first implementation bolt should create at least a minimal set such as:

- `src/harbor/__init__.py`
- `src/harbor/app.py`
- `src/harbor/config.py`
- `tests/test_import_smoke.py`
- `tests/test_health_smoke.py`
- `config/README.md`
- `tools/README.md`

The exact filenames may evolve, but the first bolt should stay close to this level of simplicity.

## 5. Naming and package posture

Recommended package posture:

- package root under `src/harbor/`
- clear entrypoint naming
- avoid ambiguous top-level script sprawl
- prefer explicit module names over generic placeholders

## 6. Repo cleanliness rules

The scaffold should support the following hygiene rules:

- runtime-generated files do not mix with tracked product docs
- durable docs do not mix with temp exports
- tests do not live inside application code
- helper scripts do not silently become production runtime
- local-only secrets remain outside tracked files

## 7. First `.gitignore` implications

The repository should continue ignoring at least:

- virtual environment directories
- Python cache files
- runtime logs
- temp exports
- local env files
- local database or secret material where applicable

## 8. Intentional omissions

The scaffold does not yet require:

- final frontend structure
- scheduler process layout
- worker split
- migration tool choice
- containerization layout
- CI workflow details

These may come later, after T1.x runtime proof exists.

## 9. Exit criteria

The scaffold baseline is ready when:

- the directory plan is explicit
- each top-level folder has a stated purpose
- the first implementation bolt can create files without structural ambiguity
- future runtime and ops additions have clear placement rules
