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
  - *Level 1 (Outcome):* Zero-word-drop Koyal ASR legal guarantee banner.
  * *Level 2 (Autonomous Edge Research):* 5-second Web Audio API FFT noise floor analysis and WebSocket ping/pong probe.
  * *Level 3 (Interactive Interview):* Dynamic technician dialog (`/api/v1/telemetry/interview`) enabling field remediation (e.g. fan turned off grants $+6\text{ dB}$ SNR clearance).
  * *Level 4 (Golden Exemplars):* Golden Baseline profiles (`GOLDEN-HC-FIBER`, `GOLDEN-DC-HYBRID`, `GOLDEN-TL-EDGE`) with a 0–100% alignment score and live deltas.
- **SQLite Persistence (WAL Mode):** Append-only telemetry table, incidents table, golden profiles seed table, and diagnostic interviews table in `src/database.py` with auto-initialization and zero-config local reliability.
- **Automated Incident Routing:** Real Slack Block Kit dispatcher (`#all-adalat-pulse-alerts`) and Linear P0 issue creator in `src/alerts.py`. Verified with live Linear issue `ALL-7` and live Slack alert.
- **Bi-Directional Airtable Sync:** Live REST client in `src/airtable_sync.py` syncing courtroom health to base `appviUqZAQGGD2ILo`. Verified with live record `recMbWX6eUaV3pnOD` (`typecast: True` enabled).
- **FastAPI Gateway & WebSocket Probe:** REST endpoints (`/report`, `/interview`, `/golden-profiles`, `/courtrooms/status`, `/health`) and live `/ws/probe` endpoint in `src/main.py`.
- **Operational Dashboard:** Vanilla ES6 single-page application in `src/static/` with live Web Audio API microphone sampling, 11-state fleet grid, Golden Standard comparison gauge, and Guided Interview modal.
- **Automated Verification:** 30 out of 30 unit and integration tests passing in `tests/` in 10.43s.
- **Git Repository & Remote Push:** Public repository created and synced at `https://github.com/AllenFletcherAI/adalat-pulse`.
- **Containerization:** Multi-stage production `Dockerfile` and `docker-compose.yml`.

---

## 2. Working On Now
- Finalizing documentation synchronization for Prompt Pyramid deployment.
- Pushing latest commits to GitHub `origin/main`.
- Relaunching local gateway background daemon.

---

## 3. Broken or Dangerous (Risk Register)
- **Direct Internet Exposure:** The gateway currently listens on `0.0.0.0:8000`. In production, place behind NGINX or Cloudflare Tunnel with HMAC request signing.
- **Database Backup:** SQLite `.db` file must be backed up via Litestream or cron snapshot when running in persistent cloud VMs.
- **Live Airtable Rate Limits:** Airtable enforces a 5 requests/second limit. For large batches (>100 courtrooms), use Airtable's bulk update endpoint (10 records per request).

---

## 4. What To Do Next
1. Commit all Prompt Pyramid artifacts to git.
2. Push main branch to `https://github.com/AllenFletcherAI/adalat-pulse`.
3. Keep the background server daemon active on port 8000.
4. Verify end-to-end dashboard accessibility at `http://localhost:8000`.

---

## 5. Do Not Touch
- **`src/evaluator.py` Threshold Values:** Do not loosen threshold constants (e.g. packet loss 2.0%, sample rate 16kHz) without explicit approval from Koyal ASR speech science team.
- **SQLite WAL Mode:** Do not change `PRAGMA journal_mode=WAL` to `DELETE` or `MEMORY`; WAL is essential for non-blocking concurrent writes.
