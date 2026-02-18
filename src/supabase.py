import os
import requests


def get_connection():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set.")

    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    return url, headers


def insert_prediction(row: dict):
    url, headers = get_connection()
    endpoint = f"{url}/rest/v1/predictions"
    r = requests.post(endpoint, headers=headers, json=row)
    r.raise_for_status()


def fetch_recent_predictions(window_days=7):
    from datetime import datetime, timedelta, timezone

    url, headers = get_connection()
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)

    params = {
        "select": "*",
        "ts": f"gte.{cutoff.isoformat()}",
        "order": "ts.asc",
    }

    r = requests.get(f"{url}/rest/v1/predictions", headers=headers, params=params)
    r.raise_for_status()
    return r.json()


def insert_monitoring_metrics(row: dict):
    url, headers = get_connection()
    endpoint = f"{url}/rest/v1/monitoring_metrics"
    r = requests.post(endpoint, headers=headers, json=row)
    r.raise_for_status()
