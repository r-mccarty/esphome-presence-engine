# AGENTS.md – Documentation Directory

Guidelines for agents editing documentation under `docs/`. This directory contains comprehensive technical and operational documentation. **Always consult `../CLAUDE.md` first** – it serves as the primary context map and references the most critical docs below.

## Current Status
- **Phase 2 is DEPLOYED** and fully operational
- Documentation reflects production system with 4-state debounced presence detection
- Phase 3 (automated calibration) is planned but not yet implemented

## Document Topology

### 🔑 Primary Documentation (Referenced in CLAUDE.md)
```
docs/
├── ARCHITECTURE.md                  # ⭐ Technical design, algorithms, state machine, testing strategy
├── DEVELOPMENT_WORKFLOW.md          # ⭐ Two-machine workflow (Codespace ↔ ubuntu-node)
├── HARDWARE_SETUP.md                # ⭐ Hardware specs, wiring, calibration procedures
├── troubleshooting.md               # ⭐ Common issues, solutions, diagnostic tools
└── presence-engine-spec.md          # ⭐ Source of truth for 3-phase engineering roadmap
```

### 📚 Supporting Documentation
```
docs/
├── quickstart.md                    # User onboarding and initial setup guide
├── faq.md                           # Frequently asked questions
├── calibration.md                   # Manual + planned automated calibration workflows
├── phase1-completion-steps.md       # Phase 1 verification checklist (historical)
├── phase2-completion-steps.md       # Phase 2 verification checklist (historical)
├── gitops-deployment-guide.md       # CI/CD + OTA deployment workflow
├── self-hosted-runner-setup.md      # GitHub Actions runner instructions
├── ubuntu-node-setup.md             # Dedicated Ubuntu HA node setup guide
├── RFD-001-still-vs-moving-energy.md# Design decision: why still energy vs moving
└── assets/                          # Images, diagrams (some are 0-byte placeholders)
```

## Authoring Principles
1. **Accuracy first** – reflect actual firmware defaults and current state:
   - **Baseline**: μ_still = 6.7%, σ_still = 3.5% (calibrated 2025-11-06)
   - **Thresholds**: k_on = 9.0, k_off = 4.0
   - **Debounce timers**: on = 3s, off = 5s, absolute_clear = 30s
   - **Phase 2 is DEPLOYED** (not "planned" or "ready for deployment")
2. **Phase markers** – clearly distinguish:
   - ✅ Phase 1 (Z-score detection) – COMPLETE
   - ✅ Phase 2 (State machine + debouncing) – DEPLOYED
   - ⏳ Phase 3 (Automated calibration) – PLANNED (services exist but only log messages)
3. **Audience clarity**:
   - Engineering specs (ARCHITECTURE.md, presence-engine-spec.md) assume C++/ESPHome expertise
   - Operator guides (quickstart.md, troubleshooting.md, FAQ) must be accessible to Home Assistant users
   - Workflow docs (DEVELOPMENT_WORKFLOW.md, HARDWARE_SETUP.md) bridge both audiences
4. **Update everything** – when behavior changes, update all affected docs:
   - Technical specs (ARCHITECTURE.md, presence-engine-spec.md)
   - User guides (quickstart.md, troubleshooting.md, FAQ)
   - Configuration examples (ESPHome YAML, HA dashboards)
   - Root docs (README.md, CLAUDE.md)
   - Tests (unit tests, E2E tests)
5. **Reference CLAUDE.md structure** – when creating cross-references, prioritize the 5 primary docs that CLAUDE.md highlights

## Style Guide
- Markdown, 2-space indentation inside lists and code fences, ≤120 character lines.
- Use fenced code blocks with language hints (` ```yaml`, ` ```cpp`, ` ```bash`).
- Prefer active voice and present tense.
- Call out warnings with blockquotes: `> **Warning**: ...`
- Link to related sections using relative paths (`[Phase 2 checklist](phase2-completion-steps.md)`).
- Embed images from `assets/` with descriptive alt text.

## Critical Context: Two-Machine Workflow

This project uses a **two-machine workflow** (detailed in DEVELOPMENT_WORKFLOW.md):
- **Codespaces/Local**: Documentation editing, git operations
- **ubuntu-node**: Firmware compilation, flashing, Home Assistant API access

When documenting workflows:
- Clearly indicate which machine each step runs on
- Provide SSH instructions when steps require ubuntu-node
- Explain why certain operations require physical hardware access
- Reference helper scripts on ubuntu-node (`~/sync-and-flash.sh`, `~/flash-firmware.sh`)

## Review Checklist Before Commit
- [ ] Facts match firmware + HA configuration (entity IDs, defaults, state names)
- [ ] Phase status correct (Phase 2 DEPLOYED, Phase 3 PLANNED)
- [ ] Two-machine workflow clearly explained where relevant
- [ ] Screenshots/diagrams updated if UI changed
- [ ] Internal/external links work (use `markdown-link-check` if unsure)
- [ ] Spelling/grammar checked (`cspell` or editor tools)
- [ ] Phase references accurate (✅ Phase 1/2 complete, ⏳ Phase 3 planned)
- [ ] Tables + lists render correctly in GitHub preview
- [ ] Cross-references prioritize the 5 primary docs from CLAUDE.md

## Helpful Commands
```bash
# Lint Markdown (install markdownlint-cli first)
markdownlint docs/**/*.md

# Spell check (install cspell first)
cspell "docs/**/*.md"

# Search for outdated values
rg "k_on" docs/
rg "Phase 1" docs/
```

Need repo-wide context? See `../AGENTS.md`.
