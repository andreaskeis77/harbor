# Harbor - Domain Model v0.1

Status: Draft baseline for A0.2
Phase: A0.2
Purpose: Define the first stable business object model for Harbor before runtime implementation

---

## 1. Purpose of this document

This document defines the first domain model baseline for Harbor.

Harbor is not modeled as a generic chatbot with a document store. It is modeled as a project-partitioned research system with:

- explicit project boundaries
- versioned project definition
- controlled source intake
- project-local review and analysis
- resumable work states
- later refresh, discovery, monitoring, and agentic extensions

This document defines:

- domain entities
- domain relationships
- business boundaries
- ownership of meaning
- lifecycle expectations
- what belongs to the canonical model vs what is merely derived or operational

---

## 2. Modeling principles

### 2.1 Project is the top-level business partition

The most important partition in Harbor is the project.

Everything business-relevant is interpreted in the context of a concrete project:

- handbook
- questions
- sources
- evidence
- analyses
- gaps
- review state
- refresh state
- monitoring state

### 2.2 Global reuse is technical, not implicit business coupling

A source artifact may be technically deduplicated across projects.

But business interpretation must remain project-local.

That means:

- the same source may appear in several projects
- each project may rate or use it differently
- changes in one project must not silently alter another project

### 2.3 Source, evidence, and analysis are distinct layers

Harbor must distinguish between:

- the logical source
- the captured source snapshot/artifact
- the extracted evidence units
- the derived analysis
- the review/decision layer

### 2.4 Versioned definition before automation

A project is not only a bucket of sources. It has a versioned operating definition.

The Research Handbook is therefore a first-class business object.

### 2.5 Reviewable change is more important than raw accumulation

Harbor is designed to support review, resumption, and controlled update handling.

Therefore the model must support:

- old state
- current state
- changed state
- unreviewed candidate state

---

## 3. Domain layers

The business model is easiest to understand in layers.

### 3.1 Project definition layer

Defines what the project is supposed to investigate.

Includes:

- Project
- ResearchHandbook
- HandbookVersion
- ResearchQuestion
- QuestionRelationship
- ProjectTag
- ProjectStatus

### 3.2 Research material layer

Defines what was found or supplied.

Includes:

- Source
- ProjectSource
- SourceCandidate
- SourceSnapshot
- Artifact
- Extract
- Claim
- CitationAnchor

### 3.3 Research interpretation layer

Defines what the system or user concluded.

Includes:

- AnalysisArtifact
- ComparisonView
- Insight
- ResearchGap
- DecisionNote
- ReviewDecision

### 3.4 Research operations layer

Defines what was done operationally.

Includes:

- SearchCampaign
- RefreshRun
- DiscoveryRun
- MonitoringPolicy
- MonitoringRun
- AgentRun
- RunEvent
- ChangeEvent

### 3.5 Reuse layer

Defines how prior work is turned into explicit reuse.

Includes:

- Blueprint
- BlueprintVersion
- BlueprintUse
- ReuseModule (future-facing)
- ResearchPattern (future-facing)

---

## 4. Core entities

## 4.1 Project

Represents one independent research space.

Typical fields:

- `project_id`
- `project_key`
- `title`
- `short_description`
- `project_type`
- `status`
- `created_at`
- `updated_at`
- `archived_at`
- `owner_principal`
- `current_handbook_version_id`
- `current_review_state`

Business rules:

- every project has exactly one current handbook version
- a project can exist without sources
- a project can be archived without losing history
- a project may become blueprint-eligible only after explicit decision

## 4.2 ResearchHandbook

Represents the logical handbook object attached to a project.

Purpose:

- hold the canonical research definition
- provide continuity across revisions

Typical fields:

- `handbook_id`
- `project_id`
- `current_version_id`
- `created_at`
- `updated_at`

Business rules:

- one active handbook per project
- content is versioned, not overwritten without trace

## 4.3 HandbookVersion

Represents one frozen definition state of the handbook.

Typical fields:

- `handbook_version_id`
- `handbook_id`
- `version_no`
- `title`
- `summary`
- `scope_in`
- `scope_out`
- `decision_criteria`
- `search_policy`
- `operations_policy`
- `change_note`
- `created_at`
- `created_by`

Business rules:

- versions are append-oriented
- one version is current
- old versions remain referenceable
- diffs between versions should be derivable

## 4.4 ResearchQuestion

Represents one main question or subquestion.

Typical fields:

