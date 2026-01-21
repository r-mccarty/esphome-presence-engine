# RFD: Anvil Review e94ea1b

**Commit:** e94ea1b2387e3ab760c0c73c244df74facdcec55

**Date:** 2026-01-21

**Author:** Code Review Agent

---

## Summary

This change fixes the anvil review workflow to pass the decoded prompt through to Codex on the
remote Sprite VM. The adjustment ensures the prompt variable is not expanded too early when
building the remote script, so Codex receives the intended content.

---

## Findings

None.

---

## Recommended Actions

- Monitor the next anvil workflow run to confirm the prompt reaches Codex as expected.
