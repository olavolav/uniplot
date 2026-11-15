# Version control

The user performs all version-control operations manually, without exceptions.
Do not run commands that change version-control state, including staging,
committing, branching, switching branches, merging, rebasing, resetting,
stashing, tagging, pulling, or pushing. Read-only inspection is permitted.

# Project verification

Before handing control back to the user after project work, run `make test` and
ensure it passes. Fix failures and rerun the suite before finishing. If a blocker
prevents a passing run, report the blocker and the verification status explicitly.
