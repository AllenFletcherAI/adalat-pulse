"""Deterministic health evaluation engine for Adalat-Pulse."""

from typing import List, Dict, Any
from src.config import settings
from src.models import (
    TelemetryReportRequest,
    EvaluationResult,
    Verdict,
)


def evaluate_telemetry(report: TelemetryReportRequest) -> EvaluationResult:
    """Evaluates courtroom pre-flight telemetry against strict Koyal ASR benchmarks.

    Returns deterministic verdict: OPTIMAL, DEGRADED, or CRITICAL.
    """
    net = report.network
    hw = report.hardware

    critical_reasons: List[str] = []
    degraded_reasons: List[str] = []

    # 1. Packet Loss Check (Koyal ASR drops audio frames over WebSocket)
    if net.packet_loss_pct > settings.PACKET_LOSS_CRITICAL_PCT:
        critical_reasons.append(
            f"HIGH_PACKET_LOSS: Packet loss of {net.packet_loss_pct:.1f}% exceeds critical limit of "
            f"{settings.PACKET_LOSS_CRITICAL_PCT:.1f}%. Koyal ASR WebSocket drops live Indic speech frames."
        )
    elif net.packet_loss_pct > settings.PACKET_LOSS_DEGRADED_PCT:
        degraded_reasons.append(
            f"ELEVATED_PACKET_LOSS: Packet loss of {net.packet_loss_pct:.1f}% exceeds optimal limit of "
            f"{settings.PACKET_LOSS_DEGRADED_PCT:.1f}%. Mild transcription stutter expected."
        )

    # 2. Network Latency Check (Sub-second live courtroom transcription)
    if net.latency_ms > settings.LATENCY_CRITICAL_MS:
        critical_reasons.append(
            f"HIGH_LATENCY: Network latency of {net.latency_ms:.0f} ms exceeds critical limit of "
            f"{settings.LATENCY_CRITICAL_MS:.0f} ms. Real-time transcription lag disrupts courtroom stenographer."
        )
    elif net.latency_ms > settings.LATENCY_DEGRADED_MS:
        degraded_reasons.append(
            f"ELEVATED_LATENCY: Network latency of {net.latency_ms:.0f} ms exceeds optimal limit of "
            f"{settings.LATENCY_DEGRADED_MS:.0f} ms."
        )

    # 3. Packet Jitter Check (Audio buffer underflow risk)
    if net.jitter_ms > settings.JITTER_CRITICAL_MS:
        critical_reasons.append(
            f"HIGH_JITTER: Packet jitter of {net.jitter_ms:.1f} ms exceeds critical limit of "
            f"{settings.JITTER_CRITICAL_MS:.0f} ms. Causes audio buffer underflows."
        )
    elif net.jitter_ms > settings.JITTER_DEGRADED_MS:
        degraded_reasons.append(
            f"ELEVATED_JITTER: Packet jitter of {net.jitter_ms:.1f} ms exceeds optimal limit of "
            f"{settings.JITTER_DEGRADED_MS:.0f} ms."
        )

    # 4. WebSocket Keepalive Round-Trip Time Check
    if net.ws_rtt_ms > settings.WS_RTT_CRITICAL_MS:
        critical_reasons.append(
            f"WS_HEARTBEAT_TIMEOUT_RISK: WebSocket keepalive RTT of {net.ws_rtt_ms:.0f} ms exceeds critical limit of "
            f"{settings.WS_RTT_CRITICAL_MS:.0f} ms. Connection drops imminent."
        )
    elif net.ws_rtt_ms > settings.WS_RTT_DEGRADED_MS:
        degraded_reasons.append(
            f"WS_HEARTBEAT_LATENCY: WebSocket keepalive RTT of {net.ws_rtt_ms:.0f} ms exceeds optimal limit of "
            f"{settings.WS_RTT_DEGRADED_MS:.0f} ms."
        )

    # 5. Microphone Hardware Sample Rate (Acoustic model requires >= 16 kHz)
    if hw.mic_sample_rate_hz < settings.MIN_MIC_SAMPLE_RATE_HZ:
        critical_reasons.append(
            f"INSUFFICIENT_SAMPLE_RATE: Microphone hardware sample rate of {hw.mic_sample_rate_hz} Hz is below "
            f"the required {settings.MIN_MIC_SAMPLE_RATE_HZ} Hz. Koyal Indic acoustic models cannot parse sub-16kHz audio."
        )
    elif hw.mic_sample_rate_hz not in (16000, 48000):
        degraded_reasons.append(
            f"NON_STANDARD_SAMPLE_RATE: Microphone sample rate of {hw.mic_sample_rate_hz} Hz requires client CPU resampling."
        )

    # 6. Audio Signal-to-Noise Ratio (Rural courtroom background noise floor)
    if hw.snr_db < settings.SNR_CRITICAL_DB:
        critical_reasons.append(
            f"EXCESSIVE_AMBIENT_NOISE: Audio SNR of {hw.snr_db:.1f} dB is below critical floor of "
            f"{settings.SNR_CRITICAL_DB:.1f} dB. Background noise (ceiling fans/crowd) masks speech signal."
        )
    elif hw.snr_db < settings.SNR_DEGRADED_DB:
        degraded_reasons.append(
            f"ELEVATED_AMBIENT_NOISE: Audio SNR of {hw.snr_db:.1f} dB is below optimal floor of "
            f"{settings.SNR_DEGRADED_DB:.1f} dB. Acoustic gain boost recommended."
        )

    # Composite Verdict Determination
    metrics_summary: Dict[str, Any] = {
        "packet_loss_pct": net.packet_loss_pct,
        "latency_ms": net.latency_ms,
        "jitter_ms": net.jitter_ms,
        "ws_rtt_ms": net.ws_rtt_ms,
        "mic_sample_rate_hz": hw.mic_sample_rate_hz,
        "snr_db": hw.snr_db,
        "mic_device_name": hw.mic_device_name,
    }

    if critical_reasons:
        return EvaluationResult(
            verdict=Verdict.CRITICAL,
            can_start_session=False,
            reason_codes=critical_reasons,
            summary="PRE-FLIGHT FAILED: Critical network or hardware faults detected. Court session cannot begin safely.",
            metrics=metrics_summary,
        )

    if degraded_reasons:
        return EvaluationResult(
            verdict=Verdict.DEGRADED,
            can_start_session=True,
            reason_codes=degraded_reasons,
            summary="PRE-FLIGHT WARNING: Sub-optimal telemetry detected. Court session may proceed with active monitoring.",
            metrics=metrics_summary,
        )

    return EvaluationResult(
        verdict=Verdict.OPTIMAL,
        can_start_session=True,
        reason_codes=["ALL_SYSTEMS_OPTIMAL: Telemetry clears all Koyal ASR quality gates."],
        summary="PRE-FLIGHT PASSED: Courtroom network and audio hardware meet optimal live transcription benchmarks.",
        metrics=metrics_summary,
    )
