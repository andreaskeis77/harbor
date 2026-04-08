# Harbor – Workflow Summary Surface v0.1

Status: delivered baseline

## Purpose
The workflow summary surface gives one compact project-level read model for operator control.

## API
- `GET /api/v1/projects/{project_id}/workflow-summary`

## Returned sections
- `project_id`
- `project_title`
- `counts`
- `lineage_items`

## Count fields
- `search_campaign_count`
- `search_run_count`
- `search_result_candidate_count`
- `candidate_pending_count`
- `candidate_promoted_count`
- `candidate_accepted_count`
- `review_queue_item_count`
- `review_queue_open_count`
- `review_queue_in_review_count`
- `review_queue_completed_count`
- `project_source_count`

## Lineage semantics
Each lineage item starts at one `SearchResultCandidate` and shows the furthest linked objects currently attached:
- optional linked `ReviewQueueItem`
- optional linked `ProjectSource`
- optional linked `Source`

This makes the current workflow state visible without requiring multiple manual list calls.

## Out of scope
- analytics / dashboards
- sorting/filtering options beyond current API defaults
- UI presentation
- historical audit timelines
