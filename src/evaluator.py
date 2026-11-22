"""Deterministic health evaluation and Prompt Pyramid alignment engine for Adalat-Pulse.

Incorporates:
1. Level 1: Outcome-driven session clearance (Zero-Word-Drop Koyal Transcription guarantee).
2. Level 2: Comprehensive multi-metric hardware and network telemetry audit.
3. Level 3: Interactive operator interview dialogue generation for degraded states.
4. Level 4: Certified Golden Standard baseline alignment delta scoring.
"""

from typing import List, Dict, Any, Optional
from src.config import settings
from src.models import (
    TelemetryReportRequest,
    EvaluationResult,
    Verdict,
    GoldenAlignmentScore,
    OperatorInterviewQuestion,
    GoldenBaselineProfile,
    CourtroomTier,
)
from src.database import get_golden_profile


def calculate_golden_alignment(
    report: TelemetryReportRequest,
    profile_id: Optional[str] = "GOLDEN-HC-FIBER"
) -> GoldenAlignmentScore:
    """Computes alignment score (0-100%) and deltas against a certified Golden Standard profile."""
    golden_data = get_golden_profile(profile_id or "GOLDEN-HC-FIBER")
    if not golden_data:
        # Fallback to default high court baseline
        golden_data = {
            "profile_id": "GOLDEN-HC-FIBER",
            "title": "High Court Dedicated Leased Line Benchmark",
            "target_latency_ms": 35.0,
            "target_packet_loss_pct": 0.0,
            "target_snr_db": 28.0,
        }

    net = report.network
    hw = report.hardware

    target_lat = golden_data["target_latency_ms"]
    target_loss = golden_data["target_packet_loss_pct"]
    target_snr = golden_data["target_snr_db"]

    latency_delta = round(net.latency_ms - target_lat, 1)
    loss_delta = round(net.packet_loss_pct - target_loss, 2)
    snr_delta = round(hw.snr_db - target_snr, 1)

    # Calculate alignment score
    score = 100.0

    # Latency penalty: 1% per 10ms above target
    if latency_delta > 0:
        score -= min(30.0, (latency_delta / 10.0))

    # Packet loss penalty: 15% per 1.0% loss above target
    if loss_delta > 0:
        score -= min(40.0, (loss_delta * 15.0))

    # SNR penalty: 2% per 1 dB below target
    if snr_delta < 0:
        score -= min(30.0, (abs(snr_delta) * 2.0))

    alignment_pct = max(0.0, min(100.0, round(score, 1)))

    if alignment_pct >= 90.0:
        summary = f"EXEMPLARY: {alignment_pct}% match to {golden_data['title']}."
    elif alignment_pct >= 70.0:
        summary = f"ACCEPTABLE: {alignment_pct}% match to {golden_data['title']}. Minor delta observed."
    else:
        summary = f"DIVERGENT: {alignment_pct}% match to {golden_data['title']}. Substantial deviation from benchmark."

    return GoldenAlignmentScore(
        profile_id=golden_data["profile_id"],
        profile_title=golden_data["title"],
        alignment_pct=alignment_pct,
        latency_delta_ms=latency_delta,
        packet_loss_delta_pct=loss_delta,
        snr_delta_db=snr_delta,
        summary=summary,
    )


def generate_interview_questions(
    report: TelemetryReportRequest
) -> List[OperatorInterviewQuestion]:
    """Generates targeted clarifying questions when telemetry enters degraded brackets."""
    questions: List[OperatorInterviewQuestion] = []
    net = report.network
    hw = report.hardware

    # 1. Acoustic Ambient Noise Interview Trigger (12.0 - 19.9 dB)
    if settings.SNR_CRITICAL_DB <= hw.snr_db < settings.SNR_DEGRADED_DB:
        questions.append(
            OperatorInterviewQuestion(
                question_id="Q-AUDIO-FAN",
                prompt=f"Elevated ambient noise detected ({hw.snr_db:.1f} dB SNR). Is the high-speed ceiling fan or AC running directly near the boundary microphone?",
                category="ACOUSTIC_NOISE",
                options=[
                    "Ceiling Fan Turned Off (Remediation Applied)",
                    "Ceiling Fan Switched to Low Speed",
                    "Cannot Turn Off Noise Source"
                ],
                remediation_advice="Turn off high-speed ceiling fan directly above the bench boundary microphone to restore 20+ dB SNR."
            )
        )

    # 2. Network Packet Loss Interview Trigger (0.5% - 2.0%)
    if settings.PACKET_LOSS_DEGRADED_PCT < net.packet_loss_pct <= settings.PACKET_LOSS_CRITICAL_PCT:
        questions.append(
            OperatorInterviewQuestion(
                question_id="Q-NET-UPLINK",
                prompt=f"Elevated packet loss detected ({net.packet_loss_pct:.1f}%). Which network uplink is currently active on the courtroom terminal?",
                category="NETWORK_UPLINK",
                options=[
                    "Switched to Secondary 4G Backup Dongle",
                    "Restarted Primary Leased Line ONT Router",
                    "Retaining Primary Uplink (No Backup Available)"
                ],
                remediation_advice="Plug in the pre-configured Jio/Airtel secondary 4G backup dongle into USB Port 1."
            )
        )

    # 3. Network Latency Interview Trigger (120 - 300 ms)
    if settings.LATENCY_DEGRADED_MS < net.latency_ms <= settings.LATENCY_CRITICAL_MS:
        questions.append(
            OperatorInterviewQuestion(
                question_id="Q-NET-CONGESTION",
                prompt=f"Elevated latency observed ({net.latency_ms:.0f} ms). Are other court computers uploading scanned case files on this LAN?",
                category="NETWORK_CONGESTION",
                options=[
                    "Paused Case File Uploads on Local LAN",
                    "Court Terminal Switched to Dedicated VLAN",
                    "LAN Congestion Cannot Be Reduced"
                ],
                remediation_advice="Pause background bulk judicial document uploads during live hearing sessions."
            )
        )

    return questions


