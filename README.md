# ⚡ Adalat-Pulse

> **Edge-ready Courtroom Pre-Flight Diagnostic & Deployment Telemetry Gateway**  
> *Built for Adalat AI (Associate, CTO's Office Artifact)*  
> *Author:* **Allen Fletcher** (Integrated M.Tech AI & ML, VIT Bhopal)  
> *Standard:* ASD-STE100 Simplified Technical English & Whiteboard Defense Benchmark

[![Tests: 30 Passing](https://img.shields.io/badge/tests-30%20passing-brightgreen.svg)](tests/)
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
               ▼  1. Level 2: Real Hardware & Network Diagnostic Probe (Web Audio FFT + WS Ping)
[Adalat-Pulse Gateway (FastAPI / Uvicorn / WebSockets)]
               │
               ▼  2. Level 4 & Level 3: Deterministic Quality Gate & Golden Exemplar Evaluation
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
               (Level 1 Outcome & Level 3 Interview)           (Switch to 4G Backup Dongle)
```

---

## 3. The 4-Tier Prompt Pyramid Architecture

Instead of writing brittle, instruction-heavy procedural checklists, `Adalat-Pulse` implements the **Prompt Pyramid** operational paradigm used by leading AI engineering teams:

```text
               ▲
              / \
             / L4\      LEVEL 4: What Good Looks Like (Golden Exemplars)
            /-----\     • Delhi HC Fiber Baseline (35ms, 0% loss, 28dB SNR)
           /   L3  \    • District Dual-ISP Baseline (70ms, 0.2% loss, 22dB SNR)
          /---------\   • Taluka Edge Baseline (110ms, 0.5% loss, 18dB SNR)
         /     L2    \
        /-------------\ LEVEL 3: The Interactive Interview
       /       L1      \• Dynamic dialogue resolving degraded edge telemetry
      /-----------------\• Direct operator remediation ("Ceiling fan turned off")
                         
                        LEVEL 2: Autonomous Edge Research
                        • 5-Second real-time FFT noise floor audit
                        • WebSocket burst probe measuring latency, jitter, loss

                        LEVEL 1: Goal First (The Outcome)
                        • "100% Zero-Word-Drop Koyal Indic ASR Guarantee"
```

1. **Level 1 (Goal First):** Anchor the system to the non-negotiable legal outcome: *"Guarantee uninterrupted, zero-word-drop Indic speech-to-text (Koyal ASR) for the duration of the court session"*.
2. **Level 2 (Autonomous Edge Research):** Survey the physical ground truth using real browser-level Web Audio API FFT analysis (noise floor SNR) and WebSocket burst ping/pong probes before taking any action.
3. **Level 3 (Interactive Interview):** Clarify ambiguities before sounding false alarms. When metrics fall into degraded bands, the gateway engages the courtroom technician with a targeted diagnostic interview (`Q-AUDIO-FAN`, `Q-NET-UPLINK`). Physical remediation (e.g. turning off a loud ceiling fan) dynamically applies an acoustic boost (+6 dB) and upgrades the verdict to `OPTIMAL` without canceling the hearing.
4. **Level 4 (Show What Good Looks Like):** Benchmark real telemetry against certified **Golden Baselines** (`GOLDEN-HC-FIBER`, `GOLDEN-DC-HYBRID`, `GOLDEN-TL-EDGE`). The engine computes a 0–100% Golden Alignment Score and live deltas against target benchmarks.

---

## 4. Koyal Indic ASR Quality Gates

| Metric | Optimal Gate | Degraded Warning | Critical Breach | Root Cause & Operational Impact |
| :--- | :--- | :--- | :--- | :--- |
| **Packet Loss** | $\le 0.5\%$ | $0.51\% - 2.0\%$ | $> 2.0\%$ | WebSocket drops audio frames; Koyal ASR halts or hallucinates. |
| **Network Latency** | $\le 120\text{ ms}$ | $121 - 300\text{ ms}$ | $> 300\text{ ms}$ | Interactive transcript lag disrupts courtroom proceedings. |
| **Packet Jitter** | $\le 15\text{ ms}$ | $16 - 40\text{ ms}$ | $> 40\text{ ms}$ | Audio buffer underflow causes choppy phoneme input. |
| **WebSocket RTT** | $\le 150\text{ ms}$ | $151 - 350\text{ ms}$ | $> 350\text{ ms}$ | Heartbeat ping timeout; edge gateway disconnects. |
| **Mic Sample Rate**| $16\text{ kHz}$ or $48\text{ kHz}$ | Non-standard rate | $< 16\text{ kHz}$ | Acoustic models fail to extract phonetic features below 16 kHz. |
| **Ambient Noise (SNR)**| $\ge 20\text{ dB}$ | $12.0 - 19.9\text{ dB}$ | $< 12.0\text{ dB}$ | Ceiling fans and courtroom chatter drown out speech signals. |

---

## 5. Live Integrations (Zero Mocks / Zero Hardcoded Data)

* **Airtable Sync:** Directly connected to live partner base `Adalat Telemetry` (`appviUqZAQGGD2ILo`), mapping live courtroom status, latency, packet loss, and ASR readiness.
* **Slack Routing:** Automated Block Kit alerts delivered directly to `#all-adalat-pulse-alerts` with field operator remediation instructions.
* **Linear Issue Tracking:** Automated GraphQL mutations creating P0 issues in Linear under team `ALL` (`Allen Simeon Fletcher`).
* **Web Audio API Hardware Inspection:** Real browser-level audio sampling reading hardware sample rate and computing live room noise floor (SNR in dB).

---

## 6. Repository Structure

```text
adalat-pulse/
├── docs/
│   ├── ARCHITECTURE.md       # 1-page system diagram, component boundaries, and data flow
│   ├── DECISIONS.md          # Plain-language log of architecture choices and rejected options (ADR-001 to ADR-005)
│   ├── CONSTRAINTS.md        # Hard telemetry thresholds for Koyal ASR and safety rules
│   ├── FLOW.md               # Step-by-step lifecycle from pre-flight ping to alert dispatch
│   ├── THREAT.md             # Security review across 5 attackers and API integrity
│   ├── TESTING.md            # Commands, test coverage rules, and terminal receipts
│   ├── HANDOVER.md           # Operational memory bank (Done, In-flight, Risks, Next steps)
│   └── PROMPT_PYRAMID.md     # 4-tier Prompt Pyramid architecture (Anthropic / Engineering Paradigm)
├── src/
│   ├── __init__.py           # Package marker
│   ├── config.py             # App configuration, environment flags, and threshold defaults
│   ├── models.py             # Pydantic v2 schemas, Golden Baselines, and Diagnostic Interview models
│   ├── database.py           # SQLite WAL connection, Golden Profiles seeds, and CRUD queries
│   ├── evaluator.py          # Deterministic health evaluation engine & Golden Alignment scoring
│   ├── alerts.py             # Slack Block Kit and Linear issue dispatchers
│   ├── airtable_sync.py      # Bi-directional partner base sync client
│   ├── main.py               # FastAPI application, Prompt Pyramid endpoints, and static mounting
│   └── static/
│       ├── index.html        # High-contrast operational dashboard (Tailwind via CDN)
│       └── app.js            # Live telemetry polling, audio FFT sampling, WS probe, and Interview Wizard
├── tests/
│   ├── __init__.py           # Test package marker
│   ├── conftest.py           # Reusable test fixtures and mock telemetry payloads
│   ├── test_models.py        # Pydantic v2 validation tests and boundary checks
│   ├── test_evaluator.py     # Deterministic evaluation logic and threshold edge cases
│   ├── test_golden_profiles.py # Golden Baseline retrieval, alignment scoring, and deltas
│   ├── test_interviews.py    # Diagnostic interview generation, dynamic remediation, and API flow
│   └── test_api.py           # End-to-end FastAPI endpoint integration tests
├── Dockerfile                # Multi-stage lightweight Python 3.11 container
├── docker-compose.yml        # Zero-config single-command local deployment
├── requirements.txt          # Production and test dependencies
└── README.md                 # Project manifesto, problem statement, and quickstart guide
```

---

## 7. Quickstart Guide

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

## 8. Verification & Test Receipts

The system includes **30 comprehensive unit and integration tests** covering validation bounds, deterministic threshold evaluation, Golden Baseline alignment, Diagnostic Interviews, and REST endpoints:

```text
============================= test session starts =============================
platform win32 -- Python 3.11.7, pytest-9.2.0, pluggy-1.7.0 -- C:\Users\admin\Documents\Adalat\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\admin\Documents\Adalat
plugins: anyio-4.16.0, asyncio-1.5.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 30 items

tests/test_api.py::test_health_check_endpoint PASSED                     [  3%]
tests/test_api.py::test_submit_optimal_telemetry_report PASSED           [  6%]
tests/test_api.py::test_submit_critical_telemetry_report PASSED          [ 10%]
tests/test_api.py::test_submit_invalid_payload_returns_422 PASSED        [ 13%]
tests/test_api.py::test_fleet_status_overview PASSED                     [ 16%]
tests/test_api.py::test_courtroom_history_not_found PASSED               [ 20%]
tests/test_api.py::test_incidents_feed PASSED                            [ 23%]
tests/test_evaluator.py::test_evaluator_optimal_verdict PASSED           [ 26%]
tests/test_evaluator.py::test_evaluator_degraded_verdict PASSED          [ 30%]
tests/test_evaluator.py::test_evaluator_critical_packet_loss PASSED      [ 33%]
tests/test_evaluator.py::test_evaluator_critical_audio_and_snr PASSED    [ 36%]
tests/test_evaluator.py::test_evaluator_critical_precedence_over_optimal PASSED [ 40%]
tests/test_evaluator.py::test_database_persistence_and_retrieval PASSED  [ 43%]
tests/test_golden_profiles.py::test_get_all_golden_profiles PASSED       [ 46%]
tests/test_golden_profiles.py::test_golden_alignment_optimal_high_score PASSED [ 50%]
tests/test_golden_profiles.py::test_golden_alignment_deltas PASSED       [ 53%]
tests/test_golden_profiles.py::test_golden_alignment_taluka_edge_profile PASSED [ 56%]
tests/test_golden_profiles.py::test_evaluator_embeds_golden_score PASSED [ 60%]
tests/test_interviews.py::test_ambient_noise_triggers_fan_question PASSED [ 63%]
tests/test_interviews.py::test_packet_loss_triggers_uplink_question PASSED [ 66%]
tests/test_interviews.py::test_critical_failure_bypasses_interview PASSED [ 70%]
tests/test_interviews.py::test_fan_turned_off_remediation_upgrades_verdict PASSED [ 73%]
tests/test_interviews.py::test_interview_api_flow PASSED                 [ 76%]
tests/test_models.py::test_valid_telemetry_request PASSED                [ 80%]
tests/test_models.py::test_courtroom_id_automatically_uppercased PASSED  [ 83%]
tests/test_models.py::test_negative_latency_rejected PASSED              [ 86%]
tests/test_models.py::test_packet_loss_bounds_enforced PASSED            [ 90%]
tests/test_models.py::test_invalid_state_code_rejected PASSED            [ 93%]
tests/test_models.py::test_zero_or_negative_mic_sample_rate_rejected PASSED [ 96%]
tests/test_models.py::test_blank_mic_device_name_fallback PASSED         [100%]

============================= 30 passed in 10.43s =============================
```

---

## 9. Author & Role Target

* **Candidate:** Allen Fletcher
* **Background:** Integrated M.Tech in AI & ML, VIT Bhopal
* **Target Role:** Associate, CTO's Office at **Adalat AI**
* **Core Competencies Demonstrated:** Systems architecture, deterministic verification, API gateway design, incident routing, live partner data synchronization, and operational resilience.
