# Handoff: P3/P4 to next phase

**Date**: 2026-04-12 (fourth sitting of the day)
**From session**: P3.2-fix → P3.3 → P3.4 → P4.1 → P4.2 → P4.3 → P4.4 (7 bolts this sitting)
**Branch**: `main` (all merged)
**Last PR**: #72 (P4.4)

---

## Session delivery summary

| Bolt | PR  | Title                                                                  |
|------|-----|------------------------------------------------------------------------|
| P3.2 | #66 | Snapshot visibility in operator project-sources UI (fix + land)        |
| P3.3 | #67 | Embed latest snapshot excerpts into chat grounding                     |
| P3.4 | #68 | Staleness signal in overview                                           |
| P4.1 | #69 | Manual fetch-now endpoint for project-sources                          |
| P4.2 | #70 | Snapshot history in operator project-sources UI                        |
| P4.3 | #71 | Fetch-error signal in overview                                         |
| P4.4 | #72 | Fetch-now operator button on project-sources rows                      |

Phase P3 (**content activation**) and Phase P4 (**refresh & error recovery**) are both complete. All bolts followed the Validation Protocol: branch → implement → targeted tests → quality gates → docs → commit → push → PR → squash-merge.

---

## Confirmed current state

- **291 tests, 95.55% coverage** (70% gate enforced)
- **13 Alembic migrations** (unchanged — P3/P4 added no schema)
- **13 ORM models** (unchanged)
- **API endpoints**: +1 from P4.1 (`POST /projects/{id}/project-sources/{ps_id}/fetch-now`)
- **3 static asset files**: `operator.js` + `operator.css` grew (snapshot history lazy-loader, fetch-now button, staleness/fetch-error totals cards); `chat.js` unchanged
- **Quality gates**: compileall + ruff (9 rule sets) + pytest with coverage — all green

---

## Architecture developments this sitting

### Snapshot excerpts in chat grounding (P3.3)
`openai_adapter._prepare_project_sources` now accepts `snapshot_excerpt` + `snapshot_fetched_at` per source. The adapter route attaches excerpts only when the latest snapshot is `http_status == 200` with non-empty `extracted_text`. Budget is per-source (`MAX_SNAPSHOT_EXCERPT_CHARS = 600`), not global — the existing prior-turn compaction already bounds overall prompt size. `request_metadata` now reports `project_source_snapshot_count_included` and `project_source_snapshot_count_truncated`.

### "Latest snapshot per project_source" subquery pattern (P3.4 + P4.3)
Both the staleness signal and the fetch-error signal need "what is the *latest* snapshot for each project_source." Window functions (`ROW_NUMBER() OVER ...`) are not portable across SQLite + Postgres at the SQLAlchemy-Core level we use. Solution adopted in `overview.py`:

```python
latest_fetched = (
    select(
        SourceSnapshotRecord.project_source_id.label("psid"),
        func.max(SourceSnapshotRecord.fetched_at).label("max_fetched"),
    )
    .group_by(SourceSnapshotRecord.project_source_id)
    .subquery()
)
# ... JOIN back to SourceSnapshotRecord on (psid, fetched_at == max_fetched)
```

Staleness variant uses LEFT JOIN + HAVING (`MAX(fetched_at) IS NULL OR MAX(fetched_at) < threshold`) so never-fetched web_page sources count as stale. This pattern is now load-bearing on two overview surfaces and will generalize if a third metric needs "latest per project_source."

### Observer-free manual fetch endpoint (P4.1)
`POST .../fetch-now` does **not** route through the automation-task observer. Rationale: this is a synchronous operator-initiated action; its success/failure is visible to the operator immediately via the response + the snapshot it writes. Adding an observer would inflate `automation_task_registry` without new information. Failed fetches still persist a `SourceSnapshotRecord` with `fetch_error` set — same as the scheduler path. Contract symmetry with the scheduler is by-data, not by-observer.

### Snapshot history as a client-side lazy-loader (P4.2)
Inline `<details>` on each project-source row fetches `/snapshots` (the list endpoint from P3.1), caps client-side at 10 entries, marks index 0 with `.is-latest`. No server-side "history" endpoint, no pagination. The existing list endpoint already supports the limit parameter; we just don't pass it because 10 is small enough to slice client-side. If/when snapshot retention grows, move the cap to the query.

