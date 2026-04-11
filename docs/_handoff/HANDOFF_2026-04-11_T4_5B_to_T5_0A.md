# Handoff — T4.5B to T5.0A
Stand: 2026-04-11

## Confirmed accepted state

T4.5B merged into `main` via PR #29.
Release baseline: v0.2.0-alpha (H1-H4 quality milestone).

### What T4.5B delivered
- `source_attribution` TEXT column on `openai_project_chat_turn_registry` (migration 0011)
- `_prepare_project_sources()` extracts `source_id`, `project_source_id`, title, canonical_url, note
- `openai_project_chat_turn_payload()` returns `source_attribution` list in response
- `OpenAIProjectChatTurnRead` exposes `source_attribution` (JSON deserialized)
- Chat history: compact source badge per turn (count + titles)
- Inspector panel: collapsible source attribution detail section
- 2 new tests, 117 total, 96% coverage, quality gates green

## Metrics snapshot
- Tests: 117
- Coverage: 96% (gate: 70%)
- Migrations: 11 (linear chain, integrity-tested)
- Engineering manifest rules: 24
- Ruff rule sets: E, F, I, B, UP, SIM, PIE, LOG, RUF

## Accepted bolt history (complete)
- A0 baseline
- T1.0–T1.13: backend foundation, persistence, research workflow, v0.1.0-alpha
- T2.0A–T2.2A: operator web shell (read, promote, create, UX hardening)
- T3.0A–T3.1B: OpenAI adapter, dry-run surface, persisted logs
- T4.0A–T4.5B: chat surface, sessions, multi-turn, inspector, composer, instructions, rendering density, source grounding + attribution
- H1–H4: migration integrity, typed exceptions, transactions, observability, coverage depth, input boundaries, E2E lifecycle

## Architecture context for T5.0A

### Current source flow
1. Sources are created globally (`source_registry`)
2. Linked to projects via `project_source_registry` (with relevance, review_status, note)
3. During chat turn construction, `_accepted_project_sources_for_chat_context()` filters by `review_status == "accepted"`
4. `_prepare_project_sources()` caps to `MAX_PROJECT_SOURCES_IN_CHAT_CONTEXT = 6`, extracts flat text fields + IDs
5. `_project_sources_lines()` renders them as numbered plain text into `rendered_input_text`
6. `source_attribution` persists which sources were included (JSON with IDs + metadata)

### Key files
- `src/harbor/openai_adapter.py` — prompt construction, source preparation, payload building
- `src/harbor/api/routes/openai_adapter.py` — chat turn endpoint, source loading
- `src/harbor/openai_chat_session_registry.py` — turn persistence, read models
- `src/harbor/persistence/models.py` — ORM models
- `src/harbor/source_registry.py` — source/project-source CRUD and read models
- `src/harbor/api/routes/operator_web.py` — chat UI (HTML + JS, ~3700 LOC)
- `tests/test_openai_adapter_api.py` — adapter tests including source grounding + attribution

### Current limitations (T5 opportunities)
- Sources are rendered as flat text — no structured summary with relevance/trust metadata
- No handbook content in chat context
- No way for operator to add sources or create handbook entries from within the chat
- Assistant responses don't reference specific sources (no citation mechanism)
- MAX 6 sources, no prioritization by relevance or trust tier

## T5 roadmap (proposed sequence)

### T5.0A — Enriched source context in chat prompt
- Include `relevance`, `trust_tier`, `review_status` in the rendered source section
- Structured rendering (not just title + URL) so the LLM can reason about source quality
- Backend-only change (adapter prompt construction)
- No new persistence, no UI changes
- Testable via existing adapter test harness

### T5.0B — Source citation in assistant responses
- Prompt engineering to encourage the LLM to cite sources by number/title
- Post-processing to detect and surface source references in output
- UI: render cited sources as linked references in assistant messages

### T5.1A — Handbook context in chat
- Load relevant handbook entries for the project
- Inject as additional knowledge layer in chat prompt
- Similar pattern to source injection

### T5.1B — Operator action: add source from chat
- Operator can submit a URL from within the chat to propose as new source
- Creates source + project_source + review queue item
- Reuses existing promotion flow

### T5.2A — Operator action: draft handbook entry from chat
- Operator can mark a chat response as handbook draft
- Persists as handbook version with explicit operator action
- No auto-synthesis

## Sustainability rules (carry forward)

### Validation protocol (every bolt)
1. Targeted pytest for changed surfaces
2. Relevant smoke slices
3. `python .\tools\task_runner.py quality-gates`
4. Only then commit and push

### Engineering discipline
- Small controlled bolts — one coherent change per bolt
- Start from verified `main` — fresh branch per bolt
- Complete artifacts — all touched layers updated coherently
- Root-cause analysis before next artifact after any red validation
- Use the established test harness — extend `conftest.py`, reuse fakes
- Coverage must never regress (current: 96%, gate: 70%)
- Docs updated with every bolt (MASTERPLAN, PROJECT_STATE, manifest if new rules)
- Lessons learned documented when surprising discoveries occur

### Explicit non-goals (unchanged)
- Autonomous tool orchestration
- Automated search execution
- Handbook synthesis without explicit operator action
- Vector/embedding subsystem
- Multi-user collaboration
- Background agents
