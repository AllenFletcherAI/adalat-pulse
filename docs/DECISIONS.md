# ARCHITECTURAL DECISION RECORDS (ADR)
**Standard:** ASD-STE100 Simplified Technical English  
**System:** Adalat-Pulse  

---

## ADR-001: SQLite with WAL Mode vs Managed PostgreSQL
* **Date:** November 2026
* **Decision:** Use local SQLite with Write-Ahead Logging (`PRAGMA journal_mode=WAL;`).
* **Why:** `Adalat-Pulse` is designed to run both as a centralized CTO operations hub and as an edge gateway inside high court server rooms across Indian states. SQLite requires zero network configuration, zero password management, and zero operational maintenance. In WAL mode, SQLite supports non-blocking concurrent reads during telemetry writes.
* **Rejected Alternative:** Managed PostgreSQL / Cloud RDS. Rejected because it introduces remote network dependencies, connection pool exhaustion risks, and high operational overhead during edge deployments.
* **When to Reconsider:** If concurrent ingestion writes exceed 2,000 requests per second across multiple server nodes.

---

## ADR-002: Deterministic Quality Gates vs Statistical / ML Anomaly Detection
* **Date:** November 2026
* **Decision:** Use pure, deterministic threshold evaluation in `src/evaluator.py`.
* **Why:** In a live judicial courtroom with a sitting judge, an alert that halts or delays a court session must be 100% explainable and reproducible. If a court session is halted, the district technical officer must know the exact rule that failed (e.g. *packet loss was 3.8%, exceeding the 2.0% limit*). Statistical or ML anomaly models produce probabilistic outputs that cause confusion and debate during courtroom incidents.
* **Rejected Alternative:** Isolation Forests or LSTM Anomaly Detectors. Rejected because black-box models cannot provide deterministic legal or operational guarantees.
* **When to Reconsider:** If analyzing long-term seasonal broadband degradation across entire state districts.

---

## ADR-003: Vanilla ES6 + Tailwind CDN vs React / Next.js SPA
* **Date:** November 2026
* **Decision:** Build the operational control dashboard with Vanilla ES6 and Tailwind CSS via CDN.
* **Why:** Eliminates 300+ MB of `node_modules`, build toolchains, and package vulnerabilities. The entire dashboard loads in under 200 ms and can be inspected or modified directly in any environment without a Node.js runtime.
* **Rejected Alternative:** React / Next.js. Rejected because build steps and dependency bloat create unnecessary friction for operational gateways.
* **When to Reconsider:** If the frontend requires complex multi-page state management with tens of thousands of simultaneous UI components.

---

## ADR-004: Live Web Audio API & WebSockets vs Synthetic Mock Sliders
* **Date:** November 2026
* **Decision:** Implement real hardware inspection using the browser's Web Audio API and real WebSocket round-trips over `/ws/probe`.
* **Why:** Synthetic dummy data gives false confidence. Real courtrooms fail because of hardware mismatch (e.g. 8 kHz analogue PA jacks) or acoustic noise (unbalanced ceiling fans). Using `navigator.mediaDevices.getUserMedia` and `AnalyserNode` FFT allows real courtroom testing on actual edge hardware.
* **Rejected Alternative:** Static sliders with fake random numbers. Rejected because simulated data masks physical courtroom hardware defects.

---

## ADR-005: 4-Tier Prompt Pyramid Architecture (Golden Exemplars & Interactive Interviews vs Rigid Linear Scripts)
* **Date:** November 2026
* **Decision:** Implement the 4-tier Prompt Pyramid operational model:
  1. *Level 1 (Outcome First):* Establish a single non-negotiable legal outcome ("100% Zero-Word-Drop Koyal Indic ASR Guarantee").
  2. *Level 2 (Autonomous Edge Research):* Collect real-world ground truth via browser Web Audio FFT analysis and WebSocket burst probing.
  3. *Level 3 (Interactive Interview):* Generate interactive technician dialogues for degraded telemetry (`Q-AUDIO-FAN`, `Q-NET-UPLINK`) to resolve gray areas with direct remediation before raising false-alarm session cancellations.
  4. *Level 4 (Golden Exemplars):* Benchmark live measurements against 3 certified hardware/network baselines (`GOLDEN-HC-FIBER`, `GOLDEN-DC-HYBRID`, `GOLDEN-TL-EDGE`) with a 0–100% Alignment Score and deltas.