- `question_id`
- `project_id`
- `parent_question_id` (nullable)
- `question_text`
- `question_type`
- `priority`
- `status`
- `created_at`
- `updated_at`

Examples:

- "Where can we learn diving safely as beginners?"
- "Which destinations are strong in late December?"
- "Which hotels have easy reef access?"
- "What can a non-diving spouse do on site?"

Business rules:

- questions belong to one project
- questions may be nested
- questions may remain open, partially answered, blocked, or closed

## 4.5 Source

Represents a logical source identity independent of project-specific interpretation.

Examples:

- one specific hotel website
- one forum thread
- one PDF report
- one article URL

Typical fields:

- `source_id`
- `canonical_locator`
- `source_type`
- `publisher_name`
- `origin_domain`
- `access_method`
- `auth_requirement`
- `trust_tier_default`
- `is_active`
- `created_at`
- `updated_at`

Business rules:

- source identity should be stable where possible
- source is not the same as one fetched snapshot
- source does not itself carry final project relevance

## 4.6 ProjectSource

Represents the relationship between a project and a source.

This is one of the most important Harbor entities.

Typical fields:

- `project_source_id`
- `project_id`
- `source_id`
- `relevance_status`
- `review_status`
- `priority`
- `project_context_note`
- `trust_tier_override`
- `first_linked_at`
- `last_reviewed_at`

Why it matters:

- the same source may matter differently in two projects
- review status must remain project-local
- relevance must remain project-local

## 4.7 SourceCandidate

Represents a newly discovered but not yet accepted source relation for a project.

Typical fields:

- `source_candidate_id`
- `project_id`
- `source_id` (nullable until normalized)
- `candidate_locator`
- `discovered_via_run_id`
- `candidate_reason`
- `candidate_status`
- `created_at`
- `resolved_at`

Business rules:

- candidates are not yet trusted project knowledge
- candidates may be accepted, rejected, merged, or deferred

## 4.8 SourceSnapshot

Represents one captured state of a source at a given time.

Typical fields:

- `source_snapshot_id`
- `source_id`
- `retrieved_at`
- `retrieval_method`
- `content_hash`
- `content_type`
- `storage_ref`
- `parser_version`
- `fetch_status`
- `snapshot_note`

Business rules:

- several snapshots may exist for one source
- snapshots are the basis for temporal comparison
- analysis should ideally point to snapshots, not only live URLs

## 4.9 Artifact

Represents the stored raw or normalized payload.

Examples:

- HTML file
- PDF file
- cleaned text
- uploaded note
- manually entered transcript

Typical fields:

- `artifact_id`
- `source_snapshot_id` (nullable for manual uploads)
- `artifact_kind`
- `storage_ref`
- `byte_count`
- `content_hash`
- `created_at`

## 4.10 Extract

Represents a chunk or extracted information unit from an artifact or snapshot.

Typical fields:

- `extract_id`
- `artifact_id`
- `project_id`
- `extract_text`
- `embedding_ref`
- `sequence_no`
- `created_at`

Business rules:

- extracts may be global or project-associated in implementation
- business interpretation in Harbor should remain project-aware where needed

## 4.11 Claim

Represents one interpretable factual proposition derived from a source.

Examples:

- "Hotel X offers direct house reef access"
- "Destination Y is strong for beginner diving in January"

Typical fields:

- `claim_id`
- `project_id`
- `source_snapshot_id`
- `claim_text`
- `claim_type`
- `confidence_hint`
- `claim_status`
- `created_at`

Business rules:

- claims are not raw source text
- claims require provenance
- claims may later be contradicted or superseded

## 4.12 CitationAnchor

Represents the exact anchor from which a claim or analysis is supported.

Typical fields:

- `citation_anchor_id`
- `source_snapshot_id`
- `artifact_id`
- `locator_type`
- `locator_value`
- `quoted_text`
- `created_at`

Purpose:

- preserve traceability to the original support point

## 4.13 AnalysisArtifact

Represents a derived analytic output.

Examples:

- a destination comparison
- a shortlist
- a thematic memo
- a recommendation draft
- an answer synthesis

Typical fields:

- `analysis_artifact_id`
- `project_id`
- `analysis_type`
- `title`
- `body`
- `status`
- `created_at`
- `updated_at`
- `supersedes_analysis_artifact_id` (nullable)

Business rules:

- analyses are derived, not primary truth
- analyses may become stale
- analyses should carry freshness/review state

