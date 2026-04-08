# Harbor – Search Run Registry v0.1

Status: delivered baseline

## Purpose
A search run represents one concrete execution attempt inside a search campaign.

## Scope
- create a search run
- list search runs within a search campaign
- read one search run
- patch search run state fields

## API
- `POST /api/v1/projects/{project_id}/search-campaigns/{search_campaign_id}/runs`
- `GET /api/v1/projects/{project_id}/search-campaigns/{search_campaign_id}/runs`
- `GET /api/v1/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/{search_run_id}`
- `PATCH /api/v1/projects/{project_id}/search-campaigns/{search_campaign_id}/runs/{search_run_id}`

## Stored fields
- `search_run_id`
- `project_id`
- `search_campaign_id`
- `title`
- `run_kind`
- `status`
- `query_text_snapshot`
- `note`
- `started_at`
- `finished_at`
- `created_at`
- `updated_at`

## Out of scope
- actual search execution
- adapter orchestration
- scheduling
- ranking logic
