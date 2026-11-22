"""Pydantic v2 data models, validations, and schemas for Adalat-Pulse."""

from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator


class Verdict(str, Enum):
    OPTIMAL = "OPTIMAL"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"


class StateCode(str, Enum):
    KL = "KL"  # Kerala
    KA = "KA"  # Karnataka
    AP = "AP"  # Andhra Pradesh
    MH = "MH"  # Maharashtra
    DL = "DL"  # Delhi
    TN = "TN"  # Tamil Nadu
    UP = "UP"  # Uttar Pradesh
    WB = "WB"  # West Bengal
    GJ = "GJ"  # Gujarat
    RJ = "RJ"  # Rajasthan
    MP = "MP"  # Madhya Pradesh


class IncidentSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class NetworkMetrics(BaseModel):
    """Network performance metrics measured during 5-second diagnostic probe."""
    latency_ms: float = Field(..., ge=0.0, description="Round-trip latency in milliseconds")
    jitter_ms: float = Field(..., ge=0.0, description="Packet arrival jitter in milliseconds")
    packet_loss_pct: float = Field(..., ge=0.0, le=100.0, description="Packet loss percentage (0.0 to 100.0)")
    ws_rtt_ms: float = Field(..., ge=0.0, description="WebSocket keepalive round-trip time in milliseconds")

    @field_validator("packet_loss_pct")
    @classmethod
    def validate_packet_loss(cls, v: float) -> float:
        if v < 0.0 or v > 100.0:
            raise ValueError("Packet loss percentage must be between 0.0 and 100.0")
        return round(v, 2)


class HardwareMetrics(BaseModel):
    """Hardware audio readiness metrics for Koyal Indic ASR."""
    mic_sample_rate_hz: int = Field(..., gt=0, description="Audio input hardware sample rate in Hz (e.g. 16000 or 48000)")
    snr_db: float = Field(..., description="Audio Signal-to-Noise Ratio in decibels (ambient noise floor)")
    mic_device_name: str = Field(default="Default Audio Capture Device", min_length=1, description="Audio device name")

    @field_validator("mic_device_name")
    @classmethod
    def sanitize_device_name(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            return "Unknown Audio Device"
        return cleaned[:100]


class TelemetryReportRequest(BaseModel):
    """Courtroom Pre-Flight Diagnostic Report payload submitted to gateway."""
    courtroom_id: str = Field(..., min_length=3, max_length=64, description="Unique courtroom identifier (e.g. DL-HC-CRT04)")
    state: StateCode = Field(..., description="Two-letter Indian state code")
    bench_name: str = Field(..., min_length=2, max_length=128, description="Court bench description")
    network: NetworkMetrics
    hardware: HardwareMetrics
    client_timestamp: Optional[datetime] = None
    app_version: str = Field(default="1.0.0", max_length=16)

    @field_validator("courtroom_id")
    @classmethod
    def uppercase_courtroom_id(cls, v: str) -> str:
        return v.strip().upper()


class EvaluationResult(BaseModel):
    """Deterministic evaluation verdict and plain-language reasoning."""
    verdict: Verdict
    can_start_session: bool
    reason_codes: List[str] = Field(default_factory=list)
    summary: str
    metrics: Dict[str, Any] = Field(default_factory=dict)


class TelemetryResponse(BaseModel):
    """Gateway ingestion response returned to courtroom client."""
    success: bool = True
    snapshot_id: int
    courtroom_id: str
    state: StateCode
    verdict: Verdict
    can_start_session: bool
    evaluation: EvaluationResult
    incident_id: Optional[str] = None
    airtable_synced: bool = False
    slack_alert_sent: bool = False
    linear_ticket_created: bool = False
    created_at: str


class CourtroomStatusSummary(BaseModel):
    """Current live health snapshot for a single courtroom."""
    courtroom_id: str
    state: StateCode
    bench_name: str
    verdict: Verdict
    latency_ms: float
    packet_loss_pct: float
    snr_db: float
    can_start_session: bool
    last_ping: str
    incident_id: Optional[str] = None


class RegionalStats(BaseModel):
    """Aggregate statistics for an Indian partner state."""
    state: StateCode
    state_name: str
    total_courtrooms: int
    optimal_count: int
    degraded_count: int
    critical_count: int
    healthy_pct: float


class FleetStatusOverview(BaseModel):
    """Global CTO fleet telemetry overview across all 11 partner states."""
    total_active_courtrooms: int
    fleet_health_pct: float
    verdict_breakdown: Dict[str, int]
    regions: List[RegionalStats]
    recent_critical_incidents: int
    last_updated: str
