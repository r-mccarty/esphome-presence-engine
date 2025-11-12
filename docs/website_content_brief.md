# Website Content & Marketing Brief: AuraSense Strategy

**Document Version:** 2.0
**Last Updated:** 2025-11-12

**Objective:** To provide the front-end development and marketing teams with the strategic framework, brand
positioning, and content approach for the AuraSense mmWave Presence Sensor. This document translates our
Brand-Led + Product/Tech-Led strategic foundation into compelling, authentic marketing that drives
Product-Led Growth.

---

## Strategic Foundation

### Our Competitive Moat

**Primary: Brand-Led**
AuraSense is building a company that is *loved*, not just used. Our brand promise is simple: smart home
products that respect your intelligence, value your time, and deliver an experience so thoughtful that
you want to tell others about it.

**Secondary: Product/Tech-Led**
This promise is backed by demonstrably superior engineering. We don't just claim reliability—we achieve it
through statistical algorithms, deliberate state machine design, and obsessive attention to the "first
five minutes" experience.

### Our Acquisition Strategy

**Primary: Product-Led Growth (PLG)**
The product experience must be so exceptional that it fuels its own growth through user advocacy. A
frictionless setup, immediate reliability, and transparent operation create natural evangelists.

**Secondary: Marketing-Led Growth (MLG)**
High-quality content amplifies this advocacy by telling the *why* behind the product's design choices.
We attract technically-minded users who appreciate substance over hype.

### Strategic Coherence

The brand makes a promise → The product delivers on that promise so effectively that users become
advocates → The content tells the story of why it works, attracting more users to experience it.

---

## 1. Target Audience & Positioning

### Primary Audience: The Discerning Home Automator

**Profile:**
- Home Assistant power users who have been burned by unreliable presence detection
- Value substance over marketing fluff; respond to peer reviews and technical transparency
- Willing to pay a premium for quality but expect that premium to be *earned*
- View their smart home as a craft, not just a collection of gadgets

**Pain Points:**
- "My lights turn off while I'm still in bed." (Technical failure)
- "My current sensor is a black box I can't understand or tune." (Lack of transparency)
- "I'm tired of products that over-promise and under-deliver." (Brand fatigue)
- "Camera-based solutions feel like privacy invasions." (Values conflict)

**What They're Really Looking For:**
Not just another sensor, but a company that *respects their intelligence* and shares their values.

### Secondary Audience: DIY Electronics Enthusiasts

Sophisticated hobbyists looking for a well-engineered, well-documented project that teaches them
something while integrating seamlessly into their smart home.

---

## 2. Brand Voice & Messaging Framework

### Brand Personality

- **Confident but Humble:** We're proud of our engineering, but we explain *why* it works rather than
  just claiming superiority.
- **Transparent:** We show our state machine diagrams, publish our algorithms, and explain our design
  trade-offs openly.
- **Respectful:** We assume our users are intelligent and technical. No dumbing down, no hand-waving.
- **Obsessive About Details:** From the unboxing experience to the debug text sensor, every touchpoint
  reflects care.

### Messaging Pillars

1. **Reliability is Earned, Not Claimed**
   We don't just say "rock-solid reliability"—we show you the 4-state machine and temporal filtering
   that makes false positives virtually impossible.

2. **Privacy by Design, Not by Marketing**
   mmWave radar + local processing isn't a checkbox feature—it's a fundamental architectural choice that
   reflects our values.

3. **Transparency Builds Trust**
   Every parameter is tunable. Every state transition is visible. We're not a black box because we
   respect your right to understand and control your home.

4. **The First Five Minutes Matter**
   If setup is frustrating, nothing else matters. We've obsessed over the out-of-box experience so your
   first impression is "these people *get it*."

---

## 3. Elevator Pitch & Hero Messaging

### Tagline
**Stop Detecting Motion. Start Understanding Presence.**

### Hero Headline (Landing Page)
**Smart Home Presence Detection That Respects Your Intelligence**

