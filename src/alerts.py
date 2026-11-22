"""Automated incident dispatch engine for Slack and Linear."""

import uuid
import httpx
from datetime import datetime, timezone
from typing import Optional, Tuple, Dict, Any
from src.config import settings
from src.models import (
    TelemetryReportRequest,
    EvaluationResult,
    Verdict,
)
from src.database import save_incident


async def dispatch_critical_incident(
    report: TelemetryReportRequest,
    evaluation: EvaluationResult
) -> Tuple[str, bool, bool, Optional[str]]:
    """Generates an incident ID and dispatches real alerts to Slack and Linear.

    Returns:
        (incident_id, slack_success, linear_success, linear_issue_id)
    """
    ts_compact = datetime.now(timezone.utc).strftime("%y%m%d-%H%M%S")
    incident_id = f"INC-{report.state.value}-{report.courtroom_id}-{ts_compact}"

    title = f"[Courtroom P0 Alert] {report.courtroom_id} ({report.state.value}) - Pre-Flight Diagnostic Failed"
    reasons_text = "\n• " + "\n• ".join(evaluation.reason_codes)

    details = (
        f"**Courtroom ID:** {report.courtroom_id}\n"
        f"**State / Bench:** {report.state.value} | {report.bench_name}\n"
        f"**Verdict:** {evaluation.verdict.value}\n"
        f"**Can Start Session:** {evaluation.can_start_session}\n\n"
        f"### Breached Quality Gates:\n{reasons_text}\n\n"
        f"### Telemetry Snapshot:\n"
        f"- Packet Loss: `{report.network.packet_loss_pct:.1f}%`\n"
        f"- Latency: `{report.network.latency_ms:.0f} ms`\n"
        f"- Jitter: `{report.network.jitter_ms:.1f} ms`\n"
        f"- WS RTT: `{report.network.ws_rtt_ms:.0f} ms`\n"
        f"- Mic Sample Rate: `{report.hardware.mic_sample_rate_hz} Hz`\n"
        f"- Audio SNR: `{report.hardware.snr_db:.1f} dB`\n"
        f"- Input Device: `{report.hardware.mic_device_name}`\n"
    )

    slack_status = "SKIPPED_NO_URL"
    linear_status = "SKIPPED_NO_KEY"
    linear_issue_id: Optional[str] = None
    slack_success = False
    linear_success = False

    # 1. Dispatch Live Slack Alert
    if settings.SLACK_WEBHOOK_URL:
        try:
            slack_payload = {
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"[CRITICAL TELEMETRY] {report.courtroom_id}"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": f"*Courtroom:*\n`{report.courtroom_id}` ({report.state.value})"},
                            {"type": "mrkdwn", "text": f"*Bench:*\n{report.bench_name}"},
                            {"type": "mrkdwn", "text": f"*Packet Loss:*\n`{report.network.packet_loss_pct:.1f}%` (Limit: 2.0%)"},
                            {"type": "mrkdwn", "text": f"*Latency:*\n`{report.network.latency_ms:.0f} ms` (Limit: 300 ms)"},
                            {"type": "mrkdwn", "text": f"*Audio SNR:*\n`{report.hardware.snr_db:.1f} dB` (Min: 12.0 dB)"},
                            {"type": "mrkdwn", "text": f"*Sample Rate:*\n`{report.hardware.mic_sample_rate_hz} Hz` (Min: 16k)"}
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Root Cause:*\n{reasons_text}\n\n*Action Required:* Switch courtroom terminal to secondary 4G backup dongle or check audio interface."
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                            {"type": "mrkdwn", "text": f"Incident ID: `{incident_id}` | Adalat-Pulse Telemetry Gateway"}
                        ]
                    }
                ]
            }

            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.post(settings.SLACK_WEBHOOK_URL, json=slack_payload)
                if res.status_code == 200:
                    slack_status = "DELIVERED"
                    slack_success = True
                else:
                    slack_status = f"FAILED_HTTP_{res.status_code}"
        except Exception as e:
            slack_status = f"ERROR: {str(e)[:100]}"

    # 2. Dispatch Live Linear P0 Ticket
    if settings.LINEAR_API_KEY and settings.LINEAR_TEAM_ID:
        try:
            linear_query = """
            mutation CreateIssue($input: IssueCreateInput!) {
                issueCreate(input: $input) {
                    success
                    issue {
                        id
                        identifier
                        title
                        url
                    }
                }
            }
            """
            linear_variables = {
                "input": {
                    "teamId": settings.LINEAR_TEAM_ID,
                    "title": title,
                    "description": details,
                    "priority": 1  # 1 = Urgent (P0)
                }
            }

            headers = {
                "Authorization": settings.LINEAR_API_KEY,
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.post(
                    "https://api.linear.app/graphql",
                    json={"query": linear_query, "variables": linear_variables},
                    headers=headers
                )
                if res.status_code == 200:
                    data = res.json()
                    issue_data = data.get("data", {}).get("issueCreate", {})
                    if issue_data.get("success"):
                        linear_issue = issue_data.get("issue", {})
                        linear_issue_id = linear_issue.get("identifier") or linear_issue.get("id")
                        linear_status = f"CREATED_{linear_issue_id}"
                        linear_success = True
                    else:
                        linear_status = f"FAILED: {data.get('errors', 'Unknown error')}"
                else:
                    linear_status = f"FAILED_HTTP_{res.status_code}"
        except Exception as e:
            linear_status = f"ERROR: {str(e)[:100]}"

    # 3. Persist Incident to Local SQLite
    save_incident(
        incident_id=incident_id,
        courtroom_id=report.courtroom_id,
        state=report.state.value,
        severity="CRITICAL",
        verdict=evaluation.verdict.value,
        title=title,
        details=details,
        slack_status=slack_status,
        linear_status=linear_status,
        linear_issue_id=linear_issue_id
    )

    return incident_id, slack_success, linear_success, linear_issue_id
