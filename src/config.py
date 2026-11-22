"""Configuration settings for Adalat-Pulse gateway."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server Runtime
    APP_ENV: str = "production"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DATABASE_URL: str = "sqlite:///./data/adalat_pulse.db"

    # External Integrations
    AIRTABLE_API_KEY: Optional[str] = None
    AIRTABLE_BASE_ID: Optional[str] = None
    AIRTABLE_TABLE_NAME: str = "Courtroom Telemetry"

    SLACK_WEBHOOK_URL: Optional[str] = None
    SLACK_CHANNEL: str = "#all-adalat-pulse-alerts"

    LINEAR_API_KEY: Optional[str] = None
    LINEAR_TEAM_ID: Optional[str] = None
    LINEAR_TEAM_KEY: str = "ALL"

    # Koyal ASR Telemetry Threshold Boundaries
    # 1. Packet Loss (%)
    PACKET_LOSS_CRITICAL_PCT: float = 2.0
    PACKET_LOSS_DEGRADED_PCT: float = 0.5

    # 2. Latency (ms)
    LATENCY_CRITICAL_MS: float = 300.0
    LATENCY_DEGRADED_MS: float = 120.0

    # 3. Jitter (ms)
    JITTER_CRITICAL_MS: float = 40.0
    JITTER_DEGRADED_MS: float = 15.0

    # 4. WebSocket Keepalive RTT (ms)
    WS_RTT_CRITICAL_MS: float = 350.0
    WS_RTT_DEGRADED_MS: float = 150.0

    # 5. Microphone Sample Rate (Hz)
    MIN_MIC_SAMPLE_RATE_HZ: int = 16000

    # 6. Audio Signal-to-Noise Ratio (dB)
    SNR_CRITICAL_DB: float = 12.0
    SNR_DEGRADED_DB: float = 20.0


settings = Settings()
