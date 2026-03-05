"""Supabase service — stores structured data (accident reports + alerts)."""

from supabase import create_client, Client
from backend.config.settings import settings


def _get_client() -> Client:
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


_client: Client | None = None


def get_supabase() -> Client:
    global _client
    if _client is None:
        _client = _get_client()
    return _client


# ── Accident Reports ────────────────────────────────────

def save_accident_report(report: dict) -> dict:
    """Insert a row into the accident_reports table. Returns inserted row."""
    resp = get_supabase().table("accident_reports").insert(report).execute()
    return resp.data[0] if resp.data else report


def get_accident_reports(limit: int = 20) -> list[dict]:
    """Fetch recent accident reports."""
    resp = (
        get_supabase()
        .table("accident_reports")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return resp.data or []


# ── Alerts ───────────────────────────────────────────────

def save_alert(alert: dict) -> dict:
    """Insert a row into the alerts table. Returns inserted row."""
    resp = get_supabase().table("alerts").insert(alert).execute()
    return resp.data[0] if resp.data else alert


def get_alerts(limit: int = 20) -> list[dict]:
    """Fetch recent alerts."""
    resp = (
        get_supabase()
        .table("alerts")
        .select("*")
        .order("timestamp", desc=True)
        .limit(limit)
        .execute()
    )
    return resp.data or []
