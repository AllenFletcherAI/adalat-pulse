# ADALAT-PULSE — OPERATIONAL HANDOVER NOTE
**Project:** Adalat-Pulse (Courtroom Pre-Flight Diagnostic & Deployment Telemetry Gateway)  
**Standard:** ASD-STE100 Simplified Technical English  
**Date:** November 2026  
**Author:** Allen Fletcher (Associate Candidate, CTO's Office, Adalat AI)  

---

## 1. What Is Done
- **Strict Data Contracts:** Pydantic v2 validation models in `src/models.py` covering network latency, jitter, packet loss, WebSocket keepalive RTT, microphone hardware sample rate, ambient noise floor (SNR), Golden Baselines, and Operator Interview schemas.
- **Deterministic Evaluation Engine:** `src/evaluator.py` evaluates all 6 telemetry parameters against Koyal ASR quality gates. Returns `OPTIMAL`, `DEGRADED`, or `CRITICAL` with plain-language reason codes.
- **4-Tier Prompt Pyramid Architecture:** Fully implemented across `src/models.py`, `src/evaluator.py`, `src/database.py`, and `src/static/`:
  - *Level 1 (Outcome):* Zero-word-drop Koyal ASR legal guarantee.
  - *Level 2 (Autonomous Edge Research):* 5-second Web Audio API FFT noise floor analysis and WebSocket ping/pong probe.
  - *Level 3 (Interactive Interview):* Dynamic technician dialog (`/api/v1/telemetry/interview`) enabling field remediation (e.g. fan turned off grants $+6\text{ dB}$ SNR clearance).
  - *Level 4 (Golden Exemplars):* Golden Baseline profiles (`GOLDEN-HC-FIBER`, `GOLDEN-DC-HYBRID`, `GOLDEN-TL-EDGE`) with a 0–100% alignment score and live deltas.
- **SQLite Persistence (WAL Mode):** Append-only telemetry table, incidents table, golden profiles seed table, and diagnostic interviews table in `src/database.py` with auto-initialization and zero-config local reliability.
- **Automated Incident Routing:** Real Slack Block Kit dispatcher (`#all-adalat-pulse-alerts`) and Linear P0 issue creator in `src/alerts.py`. Verified with live Linear issue `ALL-7` and live Slack alert.
- **Bi-Directional Airtable Sync:** Live REST client in `src/airtable_sync.py` syncing courtroom health to base `appviUqZAQGGD2ILo`. Verified with live record `recMbWX6eUaV3pnOD` (`typecast: True` enabled).
- **FastAPI Gateway & WebSocket Probe:** REST endpoints (`/report`, `/interview`, `/golden-profiles`, `/courtrooms/status`, `/health`) and live `/ws/probe` endpoint in `src/main.py`.
- **Zero-Scroll Single-Viewport Architecture (ADR-010):**
  - Viewport strictly locked to 100dvh (`h-[100dvh] overflow-hidden`): zero browser window scrolling on any screen $\ge 1280 \times 800$.
  - Eradicated all introductory/marketing copy (no giant H2 hero or explanatory paragraphs).
  - Consolidated 4 oversized KPI cards into a clean 44px top header micro-stat strip (`Active`, `Fleet`, `Optimal`, `Incidents`).
  - Unified all 6 telemetry parameters into a single compact horizontal grid with an integrated 4px hairline audio level bar.
  - In-place pre-allocated verdict container (zero layout shift; standby $\rightarrow$ progress $\rightarrow$ verdict without page height expansion).
  - Compact 4-column regional matrix (38px cards) and strictly contained incident feed (internal scroll only).
- **Typographic Craftsmanship & OKLCH Micro-Interactions (ADR-012):**
  - Font stacks: Standardized on `Switzer` (Clean Swiss Sans) and `IBM Plex Mono` (Tech Mono). Purged `Inter`, `Roboto`, `Geist`, `JetBrains Mono`.
  - Zero-shift tabs: Reserved bold width via `inline-grid` stacking with hidden `::after` copy.
  - Centered labels/buttons: `text-box-trim: trim-both` and `text-box-edge: cap alphabetic`.
  - Small-caps acronyms: `font-variant-caps: all-small-caps` on `ASR`, `SNR`, `RTT`, `WS`, `WAL`, `P0`.
  - Typographic curly quotes: `“`, `”`, `’` applied across all copy and generated reason codes.
  - Alpha borders: `rgb(255 255 255 / 0.08)` blending seamlessly across surface depth levels (L0 to L3).
  - OKLCH status palette: Matched lightness $L = 0.72$ for optimal, degraded, and critical indicators.
  - Gradients & edge masks in OKLCH: Eliminates muddy gray dead zones.
  - Popovers & exits: Start at `scale: 0.95` from trigger bounding box; exits 20% shorter (160ms vs 200ms) collapsing toward trigger.
  - Icon swaps: Blurs to 4px and scales to 0.85 on exit; sharpens and scales to 1.0 on entrance.
  - Staggered settlements: 30ms list row cascade; +60ms/+120ms/+180ms verdict detail settlements.
  - Single-shot harmonic success pulse on clearance and sync completion.
- **Automated Verification:** 30 out of 30 unit and integration tests passing in `tests/` in 12.25s.
- **Git Repository & Remote Push:** Public repository created and synced at `https://github.com/AllenFletcherAI/adalat-pulse`.
- **Containerization:** Multi-stage production `Dockerfile` and `docker-compose.yml`.

---

## 2. Working On Now
- System operating with full craftsmanship, typography, and motion standards in production zero-scroll mode.
- Uvicorn daemon running healthy on port 8000.

---

## 3. Broken or Dangerous (Risk Register)
- **Direct Internet Exposure:** The gateway currently listens on `0.0.0.0:8000`. In production, place behind NGINX or Cloudflare Tunnel with HMAC request signing.
- **Database Backup:** SQLite `.db` file must be backed up via Litestream or cron snapshot when running in persistent cloud VMs.
- **Live Airtable Rate Limits:** Airtable enforces a 5 requests/second limit. For large batches (>100 courtrooms), use Airtable's bulk update endpoint (10 records per request).

---

## 4. What To Do Next
1. Commit all craftsmanship and typographic updates to git.
2. Push main branch to `https://github.com/AllenFletcherAI/adalat-pulse`.
3. Keep background server daemon active on port 8000.

---

## 5. Do Not Touch
- **`src/evaluator.py` Threshold Values:** Do not loosen threshold constants (e.g. packet loss 2.0%, sample rate 16kHz) without explicit approval from Koyal ASR speech science team.
- **SQLite WAL Mode:** Do not change `PRAGMA journal_mode=WAL` to `DELETE` or `MEMORY`; WAL is essential for non-blocking concurrent writes.
