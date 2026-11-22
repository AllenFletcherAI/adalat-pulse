"""Unit tests for Level 3 Operator Interview dialogue and remediation workflows."""

import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.models import (
    TelemetryReportRequest,
    NetworkMetrics,
    HardwareMetrics,
    StateCode,
    Verdict,
    InterviewResponseRequest,
)
from src.evaluator import generate_interview_questions, evaluate_telemetry
from src.database import get_courtroom_interviews


def test_ambient_noise_triggers_fan_question():
    """Verifies that ambient noise between 12-20 dB triggers ceiling fan interview question."""
    noisy_report = TelemetryReportRequest(
        courtroom_id="UP-DC-LKO01",
        state=StateCode.UP,
        bench_name="Lucknow District Court Hall 01",
        network=NetworkMetrics(latency_ms=45.0, jitter_ms=5.0, packet_loss_pct=0.1, ws_rtt_ms=50.0),
        hardware=HardwareMetrics(mic_sample_rate_hz=16000, snr_db=15.5, mic_device_name="PA Mic")
    )
    questions = generate_interview_questions(noisy_report)
    assert len(questions) >= 1
    assert any(q.question_id == "Q-AUDIO-FAN" for q in questions)
    fan_q = next(q for q in questions if q.question_id == "Q-AUDIO-FAN")
    assert "ceiling fan" in fan_q.prompt.lower()


def test_packet_loss_triggers_uplink_question():
    """Verifies that packet loss between 0.5-2.0% triggers network uplink question."""
    lossy_report = TelemetryReportRequest(
        courtroom_id="MP-DC-BPL02",
        state=StateCode.MP,
        bench_name="Bhopal Civil Bench 02",
        network=NetworkMetrics(latency_ms=60.0, jitter_ms=8.0, packet_loss_pct=1.4, ws_rtt_ms=75.0),
        hardware=HardwareMetrics(mic_sample_rate_hz=16000, snr_db=25.0, mic_device_name="Mic Array")
    )
    questions = generate_interview_questions(lossy_report)
    assert len(questions) >= 1
    assert any(q.question_id == "Q-NET-UPLINK" for q in questions)


def test_critical_failure_bypasses_interview():
    """Verifies that critical failures halt immediately without prompting operator interview."""
    critical_report = TelemetryReportRequest(
        courtroom_id="DL-HC-CRT05",
        state=StateCode.DL,
        bench_name="Delhi High Court Bench 05",
        network=NetworkMetrics(latency_ms=500.0, jitter_ms=50.0, packet_loss_pct=5.0, ws_rtt_ms=600.0),
        hardware=HardwareMetrics(mic_sample_rate_hz=8000, snr_db=6.0, mic_device_name="Defective Mic")
    )
    eval_result = evaluate_telemetry(critical_report)
    assert eval_result.verdict == Verdict.CRITICAL
    assert len(eval_result.pending_questions) == 0


def test_fan_turned_off_remediation_upgrades_verdict():
    """Verifies that confirming ceiling fan turned off applies +6 dB SNR and clears the verdict."""
    borderline_report = TelemetryReportRequest(
        courtroom_id="TN-DC-CHE04",
        state=StateCode.TN,
        bench_name="Chennai City Civil Court Hall 04",
        network=NetworkMetrics(latency_ms=45.0, jitter_ms=4.0, packet_loss_pct=0.1, ws_rtt_ms=50.0),
        hardware=HardwareMetrics(mic_sample_rate_hz=16000, snr_db=17.0, mic_device_name="Desk Mic")
    )
    # Before interview: DEGRADED (SNR 17.0 < 20.0 dB)
    initial_eval = evaluate_telemetry(borderline_report)
    assert initial_eval.verdict == Verdict.DEGRADED

    # Technician applies remediation
    borderline_report.interview_responses = {
        "Q-AUDIO-FAN": "Ceiling Fan Turned Off (Remediation Applied)"
    }
    remediated_eval = evaluate_telemetry(borderline_report)
    assert remediated_eval.verdict == Verdict.OPTIMAL
    assert any("REMEDIATION_CONFIRMED" in r for r in remediated_eval.reason_codes)


@pytest.mark.asyncio
async def test_interview_api_flow(degraded_report: TelemetryReportRequest):
    """Verifies that POST /api/v1/telemetry/interview re-evaluates and logs to database."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        interview_payload = {
            "courtroom_id": degraded_report.courtroom_id,
            "question_id": "Q-AUDIO-FAN",
            "selected_option": "Ceiling Fan Turned Off (Remediation Applied)",
            "remediation_applied": True,
            "original_report": degraded_report.model_dump(mode="json")
        }
        res = await client.post("/api/v1/telemetry/interview", json=interview_payload)
        assert res.status_code == 200
        data = res.json()
        assert data["courtroom_id"] == "KA-DC-BLR03"
        assert data["snapshot_id"] > 0

        # Verify interaction logged in SQLite
        interviews = get_courtroom_interviews("KA-DC-BLR03")
        assert len(interviews) >= 1
        assert interviews[0]["question_id"] == "Q-AUDIO-FAN"
        assert interviews[0]["remediation_applied"] == 1
