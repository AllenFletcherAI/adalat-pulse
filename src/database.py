"""Deterministic SQLite persistence layer for Adalat-Pulse.

Supports append-only telemetry snapshots, incident tracking, certified golden standard profiles,
and technician interview interaction history.
"""

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
    CourtroomTier,
    GoldenBaselineProfile,
)


def get_db_path() -> str:
    """Extracts filesystem path from SQLite database URL and ensures parent directory exists."""
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite:///"):
        path_str = db_url.replace("sqlite:///", "")
    else:
        path_str = "data/adalat_pulse.db"

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
    """Initializes tables, seed profiles, and indexes."""
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
            golden_profile_id TEXT,
            alignment_pct REAL,
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

        CREATE TABLE IF NOT EXISTS golden_profiles (
            profile_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            courtroom_tier TEXT NOT NULL,
            target_latency_ms REAL NOT NULL,
            target_packet_loss_pct REAL NOT NULL,
            target_jitter_ms REAL NOT NULL,
            target_ws_rtt_ms REAL NOT NULL,
            target_snr_db REAL NOT NULL,
            required_sample_rate_hz INTEGER NOT NULL,
            hardware_stack TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS diagnostic_interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            courtroom_id TEXT NOT NULL,
            question_id TEXT NOT NULL,
            selected_option TEXT NOT NULL,
            remediation_applied INTEGER NOT NULL,
            result_verdict TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS airtable_sync_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            synced_count INTEGER NOT NULL,
            status TEXT NOT NULL,
            details TEXT,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Ensure schema migrations for existing local databases
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(telemetry_snapshots)")
        columns = [row[1] for row in cursor.fetchall()]
        if "golden_profile_id" not in columns:
            conn.execute("ALTER TABLE telemetry_snapshots ADD COLUMN golden_profile_id TEXT")
        if "alignment_pct" not in columns:
            conn.execute("ALTER TABLE telemetry_snapshots ADD COLUMN alignment_pct REAL")

        # Seed Level 4 Golden Profiles if not already present
        conn.execute("""
        INSERT OR IGNORE INTO golden_profiles (
            profile_id, title, courtroom_tier,
            target_latency_ms, target_packet_loss_pct, target_jitter_ms, target_ws_rtt_ms,
            target_snr_db, required_sample_rate_hz, hardware_stack
        ) VALUES 
        (
            'GOLDEN-HC-FIBER',
            'High Court Dedicated Leased Line Benchmark',
            'HIGH_COURT',
            35.0, 0.0, 4.0, 45.0,
            28.0, 48000,
            'Dedicated 1 Gbps Leased Line + Shure MX393 Boundary Microphones'
        ),
        (
            'GOLDEN-DC-HYBRID',
            'District Court Civil Bench Dual-ISP Benchmark',
            'DISTRICT_COURT',
            70.0, 0.2, 8.0, 80.0,
            22.0, 16000,
            'Dual 100 Mbps Broadband (BSNL + Airtel) + Digital Desktop Array'
        ),
        (
            'GOLDEN-TL-EDGE',
            'Rural Taluka Sub-Division Edge 4G Benchmark',
            'TALUKA_COURT',
            110.0, 0.5, 14.0, 120.0,
            18.0, 16000,
            'Bonded Cellular Dongles (Jio + Airtel) + Directional Noise-Canceling Mic'
        )
        """)
        conn.commit()


def save_telemetry_snapshot(
    report: TelemetryReportRequest,
    evaluation: EvaluationResult,
    incident_id: Optional[str] = None
) -> int:
    """Saves a courtroom diagnostic report with golden alignment to SQLite."""
    with get_connection() as conn:
        alignment_pct = (
            evaluation.golden_alignment.alignment_pct
            if evaluation.golden_alignment else None
        )
        cursor = conn.execute(
            """
            INSERT INTO telemetry_snapshots (
                courtroom_id, state, bench_name,
                latency_ms, jitter_ms, packet_loss_pct, ws_rtt_ms,
                mic_sample_rate_hz, snr_db, mic_device_name,
                verdict, can_start_session, reasons, incident_id,
                golden_profile_id, alignment_pct
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                incident_id,
                report.golden_profile_id,
                alignment_pct
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
                t.golden_profile_id,
                t.alignment_pct,
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
                reasons, incident_id, golden_profile_id, alignment_pct, created_at
            FROM telemetry_snapshots
            WHERE courtroom_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (courtroom_id.upper(), limit)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_golden_profiles() -> List[Dict[str, Any]]:
    """Retrieves all certified golden standard baseline profiles."""
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM golden_profiles ORDER BY target_latency_ms ASC")
        return [dict(row) for row in cursor.fetchall()]


def get_golden_profile(profile_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single golden profile by ID."""
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM golden_profiles WHERE profile_id = ?", (profile_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def save_interview_interaction(
    courtroom_id: str,
    question_id: str,
    selected_option: str,
    remediation_applied: bool,
    result_verdict: str
) -> None:
    """Persists a technician diagnostic interview response."""
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO diagnostic_interviews (
                courtroom_id, question_id, selected_option,
                remediation_applied, result_verdict
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                courtroom_id.upper(),
                question_id,
                selected_option,
                1 if remediation_applied else 0,
                result_verdict
            )
        )
        conn.commit()


def get_courtroom_interviews(courtroom_id: str) -> List[Dict[str, Any]]:
    """Retrieves historical diagnostic interview interactions for a courtroom."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT id, courtroom_id, question_id, selected_option,
                   remediation_applied, result_verdict, created_at
            FROM diagnostic_interviews
            WHERE courtroom_id = ?
            ORDER BY created_at DESC
            """,
            (courtroom_id.upper(),)
        )
        return [dict(row) for row in cursor.fetchall()]


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


# Auto-initialize on module load
try:
    init_db()
except Exception:
    pass
