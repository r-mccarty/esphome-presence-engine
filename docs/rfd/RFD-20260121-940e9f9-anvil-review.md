# RFD: Anvil Review 940e9f9

**Commit:** 940e9f9ea7dfe968290ca54368e0250607e1d0a7

**Date:** 2026-01-21

**Author:** Code Review Agent

---

## Summary

This commit adds a cleanup step in the anvil-review workflow to delete a stale
`.git/index.lock` before fetching and checking out the target SHA. The intent is to
prevent the workflow from failing when a previous git process left a lock file
behind.

---

## Findings

### 1. LOW: Lock removal does not verify the lock is stale

**File:** `.github/workflows/anvil-review.yml`
**Line:** 95-97

The workflow deletes `.git/index.lock` unconditionally when present. If another
git process is actively running in the same workspace, removing the lock can
corrupt repository state or interrupt the in-flight operation. The workflow
likely runs single-threaded in CI, so this is a low-probability risk, but it is
still a sharp edge without a guard.

### 2. INFO: No visibility when a lock is cleared

**File:** `.github/workflows/anvil-review.yml`
**Line:** 95-97

The removal happens silently. If a stale lock appears repeatedly, there is no
log signal to indicate the cleanup is occurring, which can make diagnosing the
underlying cause harder.

---

## Recommended Actions

1. Verify the lock is stale before deletion (for example, ensure no git process
   is running or retry `git fetch` once before removing the lock).
2. Add a short log line when a lock is cleared so repeated lock incidents are
   visible in CI logs.
