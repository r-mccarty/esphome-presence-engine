# AGENTS.md - Documentation

This file provides guidance for AI agents working with documentation files in this directory.

## Overview

This directory contains user-facing and developer documentation for the bed presence detection system. Documentation is written in Markdown and follows a structure designed for both users and developers.

## Directory Structure

```
docs/
├── presence-engine-spec.md          # SOURCE OF TRUTH - 3-phase engineering spec
├── phase1-hardware-setup.md         # Hardware wiring and baseline calibration
├── quickstart.md                    # User-facing quickstart guide
├── calibration.md                   # Calibration procedures (all phases)
├── faq.md                           # Frequently asked questions
├── troubleshooting.md               # User troubleshooting guide
├── ubuntu-node-setup.md             # Ubuntu HA node setup guide
├── phase1-completion-steps.md       # Phase 1 completion checklist
└── assets/                          # Images, diagrams, media
    ├── wiring_diagram.png           # Hardware wiring (placeholder - 0 bytes)
    ├── demo.gif                     # Demo video (placeholder - 0 bytes)
    └── (other images)
```

## Documentation Hierarchy

### Engineering Documentation (Developer-Facing)

1. **presence-engine-spec.md** - **PRIMARY SOURCE OF TRUTH**
   - 3-phase development roadmap
   - Detailed engineering requirements
   - Implementation plans for each phase
   - Testing validation criteria
   - **CRITICAL**: Always read this before implementing new features

2. **phase1-hardware-setup.md**
   - Hardware wiring instructions
   - Manual baseline calibration procedure
   - GPIO pin mappings
   - Hardware-specific troubleshooting

3. **phase1-completion-steps.md**
   - Phase 1 completion checklist
   - Verification steps
   - Known limitations

4. **ubuntu-node-setup.md**
   - Guide for setting up Ubuntu as Home Assistant node
   - System configuration for dedicated HA hardware

### User Documentation (User-Facing)

1. **quickstart.md**
   - High-level getting started guide
   - Installation steps
   - Basic configuration
   - First-time user experience

2. **calibration.md**
   - Calibration procedures (Phase 1 manual, Phase 3 automated)
   - Threshold tuning guidance
   - When to recalibrate

3. **troubleshooting.md**
   - Common issues and solutions
   - Diagnostic procedures
   - Support resources

4. **faq.md**
   - Frequently asked questions
   - Conceptual explanations
   - Design rationale

## Documentation Principles

### 1. Accuracy Over Brevity
- **Do**: Provide complete, accurate information even if verbose
- **Don't**: Omit important details to save space

### 2. Phase Awareness
- **Do**: Clearly mark which phase features belong to
- **Don't**: Document unimplemented features without "Phase X" markers

Example:
```markdown
## Threshold Configuration

Phase 1 provides basic threshold tuning via `k_on` and `k_off` parameters.

**Phase 2 (Planned)**: Will add debounce timer configuration.
**Phase 3 (Planned)**: Will add automated calibration via HA services.
```

### 3. Target Audience Clarity
- **Engineering docs** (spec, hardware setup): Assume technical knowledge
- **User docs** (quickstart, FAQ): Assume minimal technical background

### 4. Living Documentation
- Update docs when behavior changes
- Mark outdated sections clearly
- Remove obsolete content rather than leaving confusing contradictions

## Key Documentation Files

### presence-engine-spec.md (PRIMARY SOURCE)

**Purpose**: Engineering specification for 3-phase development roadmap
**Audience**: Developers, contributors, AI agents
**Status**: Complete for Phase 1, detailed plans for Phase 2/3

**Structure**:
1. Prerequisites & Environment
2. Phase 1: Foundational Logic (z-score detection)
3. Phase 2: Temporal Filtering & State Management
4. Phase 3: Environmental Hardening & Calibration

**Critical sections**:
- Phase 1 Engineering Requirements (lines 13-43)
- Phase 2 State Machine Design (lines 61-94)
- Phase 3 Calibration Services (lines 98-131)

**When to update**:
- ✅ When implementing a phase (document actual implementation)
- ✅ When discovering better approaches (update with rationale)
- ❌ Don't change phase requirements without discussion (source of truth)

**Example change**:
```markdown
## Phase 1: Foundational Logic

**Status**: ✅ IMPLEMENTED (as of 2024-01)

**Actual implementation notes**:
- Used `binary_sensor` platform with custom C++ component
- Threshold entities use `number.template` platform with `restore_value: true`
- Z-score calculation in C++ for performance (not ESPHome lambda)
```

### phase1-hardware-setup.md

