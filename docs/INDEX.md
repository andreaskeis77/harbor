# Docs Index

## Start here now
- `MASTERPLAN.md`
- `PROJECT_STATE.md`
- `STRATEGY_ROADMAP_v0_1.md`
- `WORKING_AGREEMENT.md`
- `VALIDATION_PROTOCOL.md`
- `docs/_handoff/HANDOFF_2026-04-10_T4_4B_to_T4_5A.md`

## Strategy / governance
- `MASTERPLAN.md`
- `PROJECT_STATE.md`
- `ENGINEERING_MANIFEST.md`
- `WORKING_AGREEMENT.md`
- `DELIVERY_PROTOCOL.md`
- `VALIDATION_PROTOCOL.md`

## Runbooks / release
- `RUNBOOK_ALPHA_OPERATOR_v0_1.md`
- `RELEASE_CHECKLIST_ALPHA_v0_1.md`

## Accepted A0 baseline
- `PRODUCT_SCOPE_v0_1.md`
- `DOMAIN_MODEL_v0_1.md`
- `USER_STORIES_v0_1.md`
- `FUNCTIONAL_REQUIREMENTS_v0_1.md`
- `HANDBOOK_SPEC_v0_1.md`
- `BLUEPRINT_MODEL_v0_1.md`
- `WORKFLOW_MODEL_v0_1.md`
- `SYSTEM_ARCHITECTURE_v0_1.md`
- `RUNTIME_BOUNDARIES_v0_1.md`
- `TECHNICAL_BOOTSTRAP_v0_1.md`
- `REPOSITORY_SCAFFOLDING_v0_1.md`
- `RUNTIME_CONFIGURATION_v0_1.md`
- `LOCAL_OPERATOR_SURFACE_v0_1.md`
- `PERSISTENCE_FOUNDATION_v0_1.md`
- `POSTGRES_BASELINE_v0_1.md`

## Handoffs
- `docs/_handoff/`

## Concepts
- `docs/concepts/README.md`

## ADRs
- `docs/adr/README.md`

## 2026-04-10 updates

- `LESSONS_LEARNED_T4_5A_2026-04-10.md`
- `docs/_handoff/HANDOFF_2026-04-10_T4_5A_to_T4_5B.md`
- method hardening updates in `ENGINEERING_MANIFEST.md`, `DELIVERY_PROTOCOL.md`, `WORKING_AGREEMENT.md`, and `VALIDATION_PROTOCOL.md`

## 2026-04-11 updates — H1–H4 Hardening Phases

- `LESSONS_LEARNED_H1_2026-04-11.md` — migration consolidation, observability, test infrastructure
- `LESSONS_LEARNED_H2_2026-04-11.md` — typed exceptions, transaction middleware, coverage gate
- `LESSONS_LEARNED_H3_2026-04-11.md` — coverage depth, alembic logger fix, expanded lint rules
- `LESSONS_LEARNED_H4_2026-04-11.md` — validation edge cases, input boundaries, E2E workflow
- `HARBOR_PROJECT_REPORT_2026-04-11.md` — comprehensive project analysis report (updated)
- 56 → 116 tests, 96% coverage, 24 permanent manifest rules
- typed domain exception hierarchy + middleware exception handlers
- request-scoped transaction middleware (commit-on-success / rollback-on-error)
- structured request logging with request-id propagation
- consolidated linear migration chain (10 migrations, 3 integrity tests)
- expanded Ruff rules: E, F, I, B, UP, SIM, PIE, LOG, RUF
- centralized test fixtures (`tests/conftest.py`)
- stale artifact cleanup (`config/.env.example`, orphaned `alembic/` directory)
