# RFD: Hammer Review 9f62daf

**Commit:** 9f62daf77bcab9052af16ebe659eaa112135b092

**Date:** 2026-01-21

**Author:** Code Review Agent

---

## Summary

This commit refactors `.github/workflows/hammer-review.yml` to:
1. Centralize prompt generation by fetching `build_prompt.py` from the `agent-harness` repo
2. Fix the Authorization header format (from escaped quotes to a variable)
3. Add `tr -d '\n'` to strip trailing newlines from base64 output
4. Restructure the heredoc for the remote script execution on the sprite VM

The changes address issues from the previous commit (e01bfaf) which had a broken heredoc structure, but introduce new concerns around the heredoc syntax and variable expansion.

---

## Findings

### 1. HIGH: Heredoc Indentation May Cause Script Content Issues

**Severity:** High
**File:** `.github/workflows/hammer-review.yml`
**Lines:** 85-102

The heredoc content is indented with 10 leading spaces:

```yaml
          REMOTE_SCRIPT=$(cat <<EOF
          set -euo pipefail
          cd /home/sprite/workspace
          ...
          EOF
          )
```

**Analysis:** Unlike the previous RFD's findings about heredoc delimiters not matching, this commit has a different issue. The closing `EOF` is also indented, which in standard bash would cause the heredoc to not terminate properly. However, there are two possibilities:

1. If the YAML runner strips leading whitespace before passing to bash, this would work
2. If the content is passed as-is, the script would have 10 leading spaces on each line

Since GitHub Actions runs this in a bash shell, the indented `EOF` terminator will likely **not** be recognized, causing a syntax error or the heredoc to capture more content than intended.

**Evidence from current file (lines 85-103):**
```yaml
          REMOTE_SCRIPT=$(cat <<EOF
          set -euo pipefail
          ...
          EOF
          )
```

The `EOF` at line 102 has leading spaces, which bash's `<<EOF` syntax will not recognize as the terminator.

**Recommendation:** Either:
- Use `<<-EOF` with tabs (not spaces) for the terminator
- Or de-indent the heredoc content and terminator to column 0

### 2. MEDIUM: Variable Expansion in Heredoc May Cause Issues

**Severity:** Medium
**File:** `.github/workflows/hammer-review.yml`
**Lines:** 99-101

Inside the heredoc, there's complex variable interpolation:

```bash
          PROMPT_B64="${PROMPT_B64}"
          PROMPT="\$(printf '%s' \"\$PROMPT_B64\" | base64 -d -i)"
          claude --print --output-format json --dangerously-skip-permissions --max-turns ${MAX_TURNS} "\$PROMPT"
```

**Analysis:** The heredoc uses `<<EOF` (not `<<'EOF'`), so variable expansion occurs. The mix of:
- `${PROMPT_B64}` - expanded at heredoc creation time (correct)
- `\$PROMPT_B64` - escaped to be literal `$PROMPT_B64` for the remote script (correct)
- `${MAX_TURNS}` - expanded at heredoc creation time (correct)
- `\$PROMPT` - escaped for remote script (correct)

The escaping appears correct, but the complexity makes this error-prone.

**Minor Issue:** The use of `base64 -d -i` is correct (`-i` ignores non-alphabet characters), but not all `base64` implementations support `-i`. GNU coreutils does, but this should work in the sprite VM.

### 3. MEDIUM: External Script Dependency Without Version Pinning

**Severity:** Medium
**File:** `.github/workflows/hammer-review.yml`
**Line:** 79

```bash
PROMPT_B64="$(curl -fsSL -H "$AUTH_HEADER" https://raw.githubusercontent.com/r-mccarty/agent-harness/main/scripts/hammer/build_prompt.py | python | tr -d '\n')"
```

**Analysis:** The workflow fetches `build_prompt.py` from the `main` branch of `agent-harness`. This creates:
- A runtime dependency on an external repository
- No version pinning - changes to `build_prompt.py` could break this workflow
- If the external script has bugs or is unavailable, the workflow fails

**Recommendation:**
- Pin to a specific commit SHA or tag instead of `main`
- Or vendor the script locally in this repository
- Consider adding error handling if curl fails

### 4. LOW: Authorization Header Format Change

**Severity:** Low (Informational)
**File:** `.github/workflows/hammer-review.yml`
**Line:** 78

Changed from:
```bash
PROMPT_B64="$(curl -fsSL -H \"Authorization: Bearer ${AGENT_HARNESS_TOKEN}\" ...)"
```

To:
```bash
AUTH_HEADER="Authorization: token ${AGENT_HARNESS_TOKEN}"
PROMPT_B64="$(curl -fsSL -H "$AUTH_HEADER" ...)"
```

**Analysis:** The fix uses `token` instead of `Bearer` for the GitHub API. Both formats work with GitHub's API, but `token` is the traditional format for Personal Access Tokens and `GITHUB_TOKEN`. This change is correct and also fixes the quoting issue from the previous commit.

### 5. LOW: Missing Error Handling for External Script Execution

**Severity:** Low
**File:** `.github/workflows/hammer-review.yml`
**Line:** 79

If the external `build_prompt.py` fails or returns empty output, `PROMPT_B64` will be empty, but the workflow continues execution. This could lead to the claude command receiving an empty prompt.

**Recommendation:** Add a check after fetching the prompt:
```bash
if [ -z "$PROMPT_B64" ]; then
  echo "Failed to generate prompt"
  exit 1
fi
```

---

## Workflow Status

The workflow run (https://github.com/r-mccarty/esphome-presence-engine/actions/runs/21211437603) was observed as "in_progress" during this review. The "Run hammer review" step was actively executing, suggesting the workflow **has progressed past** the heredoc parsing stage, which indicates the heredoc syntax may be working despite the indentation concerns.

---

## Recommended Actions

### Immediate

1. **Monitor the current workflow run** - If it completes successfully, the heredoc concerns may not be blocking issues in the GitHub Actions environment.

2. **Add prompt validation** - Before running claude, validate that `PROMPT_B64` is non-empty:
   ```bash
   if [ -z "$PROMPT_B64" ]; then
     echo "Error: Failed to fetch or generate prompt"
     exit 1
   fi
   ```

### Short-term

3. **Pin the external script version** - Use a commit SHA instead of `main`:
   ```bash
   https://raw.githubusercontent.com/r-mccarty/agent-harness/<commit-sha>/scripts/hammer/build_prompt.py
   ```

4. **Consider local vendoring** - If `build_prompt.py` is stable, copy it into this repository to eliminate the external dependency.

### Testing Recommendations

5. **Add workflow validation** - Test the heredoc syntax locally before committing:
   ```bash
   bash -n script.sh  # Syntax check
   shellcheck script.sh  # Linting
   ```

6. **Add a dry-run option** - Consider a `workflow_dispatch` input to test the workflow without actually running claude.

---

## Conclusion

This commit makes meaningful progress in aligning the hammer review runner by:
- Fixing the Authorization header quoting issues from e01bfaf
- Centralizing prompt generation to an external, maintainable script
- Cleaning up the base64 output with `tr -d '\n'`

The heredoc indentation is the primary concern, though the active workflow suggests it may work in the GitHub Actions environment. The external script dependency adds fragility that should be addressed with version pinning.

**Risk Assessment:** Medium - The workflow appears functional based on the in-progress run, but the indented heredoc and external dependency introduce maintainability and reliability concerns.
