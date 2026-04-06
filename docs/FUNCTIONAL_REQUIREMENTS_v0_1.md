# Harbor – Functional Requirements v0.1

Status: Draft baseline for product definition phase  
Phase: A0.3  
Scope: Initial functional requirements for Harbor

---

## 1. Purpose

This document translates the current Harbor scope and user stories into an initial functional requirement set.

The purpose is not yet to define implementation details. The purpose is to define what Harbor must be able to do at the product level.

---

## 2. Requirement conventions

- **FR** = Functional Requirement
- Requirements marked **V1 Core** are expected to be in the first meaningful implementation slice.
- Requirements marked **Later** are intentionally modeled now but are not mandatory for the first implementation slice.

---

## 3. Project management requirements

### FR-001 — Harbor shall support creation of a new project.  
Priority: **V1 Core**

### FR-002 — Harbor shall store each project as a distinct top-level research space.  
Priority: **V1 Core**

### FR-003 — Harbor shall support listing existing projects.  
Priority: **V1 Core**

### FR-004 — Harbor shall support opening and working within one selected project context at a time.  
Priority: **V1 Core**

### FR-005 — Harbor shall support project status transitions at least across draft, active, review, and archived states.  
Priority: **V1 Core**

### FR-006 — Harbor shall support project typing at least for quick, standard, and deep project modes.  
Priority: **V1 Core**

### FR-007 — Harbor shall preserve archived projects without data loss.  
Priority: **V1 Core**

---

## 4. Research handbook requirements

### FR-008 — Harbor shall maintain a project-specific Research Handbook for every project.  
Priority: **V1 Core**

### FR-009 — Harbor shall support editing and versioning of the Research Handbook.  
Priority: **V1 Core**

### FR-010 — Harbor shall preserve prior handbook versions.  
Priority: **V1 Core**

### FR-011 — Harbor shall represent at least the following handbook sections: project goal, primary question, subquestions, in-scope, out-of-scope, evaluation criteria, search strategy, gaps, and change history.  
Priority: **V1 Core**

### FR-012 — Harbor shall allow a project scope to be expanded, narrowed, or corrected after initial creation.  
Priority: **V1 Core**

---

## 5. Source and evidence requirements

### FR-013 — Harbor shall support adding sources to a project.  
Priority: **V1 Core**

### FR-014 — Harbor shall distinguish a globally identified source from its project-specific interpretation or relevance.  
Priority: **V1 Core**

### FR-015 — Harbor shall support classification of sources by type, review status, and relevance.  
Priority: **V1 Core**

### FR-016 — Harbor shall support storing source snapshots or source artifacts for traceability where applicable.  
Priority: **V1 Core**

### FR-017 — Harbor shall support storing manually supplied files or notes as project-relevant evidence.  
Priority: **V1 Core**

### FR-018 — Harbor shall support extraction or storage of searchable evidence units derived from sources.  
Priority: **V1 Core**

### FR-019 — Harbor shall preserve provenance links from derived evidence back to source and snapshot context.  
Priority: **V1 Core**

---

## 6. Search and refresh requirements

### FR-020 — Harbor shall support launching an initial project-specific source search.  
Priority: **V1 Core**

### FR-021 — Harbor shall support launching a refresh against already known project sources.  
Priority: **V1 Core**

### FR-022 — Harbor shall record search and refresh runs as distinct project activities.  
Priority: **V1 Core**

### FR-023 — Harbor shall record whether newly discovered material is accepted, pending review, duplicate, or rejected.  
Priority: **V1 Core**

### FR-024 — Harbor should support repeated discovery searches for newly emerging sources after the initial research phase.  
Priority: **Later / likely V2**

### FR-025 — Harbor should support more explicit update and delta handling for meaningful changes versus noise.  
Priority: **Later / likely V2**

---

## 7. Review and resume requirements

### FR-026 — Harbor shall support a project review view that shows newly added or changed material since a prior review point.  
Priority: **V1 Core**

### FR-027 — Harbor shall support a project resume view that summarizes current scope, recent changes, open gaps, and next sensible actions.  
Priority: **V1 Core**

