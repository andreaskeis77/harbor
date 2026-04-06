# Technical Bootstrap v0.1

Status: Draft baseline for first implementation entry
Phase: A0.6
Scope: Minimal technical starting posture before the first runtime bolt

## 1. Purpose

This document defines the minimum technical bootstrap target for Harbor.

It answers a narrow but important question:

**What must exist before Harbor starts real implementation work?**

The goal is not to overbuild. The goal is to create a stable, inspectable, repeatable first technical footing.

## 2. Design goals

The first technical bootstrap must satisfy the following goals:

1. **Deterministic local development**
   - one canonical local repo root
   - one clear startup path
   - one small validation path

2. **Minimal but real structure**
   - enough structure to support implementation
   - not so much structure that the repo becomes ceremony-heavy

3. **Separation before growth**
   - docs, source, tests, tools, runtime data, and temporary artifacts should not be mixed

4. **Future-safe storage posture**
   - early bootstrap must already respect the architecture choice of Postgres + pgvector + artifact store

5. **Explicit non-goals**
   - the first technical bolt must not pretend to deliver product completeness

## 3. Canonical local posture

Canonical local repository root:

`C:\projekte\Harbor`

Expected local development posture in the first implementation phase:

- Windows-first development
- VS Code as primary editor
- PowerShell as standard shell
- Git-based workflow
- local Python virtual environment
- documentation and runtime code kept in the same repository

## 4. Minimum technical surfaces for T1.0

The first implementation tranche should introduce only the following technical surfaces.

### 4.1 Source tree baseline

A first durable source tree with at least:

- `src/`
- `tests/`
- `tools/`
- `config/`
- `var/`
- `data/` or documented external artifact root contract
- runtime bootstrap files

### 4.2 Python package root

A minimal Harbor Python package or application root that makes later imports, tests, and app startup explicit.

### 4.3 App entrypoint skeleton

A basic app entrypoint, expected to target a future FastAPI service surface.

The first version may expose only:

- a simple application object
- a health endpoint or equivalent health command
- minimal startup wiring

### 4.4 Configuration contract

A small, explicit configuration surface should exist from the beginning.

It should define at least:

- environment name
- database connection target
- artifact root
- log root
- app host/port defaults

### 4.5 Health posture

The bootstrap must include a minimal health surface.

Examples:

- `/healthz`
- a CLI health command
- or both

The purpose is not observability completeness. The purpose is to create an early, repeatable runtime proof.

### 4.6 Test posture

A first minimal test posture must exist.

It should include at least:

- import smoke
- config smoke
- app/health smoke
- one clearly documented test command

### 4.7 Validation posture

A first lightweight validation path should exist before full quality gates are introduced.

Examples:

- basic import check
- basic test run
- optional lint smoke
- health startup smoke

## 5. What T1.0 must not include

The first technical bootstrap should intentionally avoid the following:

- complete project domain implementation
- source ingestion engine
- full review workflow implementation
- complete database schema set
- full authentication or authorization model
- production-grade scheduler
- full web frontend
- full GPT action surface
- autonomous monitoring agents

## 6. Initial runtime shape

The intended first runtime shape is deliberately small:

- one application process
- one explicit config surface
- one health proof path
- one minimal test path
- one documented startup command

This is enough to validate the technical skeleton before meaningful product behavior is added.

## 7. Storage implications

Even before full implementation, T1.0 should respect the accepted storage posture.

That means the bootstrap should anticipate:

- Postgres as canonical relational state
- pgvector as part of semantic retrieval support
- filesystem-based artifact storage
- logs and runtime evidence kept separate from durable product data

The first bolt does not need to create all database objects, but it should not choose a conflicting posture.

## 8. Bootstrap deliverables for T1.0

Recommended deliverables:

- repository scaffold
- initial package files
- config skeleton
- FastAPI app skeleton
- health endpoint
- startup instructions
- first tests
- first run/validation instructions
- project state and handoff update

## 9. Exit criteria

T1.0 technical bootstrap is successful when:

- the repo has the agreed scaffold
- the app can start in a minimal form
- a health proof exists
- the first technical validation command succeeds
- docs reflect the actual bootstrap state
- the next implementation target is explicit

## 10. Leads into next phase

This document directly leads into:

**T1.0 — Repository scaffold and technical bootstrap implementation**
