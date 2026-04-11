# Lessons Learned — H4 Phase 4 Hardening (2026-04-11)

## What went well

### Validation edge-case tests exposed the real coverage gap
The review_queue_registry had 84% coverage — seemingly good — but the uncovered 16% was entirely validation logic: entity-not-found checks, cross-entity ownership mismatches, and lineage integrity guards. These are exactly the paths that cause silent data corruption or confusing 500s in production. Adding 17 targeted tests raised coverage to 97% and verified every validation branch.

### Input boundary tests are cheap and high-value
15 Pydantic boundary tests took minimal effort to write (simple 422 assertions) but exercise the full FastAPI validation pipeline. They verify that `min_length`, `max_length`, and `ge` constraints are actually enforced at the API boundary, not just declared in models.

### E2E lifecycle test found a real assumption mismatch
The workflow summary endpoint returns lineage items ordered by creation time, not by promotion status. The initial E2E test assumed the first lineage item would be the promoted candidate — it was actually the second (unpromoted) candidate. This is exactly the kind of ordering assumption that causes flaky tests or incorrect UI rendering in production.

## What was tricky

### Workflow summary response shape was undocumented in tests
No existing test exercised the `/workflow-summary` endpoint structure. The E2E test had to discover the response shape (`project_id`, `project_title`, `counts`, `lineage_items`) by reading the Pydantic model. The field names in `WorkflowSummaryCounts` use `_count` suffixes (e.g., `search_campaign_count`), not the plural form one might guess. This reinforces why E2E tests matter — they catch shape mismatches before consumers do.

### Cross-entity ownership validation requires complex test setup
Testing that "candidate belongs to a different campaign" requires creating two campaigns, a run under one, a candidate under that run, then referencing the wrong campaign ID. Each edge case needs 3-5 entity-creation steps. Helper functions are essential to keep these tests readable.

## Rules reinforced

1. **Coverage percentage hides the gap location.** 84% sounds good, but if the uncovered 16% is all validation logic, the system has no safety net for bad input. Always check *which* lines are uncovered, not just the number.
2. **Test what the API actually returns, not what you think it returns.** Response shapes, field names, and ordering can differ from intuition. E2E tests catch these mismatches.
3. **Input validation is a system boundary.** Pydantic constraints are declarations, not guarantees, until tested through the full request pipeline.
4. **E2E tests are the integration safety net.** Individual unit tests can all pass while the full pipeline has a broken state transition. At least one test must traverse the entire workflow.

## Metrics

| Metric | Before H4 | After H4 |
|--------|-----------|----------|
| Tests | 82 | 116 |
| Coverage (reported) | 95% | 96% |
| review_queue_registry coverage | 84% | 97% |
| Validation edge-case tests | 0 dedicated | 17 |
| Input boundary tests | 0 | 15 |
| E2E workflow tests | 0 | 1 (full pipeline) |
| Engineering manifest rules | 20 | 24 |