**Purpose**: Hardware wiring guide and manual calibration procedure
**Audience**: Users with hardware, developers testing firmware
**Status**: Complete for Phase 1

**Critical information**:
- M5Stack to LD2410 wiring (GPIO pins, UART settings)
- Step-by-step baseline data collection
- Calculating μ and σ from sensor readings
- Updating hardcoded values in C++ code

**When to update**:
- ✅ When testing with actual hardware reveals issues
- ✅ When adding support for different boards (ESP32-C3, etc.)
- ✅ When improving calibration procedure

### quickstart.md

**Purpose**: User-facing getting started guide
**Audience**: New users with minimal HA experience
**Status**: Complete for Phase 1

**Tone**: Friendly, instructional, assumes minimal technical background

**Structure**:
1. Hardware requirements
2. Firmware flashing
3. Home Assistant integration
4. Basic configuration
5. Next steps

**When to update**:
- ✅ When user onboarding flow changes
- ✅ When adding major features that affect setup
- ✅ When users report confusion (clarify unclear sections)

### calibration.md

**Purpose**: Detailed calibration procedures for all phases
**Audience**: Users who need to tune or recalibrate
**Status**: Phase 1 manual calibration documented, Phase 3 placeholder

**When to update**:
- ✅ When implementing Phase 3 automated calibration
- ✅ When discovering better calibration techniques
- ✅ When adding MAD statistical methods

### troubleshooting.md

**Purpose**: Solutions to common problems
**Audience**: Users experiencing issues
**Status**: Covers Phase 1 common issues

**Structure**: Problem → Cause → Solution format

**When to update**:
- ✅ When users report new issues (add to doc)
- ✅ When fixing bugs (explain what was wrong)
- ✅ When discovering better diagnostic procedures

### faq.md

**Purpose**: Answer common conceptual questions
**Audience**: Users curious about how things work
**Status**: Covers Phase 1 concepts

**Good FAQ entries**:
- "Why is my sensor 'twitchy'?" → Explains Phase 1 has no debouncing
- "What is a z-score?" → Explains statistical normalization
- "Can I use a different sensor?" → Explains LD2410 specifics

**When to update**:
- ✅ When users repeatedly ask the same question
- ✅ When adding features that raise new questions
- ✅ When clarifying misconceptions

## Writing Style Guidelines

### Markdown Conventions

**Headers**:
```markdown
# Top-level title (one per document)
## Major section
### Subsection
#### Minor subsection (use sparingly)
```

**Code blocks** with language highlighting:
````markdown
```yaml
# ESPHome configuration
sensor:
  - platform: ld2410
```

```cpp
// C++ code
float z_score = (energy - mu) / sigma;
```

```bash
# Shell commands
esphome compile bed-presence-detector.yaml
```
````

**Emphasis**:
```markdown
*Italic* for emphasis
**Bold** for strong emphasis
`code` for inline code, filenames, entity IDs
```

**Lists**:
```markdown
- Unordered list item
- Another item
  - Nested item (2-space indent)

1. Ordered list item
2. Another item
   - Can mix with unordered (3-space indent for alignment)
```

**Links**:
```markdown
[Link text](relative/path/to/file.md)
[External link](https://example.com)
[Section link](#section-heading)
```

**Blockquotes** (for warnings, notes):
```markdown
> **Warning**: This will erase all calibration data.

> **Note**: Phase 2 feature - not yet implemented.
```

### Technical Writing Best Practices

#### Use Active Voice
**Good**: "The sensor detects presence when z-score exceeds k_on"
**Bad**: "Presence is detected when z-score exceeds k_on"

#### Use Present Tense
**Good**: "The algorithm calculates the z-score"
**Bad**: "The algorithm will calculate the z-score"
(Exception: When describing future phases, use future tense with clear markers)

#### Be Specific
**Good**: "Set k_on to 4.0"
**Bad**: "Set k_on to a reasonable value"

#### Define Acronyms
**First use**: "MAD (Median Absolute Deviation) is a robust measure of variability"
**Subsequent uses**: "Use MAD instead of standard deviation"

#### Structure for Scanning
- Use descriptive headers
- Put important information first
- Use bullet points for lists
- Break up large paragraphs

#### Provide Context
**Good**:
```markdown
## Baseline Calibration

Before the sensor can detect presence, it needs to understand what "normal"
looks like in your specific environment. This is called baseline calibration.

Phase 1 requires manual calibration:
1. Collect sensor readings with empty bed
2. Calculate mean (μ) and standard deviation (σ)
3. Update values in code and reflash
```

**Bad**:
```markdown
## Baseline Calibration

Calculate μ and σ. Update bed_presence.h lines 43-46.
```

## Documentation Maintenance

