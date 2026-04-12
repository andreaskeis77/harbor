# Lessons Learned — 2026-04-12 Session (H5 + T6.0A/B + C.1/C.2)

This session delivered nine bolts in one sitting: H5.0A, H5.0B, H5.1A, H5.1B, H5.1C, T6.0A, C.1, C.2, T6.0B.

## What went well

### Extracting static assets paid for itself immediately
H5.1A/B/C extracted ~4000 lines of embedded HTML/CSS/JS from `operator_web.py` into dedicated `operator.js`, `chat.js`, and `operator.css` files. Every subsequent bolt in this session (C.1 collapsibles, C.2 automation panel) was then a focused edit in three files instead of one monolith. The cost of extraction was paid once; the savings compound per follow-up bolt.

### "Infrastructure-first, one real call-site" scoped T6.0A correctly
T6.0A could have grown into a scheduler + executor + retry + metrics story. Instead it shipped as: registry + migration + API + one real instrumentation (`draft-handbook`). That gave us a deployable observability baseline without speculative machinery — and T6.0B could then address a real-world concern (failure survives rollback) on a working foundation instead of a paper design.

### Making T6.0A visible in C.2 closed the loop
T6.0A's Task Log had no UI when it merged. C.2 added the panel two bolts later, which validated the API shape end-to-end *before* a second call-site is added in T6.1. The UX consolidation phase paid for itself: we discovered no shape mismatches because the Pydantic read model drove the renderer.

### Bolts compose best when they stay single-concern
Each bolt in this session had one purpose: H5.0A adds review actions in UI; H5.1A moves JS to a file; T6.0A adds a registry; C.1 adds collapsibles; T6.0B moves failure to a side channel. Nothing was bundled. When C.1 and C.2 both shipped in 30 minutes back-to-back, it was because each was small enough to reason about independently.

## What was tricky

### SQLite single-writer forced a design decision in T6.0B
The first cut of T6.0B used the side-channel observer for *every* state transition (start, succeed, fail). That deadlocked on SQLite: the request session held a pending write from `create_handbook_version`, and the observer's `complete_observer` commit waited forever for the lock. The fix was to split responsibilities honestly: side-channel for **start** (so an attempt is always recorded) and **fail** (the whole point of the pattern), but keep **success** on the request session (which already holds the write lock it needs). The failure path also explicitly calls `session.rollback()` before invoking the side-channel, so the observer can actually acquire the writer lock.

This is not a SQLite-only concern — it's a real observation about how side-channel observers interact with request transactions. In Postgres, MVCC hides the symptom, but the honest coupling is still there: the observer's visibility guarantees are bounded by the session boundaries you respect.

### Tests that assert against HTML-rendered JS fragments need care after extraction
H5.1A extracted the JS into `operator.js`. Tests that previously grepped `/promote-to-review` from the HTML response body now had to split: HTML markers stay on the page response; JS-behavior markers move to a new test that fetches `/static/operator.js`. Easy to miss — the first H5.1A CI run was red because of exactly this.

### The manifest's "honest state handling" rule made scope decisions sharp
T6.0A could have tried to make failure-recording work with a half-measure (e.g., a best-effort `try/except` around the existing in-session writes). Explicitly writing "failure recording outside the transaction boundary is out of scope for T6.0A" in the registry docstring forced us to ship T6.0A with a known limitation and then *design* T6.0B around that limitation instead of hiding it.

## Rules reinforced

1. **Ship observability before automation.** T6.0A is just a Task Log — no orchestration, no scheduler. It's what lets T6.1+ be safe.
2. **Keep one concern per bolt, even when bundling feels faster.** H5.1A/B/C could have been one PR. Running them as three kept each diff readable.
3. **Don't hide limitations — write them into the next bolt's scope.** T6.0A's docstring said failure-across-rollback is out of scope. T6.0B's PR description opened with "closes the deliberate gap." That's a healthy loop.
4. **Default to editing static files, not generating them.** H5.1A/B/C cut the cost of every subsequent UI bolt. Embedded frontends in Python strings accumulate change-cost faster than it looks.
5. **Writer locks are a property of the session, not the database.** Observer patterns need to think about who holds writes and for how long, even in "fast" SQLite cases.

## Metrics

| Metric | Before session | After session |
|--------|----------------|---------------|
| Tests | 135 | 172 (+37) |
| Coverage | 96% | 96% |
| Alembic migrations | 11 | 12 |
| API endpoints | 49 | 51 |
| ORM models | 11 | 12 |
| Static asset files | 0 | 3 (operator.js, chat.js, operator.css) |
| Bolts merged | — | 9 (#35–#43) |
| Session duration | — | one sitting |

## Open follow-ups flagged during the session

- **T6.1**: instrument `propose-source` through the observer to prove the pattern generalizes beyond `draft-handbook`.
- **C.3**: unified status/toast mechanism (the scattered `data-*-status` mounts are the next UX debt).
- **C.4**: review queue as a central pending-actions view.
- **operator_web.py** is still ~1000 lines of embedded HTML. After H5.1, the JS and CSS are out, but the HTML structure itself could be templated once it grows further.
