# Harbor Strategy Roadmap

**Last updated:** 2026-04-12 (after C.6 merge, PR #51)
**Scope:** Supersedes the prior `v0.1` roadmap draft. This is the active planning document for the next large chapter of Harbor development, covering backend, services, database, operator UX, deployment to a Windows VPS, and external-provider (OpenAI) integration.

---

## 1. Purpose

Harbor has outgrown its initial roadmap. The backend is feature-complete for the manual operator flow, T5 and T6-baseline are delivered, and the operator shell is functionally usable. This document reframes Harbor's next phase as an **ordered release path** toward a productively deployable personal research OS on the user's Windows VPS.

---

## 2. Guiding idea (unchanged)

Harbor grows in layers:

1. canonical backend
2. operator usability
3. LLM integration seam
4. thin chat surface
5. source-grounded knowledge
6. explicit operator actions
7. deeper automation only after earlier layers are stable
8. **(new)** productive deployment + intelligence amplification

Layers 1–6 are complete. Layer 7 is partially delivered (T6.0–T6.4 + C.6). Layer 8 is the focus of this roadmap.

---

## 3. State snapshot (2026-04-12)

### Delivered
- **A0, T1.0–T1.13**: canonical backend, manual research workflow, `v0.1.0-alpha` baseline
- **T2.0A–T2.2A**: operator web shell (`/operator/...`)
- **T3.0A–T3.1B**: OpenAI adapter + dry-run surfaces
- **T4.0A–T4.5B**: chat surface with persisted sessions, multi-turn grounding, source attribution
- **T5.0A–T5.2A**: source-enriched chat, citations, handbook context, operator actions (propose source, draft handbook)
- **H5.0A–H5.1C**: source-review workflow, handbook version history, static asset extraction
- **T6.0A–T6.4**: automation task registry, side-channel observer, 2 non-mutating drivers (`snapshot_workflow_summary`, `handbook_freshness_check`), minimal externally-triggered scheduler
- **C.1–C.6**: UX consolidation (collapsible cards, toasts, pending-actions queue, automation-task filters, scheduler operator surface)

### Metrics
- **204 tests, 96% coverage**, 70% gate enforced
- **13 Alembic migrations** (linear chain, integrity-tested)
- **58 API endpoints** across 14 route modules
- **13 ORM models**
- **5 observer call-sites** (`draft-handbook`, `propose-source`, `snapshot_workflow_summary`, `handbook_freshness_check`, scheduler dispatcher)
- Quality gates green: `compileall + ruff (9 rulesets) + pytest --cov`

### What is usable today end-to-end
A single operator can, via browser on `/operator/...` + `/chat`:

1. Manage research projects (create/list/inspect)
2. Manually build search campaigns → runs → candidates
3. Promote candidates → review queue → project sources (one-click)
4. Review-status sources (accepted/rejected)
5. Save handbook versions + see history
6. Overview pending actions cross-project
7. Chat with GPT-5 grounded on project sources + handbook
8. Propose sources / save handbook versions from chat context
9. Observe automation tasks per project, filter by kind/status
10. Enable scheduler handlers, set intervals, fire a tick on demand

### Honest limitations
- No real automation (scheduler is externally-triggered, no background loop)
- No source content (only URLs + metadata; nothing fetched)
- No search/pagination/sorting on tables (unusable at 100+ rows)
- No bulk actions, no diff viewer, no exports
- No auth, no HTTPS posture, no mobile layout
- No dashboard beyond pending-actions
- All data still on local dev box (or SQLite)

---

## 4. Strategic direction (decided)

Three direction decisions made 2026-04-12 that shape all following phases:

| Question | Decision | Consequence |
|---|---|---|
| **A. Ingestion** | A3 chat-assisted initially → A2 second search provider later | P3 adds `suggest_sources_for_project` adapter method; P3 optional second search adapter |
| **B. Source content** | B1 HTTP-fetch + extract as `source_snapshot` | P1 delivers `source_snapshot` model + fetch worker |
| **C. Deployment target** | **Productive on user's Windows VPS** (pivoted from "local-only") | P4 becomes mandatory, not optional; single-token auth required; mobile-friendly layout required; Postgres + Docker-compose deployment required |

---

## 5. Four-phase roadmap

Each phase ends with a tagged release. Each bolt follows the Validation Protocol: Discussed → Prepared → Applied → Validated → Accepted.

### Phase P1 — Source content & scheduling autonomy
**Target release:** `v0.2.0`
**Estimated span:** 4–6 sittings

Harbor gains real content behind its sources and runs scheduled work without an external trigger.

| Bolt | Title | Kind |
|---|---|---|
| **T6.5** | First project-less automation driver (`stale_source_sweep`) | backend |
| **C.7** | Scheduler tick-outcomes surface (last-tick panel + history) | UX |
| **T7.0** | `source_snapshot` model + migration (fetched_at, http_status, extracted_text, content_hash) | DB |
| **T7.1** | `fetch_source_content` scheduler handler (robots.txt-aware, timeout, size cap) | backend |
| **T7.2** | `source_content_staleness_check` driver (marks snapshots > N days old) | backend |
| **T7.3** | Optional in-process tick loop (feature-flag `HARBOR_SCHEDULER_EMBEDDED`, default off) | runtime |

**Operator visibility**: snapshot panel per project source (status, fetched_at, extracted preview); last-tick panel on scheduler page.

---

### Phase P2 — Operator UX for scale
**Target release:** `v0.3.0`
**Estimated span:** 3–4 sittings

Harbor becomes daily-usable even with hundreds of candidates and thousands of chat turns.

| Bolt | Title | Kind |
|---|---|---|
| **U1** | Server-side pagination primitive (`limit`/`offset` on candidates, review-queue, automation-tasks, chat-turns) | backend + UX |
| **U2** | Full-text search (SQLite FTS5 / Postgres tsvector) across projects, sources, handbook, chat-turns | backend + UX |
| **U3** | Sortable tables (header-click, persisted per column) | UX |
| **U4** | Bulk actions on review-queue (select + promote-all / reject-all) | UX |
| **U5** | Operator overview dashboard (`/operator/overview`: pending-actions count, failed tasks, stale sources, last tick, scheduler health) | UX |
| **U6** | Handbook diff viewer (version N vs. N-1, markdown diff) | UX |

---

### Phase P3 — Intelligence amplifier
**Target release:** `v0.4.0`
**Estimated span:** 3–5 sittings

OpenAI integration stops being "chat add-on" and becomes a research accelerator.

| Bolt | Title | Kind |
|---|---|---|
| **I1** | `suggest_sources_for_project` adapter method + operator action (prompt + URL-extraction into candidate batch; operator still promotes explicitly) | backend + UX |
| **I2** | `handbook_synthesis_draft` automation driver (writes into a draft slot; operator must promote to version explicitly — respects the out-of-scope rule) | backend |
| **I3** | Chat-turn regenerate with different model/instructions (no new session required) | UX |
| **I4** | Per-source recap (3-sentence summary, cached on `source_snapshot`) | backend |
| **I5** | Optional second search provider (Tavily or Brave) behind feature flag — delivers A2 ingestion | backend |

---

### Phase P4 — Deploy-readiness (Windows VPS)
**Target release:** `v1.0.0-beta`
**Estimated span:** 2–3 sittings

Harbor runs productively on the user's Windows VPS over HTTPS with single-user auth.

| Bolt | Title | Kind |
|---|---|---|
| **D1** | Single-user API-token auth (header `X-Harbor-Token`, env-driven, bypass for `/healthz`+`/runtime`) | backend |
| **D2** | Responsive CSS pass (breakpoints, touch targets, mobile nav) | UX |
| **D3** | Export: CSV / JSON / Markdown (handbook, sources, review-queue) | backend + UX |
| **D4** | Postgres + Docker-compose deployment posture + documented Windows-VPS deploy walkthrough | ops |
| **D5** | Accessibility pass (focus rings, ARIA labels, keyboard shortcuts: Cmd+Enter to send chat, j/k to navigate turns) | UX |

---

## 6. Release anchors

| Version | Anchor | Content |
|---|---|---|
| `v0.1.0-alpha` | T1.13 | Manual workflow baseline (already shipped) |
| `v0.2.0` | End of P1 | Source content + autonomous scheduler |
| `v0.3.0` | End of P2 | Scales to hundreds of rows; dashboard |
| `v0.4.0` | End of P3 | Real research accelerator |
| `v1.0.0-beta` | End of P4 | Deployed on VPS, mobile-reachable, exportable |
| `v1.0.0` | After beta burn-in on VPS | First production-grade release |

---

## 7. Deployment strategy (Windows VPS)

Harbor will run on the user's Windows VPS once P4 lands. Until then, the VPS can already host the current build with a lighter posture.

### 7.1 Release process

All releases follow the same ritual:

1. **Bolt accepted** on `main` (PR merged, quality gates green)
2. **Tag a release candidate** from `main` (`v0.2.0-rc1`) when a phase completes
3. **Local smoke** on the same tag (Postgres compose-up locally to catch env drift)
4. **Tag final** (`v0.2.0`) after rc passes
5. **Deploy to VPS** by checkout + restart (see 7.3)
6. **Post-deploy smoke** on the VPS (`/healthz`, `/runtime`, `/db/status`, one chat turn)

### 7.2 VPS target posture (end state, from P4)

- **OS**: Windows Server on VPS
- **Python runtime**: 3.11 in `.venv` (same as dev)
- **Database**: Postgres 15+ (via Docker Desktop for Windows or native Windows installer)
- **Process supervisor**: Windows Service wrapping `uvicorn harbor.app:app --host 127.0.0.1 --port 8000`, driven by `nssm` or `sc.exe`
- **Reverse proxy**: Caddy or IIS with HTTPS termination (Let's Encrypt via Caddy is lowest-friction on Windows); reverse-proxies `:443 → 127.0.0.1:8000`
- **Secrets**: loaded from `C:\harbor\.env` (not in repo, not readable by non-admin users)
- **Scheduler**: external trigger via **Windows Task Scheduler** calling `curl.exe -X POST https://harbor.yourdomain/api/v1/scheduler/tick -H "X-Harbor-Token: ..."` every N minutes, *OR* embedded in-process loop (P1 bolt T7.3) behind feature flag
- **Auth**: single-user token (P4 bolt D1); all write endpoints behind it; `/healthz` + `/runtime` public
- **Logs**: stdout → redirected to `C:\harbor\logs\harbor.log` by the service wrapper; rotation via `logrotate`-equivalent (or Windows event-log adapter later)
- **Backups**: nightly `pg_dump` → `C:\harbor\backups\YYYY-MM-DD.sql`, kept 14 days; scripted via Windows Task Scheduler

### 7.3 Deploy flow (from P4 onward)

One-time setup:
1. Clone repo to `C:\harbor\` on VPS
2. Create `C:\harbor\.venv`, install deps
3. Copy `.env.example` → `.env`, fill in real values (DB, OpenAI, auth token)
4. `alembic upgrade head`
5. Install as Windows Service (`nssm install Harbor ...`)
6. Configure Caddy to reverse-proxy + terminate HTTPS
7. Start service

Per release:
```powershell
cd C:\harbor
git fetch --tags
git checkout v0.2.0
.\.venv\Scripts\pip.exe install -r requirements.txt
.\.venv\Scripts\alembic.exe upgrade head
Restart-Service Harbor
# post-deploy smoke
Invoke-WebRequest https://harbor.yourdomain/healthz
```

This flow is documented as **bolt D4** (Postgres + Docker-compose posture + Windows-VPS deploy walkthrough).

### 7.4 Interim (before P4 lands)

You can already run the current build on the VPS with a **trusted-network** posture:

- Bind to `127.0.0.1:8000` only, no public exposure (reverse-proxy behind VPN or RDP-tunnel)
- SQLite for now (`HARBOR_SQLALCHEMY_DATABASE_URL=sqlite+pysqlite:///C:/harbor/var/harbor.db`)
- Manual `git pull` + `alembic upgrade head` + restart
- No auth yet (acceptable only if not publicly reachable)

Once D1 (auth) and D4 (Postgres+docs) are delivered, the VPS can be safely exposed over HTTPS.

---

## 8. OpenAI integration and secret handling

### 8.1 How Harbor talks to OpenAI

The integration lives in `src/harbor/openai_adapter.py`. Flow:

1. Operator clicks (dry-run / send chat turn / propose source / draft handbook) in the operator web shell
2. Harbor constructs a prompt that includes project sources + handbook context
3. Harbor calls the OpenAI SDK (`openai` Python package) via `OpenAI(api_key=..., base_url=..., timeout=...)`
4. Default model: `gpt-5` (configurable via `HARBOR_OPENAI_MODEL`)
5. Response is persisted (chat turn, dry-run log) with full request + response metadata
6. Source citations (`[1]`, `[2]`) are extracted and rendered as inline badges

The runtime surface `/api/v1/openai/runtime` reports whether the key is present (boolean only, never the key itself). No key is ever logged or returned to the browser.

### 8.2 Do you need to provide an API key?

**Yes**. Harbor does not ship with any key. You obtain one from OpenAI:
1. Sign in at https://platform.openai.com/
2. Billing → add payment method + a sensible spend cap (recommend $20–50/month initially)
3. API keys → Create new secret key → copy the `sk-...` value
4. Give it a name like "Harbor VPS prod" so you can revoke it without affecting other keys

### 8.3 Where the key lives

The key is a **standard 12-factor secret**: it goes in an env var loaded from a `.env` file. Harbor reads:

| Env var | Required | Purpose |
|---|---|---|
| `HARBOR_OPENAI_API_KEY` | yes, for OpenAI features | your `sk-...` key |
| `HARBOR_OPENAI_MODEL` | no (default `gpt-5`) | model to call |
| `HARBOR_OPENAI_BASE_URL` | no | override for proxies / Azure OpenAI |
| `HARBOR_OPENAI_TIMEOUT_SECONDS` | no (default `30.0`) | request timeout |

### 8.4 Where you put them

**On your dev machine (`C:\projekte\Harbor`):**
1. Copy `.env.example` → `.env`
2. Add:
   ```
   HARBOR_OPENAI_API_KEY=sk-your-actual-key-here
   HARBOR_OPENAI_MODEL=gpt-5
   ```
3. `.env` is already in `.gitignore` — it will never be committed.
4. Restart `uvicorn`; visit `/api/v1/openai/runtime` — `configured: true` means Harbor sees the key.

**On the VPS (`C:\harbor\`):**
1. Same `.env` shape, separate file
2. Restrict ACL: `icacls C:\harbor\.env /inheritance:r /grant:r "Administrators:(R)"` — only admin can read it
3. Never paste the key into chat, into a GitHub issue, or into a non-Harbor `.env` file

### 8.5 Rotation + safety hygiene

- Generate a **separate key per environment** (dev + prod), named accordingly. If one leaks, you revoke only one.
- If you ever suspect a key is leaked: revoke immediately at https://platform.openai.com/api-keys, generate new one, update `.env`, restart service. There is **no grace period** — rotate first, investigate after.
- Set a hard **monthly spend cap** in the OpenAI billing portal (this is the real safety net, not the key itself)
- Do **not** commit `.env`. Do **not** screenshot `.env`. Do **not** paste it in bug reports. Harbor's logs and `/runtime` surface are designed to never expose the key — but they can only protect what is entered correctly.

### 8.6 Future providers

If Phase P3 adds a second search provider (Tavily/Brave, bolt I5), it will follow the exact same pattern: `HARBOR_TAVILY_API_KEY=...` (or similar), loaded from `.env`, surfaced as `configured: true/false` only. No key ever crosses the browser boundary.

---

## 9. What is explicitly still out-of-scope

Even with the new deploy-productive direction, the following remain out:

- **Autonomous agent orchestration** (no LLM-driven tool chains)
- **Automated source acceptance** (operator must still explicitly promote)
- **Multi-user collaboration** (D1 is single-token; no user records, no sharing)
- **Vector retrieval / embeddings** (FTS5 / tsvector is sufficient for the planned scale)
- **Custom web crawler** (T7.1 only fetches URLs the operator has already accepted)
- **Public API for third-party integrations** (D1 is single-user only)

These can become candidates after `v1.0.0` stabilizes, but they are not part of this roadmap chapter.

---

## 10. Delivery discipline (unchanged)

Each bolt remains:
- small and focused
- repo-consistent
- locally validated (pytest + quality-gates + smoke slice)
- explicitly merged before the next bolt starts
- driven from `origin/main` as canonical baseline

Do not continue from an unverified reconstructed slice.

---

## 11. Recommended immediate next step

Start **Phase P1 with T6.5** (`stale_source_sweep` — first project-less automation driver). It is the smallest bolt that challenges the scheduler's fan-out assumption and naturally sets up T7.0 (source_snapshot model). After T6.5 and C.7, T7.0 unlocks the content layer.

Prior handoff: `docs/_handoff/HANDOFF_2026-04-12_T6_4_to_next.md`