### Supporting Headline
A privacy-first mmWave sensor engineered for the reliability your automations deserve. No false
positives. No black boxes. No compromises.

### Elevator Pitch (150 words)
The AuraSense Bed Presence Sensor isn't just another sensor—it's a statement about how smart home
products should be built.

At its core is a statistical presence *engine* that uses z-score analysis and a 4-state machine to
deliver the reliability that other sensors promise but don't deliver. No more lights turning off while
you're sleeping. No more false triggers from fans or pets. Just confidence that your automations will
work, every time.

But reliability is just the baseline. We've obsessed over the details: a setup wizard that works in
under five minutes, real-time transparency into the sensor's reasoning, and documentation that treats
you like the intelligent tinkerer you are.

All processing happens locally—no cloud, no cameras, no compromise on privacy.

This is presence detection built by people who *care*. We think you'll notice the difference.

---

## 4. Key Value Propositions (The "Why AuraSense")

These should be the primary content blocks on the landing page, presented in order of emotional impact
→ technical credibility.

### 1. Built to Be Loved, Not Just Used

**The Promise:**
Smart home products should earn your loyalty through excellence, not lock you in with ecosystems. We're
building a company where every detail—from the unboxing to the GitHub README—reflects genuine care.

**The Evidence:**
- Premium unboxing experience with clear, visual quick-start guide
- Obsessively documented architecture (7,000+ words of public technical specs)
- Active community engagement and responsive support
- Open-source firmware (ESPHome) with full transparency into algorithms

**CTA:** *Experience the difference →*

---

### 2. Reliability You Can Actually Trust

**The Problem:**
You've been burned before. Sensors that claim "99% accuracy" but turn your lights off mid-sleep.
Products that work great in the demo but fail in real-world conditions.

**Our Approach:**
We don't claim perfection—we *show you the engineering* that makes false positives virtually impossible:

- **4-State Verification Engine:** Presence must be sustained and verified before triggering, eliminating
  transient noise.
- **Statistical Intelligence:** Z-score analysis (not arbitrary thresholds) makes the sensor adaptable to
  your unique environment.
- **Stillness Detection:** Our "Absolute Clear Delay" solves the age-old problem of sensors failing when
  you lie perfectly still.
- **Hysteresis by Design:** Separate ON/OFF thresholds (`k_on=9.0`, `k_off=4.0`) prevent oscillation and
  "flapping."

**The Result:** Automations that work so reliably you forget they're there—which is exactly how smart
homes should feel.

**CTA:** *See the state machine →*

---

### 3. Privacy is Architecture, Not Marketing

**The Reality Check:**
Anyone can claim "privacy-first." Few companies make the expensive engineering choices to actually
deliver it.

**Our Commitment:**
- **mmWave Radar Technology:** Detects *that* you're there, not *who* you are. No images, no facial
  recognition, no personally identifiable data.
- **100% Local Processing:** All computation happens on the ESP32. No cloud dependencies, no data leaving
  your network, no latency.
- **Home Assistant Native:** Integrates directly with your self-hosted HA instance. Your data never
  touches our servers because *we don't have servers*.

**Why It Matters:**
Your bedroom is your sanctuary. We designed this sensor for ours, and we'd never compromise that.

**CTA:** *Learn about our architecture →*

---

### 4. Transparency You Can Verify

**The Philosophy:**
Black boxes are for products that don't want you looking too closely. We invite you to look.

**What "Transparent" Means at AuraSense:**
- **Every Parameter is Tunable:** From statistical thresholds to debounce timers, you have full control
  via the Home Assistant UI.
- **Real-Time State Reasoning:** The `text_sensor.presence_state_reason` shows you exactly why the sensor
  made each decision (e.g., "PRESENT: z=12.3, high_conf 2s ago").
- **Open-Source Foundation:** Built on ESPHome with fully accessible C++ source and unit tests.
- **Public Documentation:** Our technical architecture doc isn't a simplified "marketing version"—it's
  the real engineering spec, available to everyone.

