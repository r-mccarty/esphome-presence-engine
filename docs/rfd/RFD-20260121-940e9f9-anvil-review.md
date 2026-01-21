# RFD: Anvil Review 940e9f9

**Commit:** 940e9f9ea7dfe968290ca54368e0250607e1d0a7

**Date:** 2026-01-21

**Author:** Code Review Agent

---

## Summary

This commit adds a cleanup step in the anvil-review workflow to delete a stale
`.git/index.lock` before fetching and checking out the target SHA. The intent is
preventing the workflow from failing when a previous git process left a lock
file behind.

---

## Findings

### 1. MEDIUM: Lock Removal Can Mask Active Git Operations

**File:** `.github/workflows/anvil-review.yml`
**Lines:** 95-97

**Risk:** The workflow unconditionally removes `.git/index.lock` if it exists. If
another git process is running in the same workspace (for example, a concurrent
job or a hung but still-active process), deleting the lock can lead to index
corruption or partial writes. This is a low-likelihood scenario in CI, but the
workflow targets a shared path (`/home/sprite/workspace/${REPO_NAME}`), which
makes concurrency a non-zero risk.

---

## Recommended Actions

1. Before deleting `.git/index.lock`, add a guard to ensure no git process is
   active in the repo (for example, check `lsof`/`fuser` on the lock file or
   verify no `git` process owns that directory).
2. Log when the lock is removed so failures can be correlated to cleanup actions
   during workflow troubleshooting.