### FR-028 — Harbor shall support identification of unreviewed items within a project.  
Priority: **V1 Core**

### FR-029 — Harbor shall support explicit review decisions on sources, candidates, and relevant project artifacts.  
Priority: **V1 Core**

---

## 8. Analysis and gap requirements

### FR-030 — Harbor shall support storing project-specific analyses derived from the current evidence base.  
Priority: **V1 Core**

### FR-031 — Harbor shall distinguish analyses from primary sources and evidence artifacts.  
Priority: **V1 Core**

### FR-032 — Harbor shall support explicit capture of research gaps or unresolved questions within a project.  
Priority: **V1 Core**

### FR-033 — Harbor shall support associating research gaps with handbook sections, subquestions, or source limitations where relevant.  
Priority: **V1 Core**

---

## 9. Blueprint and reuse requirements

### FR-034 — Harbor shall support marking an archived project as blueprint-eligible or blueprint-approved.  
Priority: **V1 Core**

### FR-035 — Harbor shall support creation of a new project from a selected blueprint.  
Priority: **V1 Core**

### FR-036 — Harbor shall preserve a provenance reference from the derived project to the blueprint and blueprint version it came from.  
Priority: **V1 Core**

### FR-037 — Harbor shall ensure that a project derived from a blueprint becomes independently editable after creation.  
Priority: **V1 Core**

### FR-038 — Harbor should later support partial reuse of selected blueprint sections, patterns, or modules.  
Priority: **Later / likely V2**

---

## 10. Interaction surface requirements

### FR-039 — Harbor shall provide a web interface as an operational project workspace.  
Priority: **V1 Core**

### FR-040 — Harbor shall support interaction through a Custom GPT connected to the same backend state.  
Priority: **V1 Core**

### FR-041 — Harbor shall ensure that website and Custom GPT operate against the same canonical project state.  
Priority: **V1 Core**

### FR-042 — Harbor should provide equivalent access to core project actions across both primary surfaces where practical.  
Priority: **V1 Core**

---

## 11. Run history and continuity requirements

### FR-043 — Harbor shall preserve a history of meaningful project activities such as handbook changes, searches, refreshes, and review actions.  
Priority: **V1 Core**

### FR-044 — Harbor shall provide enough recorded context to understand what happened in a project over time.  
Priority: **V1 Core**

### FR-045 — Harbor shall support continued work on a project after interruptions or longer inactivity.  
Priority: **V1 Core**

---

## 12. Monitoring and agentic horizon requirements

### FR-046 — Harbor should be designed so that scheduled refresh and discovery policies can be added later without breaking the core project model.  
Priority: **Later / likely V2**

### FR-047 — Harbor should be designed so that agentic source discovery and update monitoring can later generate candidates and review work rather than silently mutating accepted knowledge.  
Priority: **Later / likely V3**

### FR-048 — Harbor should later support monitoring policies at the project level.  
Priority: **Later / likely V2/V3**

---

## 13. Explicit non-requirements for the first implementation slice

The following are intentionally not required for the initial implementation slice:

- full multi-user collaboration,
- unrestricted autonomous agents,
- full login/paywall automation,
- live inheritance between blueprints and derived projects,
- enterprise-grade permission models,
- unlimited global cross-project knowledge blending.

---

## 14. Minimum v1 core requirement set

The minimum meaningful Harbor v1 slice should satisfy at least:

- FR-001 to FR-023
- FR-026 to FR-037
- FR-039 to FR-045

This would establish:

- project creation and separation,
- handbook management,
- source and evidence handling,
- manual initial search and refresh,
- review and resume,
- blueprint-based reuse,
- canonical backend continuity across web and GPT.

---

## 15. Summary

The current functional baseline confirms that Harbor v1 is not primarily a generalized autonomous research agent.

Harbor v1 is a governed, project-based research memory and workflow system with:

- separated project spaces,
- versioned project definition,
- evidence-aware source handling,
- reviewable updates,
- reusable blueprint structures,
- and one canonical backend shared by web and Custom GPT.
