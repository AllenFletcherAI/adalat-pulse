"""Live Airtable partner base synchronization client."""

import urllib.parse
import httpx
from typing import Dict, Any, Optional, List
from src.config import settings
from src.models import TelemetryReportRequest, EvaluationResult
from src.database import get_latest_courtrooms, log_airtable_sync


def get_airtable_headers() -> Dict[str, str]:
    """Generates authorization headers for Airtable API."""
    if not settings.AIRTABLE_API_KEY:
        raise ValueError("AIRTABLE_API_KEY is not configured.")
    return {
        "Authorization": f"Bearer {settings.AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }


def get_table_url() -> str:
    """Constructs Airtable REST API endpoint for the configured base and table."""
    if not settings.AIRTABLE_BASE_ID:
        raise ValueError("AIRTABLE_BASE_ID is not configured.")
    encoded_table = urllib.parse.quote(settings.AIRTABLE_TABLE_NAME)
    return f"https://api.airtable.com/v0/{settings.AIRTABLE_BASE_ID}/{encoded_table}"


async def sync_courtroom_to_airtable(
    report: TelemetryReportRequest,
    evaluation: EvaluationResult
) -> bool:
    """Upserts a single courtroom telemetry snapshot directly into Airtable."""
    if not settings.AIRTABLE_API_KEY or not settings.AIRTABLE_BASE_ID:
        return False

    url = get_table_url()
    headers = get_airtable_headers()

    fields_payload = {
        "Courtroom ID": report.courtroom_id,
        "Verdict": evaluation.verdict.value,
        "State": report.state.value,
        "Latency (ms)": round(report.network.latency_ms, 1),
        "Packet Loss (%)": round(report.network.packet_loss_pct, 1),
        "ASR Ready": evaluation.can_start_session,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Check if record already exists for this courtroom
            formula = f"{{Courtroom ID}} = '{report.courtroom_id}'"
            find_res = await client.get(url, headers=headers, params={"filterByFormula": formula, "maxRecords": 1})

            if find_res.status_code == 200:
                existing_records = find_res.json().get("records", [])
                if existing_records:
                    # Update existing record
                    record_id = existing_records[0]["id"]
                    patch_res = await client.patch(
                        f"{url}/{record_id}",
                        headers=headers,
                        json={"fields": fields_payload, "typecast": True}
                    )
                    return patch_res.status_code == 200

            # Record does not exist: create new
            create_res = await client.post(
                url,
                headers=headers,
                json={"fields": fields_payload, "typecast": True}
            )
            return create_res.status_code in (200, 201)

    except Exception as e:
        log_airtable_sync(0, f"ERROR: {str(e)[:100]}")
        return False


async def sync_all_active_courtrooms() -> Dict[str, Any]:
    """Syncs the latest state of all courtrooms from SQLite to Airtable."""
    if not settings.AIRTABLE_API_KEY or not settings.AIRTABLE_BASE_ID:
        return {"success": False, "synced_count": 0, "message": "Airtable credentials not configured"}

    courtrooms = get_latest_courtrooms()
    if not courtrooms:
        return {"success": True, "synced_count": 0, "message": "No courtrooms found to sync"}

    url = get_table_url()
    headers = get_airtable_headers()
    synced_count = 0
    errors: List[str] = []

    async with httpx.AsyncClient(timeout=15.0) as client:
        for cr in courtrooms:
            fields_payload = {
                "Courtroom ID": cr["courtroom_id"],
                "Verdict": cr["verdict"],
                "State": cr["state"],
                "Latency (ms)": round(cr["latency_ms"], 1),
                "Packet Loss (%)": round(cr["packet_loss_pct"], 1),
                "ASR Ready": bool(cr["can_start_session"]),
            }

            try:
                formula = f"{{Courtroom ID}} = '{cr['courtroom_id']}'"
                find_res = await client.get(url, headers=headers, params={"filterByFormula": formula, "maxRecords": 1})

                if find_res.status_code == 200:
                    records = find_res.json().get("records", [])
                    if records:
                        rec_id = records[0]["id"]
                        upd_res = await client.patch(
                            f"{url}/{rec_id}",
                            headers=headers,
                            json={"fields": fields_payload, "typecast": True}
                        )
                        if upd_res.status_code == 200:
                            synced_count += 1
                        continue

                # Create if not found
                add_res = await client.post(
                    url,
                    headers=headers,
                    json={"fields": fields_payload, "typecast": True}
                )
                if add_res.status_code in (200, 201):
                    synced_count += 1
                else:
                    errors.append(f"{cr['courtroom_id']}: HTTP {add_res.status_code}")
            except Exception as e:
                errors.append(f"{cr['courtroom_id']}: {str(e)[:60]}")

    status = "SUCCESS" if synced_count > 0 else "FAILED"
    details = f"Synced {synced_count}/{len(courtrooms)}. Errors: {', '.join(errors)}" if errors else f"Synced {synced_count} courtrooms."
    log_airtable_sync(synced_count, status, details)

    return {
        "success": synced_count > 0 or len(courtrooms) == 0,
        "synced_count": synced_count,
        "total_courtrooms": len(courtrooms),
        "errors": errors
    }
