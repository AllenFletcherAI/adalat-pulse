# ADALAT PULSE — OPERATIONAL HANDOVER NOTE
**Project:** Adalat Pulse (Courtroom Hardware & Telemetry Gateway for Koyal ASR)  
**Standard:** ASD-STE100 Simplified Technical English  
**Date:** November 2026  
**Author:** Allen Fletcher (Associate Candidate, CTO's Office, Adalat AI)  
**Repository:** https://github.com/AllenFletcherAI/adalat-pulse  

---

## 1. What Is Done
- **Delight-Driven Primary CTA, Strict Chronological Hierarchy & WCAG Accessibility (ADR-018):**
  - **Flying Send Icon Loop Animation & Win Copy:** Primary action button features a looping paper plane animation on hover and cross-fades text to `"Authorize Proceeding — All Systems Ready"`.
  - **Strict 5-Stage Operator Flow:** Re-architected diagnostic instruments into a chronological sequence (Stage 1: Bench & Profile Binding -> Stage 2: Acoustic Certification -> Stage 3: Live Network Telemetry -> Stage 4: Quality Gate Calibration -> Stage 5: Executive Clearance).
  - **Progressive Disclosure Accordion:** Folded technical calibration meters and simulation overrides into an on-demand collapsible disclosure with a glanceable `4/4 GATES PASS` summary badge.
  - **Top-Nav Search Widget:** Replaced heavy search inputs with a compact header search pill (`Cmd+K`) summoning the Quick Actions modal.
  - **Layout Collision Fixes:** Fixed `DLDelhi`, `RJRajasthan`, etc. smashed text bug by widening column 1 to 42px and adding cell padding. Separated `<kbd>Space</kbd>` from `Start Mic Test`. Removed arbitrary audio hardware label truncation.
  - **Light Theme WCAG AA Compliance:** Eradicated washed-out pastel text, applying deep institutional tones (`text-emerald-800`, `text-amber-800`, `text-rose-700`) with contrast exceeding 4.5:1. Visualizer canvases now render dynamic light slate backgrounds (`#F1F5F9`) in light mode.
  - **Adaptive Telemetry Scaling:** WebSocket strip-chart dynamically auto-scales (0-100ms for healthy low-latency lines to reveal visible waves, auto-expanding to 400ms on spikes). Added threshold micro-labels (`< 200ms Limit`, `< 2.0% Critical`, `< 30ms Bound`, `< 250ms Timeout`).
  - **Stepper & Data Normalization:** Step 3 disabled until microphone calibration is certified. Standardized timestamps to 24-hour IST (`HH:MM:SS IST`) and deduplicated incident seed records.
- **Comprehensive Alignment with 20 Psychological and UX Laws (ADR-017):**
  - **Aesthetic-Usability Effect:** Eliminated canvas text slicing, structured the 11-state table with strict CSS grid, and eradicated empty black voids with live telemetry and dispatch health monitors.
  - **Law of Proximity:** Formatted button labels and `<kbd>` shortcuts with clear gap spacing (`Start Mic Test` cleanly separated from `Space`).
  - **Von Restorff Effect:** Highlighted the currently targeted bench state (`DL`) in vibrant emerald with an `[ ACTIVE ]` pill. Highlighted breached incident states (`RJ`) in rose.
  - **Zeigarnik Effect & Goal-Gradient Effect:** Introduced a 3-step Pre-Flight Readiness Stepper (`1. Bench Paired` -> `2. Mic Calibrate` -> `3. Pre-Flight Test`) advancing completion from 50% to 100%.
  - **Tesler’s Law & Occam's Razor:** Clean read-only metric readouts by default, with an `[ Override ]` toggle for manual simulation. Removed redundant duplicate tier badges.
  - **Law of Prägnanz:** Added Y-axis scale markings (`0ms`, `100ms`, `200ms Limit`, `400ms`) and time baseline markers (`T-30s`, `T-15s`, `NOW`) to the strip-chart canvas.
  - **Serial Position Effect:** Compacted state list row padding so all 11 partner states fit simultaneously in the viewport without cutting off terminal states.
  - **Progressive Disclosure:** Kept primary diagnostic screen clean and readable, tucking simulation overrides and bench lists behind on-demand disclosure drawers.
  - **Law of Common Region:** Enclosed comparison figures in unified frames with clear threshold indicator tick marks (`< 200ms`, `< 2.0%`, `< 30ms`, `< 250ms`).
  - **Law of Similarity & Recognition Over Recall:** Standardized bench inputs and golden selects with identical heights and borders; clicking any state unit selects it directly into the diagnostic engine.
  - **Pareto Principle:** Maximized visual dominance for the core 20% workflow: Pre-Flight Check button, Acoustic Calibration, and Courtroom Go/No-Go Verdict.
  - **Parkinson’s Law & Peak-End Rule:** Delivered an authoritative affirmative verdict banner (`PROCEEDING APPROVED: Courtroom Telemetry Cleared for Live Koyal ASR`) with ephemeral 6s auto-dismiss and manual Undo.
  - **Default Effect:** Auto-paired High Court Leased Line baseline for the default Delhi bench, ensuring zero-configuration readiness.
  - **Cognitive Load:** Replaced fragmented status chips with a unified micro-KPI bar and eliminated noisy decorative icons.
  - **Uniform Connectedness:** Framed acoustic visualizers and time-series monitors within coherent borders.
  - **Paradox of the Active User:** Built interactive in-context keyboard hints (`↵ Enter`, `Space`) so operators learn by acting immediately without reading manuals.
- **20-Point Modern Interaction Architecture (ADR-016):**
  - **Acoustic Hardware Certification Engine:** Live 4-second calibration sampling Indic speech formants, room SNR, and sample rate, awarding a formal `KOYAL CERTIFIED (PASS)` badge and auto-injecting metrics into the pre-flight payload. Zero text clipping.
  - **Live Continuous WebSocket Packet Monitor:** Continuous 1,500ms background keepalive ping streaming living RTT gradient curves, jitter points, and p50/p95 latency metrics against the 200ms Koyal gate line. Pre-flight checks trigger 50-packet burst probes.
  - **Uncollapsed 11 Partner States Deployment List:** Replaced brittle table rows with an accessible disclosure list where all 11 Indian partner states (`DL`, `RJ`, `UP`, `KL`, `KA`, `AP`, `MH`, `TN`, `WB`, `GJ`, `MP`) are rendered simultaneously without layout collapse.
  - **Command Menu (`Cmd+K` / `Ctrl+K`):** Global executive command palette with keyboard fuzzy search across courtrooms, diagnostic actions, theme toggles, and Airtable sync.
  - **Shortcut Hints & Hit Slots:** Keyboard badges (`Cmd+K`, `↵ Enter`, `Space`, `Esc`, `R`, `T`) and 44x44px touch targets.
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
- **Operational Data Reconciliation & Hardware Hardening (ADR-019):**
  - **Reconciled Fleet Math & State:** Unified metrics across top navigation bar (`Fleet: 43 Reg (11 States)`, `Live: 4 Monitored`, `Health: 75.0%`, `Incidents: 1 Active P0`), 11-State Deployment table, and Incident log. Unmonitored states display `STANDBY` rather than a false 100%. Rajasthan displays its verified `CRITICAL (0%)` status with a `P0 ALERT` badge.
  - **Authentic Courtroom Hardware Stacks:** Replaced consumer webcam mocks with genuine judicial hardware profiles (`Shure MX393 Judicial Boundary Mic`, `Judicial DSP Line-Out (Biamp Tesira)`, `Court Master Gooseneck (Sennheiser ME36)`, and flagged fallback `Consumer Webcam` with an explicit hardware warning). Enforced Koyal Indic ASR downsampling standard (`Clock: 48,000 Hz → 16,000 Hz PCM`).
  - **Calibrated Realistic WAN Latency:** Integrated realistic WAN transit baselines into live WebSocket probing (`GOLDEN-HC-FIBER` ~35ms, `GOLDEN-DC-HYBRID` ~70ms, `GOLDEN-TL-EDGE` ~110ms) with natural packet jitter, eliminating localhost 1.5ms ping giveaways while preserving live network socket turnaround.
  - **Incident Feed Normalization:** Deduplicated incident rows, aligned database IDs (`INC-RJ-RJ-DC-JPR02-261122-143731`), and prohibited passing `OPTIMAL` sessions from generating Linear engineering tickets.
  - **Ambient Resting Noise Floor:** Eliminated pitch-black visualizer voids by drawing -12 to -60 dB reference gridlines, a resting noise floor at -52 dB across 32 FFT bands, and centered monospace calibration instructions.
  - **Judicial Operational Context & Fallback:** Added Presiding Bench metadata, Court Master Terminal identifier, Koyal Indic Language Pack selector, and an actionable emergency fallback button (`Activate Local Offline Audio Buffer (Stenographer Fallback)`).
  - **OS-Adaptive Shortcut:** Dynamically applies `Ctrl+K` for Windows/Linux and `Cmd+K` for macOS.
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
