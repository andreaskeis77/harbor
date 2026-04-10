# Harbor Masterplan

## Product direction
Harbor is a project-partitioned research operating system, not a generic chat-RAG.

The sequence stays:

- A0 — accepted product / architecture / governance baseline
- T1 — local technical bootstrap and manual operator flow baseline
- T2 — operator web surface
- T3 — OpenAI adapter and dry-run surfaces
- T4 — chat surface and operator-facing chat hardening
- T5 — source-grounded knowledge and operator action surfaces
- T6 — deeper automation / monitoring evolution

## Current accepted state

Accepted:

- A0 baseline
- T1.0 runtime bootstrap
- T1.1 runtime configuration and local operator surface
- T1.2 persistence foundation and Postgres baseline
- T1.3 project registry vertical slice
- T1.4 handbook persistence baseline
- T1.5 source / project-source first slice
- T1.6A search campaign registry baseline
- T1.6B review queue baseline
- T1.7A search run registry baseline
- T1.7B search result candidate baseline
- T1.8 candidate-to-review promotion
- T1.9 review-queue-to-source promotion
- T1.10 duplicate guards for promotion flow
- T1.11 workflow summary and lineage surface
- T1.12 docs + runbook + release hygiene
- T1.13 `v0.1.0-alpha` release cut
- T2.0A operator web shell read surface
- T2.1A operator promote actions in web shell
- T2.1B manual create actions in web shell
- T2.2A operator UX/API hardening
- T3.0A OpenAI adapter baseline
- T3.0B OpenAI project dry-run surface
- T3.1A operator web shell OpenAI dry-run panel
- T3.1B persisted OpenAI dry-run log history
- T4.0A chat surface baseline
- T4.0B persisted chat sessions and turns
- T4.1A project-grounded multi-turn chat context hardening
- T4.1B chat turn context inspection panel
- T4.2A chat session title/status UX hardening
- T4.2B chat error/retry UX hardening
- T4.3A chat composer / instructions UX split
- T4.3B chat instructions preset/default UX hardening
- T4.4A chat turn rendering density/readability hardening
- T4.4B selected-turn diff/compare readability hardening

## Current focus
- T4.5A project-source-grounded chat baseline

## Phase intent

### T1
Establish the canonical backend, persistence foundation, manual research workflow, and alpha release baseline.

### T2
Expose the backend through an operator web shell while keeping the web layer thin and API-only.

### T3
Establish a clean, testable OpenAI integration seam and operator-visible dry-run surfaces before broader chat behavior.

### T4
Build a thin chat surface on the canonical backend, add persistence for sessions/turns, then harden readability and operator UX.

### T5
Ground the chat in Harbor knowledge and begin controlled operator action surfaces, starting with project sources and later handbook/action handoff.

## T4 current sequence

### T4.0A
- chat page baseline
- project selector
- single-message send through existing dry-run path
- transient in-browser history only

### T4.0B
- persisted chat sessions
- persisted chat turns
- load/continue sessions in `/chat`

### T4.1A
- multi-turn context hardening
- bounded prior-turn inclusion
- compaction metadata

### T4.1B
- selected-turn context inspection panel

### T4.2A
- session title/status UX hardening

### T4.2B
- chat error/retry UX hardening

### T4.3A
- chat composer / instructions UX split

### T4.3B
- instructions preset/default UX hardening

### T4.4A
- dense, readable per-turn rendering

### T4.4B
- selected-turn diff/compare readability hardening

### T4.5A
- project-source-grounded chat baseline
- include project sources in adapter-side prompt context
- expose project-source grounding metadata in request payload
- no new persistence
- no new automation
- no new broad UI surface

## Explicit non-goals right now

Not now:

- autonomous tool orchestration
- automated search execution
- handbook synthesis from chat without explicit operator action
- vector/embedding subsystem
- multi-user collaboration
- background agents

## Transition rule

Every accepted slice updates:

- `README.md`
- `docs/MASTERPLAN.md`
- `docs/PROJECT_STATE.md`
- `docs/INDEX.md`
- `docs/_handoff/HANDOFF_*.md`

For Harbor, docs are not commentary. They are part of the operable system.

## 2026-04-10 validated branch update

Validated on branch `bolt/t4-5a-project-source-grounded-chat-baseline-v2`:
- T4.5A is complete and locally green.
- Chat turns are now grounded in accepted project sources.
- The next planned product bolt remains `T4.5B — source attribution / source visibility in chat`.

Methodically, this update also hardens Harbor delivery discipline: complete artifacts, verified bases, root-cause analysis after red applies, and no further patching on top of a broken artifact.
