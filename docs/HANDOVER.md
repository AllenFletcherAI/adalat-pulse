# ADALAT PULSE — OPERATIONAL HANDOVER NOTE
**Project:** Adalat Pulse (Courtroom Hardware & Telemetry Gateway for Koyal ASR)  
**Standard:** ASD-STE100 Simplified Technical English  
**Date:** November 2026  
**Author:** Allen Fletcher (Associate Candidate, CTO's Office, Adalat AI)  
**Repository:** https://github.com/AllenFletcherAI/adalat-pulse  

---

## 1. What Is Done
- **Real-Time Hardware Audio Laboratory (IRL/IRT Voice Testing):** Dual visualizers featuring a 32-band FFT frequency spectrum analyzer canvas and time-domain oscilloscope canvas powered by Web Audio API `navigator.mediaDevices.getUserMedia()`. Includes explicit `[Start Mic Test]` / `[Stop Mic Test]` toggle and `[Reset Audio]` control with complete media track cleanup and canvas clearing.
- **WebSocket Packet Round-Trip Strip-Chart:** Live scrolling HTML5 canvas plotting real-time `/ws/probe` packet round-trip times (RTT) and jitter points against the 200ms Koyal ASR guideline.
- **Dynamic Multi-Metric Comparative Figures & Delta Bars:** Side-by-side comparison for Latency, Packet Loss, Jitter, and WS Keepalive RTT featuring live measurements, golden baselines, real-time deltas, Pass/Breach gate badges, and threshold indicator ticks.
- **Purge of All Mock Scenarios:** Eradicated simulated scenario buttons (`Fiber optimal`, `Monsoon`, etc.). All diagnostics operate exclusively on live WebSocket and microphone audio.
- **Ephemeral Auto-Dismissing Verdict Banner:** Automatically dismisses after 6 seconds on optimal clearance, with manual `[Dismiss]` and global `[Reset Console]` capabilities.
- **Live Incident Routing on Every Check:** Diagnostic checks breaching degraded or critical thresholds immediately prepend an incident entry to the Live Incident Routing table with live IST timestamps, Slack dispatch status, and Linear ticket IDs.
- **Hierarchical 11-State Jurisdiction Subsections:** Expandable inline accordion tables revealing Principal Seats, regional benches, District Courts, Sessions Courts, and Taluka Courts across all 11 states with direct `[Test]` actions.
- **Deterministic Order of Operations & Automatic Pairing:** Courtroom bench selection automatically binds to its certified golden standard (`-HC-` -> Leased Line, `-DC-` -> Dual-ISP, `-TL-` -> Edge 4G) with unified 38px height and matching chevrons.
- **Solitary Bold Brand Header:** Clean **Adalat Pulse** typography alone on left (wave icon eradicated).
- **100% Emoji Eradication:** Zero emojis across all code, alerts, Linear titles, and documentation.
- **Strict 100dvh Single-Viewport Fit:** High-density command cockpit fits strictly within `100dvh` with zero window vertical scrollbars.
- **Automated Verification:** 30 out of 30 unit and integration tests passing in `tests/`.
- **Server Health:** Uvicorn daemon running healthy on port 8000 (`http://localhost:8000`).

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
