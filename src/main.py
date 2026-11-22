"""FastAPI REST Gateway & Real-Time WebSocket Probe for Adalat-Pulse."""

import os
import json
import time
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.models import (
    TelemetryReportRequest,
    TelemetryResponse,
    EvaluationResult,
    Verdict,
    StateCode,
    CourtroomStatusSummary,
    FleetStatusOverview,
    RegionalStats,
    InterviewResponseRequest,
    GoldenBaselineProfile,
)
from src.database import (
    init_db,
    save_telemetry_snapshot,
    get_latest_courtrooms,
    get_courtroom_history,
    get_recent_incidents,
    get_golden_profiles,
    get_golden_profile,
    save_interview_interaction,
    get_courtroom_interviews,
)
from src.evaluator import evaluate_telemetry
from src.alerts import dispatch_critical_incident
from src.airtable_sync import sync_courtroom_to_airtable, sync_all_active_courtrooms


# Map 11 partner state codes to human-readable Indian state names
STATE_NAMES: Dict[str, str] = {
    "KL": "Kerala",
    "KA": "Karnataka",
    "AP": "Andhra Pradesh",
    "MH": "Maharashtra",
    "DL": "Delhi",
    "TN": "Tamil Nadu",
    "UP": "Uttar Pradesh",
    "WB": "West Bengal",
    "GJ": "Gujarat",
    "RJ": "Rajasthan",
    "MP": "Madhya Pradesh",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes SQLite database schema on startup."""
    init_db()
    yield


app = FastAPI(
    title="Adalat-Pulse Telemetry Gateway",
    description="Edge-ready Courtroom Pre-Flight Diagnostic & Deployment Telemetry Gateway for Adalat AI",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for local client and web dashboard interactions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static web dashboard assets
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.api_route("/", methods=["GET", "HEAD"], response_class=FileResponse)
async def serve_dashboard():
    """Serves the single-page operational control dashboard."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return JSONResponse({"message": "Adalat-Pulse Gateway Active. Dashboard index.html not yet installed."})


@app.websocket("/ws/probe")
async def websocket_telemetry_probe(websocket: WebSocket):
    """Real-time WebSocket ping/pong probe to measure actual courtroom network latency and jitter.

    Clients send timestamped frames; server echoes back instantly.
    Allows client to measure actual RTT, jitter, and packet drop without mock numbers.
    """
    await websocket.accept()
    try:
        while True:
            text = await websocket.receive_text()
            data = json.loads(text)
            client_ts = data.get("client_ts", 0)
            seq = data.get("seq", 0)
            server_ts = time.time() * 1000  # ms

            await websocket.send_text(json.dumps({
                "seq": seq,
                "client_ts": client_ts,
                "server_ts": server_ts,
                "status": "PONG"
            }))
    except WebSocketDisconnect:
        pass
    except Exception:
        await websocket.close()


@app.post("/api/v1/telemetry/report", response_model=TelemetryResponse)
async def submit_telemetry_report(report: TelemetryReportRequest):
    """Ingests and deterministically evaluates a courtroom pre-flight diagnostic report.

    Persists to SQLite, dispatches alerts if critical, and synchronizes to Airtable.
    """
    # 1. Deterministic Health Evaluation
    evaluation = evaluate_telemetry(report)

    incident_id: Optional[str] = None
    slack_sent = False
    linear_created = False

    # 2. Automated Incident Routing if Critical
    if evaluation.verdict == Verdict.CRITICAL:
        incident_id, slack_sent, linear_created, _ = await dispatch_critical_incident(report, evaluation)

    # 3. Persist Snapshot to SQLite
    snapshot_id = save_telemetry_snapshot(report, evaluation, incident_id)

    # 4. Live Airtable Synchronization
    airtable_synced = await sync_courtroom_to_airtable(report, evaluation)

    now_iso = datetime.now(timezone.utc).isoformat()

    return TelemetryResponse(
        success=True,
        snapshot_id=snapshot_id,
        courtroom_id=report.courtroom_id,
        state=report.state,
        verdict=evaluation.verdict,
        can_start_session=evaluation.can_start_session,
        evaluation=evaluation,
        incident_id=incident_id,
        airtable_synced=airtable_synced,
        slack_alert_sent=slack_sent,
        linear_ticket_created=linear_created,
        created_at=now_iso,
    )


@app.get("/api/v1/courtrooms/status", response_model=FleetStatusOverview)
async def get_fleet_courtroom_status():
    """Returns aggregated live telemetry overview across all 11 Indian partner states."""
    latest_rows = get_latest_courtrooms()

    # Calculate regional aggregates
    state_groups: Dict[str, List[Dict[str, Any]]] = {code: [] for code in STATE_NAMES.keys()}
    for row in latest_rows:
        s_code = row["state"]
        if s_code in state_groups:
            state_groups[s_code].append(row)

    regions: List[RegionalStats] = []
    verdict_counts = {"OPTIMAL": 0, "DEGRADED": 0, "CRITICAL": 0}

    for code, name in STATE_NAMES.items():
        courts = state_groups[code]
        opt = sum(1 for c in courts if c["verdict"] == "OPTIMAL")
        deg = sum(1 for c in courts if c["verdict"] == "DEGRADED")
        crit = sum(1 for c in courts if c["verdict"] == "CRITICAL")
        tot = len(courts)
        health_pct = round((opt / tot * 100), 1) if tot > 0 else 100.0

        verdict_counts["OPTIMAL"] += opt
        verdict_counts["DEGRADED"] += deg
        verdict_counts["CRITICAL"] += crit

        regions.append(RegionalStats(
            state=StateCode(code),
            state_name=name,
            total_courtrooms=tot,
            optimal_count=opt,
            degraded_count=deg,
            critical_count=crit,
            healthy_pct=health_pct,
        ))

    total_active = len(latest_rows)
    fleet_health = (
        round((verdict_counts["OPTIMAL"] / total_active * 100), 1)
        if total_active > 0 else 100.0
    )

    incidents = get_recent_incidents(10)

    return FleetStatusOverview(
        total_active_courtrooms=total_active,
        fleet_health_pct=fleet_health,
        verdict_breakdown=verdict_counts,
        regions=regions,
        recent_critical_incidents=len(incidents),
        last_updated=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/api/v1/golden-profiles")
async def list_golden_profiles():
    """Returns certified Golden Standard baseline profiles for Level 4 exemplar benchmarking."""
    profiles = get_golden_profiles()
    return {"count": len(profiles), "profiles": profiles}


@app.post("/api/v1/telemetry/interview", response_model=TelemetryResponse)
async def submit_operator_interview(feedback: InterviewResponseRequest):
    """Processes technician responses to diagnostic interview questions and applies remediations."""
    report = feedback.original_report
    if not report.interview_responses:
        report.interview_responses = {}
    report.interview_responses[feedback.question_id] = feedback.selected_option

    # Re-evaluate with remediation applied
    evaluation = evaluate_telemetry(report)

    # Persist technician interaction
    save_interview_interaction(
        courtroom_id=feedback.courtroom_id,
        question_id=feedback.question_id,
        selected_option=feedback.selected_option,
        remediation_applied=feedback.remediation_applied,
        result_verdict=evaluation.verdict.value,
    )

    incident_id: Optional[str] = None
    slack_sent = False
    linear_created = False

    if evaluation.verdict == Verdict.CRITICAL:
        incident_id, slack_sent, linear_created, _ = await dispatch_critical_incident(report, evaluation)

    snapshot_id = save_telemetry_snapshot(report, evaluation, incident_id)
    airtable_synced = await sync_courtroom_to_airtable(report, evaluation)

    now_iso = datetime.now(timezone.utc).isoformat()
    return TelemetryResponse(
        success=True,
        snapshot_id=snapshot_id,
        courtroom_id=report.courtroom_id,
        state=report.state,
        verdict=evaluation.verdict,
        can_start_session=evaluation.can_start_session,
        evaluation=evaluation,
        incident_id=incident_id,
        airtable_synced=airtable_synced,
        slack_alert_sent=slack_sent,
        linear_ticket_created=linear_created,
        created_at=now_iso,
    )


@app.get("/api/v1/courtrooms/{courtroom_id}/history")
async def get_single_courtroom_history(courtroom_id: str, limit: int = 50):
    """Retrieves time-series telemetry records for a single courtroom."""
    history = get_courtroom_history(courtroom_id, limit)
    if not history:
        raise HTTPException(status_code=404, detail=f"No telemetry found for courtroom {courtroom_id}")
    return {"courtroom_id": courtroom_id.upper(), "records_count": len(history), "history": history}


@app.get("/api/v1/incidents")
async def get_incidents_feed(limit: int = 20):
    """Retrieves live incident feed with Slack and Linear dispatch receipts."""
    incidents = get_recent_incidents(limit)
    return {"count": len(incidents), "incidents": incidents}


@app.post("/api/v1/sync/airtable")
async def trigger_airtable_sync():
    """Manually triggers synchronization of all active courtrooms to Airtable partner base."""
    result = await sync_all_active_courtrooms()
    return result


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint validating runtime integrity and SQLite connectivity."""
    db_ok = False
    try:
        from src.database import get_connection
        with get_connection() as conn:
            cursor = conn.execute("SELECT 1")
            db_ok = (cursor.fetchone()[0] == 1)
    except Exception:
        db_ok = False

    return {
        "status": "HEALTHY" if db_ok else "UNHEALTHY",
        "service": "Adalat-Pulse Telemetry Gateway",
        "version": "1.0.0",
        "database_connected": db_ok,
        "environment": settings.APP_ENV,
        "slack_configured": bool(settings.SLACK_WEBHOOK_URL),
        "linear_configured": bool(settings.LINEAR_API_KEY and settings.LINEAR_TEAM_ID),
        "airtable_configured": bool(settings.AIRTABLE_API_KEY and settings.AIRTABLE_BASE_ID),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
