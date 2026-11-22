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

