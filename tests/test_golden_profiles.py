"""Unit tests for Level 4 Golden Standard baseline profiles and alignment scoring."""

import pytest
from src.models import (
    TelemetryReportRequest,
    NetworkMetrics,
    HardwareMetrics,
    StateCode,
)
from src.evaluator import calculate_golden_alignment, evaluate_telemetry
from src.database import get_golden_profiles, get_golden_profile


def test_get_all_golden_profiles():
    """Verifies that all 3 certified golden standard baselines are loaded in SQLite."""
    profiles = get_golden_profiles()
    assert len(profiles) >= 3
    ids = [p["profile_id"] for p in profiles]
    assert "GOLDEN-HC-FIBER" in ids
    assert "GOLDEN-DC-HYBRID" in ids
    assert "GOLDEN-TL-EDGE" in ids


def test_golden_alignment_optimal_high_score(optimal_report: TelemetryReportRequest):
    """Verifies that optimal telemetry scores near 100% against High Court Fiber baseline."""
    score = calculate_golden_alignment(optimal_report, "GOLDEN-HC-FIBER")
    assert score.profile_id == "GOLDEN-HC-FIBER"
    assert score.alignment_pct >= 90.0
    assert "EXEMPLARY" in score.summary


def test_golden_alignment_deltas():
    """Verifies that latency, packet loss, and SNR deltas are computed accurately."""
    custom_report = TelemetryReportRequest(
        courtroom_id="KA-DC-BLR01",
        state=StateCode.KA,
        bench_name="Bengaluru City Civil Bench 01",
        network=NetworkMetrics(latency_ms=55.0, jitter_ms=6.0, packet_loss_pct=0.4, ws_rtt_ms=65.0),
        hardware=HardwareMetrics(mic_sample_rate_hz=16000, snr_db=24.0, mic_device_name="Array Mic"),
        golden_profile_id="GOLDEN-HC-FIBER"
    )
    score = calculate_golden_alignment(custom_report, "GOLDEN-HC-FIBER")
    # Target latency: 35.0, measured: 55.0 -> delta = +20.0
    assert score.latency_delta_ms == 20.0
    # Target loss: 0.0, measured: 0.4 -> delta = +0.4
    assert score.packet_loss_delta_pct == 0.4
    # Target SNR: 28.0, measured: 24.0 -> delta = -4.0
    assert score.snr_delta_db == -4.0


def test_golden_alignment_taluka_edge_profile():
    """Verifies scoring against Rural Taluka edge 4G baseline."""
    taluka_report = TelemetryReportRequest(
        courtroom_id="RJ-TL-KTA01",
        state=StateCode.RJ,
        bench_name="Kota Taluka Sub-Division Court 01",
        network=NetworkMetrics(latency_ms=105.0, jitter_ms=12.0, packet_loss_pct=0.45, ws_rtt_ms=115.0),
        hardware=HardwareMetrics(mic_sample_rate_hz=16000, snr_db=19.5, mic_device_name="Noise-Canceling Mic"),
        golden_profile_id="GOLDEN-TL-EDGE"
    )
    score = calculate_golden_alignment(taluka_report, "GOLDEN-TL-EDGE")
    assert score.profile_id == "GOLDEN-TL-EDGE"
    # Target: 110ms, measured: 105ms -> latency delta is negative (better than target)
    assert score.latency_delta_ms <= 0.0
    assert score.alignment_pct >= 90.0


def test_evaluator_embeds_golden_score(optimal_report: TelemetryReportRequest):
    """Verifies that the evaluator includes golden alignment in EvaluationResult."""
    result = evaluate_telemetry(optimal_report)
    assert result.golden_alignment is not None
    assert result.golden_alignment.profile_id == "GOLDEN-HC-FIBER"
    assert result.metrics["golden_alignment_pct"] == result.golden_alignment.alignment_pct
