# Harbor Domain Model v0.1

## Main domain objects

- Project
- ResearchHandbook
- HandbookVersion
- ResearchQuestion
- Source
- ProjectSource
- SourceSnapshot
- AnalysisArtifact
- ResearchGap
- SearchCampaign
- RefreshRun
- ReviewDecision
- Blueprint

## Key modeling rule

A source may exist globally, but its relevance and interpretation are project-local.
That is why Harbor distinguishes:
- `Source`
- `ProjectSource`

## Blueprint rule

Blueprint usage is modeled as explicit reuse by snapshot import rather than implicit live inheritance.