### Updating Documentation When Code Changes

**Scenario**: You implement a new feature or fix a bug

**Checklist**:
1. **Engineering spec** (`presence-engine-spec.md`):
   - [ ] If implementing a planned feature, mark it as complete
   - [ ] Document any deviations from planned approach
   - [ ] Add "Actual implementation notes" section

2. **User-facing docs** (quickstart, FAQ, troubleshooting):
   - [ ] Update setup instructions if workflow changed
   - [ ] Add new FAQ entries for expected questions
   - [ ] Add troubleshooting entries for potential issues

3. **Technical docs** (hardware setup, calibration):
   - [ ] Update code references (file paths, line numbers)
   - [ ] Update entity names if changed
   - [ ] Update example values if defaults changed

4. **CLAUDE.md** (in root):
   - [ ] Update "Current Status" section
   - [ ] Update "Known Issues" if fixed
   - [ ] Update file line number references

### Keeping Documentation Synchronized

**Problem**: Code changes but docs don't, leading to confusion

**Solutions**:

1. **Link docs to tests**: When tests change, docs should change
   ```markdown
   # In presence-engine-spec.md
   Phase 1 is considered complete when all 14 unit tests pass
   (see `esphome/test/test_presence_engine.cpp`)
   ```

2. **Use specific code references**: Include file paths and line numbers
   ```markdown
   # In phase1-hardware-setup.md
   Update the baseline values in `esphome/custom_components/bed_presence_engine/bed_presence.h:43-46`
   ```

3. **Document version/phase info**: Make it clear what version docs apply to
   ```markdown
   # At top of document
   **Status**: Phase 1 Complete (as of 2024-01)
   **Next update**: When Phase 2 state machine is implemented
   ```

4. **Regular audits**: Periodically review docs for accuracy
   - Read through docs as if you're a new user
   - Verify all links work
   - Check code references are still accurate
   - Test procedures still work

## Assets and Media

### Current Status
The `assets/` directory contains **placeholder files** (0 bytes):
- `wiring_diagram.png` - ❌ Not yet created
- `demo.gif` - ❌ Not yet created

### Creating Wiring Diagrams

**Tools**: Fritzing, draw.io, or similar

**Content to include**:
- M5Stack Basic v2.7 pinout
- LD2410 sensor pins (UART, power)
- Wire connections (TX, RX, GND, VCC)
- Pin labels (GPIO16, GPIO17)
- Voltage levels (3.3V logic, 5V power)

**Format**: PNG (for diagrams), SVG (if vector graphics)

**Naming**: Descriptive names (e.g., `m5stack_ld2410_wiring.png`)

### Creating Demo Media

**Types**:
- GIF: Short (5-10 second) demos of features
- PNG: Screenshots of Home Assistant dashboard
- MP4: Longer video tutorials (link to external hosting)

**Best practices**:
- Keep file sizes reasonable (<5MB)
- Use descriptive filenames
- Include alt text in Markdown:
  ```markdown
  ![Wiring diagram showing M5Stack connected to LD2410](assets/wiring_diagram.png)
  ```

### Referencing Assets in Documentation

```markdown
## Hardware Setup

Connect the M5Stack to the LD2410 sensor as shown:

![M5Stack to LD2410 wiring diagram](assets/m5stack_ld2410_wiring.png)

| M5Stack Pin | LD2410 Pin | Purpose |
|-------------|------------|---------|
| GPIO17      | RX         | UART TX |
| GPIO16      | TX         | UART RX |
| GND         | GND        | Ground  |
| 5V          | VCC        | Power   |
```

## Documentation for Different Phases

### Phase 1 Documentation (Current)
**Status**: ✅ Complete

**Documented**:
- Z-score algorithm explanation
- Manual baseline calibration
- Threshold tuning (k_on, k_off)
- Hysteresis behavior
- Hardware wiring
- Entity names

**Intentionally missing**:
- Debounce configuration (Phase 2)
- State machine states (Phase 2)
- Automated calibration (Phase 3)

### Phase 2 Documentation (Planned)

**Will need to add**:
1. **Engineering spec updates**:
   - Mark Phase 2 as "IMPLEMENTED"
   - Document actual state machine implementation

2. **User guide additions**:
   - Debounce timer explanation
   - When to adjust debounce timers
   - State machine state meanings (IDLE, DEBOUNCING_ON, etc.)

3. **Troubleshooting additions**:
   - Debounce too short/long symptoms
   - State machine stuck in debounce state

4. **FAQ additions**:
   - "What is debouncing?"
   - "Why does state change take several seconds?"

### Phase 3 Documentation (Planned)

