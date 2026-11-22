# ADALAT PULSE — OPERATIONAL HANDOVER NOTE
**Project:** Adalat Pulse (Courtroom Hardware & Telemetry Gateway for Koyal ASR)  
**Standard:** ASD-STE100 Simplified Technical English  
**Date:** November 2026  
**Author:** Allen Fletcher (Associate Candidate, CTO's Office, Adalat AI)  
**Repository:** https://github.com/AllenFletcherAI/adalat-pulse  

---

## 1. What Is Done
- **20-Point Modern Interaction Architecture (ADR-016):**
  - **Acoustic Hardware Certification Engine:** Live 4-second calibration sampling Indic speech formants, room SNR, and sample rate, awarding a formal `KOYAL CERTIFIED (PASS)` badge and auto-injecting metrics into the pre-flight payload. Zero text clipping.
  - **Live Continuous WebSocket Packet Monitor:** Continuous 1,500ms background keepalive ping streaming living RTT gradient curves, jitter points, and p50/p95 latency metrics against the 200ms Koyal gate line. Pre-flight checks trigger 50-packet burst probes.
  - **Uncollapsed 11 Partner States Deployment List:** Replaced brittle table rows with an accessible disclosure list where all 11 Indian partner states (`DL`, `RJ`, `UP`, `KL`, `KA`, `AP`, `MH`, `TN`, `WB`, `GJ`, `MP`) are rendered simultaneously without layout collapse.
  - **Command Menu (`Cmd+K` / `Ctrl+K`):** Global executive command palette with keyboard fuzzy search across courtrooms, diagnostic actions, theme toggles, and Airtable sync.
  - **Shortcut Hints & Hit Slots:** Keyboard badges (`⌘K`, `↵ Enter`, `Space`, `Esc`, `R`, `T`) and 44x44px touch targets.
  - **Floating Undo Toast:** 5-second interactive undo notification on console resets.
  - **Stale-While-Revalidate (SWR):** Instant zero-latency `localStorage` cache hydration with background revalidation.
  - **Swipe-to-Dismiss Sheets:** Touch/pointer downward drag gesture dismissing modals on 100px threshold.
  - **Continuous Squircles & Safe Area Insets:** Superellipse corner radii and `env(safe-area-inset-*)` support.
  - **Idempotency Keys:** Deterministic UUIDv4 token (`X-Idempotency-Key`) preventing duplicate writes.
  - **Amazon Safe Triangle:** Pointer steering tracking preventing premature submenu closure.
- **Side-by-Side Benchmark Telemetry Table:** Real-time deltas ($\Delta$), Pass/Breach gate badges, and threshold indicator ticks.
- **Filtered Incident Routing Log:** `ALL` and `CRITICAL` filters with automated dispatch standby monitoring.
- **Deterministic Order of Operations & Automatic Pairing:** Courtroom bench selection automatically binds to its certified golden standard (`-HC-` -> Leased Line, `-DC-` -> Dual-ISP, `-TL-` -> Edge 4G).
- **100% Emoji Eradication:** Zero emojis across code, UI, alerts, and documentation.
- **Strict 100dvh Single-Viewport Fit:** Complete executive command cockpit strictly fits within `100dvh` with zero window-level vertical scrollbars.
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
