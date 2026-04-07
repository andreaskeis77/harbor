# Harbor Masterplan

## Purpose

This document is the long-lived roadmap for Harbor.

It is the canonical reference for:
- phase sequence
- strategic priorities
- what is deferred
- transition gates between phases

## Product direction

Harbor is a project-partitioned research operating system.

It is not only a chat experience and not only a vector-search feature set.
It is a governed system for:
- project definition
- source collection
- evidence storage
- review
- resume
- refresh
- later monitoring and agentic assistance

## Phase sequence

### A0 — Definition and architecture baseline
Goal:
- product, domain, architecture, workflow, and bootstrap definition

Status:
- accepted

### T1.0 — Repository scaffold and technical bootstrap
Goal:
- canonical repository structure
- minimal FastAPI application
- health endpoint
- local bootstrap
- minimal tests and quality gates

Status:
- current phase

### T1.1 — Runtime configuration and local operator surface
Goal:
- stronger runtime settings
- local operator commands
- local start-run conventions
- clearer environment handling

### T1.2 — Persistence foundation
Goal:
- database posture starts to become executable
- schema bootstrap
- migration posture
- canonical persistence boundaries

### T1.3 — Minimal application surface
Goal:
- first project-facing API surface
- likely project list, project create, and handbook baseline

### T2.x — First vertical functional slices
Goal:
- Projects
- Handbook versions
- project dashboards
- then Sources
- then Search and Refresh
- then Review and Resume

### VPS preview phase
Goal:
- stable deployable preview environment
- health and restart posture
- operator runbook

### GPT integration phase
Goal:
- same backend used by website and Custom GPT
- first stable actions surface

### Monitoring and Agent phase
Goal:
- controlled refresh automation
- later candidate-producing agents
- never unchecked write access into canonical knowledge

## Rules for roadmap changes

Any major roadmap change must update:
- `docs/MASTERPLAN.md`
- `docs/PROJECT_STATE.md`
- one new `docs/_handoff/HANDOFF_*.md`
