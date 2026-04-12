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
- T5.2A — operator action: draft handbook entry from chat
- H5.0A / H5.0B — source-review workflow + handbook version history in the operator web shell
- H5.1A / H5.1B / H5.1C — operator/chat JS and CSS extracted to static assets
- T6.0A — automation task registry (observability baseline)
- T6.0B — side-channel observer (failures survive rollback)
- C.1 — collapsible operator section-cards (localStorage-persisted)
- C.2 — automation task log surface on project-detail

T5 is feature-complete; H5 hardening is done; T6 observability baseline is in place; UX consolidation has two of four bolts delivered.

Next:
- **T6.1** — second automation call-site through the observer pattern, or
- **C.3 / C.4** — remaining UX consolidation bolts (unified status feedback, review queue consolidation)

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
- `/chat` is an inspectable, persisted operator chat surface with source grounding.

### T5 — source-grounded knowledge and operator actions (COMPLETE)
Goal:
- ground chat in Harbor's curated knowledge (sources + handbook)
- provide explicit operator action surfaces from chat context

Delivered:
- T5.0A: enriched source context in chat prompt (relevance, trust_tier, review_status)
- T5.0B: source citation in assistant responses (`[N]` extraction, inline badges)
- T5.1A: handbook context in chat prompt (truncated at 2000 chars)
- T5.1B: propose source from chat (convenience endpoint + UI form)
- T5.2A: draft handbook from chat (save assistant output as handbook version)

### T6 — deeper automation
Only after operator surfaces are complete:
- search campaign execution automation
- background task infrastructure
- monitoring/observability for automated workflows (**T6.0A / T6.0B delivered the observability baseline**)
- stricter agent patterns

Delivered so far:
- T6.0A: `automation_task_registry` + migration + API + `draft-handbook` instrumented as the first call-site
- T6.0B: side-channel observer so failures survive rollback; `session.rollback()` in the failure path releases SQLite write locks

Open in T6:
- T6.1: second call-site (e.g. `propose-source` from chat) to validate the observer pattern generalizes
- T6.2+: actual automation drivers (scheduler, executor) on top of the observability baseline

## Candidate intermediate phases

### H5 — T5 hardening (COMPLETE)
Delivered:
- H5.0A: source review workflow in web shell
- H5.0B: handbook version history in web shell
- H5.1A/B/C: operator/chat JS and CSS extracted to `src/harbor/static/`

### UX consolidation (partial)
Delivered:
- C.1: collapsible operator section-cards with per-operator localStorage persistence
- C.2: automation task log panel on project-detail (makes T6.0A visible)

Open:
- C.3: unified status/toast feedback (replaces scattered `data-*-status` mounts)
- C.4: review queue as a central pending-actions view
- (future) chat session management (archive, delete, export)

## Delivery discipline

Each bolt should remain:
- small
- repo-consistent
- locally validated
- explicitly merged before the next bolt starts

Do not continue from an unverified reconstructed slice.
Use `origin/main` as the canonical baseline for every new bolt.
