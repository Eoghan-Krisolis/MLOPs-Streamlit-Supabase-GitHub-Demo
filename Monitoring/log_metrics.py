import json
from datetime import datetime, timezone

from src.supabase import insert_monitoring_metrics


def make_metrics_row(
    model_version: str,
    window_days: int,
    current_rows: int,
    drift_share: float,
    drift_flags: dict,
    threshold: float,
    retrain_triggered: bool,
) -> dict:
    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "model_version": model_version,
        "window_days": int(window_days),
        "current_rows": int(current_rows),
        "drift_share": float(drift_share),
        "drifted_features": drift_flags,
        "threshold": float(threshold),
        "retrain_triggered": bool(retrain_triggered),
    }