**The Trust Factor:**
When you can verify claims yourself, marketing becomes unnecessary. We're confident enough in our
engineering to show you *how* it works, not just *that* it works.

**CTA:** *Explore the documentation →*

---

### 5. The First Five Minutes Are Perfect

**The Recognition:**
If setup is frustrating, the rest of the experience doesn't matter. You'll resent the product before you
ever see its value.

**Our Obsession:**
- **Setup Wizard in Home Assistant:** Automated calibration, guided distance windowing, visual feedback.
  No YAML editing required (but available for power users).
- **Works Out of the Box:** Sane defaults (`k_on=9.0`, `k_off=4.0`, 3s/5s debounce) that work for 90%
  of users immediately.
- **Visual Quick-Start Guide:** In the box, one page, clear diagrams. No 40-page manual.
- **Community-Tested:** Our defaults aren't guesses—they're validated across dozens of real-world
  deployments.

**The Philosophy:**
Respecting your time is respecting you. Every minute we save you in setup is a minute you're more likely
to recommend us to a friend.

**CTA:** *See setup in action →*

---

### 6. Engineering That Stands Up to Scrutiny

**For the Technical Audience:**
You don't just want it to work—you want to understand *why* it works so you can trust it in edge cases.

**Technical Differentiators:**

**Still Energy vs. Moving Energy:**
- Most mmWave sensors react to all motion, making them vulnerable to fans and pets.
- We deliberately use **still energy** as the primary signal. A sleeping human is a large, stationary
  mass with high still energy. A fan is pure moving energy. This architectural choice eliminates entire
  classes of false positives.

**Z-Score Statistical Analysis:**
- Instead of raw energy thresholds (which vary by room, sensor placement, and even temperature), we
  normalize against the empty-room baseline.
- `z_score = (current_energy - baseline_mean) / baseline_stddev`
- This makes the sensor automatically adapt to your environment and dramatically improves reliability
  across different hardware and rooms.

**Temporal Filtering (Debounce):**
- The core of our reliability. Signals must be *sustained* for configured durations before triggering
  state changes.
- Default: 3s ON debounce, 5s OFF debounce, 30s Absolute Clear Delay.
- This eliminates transient noise and the "twitchiness" that plagues simple threshold-based sensors.

**Absolute Clear Delay:**
- Our solution to the "sleeping person detection" problem.
- After each high-confidence presence signal, a 30s timer starts. The sensor won't even *consider*
  clearing until this timer expires.
- This prevents false negatives when you lie perfectly still, watching TV or sleeping.

**CTA:** *Read the full architecture spec →*

---

## 5. The 4-State Presence Engine (Technical Deep Dive)

This section should be a separate page/tab for users who want the full technical explanation. It
demonstrates our commitment to transparency and provides the "reason to believe" for our reliability
claims.

### Introduction: Why a State Machine?

Simple sensors are binary: ON or OFF based on whether a reading exceeds a threshold. This approach is
fast but fragile—any noise can cause false triggers, and any signal drop (like a person lying still)
causes false negatives.

AuraSense uses a **4-state finite state machine** that *verifies* presence before changing state. This
makes the sensor deliberate, resilient, and immune to the reliability problems that plague simpler
designs.

### State Machine Diagram

```
                     z_still >= k_on
                ┌─────────────────────┐
                │                     │
                ▼                     │
    ┌───────────────────┐             │
    │       IDLE        │◄────────────┤
    │  (Binary: OFF)    │             │
    └───────────────────┘             │
                │                     │
                │ z_still >= k_on     │
                ▼                     │
    ┌───────────────────┐             │
    │  DEBOUNCING_ON    │             │
    │  (Binary: OFF)    │             │
    │  Timer running    │             │
    └───────────────────┘             │
                │                     │
     Timer >= on_debounce_ms          │
      & z_still >= k_on               │
                │                     │
                ▼                     │
    ┌───────────────────┐             │
    │     PRESENT       │             │
    │  (Binary: ON)     │             │
    │  Update high_conf │             │
    └───────────────────┘             │
                │                     │
     z_still < k_off &                │
     time since high_conf             │
       >= abs_clear_delay             │
                │                     │
                ▼                     │
    ┌───────────────────┐             │
    │  DEBOUNCING_OFF   │             │
    │  (Binary: ON)     │             │
    │  Timer running    │             │
    └───────────────────┘             │
                │                     │
     Timer >= off_debounce_ms         │
      & z_still < k_off               │
                │                     │
                └─────────────────────┘

Reset Conditions (abort debounce):
- DEBOUNCING_ON → IDLE:    if z_still < k_on (lost signal)
- DEBOUNCING_OFF → PRESENT: if z_still >= k_on (signal returned)
```

