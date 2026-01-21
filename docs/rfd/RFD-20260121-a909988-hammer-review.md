# RFD: Hammer Review a909988

**Commit:** a909988efd8c005fe9f8359f8b8644da7f9f1f02

**Date:** 2026-01-21

**Author:** Code Review Agent

---

## Summary

This commit re-indents the heredoc content in `.github/workflows/hammer-review.yml` to align with the surrounding YAML indentation level. Specifically, the Python code inside the `<<'PY'` heredoc and the bash script inside the `<<EOF` heredoc are both indented to match the YAML block structure.

The change appears to be cosmetic (improving YAML visual consistency), but introduces a **critical functional regression** due to how heredocs handle leading whitespace.

---

## Findings

### 1. CRITICAL: Python Heredoc Indentation Breaks Python Syntax

**Severity:** Critical
**File:** `.github/workflows/hammer-review.yml`
**Lines:** 77-110 (post-change)

The Python code inside the heredoc starting at line 77 is now indented with 10 leading spaces:

```yaml
          PROMPT_B64="$(python - <<'PY'
          import base64
          import os
          ...
          PY
          )"
```

**Problem:** Heredocs in bash preserve all content literally, including leading whitespace. When `python -` receives this code, it will see every line with 10 leading spaces. Python will interpret this as an `IndentationError` because:
- The first `import base64` line starts at column 10
- Python expects top-level statements to start at column 0

**Expected Error:**
```
IndentationError: unexpected indent
```

**Evidence from diff:**
```diff
-          PROMPT_B64="$(python - <<'PY'
-import base64
-import os
+          PROMPT_B64="$(python - <<'PY'
+          import base64
+          import os
```

The original code correctly had Python statements at column 0 within the heredoc.

### 2. CRITICAL: Bash Heredoc Indentation Causes Script Failure

**Severity:** Critical
**File:** `.github/workflows/hammer-review.yml`
**Lines:** 116-134 (post-change)

The bash script inside the `<<EOF` heredoc is now indented:

```yaml
          REMOTE_SCRIPT=$(cat <<EOF
          set -euo pipefail
          cd /home/sprite/workspace
          ...
          EOF
          )
```

**Problem:** The `EOF` delimiter is now indented, but bash heredocs require the closing delimiter to match exactly. While `<<-EOF` allows for tab-indented terminators, regular `<<EOF` requires the terminator at column 0.

Additionally, even if the terminator worked, the script content now has leading whitespace which:
- Could cause issues with shebang-like first lines
- Changes the actual script content being passed to `sprite exec`

**The closing `EOF` has 10 leading spaces**, which means bash won't recognize it as the heredoc terminator, causing the heredoc to remain open and likely result in a syntax error or unexpected behavior.

### 3. LOW: Inconsistent Tab vs Space Usage Risk

**Severity:** Low
**File:** `.github/workflows/hammer-review.yml`

If the intent was to use `<<-` heredocs (which strip leading tabs), the current implementation uses spaces, not tabs. The `<<-` syntax only strips leading tabs, not spaces.

---

## Recommended Actions

### Immediate (Before Merge)

1. **Revert the heredoc indentation changes** - The Python and Bash heredocs must have their content at column 0 (or use proper heredoc syntax for indented content).

2. **Alternative fix if indentation is desired:**
   - For Python: Use `<<-'PY'` with tabs (not spaces), OR use `python -c` with properly escaped strings, OR use a separate Python script file
   - For Bash: Use `<<-EOF` with tabs (not spaces) for indented terminator

### Recommended Fix

Revert to the previous commit's heredoc formatting:

```yaml
          PROMPT_B64="$(python - <<'PY'
import base64
import os
...
PY
)"
```

and:

```yaml
          REMOTE_SCRIPT=$(cat <<EOF
set -euo pipefail
cd /home/sprite/workspace
...
EOF
)
```

### Testing Recommendation

Before future changes to this workflow:
1. Add a test workflow or local test that validates the Python and Bash heredocs execute correctly
2. Consider extracting the Python/Bash scripts to separate files (e.g., `scripts/generate_prompt.py`, `scripts/remote_review.sh`) to avoid heredoc complexity

---

## Conclusion

This commit introduces a **critical regression** that will cause the Hammer Review workflow to fail on every invocation. The Python code will fail with `IndentationError` and the Bash heredoc terminator won't be recognized. The commit should be reverted or fixed before any subsequent workflow runs.
