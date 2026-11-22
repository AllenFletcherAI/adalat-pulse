# DATA & INCIDENT FLOW: ADALAT-PULSE
**Standard:** ASD-STE100 Simplified Technical English  
**System:** Adalat-Pulse  

---

## 1. End-to-End Request & Incident Lifecycle

```text
[Courtroom Audio & Network Terminal]
               │
               ▼ 1. User clicks "Run 5-Second Pre-Flight Check"
[Browser Client: Web Audio API & WebSocket /ws/probe]
               │
               ▼ 2. Measures Hardware (16/48 kHz, Noise SNR) & Network (RTT, Loss, Jitter)
[POST /api/v1/telemetry/report (FastAPI)]
               │
               ▼ 3. Pydantic v2 Schema Validation (Rejects invalid states / numbers)
[Deterministic Health Evaluator (src/evaluator.py)]
               │
               ├───────────────────────────────────────────────┐
               ▼ (Verdict: OPTIMAL or DEGRADED)                ▼ (Verdict: CRITICAL)
[4a. Store Snapshot to SQLite (WAL)]            [4b. Generate Incident ID (INC-STATE-ID-TS)]
               │                                               │
               ├───────────────────────────────┐               ├───────────────────────────────┐
               ▼                               ▼               ▼                               ▼
[5a. Live Sync to Airtable]     [6a. Update Ops Dashboard] [5b. Dispatch Slack Alert]   [5c. Create Linear P0 Issue]
(Base: appviUqZAQGGD2ILo)       (Fleet health % & state grid) (#all-adalat-pulse-alerts) (Team Key: ALL)
                                                               │                               │
                                                               └───────────────┬───────────────┘
                                                                               ▼
                                                                [6b. Store Incident in SQLite]
                                                                (Status logged with receipts)
```

---

## 2. Step-by-Step Execution Sequence

1. **Pre-Flight Initiation:** A courtroom technical assistant opens the Adalat-Pulse console before the bench sits.
2. **5-Second Probe:**
   - Web Audio API checks the active audio device sample rate and computes ambient noise floor SNR.
   - WebSocket `/ws/probe` transmits 20 timestamped frames to measure real network latency, jitter, and packet drop.
3. **Payload Submission:** Client constructs a JSON payload conforming to `TelemetryReportRequest` and posts to `/api/v1/telemetry/report`.
4. **Validation & Evaluation:**
   - FastAPI validates types and boundaries via Pydantic v2.
   - `evaluator.py` compares all 6 parameters against Koyal ASR quality gates.
5. **Persistence:**
   - Snapshot is stored in SQLite table `telemetry_snapshots` with row ID.
6. **Incident Dispatch (If Critical):**
   - Incident ID generated (`INC-<state>-<courtroom_id>-<timestamp>`).
   - Asynchronous HTTP request dispatches Slack Block Kit notification with field remediation steps to `#all-adalat-pulse-alerts`.
   - GraphQL mutation creates an Urgent (P0) issue in Linear under the designated team.
   - Incident record saved in SQLite table `incidents`.
7. **Partner Base Synchronization:**
   - Courtroom status is upserted into Airtable base `appviUqZAQGGD2ILo` (`Courtroom Telemetry` table).
8. **Dashboard Real-Time Refresh:**
   - Browser polling picks up new status and reflects live regional health across the 11 partner states.
