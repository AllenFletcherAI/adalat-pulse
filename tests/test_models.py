"""Validation tests for Pydantic v2 schemas in Adalat-Pulse."""

import pytest
from pydantic import ValidationError
from src.models import (
    TelemetryReportRequest,
    NetworkMetrics,
    HardwareMetrics,
    StateCode,
    Verdict,
)


def test_valid_telemetry_request(optimal_report: TelemetryReportRequest):
    """Verifies that an optimal report satisfies all validation constraints."""
    assert optimal_report.courtroom_id == "KL-HC-CRT01"
    assert optimal_report.state == StateCode.KL
    assert optimal_report.network.packet_loss_pct == 0.1
    assert optimal_report.hardware.mic_sample_rate_hz == 16000


def test_courtroom_id_automatically_uppercased():
    """Verifies that lowercase courtroom IDs are normalized to uppercase."""
    report = TelemetryReportRequest(
        courtroom_id="dl-hc-crt04",
        state=StateCode.DL,
        bench_name="Delhi High Court Bench 04",
        network=NetworkMetrics(latency_ms=20.0, jitter_ms=2.0, packet_loss_pct=0.0, ws_rtt_ms=30.0),
        hardware=HardwareMetrics(mic_sample_rate_hz=48000, snr_db=30.0, mic_device_name="Conference Mic")
    )
    assert report.courtroom_id == "DL-HC-CRT04"


def test_negative_latency_rejected():
    """Verifies that negative network latency is strictly rejected."""
    with pytest.raises(ValidationError) as exc:
        NetworkMetrics(latency_ms=-10.0, jitter_ms=5.0, packet_loss_pct=0.0, ws_rtt_ms=50.0)
    assert "latency_ms" in str(exc.value)


def test_packet_loss_bounds_enforced():
    """Verifies that packet loss > 100% or < 0% is strictly rejected."""
    with pytest.raises(ValidationError) as exc_high:
        NetworkMetrics(latency_ms=50.0, jitter_ms=5.0, packet_loss_pct=105.0, ws_rtt_ms=50.0)
    assert "packet_loss_pct" in str(exc_high.value)

    with pytest.raises(ValidationError) as exc_low:
        NetworkMetrics(latency_ms=50.0, jitter_ms=5.0, packet_loss_pct=-1.0, ws_rtt_ms=50.0)
    assert "packet_loss_pct" in str(exc_low.value)


def test_invalid_state_code_rejected():
    """Verifies that unregistered state codes are rejected by the StateCode enum."""
    with pytest.raises(ValidationError) as exc:
        TelemetryReportRequest(
            courtroom_id="XX-HC-CRT01",
            state="XX",  # Invalid state
            bench_name="Unknown Bench",
            network=NetworkMetrics(latency_ms=50.0, jitter_ms=5.0, packet_loss_pct=0.0, ws_rtt_ms=50.0),
            hardware=HardwareMetrics(mic_sample_rate_hz=16000, snr_db=20.0, mic_device_name="Mic")
        )
    assert "state" in str(exc.value)


def test_zero_or_negative_mic_sample_rate_rejected():
    """Verifies that sample rate <= 0 Hz is rejected."""
    with pytest.raises(ValidationError) as exc:
        HardwareMetrics(mic_sample_rate_hz=0, snr_db=20.0, mic_device_name="USB Mic")
    assert "mic_sample_rate_hz" in str(exc.value)


def test_blank_mic_device_name_fallback():
    """Verifies that empty whitespace mic device name falls back to default."""
    hw = HardwareMetrics(mic_sample_rate_hz=16000, snr_db=20.0, mic_device_name="   ")
    assert hw.mic_device_name == "Unknown Audio Device"
