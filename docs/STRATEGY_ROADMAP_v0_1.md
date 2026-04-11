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

T5 is feature-complete as originally scoped.

Next:
- Planning phase: T5 hardening (H5) or T6 automation baseline

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
- monitoring/observability for automated workflows
- stricter agent patterns

## Candidate intermediate phases

### H5 — T5 hardening
Before T6, harden the T5 deliverables:
- stale doc catch-up
- operator_web.py structural cleanup (CSS/JS extraction)
- handbook version history in operator web shell
- source review workflow in web shell

### UX consolidation
Before deeper automation:
- unified operator dashboard
- source review status changes in web shell (currently API-only)
- chat session management (archive, delete, export)

## Delivery discipline

Each bolt should remain:
- small
- repo-consistent
- locally validated
- explicitly merged before the next bolt starts

Do not continue from an unverified reconstructed slice.
Use `origin/main` as the canonical baseline for every new bolt.