## 4.14 ResearchGap

Represents a known unresolved information gap.

Examples:

- missing price
- unknown transfer logistics
- conflicting statements
- login-protected data
- offline-only information

Typical fields:

- `research_gap_id`
- `project_id`
- `question_id` (nullable)
- `gap_type`
- `gap_text`
- `severity`
- `status`
- `created_at`
- `resolved_at`

## 4.15 ReviewDecision

Represents one explicit review outcome.

Examples:

- source accepted
- source rejected
- claim marked doubtful
- analysis confirmed current
- gap escalated

Typical fields:

- `review_decision_id`
- `project_id`
- `decision_scope_type`
- `decision_scope_id`
- `decision_outcome`
- `rationale`
- `decided_at`
- `decided_by`

Business rules:

- review decisions are immutable evidence of review history
- a later review may supersede but not erase an earlier decision

---

## 5. Operations entities

## 5.1 SearchCampaign

Represents one intentional search effort within a project.

Typical fields:

- `search_campaign_id`
- `project_id`
- `campaign_type`
- `goal`
- `query_strategy`
- `status`
- `started_at`
- `finished_at`
- `initiated_by`

Examples:

- initial search
- targeted hotel discovery
- gap-specific search

## 5.2 RefreshRun

Represents one update check against known sources.

Typical fields:

- `refresh_run_id`
- `project_id`
- `scope_definition`
- `status`
- `started_at`
- `finished_at`
- `changes_detected_count`

Purpose:

- detect whether known sources changed
- create change candidates instead of silently mutating accepted knowledge

## 5.3 DiscoveryRun

Represents one run meant to find new sources beyond the known set.

Typical fields:

- `discovery_run_id`
- `project_id`
- `strategy_note`
- `status`
- `started_at`
- `finished_at`
- `candidate_count`

## 5.4 MonitoringPolicy

Future-facing but important already.

Represents the policy that defines how a project or source set should be revisited.

Typical fields:

- `monitoring_policy_id`
- `project_id`
- `policy_scope`
- `frequency_class`
- `change_threshold`
- `is_active`
- `created_at`

## 5.5 MonitoringRun

Represents one execution of a monitoring policy.

## 5.6 AgentRun

Represents a future agentic run.

Important rule:

- agent runs create candidates, alerts, and review work
- agent runs do not directly write accepted truth into the project state without review rules

## 5.7 ChangeEvent

Represents one detected change.

Examples:

- source content changed
- source removed
- source newly relevant
- analysis now stale
- prior claim contradicted

Typical fields:

- `change_event_id`
- `project_id`
- `change_scope_type`
- `change_scope_id`
- `change_kind`
- `detected_at`
- `status`
- `details_json`

---

## 6. Blueprint and reuse entities

## 6.1 Blueprint

Represents an explicitly reusable project template derived from an archived project.

Typical fields:

- `blueprint_id`
- `source_project_id`
- `status`
- `blueprint_title`
- `suitability_note`
- `created_at`

Business rules:

- not every archived project is automatically a blueprint
- blueprint creation is explicit

## 6.2 BlueprintVersion

Represents the frozen reusable state of the blueprint.

Typical fields:

- `blueprint_version_id`
- `blueprint_id`
- `version_no`
- `derived_from_handbook_version_id`
- `scope_snapshot`
- `question_template_snapshot`
- `criteria_snapshot`
- `search_pattern_snapshot`
- `created_at`

## 6.3 BlueprintUse

Represents the fact that a new project was created from a blueprint.

Typical fields:

- `blueprint_use_id`
- `blueprint_version_id`
- `target_project_id`
- `reuse_mode`
- `created_at`

Business rule:

- default reuse mode in v1 is snapshot import, not live inheritance

## 6.4 ReuseModule (future-facing)

Represents a reusable part of a blueprint rather than a full-project copy.

Examples:

- one question set
- one criteria matrix
- one search heuristic set
- one operations policy block

## 6.5 ResearchPattern (future-facing)

Represents a reusable method pattern that is more abstract than a project blueprint.

Examples:

- travel-destination comparison pattern
- provider shortlist pattern
- due-diligence gap pattern

---

## 7. Relationship model

The most important relationships are:

### 7.1 Project-centered relationships

