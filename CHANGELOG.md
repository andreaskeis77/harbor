# Changelog

All notable changes to Harbor are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to a pragmatic semver variant: `MAJOR.MINOR.PATCH[-preid]`.
Alpha releases track internal phase deliveries; breaking changes between alpha
minors are permitted until the first non-alpha release.

## [0.3.0-alpha] — 2026-04-12

VPS-deployment-ready baseline. No schema changes since `v0.2.0-alpha`; this
release consolidates the snapshot pipeline, activates snapshot content in chat
grounding, and adds operator-facing refresh + error-recovery surfaces.

### Added — Content activation (Phase P3)
- `GET /projects/{pid}/project-sources/{psid}/snapshots` + `.../snapshots/latest`
  (P3.1). Cross-project access returns 404.
- "Latest snapshot" column on the project-sources table with inline
  lazy-loading details (P3.2).
- Chat grounding embeds an up-to-600-char excerpt of the latest successful
  snapshot per accepted project source; `project_source_snapshot_count_included`
  and `_truncated` reported in request metadata (P3.3).
- `overview.totals.project_sources_stale_count` + per-project
  `stale_snapshot_count` (14-day threshold; never-fetched web_page sources
  count as stale). New "Stale snapshots" column on `/operator/overview` (P3.4).

### Added — Refresh & error recovery (Phase P4)
- `POST /projects/{pid}/project-sources/{psid}/fetch-now`: synchronous
  operator-initiated refetch using the same httpx helper as the scheduler;
  writes a `SourceSnapshotRecord` including error cases; 422 for non-web_page
  or URL-less sources; does NOT route through the automation-task observer
  (P4.1).
- Snapshot history inline details on project-sources rows (up to 10 most
  recent snapshots via the list endpoint) (P4.2).
- `overview.totals.project_sources_fetch_error_count` + per-project
  `fetch_error_count` (based on latest-snapshot `fetch_error`). New "Fetch
  errors" column on `/operator/overview` (P4.3).
- Fetch-now operator button on project-sources rows (web_page + canonical_url
  only) (P4.4).

### Changed
- `README.md` release baseline reflects v0.3.0-alpha; start-here pointer
  updated to the current handoff.
- `.env.example` documents SQLite as the v0.3.0-alpha default (VPS:
  `C:/Harbor/var/harbor.db`, port 8100). Postgres marked as deferred
  alternative.
- Release checklist renamed from `RELEASE_CHECKLIST_ALPHA_v0_1.md` to
  `RELEASE_CHECKLIST_ALPHA.md` and made version-agnostic (template form).

### Engineering notes
- 291 tests, 95.55% coverage. 14 Alembic migrations, 14 ORM models.
- No schema migrations in P3/P4; everything builds on `source_snapshot` from
  T7.0 (`v0.2.0-alpha`).
- "Latest snapshot per project_source" uses a GROUP BY + JOIN-back pattern
  (not window functions) for SQLite + Postgres portability. Load-bearing on
  staleness and fetch-error overview metrics.

## [0.2.0-alpha] — 2026-04-12

Scheduler and snapshot baseline. Established the infrastructure on which the
v0.3.0-alpha content-activation and refresh surfaces rest.

### Added — Automation and scheduler (Phase T6)
- Automation task registry + API with state machine
  (pending → running → succeeded|failed) (T6.0A).
- Side-channel observer pattern: failures are recorded even when the request
  transaction rolls back (T6.0B).
- `propose-source` instrumented through the observer (T6.1).
- Workflow-summary snapshot automation driver: first non-mutating observer
  call-site (T6.2).
- Handbook-freshness-check automation driver: second non-mutating observer
  call-site (T6.3).
- Minimal scheduler primitive: schedule table, handler registry,
  externally-triggered tick (T6.4).
- First project-less automation driver (`stale_source_sweep` via new
  `GLOBAL_SCHEDULE_HANDLERS` registry) (T6.5).

### Added — Snapshot pipeline (Phase T7)
- `source_snapshot` model + migration + registry CRUD (T7.0). FK to
  `project_source_registry`; fields `fetched_at`, `http_status`,
  `content_hash`, `extracted_text`, `fetch_error`.
- `fetch_source_content` per-project scheduler handler: httpx-based, 10s
  timeout + 2 MiB cap, 5 web_page sources per tick, never-fetched-first
  priority; writes `SourceSnapshotRecord` even on error (T7.1).
- `source_content_staleness_check` per-project non-mutating driver (T7.2).
- Optional in-process scheduler tick loop (`EmbeddedSchedulerLoop`, off by
  default, feature-flagged via `HARBOR_SCHEDULER_EMBEDDED`) (T7.3).

### Added — Operator UX primitives (U1–U6)
- Server-side pagination primitive (`harbor.pagination`;
  `limit`/`offset`/`total` on automation-tasks, review-queue-items,
  search-result-candidates, chat-turns, scheduler/recent-tasks) (U1).
- Cross-entity search primitive (`GET /api/v1/search`; ILIKE across project
  title/desc, source title/url, handbook markdown/change_note, chat turn
  input/output) (U2).
- Sortable operator tables (generic `table.sortable` module;
  localStorage-persisted per table) (U3).
- Bulk review-queue status endpoint with partial-success response (U4).
- Operator overview dashboard (`GET /api/v1/overview`,
  `/operator/overview`) (U5).
- Handbook version diff viewer (`GET
  /projects/{pid}/handbook/versions/{target}/diff`; stdlib
  `difflib.unified_diff`) (U6).

### Added — UX consolidation (Phase C)
- Unified toast/status primitive replaces scattered inline mounts (C.3).
- Cross-project pending-actions queue (API + operator page) (C.4).
- Automation task kind/status filter controls on project-detail task log (C.5).
- Operator scheduler page (`/operator/scheduler`: enable, interval, save,
  one-click tick) (C.6).
- Scheduler tick-outcome surface (`GET /scheduler/recent-tasks` + "Recent
  scheduled runs" table) (C.7).

## [0.1.0-alpha] — 2026-04-07

Manual operator flow baseline. First explicitly documented alpha release.

### Added
- A0 baseline accepted (product, domain, architecture).
- FastAPI runtime, DB status surface, healthz.
- Persistence foundation with SQLAlchemy 2.0 + Alembic, Postgres baseline.
- Project registry, handbook, source + project-source, search campaign,
  review queue, search run, search result candidate slices.
- Candidate → review → source promotion flow with duplicate guards.
- Workflow summary + lineage surface.
- Operator web shell under `/operator/...`.
- OpenAI adapter baseline with project dry-run surface + persisted dry-run
  log history.
- Chat surface under `/chat`; persisted project-scoped chat sessions and
  multi-turn context.
- Chat composer/instructions UX split; preset/default instructions; density
  and readability hardening.
- Project-source-grounded chat; source attribution + citation extraction.
- Handbook context injection in chat prompt.
- Operator actions: propose source from chat, draft handbook entry from chat.
- Source-review workflow and handbook version history in operator web shell.
- Static assets extracted to `src/harbor/static/` (`operator.js`, `chat.js`,
  `operator.css`).

### Engineering baseline
- Typed domain exceptions with middleware-based exception-to-HTTP-status
  translation.
- Request-scoped transaction middleware (commit-on-success,
  rollback-on-error).
- Structured request logging with request-id propagation.
- pytest-cov 70% coverage quality gate; expanded Ruff lint rules
  (E, F, I, B, UP, SIM, PIE, LOG, RUF).
