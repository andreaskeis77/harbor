# Harbor — Workflow Model v0.1

Status: Draft baseline  
Phase: A0.4  
Scope: Operational workflow states and transitions for Harbor projects

---

## 1. Purpose

Harbor is not only a storage system. It is a guided research workflow system.

That means Harbor needs explicit workflow logic for how a project moves through:

- definition
- evidence acquisition
- review
- refresh
- archive
- reuse

These states must not live only in the operator's head.

---

## 2. Workflow goals

The Harbor workflow model must make it easy to:

- start new projects cleanly
- refine the project definition over time
- understand current progress
- review what has changed
- resume work after a pause
- refresh known sources
- transition stable work into archive
- release reusable blueprints deliberately

---

## 3. Primary project workflow states

### 3.1 Draft

The project idea exists, but the project is still being shaped.

Typical focus:

- define goal
- define central question
- define first scope boundaries
- create first handbook version

### 3.2 Active Research

The project is actively gathering and organizing evidence.

Typical focus:

- search campaigns
- source intake
- source review
- evidence extraction
- first analyses
- gap registration

### 3.3 Review

The project is being checked deliberately for quality and clarity.

Typical focus:

- what changed since last review
- which sources are unreviewed
- which analyses are stale or weak
- whether the handbook needs revision
- whether scope should be narrowed or expanded

### 3.4 Archived

The project is paused or complete as an active research unit.

Typical focus:

- preserve final project state
- keep evidence and history accessible
- optionally prepare for blueprint release

### 3.5 Blueprint

The project or a curated derivative is available for reuse.

Typical focus:

- reuse suitability
- blueprint release notes
- provenance for derived projects

---

## 4. Primary workflow activities

Harbor should support at least the following activities.

### 4.1 Define

Create or refine project scope and handbook.

### 4.2 Search

Run a project-specific search campaign for new sources.

### 4.3 Intake

Accept sources or source candidates into the project context.

### 4.4 Review

Judge candidate relevance, trust, and current usefulness.

### 4.5 Analyze

Generate or store project-local synthesis and comparisons.

### 4.6 Gap logging

Record unanswered questions or blocked information areas.

### 4.7 Refresh

Re-check known sources for change or drift.

### 4.8 Resume

Re-enter a project after time has passed.

### 4.9 Archive

Close or pause the active research loop.

### 4.10 Blueprint release

Promote reusable project structure for future reuse.

---

## 5. Resume model

Resume is important enough to be a first-class workflow, not a convenience feature.

Harbor should make it possible to reopen a project and immediately see:

- current project state
- current handbook version
- last major activity
- what changed since last review
- unresolved gaps
- recommended next actions

---

## 6. Review model

Review is also a first-class workflow.

Review should be able to answer:

- which sources are new
- which sources changed
- which candidates are pending
- which assumptions became questionable
- which analyses need refresh
- whether the handbook should change

Review is where Harbor avoids becoming a passive storage graveyard.

---

## 7. Refresh workflow

Refresh should be treated as a distinct operation from initial search.

A refresh run should focus on:

- already known sources
- changed content detection
- freshness posture
- possible need for new review
- update events and delta awareness

In v1, refresh may be manually triggered.

Later, refresh may become scheduled.

---

## 8. Search versus discovery

Harbor should distinguish:

- **Search**: a concrete campaign based on the current handbook
- **Discovery**: wider exploration for new source classes or unanticipated evidence

Discovery may remain more limited in v1, but the conceptual difference matters.

---

## 9. Candidate and acceptance flow

Harbor should not treat every found source as accepted knowledge immediately.

A safer workflow is:

1. source candidate found
2. source candidate reviewed
3. accepted as project source, or rejected, or deferred
4. source snapshot and evidence extraction proceed
5. analyses update later

This workflow protects project quality.

---

## 10. Workflow relation to blueprints

Blueprint release should happen after a project is sufficiently mature or archived.

Derived projects should begin with:

- imported reusable structure
- a new handbook version for the new project
- fresh project identity
- independent workflow state

---

## 11. V1 versus later phases

### V1 must support

- draft to active research
- active research to review
- review back to active research
- review to archive
- archive to resume
- archive to blueprint release
- manual refresh

### Later phases may support

- scheduled refresh
- discovery campaigns
- monitoring policies
- agent-run candidate generation
- alert workflows
- more advanced reuse and blueprint modules

---

## 12. Exit criteria for this baseline

The workflow model is sufficiently defined for the current phase when:

- Harbor has explicit project workflow states
- resume and review are first-class activities
- refresh is distinct from initial search
- archive and blueprint release are separate decisions
- the workflow model clearly supports both short and long-running projects