- Project 1..1 ResearchHandbook
- Project 1..n HandbookVersion (indirectly through handbook)
- Project 1..n ResearchQuestion
- Project 1..n ProjectSource
- Project 1..n ResearchGap
- Project 1..n AnalysisArtifact
- Project 1..n ReviewDecision
- Project 1..n SearchCampaign
- Project 1..n RefreshRun
- Project 1..n DiscoveryRun
- Project 1..n ChangeEvent

### 7.2 Source-centered relationships

- Source 1..n SourceSnapshot
- Source 1..n ProjectSource
- SourceSnapshot 1..n Artifact
- Artifact 1..n Extract
- SourceSnapshot 1..n Claim
- Claim n..n AnalysisArtifact (logical relationship; may be implemented via join table)
- Claim 1..n CitationAnchor

### 7.3 Blueprint relationships

- Archived Project 0..1 Blueprint
- Blueprint 1..n BlueprintVersion
- BlueprintVersion 1..n BlueprintUse
- BlueprintUse n..1 Project

---

## 8. Canonical boundaries and non-canonical objects

## 8.1 Canonical business state

The following belong to the canonical Harbor business state:

- projects
- handbook versions
- project questions
- project-source relationships
- accepted review decisions
- research gaps
- analysis artifact metadata
- search/refresh/discovery run metadata
- blueprint definitions

## 8.2 Derived but important state

The following are derived but still first-class enough to persist:

- extracts
- claims
- change events
- freshness/staleness indicators
- coverage summaries

## 8.3 Non-canonical or transient state

The following should not be treated as business truth by default:

- temporary model prompts
- ad hoc generation scratch text
- raw intermediate parser noise
- incomplete agent reasoning traces

---

## 9. Lifecycle and status patterns

Several entity families need status/state fields.

### 9.1 Project status

Recommended values:

- `draft`
- `active_research`
- `in_review`
- `archived`

### 9.2 Question status

Recommended values:

- `open`
- `in_progress`
- `partially_answered`
- `blocked`
- `closed`

### 9.3 ProjectSource review status

Recommended values:

- `unreviewed`
- `accepted`
- `rejected`
- `deferred`
- `needs_refresh`

### 9.4 Analysis freshness status

Recommended values:

- `draft`
- `current`
- `review_needed`
- `stale`
- `superseded`

### 9.5 Candidate status

Recommended values:

- `new`
- `accepted`
- `rejected`
- `duplicate`
- `deferred`

---

## 10. Cross-project separation rules

Harbor must enforce several cross-project separation rules.

### 10.1 No implicit scope bleed

Changing the handbook in Project A must not alter Project B.

### 10.2 No implicit review bleed

Accepting or rejecting a source in Project A must not automatically decide its role in Project B.

### 10.3 No implicit analysis bleed

An analysis artifact belongs to one project unless deliberately exported or reused.

### 10.4 No hidden inheritance via blueprint use

A project created from a blueprint must become independently editable after creation.

---

## 11. Future-facing extensions already anticipated by the model

The model should remain open for later additions such as:

- alerts/notifications
- source-family rules
- policy-driven refresh scheduling
- trust-scoring engines
- conflict detection across claims
- semantic coverage scoring
- multi-user review assignments
- richer blueprint module libraries

These should extend the current model, not replace its core project-partitioned logic.

---

## 12. Implementation consequences

This domain model has several consequences for later implementation.

### 12.1 Postgres should be modeled around project-local joins

The system of record should make project-local reads and writes cheap and explicit.

### 12.2 Review history must be append-friendly

Do not design the review layer as only one mutable flag without history.

### 12.3 Source deduplication must not destroy project-local interpretation

Global source normalization is useful, but it must not flatten project meaning.

### 12.4 Handbook versioning is mandatory, not optional

Do not collapse the handbook into one mutable text field if version comparison matters.

---

## 13. Open questions after this baseline

Still open after Domain Model v0.1:

1. exact relational schema layout
2. exact join model for claims, analyses, and citations
3. whether extracts are persisted globally, project-locally, or both
4. how much of the handbook is stored as structured fields vs rich document body
5. first read-models for the website dashboard
6. exact API contracts for project opening, review, and refresh
7. what minimum metadata is required for discovery and monitoring runs
8. how blueprint modules should be introduced later without overcomplicating v1

---

## 14. Baseline summary

Harbor is modeled around one central business idea:

A project is an independent research operating space with its own definition, sources, evidence, review history, and derived analyses.

Everything else - retrieval, refresh, monitoring, agents, and blueprint reuse - must preserve that principle rather than dilute it.
