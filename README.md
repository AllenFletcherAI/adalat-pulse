# ⚡ Adalat-Pulse

> **Edge-ready Courtroom Pre-Flight Diagnostic & Deployment Telemetry Gateway**  
> *Built for Adalat AI (Associate, CTO's Office Artifact)*  
> *Author:* **Allen Fletcher** (Integrated M.Tech AI & ML, VIT Bhopal)  
> *Standard:* ASD-STE100 Simplified Technical English & Whiteboard Defense Benchmark

[![Tests: 20 Passing](https://img.shields.io/badge/tests-20%20passing-brightgreen.svg)](tests/)
[![FastAPI](https://img.shields.io/badge/framework-FastAPI%200.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Pydantic v2](https://img.shields.io/badge/validation-Pydantic%20v2-e92063.svg?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![SQLite WAL](https://img.shields.io/badge/database-SQLite%20WAL-003B57.svg?logo=sqlite&logoColor=white)](https://sqlite.org)
[![Airtable Sync](https://img.shields.io/badge/integration-Airtable%20Live-18BFFF.svg?logo=airtable&logoColor=white)](https://airtable.com)
[![Slack Alerts](https://img.shields.io/badge/alerts-Slack%20Block%20Kit-4A154B.svg?logo=slack&logoColor=white)](https://slack.com)
[![Linear](https://img.shields.io/badge/issues-Linear%20P0%20GraphQL-5E6AD2.svg?logo=linear&logoColor=white)](https://linear.app)

---

## 1. Executive Summary & Operational Mission

Adalat AI operates across **11 partner states** and **6,000+ judges**, automating court proceedings with Indic speech-to-text (**Koyal ASR**). 

The primary engineering bottleneck in district and taluka courtrooms is **rural internet instability**. When courtroom network packet loss exceeds **2.0%** or network latency exceeds **300 ms**, live WebSocket streams drop audio frames. This causes transcription to halt, desynchronize, or hallucinate during live judicial hearings.

**`Adalat-Pulse` directly solves this operational problem:**
- Runs a deterministic **5-second pre-flight diagnostic** before a court session begins.
- Tests network quality (packet loss, latency, jitter, WebSocket RTT) and audio hardware (16 kHz sample rate, noise floor SNR).
- Issues an instant verdict: `OPTIMAL`, `DEGRADED`, or `CRITICAL`.
- Halts sessions before critical failures occur, routes P0 incidents directly to **Slack** and **Linear**, and synchronizes live health state with **Airtable partner bases**.

---

## 2. System Architecture

```text
[Courtroom Audio & Network Terminal]
               │
               ▼  1. 5-Second Hardware & Network Diagnostic Probe
[Adalat-Pulse Gateway (FastAPI / Uvicorn / WebSockets)]
               │
               ▼  2. Deterministic Quality Gate Evaluation (evaluator.py)
        ┌──────┴───────────────────────────────────────┐
        ▼ (OPTIMAL / DEGRADED)                         ▼ (CRITICAL BREACH)
[SQLite Store (WAL Mode)]                     [Automated Incident Router]
        │                                              ├─────────────────────────┐
        ▼                                              ▼                         ▼
[Airtable Partner Base Sync]                   [Slack Block Kit]         [Linear P0 Issue]
(Base: Adalat Telemetry)                       (#all-adalat-pulse-alerts) (Key: ALL)
        │                                              │                         │
        └──────────────────────┬───────────────────────┘                         │
                               ▼                                                 ▼
               [Operational Control Dashboard]                 [District Field Engineering Action]
               (Real-Time 11-State Fleet Grid)                 (Switch to 4G Backup Dongle)
```

---

## 3. Koyal Indic ASR Quality Gates

| Metric | Optimal Gate | Degraded Warning | Critical Breach | Root Cause & Operational Impact |
| :--- | :--- | :--- | :--- | :--- |
| **Packet Loss** | $\le 0.5\%$ | $0.51\% - 2.0\%$ | $> 2.0\%$ | WebSocket drops audio frames; Koyal ASR halts or hallucinates. |
| **Network Latency** | $\le 120\text{ ms}$ | $121 - 300\text{ ms}$ | $> 300\text{ ms}$ | Interactive transcript lag disrupts courtroom proceedings. |
| **Packet Jitter** | $\le 15\text{ ms}$ | $16 - 40\text{ ms}$ | $> 40\text{ ms}$ | Audio buffer underflow causes choppy phoneme input. |
| **WebSocket RTT** | $\le 150\text{ ms}$ | $151 - 350\text{ ms}$ | $> 350\text{ ms}$ | Heartbeat ping timeout; edge gateway disconnects. |
| **Mic Sample Rate**| $16\text{ kHz}$ or $48\text{ kHz}$ | Non-standard rate | $< 16\text{ kHz}$ | Acoustic models fail to extract phonetic features below 16 kHz. |
| **Ambient Noise (SNR)**| $\ge 20\text{ dB}$ | $12.0 - 19.9\text{ dB}$ | $< 12.0\text{ dB}$ | Ceiling fans and courtroom chatter drown out speech signals. |

---

## 4. Live Integrations (Zero Mocks / Zero Hardcoded Data)

* **Airtable Sync:** Directly connected to live partner base `Adalat Telemetry` (`appviUqZAQGGD2ILo`), mapping live courtroom status, latency, packet loss, and ASR readiness.
* **Slack Routing:** Automated Block Kit alerts delivered directly to `#all-adalat-pulse-alerts` with field operator remediation instructions.
* **Linear Issue Tracking:** Automated GraphQL mutations creating P0 issues in Linear under team `ALL` (`Allen Simeon Fletcher`).
* **Web Audio API Hardware Inspection:** Real browser-level audio sampling reading hardware sample rate and computing live room noise floor (SNR in dB).

---

## 5. Repository Structure

```text
adalat-pulse/
├── docs/
│   ├── ARCHITECTURE.md       # 1-page system diagram, component boundaries, and data flow
│   ├── DECISIONS.md          # Plain-language log of architecture choices and rejected options
│   ├── CONSTRAINTS.md        # Hard telemetry thresholds for Koyal ASR and safety rules
│   ├── FLOW.md               # Step-by-step lifecycle from pre-flight ping to alert dispatch
│   ├── THREAT.md             # Security review across 5 attackers and API integrity
│   ├── TESTING.md            # Commands, test coverage rules, and terminal receipts
│   └── HANDOVER.md           # Operational memory bank (Done, In-flight, Risks, Next steps)
├── src/
│   ├── __init__.py           # Package marker
│   ├── config.py             # App configuration, environment flags, and threshold defaults
│   ├── models.py             # Pydantic v2 schemas, type validations, and custom validators
│   ├── database.py           # SQLite WAL connection, table definitions, and CRUD queries
│   ├── evaluator.py          # Pure deterministic health evaluation engine
│   ├── alerts.py             # Slack Block Kit and Linear issue dispatchers
│   ├── airtable_sync.py      # Bi-directional partner base sync client
│   ├── main.py               # FastAPI application, route handlers, and static mounting
│   └── static/
│       ├── index.html        # High-contrast operational dashboard (Tailwind via CDN)
│       └── app.js            # Live telemetry polling, audio/network simulator, and visualizer
├── tests/
│   ├── __init__.py           # Test package marker
│   ├── conftest.py           # Reusable test fixtures and mock telemetry payloads
│   ├── test_models.py        # Pydantic v2 validation tests and boundary checks
│   ├── test_evaluator.py     # Deterministic evaluation logic and threshold edge cases
│   └── test_api.py           # End-to-end FastAPI endpoint integration tests
├── Dockerfile                # Multi-stage lightweight Python 3.11 container
├── docker-compose.yml        # Zero-config single-command local deployment
├── requirements.txt          # Production and test dependencies
└── README.md                 # Project manifesto, problem statement, and quickstart guide
```

---

## 6. Quickstart Guide

### Option A: Local Python Runtime
```powershell
# 1. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure credentials
cp .env.example .env
# Edit .env with your Airtable, Slack, and Linear credentials

# 4. Run automated test suite
pytest -v tests/

# 5. Launch the gateway server
uvicorn src.main:app --host 0.0.0.0 --port 8000
```
Visit the Operational Dashboard: **`http://localhost:8000`**

### Option B: Docker Compose (Instant Containerization)
```bash
docker compose up --build
```

---

## 7. Verification & Test Receipts

The system includes **20 comprehensive unit and integration tests** covering validation bounds, deterministic threshold evaluation, and API routes:

```text
tests/test_api.py::test_health_check_endpoint PASSED                     [  5%]
tests/test_api.py::test_submit_optimal_telemetry_report PASSED           [ 10%]
tests/test_api.py::test_submit_critical_telemetry_report PASSED          [ 15%]
tests/test_api.py::test_submit_invalid_payload_returns_422 PASSED        [ 20%]
tests/test_api.py::test_fleet_status_overview PASSED                     [ 25%]
tests/test_api.py::test_courtroom_history_not_found PASSED               [ 30%]
tests/test_api.py::test_incidents_feed PASSED                            [ 35%]
tests/test_evaluator.py::test_evaluator_optimal_verdict PASSED           [ 40%]
tests/test_evaluator.py::test_evaluator_degraded_verdict PASSED          [ 45%]
tests/test_evaluator.py::test_evaluator_critical_packet_loss PASSED      [ 50%]
tests/test_evaluator.py::test_evaluator_critical_audio_and_snr PASSED    [ 55%]
tests/test_evaluator.py::test_evaluator_critical_precedence_over_optimal PASSED [ 60%]
tests/test_evaluator.py::test_database_persistence_and_retrieval PASSED  [ 65%]
tests/test_models.py::test_valid_telemetry_request PASSED                [ 70%]
tests/test_models.py::test_courtroom_id_automatically_uppercased PASSED  [ 75%]
tests/test_models.py::test_negative_latency_rejected PASSED              [ 80%]
tests/test_models.py::test_packet_loss_bounds_enforced PASSED            [ 85%]
tests/test_models.py::test_invalid_state_code_rejected PASSED            [ 90%]
tests/test_models.py::test_zero_or_negative_mic_sample_rate_rejected PASSED [ 95%]
tests/test_models.py::test_blank_mic_device_name_fallback PASSED         [100%]

============================= 20 passed in 9.91s ==============================
```

---

## 8. Author & Role Target

* **Candidate:** Allen Fletcher
* **Background:** Integrated M.Tech in AI & ML, VIT Bhopal
* **Target Role:** Associate, CTO's Office at **Adalat AI**
* **Core Competencies Demonstrated:** Systems architecture, deterministic verification, API gateway design, incident routing, live partner data synchronization, and operational resilience.
