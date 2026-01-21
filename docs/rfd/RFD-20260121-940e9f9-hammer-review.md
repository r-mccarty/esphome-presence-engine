# RFD: Hammer Review 940e9f9

**Commit:** 940e9f9ea7dfe968290ca54368e0250607e1d0a7

**Date:** 2026-01-21

**Author:** Code Review Agent

---

## Summary

This commit adds defensive cleanup of stale `.git/index.lock` files in the anvil-review GitHub Actions workflow. The change removes any leftover git lock file before performing `git fetch` operations to prevent failures caused by previously interrupted or crashed git operations in the persistent Sprite VM workspace.

**Change:**
```diff
@@ -92,6 +92,9 @@ jobs:
             git clone https://github.com/${REPO_FULL}.git "${REPO_NAME}"
           fi
           cd "/home/sprite/workspace/${REPO_NAME}"
+          if [ -f ".git/index.lock" ]; then
+            rm -f .git/index.lock
+          fi
           git fetch origin
```

The fix is inserted at `.github/workflows/anvil-review.yml` lines 95-97.

---

## Findings

### 1. LOW: Race Condition Risk with Lock File Removal

**Severity:** Low
**File:** `.github/workflows/anvil-review.yml`
**Lines:** 95-97

**Analysis:** The pattern of checking for a lock file and then removing it has an inherent TOCTOU (time-of-check-time-of-use) race condition:

```bash
if [ -f ".git/index.lock" ]; then
  rm -f .git/index.lock
fi
```

Between the `[ -f ... ]` check and the `rm -f`, the file could theoretically be created by another process. However, in practice:

1. The Sprite VM runs workflows with `concurrency: group: anvil-review-${{ github.ref }}` and `cancel-in-progress: false`, meaning only one anvil-review can run at a time for a given branch
2. The `rm -f` would succeed even if the file was just created or already removed
3. The check is primarily defensive against stale locks from prior runs, not concurrent operations

**Risk Assessment:** Negligible. The concurrency controls make this a non-issue, and the `-f` flag on `rm` handles edge cases gracefully.

### 2. INFO: Incomplete Lock File Coverage

**Severity:** Informational
**File:** `.github/workflows/anvil-review.yml`
**Lines:** 95-97

**Analysis:** Git can create multiple lock files depending on the operation:

| Lock File | Created By |
|-----------|------------|
| `.git/index.lock` | `git add`, `git commit`, `git checkout`, etc. |
| `.git/HEAD.lock` | Operations that modify HEAD |
| `.git/config.lock` | Config modifications |
| `.git/refs/heads/<branch>.lock` | Branch operations |

The commit only removes `.git/index.lock`. For a workflow that runs `git fetch`, `git checkout`, and `git reset`, the most likely stale lock is indeed `index.lock`, but other lock files could theoretically cause issues.

**Recommendation:** The current fix addresses the most common case. If other lock file issues arise, they can be addressed then. No action needed now.

### 3. INFO: Root Cause Not Addressed

**Severity:** Informational
**File:** `.github/workflows/anvil-review.yml`

**Analysis:** The presence of stale lock files indicates that prior workflow runs are not terminating cleanly. Possible root causes:

1. Sprite VM timeout killing processes mid-operation
2. Network interruptions during remote git operations
3. Codex subprocess termination issues
4. The `cancel-in-progress: false` setting means workflows queue rather than cancel, which is good, but long-running or stuck jobs could be problematic

This fix is a valid defensive measure, but monitoring for recurring lock file issues might reveal underlying stability problems worth investigating.

### 4. INFO: Previously Identified Issues Remain Unaddressed

**Severity:** Informational
**File:** `.github/workflows/anvil-review.yml`

The following issues from prior RFDs remain present:

1. **Unused `MAX_TURNS` variable** (line 22) - Not passed to codex
2. **Unused `REVIEWER_NAME` variable** (line 20) - Never referenced
3. **Missing prompt validation** - No check for empty prompt before piping to codex
4. **Unpinned external script dependency** (line 82) - `build_prompt.py` fetched from `main` branch

These are not regressions from this commit and remain intentionally out of scope for this fix.

---

## Technical Context: Git Lock Files

Git uses lock files to prevent concurrent modifications to repository state. The `.git/index.lock` file is created when git is modifying the index (staging area) and is automatically removed when the operation completes.

A stale lock file occurs when:
- A git operation is interrupted (e.g., process killed, network timeout)
- A system crash occurs during a git operation
- A bug causes git to not properly clean up

The standard recovery is to manually remove the lock file, which is exactly what this fix automates for the CI environment.

---

## Recommended Actions

### None Required

This is a correct and appropriate defensive fix for a CI environment. The change:

1. **Is correct** - Removing stale lock files before git operations is standard practice
2. **Is minimal** - Only addresses the specific issue without over-engineering
3. **Is safe** - The `-f` flag ensures the `rm` command succeeds even if the file doesn't exist
4. **Is well-placed** - Positioned after `cd` into the repo but before any git operations

### Optional Monitoring

If stale lock files become a recurring issue, consider:

1. Adding logging when a lock file is removed (`echo "Removed stale index.lock"`) to track frequency
2. Investigating why prior runs are not terminating cleanly
3. Extending to cover other git lock files if needed

---

## Conclusion

This commit adds a sensible defensive measure to handle stale git lock files in the Sprite VM workspace. Lock files can be left behind when previous workflow runs are interrupted, and this fix ensures the anvil-review workflow can proceed even in those cases.

**Risk Assessment:** None - This is a standard CI hygiene fix with no side effects. The workflow should be more robust against stale git state.