**Will need to add**:
1. **Calibration guide rewrite**:
   - Automated calibration procedure
   - Using Home Assistant services
   - Calibration wizard UI walkthrough

2. **Engineering spec updates**:
   - Mark Phase 3 as "IMPLEMENTED"
   - Document MAD statistics implementation

3. **Advanced features**:
   - Distance windowing configuration
   - MAD vs standard deviation explanation
   - When to recalibrate

## Common Documentation Tasks

### Adding a New FAQ Entry

1. Open `faq.md`
2. Add question to table of contents (if exists)
3. Add entry in appropriate section:
   ```markdown
   ### Why does the sensor not detect me sometimes?

   **Short answer**: The sensor may need calibration, or you may be outside
   the detection range.

   **Detailed explanation**:
   The LD2410 sensor detects presence using mmWave radar, which requires
   movement or micro-movements (like breathing). If you're perfectly still
   and holding your breath, the sensor may not detect you. This is expected
   behavior.

   **Solutions**:
   1. Ensure baseline calibration was performed correctly
   2. Lower the k_on threshold if sensor is too insensitive
   3. Verify sensor is pointed at the bed (not wall/ceiling)
   4. Check wiring connections are secure
   ```

### Adding a Troubleshooting Entry

1. Open `troubleshooting.md`
2. Add to appropriate section (Firmware, Hardware, Home Assistant)
3. Use Problem → Cause → Solution format:
   ```markdown
   ### Sensor Always Reports "Occupied"

   **Symptoms**:
   - binary_sensor.bed_occupied shows "on" constantly
   - Never transitions to "off" even when bed is empty

   **Possible Causes**:
   1. Baseline statistics (μ, σ) are incorrect for environment
   2. k_off threshold is too low
   3. Sensor is detecting environmental noise (fan, heater)

   **Solutions**:
   1. **Recalibrate baseline** (see [Phase 1 Hardware Setup](phase1-hardware-setup.md)):
      - Collect 60 seconds of data with empty bed
      - Recalculate μ and σ
      - Update values in bed_presence.h
   2. **Increase k_off threshold**:
      - In Home Assistant, raise k_off from 2.0 to 3.0 or 4.0
      - Monitor behavior for 24 hours
   3. **Check for environmental interference**:
      - Temporarily disable fans/heaters in room
      - Check if issue persists
   ```

### Updating Code References

When code changes (file moves, refactoring, etc.), update all references:

```bash
# Find all code references in docs
cd docs
grep -r "bed_presence.h" .
grep -r "line 43" .

# Update each file with new path/line numbers
```

**Example update**:
```markdown
# OLD
Update `bed_presence.h:43-46` with your calibrated values

# NEW
Update `esphome/custom_components/bed_presence_engine/bed_presence.h:43-46`
with your calibrated values
```

## Documentation Review Checklist

Before committing documentation changes:

- [ ] **Spelling**: Run spell check (US English)
- [ ] **Links**: Verify all links work (relative paths, external URLs)
- [ ] **Code references**: Verify file paths and line numbers are current
- [ ] **Entity names**: Verify entity IDs match actual implementation
- [ ] **Phase markers**: All features marked with correct phase
- [ ] **Screenshots**: Images are up-to-date (if UI changed)
- [ ] **Consistency**: Terminology matches other docs
- [ ] **Formatting**: Markdown renders correctly (preview in GitHub/editor)
- [ ] **Accuracy**: Technical details are correct (test procedures if unsure)
- [ ] **Completeness**: Don't leave readers with unanswered questions

## Tools for Documentation

### Markdown Editors
- **VS Code**: Built-in markdown preview, linting extensions
- **Typora**: WYSIWYG markdown editor
- **GitHub web editor**: Preview button shows rendered output

### Linting
```bash
# Install markdownlint
npm install -g markdownlint-cli

# Check docs
markdownlint docs/**/*.md

# Auto-fix common issues
markdownlint --fix docs/**/*.md
```

### Link Checking
```bash
# Install markdown-link-check
npm install -g markdown-link-check

# Check all links
markdown-link-check docs/**/*.md
```

### Spell Checking
```bash
# Install cspell
npm install -g cspell

# Check spelling
cspell "docs/**/*.md"

# Add project-specific words to .cspell.json
```

## Additional Resources

- **Markdown Guide**: https://www.markdownguide.org/
- **Technical Writing Style Guide**: https://developers.google.com/style
- **GitHub Flavored Markdown**: https://github.github.com/gfm/
- **Diagram Tools**: https://www.diagrams.net/ (draw.io)

---

**Need broader context?** See `../CLAUDE.md` for comprehensive project documentation, or `../AGENTS.md` for repository-wide agent guidance.
