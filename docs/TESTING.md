# TEST EXECUTION & VERIFICATION PROOF: ADALAT-PULSE
**Standard:** ASD-STE100 Simplified Technical English  
**System:** Adalat-Pulse  

---

## 1. Test Suite Architecture

The test suite contains **30 deterministic unit and integration tests** verifying data contracts, threshold boundaries, persistence, Golden Profiles, Operator Interviews, and REST endpoints:

- `tests/test_models.py` (7 tests): Validates Pydantic v2 schemas, field boundaries, bounds checks, and enum rejections.
- `tests/test_evaluator.py` (6 tests): Validates deterministic evaluation against Koyal ASR quality gates, critical precedence, and SQLite storage.
- `tests/test_golden_profiles.py` (5 tests): Validates Golden Baseline retrieval, 0–100% alignment scoring, deltas against targets, and evaluator embedding.
- `tests/test_interviews.py` (5 tests): Validates diagnostic interview generation, audio fan and network uplink questions, critical bypass, remediation upgrades (+6 dB), and the `/telemetry/interview` API flow.
- `tests/test_api.py` (7 tests): Validates FastAPI endpoints (`/health`, `/telemetry/report`, `/courtrooms/status`, `/history`, `/incidents`).

---

## 2. Test Execution Command

To execute the complete test suite locally:

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run pytest with full verbosity
pytest -v tests/
```

---

## 3. Real Terminal Receipt (30/30 Passing)

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

## 4. Live Service Receipts

### 1. Airtable Synchronization Receipt
- **Base ID:** `appviUqZAQGGD2ILo`
- **Table:** `Courtroom Telemetry`
- **Response:** `HTTP 200 OK` (Records synced and queried).

### 2. Slack Webhook Alert Receipt
- **Target Channel:** `#all-adalat-pulse-alerts`
- **Response:** `HTTP 200 OK` (`ok`).
- **Payload:** Slack Block Kit notification with field remediation advice.

### 3. Linear GraphQL Integration Receipt
- **Account:** Allen Fletcher (`allensimeonfletcher@gmail.com`)
- **Team:** `Allen Simeon Fletcher` (Key: `ALL`, Team ID: `3ca0f0c3-4c83-4471-8be5-36dc2c0f71ca`)
- **Response:** `HTTP 200 OK` (Viewer & Team verified).