### Fetch-now button as a conditional row action (P4.4)
Rendered only when `source.source_type === "web_page" && source.canonical_url`. Click handler reuses the existing `runOperatorAction(button, postJson, "Snapshot fetched.")` primitive — same UX contract as every other row-action button. After success, the project-detail page reloads; the snapshot history `<details>` will now include the new row.

### Key files touched this session

| File                                                            | Role                                                                         |
|-----------------------------------------------------------------|------------------------------------------------------------------------------|
| `src/harbor/api/routes/source_snapshots.py`                     | P4.1 `fetch-now` endpoint; body-decode helper; InvalidPayloadError for non-web_page |
| `src/harbor/api/routes/openai_adapter.py`                       | P3.3 attaches snapshot excerpt to accepted project sources in chat grounding |
| `src/harbor/openai_adapter.py`                                  | P3.3 `_prepare_project_sources` + `_project_sources_lines` render excerpt    |
| `src/harbor/overview.py`                                        | P3.4 staleness subquery; P4.3 fetch-error subquery; new totals + per-project counts |
| `src/harbor/api/routes/operator_web.py`                         | P3.2 "Latest snapshot" column; P3.4 "Stale snapshots" column; P4.3 "Fetch errors" column |
| `src/harbor/static/operator.js`                                 | P3.2 lazy-loader; P4.2 history renderer; P4.4 fetch-now button + click handler |
| `src/harbor/static/operator.css`                                | Snapshot meta/preview/error/entry/count styles                               |
| `tests/test_operator_snapshot_ui.py` (new)                      | P3.2                                                                         |
| `tests/test_openai_chat_grounding_snapshots.py` (new)           | P3.3 (3 tests)                                                               |
| `tests/test_overview_staleness.py` (new)                        | P3.4 (5 tests)                                                               |
| `tests/test_fetch_now_api.py` (new)                             | P4.1 (4 tests)                                                               |
| `tests/test_overview_fetch_errors.py` (new)                     | P4.3 (4 tests)                                                               |
| `tests/test_operator_fetch_now_ui.py` (new)                     | P4.4 (2 tests)                                                               |

---

## Candidate next steps

Phases P3 (content activation) and P4 (refresh & error recovery) are done. Snapshot content flows into prompts, staleness + fetch-error signals are on the overview, operators can manually trigger a refetch and inspect history. Natural next fronts:

### Option A — **P5: snapshot-to-chat cite-back**
Assistant responses already receive snapshot excerpts per source (P3.3). A follow-up would be making citation targets link back to the specific snapshot (`snapshot_id` on the attribution) so operators can jump from an assistant citation into the exact fetched content. Small-to-medium bolt; builds directly on P3.3's data flow.

### Option B — **P5-alt: cross-project source dedup**
Same `canonical_url` across projects is currently independent. A "suggest-merge" surface could use snapshot `content_hash` to propose deduplication. Medium bolt; exercises the snapshot table's identity claim.

### Option C — **P6: automated search execution**
Still explicitly out-of-scope per `PROJECT_STATE.md`. If phase P7+ is on the horizon, the scheduler + snapshot fetching are the prerequisite that now exists.

### Option D — **Operator UX polish**
Several candidates: bulk fetch-now, inline fetch-error details on the overview table, snapshot size/diff column. Low-risk bolts that harden what P3/P4 delivered before adding new phases.

### Recommended path
**Option A (P5 cite-back) first** — it completes the P3.3 → operator-UI loop (snapshot content is in the prompt; citation UI should let the operator verify what the model saw). Then **Option D** polish where gaps hurt the workflow, **then** P6 once the operator feedback loop on snapshots is closed.

---

