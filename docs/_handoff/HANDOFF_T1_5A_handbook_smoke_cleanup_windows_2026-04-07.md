# HANDOFF_T1_5A_handbook_smoke_cleanup_windows_2026-04-07

- Scope: stabilize Windows cleanup behavior for `smoke-handbook-slice`.
- Change: use `ignore_cleanup_errors=True` in the handbook temp-directory helper.
- Intent: avoid non-blocking Windows temp-file cleanup failures after successful smoke execution.
- Follow-up: keep this scoped to operator-surface smoke behavior only.
