"""Unit tests for deterministic health evaluation and SQLite persistence."""

import pytest
from src.evaluator import evaluate_telemetry
from src.models import (
    TelemetryReportRequest,
    NetworkMetrics,
    HardwareMetrics,
    Verdict,
    StateCode,
)
from src.database import (
    save_telemetry_snapshot,
    get_latest_courtrooms,
    get_courtroom_history,
)


def test_evaluator_optimal_verdict(optimal_report: TelemetryReportRequest):
    """Verifies that optimal metrics produce an OPTIMAL verdict allowing session start."""
    result = evaluate_telemetry(optimal_report)
    assert result.verdict == Verdict.OPTIMAL
    assert result.can_start_session is True
    assert any("ALL_SYSTEMS_OPTIMAL" in code for code in result.reason_codes)


def test_evaluator_degraded_verdict(degraded_report: TelemetryReportRequest):
    """Verifies that sub-optimal metrics produce a DEGRADED verdict with warning codes."""
    result = evaluate_telemetry(degraded_report)
    assert result.verdict == Verdict.DEGRADED
    assert result.can_start_session is True
    assert any("ELEVATED_PACKET_LOSS" in code for code in result.reason_codes)
    assert any("ELEVATED_LATENCY" in code for code in result.reason_codes)
    assert any("NON_STANDARD_SAMPLE_RATE" in code for code in result.reason_codes)


def test_evaluator_critical_packet_loss(critical_packet_loss_report: TelemetryReportRequest):
    """Verifies that packet loss > 2.0% halts the session with a CRITICAL verdict."""
    result = evaluate_telemetry(critical_packet_loss_report)
    assert result.verdict == Verdict.CRITICAL
    assert result.can_start_session is False
    assert any("HIGH_PACKET_LOSS" in code for code in result.reason_codes)


def test_evaluator_critical_audio_and_snr(critical_audio_report: TelemetryReportRequest):
    """Verifies that low sample rate and excessive room noise trigger CRITICAL."""
    result = evaluate_telemetry(critical_audio_report)
    assert result.verdict == Verdict.CRITICAL
    assert result.can_start_session is False
    assert any("INSUFFICIENT_SAMPLE_RATE" in code for code in result.reason_codes)
    assert any("EXCESSIVE_AMBIENT_NOISE" in code for code in result.reason_codes)


def test_evaluator_critical_precedence_over_optimal():
    """Verifies that even if 5 metrics are optimal, a single critical latency breaches the gate."""
    mixed_report = TelemetryReportRequest(
        courtroom_id="DL-HC-CRT09",
        state=StateCode.DL,
        bench_name="Delhi High Court Bench 09",
        network=NetworkMetrics(
            latency_ms=450.0,  # CRITICAL (> 300 ms)
            jitter_ms=2.0,     # Optimal
            packet_loss_pct=0.0,  # Optimal
            ws_rtt_ms=40.0     # Optimal
        ),
        hardware=HardwareMetrics(
            mic_sample_rate_hz=48000,  # Optimal
            snr_db=32.0,  # Optimal
            mic_device_name="Broadcast Mic"
        )
    )
    result = evaluate_telemetry(mixed_report)
    assert result.verdict == Verdict.CRITICAL
    assert result.can_start_session is False
    assert any("HIGH_LATENCY" in code for code in result.reason_codes)


def test_database_persistence_and_retrieval(optimal_report: TelemetryReportRequest):
    """Verifies that telemetry snapshots are persisted and queryable from SQLite."""
    eval_result = evaluate_telemetry(optimal_report)
    snapshot_id = save_telemetry_snapshot(optimal_report, eval_result)
    assert snapshot_id > 0

    latest = get_latest_courtrooms()
    assert len(latest) >= 1
    courtroom = next(c for c in latest if c["courtroom_id"] == "KL-HC-CRT01")
    assert courtroom["verdict"] == "OPTIMAL"
    assert courtroom["state"] == "KL"
    assert courtroom["can_start_session"] == 1

    history = get_courtroom_history("KL-HC-CRT01")
    assert len(history) >= 1
    assert history[0]["courtroom_id"] == "KL-HC-CRT01"
