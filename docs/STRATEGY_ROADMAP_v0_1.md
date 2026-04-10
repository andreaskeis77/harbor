# Harbor Strategy Roadmap v0.1

## Purpose
This roadmap turns Harbor development into an ordered release path instead of an open-ended feature stream.

## Guiding idea
Harbor should grow in this order:

1. canonical backend
2. operator usability
3. LLM integration seam
4. thin chat surface
5. source-grounded knowledge
6. explicit operator actions
7. deeper automation only after the earlier layers are stable

## Current status snapshot

Completed through:
- T4.4B — selected-turn diff/compare readability hardening

Next:
- T4.5A — project-source-grounded chat baseline

## Phase roadmap

### A0 — accepted baseline
Goal:
- product scope
- domain model
- architecture/governance baseline

### T1 — manual operator flow baseline
Goal:
- canonical runtime
- persistence
- manual research workflow
- `v0.1.0-alpha` baseline

Outcome:
- Harbor can manage projects, sources, campaigns, runs, candidates, review queue, promotion flow, and workflow summary.

### T2 — operator web shell
Goal:
- thin browser surface over the canonical APIs
- operator read/actions without backend bypass

Outcome:
- `/operator/...` is usable and hardened.

### T3 — OpenAI adapter and dry-run
Goal:
- clean OpenAI seam before broader chat behavior
- runtime/probe surfaces
- project dry-run
- persisted dry-run history

Outcome:
- Harbor can exercise the model in a controlled, inspectable way.

### T4 — chat surface
Goal:
- thin chat surface on the canonical backend
- persisted sessions/turns
- bounded multi-turn grounding
- readable operator UX

Outcome:
- `/chat` is now an inspectable, persisted operator chat surface.

### T4.5 — source-grounded chat
Goal:
- move from project-only grounding to project-plus-source grounding

First slice:
- T4.5A — include accepted project sources in chat context

Expected benefit:
- answers become grounded in the same curated sources Harbor already stores.

### T5 — operator action surfaces
Goal:
- convert grounded chat output into explicit Harbor actions

Likely first slices:
- handbook/notes drafting from selected chat output
- explicit save/transfer action from chat to handbook/project notes
- source-attributed response rendering

### T6 — deeper automation
Only after T5 is stable:
- broader workflow automation
- search/discovery refresh automation
- stricter monitoring/agent patterns

## Delivery discipline

Each bolt should remain:
- small
- repo-consistent
- locally validated
- explicitly merged before the next bolt starts

Do not continue from an unverified reconstructed slice.
Use `origin/main` as the canonical baseline for every new bolt.
