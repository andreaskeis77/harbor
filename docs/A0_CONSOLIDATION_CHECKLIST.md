# A0 Consolidation Checklist

Status: Active checklist  
Phase: A0.C1

## 1. Objective

Use this checklist to verify and freeze the Harbor A0 documentation baseline.

## 2. Repository presence check

Confirm the following files exist in the repository:

- [ ] `README.md`
- [ ] `docs/INDEX.md`
- [ ] `docs/MASTERPLAN.md`
- [ ] `docs/PROJECT_STATE.md`
- [ ] `docs/HANDOFF_MANIFEST.md`
- [ ] `docs/HANDOFF_GUIDE.md`
- [ ] `docs/ENGINEERING_MANIFEST.md`
- [ ] `docs/WORKING_AGREEMENT.md`
- [ ] `docs/DELIVERY_PROTOCOL.md`
- [ ] `docs/VALIDATION_PROTOCOL.md`
- [ ] `docs/PRODUCT_SCOPE_v0_1.md`
- [ ] `docs/DOMAIN_MODEL_v0_1.md`
- [ ] `docs/USER_STORIES_v0_1.md`
- [ ] `docs/FUNCTIONAL_REQUIREMENTS_v0_1.md`
- [ ] `docs/HANDBOOK_SPEC_v0_1.md`
- [ ] `docs/BLUEPRINT_MODEL_v0_1.md`
- [ ] `docs/WORKFLOW_MODEL_v0_1.md`
- [ ] `docs/SYSTEM_ARCHITECTURE_v0_1.md`
- [ ] `docs/RUNTIME_BOUNDARIES_v0_1.md`
- [ ] `docs/TECHNICAL_BOOTSTRAP_v0_1.md`
- [ ] `docs/REPOSITORY_SCAFFOLDING_v0_1.md`

## 3. Consistency check

Review whether the following are aligned:

- [ ] project partitioning is consistent across scope, domain model, and requirements
- [ ] research handbook is consistently treated as a versioned control object
- [ ] blueprint reuse is consistently snapshot-based rather than live inheritance
- [ ] Postgres remains the system of record across all relevant docs
- [ ] one canonical backend for website and Custom GPT is consistent everywhere
- [ ] later monitoring/agentic behavior is consistently treated as post-v1

## 4. Current-state check

- [ ] `MASTERPLAN.md` reflects the recommended phase order
- [ ] `PROJECT_STATE.md` reflects the honest current state
- [ ] latest handoff reflects the true next step

## 5. Freeze decision

Mark one:

- [ ] A0 baseline accepted
- [ ] A0 baseline accepted with minor follow-up cleanup
- [ ] A0 baseline not yet accepted

## 6. Output requirement

After using this checklist, create or update a handoff that records:

- what was checked
- what was missing
- what was corrected
- whether A0 is accepted
- the next recommended bolt
