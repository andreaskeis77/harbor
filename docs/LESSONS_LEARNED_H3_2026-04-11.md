# Lessons Learned — H3 Phase 3 Hardening (2026-04-11)

## What went well

### Coverage exclusion dramatically improved signal
Excluding the two CLI-only operator surfaces (690 lines, 0% coverage by design) changed the coverage metric from 67% to 95%. The 70% gate now measures meaningful API/domain code, not CLI tools that can't be API-tested. This is a better quality signal.

### Error-path tests caught real gaps
The 503 `DatabaseNotConfiguredError` test exposed that the Phase 2 middleware handler was untested. The connectivity error test validated that `status.py` properly captures and reports DB connection failures without raising. These are paths that only manifest in production-like scenarios.

### Expanded Ruff rules auto-fixed modernization issues
Adding UP (pyupgrade), SIM (simplification), LOG (logging), and RUF (Ruff-specific) rules found 14 violations, 11 auto-fixable. The most impactful: `UP037` removed unnecessary string quotes from type annotations across 8 files, and `UP035` modernized an import in `openai_adapter.py`.

## What was tricky

### Alembic fileConfig silently disables application loggers
**Root cause of the session's hardest debugging issue.** Alembic's `env.py` calls `fileConfig(config.config_file_name)` which defaults to `disable_existing_loggers=True`. When the alembic migration tests ran before the logging tests, Python's `fileConfig` disabled the `harbor.request` logger — causing the log-output verification tests to fail (no records captured).

**Symptoms**: Tests passed in isolation, failed in the full suite. The failure was non-deterministic-looking but actually deterministic based on alphabetical test file ordering (`test_alembic_*` runs before `test_middleware*`).

**Fix**: `fileConfig(config.config_file_name, disable_existing_loggers=False)`.

**Lesson**: Any call to `logging.config.fileConfig()` or `logging.config.dictConfig()` without `disable_existing_loggers=False` is a latent bug in any codebase that configures logging from multiple entry points.

### Capturing log output in tests requires careful handler management
Standard `caplog` and `capsys` fixtures don't reliably capture logging output when:
- The logger has `propagate=False` (caplog relies on root propagation)
- The StreamHandler is created before capsys/caplog replace sys.stderr

**Solution**: Use a custom `_CollectingHandler` added directly to the target logger. This is deterministic regardless of logger hierarchy or test execution order.

### Config redaction logic has subtle edge cases
The URL redaction code in `config.py` handles: explicit URLs with credentials, explicit URLs without credentials, postgres-from-parts assembly, and the unconfigured case. Each path needs a separate test because the branching logic differs.

## Rules reinforced

1. **Test what matters, exclude what doesn't.** Coverage metrics must reflect the code under test, not unrelated CLI tooling. Exclusions must be explicit and documented.
2. **Every exception handler needs a test.** If middleware maps ExceptionType → HTTP status, there must be a test that raises ExceptionType and asserts the status code.
3. **Logging configuration calls are global mutations.** Any `fileConfig()`/`dictConfig()` call can disable other loggers. Always pass `disable_existing_loggers=False` unless you explicitly intend to reset all logging.
4. **Test failures that depend on execution order indicate shared mutable state.** The most common culprit is Python's `logging` module, which is global and stateful.

## Metrics

| Metric | Before H3 | After H3 |
|--------|-----------|----------|
| Tests | 65 | 82 |
| Coverage (reported) | 67% | 95% |
| Coverage gate | 60% | 70% |
| Ruff rule sets | 4 (E,F,I,B) | 9 (E,F,I,B,UP,SIM,PIE,LOG,RUF) |
| Error-path tests | 0 dedicated | 11 (503, redaction, connectivity, middleware handlers) |
| Observability tests | 0 | 2 (structured log, error trace) |
| Alembic logger bug | latent | fixed + tested |
