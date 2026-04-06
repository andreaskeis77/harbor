# Harbor — Blueprint Model v0.1

Status: Draft baseline  
Phase: A0.4  
Scope: Controlled reuse of archived research projects and reusable research structures

---

## 1. Purpose

Harbor should not only preserve completed projects but also convert selected project
results into reusable starting structures for future work.

A blueprint is therefore not just an archive marker. It is a deliberate reuse
artifact derived from a completed or mature project.

---

## 2. Core design principle

Blueprint reuse must increase efficiency **without creating hidden coupling**
between old and new projects.

Therefore the v1 default rule is:

**A blueprint is imported as a snapshot into a new project. It does not create
live inheritance.**

---

## 3. Why blueprints matter

Blueprints create three kinds of long-term leverage:

1. faster project startup
2. more consistent research quality
3. gradual accumulation of reusable research patterns

---

## 4. Blueprint sources

A blueprint may originate from:

- a fully archived project
- a mature project phase deemed reusable
- later, a curated subset of a project
- later, a handbook section module or workflow template

In the current baseline, the main source is:

- **an archived project marked as blueprint-eligible**

---

## 5. What a blueprint may contain

A blueprint may contain reusable structures such as:

- research goal pattern
- central question pattern
- subquestion tree
- evaluation criteria
- source strategy
- search strategy
- known gap categories
- operator notes
- suggested workflow posture

A blueprint should generally avoid carrying forward:

- stale factual results as if still current
- transient prices or availability claims
- project-specific review states
- volatile source freshness assumptions without revalidation

---

## 6. Blueprint lifecycle

### 6.1 Candidate

A project may be considered potentially reusable.

### 6.2 Blueprint-eligible

A completed project is explicitly assessed as a candidate for blueprint release.

### 6.3 Blueprint released

The reusable structure is approved for future project creation.

### 6.4 Superseded

A newer blueprint version becomes preferable.

### 6.5 Retired

The blueprint remains historically visible but should no longer be used by default.

---

## 7. Blueprint object expectations

A blueprint object should include at least:

- blueprint_id
- blueprint_title
- source_project_id
- source_handbook_version_id
- blueprint_status
- reuse_notes
- suitability_notes
- created_at
- updated_at

---

## 8. Blueprint usage in v1

In v1 Harbor should support the following basic pattern:

1. an archived project is marked as reusable
2. a new project is created from that blueprint
3. Harbor stores provenance showing the origin blueprint and version
4. the new project becomes an independent project immediately

This gives reuse value without inheritance complexity.

---

## 9. Partial reuse

Partial reuse is explicitly valuable but not mandatory for v1.

Important examples include:

- evaluation criteria only
- specific subquestion groups
- source strategy only
- gap patterns only
- workflow posture only

This should be designed into the model early, even if the first runtime only
supports full-project snapshot import.

---

## 10. Reuse safety rules

Blueprint reuse must obey these rules:

- no hidden synchronization between source project and derived project
- no silent import of outdated factual conclusions as current truth
- provenance of reuse must be queryable
- operator should understand what was reused
- derived projects must remain independently editable

---

## 11. Blueprint suitability metadata

Harbor should later support human-readable reuse guidance such as:

- suitable for quick projects
- suitable for deep projects
- suitable for travel research
- suitable for monitoring-oriented work
- suitable when strong evaluation criteria are needed
- not ideal when current-time facts dominate

Even if not all of this is implemented immediately, the model should anticipate it.

---

## 12. Relationship to handbook

Blueprints are tightly linked to handbook structure.

In many cases, the reusable value of a project lies mostly in:

- handbook structure
- research decomposition
- criteria definition
- typical gap patterns

Therefore the blueprint system should treat handbook provenance as central.

---

## 13. Relationship to workflow

Blueprint release is not automatic.

A likely future workflow is:

- Active Research
- Review
- Archive
- Blueprint assessment
- Blueprint release

This makes blueprint creation a deliberate quality step, not an accidental side effect.

---

## 14. Exit criteria for this baseline

The blueprint model is sufficiently defined for the current phase when:

- Harbor distinguishes archive from blueprint release
- snapshot import is the accepted v1 reuse rule
- blueprint provenance is required
- future partial reuse is recognized as a design direction
