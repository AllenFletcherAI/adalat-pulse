"""Integration tests for FastAPI REST endpoints in Adalat-Pulse."""

import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.models import TelemetryReportRequest


@pytest.mark.asyncio
async def test_health_check_endpoint():
    """Verifies that the /api/v1/health endpoint confirms database connectivity."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "HEALTHY"
        assert data["database_connected"] is True
        assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_submit_optimal_telemetry_report(optimal_report: TelemetryReportRequest):
    """Verifies that submitting an optimal report returns an OPTIMAL verdict."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = optimal_report.model_dump(mode="json")
        response = await client.post("/api/v1/telemetry/report", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["verdict"] == "OPTIMAL"
        assert data["can_start_session"] is True
        assert data["courtroom_id"] == "KL-HC-CRT01"
        assert data["snapshot_id"] > 0


@pytest.mark.asyncio
async def test_submit_critical_telemetry_report(critical_packet_loss_report: TelemetryReportRequest):
    """Verifies that submitting a critical report generates an incident ID and halts session."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = critical_packet_loss_report.model_dump(mode="json")
        response = await client.post("/api/v1/telemetry/report", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["verdict"] == "CRITICAL"
        assert data["can_start_session"] is False
        assert data["incident_id"] is not None
        assert data["incident_id"].startswith("INC-RJ-RJ-DC-JPR02")


@pytest.mark.asyncio
async def test_submit_invalid_payload_returns_422():
    """Verifies that schema validation failures return HTTP 422."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        invalid_payload = {
            "courtroom_id": "X",  # Too short (< 3 chars)
            "state": "INVALID_STATE",
            "bench_name": "Test",
            "network": {"latency_ms": -50.0, "jitter_ms": 0, "packet_loss_pct": 150.0, "ws_rtt_ms": 0},
            "hardware": {"mic_sample_rate_hz": 0, "snr_db": 0}
        }
        response = await client.post("/api/v1/telemetry/report", json=invalid_payload)
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_fleet_status_overview(optimal_report: TelemetryReportRequest):
    """Verifies that /api/v1/courtrooms/status aggregates stats for all 11 Indian partner states."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Submit a report first
        payload = optimal_report.model_dump(mode="json")
        await client.post("/api/v1/telemetry/report", json=payload)

        response = await client.get("/api/v1/courtrooms/status")
        assert response.status_code == 200
        data = response.json()
        assert data["total_active_courtrooms"] >= 1
        assert len(data["regions"]) == 11  # All 11 partner states represented
        state_codes = [r["state"] for r in data["regions"]]
        for expected in ["KL", "KA", "AP", "MH", "DL", "TN", "UP", "WB", "GJ", "RJ", "MP"]:
            assert expected in state_codes


@pytest.mark.asyncio
async def test_courtroom_history_not_found():
    """Verifies that querying an unknown courtroom history returns HTTP 404."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/courtrooms/UNKNOWN-ID/history")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_incidents_feed():
    """Verifies that the /api/v1/incidents endpoint returns a valid incident array."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/incidents")
        assert response.status_code == 200
        data = response.json()
        assert "incidents" in data
        assert isinstance(data["incidents"], list)
