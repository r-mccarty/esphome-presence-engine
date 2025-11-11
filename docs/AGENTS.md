# AGENTS.md – Documentation Directory

This file covers everything under `docs/`. For repo-wide orientation read
`../CLAUDE.md` first; it points to the authoritative specs and workflows this
directory depends on.

## Before You Edit
1. **Confirm context** – Re-read `../CLAUDE.md` plus the relevant deep dives
   (`docs/ARCHITECTURE.md`, `docs/presence-engine-spec.md`,
   `docs/development-scorecard.md`) so terminology and defaults stay aligned.
2. **Map ownership** – Historical notes belong in
   `docs/development-scorecard.md`, workflow/process content in
   `docs/DEVELOPMENT_WORKFLOW.md`, hardware specifics in
   `docs/HARDWARE_SETUP.md`, and operator guidance in `docs/quickstart.md`,
   `docs/calibration.md`, or `docs/troubleshooting.md`. Keep this directory
   tidy by filing updates in the right document instead of bloating AGENTS.md.

## Scope & Expectations
- Maintain the written source of truth for the Phase 3 firmware and the
  Phase 3.1+ objectives (calibration persistence, analytics, monitoring).
- Ensure instructions describe the two-machine workflow (Codespaces ↔
  ubuntu-node) whenever flashing, HA access, or scripts are mentioned.
- Keep entity IDs, defaults (`μ=6.7%`, `σ=3.5%`, `k_on=9.0`, etc.), and UI
  screenshots synchronized with ESPHome + Home Assistant configs.
- Reference other docs rather than rewriting them here; link using relative
  paths.

## Authoring Checklist
- [ ] Facts reflect the current firmware, HA dashboard, and helper entities.
- [ ] Phase status is clear (Phase 3 deployed, Phase 3.1+ in flight).
- [ ] Two-machine steps specify which host runs each command.
- [ ] Cross-references point to the five flagship docs highlighted in
      `../CLAUDE.md` when applicable.
- [ ] Markdown follows project style: ≤120-char lines, fenced code blocks with
      language hints, warnings formatted as `> **Warning**: ...`.
- [ ] Related docs/tests were updated (e.g., quickstart + troubleshooting when
      thresholds or entities change).

## Useful Commands
```bash
# Lint markdown (install markdownlint-cli)
markdownlint docs/**/*.md

# Spell check (install cspell)
cspell "docs/**/*.md"

# Grep for stale defaults
rg "k_on" docs/
rg "Phase 3" docs/
```

Need additional context? Go back to `../CLAUDE.md` (source of truth) or the
directory-specific documents listed above.
