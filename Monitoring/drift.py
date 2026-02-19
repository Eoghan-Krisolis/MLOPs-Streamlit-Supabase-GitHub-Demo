import pandas as pd
from evidently.metric_preset import DataDriftPreset
from evidently.report import Report

from src.config import FEATURES, REFERENCE_PATH


def compute_drift(current_df):
    reference_df = pd.read_csv(REFERENCE_PATH)[FEATURES]
    current_df = current_df[FEATURES]

    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference_df, current_data=current_df)

    results = report.as_dict()
    drift_info = results["metrics"][0]["result"]["drift_by_columns"]

    drift_flags = {col: drift_info[col]["drift_detected"] for col in FEATURES}
    drift_share = sum(drift_flags.values()) / len(FEATURES)

    return drift_share, drift_flags, report
