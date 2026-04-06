# Harbor Masterplan

Status: Active planning baseline  
Current control point: **A0.C1 — A0 consolidation and baseline freeze preparation**

---

## 1. Purpose

This document is the long-lived masterplan for Harbor.

It is the canonical place for the overall sequence of work across chats.
It is not the detailed current-state log and it is not a handoff substitute.

Use:

- `PROJECT_STATE.md` for the actual current accepted state
- `docs/_handoff/HANDOFF_*.md` for local tranche handoffs
- this file for the long-range sequence and decision frame

---

## 2. Product direction

Harbor is a project-partitioned research operating system.

Its long-term target posture is:

- project-based research spaces
- versioned research handbooks
- source and evidence governance
- review and resume capability
- refresh and discovery capability
- later monitoring and agentic assistance
- one canonical backend for website and Custom GPT
- VPS-hosted operation with explicit health, logging, and recovery posture

---

## 3. Phase overview

### A0 — Documentation and architecture baseline

Goal:

- define Harbor clearly enough that implementation starts from a controlled target

Main outputs:

- product scope
- domain model
- user stories and functional requirements
- handbook/blueprint/workflow model
- system architecture and runtime boundaries
- technical bootstrap and repository scaffolding concept
- masterplan and handoff governance
- A0 consolidation and acceptance logic

### T1 — Technical bootstrap and first runtime foundation

Goal:

- create the first real runnable repository scaffold and minimal runtime posture

Expected outputs:

- repository scaffold
- Python project baseline
- config surface
- minimal app structure
- health endpoint
- tests and quality-gate seed
- local run commands

### T2 — Core Harbor vertical slices

Goal:

- implement the first durable product slices against the canonical backend

Recommended first slices:

1. Projects
2. Research handbook versioning
3. Project dashboard / resume state
4. Sources and project-source mapping
5. Manual source capture and snapshot basics

### T3 — Search / refresh / review operations

Goal:

- add project-scoped research operations

Expected outputs:

- search campaign model
- refresh run model
- review queue
- delta detection
- candidate handling

### T4 — Website and GPT interaction surface

Goal:

- expose Harbor through both the web UI and the Custom GPT against the same backend

### T5 — VPS preview release

Goal:

- deploy a stable preview environment on the VPS with documented health, start,
  stop, recovery, and smoke-test paths

### T6 — Monitoring and later agentic expansion

Goal:

- add long-running update discovery and monitoring safely

Guardrail:

- agents never write unreviewed findings directly into the canonical accepted
  knowledge layer

---

## 4. Immediate execution order

The currently recommended execution order is:

1. A0.C1 — consolidate A0 and freeze the baseline
2. T1.0 — repository scaffold and technical bootstrap implementation
3. T1.1 — config and runtime foundations
4. T1.2 — persistence and database foundation
5. T1.3 — minimal API surface
6. T2.0 — first vertical slice: projects and handbook
7. T2.1 — sources and project-source mapping
8. T3.x — search / refresh / review operations
9. T4.x — web UI and GPT interaction surface
10. T5.x — VPS preview release
11. T6.x — monitoring and later agentic expansion

---

## 5. Not now

The following are intentionally not immediate priorities:

- multi-user collaboration
- aggressive long-running autonomous agents
- complex login-dependent automation
- enterprise-grade authorization models
- broad generic crawler behavior without review boundaries
- live inheritance between blueprints and derived projects

---

## 6. A0 exit criterion

A0 is considered accepted only when:

- the A0 document set is actually present in the repository
- the A0 document set is reviewed for internal consistency
- the implementation start line for T1.0 is explicit
- `PROJECT_STATE.md` and the latest handoff both reflect the accepted A0 state

---

## 7. Update rule

Every major tranche should update:

- `docs/MASTERPLAN.md`
- `docs/PROJECT_STATE.md`
- one new file under `docs/_handoff/`
