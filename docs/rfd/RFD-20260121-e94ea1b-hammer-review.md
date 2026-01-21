# RFD: Hammer Review e94ea1b

**Commit:** e94ea1b2387e3ab760c0c73c244df74facdcec55

**Date:** 2026-01-21

**Author:** Code Review Agent

---

## Summary

This commit fixes a shell variable expansion bug in the anvil-review GitHub Actions workflow. The change ensures the `$PROMPT` variable is properly escaped within the heredoc so it expands in the remote Sprite VM context rather than prematurely in the GitHub Actions runner.

**Change:**
```diff
-          printf '%s' "$PROMPT" | codex exec --dangerously-bypass-approvals-and-sandbox -
+          printf '%s' "\$PROMPT" | codex exec --dangerously-bypass-approvals-and-sandbox -
```

---

## Findings

### 1. HIGH: Correctly Fixes Premature Variable Expansion (Positive)

**Severity:** Critical fix (resolves a blocking bug)
**File:** `.github/workflows/anvil-review.yml`
**Line:** 104

**Analysis:** The previous code had `"$PROMPT"` inside the heredoc. Since the heredoc uses `<<EOF` (not `<<'EOF'` with single quotes), variables inside it are subject to expansion. The issue was:

1. `PROMPT` is defined **inside** the remote script (line 103): `PROMPT="\$(printf '%s' \"\$PROMPT_B64\" | base64 -d -i)"`
2. The `printf '%s' "$PROMPT" | codex exec ...` line was being expanded in the **outer** GitHub Actions shell context
3. At that point, `$PROMPT` doesn't exist in the outer shell, so it would expand to an empty string
4. The result: codex would receive empty stdin, causing the review to fail

The fix properly escapes `$PROMPT` as `\$PROMPT`, so the variable reference is preserved in the string and only expanded when the remote script actually runs inside the Sprite VM.

**Impact:** This was a critical bug that would have caused the anvil-review workflow to silently fail or produce no output. The fix is correct and necessary.

**Verification:** The fix follows the same pattern already established for `PROMPT_B64` on line 102 (`PROMPT_B64="${PROMPT_B64}"`) and the `PROMPT` assignment on line 103, which both use proper escaping.

### 2. LOW: Inconsistent Escaping Style in Heredoc

**Severity:** Low (cosmetic/maintainability)
**File:** `.github/workflows/anvil-review.yml`
**Lines:** 102-104

**Analysis:** The heredoc now has two different escaping styles:

```bash
PROMPT_B64="${PROMPT_B64}"      # Outer variable, expanded immediately (correct)
PROMPT="\$(printf '%s' \"\$PROMPT_B64\" | base64 -d -i)"  # Escaped for remote execution (correct)
printf '%s' "\$PROMPT" | codex exec ...  # Escaped for remote execution (correct - after this fix)
```

This is functionally correct but may be confusing to future maintainers:
- `${PROMPT_B64}` on line 102 is intentionally expanded in the outer shell (to inject the value into the remote script)
- `\$PROMPT` and `\$PROMPT_B64` are escaped to defer expansion to the remote shell

**Recommendation:** No action needed. The pattern is correct. Consider adding a comment explaining the escaping strategy if this becomes a maintenance concern.

### 3. INFO: Previously Identified Issues Remain Unaddressed

**Severity:** Informational
**File:** `.github/workflows/anvil-review.yml`

The following issues from RFD-20260121-306db1c-hammer-review remain present:

1. **Unused `MAX_TURNS` variable** (line 22) - Not passed to codex
2. **Unused `REVIEWER_NAME` variable** (line 20) - Never referenced
3. **Missing prompt validation** - No check for empty prompt before piping to codex
4. **Unpinned external script dependency** (line 82) - `build_prompt.py` fetched from `main` branch

These are not regressions from this commit and were intentionally out of scope for this fix.

---

## Technical Deep Dive: Heredoc Variable Expansion

For context, here's how shell heredoc expansion works:

| Syntax | Behavior |
|--------|----------|
| `<<EOF` | Variables and commands are expanded |
| `<<'EOF'` | Literal string, no expansion |
| `<<-EOF` | Same as `<<EOF` but strips leading tabs |

With `<<EOF`, any `$VAR` or `$(cmd)` is expanded before the heredoc content is passed to the command. To defer expansion, you must escape: `\$VAR` or `\$(cmd)`.

In this workflow:
- `${PROMPT_B64}` (line 102) - Intentionally expanded to inject the base64 prompt value
- `\$PROMPT_B64` (line 103) - Escaped so it's expanded in the remote shell
- `\$PROMPT` (line 104, after fix) - Escaped so it's expanded in the remote shell

---

## Recommended Actions

### None Required

This is a correct and minimal fix for a critical bug. The change:

1. **Is correct** - The escaping is necessary and properly applied
2. **Is minimal** - Only the one line that needed fixing was modified
3. **Follows existing patterns** - Consistent with the escaping used elsewhere in the same heredoc

### Optional Follow-ups (from prior RFD)

These are not blockers but were noted in the prior review:

1. Remove or use `MAX_TURNS` and `REVIEWER_NAME` variables
2. Add prompt validation before codex invocation
3. Pin the external `build_prompt.py` script to a specific commit

---

## Conclusion

This commit correctly fixes a shell variable expansion bug that would have caused the anvil-review workflow to fail. The `$PROMPT` variable was being expanded in the GitHub Actions runner context (where it doesn't exist) instead of the remote Sprite VM context (where it's defined). The fix properly escapes the variable as `\$PROMPT` to defer expansion.

**Risk Assessment:** None - This is a correct bug fix with no side effects. The workflow should now function as intended.
