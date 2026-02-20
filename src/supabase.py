import logging
import os
from typing import Any, cast

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _get_url() -> str:
    url = os.getenv("SUPABASE_URL")
    if not url:
        raise RuntimeError("SUPABASE_URL must be set.")
    return url


def _headers(key: str) -> dict[str, str]:
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def _get_anon_key() -> str:
    key = os.getenv("SUPABASE_KEY")
    if not key:
        raise RuntimeError("SUPABASE_KEY must be set for Streamlit logging.")
    return key


def _get_service_role_key() -> str:
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not key:
        raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY must be set for monitoring jobs.")
    return key


# -----------------------------
# Streamlit use case (anon key)
# -----------------------------
def insert_prediction(row: dict[str, Any]) -> None:
    url = _get_url()
    key = _get_anon_key()

    endpoint = f"{url}/rest/v1/predictions"
    r = requests.post(endpoint, headers=_headers(key), json=row)

    logger.info("Supabase INSERT predictions status: %s", r.status_code)

    if r.status_code >= 400:
        logger.error("Supabase INSERT predictions error: %s", r.text)

    r.raise_for_status()


# -----------------------------
# Monitoring use case (service_role)
# -----------------------------
def fetch_recent_predictions(window_days: int = 7) -> list[dict[str, Any]]:
    from datetime import datetime, timedelta, timezone

    url = _get_url()
    key = _get_service_role_key()

    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)

    params = {
        "select": "*",
        "ts": f"gte.{cutoff.isoformat()}",
        "order": "ts.asc",
    }

    r = requests.get(
        f"{url}/rest/v1/predictions",
        headers=_headers(key),
        params=params,
    )
    r.raise_for_status()
    return cast(list[dict[str, Any]], r.json())


def insert_monitoring_metrics(row: dict[str, Any]) -> None:
    url = _get_url()
    key = _get_service_role_key()

    endpoint = f"{url}/rest/v1/monitoring_metrics"
    r = requests.post(endpoint, headers=_headers(key), json=row)

    logger.info("Supabase INSERT monitoring_metrics status: %s", r.status_code)

    if r.status_code >= 400:
        logger.error("Supabase INSERT monitoring_metrics error: %s", r.text)

    r.raise_for_status()