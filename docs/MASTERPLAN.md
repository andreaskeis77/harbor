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
- T4.5A project-source-grounded chat baseline
- T4.5B source attribution / source visibility in chat
- T5.0A enriched source context in chat prompt
- T5.0B source citation in assistant responses
- T5.1A handbook context in chat

## Current focus
- T5.1A — handbook context in chat (in progress)

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

### T4.5B
- source attribution / source visibility in chat
- persist source_attribution JSON on each chat turn (Alembic migration)
- expose source_attribution in chat turn API response (source_id, project_source_id, title, URL, note)
- chat history: compact source badge per turn
- inspector panel: collapsible source attribution detail section
- no new automation
- no new broad UI surface

## T5 current sequence

### T5.0A
- enriched source context in chat prompt
- `_prepare_project_sources()` extracts `relevance`, `trust_tier`, `review_status`
- `_project_sources_lines()` renders structured metadata bracket per source
- source_attribution includes enriched fields
- backend-only change (no UI, no persistence, no migration)
- 2 new unit tests, enriched assertions on existing integration test

### T5.0B
- source citation in assistant responses
- prompt engineering: citation instruction appended when sources are present
- rendered source section includes "Cite sources by number" instruction
- post-processing: `_extract_source_citations()` extracts `[N]` references from output
- `cited_sources` field in chat turn payload (computed, not persisted)
- UI: inline citation badges with hover title in assistant messages
- 4 new unit tests, enriched assertions on 4 existing tests

### T5.1A
- handbook context in chat
- load current handbook version for the project during chat turn construction
- inject handbook content as knowledge layer in the chat prompt (between project context and sources)
- `_prepare_handbook_context()` with truncation at `MAX_HANDBOOK_CHARS = 2000`
- `_handbook_context_lines()` renders handbook section with placeholder when absent
- handbook metadata in `request_metadata` (`handbook_available`, `handbook_chars`, `handbook_truncated`)
- no new persistence, no UI changes
- 6 new unit tests, enriched assertions on 2 existing tests

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

## H1 — Phase 1 hardening (2026-04-11)

Cross-cutting hardening bolt inserted between T4.5A and T4.5B.

### H1 scope
- consolidated migration chain (single `migrations/` path, linear chain, no branches)
- migration integrity tests (upgrade-head, chain-linearity, ORM-model parity)
- structured application logging (`harbor.*` logger hierarchy)
- request-logging middleware (method, path, status, duration, request-id)
- global exception handler (500 with traceable request-id)
- centralized test fixtures (`tests/conftest.py`)
- stale configuration cleanup (`config/.env.example`, orphaned `alembic/`)
- engineering manifest hardening with new permanent rules

### H1 rationale
External project review identified that Harbor's functional core was solid but the non-functional foundation (migration integrity, observability, test maintainability) had silent gaps that could compound into operational failures. This hardening bolt addresses those gaps before further feature work.

## H2 — Phase 2 hardening (2026-04-11)

Continuation of cross-cutting hardening, focusing on architecture resilience.

### H2 scope
- typed domain exception hierarchy (`HarborError` → `NotFoundError`, `DuplicateError`, `NotPromotableError`, `InvalidPayloadError`)
- all 8 registry files migrated from string-based `KeyError`/`ValueError` to typed exceptions
- all 8 route files cleaned: no `HTTPException`, no `try/except KeyError`, no `_translate_*` helpers
- middleware exception handlers map domain types to HTTP status codes centrally
- request-scoped transaction middleware: `get_db_session` owns commit/rollback boundary
- all 16 `session.commit()` calls in registries converted to `session.flush()`
- `DatabaseNotConfiguredError` replaces the last `HTTPException` in `session.py`
- `pytest-cov` added with 60% coverage quality gate in `pyproject.toml`
- 6 new tests for exception mapping and transaction atomicity
- engineering manifest updated with 4 new permanent rules

### H2 rationale
Phase 1 established observability and test infrastructure but the error handling remained fragile: 48 string-based `KeyError` raises, 17 string-pattern matches in routes, and no transactional safety at the request boundary. Phase 2 replaces this with a typed, middleware-driven architecture that is both safer and easier to extend.

## H3 — Phase 3 hardening (2026-04-11)

Continuation of cross-cutting hardening, focusing on test depth, observability verification, and lint safety.

### H3 scope
- coverage gate raised from 60% to 70%, CLI operator surfaces excluded (95% effective coverage)
- 17 new tests: error-path tests (503, config redaction, connectivity), observability tests (structured log output, error tracing), middleware handler mapping tests
- status module hardened: structured logging for DB connectivity errors
- Ruff expanded from 4 rule sets to 9: `E, F, I, B, UP, SIM, PIE, LOG, RUF`
- alembic `env.py` fixed: `fileConfig(disable_existing_loggers=False)` prevents logger contamination
- validation protocol updated with H2/H3 checks section
- engineering manifest updated with 4 new permanent rules

### H3 rationale
Phase 2 established the exception hierarchy and transaction middleware but left error paths untested, logging output unverified, and the lint rule set too narrow. Phase 3 closes these gaps: every middleware handler has a test, structured logging is verified end-to-end, and the expanded lint rules catch modernization issues (UP), complexity anti-patterns (SIM), logging misuse (LOG), and Python-specific pitfalls (RUF). A critical discovery was that alembic's `fileConfig()` was silently disabling all Harbor loggers — now fixed and tested.

## H4 — Phase 4 hardening (2026-04-11)

Continuation of cross-cutting hardening, focusing on validation depth, input boundaries, and end-to-end workflow testing.

### H4 scope
- quality-gates runner: `compileall` step added for `tools/` directory
- expanded endpoint tests: `/runtime` and `/healthz` structure verification
- 17 new review-queue validation edge-case tests covering all uncovered branches (84% → 97% coverage)
- 15 new Pydantic input-validation boundary tests verifying 422 rejection for `min_length`, `max_length`, `ge` constraints
- 1 comprehensive E2E workflow lifecycle test: project → campaign → run → candidate → review promotion → source promotion with full state-transition and lineage verification
- engineering manifest updated with 4 new permanent rules
- validation protocol updated with H4 checks section

### H4 rationale
Phases 1-3 established infrastructure, architecture, and error-path testing. Phase 4 completes the testing pyramid: validation edge cases in the deepest registry functions, input constraint enforcement at the API boundary, and a full pipeline E2E test that verifies the entire research workflow operates as a coherent system. This catches regression risks that isolated unit and integration tests cannot: cross-entity ownership mismatches, disposition state machines, and duplicate-guard interactions across promotion stages.
