# Harbor Validation Protocol

## Goal

Validation distinguishes discussion, preparation, and accepted state.

## Validation levels

### Discussed
An idea exists, but no artifact baseline exists.

### Prepared
Files exist, but they have not yet been confirmed in the real repository state.

### Validated
The files are in the repository and were reviewed or checked.

### Accepted
The validated state is explicitly accepted as the current baseline.

## T1.0 expected minimum checks

- importability of the package
- `/healthz`
- pytest green
- ruff green
- compileall green
