# Lessons Learned — H2 Phase 2 Hardening (2026-04-11)

## What went well

### Typed exception hierarchy was a clean replacement
The domain exception hierarchy (`HarborError` → subtypes) mapped 1:1 onto the existing error semantics. Every `KeyError("project_not_found")` became a `NotFoundError("Project", project_id)` with no behavioral ambiguity. The middleware exception handlers reduced error-handling code in routes from ~120 lines of try/except blocks to zero.

### Transaction middleware was a safe refactor
Replacing `session.commit()` with `session.flush()` in all 16 registry call sites and centralizing the commit in `get_db_session` required no logic changes. All 59 existing tests passed on the first run after the switch, validating that flush + commit-at-boundary is semantically equivalent to commit-in-registry for Harbor's use cases.

### Coverage gate caught nothing but provided confidence
Adding `--cov-fail-under=60` as a quality gate passed immediately (67% coverage). The value is in preventing future regressions, not in catching current gaps.

### Error message format change was caught by tests
When switching from `HTTPException(detail="Project not found.")` to `NotFoundError("Project", project_id)`, the error message format changed from `"Project not found."` to `"Project 'not-found' not found."`. Four existing test assertions caught this immediately, validating the test suite's sensitivity to contract changes.

## What was tricky

### IntegrityError patterns need special handling
Two registries (`source_registry.py`, `review_queue_registry.py`) catch `IntegrityError` and convert to `DuplicateError`. These `try/except IntegrityError` blocks must use `session.flush()` (not `session.commit()`), and the explicit `session.rollback()` calls become unnecessary because the dependency-level rollback handles it. This is a subtle correctness detail — removing `session.rollback()` is only correct because the dependency now owns the rollback.

### Replace-all edits can miss indentation variations
A `replace_all` edit targeting `session.commit()` missed occurrences inside `try` blocks with different indentation. Verification after bulk edits (grepping for the old pattern) is essential.

### HTTPException removal must be verified end-to-end
Removing `HTTPException` from imports while the function body still references it creates a `NameError` that only manifests at runtime. The broken intermediate state was caught in this session but highlights the risk of partial edits.

## Rules reinforced

1. **Grep-verify after bulk edits.** After any replace-all operation, grep for the old pattern to confirm zero remaining occurrences.
2. **Test assertions are API contracts.** Changing error message format is a contract change that must update corresponding test assertions.
3. **Transaction boundary ownership must be explicit.** Either the caller or the callee owns the commit — never both, never neither. Harbor's convention: the FastAPI dependency owns commit/rollback.

## Metrics

| Metric | Before H2 | After H2 |
|--------|-----------|----------|
| Tests | 59 | 65 |
| Coverage | not measured | 67% (60% gate) |
| `KeyError` raises in registries | 48 | 0 |
| String-pattern `except KeyError` in routes | 17 | 0 |
| `HTTPException` imports in routes | 8 | 0 |
| `session.commit()` in registries | 16 | 0 |
| Domain exception types | 0 | 5 |
| Middleware exception handlers | 1 (global 500) | 6 |
