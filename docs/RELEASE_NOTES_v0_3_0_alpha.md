# Harbor v0.3.0-alpha — Release Notes

**Released:** 2026-04-12
**Tag:** `v0.3.0-alpha`
**Previous:** `v0.2.0-alpha`

## Summary

VPS-deployment-ready baseline. Harbor is now operationally complete enough to
run on the Contabo Windows VPS as a single-operator research system: the
snapshot pipeline captures content from accepted web-page sources, that
content flows into chat grounding, operators can see staleness and fetch
errors at a glance, trigger manual refetches, and inspect snapshot history
inline.

No schema changes since `v0.2.0-alpha`. All P3/P4 work builds on the
`source_snapshot` model delivered in T7.0.

## What's new since v0.2.0-alpha

### Content activation (P3)

Snapshots stop being passive storage. The latest successful snapshot per
accepted project source now:

- is readable via `GET /projects/{pid}/project-sources/{psid}/snapshots` +
  `.../snapshots/latest` (P3.1),
- renders inline under a "Latest snapshot" column on the operator
  project-sources table (P3.2),
- is embedded (up to 600 chars per source) into the chat-turn rendered input
  so the model can actually use it (P3.3),
- contributes to a staleness signal on the overview dashboard — 14-day
  threshold, never-fetched web_page sources count as stale (P3.4).

### Refresh & error recovery (P4)

Operators have a closed feedback loop when content goes stale or breaks:

- `POST /projects/{pid}/project-sources/{psid}/fetch-now` fetches the URL
  synchronously using the same httpx helper as the scheduler and writes a
  `SourceSnapshotRecord` including the error case (P4.1).
- Snapshot history is browsable inline on each project-source row (P4.2).
- Fetch-error counts surface on the overview dashboard (P4.3).
- A conditional fetch-now button on project-sources rows triggers P4.1 and
  reloads the page (P4.4).

## VPS deployment posture

This release is explicitly the target for first VPS deployment alongside
Capsule on the Contabo Windows VPS:

- **Database:** SQLite at `C:\Harbor\var\harbor.db` (not Postgres).
- **Bind:** `127.0.0.1:8100` (Capsule reserves 8000).
- **Admin access:** Tailscale-RDP only (no public RDP).
- **Operator UI access:** Tailscale browser access to
  `http://<vps-tailscale-ip>:8100`. No Cloudflare Tunnel, no domain, no
  public reach.
- **OpenAI key:** dedicated key per environment
  (`harbor-vps-prod` distinct from `harbor-dev-local`) with hard monthly
  budget set in the OpenAI console.

Deployment scripts and runbook land in the v0.3.1-alpha (or later) cycle.

## Known limitations (intentionally out of scope)

- No automated search execution (P6 deferred).
- No cite-back from chat citations to specific snapshot IDs (P5 deferred).
- No cross-project source deduplication via `content_hash` (P5-alt
  deferred).
- No bulk fetch-now, no fetch-error inline drilldown, no snapshot-diff
  column (UX polish deferred).
- Single-operator model only — no multi-user, no role-based access.
- SQLite only — Postgres infrastructure exists in config but is not the
  v0.3.0-alpha target.

## Metrics

- 291 tests, 95.55% coverage (70% gate enforced)
- 14 Alembic migrations (linear chain, integrity-tested)
- 14 ORM models
- Quality gates: ruff (9 rule sets) + pytest-cov + compileall

## Upgrade notes (v0.2.0-alpha → v0.3.0-alpha)

No migration required — zero schema delta. Pull, `pip install -e .[dev]`,
`alembic upgrade head` (no-op), restart.

`.env` changes: optional. If you want to be explicit about SQLite, set
`HARBOR_SQLALCHEMY_DATABASE_URL=sqlite+pysqlite:///./var/harbor_dev.db`.
