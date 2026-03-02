import json

import pandas as pd

from monitoring.drift import compute_drift
from monitoring.log_metrics import make_metrics_row
from src.config import MODEL_META_PATH, MONITORING_DIR
from src.supabase import fetch_recent_predictions, insert_monitoring_metrics
from src.train import main as retrain
from pathlib import Path
import os



def main():
    summary_file = os.getenv("GITHUB_STEP_SUMMARY")

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

    report_path = MONITORING_DIR / "drift_report.html"
    report.save_html(str(report_path))

    min_rows_required = 200
    current_rows = len(current_df)

    if current_rows < min_rows_required:
        print("::warning::Insufficient prediction data for reliable drift detection.")
        retrain_triggered = False
    else:
        retrain_triggered = drift_share >= threshold

    if retrain_triggered:
        print("::warning::Drift threshold exceeded. Automatic retraining trigerred. New training data may be needed.")
        retrain()
    else:
        print("No retraining needed.")

    try:
        metrics_row = make_metrics_row(
            model_version=model_version,
            window_days=window_days,
            current_rows=current_rows,
            drift_share=drift_share,
            drift_flags=drift_flags,
            threshold=threshold,
            retrain_triggered=(drift_share >= threshold),
        )
        insert_monitoring_metrics(metrics_row)

        if summary_file:
            with open(summary_file, "a") as f:
                f.write("## Drift Report\n")
                f.write(f"- Number of rows: {current_rows}\n")
                f.write(f"- Rows required for robust drift calculation: {min_rows_required}\n")
                f.write(f"- Drift share: {drift_share:.3f}\n")
                f.write(f"- Drift threshold: {threshold}\n")
                if retrain_triggered:
                    f.write(f"*Action required:* Significant feature drift detected, update training data and retrain model")
    except Exception:
        pass


if __name__ == "__main__":
    main()
