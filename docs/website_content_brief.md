# OpticWorks Website Content Brief

**Objective:** Deliver a self-contained narrative that equips the brand, content, and front-end
teams to ship a premium product experience for OpticWorks' mmWave Presence Sensor for Home Assistant.
The brief translates the business strategy (Brand-Led + Product-Led Growth) into web-ready messaging,
visual cues, and proof points.

## 1. Target Audience

- **Primary:** Home Assistant power users and smart home enthusiasts who demand rock-solid automation
  and appreciate thoughtful industrial design.
- **Secondary:** Design-forward DIY makers and boutique home integrators seeking a standout sensor to
  showcase in premium installations.
- **Tertiary:** Reviewers, influencers, and technical writers who can validate OpticWorks' claims
  through hands-on testing.
- **Pain Points to Acknowledge:**
  - "Every presence sensor I've tried is twitchy or opaque."
  - "I need reliability that matches the polish of the rest of my smart home."
  - "Setup should feel premium, not like a weekend project." 
  - "I only advocate products that respect privacy and provide transparent telemetry."

## 2. Elevator Pitch (The "Hook")

**Tagline:** Presence, Perfected.

**Pitch:** OpticWorks delivers a crafted presence experience that feels as refined as it is reliable.
Our mmWave engine understands the rhythm of your home, pairing meticulous hardware and a calm,
confident interface inside Home Assistant. It's the sensor you recommend because it delights in the
first five minutes and keeps earning trust every night.

## 3. Core Story Pillars

1. **Lovable Reliability:** A four-state presence engine with hysteresis, temporal filtering, and
   absolute clear delay creates deliberate state changes that end "flapping" automations.
2. **Crafted Premium Experience:** From the machined enclosure to the unboxing ritual, OpticWorks
   signals quality. Every interaction—from magnetic mounting to the Home Assistant dashboard—feels
   intentional and elegant.
3. **Transparent Intelligence:** Live state reasoning (`text_sensor.presence_state_reason`), tunable
   thresholds (`k_on = 9.0`, `k_off = 4.0`), and still-energy analytics empower enthusiasts to see
   exactly why decisions are made.
4. **Privacy You Can Trust:** mmWave sensing plus on-device computation means no cameras, no cloud,
   and no data handoff.
5. **Community-Ready Storytelling:** Public documentation, open Home Assistant packages, and a
   frictionless setup flow invite users to try, fall in love, and advocate.

## 4. Feature Breakdown (Translate to Benefit-Led Copy)

### Four-State Presence Engine
- **What:** IDLE → DEBOUNCING_ON → PRESENT → DEBOUNCING_OFF, guarded by dual thresholds and timers.
- **Why it matters:** Users experience "calm" automations—lights stay on while occupied, clear when
  genuinely empty.

### Temporal Filtering & Absolute Clear Delay
- **What:** 3s on-debounce, 5s off-debounce, and 30s absolute clear delay defaults.
- **Why it matters:** The system waits for conviction, eliminating false clears when someone is lying
  still and rejecting fleeting spikes from HVAC or pets.

### Z-Score Statistical Intelligence
- **What:** Dynamic baselining with μ=6.7%, σ=3.5%, and z-score thresholds that adapt per room.
- **Why it matters:** Install once, tune once—the sensor adjusts to different environments without
  manual recalibration.

### Frictionless First Five Minutes
- **What:** Guided Home Assistant onboarding, automatic entity naming, and pre-built dashboards.
- **Why it matters:** Aligns with Product-Led Growth—users feel the value before reading the manual,
  making them more likely to share and recommend.

### Premium Industrial & Interaction Design
- **What:** Low-profile enclosure, color-accurate status LED, and magnetic mounting system.
- **Why it matters:** Reinforces the Brand-Led foundation—OpticWorks looks and feels like a flagship
  product, not a DIY compromise.

## 5. Proof & Technical Differentiators

- **Still-Energy Focus:** Purposefully interprets still energy to detect resting occupants while
  ignoring oscillating fans or hallway movement.
- **On-Device, Cloud-Free:** All inference runs on the ESP32. Latency stays low; data stays local.
- **Debugging Clarity:** Real-time state reason strings and plotted energy charts explain every
  transition, building confidence for integrators.
- **Open Yet Polished:** Firmware, dashboards, and documentation are public, inviting community
  contributions without sacrificing brand standards.

## 6. Brand Voice & Visual Direction

- **Tone:** Confident, serene, and design-forward. Blend technical precision with warm assurance.
- **Hero Concept:** A split-screen video—on the left, a generic sensor flutters; on the right,
  OpticWorks calmly reports `binary_sensor.bed_occupied: ON` with an elegant Home Assistant card.
- **Supporting Visuals:**
  - Macro photography of the enclosure and unboxing elements.
  - Animated state machine diagram styled with OpticWorks' palette.
  - Dashboard screenshots highlighting tunable sliders and state reasons.
- **Microcopy Guidelines:** Avoid jargon dumps; pair every spec with a benefit. Use active verbs like
  "crafts," "clarifies," and "invites."

## 7. Calls to Action

- **Primary CTA:** "Experience OpticWorks" – anchors a self-service purchase or reservation flow.
- **Secondary CTA:** "Try the Home Assistant Dashboard" – interactive demo or video walkthrough.
- **Tertiary CTA:** "Read the Technical Architecture" – links to `docs/ARCHITECTURE.md` for deep
  dives.
- **Community CTA:** "Share Your Automations" – encourages user-generated content that powers the
  flywheel.

## 8. Content & Acquisition Alignment

- **Product-Led Hooks:** Offer a downloadable Home Assistant package and quickstart video so users
  can self-onboard and feel delight immediately.
- **Marketing Amplifiers:** Publish case studies, maker spotlights, and behind-the-scenes design
  stories to reinforce the brand narrative and fuel social sharing.
- **Advocacy Loop:** Highlight testimonials, automation blueprints, and integration recipes submitted
  by the community. Reward contributors with early firmware drops or design previews.
- **Lifecycle Touchpoints:**
  - Pre-purchase email series focusing on experience, not specs.
  - Post-purchase concierge onboarding with checklists and FAQ highlights.
  - Ongoing firmware notes celebrating incremental polish (e.g., improved still-energy smoothing).

## 9. Page Architecture (Suggested)

1. **Hero Block:** Tagline, hero visual, primary CTA, and a three-bullet proof strip (Reliability,
   Craftsmanship, Privacy).
2. **Experience Section:** Narrative about the first five minutes with supporting visuals of the
   dashboard and unboxing.
3. **How It Works:** Interactive version of the four-state engine and telemetry readout.
4. **Design Story:** Showcase materials, form factor, and the founder's design philosophy.
5. **Testimonials & Community:** Quotes, automation recipes, and GitHub stars/social proof.
6. **Technical Deep Dive:** Expandable specs table, threshold defaults, and integration steps.
7. **Footer CTAs:** Purchase, documentation, and newsletter sign-up reinforcing the PLG flywheel.

## 10. Success Metrics

- **Activation:** % of visitors who start the Home Assistant onboarding walkthrough.
- **Advocacy:** Volume of user-generated automations or testimonials submitted post-purchase.
- **Conversion:** Landing-page-to-purchase (or waitlist) conversion rate.
- **Engagement:** Average time on page for the How It Works and Design Story sections.
