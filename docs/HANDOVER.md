# ADALAT PULSE — OPERATIONAL HANDOVER NOTE
**Project:** Adalat Pulse (Courtroom Hardware & Telemetry Gateway for Koyal ASR)  
**Standard:** ASD-STE100 Simplified Technical English  
**Date:** November 2026  
**Author:** Allen Fletcher (Associate Candidate, CTO's Office, Adalat AI)  
**Repository:** https://github.com/AllenFletcherAI/adalat-pulse  

---

## 1. What Is Done
- **Real-Time Live WebSocket Probe Client:** Replaced simulated timer loops with 100% real WebSocket packet streaming to `/ws/probe`. Sends 50 timestamped frames over 5 seconds, measures real RTT, calculates real RFC 3550 statistical network jitter ($J_i = J_{i-1} + \frac{|D(i-1, i)| - J_{i-1}}{16}$), and live packet loss, streaming measured numbers live into UI inputs.
- **Hardware Web Audio API Sampling:** Samples real audio hardware sample rate (44.1k/48k Hz), computes root-mean-square (RMS) acoustic noise floor, and displays live room Signal-to-Noise Ratio (SNR) in dB with an active VU meter.
- **Zero-Clipping Readable Typographic System:** Eradicated experimental `text-box-trim` that clipped ascenders and capital letters (*L*, *W*, *S*, *d*, *h*). Scaled input heights to 40px with comfortable padding and flex-aligned unit badges (`ms`, `%`, `dB`, `Hz`).
- **Complete Interactive Drill-Downs Across Every Element:**
  - *11-State Regional Matrix:* Clicking any state (`KL`, `KA`, `AP`, `MH`, `DL`, `TN`, `UP`, `WB`, `GJ`, `RJ`, `MP`) opens the State Courtroom Explorer displaying principal seat, judicial benches, live health status, and a 1-click "Test Bench" launcher.
  - *Live Incident Routing Inspector:* Clicking any P0 incident opens the Incident Inspector modal displaying the real Linear ticket ID (`ALL-7`), Slack Block Kit delivery status (`#all-adalat-pulse-alerts`), breached quality gates, and raw telemetry snapshot.
  - *Interactive Header Micro-KPIs:* Clicking `Active`, `Fleet`, or `Optimal` opens the Global Fleet Telemetry Matrix; clicking `Incidents` opens the Incident Inspector modal.
  - *Scenario Presets:* "Fiber optimal", "Monsoon", "Fan noise", and "4G lag" tabs visually highlight with distinct active styling and load baseline stress values.
  - *Courtroom Search Combobox:* Dropdown listing benches across all 11 partner state jurisdictions with instant search.
  - *System Info & Architecture Hub:* "How it works" modal explaining the mission, Koyal ASR quality gates, and automated P0 routing.
- **Dual Light/Dark Theme Engine:** True CSS-variable theming (`--bg-canvas`, `--bg-surface`, `--bg-sub`, `--border-alpha`, `--text-primary`) supporting instant switching between dark mode and high-contrast courtroom light mode with `localStorage` persistence.
- **Clean Institutional Branding:** Renamed to **Adalat Pulse** (no hyphen, no "Pre-Flight Gateway" suffix, no kiddish scales icon); introduced a precision telemetry pulse waveform SVG.
- **Strict Data Contracts & Persistence:** Pydantic v2 schemas in `src/models.py`, append-only SQLite persistence with WAL mode in `src/database.py`, and certified golden baselines.
- **Automated Incident Routing & Airtable Sync:** Live Slack Block Kit dispatcher (`#all-adalat-pulse-alerts`), Linear GraphQL P0 issue creator (`ALL-7`), and REST Airtable sync client (`appviUqZAQGGD2ILo`).
- **Automated Test Suite:** 30 out of 30 unit and integration tests passing in `tests/` in 11.71s.
- **Server Health:** Uvicorn running healthy on port 8000 (`http://localhost:8000`).

---

## 2. Working On Now
- System operating with 100% authentic real-time live network probing, zero mocks, and full interactivity across all components.
- Background Uvicorn daemon running on port 8000.

---

## 3. Broken or Dangerous (Risk Register)
- **Direct Internet Exposure:** The gateway currently listens on `0.0.0.0:8000`. In production, place behind NGINX or Cloudflare Tunnel with TLS termination.
- **Database Backup:** SQLite `.db` file must be backed up via Litestream or cron snapshot when running in persistent cloud VMs.
- **Live Airtable Rate Limits:** Airtable enforces a 5 requests/second limit. For large batches (>100 courtrooms), use Airtable's bulk update endpoint.

---

## 4. What To Do Next
1. Commit all UI, WebSocket, and interactivity updates to git.
2. Push to `https://github.com/AllenFletcherAI/adalat-pulse`.
3. Keep background server daemon active on port 8000.

---

## 5. Do Not Touch
- **`src/evaluator.py` Threshold Values:** Do not loosen threshold constants (e.g. packet loss 2.0%, sample rate 16kHz) without explicit approval from Koyal ASR speech science team.
- **SQLite WAL Mode:** Do not change `PRAGMA journal_mode=WAL` to `DELETE` or `MEMORY`; WAL is essential for non-blocking concurrent writes.
