# Harbor Masterplan

Status: Active planning baseline  
Owner: Andreas / Harbor repo  
Purpose: Preserve the long-range Harbor plan inside the repository

---

## 1. Why this file exists

Harbor will be developed over multiple chats, handoffs, and implementation cycles.

This file exists so that the project does not lose:

- its phase order
- its strategic priorities
- its current recommended sequence
- its explicit deferred topics
- its transition logic between planning and implementation

The masterplan is the long-range roadmap.
It is not the same as day-to-day project state.

---

## 2. Core planning model

Harbor uses three persistent planning layers:

### 2.1 Masterplan
`docs/MASTERPLAN.md`

Holds:
- long-range direction
- phase sequence
- strategic priorities
- major deferred topics
- phase entry and exit criteria

### 2.2 Project State
`docs/PROJECT_STATE.md`

Holds:
- current accepted phase
- validated state
- real next step
- active risks
- open questions

### 2.3 Handoffs
`docs/_handoff/HANDOFF_*.md`

Hold:
- what was changed
- what was verified
- what was not verified
- which files were involved
- what the next bolt is

---

## 3. Strategic product target

Harbor is a project-partitioned research operating system.

It is not just a chat tool and not just a vector database.

Its strategic target is:
- clearly separated research projects
- a versioned research handbook per project
- controlled source and evidence management
- repeatable review and resume workflows
- later refresh, discovery, monitoring, and agentic support
- one canonical backend for website and Custom GPT

---

## 4. Planning sequence

## A0 — Planning and definition baseline

Goal:
Create a stable product and architecture baseline before runtime implementation.

Scope:
- product scope
- domain model
- user stories
- functional requirements
- handbook model
- blueprint model
- workflow model
- system architecture
- runtime boundaries
- technical bootstrap definition

Exit condition:
- planning baseline is present in repo
- naming and terminology are stable enough
- implementation entry point is clear
- T1.0 scope is small and explicit

## A0 consolidation gate

Goal:
Do not move into implementation with an ambiguous document surface.

Required outcome:
- know which A0 documents are officially accepted
- remove or flag contradictions
- identify the exact first implementation bolt

Exit condition:
- A0 accepted baseline is documented
- T1.0 start package is explicit

## T1.0 — Technical bootstrap implementation

Goal:
Create the first real Harbor runtime skeleton.

Expected contents:
- repository scaffold
- Python project bootstrap
- app entrypoint skeleton
- config surface
- health endpoint
- first tests
- initial quality gate posture

Exit condition:
- Harbor starts locally
- basic tests pass
- commands are reproducible
- no major ambiguity about runtime layout remains

## T1.1 — Runtime and configuration baseline

Goal:
Stabilize environment, configuration, and start modes.

Expected contents:
- settings model
- `.env` handling
- local runtime commands
- clear dev startup path

## T1.2 — Persistence baseline

Goal:
Introduce canonical database posture.

Expected contents:
- Postgres connection model
- schema/migration baseline
- first persistence layer
- minimal durable data model entrypoint

## T1.3 — Minimal application API

Goal:
Create the first stable Harbor application surface.

Expected contents:
- `/healthz`
- minimal API routing
- minimal project-facing app boundary

## T2.0 — First vertical product slice

Goal:
Deliver the first end-to-end Harbor use case.

Recommended first slice:
- create project
- list projects
- open project
- store handbook text
- view handbook history or first version state

Why this slice first:
- it validates project partitioning
- it creates real system of record behavior
- it supports both website and GPT later

## T2.1 — Source model baseline

Goal:
Introduce project-linked source handling.

Expected contents:
- source
- project source
- manual source intake
- minimal review status
- source snapshot concept in code

## T2.2 — Search and refresh baseline

Goal:
Move from static project memory toward active research behavior.

Expected contents:
- first search campaign representation
- manual refresh trigger
- change/delta candidate handling
- basic review queue logic

## T2.3 — Web UI baseline

Goal:
Provide the first real operator-facing Harbor interface.

Expected contents:
- project list UI
- project detail UI
- handbook view/edit path
- source overview view

## T2.4 — Custom GPT integration baseline

Goal:
Connect GPT to Harbor without splitting the truth surface.

Expected contents:
- GPT action surface
- project selection
- handbook/state retrieval
- safe write actions

## T3.x — VPS and durable operations

Goal:
Run Harbor as a controlled system outside the development laptop.

Expected contents:
- VPS deployment model
- health checks
- logs
- backups
- runbook
- preview release and smoke test

## T4.x — Monitoring and agentic extensions

Goal:
Extend Harbor from manual research memory toward governed monitoring.

Expected contents:
- scheduled refresh
- discovery campaigns
- candidate queues
- alerts
- later agentic support with strict review boundaries

---

## 5. Current recommended sequence

The currently recommended sequence is:

1. finish A0 governance and baseline control
2. consolidate and accept A0 planning surface
3. implement T1.0 bootstrap
4. stabilize T1.1/T1.2 runtime and persistence
5. build T2.0 first vertical slice
6. only then broaden into sources, search, UI, GPT, VPS, and monitoring

---

## 6. Explicitly deferred topics

These topics are important, but not early-core priorities:

- multi-user collaboration and permissions
- unrestricted autonomous agents
- heavy scraping of protected login content
- advanced inheritance between blueprints and derived projects
- enterprise workflow features
- broad automation before review and provenance controls are stable

---

## 7. Planning rules

### 7.1 The repo is the memory
Do not rely on chat history for long-range continuity.

### 7.2 Project state must stay honest
Prepared artifacts are not the same as accepted baseline.

### 7.3 Implementation should follow explicit entry criteria
Do not start a runtime tranche until the previous planning gate is stable enough.

### 7.4 Every major bolt updates three layers
Each meaningful bolt should update:
- `docs/MASTERPLAN.md`
- `docs/PROJECT_STATE.md`
- a new `docs/_handoff/HANDOFF_*.md`

---

## 8. Masterplan review trigger

This file should be reviewed whenever one of these occurs:
- major change in product direction
- change in recommended phase order
- new architectural constraint
- decision to accelerate or defer a large capability
- preparation for a handoff to a new chat or work context

---

## 9. Immediate next planning checkpoint

Immediate recommended checkpoint:
- confirm actual accepted A0 baseline in repo
- then define the exact T1.0 implementation package
