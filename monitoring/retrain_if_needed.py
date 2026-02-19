import json

import pandas as pd

from monitoring.drift import compute_drift
from monitoring.log_metrics import make_metrics_row
from src.config import MODEL_META_PATH, MONITORING_DIR
from src.supabase import fetch_recent_predictions, insert_monitoring_metrics
from src.train import main as retrain


def main():
    threshold = float((MONITORING_DIR / "drift_threshold.txt").read_text())

    window_days = 7
    model_version = json.loads((MODEL_META_PATH).read_text())["model_version"]

    rows = fetch_recent_predictions(window_days=window_days)

    if not rows:
        print("No recent data.")
        return

    current_df = pd.DataFrame(rows)

    drift_share, drift_flags, report = compute_drift(current_df)

    print("Drift share:", drift_share)

    report.save_html(MONITORING_DIR / "drift_report.html")

    if drift_share >= threshold:
        print("Retraining triggered.")
        retrain()
    else:
        print("No retraining needed.")

    try:
        metrics_row = make_metrics_row(
            model_version=model_version,
            window_days=window_days,
            current_rows=len(current_df),
            drift_share=drift_share,
            drift_flags=drift_flags,
            threshold=threshold,
            retrain_triggered=(drift_share >= threshold),
        )
        insert_monitoring_metrics(metrics_row)
    except Exception:
        pass


if __name__ == "__main__":
    main()
