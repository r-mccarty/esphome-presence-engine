# RFD: Hammer Review 306db1c

**Commit:** 306db1ca294b21607343a16175b7a8019df8bc8a

**Date:** 2026-01-21

**Author:** Code Review Agent

---

## Summary

This commit adds a new GitHub Actions workflow `.github/workflows/anvil-review.yml` that mirrors the existing `hammer-review.yml` but uses OpenAI Codex (`codex exec`) instead of Claude for automated code reviews. The workflow:

1. Triggers on push to `main`, `dev`, and `feature/**` branches
2. Fetches the prompt generation script from the external `agent-harness` repository
3. Runs the review on a Sprite VM named "anvil" using Codex

The implementation largely copies the hammer-review workflow structure but has several issues including unused variables, a different AI invocation pattern, and inherited heredoc concerns.

---

## Findings

### 1. HIGH: Unused Environment Variables

**Severity:** High
**File:** `.github/workflows/anvil-review.yml`
**Lines:** 21-22

```yaml
      MAX_TURNS: 30
```

and

```yaml
      REVIEWER_NAME: anvil
```

**Analysis:** The `MAX_TURNS` and `REVIEWER_NAME` environment variables are defined but never used in the workflow. In the hammer-review workflow, `MAX_TURNS` is passed to the claude CLI:

```bash
claude --print --output-format json --dangerously-skip-permissions --max-turns ${MAX_TURNS} "\$PROMPT"
```

However, in anvil-review, the codex invocation does not use either variable:

```bash
printf '%s' "$PROMPT" | codex exec --dangerously-bypass-approvals-and-sandbox -
```

**Impact:** This suggests either:
- Incomplete implementation (MAX_TURNS should be passed to codex)
- Dead code that should be removed to avoid confusion

**Recommendation:** Either integrate `MAX_TURNS` with the codex CLI if it supports such a parameter, or remove the unused variables to keep the workflow clean.

### 2. HIGH: Heredoc Indentation Issue (Inherited)

**Severity:** High
**File:** `.github/workflows/anvil-review.yml`
**Lines:** 88-106

The heredoc structure has the same indentation issue as the hammer-review workflow:

```yaml
          REMOTE_SCRIPT=$(cat <<EOF
          set -euo pipefail
          cd /home/sprite/workspace
          ...
          EOF
          )
```

**Analysis:** The closing `EOF` delimiter is indented with spaces. In standard bash, `<<EOF` requires the terminator to be at column 0. However, as noted in RFD-20260121-9f62daf-hammer-review, the hammer workflow appears to work despite this concern, suggesting GitHub Actions may handle the YAML-to-bash conversion in a way that makes this work.

**Recommendation:** Monitor the workflow execution. If it fails, de-indent the heredoc or use `<<-EOF` with tab indentation.

### 3. MEDIUM: Different Prompt Delivery Mechanism

**Severity:** Medium
**File:** `.github/workflows/anvil-review.yml`
**Line:** 104

```bash
printf '%s' "$PROMPT" | codex exec --dangerously-bypass-approvals-and-sandbox -
```

**Analysis:** The anvil workflow pipes the prompt to codex via stdin (the `-` argument indicates stdin input), whereas hammer passes it as a CLI argument. This is a valid approach but has different characteristics:

- **Pros:** Avoids shell argument length limits; safer for prompts containing special characters
- **Cons:** If the prompt is empty or malformed, codex may hang waiting for input or behave unexpectedly

The workflow does not validate that `$PROMPT` is non-empty before piping, which could cause issues.

**Recommendation:** Add validation before the codex invocation:
```bash
if [ -z "$PROMPT" ]; then
  echo "Error: Prompt is empty"
  exit 1
fi
```

### 4. MEDIUM: Additional Branch Trigger (dev)

**Severity:** Medium (Informational)
**File:** `.github/workflows/anvil-review.yml`
**Lines:** 4-8

```yaml
on:
  push:
    branches:
      - main
      - dev
      - "feature/**"
```

**Analysis:** Unlike hammer-review which only triggers on `main` and `feature/**`, anvil-review also triggers on `dev`. This is a deliberate difference but worth noting:

- Two parallel review workflows will now run on `main` and `feature/**` pushes (both hammer and anvil)
- The `dev` branch will only get anvil reviews, not hammer reviews

**Recommendation:** Ensure this asymmetry is intentional. If both reviewers should cover the same branches, align the triggers.

### 5. MEDIUM: External Script Dependency Without Version Pinning (Inherited)

**Severity:** Medium
**File:** `.github/workflows/anvil-review.yml`
**Line:** 82