### How It Works: Step-by-Step

**1. IDLE (Binary: OFF)**
The bed is empty. The sensor is monitoring the baseline and waiting for a statistically significant
presence signal.

- **Transition condition:** `z_still >= k_on` (default: 9.0 standard deviations above baseline)
- **Philosophy:** We require a *strong* signal to begin verification, filtering out weak noise.

**2. DEBOUNCING_ON (Binary: OFF)**
A high signal is detected! Instead of immediately reporting presence, the sensor enters a verification
state. The binary output remains OFF.

- **Timer:** `on_debounce_ms` (default: 3,000ms / 3 seconds)
- **Philosophy:** Transient events (walking past the bed, pet jumping up briefly) won't trigger the
  sensor because they don't sustain the signal.
- **Abort condition:** If signal drops below `k_on` during this timer, abort and return to IDLE. No
  false positive occurred.

**3. PRESENT (Binary: ON)**
The high signal was sustained for the full debounce period. The sensor is now confident someone is in
bed and reports `binary_sensor.bed_occupied = ON` to Home Assistant.

- **Continuous monitoring:** While in this state, the sensor tracks the `last_high_conf_time`—the last
  moment a strong presence signal was seen.
- **Philosophy:** This timestamp is critical for the Absolute Clear Delay feature that solves the
  stillness problem.

**4. DEBOUNCING_OFF (Binary: ON)**
The signal has dropped below the OFF threshold, suggesting the person has left. But before clearing, two
conditions must be met:

- **Condition 1 (Signal):** `z_still < k_off` (default: 4.0 standard deviations)
- **Condition 2 (Time):** `(current_time - last_high_conf_time) >= abs_clear_delay_ms` (default: 30s)

**Why Both Conditions?**
Condition 2 is our defense against false negatives. If you're lying perfectly still (deep sleep,
watching TV), your energy signature may drop temporarily. The Absolute Clear Delay ensures the sensor
won't clear until at least 30 seconds have passed since the last strong signal, even if the current
reading is low.

- **Timer:** `off_debounce_ms` (default: 5,000ms / 5 seconds)
- **Philosophy:** Just as we verify presence, we verify absence. The sensor remains ON during this
  verification to prevent your lights from flickering off prematurely.
- **Abort condition:** If signal rises above `k_on` during this timer (you moved), abort and return to
  PRESENT. The bed is still occupied.

**5. Return to IDLE**
The low signal was sustained for the full OFF debounce period. The sensor confidently reports the bed is
empty and returns to IDLE, awaiting the next occupant.

---

### Why This Matters: Real-World Scenarios

**Scenario 1: Pet Jumps on Bed**
A pet jumps up for 1-2 seconds, then leaves.

- **Simple Sensor:** Instant ON → Instant OFF → Your automations trigger unnecessarily.
- **AuraSense:** Signal detected → DEBOUNCING_ON (2 seconds pass) → Signal lost before 3s timer completes
  → Abort to IDLE → No false positive. Your automations never fired.

**Scenario 2: Lying Perfectly Still**
You're in deep sleep. Your energy signature temporarily drops to near-baseline levels.

- **Simple Sensor:** Signal drops below threshold → Instant OFF → Your lights turn on, waking you.
- **AuraSense:** Signal drops → DEBOUNCING_OFF begins → But Absolute Clear Delay hasn't expired (last
  high_conf was only 10s ago) → Condition not met, stays PRESENT → Your lights stay off. You sleep
  soundly.