## Validation commands

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest tests/test_overview_staleness.py tests/test_overview_fetch_errors.py tests/test_fetch_now_api.py tests/test_openai_chat_grounding_snapshots.py tests/test_operator_snapshot_ui.py tests/test_operator_fetch_now_ui.py -q
python .\tools\task_runner.py quality-gates
python .\tools\task_runner.py smoke-operator-web-shell-slice
python .\tools\task_runner.py smoke-openai-chat-session-slice
```

---

## Lessons reinforced this sitting

1. **GROUP BY + JOIN-back beats window functions when portability matters.** SQLite + Postgres share GROUP BY semantics; window-function parity is shakier through SQLAlchemy Core at the level we use. Two overview metrics now use the same "max per group + self-join" shape — worth extracting if a third appears.
2. **Three similar lines beats a premature abstraction (manifest re-confirmed).** P4.1's body-decode helper duplicates ~10 lines of logic similar to the scheduler's fetch path. Refactoring would have required teaching both call-sites a shared helper that neither has asked for. The duplication is cheaper than the abstraction at N=2 with no third caller in sight.
3. **Not every mutating operator action needs the automation-task observer.** P4.1 writes a `SourceSnapshotRecord` — which is already the observability surface for the scheduler's fetch path. Adding observer bookkeeping would record the same event twice. Observer is for *background* actions whose outcome would otherwise be invisible.
4. **Lazy-loader `<details>` is now a reusable pattern.** P3.2, P4.2 both use the same shape: a `<details>` with `data-project-source-id`, a one-shot fetch on `toggle`, a render into an inner container. Future inline-details surfaces (e.g. snapshot diff) should follow this shape.
5. **"Render conditionally on data shape" beats "render always + error on click."** P4.4's fetch-now button exists only for `web_page` sources with a canonical URL. A universal button that returned 422 would be discoverable but wrong. The condition lives where the data lives (client-side, from the already-hydrated source record).

---

## Prompt for the new chat

Paste this into the new chat to prime context:

> Ich arbeite am Harbor-Projekt (projekt-partitioniertes Research-System, FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic + pytest). Das lokale Repo liegt unter `C:\projekte\Harbor`; `main` ist canonical baseline. Wir folgen dem Harbor Engineering Manifest und dem Validation Protocol.
>
> Letzte Session (2026-04-12, viertes Sitting) hat 7 Bolts gemerged: P3.2-fix, P3.3, P3.4, P4.1, P4.2, P4.3, P4.4 (PRs #66–#72). Damit sind **Phase P3 (content activation)** und **Phase P4 (refresh & error recovery)** komplett. Snapshot-Inhalte fließen jetzt in Chat-Grounding ein, Staleness- und Fetch-Error-Signale sind auf dem Overview sichtbar, Operatoren können manuell refetchen und Snapshot-History inline inspizieren.
>
> Stand jetzt: **291 tests, 95.55% coverage, 13 migrations, 13 ORM models**. Kein Schema-Delta in P3/P4 — alles baut auf `source_snapshot` aus T7.0 auf.
>
> Start-Lesereihenfolge:
> 1. `docs/_handoff/HANDOFF_2026-04-12_P4_to_next.md` (dieser Handoff)
> 2. `docs/_handoff/HANDOFF_2026-04-12_T6_4_to_next.md` (prior handoff)
> 3. `docs/PROJECT_STATE.md`
> 4. `docs/STRATEGY_ROADMAP_v0_1.md`
> 5. `docs/MASTERPLAN.md`, `docs/WORKING_AGREEMENT.md`, `docs/VALIDATION_PROTOCOL.md`
>
> Offene Optionen für den nächsten Bolt (Empfehlung: P5 cite-back → UX-Polish → P6):
> - **P5 cite-back** — Chat-Attributionen an `snapshot_id` hängen, damit Operator aus Zitat direkt in den gefetchten Inhalt springt; schließt den P3.3 → UI-Loop
> - **P5-alt** — Cross-Project Source-Dedup via `content_hash`
> - **UX-Polish** — bulk fetch-now, fetch-error Inline-Detail auf Overview, Snapshot-Diff-Spalte
> - **P6** — automated search execution (erst nach Close-out des Operator-Feedback-Loops)
>
> Bitte lies zuerst den Handoff und bestätige dann, welchen Bolt wir als nächstes anpacken. Keine Implementierung ohne Discussed → Prepared → Applied → Validated → Accepted.

---

## Key metrics

| Metric                       | Before sitting | After sitting |
|------------------------------|----------------|---------------|
| Tests                        | 273            | 291 (+18)     |
| Coverage                     | ~96%           | 95.55%        |
| Migrations                   | 13             | 13            |
| ORM models                   | 13             | 13            |
| Endpoints                    | N              | N+1 (fetch-now) |
| Bolts merged this sitting    | —              | 7 (#66–#72)   |
| Phases closed this sitting   | —              | P3 + P4       |
