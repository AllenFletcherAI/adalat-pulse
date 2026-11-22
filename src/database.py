"""Deterministic SQLite persistence layer for Adalat-Pulse."""

import os
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from src.config import settings
from src.models import (
    TelemetryReportRequest,
    EvaluationResult,
    Verdict,
    StateCode,
    CourtroomStatusSummary,
)


def get_db_path() -> str:
    """Extracts filesystem path from SQLite database URL and ensures parent directory exists."""
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite:///"):
        path_str = db_url.replace("sqlite:///", "")
    else:
        path_str = "data/adalat_pulse.db"

    # Handle relative or absolute paths safely
    path = Path(path_str).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    return str(path)


def get_connection() -> sqlite3.Connection:
    """Returns a SQLite connection configured with WAL mode and row factory."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db() -> None:
    """Initializes tables and indexes for telemetry, incidents, and sync logs."""
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS telemetry_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            courtroom_id TEXT NOT NULL,
            state TEXT NOT NULL,
            bench_name TEXT NOT NULL,
            latency_ms REAL NOT NULL,
            jitter_ms REAL NOT NULL,
            packet_loss_pct REAL NOT NULL,
            ws_rtt_ms REAL NOT NULL,
            mic_sample_rate_hz INTEGER NOT NULL,
            snr_db REAL NOT NULL,
            mic_device_name TEXT,
            verdict TEXT NOT NULL,
            can_start_session INTEGER NOT NULL,
            reasons TEXT,
            incident_id TEXT,
            airtable_synced INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_telemetry_courtroom ON telemetry_snapshots(courtroom_id);
        CREATE INDEX IF NOT EXISTS idx_telemetry_state ON telemetry_snapshots(state);
        CREATE INDEX IF NOT EXISTS idx_telemetry_created ON telemetry_snapshots(created_at DESC);

        CREATE TABLE IF NOT EXISTS incidents (
            id TEXT PRIMARY KEY,
            courtroom_id TEXT NOT NULL,
            state TEXT NOT NULL,
            severity TEXT NOT NULL,
            verdict TEXT NOT NULL,
            title TEXT NOT NULL,
            details TEXT NOT NULL,
            slack_status TEXT,
            linear_status TEXT,
            linear_issue_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_incidents_created ON incidents(created_at DESC);

        CREATE TABLE IF NOT EXISTS airtable_sync_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            synced_count INTEGER NOT NULL,
            status TEXT NOT NULL,
            details TEXT,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()


# Ensure tables are ready on module load
try:
    init_db()
except Exception:
    pass



def save_telemetry_snapshot(
    report: TelemetryReportRequest,
    evaluation: EvaluationResult,
    incident_id: Optional[str] = None
) -> int:
    """Saves a single courtroom diagnostic report to SQLite and returns the snapshot ID."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO telemetry_snapshots (
                courtroom_id, state, bench_name,
                latency_ms, jitter_ms, packet_loss_pct, ws_rtt_ms,
                mic_sample_rate_hz, snr_db, mic_device_name,
                verdict, can_start_session, reasons, incident_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                report.courtroom_id,
                report.state.value,
                report.bench_name,
                report.network.latency_ms,
                report.network.jitter_ms,
                report.network.packet_loss_pct,
                report.network.ws_rtt_ms,
                report.hardware.mic_sample_rate_hz,
                report.hardware.snr_db,
                report.hardware.mic_device_name,
                evaluation.verdict.value,
                1 if evaluation.can_start_session else 0,
                json.dumps(evaluation.reason_codes),
                incident_id
            )
        )
        conn.commit()
        return cursor.lastrowid or 0


def get_latest_courtrooms() -> List[Dict[str, Any]]:
    """Returns the most recent diagnostic snapshot for every active courtroom."""
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT 
                t.courtroom_id,
                t.state,
                t.bench_name,
                t.verdict,
                t.latency_ms,
                t.packet_loss_pct,
                t.snr_db,
                t.can_start_session,
                t.incident_id,
                t.created_at as last_ping
            FROM telemetry_snapshots t
            INNER JOIN (
                SELECT courtroom_id, MAX(id) as max_id
                FROM telemetry_snapshots
                GROUP BY courtroom_id
            ) latest ON t.id = latest.max_id
            ORDER BY t.created_at DESC
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_courtroom_history(courtroom_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Returns time-series telemetry records for a single courtroom."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT 
                id, courtroom_id, state, bench_name,
                latency_ms, jitter_ms, packet_loss_pct, ws_rtt_ms,
                mic_sample_rate_hz, snr_db, verdict, can_start_session,
                reasons, incident_id, created_at
            FROM telemetry_snapshots
            WHERE courtroom_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (courtroom_id.upper(), limit)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def save_incident(
    incident_id: str,
    courtroom_id: str,
    state: str,
    severity: str,
    verdict: str,
    title: str,
    details: str,
    slack_status: str,
    linear_status: str,
    linear_issue_id: Optional[str] = None
) -> None:
    """Persists an incident report generated from a critical diagnostic breach."""
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO incidents (
                id, courtroom_id, state, severity, verdict,
                title, details, slack_status, linear_status, linear_issue_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                incident_id,
                courtroom_id,
                state,
                severity,
                verdict,
                title,
                details,
                slack_status,
                linear_status,
                linear_issue_id
            )
        )
        conn.commit()


def get_recent_incidents(limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieves the most recent incident reports."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT id, courtroom_id, state, severity, verdict, title, details,
                   slack_status, linear_status, linear_issue_id, created_at
            FROM incidents
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def log_airtable_sync(synced_count: int, status: str, details: str = "") -> None:
    """Logs an Airtable partner base synchronization execution."""
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO airtable_sync_logs (synced_count, status, details)
            VALUES (?, ?, ?)
            """,
            (synced_count, status, details)
        )
        conn.commit()


def mark_airtable_synced(snapshot_ids: List[int]) -> None:
    """Marks telemetry snapshots as successfully synced to Airtable."""
    if not snapshot_ids:
        return
    with get_connection() as conn:
        placeholders = ",".join("?" for _ in snapshot_ids)
        conn.execute(
            f"UPDATE telemetry_snapshots SET airtable_synced = 1 WHERE id IN ({placeholders})",
            snapshot_ids
        )
        conn.commit()