**Scenario 3: Fan Turned On**
You turn on a fan while lying in bed. It creates moving energy noise.

- **Simple Sensor:** Total energy spikes → False ON signal (if you were out of bed) or oscillation.
- **AuraSense:** We monitor *still* energy, not total energy → Fan's moving energy is ignored → No false
  trigger.

---

## 6. Content Strategy & Messaging Hierarchy

### Primary Content Blocks (Landing Page)

**Above the Fold:**
1. Hero headline + supporting copy + hero image/video
2. Single primary CTA: "Pre-Order Now" / "Get Yours Today"
3. Trust indicators: "Used by 500+ Home Assistant enthusiasts" / "4.9★ on GitHub"

**Section 1: The Promise (Brand-Led)**
- "Built to Be Loved, Not Just Used" block
- Focus on emotional connection and brand values
- CTA: "Our Story" or "Why We Built This"

**Section 2: The Evidence (Product-Led)**
- "Reliability You Can Actually Trust" block with state machine teaser
- CTA: "See How It Works"

**Section 3: Privacy & Transparency**
- Side-by-side comparison: Camera vs. mmWave, Cloud vs. Local
- CTA: "Read Our Privacy Architecture"

**Section 4: User Experience**
- "The First Five Minutes Are Perfect" with setup video/GIF
- CTA: "Watch Setup in Action"

**Section 5: Technical Deep Dive (For Power Users)**
- Link to full state machine explanation and architecture docs
- CTA: "Read the Engineering Spec"

**Section 6: Social Proof**
- Community testimonials (authentic, technical, not marketing-speak)
- Link to GitHub, Home Assistant forums, Discord community

**Section 7: Final CTA**
- Repeat primary CTA with secondary option: "Join the Waitlist" / "Get Notified at Launch"

### Secondary Content (Separate Pages/Tabs)

1. **Technical Architecture** (The full state machine deep dive above)
2. **Documentation** (Link to GitHub docs)
3. **Community** (Forums, Discord, GitHub Discussions)
4. **About Us / Our Values** (Brand story, why we built this, what we believe)
5. **Support & FAQ** (Self-service first, contact form secondary)

---

## 7. Tone & Voice Guidelines

### Do's:
- **Be specific:** "4-state verification engine" not "advanced AI algorithms"
- **Show, don't just tell:** Diagrams, state machine visuals, before/after comparisons
- **Use technical terms when accurate:** "z-score normalization," "temporal debounce," "hysteresis"
- **Acknowledge trade-offs:** "We chose still energy over moving energy, which means..."
- **Let the product speak:** "Try it for 30 days. If it's not the most reliable sensor you've owned,
  return it."

### Don'ts:
- **Avoid hype:** No "revolutionary," "game-changing," or "world's best" without evidence
- **Don't dumb down:** Our audience is technical. Respect their intelligence.
- **No false modesty:** We're proud of our engineering. Confidence ≠ arrogance.
- **Don't hide limitations:** If the sensor works best in certain mounting configurations, say so.
- **Avoid feature lists without context:** Every feature should answer "why does this matter to me?"

### Comparative Messaging (When Necessary)

We generally avoid direct competitor comparisons, but when users ask:

**Frame it as philosophy, not feature wars:**
- "Many sensors optimize for speed—instant response to any motion. We optimize for *accuracy*—deliberate
  verification that eliminates false positives."
- "Some sensors hide their thresholds behind proprietary algorithms. We publish ours because we believe
  transparency builds trust."

---

## 8. Visual & Content Assets

### Priority 1: Hero Video/GIF (15-30 seconds)

**Concept:** Split-screen comparison showing Home Assistant dashboards.

- **Left side (Generic Sensor):** `binary_sensor.generic_presence` rapidly flaps ON→OFF→ON as a fan turns
  on. State: "Detected" → "Clear" → "Detected."