* **Why:** In field deployments across 6,000+ courtrooms, rigid procedural scripts fail when rural broadband fluctuates or ceiling fans create acoustic noise. The Prompt Pyramid mirrors the engineering paradigm practiced at top AI labs: anchor on the outcome, research physical reality, interview operators to disambiguate edge cases, and anchor to a concrete exemplar of excellence.
* **Rejected Alternative:** Rigid binary cutoff alerts or automated hard drops without operator remediation. Rejected because cancelling live hearings over minor remediable noise (e.g. an oscillating fan) damages court schedules.
* **When to Reconsider:** If autonomous edge acoustic filtering hardware is deployed at 100% of physical courtrooms, eliminating environmental variance.

---

## ADR-006: 20-Point Ergonomic Design System (Typographic, Motion, and Perceptual OKLCH Standards)
* **Date:** November 2026
* **Decision:** Enforce a comprehensive 20-point ergonomic design system across the operational frontend (`src/static/index.html` and `src/static/app.js`):
  1. *Typography & Spatial Hierarchy:*
     - **Kerning:** Explicit `font-feature-settings: "kern" 1, "liga" 1; text-rendering: optimizeLegibility;` on courtroom identifiers and headers.
     - **Tracking:** Loose tracking on uppercase micro-labels (`tracking-wider`); snug tracking on display headings (`tracking-tight`).
     - **Leading:** Contextual line-height (`leading-relaxed` on legal outcome prose; `leading-tight` on verdict titles).
     - **X-Height:** Inter font stack prioritizing tall lowercase x-height for readability on legacy 720p courtroom monitors.
     - **Line Length:** Optimal reading measure constrained to 55–65 characters (`max-w-[65ch]`).
     - **Widow Control:** CSS `text-wrap: balance` on headings, `text-wrap: pretty` on paragraphs, and non-breaking spaces (`&nbsp;`) before final words.
  2. *Geometry & Viewport Bounds:*
     - **Optical Center:** Vertically offsetting modals to 38% from the top (`optical-center-modal`) rather than mathematical 50%.
     - **Zero Cumulative Layout Shift (CLS):** Pre-allocated minimum height (`min-h-[320px]`) with shimmer skeleton loader during probing.
     - **Safe Area Insets:** CSS `env(safe-area-inset-*)` padding for edge tablets and ruggedized courtroom kiosks.
     - **Touch Targets:** Minimum 44px × 44px interactive hitboxes meeting WCAG 2.2 AA standards.
  3. *Color Physics & Numerical Integrity:*
     - **OKLCH Color Space:** Perceptually uniform status colors (`--ok-optimal`, `--ok-degraded`, `--ok-critical`, `--ok-golden`) ensuring equal perceived luminance in high-contrast dark mode.
     - **Tabular Numbers:** `font-variant-numeric: tabular-nums;` on all clocks, latency, loss, SNR, and golden scores to stop horizontal number jitter.
  4. *Interaction Architecture & UX:*
     - **Affordance:** Tactile press states (`active:scale-[0.985]`), border highlights, focus-visible rings, and explicit cursors.
     - **Accessible Combo Box:** Keyboard-first courtroom bench search and selection (`ArrowDown`, `ArrowUp`, `Enter`, `Escape`) with WAI-ARIA attributes.
     - **Progressive Disclosure:** 3-tier presentation (At-a-Glance verdict -> Key metrics -> Deep diagnostic accordion revealing raw telemetry JSON).
     - **Optimistic Updates:** Instant UI upgrade upon technician remediation with automatic rollback safety on network failure.
  5. *Motion Choreography & Transitions:*
     - **Origin-Aware Animation:** Modal expands directly from the clicked trigger button's bounding coordinates.
     - **Interruptible Animation:** Cancelable interval loops and Web Animations API transitions allowing instant reversal without visual glitches.
     - **Stagger Dynamics:** Choreographed cascade (`--stagger-index`) on fleet cards and interview options.
     - **Shared Element Transitions:** Native browser View Transitions API support (`document.startViewTransition`) during courtroom selection.
* **Why:** Courtroom technical officers frequently work under stressful conditions during active hearings on diverse hardware (from 4K CTO displays to 10-year-old CRT/LCD district terminals). The 20-point standard eliminates cognitive friction, prevents misclicks, and ensures complete accessibility across all 11 partner states.
* **Rejected Alternative:** Generic ad-hoc styling with arbitrary Tailwind utilities. Rejected because inconsistent paddings, shifting layouts, and small touch targets lead to operator errors in high-stakes judicial environments.
* **When to Reconsider:** If a dedicated native desktop client (e.g. Tauri / Electron) completely replaces the browser-based gateway dashboard.


