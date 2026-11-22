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