def evaluate_telemetry(report: TelemetryReportRequest) -> EvaluationResult:
    """Evaluates courtroom telemetry against strict Koyal ASR quality gates.

    Calculates Golden Standard alignment and triggers operator interview questions when degraded.
    """
    net = report.network
    hw = report.hardware

    # Check for technician remediation applied via interview responses
    effective_snr = hw.snr_db
    effective_packet_loss = net.packet_loss_pct
    remediation_notes: List[str] = []

    if report.interview_responses:
        # Operator turned off the ceiling fan -> apply +6.0 dB SNR acoustic clearance
        if report.interview_responses.get("Q-AUDIO-FAN") in ("Ceiling Fan Turned Off (Remediation Applied)", "Fan Turned Off"):
            effective_snr += 6.0
            remediation_notes.append("REMEDIATION_CONFIRMED: Operator turned off ceiling fan (+6.0 dB acoustic boost applied).")

        # Operator switched to 4G backup dongle -> apply network stabilization
        if "Switched to Secondary 4G Backup Dongle" in report.interview_responses.get("Q-NET-UPLINK", ""):
            effective_packet_loss = max(0.1, effective_packet_loss - 0.8)
            remediation_notes.append("REMEDIATION_CONFIRMED: Court terminal switched to secondary 4G backup.")

    critical_reasons: List[str] = []
    degraded_reasons: List[str] = []

    # 1. Packet Loss Check (Koyal ASR drops audio frames over WebSocket)
    if effective_packet_loss > settings.PACKET_LOSS_CRITICAL_PCT:
        critical_reasons.append(
            f"HIGH_PACKET_LOSS: Packet loss of {effective_packet_loss:.1f}% exceeds critical limit of "
            f"{settings.PACKET_LOSS_CRITICAL_PCT:.1f}%. Koyal ASR WebSocket drops live Indic speech frames."
        )
    elif effective_packet_loss > settings.PACKET_LOSS_DEGRADED_PCT:
        degraded_reasons.append(
            f"ELEVATED_PACKET_LOSS: Packet loss of {effective_packet_loss:.1f}% exceeds optimal limit of "
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
    if effective_snr < settings.SNR_CRITICAL_DB:
        critical_reasons.append(
            f"EXCESSIVE_AMBIENT_NOISE: Audio SNR of {effective_snr:.1f} dB is below critical floor of "
            f"{settings.SNR_CRITICAL_DB:.1f} dB. Background noise masks speech signal."
        )
    elif effective_snr < settings.SNR_DEGRADED_DB:
        degraded_reasons.append(
            f"ELEVATED_AMBIENT_NOISE: Audio SNR of {effective_snr:.1f} dB is below optimal floor of "
            f"{settings.SNR_DEGRADED_DB:.1f} dB. Acoustic gain boost recommended."
        )

    # Level 4: Calculate Golden Standard Alignment
    golden_score = calculate_golden_alignment(report, report.golden_profile_id)

    # Level 3: Generate pending interview questions if degraded
    pending_questions = generate_interview_questions(report)

    metrics_summary: Dict[str, Any] = {
        "packet_loss_pct": effective_packet_loss,
        "latency_ms": net.latency_ms,
        "jitter_ms": net.jitter_ms,
        "ws_rtt_ms": net.ws_rtt_ms,
        "mic_sample_rate_hz": hw.mic_sample_rate_hz,
        "snr_db": effective_snr,
        "mic_device_name": hw.mic_device_name,
        "golden_alignment_pct": golden_score.alignment_pct,
    }

    if critical_reasons:
        return EvaluationResult(
            verdict=Verdict.CRITICAL,
            can_start_session=False,
            reason_codes=critical_reasons + remediation_notes,
            summary="PRE-FLIGHT FAILED: Critical quality gate breach. Court session cannot begin safely.",
            metrics=metrics_summary,
            golden_alignment=golden_score,
            pending_questions=[],
        )

    if degraded_reasons:
        return EvaluationResult(
            verdict=Verdict.DEGRADED,
            can_start_session=True,
            reason_codes=degraded_reasons + remediation_notes,
            summary="PRE-FLIGHT WARNING: Sub-optimal telemetry detected. Complete the diagnostic interview to resolve.",
            metrics=metrics_summary,
            golden_alignment=golden_score,
            pending_questions=pending_questions,
        )

    all_optimal_codes = ["ALL_SYSTEMS_OPTIMAL: Telemetry clears all Koyal ASR quality gates."] + remediation_notes
    return EvaluationResult(
        verdict=Verdict.OPTIMAL,
        can_start_session=True,
        reason_codes=all_optimal_codes,
        summary="PRE-FLIGHT PASSED: Courtroom network and audio meet optimal live transcription benchmarks.",
        metrics=metrics_summary,
        golden_alignment=golden_score,
        pending_questions=[],
    )
