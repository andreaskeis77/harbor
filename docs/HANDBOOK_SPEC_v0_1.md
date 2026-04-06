# Harbor — Handbook Specification v0.1

Status: Draft baseline  
Phase: A0.4  
Scope: Definition of the Research Handbook as the central steering object per project

---

## 1. Purpose

The Research Handbook is the operational heart of each Harbor project.

It is not merely a freeform note. It is the structured, versioned control document
that defines what the project is trying to learn, how the search space is bounded,
how evidence should be assessed, and how Harbor should continue work on the project.

The handbook must be usable by:

- the human operator
- the web application
- the Custom GPT
- later background jobs and monitoring workflows

---

## 2. Design principles

### 2.1 Versioned, not overwritten

Handbook changes must be versioned.

Harbor must preserve the history of project-definition changes and make it possible
to understand how and why the scope evolved.

### 2.2 Structured, not only narrative

Free text is useful, but Harbor must treat the handbook as a structured product
artifact with defined sections and meaning.

### 2.3 Operational, not decorative

The handbook is intended to drive:

- search behavior
- relevance decisions
- source prioritization
- gap detection
- review focus
- resume behavior
- later monitoring policy

### 2.4 Mutable within guardrails

Research projects evolve. Harbor must support narrowing, expanding, splitting, or
reprioritizing a project while keeping older decisions visible.

---

## 3. What the handbook controls

The handbook defines at least:

- what the project is about
- which questions matter
- what is in scope
- what is out of scope
- which source types are preferred
- which source types are lower trust or lower priority
- how conflicting evidence should be treated
- what qualifies as a useful answer
- which gaps still matter
- what the next research steps should be

---

## 4. Mandatory handbook sections

A handbook version should contain at minimum the following sections.

### 4.1 Project identity

- project title
- short description
- project type
- current status
- current handbook version label

### 4.2 Research goal

A concise statement of what the project is trying to achieve.

### 4.3 Central question

The main question Harbor is meant to answer or support.

### 4.4 Subquestions

Structured subquestions that break the topic into manageable research units.

### 4.5 In-scope

Explicit items Harbor should consider part of the project.

### 4.6 Out-of-scope

Explicit items Harbor should not currently spend effort on.

### 4.7 Decision and evaluation criteria

The criteria by which options, claims, or candidate answers should be judged.

### 4.8 Research priorities

Which parts of the project matter most right now.

### 4.9 Source strategy

Including:

- preferred source categories
- lower-priority source categories
- likely high-trust sources
- likely volatile sources
- likely inaccessible sources

### 4.10 Search strategy

Including:

- key search terms
- variations
- domain-specific vocabulary
- known synonyms
- region/language implications where relevant

### 4.11 Hypotheses or working assumptions

Explicit assumptions help Harbor avoid hidden bias and make revisions visible.

### 4.12 Research gaps

Known unanswered questions, missing evidence, or blocked information areas.

### 4.13 Research operations policy

Operational guidance such as:

- which sources may be refreshed
- which require caution
- what counts as a meaningful update
- when human review is required
- when Harbor should stop or narrow the search

### 4.14 Change notes

A concise explanation of what changed compared with the prior handbook version.

---

## 5. Optional sections

Harbor should allow later expansion with optional sections such as:

- glossary
- named entities
- region/timeframe constraints
- ranking formula notes
- comparison dimensions
- reporting preferences
- monitoring preferences
- known exclusions or red flags

---

## 6. Handbook versioning rules

Each handbook version should be treated as a first-class artifact.

A handbook version should record at least:

- handbook_version_id
- project_id
- version_number or semantic label
- created_at
- created_by
- status
- summary_of_change
- content payload

Harbor should be able to show:

- latest version
- previous version
- what changed
- when the current version became active

---

## 7. Handbook change triggers

A new handbook version should normally be created when:

- the central question changes materially
- in-scope or out-of-scope changes
- decision criteria change
- major new subquestions are introduced
- the project shifts from short research to long monitoring
- blueprint-derived scope is tailored into a new concrete project

Small typo-level edits may later be handled differently, but the baseline posture
should prefer explicit versioning over silent modification.

---

## 8. Relationship to workflow

The handbook is closely tied to workflow state.

In different project states, different handbook sections become more important:

- Draft: goal, central question, in-scope, out-of-scope
- Active Research: source strategy, search strategy, priorities
- Review: gaps, assumptions, change notes, update criteria
- Archived: final state summary, blueprint relevance
- Blueprint: reusable structure, reusable criteria, reusable modules

---

## 9. Relationship to blueprints

A blueprint may be derived from a handbook version or a curated subset of it.

In v1, blueprint creation should preserve:

- source strategy
- subquestion structure
- evaluation logic
- typical gaps
- operator notes on reuse

But it should not automatically carry forward stale factual conclusions.

---

## 10. Exit criteria for this baseline

The handbook model is sufficiently defined for the current phase when:

- Harbor treats the handbook as a first-class project object
- the minimum section set is accepted
- versioning is required by default
- the handbook is clearly linked to search, review, resume, and blueprint logic
