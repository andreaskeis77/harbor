# Harbor – Search Result Candidate Baseline v0.1

Status: delivered baseline

## Purpose
A search result candidate represents one concrete discovered result inside a specific search run.

## Scope
- create a result candidate for a search run
- list result candidates for a run
- read one result candidate
- update candidate disposition
- persist minimal result metadata

## API
- `POST /api/v1/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/{search_run_id}/result-candidates`
- `GET /api/v1/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/{search_run_id}/result-candidates`
- `GET /api/v1/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/{search_run_id}/result-candidates/{search_result_candidate_id}`
- `PATCH /api/v1/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/{search_run_id}/result-candidates/{search_result_candidate_id}/disposition`

## Stored fields
- `search_result_candidate_id`
- `project_id`
- `search_campaign_id`
- `search_run_id`
- `title`
- `url`
- `domain`
- `snippet`
- `rank`
- `disposition`
- `note`
- `published_at`
- `created_at`
- `updated_at`

## Out of scope
- external web search execution
- deduplication merge logic
- source promotion automation
- scheduling / agentic workflows