- **Right side (AuraSense):** `binary_sensor.bed_occupied` remains stable (ON). State reason shows:
  "PRESENT: z=11.2, high_conf=2s ago." The text sensor provides calm confidence.
- **Voiceover/Text Overlay:** "Stop reacting to noise. Start understanding presence."

### Priority 2: Setup Experience Video (60-90 seconds)

**Concept:** Unboxing through first automation in under 90 seconds.

1. **Unboxing:** Clean packaging, visual quick-start card
2. **Power on:** Device boots, ESPHome adoption screen in HA
3. **Wizard UI:** Guided calibration (30s empty room capture)
4. **First detection:** Person lies on bed, state changes to PRESENT, graph shows z-score spike
5. **Create automation:** Simple "turn off lights when bed occupied" automation created in HA UI
6. **Test:** Person lies down → lights turn off reliably
7. **End screen:** "5 minutes. No frustration. Just confidence."

### Priority 3: State Machine Diagram (Interactive)

An animated SVG or interactive diagram showing the 4 states with:
- Transition conditions labeled
- Example sensor readings causing transitions
- Ability to "step through" a scenario (e.g., "Person enters bed," "Person lies still," "Person leaves")

### Priority 4: Dashboard Screenshots

High-quality screenshots of the Home Assistant dashboard showing:
- Binary sensor entity with state history graph (stable, no flapping)
- Text sensor showing state reasoning
- Configuration sliders (k_on, k_off, debounce timers) with tooltips
- Calibration status and distance window settings

### Priority 5: Physical Product Photography

**Brand-Led aesthetic:**
- Clean, white background with subtle shadows (Apple-style)
- Close-ups showing build quality, connectors, antenna positioning
- "In context" shots: sensor mounted above bed (tastefully, no people in shot for privacy)
- Packaging shots emphasizing premium unboxing experience

---

## 9. Calls to Action (Prioritized)

### Primary CTA (Conversion Goal)
**"Get Yours Today"** / **"Pre-Order Now"** → Product page with purchase options

### Secondary CTA (Engagement Goal)
**"See How It Works"** → 4-state machine technical deep dive or setup video

### Tertiary CTA (Community Building)
**"Read the Docs"** → GitHub documentation and architecture specs
**"Join the Community"** → Discord, Home Assistant forums, GitHub Discussions

### Fallback CTA (Lead Capture)
**"Get Notified at Launch"** / **"Join the Waitlist"** → Email capture for pre-launch or sold-out
scenarios

---

## 10. Success Metrics & North Star

### North Star Metric (Product-Led Growth)
**User Advocacy Rate:** Percentage of customers who recommend AuraSense to others (measured via Net
Promoter Score and direct community mentions).

**Why This Metric:**
PLG is fueled by organic advocacy. If the product is loved, users become our marketing engine. This
metric forces us to maintain quality over growth-at-all-costs.

### Supporting Metrics

1. **Setup Completion Rate:** % of users who complete wizard within first session (Target: >85%)
2. **Time to First Automation:** Median time from unboxing to first working automation (Target: <10min)
3. **Support Ticket Rate:** Tickets per 100 units sold (Target: <5, tracking downward)
4. **Documentation Engagement:** % of users who visit docs before purchase (High engagement = sign of
   informed, satisfied buyers)
5. **Return Rate:** <2% (Premium products should have low returns; high returns = expectations mismatch)

### Qualitative Indicators

- Community forum sentiment (manual review of posts)
- Unsolicited testimonials and social media mentions
- GitHub stars and contribution activity
- Home Assistant Community Store (HACS) adoption rate

---

## 11. Strategic Guardrails (What We Don't Do)

To maintain strategic coherence, we explicitly avoid:

1. **Competing on Price:** We will never be the cheapest option. Our value is quality and experience, not
   cost minimization.
2. **Feature Bloat:** We say no to features that don't serve our core promise of reliability and
   transparency. (e.g., cloud connectivity, mobile app, RGB lighting)
