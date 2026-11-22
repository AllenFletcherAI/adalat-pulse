# ADALAT PULSE — OPERATIONAL HANDOVER NOTE
**Project:** Adalat Pulse (Courtroom Hardware & Telemetry Gateway for Koyal ASR)  
**Standard:** ASD-STE100 Simplified Technical English  
**Date:** November 2026  
**Author:** Allen Fletcher (Associate Candidate, CTO's Office, Adalat AI)  
**Repository:** https://github.com/AllenFletcherAI/adalat-pulse  

---

## 1. What Is Done
- **Real-Time IRL Audio Waveform Oscilloscope:** HTML5 canvas running off Web Audio API `analyser.getByteTimeDomainData()`. Reacts dynamically to real spoken operator voice in real time, calculating live room SNR and hardware sample rate (44.1k/48k Hz).
- **Deterministic Order of Operations & Automatic Pairing:**
  - Selecting any bench automatically binds to its certified golden standard (`-HC-` $\rightarrow$ Leased Line, `-DC-` $\rightarrow$ Dual-ISP, `-TL-` $\rightarrow$ Edge 4G).
  - Aligned both inputs to unified 38px height, identical padding, and custom SVG chevrons.
- **Side-by-Side Benchmark Telemetry Table:** Replaced isolated inputs with a structured comparison matrix comparing Live Measured numbers against Golden Targets, calculating real deltas ($\Delta$) and displaying Pass/Breach gate badges in real time.
- **11-State Regional Fleet Jurisdiction Table:** Replaced floating micro-cards with an executive table showing jurisdiction seats, active benches, health percentages, and quick diagnostic testing.
- **Structured Incident Routing Log Table:** Replaced raw markdown dump in Incident Inspector modal with a structured breaches table (Parameter, Measured, Limit, ASR Impact), Linear `ALL-7` ticket, and Slack `#all-adalat-pulse-alerts` proof.
- **Zero-Crash Verdict Integration:** Fixed bug where `ga.deltas.latency_ms` crashed the UI; now safely reads `latency_delta_ms`, `packet_loss_delta_pct`, and `snr_delta_db`.
- **100% Emoji Eradication:** Audited entire codebase and documentation; purged all emojis across UI, Slack payloads, Linear titles, and docs.
- **Zero Marketing Fluff:** Purged `6,000+ judges`, `How it works` modal, and instructional captions.
- **Strict 100dvh Single-Viewport Fit:** Optimized layout vertical rhythm so the entire command cockpit strictly fits within `100dvh` without window vertical scrollbars or cut-off verdict cards.
- **Automated Verification:** 30 out of 30 unit and integration tests passing in `tests/` in 11.99s.
- **Server Health:** Uvicorn daemon running on port 8000 (`http://localhost:8000`).

---

## 2. Working On Now
- Operational in production executive mode with live oscilloscope voice testing, structured comparison tables, and zero window scrolling.
- Background Uvicorn daemon active on port 8000.

---

## 3. Broken or Dangerous (Risk Register)
- **Direct Internet Exposure:** The gateway currently listens on `0.0.0.0:8000`. In production, place behind NGINX or Cloudflare Tunnel with TLS termination.
- **Database Backup:** SQLite `.db` file must be backed up via Litestream or cron snapshot when running in persistent cloud VMs.
- **Live Airtable Rate Limits:** Airtable enforces a 5 requests/second limit. For large batches (>100 courtrooms), use Airtable's bulk update endpoint.

---

## 4. What To Do Next
1. Commit all UI, audio oscilloscope, and table structure updates to git.
2. Push to `https://github.com/AllenFletcherAI/adalat-pulse`.
3. Keep background server daemon active on port 8000.

---

## 5. Do Not Touch
- **`src/evaluator.py` Threshold Values:** Do not loosen threshold constants (e.g. packet loss 2.0%, sample rate 16kHz) without explicit approval from Koyal ASR speech science team.
- **SQLite WAL Mode:** Do not change `PRAGMA journal_mode=WAL` to `DELETE` or `MEMORY`; WAL is essential for non-blocking concurrent writes.
