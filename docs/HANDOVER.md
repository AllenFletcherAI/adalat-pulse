# ADALAT-PULSE — OPERATIONAL HANDOVER NOTE
**Project:** Adalat-Pulse (Courtroom Pre-Flight Diagnostic & Deployment Telemetry Gateway)  
**Standard:** ASD-STE100 Simplified Technical English  
**Date:** November 2026  
**Author:** Allen Fletcher (Associate Candidate, CTO's Office, Adalat AI)  

---

## 1. What Is Done
- **Strict Data Contracts:** Pydantic v2 validation models in `src/models.py` covering network latency, jitter, packet loss, WebSocket keepalive RTT, microphone hardware sample rate, and ambient noise floor (SNR).
- **Deterministic Evaluation Engine:** `src/evaluator.py` evaluates all 6 telemetry parameters against Koyal ASR quality gates. Returns `OPTIMAL`, `DEGRADED`, or `CRITICAL` with plain-language reason codes.
- **SQLite Persistence (WAL Mode):** Append-only telemetry table and incident tracking in `src/database.py` with zero-config local reliability.
- **Automated Incident Routing:** Real Slack Block Kit dispatcher (`#all-adalat-pulse-alerts`) and Linear P0 issue creator in `src/alerts.py`.
- **Bi-Directional Airtable Sync:** Live REST client in `src/airtable_sync.py` syncing courtroom health to base `appviUqZAQGGD2ILo`.
- **FastAPI Gateway & WebSocket Probe:** REST endpoints and live `/ws/probe` endpoint in `src/main.py`.
- **Operational Dashboard:** Vanilla ES6 single-page application in `src/static/` with live Web Audio API microphone sampling and 11-state fleet grid.
- **Automated Verification:** 20 out of 20 unit and integration tests passing in `tests/`.
- **Containerization:** Multi-stage production `Dockerfile` and `docker-compose.yml`.

---

## 2. Working On Now
- End-to-end container verification on local Docker daemon.
- Synchronizing documentation artifacts across `docs/`.
- Preparing initial public release commit on GitHub.

---

## 3. Broken or Dangerous (Risk Register)
- **Direct Internet Exposure:** The gateway currently listens on `0.0.0.0:8000`. In production, place behind NGINX or Cloudflare Tunnel with HMAC request signing.
- **Database Backup:** SQLite `.db` file must be backed up via Litestream or cron snapshot when running in persistent cloud VMs.
- **Live Airtable Rate Limits:** Airtable enforces a 5 requests/second limit. For large batches (>100 courtrooms), use Airtable's bulk update endpoint (10 records per request).

---

## 4. What To Do Next
1. Verify Docker image build receipt.
2. Commit all artifacts to git with atomic messages.
3. Push main branch to `https://github.com/AllenFletcherAI/adalat-pulse`.
4. Test live pre-flight diagnostic through the browser dashboard.

---

## 5. Do Not Touch
- **`src/evaluator.py` Threshold Values:** Do not loosen threshold constants (e.g. packet loss 2.0%, sample rate 16kHz) without explicit approval from Koyal ASR speech science team.
- **SQLite WAL Mode:** Do not change `PRAGMA journal_mode=WAL` to `DELETE` or `MEMORY`; WAL is essential for non-blocking concurrent writes.