3. **Overpromising in Marketing:** If we can't back up a claim with engineering, we don't make the claim.
4. **Sales-Led Growth Tactics:** No cold outreach, no aggressive sales teams, no enterprise
   "partnerships" that compromise our values.
5. **Sacrificing Onboarding for Features:** The first five minutes are sacred. No feature is worth
   complicating setup.

---

## 12. Launch Phases & Content Evolution

### Phase 1: Technical Community Launch (Current)
**Audience:** Home Assistant power users, ESPHome enthusiasts
**Content Focus:** Technical transparency, state machine deep dive, GitHub documentation prominence
**Channel:** Home Assistant forums, Reddit (r/homeassistant), GitHub
**Success:** 500-1,000 early adopters who become vocal advocates

### Phase 2: Broader Smart Home Enthusiast Launch (3-6 months)
**Audience:** Smart home hobbyists who may not be deeply technical
**Content Focus:** Simplified reliability messaging, setup experience video, comparison to frustrating
alternatives
**Channel:** YouTube reviews, smart home blogs, targeted Reddit ads
**Success:** 5,000-10,000 units sold, strong NPS (>50)

### Phase 3: Premium Home Tech Segment (12+ months)
**Audience:** High-end smart home integrators, design-conscious consumers
**Content Focus:** Brand story, premium experience, design aesthetics, privacy commitment
**Channel:** Home tech publications, integrator partnerships, referral program
**Success:** Established brand recognition, 20,000+ units sold, multi-product line

---

## Appendix A: Key Messaging Translations

| Strategic Concept | Landing Page Headline | Body Copy Focus |
|-------------------|----------------------|-----------------|
| Brand-Led Foundation | "Built to Be Loved, Not Just Used" | Story, values, attention to detail, community |
| Product-Led Foundation | "Reliability You Can Actually Trust" | State machine, z-score, stillness detection, engineering |
| PLG Acquisition | "The First Five Minutes Are Perfect" | Setup wizard, defaults, time-to-value |
| MLG Acquisition | "Transparency You Can Verify" | Open docs, published algorithms, GitHub presence |
| Privacy by Architecture | "Privacy is Architecture, Not Marketing" | mmWave tech, local processing, no cloud, no cameras |

---

## Appendix B: Competitor Positioning (Internal Use)

**NOT for public-facing content—use only to inform our differentiation strategy.**

### Typical Competitor Approaches:
1. **"Works with everything" generalists:** Emphasize compatibility, cheap prices, feature count
   - **Our counter:** Specialize in Home Assistant, optimize for one use case done perfectly
2. **"AI-powered" black boxes:** Vague claims about algorithms, no transparency, cloud dependency
   - **Our counter:** Published state machine, open-source, show the math
3. **"Plug and play" simplifiers:** No configuration, no tuning, works for average case only
   - **Our counter:** Works great out of box *and* fully tunable for edge cases
4. **Camera-based solutions:** High accuracy but privacy concerns
   - **Our counter:** Privacy-first architecture with comparable reliability

### Where We Win:
- **Technical transparency** (they can't/won't publish their algorithms)
- **Community trust** (open-source, active engagement, responsive support)
- **Setup experience** (we've obsessed over the first five minutes)
- **Privacy credibility** (architectural, not just marketing)

### Where We Accept Trade-offs:
- **Price:** We're more expensive. We're okay with that.
- **Compatibility:** Home Assistant only. We're specialists, not generalists.
- **Feature breadth:** We do one thing exceptionally well, not ten things adequately.

---

**END OF DOCUMENT**

---

## Document Changelog

**v2.0 (2025-11-12):**
- Complete rewrite to align with AuraSense strategic framework
- Added strategic foundation and acquisition engine sections
- Repositioned features within Brand-Led + Product-Led framework
- Expanded messaging hierarchy and content strategy for PLG/MLG
- Added success metrics, launch phases, and strategic guardrails
- Maintained technical deep dive content while adding brand context

**v1.0 (Previous):**
- Initial product-feature-focused brief
- Primary emphasis on technical specifications and state machine
- Limited brand positioning or strategic context