```bash
PROMPT_B64="$(curl -fsSL -H "$AUTH_HEADER" https://raw.githubusercontent.com/r-mccarty/agent-harness/main/scripts/hammer/build_prompt.py | python | tr -d '\n')"
```

**Analysis:** Same as hammer-review - the workflow fetches `build_prompt.py` from the `main` branch without version pinning. This creates a runtime dependency on external repository state.

**Note:** The script path is `scripts/hammer/build_prompt.py` - if anvil needs different prompt generation logic in the future, this coupling to "hammer" may be confusing.

**Recommendation:** Consider either:
- Creating an anvil-specific prompt script (`scripts/anvil/build_prompt.py`)
- Or renaming the shared script to a neutral path (`scripts/review/build_prompt.py`)
- Pin to a specific commit SHA

### 6. LOW: Missing Error Handling for Empty Prompt

**Severity:** Low
**File:** `.github/workflows/anvil-review.yml`
**Lines:** 102-104

```bash
PROMPT_B64="${PROMPT_B64}"
PROMPT="\$(printf '%s' \"\$PROMPT_B64\" | base64 -d -i)"
printf '%s' "$PROMPT" | codex exec --dangerously-bypass-approvals-and-sandbox -
```

**Analysis:** If `PROMPT_B64` is empty (due to curl failure or script error), `PROMPT` will be empty, and the codex command will receive empty stdin input. Unlike the claude CLI which takes the prompt as an argument (making empty prompts more obvious), piping to codex may silently fail or produce unexpected behavior.

**Recommendation:** Add validation as noted in Finding #3.

### 7. LOW: Potential Resource Conflict

**Severity:** Low
**File:** `.github/workflows/anvil-review.yml`
**Lines:** 15-17

```yaml
    concurrency:
      group: anvil-review-${{ github.ref }}
      cancel-in-progress: false
```

**Analysis:** The concurrency group is correctly scoped to anvil-review, so it won't conflict with hammer-review. However, both workflows will run in parallel on the same commits to `main` and `feature/**` branches. This doubles the compute cost and may create duplicate RFD files with conflicting filenames if both reviewers output to the same `docs/rfd/` directory.

**Recommendation:** If both reviewers should run, ensure their output file naming conventions differ (e.g., `RFD-{date}-{sha}-anvil-review.md` vs `RFD-{date}-{sha}-hammer-review.md`). The current prompt from `build_prompt.py` should handle this, but verify the output naming.

---

## Workflow Comparison

| Aspect | hammer-review.yml | anvil-review.yml |
|--------|-------------------|------------------|
| AI Tool | claude | codex |
| Sprite VM | hammer | anvil |
| Skip Token | `[skip-hammer]` | `[skip-anvil]` |
| Branches | main, feature/** | main, dev, feature/** |
| Prompt Delivery | CLI argument | stdin pipe |
| MAX_TURNS | Used | Defined but unused |

---

## Recommended Actions

### Immediate

1. **Remove or use `MAX_TURNS`** - Either integrate it with codex (if supported) or remove the variable to avoid confusion.

2. **Remove `REVIEWER_NAME`** - This variable is defined but never referenced in the workflow.

3. **Add prompt validation** - Before running codex, validate that `PROMPT` is non-empty:
   ```bash
   if [ -z "$PROMPT" ]; then
     echo "Error: Failed to fetch or generate prompt"
     exit 1
   fi
   ```

### Short-term

4. **Align branch triggers** - Decide whether anvil should review `dev` but hammer should not, or if both should cover the same branches.

5. **Pin external script version** - Use a commit SHA instead of `main` for the `build_prompt.py` fetch.

6. **Consider naming the shared prompt script neutrally** - If both hammer and anvil use the same prompt builder, rename from `scripts/hammer/` to `scripts/review/` or similar.

### Testing

7. **Monitor the first workflow run** - Verify the workflow completes successfully and produces the expected RFD output.

8. **Verify RFD naming** - Ensure anvil and hammer reviews don't create conflicting files when both run on the same commit.

---

## Conclusion

This commit introduces an OpenAI Codex-based code review workflow that parallels the existing Claude-based hammer-review. The implementation is functional but contains unused variables (`MAX_TURNS`, `REVIEWER_NAME`) that indicate either incomplete implementation or copy-paste artifacts that should be cleaned up.

The main risks are:
1. Unused configuration that may confuse future maintainers
2. Missing prompt validation that could cause silent failures
3. Two parallel review workflows running on overlapping branches (intentional but potentially costly)

**Risk Assessment:** Medium - The workflow should function based on the pattern established by hammer-review, but the unused variables and missing validation warrant attention.
