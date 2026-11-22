"""Shared pytest fixtures for Adalat-Pulse testing suite."""

import pytest
import os
from pathlib import Path
from src.config import settings
from src.models import (
    TelemetryReportRequest,
    NetworkMetrics,
    HardwareMetrics,
    StateCode,
    Verdict,
)
from src.database import init_db, get_connection


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path: Path):
    """Sets up an isolated SQLite database for each test run."""
    test_db_path = tmp_path / "test_adalat_pulse.db"
    original_url = settings.DATABASE_URL
    settings.DATABASE_URL = f"sqlite:///{test_db_path}"

    init_db()
    yield
    settings.DATABASE_URL = original_url


@pytest.fixture
def optimal_report() -> TelemetryReportRequest:
    """Returns a courtroom report that passes all Koyal ASR quality gates."""
    return TelemetryReportRequest(
        courtroom_id="KL-HC-CRT01",
        state=StateCode.KL,
        bench_name="Ernakulam High Court Bench 01",
        network=NetworkMetrics(
            latency_ms=45.0,
            jitter_ms=6.0,
            packet_loss_pct=0.1,
            ws_rtt_ms=60.0
        ),
        hardware=HardwareMetrics(
            mic_sample_rate_hz=16000,
            snr_db=25.0,
            mic_device_name="Shure Boundary Mic MX393"
        ),
        app_version="1.0.0"
    )


@pytest.fixture
def degraded_report() -> TelemetryReportRequest:
    """Returns a courtroom report with sub-optimal metrics but within warning limits."""
    return TelemetryReportRequest(
        courtroom_id="KA-DC-BLR03",
        state=StateCode.KA,
        bench_name="Bengaluru City Civil Court Hall 3",
        network=NetworkMetrics(
            latency_ms=180.0,  # > 120ms (degraded)
            jitter_ms=22.0,   # > 15ms (degraded)
            packet_loss_pct=1.1,  # > 0.5% (degraded)
            ws_rtt_ms=210.0   # > 150ms (degraded)
        ),
        hardware=HardwareMetrics(
            mic_sample_rate_hz=44100,  # Non-standard (degraded)
            snr_db=16.5,  # < 20 dB (degraded)
            mic_device_name="USB Tabletop Microphone"
        ),
        app_version="1.0.0"
    )


@pytest.fixture
def critical_packet_loss_report() -> TelemetryReportRequest:
    """Returns a courtroom report with severe packet loss breaching the 2.0% limit."""
    return TelemetryReportRequest(
        courtroom_id="RJ-DC-JPR02",
        state=StateCode.RJ,
        bench_name="Jaipur District & Sessions Court 02",
        network=NetworkMetrics(
            latency_ms=90.0,
            jitter_ms=10.0,
            packet_loss_pct=3.8,  # > 2.0% (CRITICAL)
            ws_rtt_ms=110.0
        ),
        hardware=HardwareMetrics(
            mic_sample_rate_hz=16000,
            snr_db=22.0,
            mic_device_name="Court Digital Pod"
        ),
        app_version="1.0.0"
    )


@pytest.fixture
def critical_audio_report() -> TelemetryReportRequest:
    """Returns a courtroom report with sub-16kHz sample rate and heavy background noise."""
    return TelemetryReportRequest(
        courtroom_id="UP-DC-LKO05",
        state=StateCode.UP,
        bench_name="Lucknow District Court Hall 05",
        network=NetworkMetrics(
            latency_ms=80.0,
            jitter_ms=8.0,
            packet_loss_pct=0.2,
            ws_rtt_ms=95.0
        ),
        hardware=HardwareMetrics(
            mic_sample_rate_hz=8000,  # < 16000 Hz (CRITICAL)
            snr_db=8.5,  # < 12.0 dB (CRITICAL)
            mic_device_name="Legacy Analogue PA Line-in"
        ),
        app_version="1.0.0"
    )
