from __future__ import annotations

from typing import Any

import pandas as pd
from evidently.metric_preset import DataDriftPreset
from evidently.report import Report

from src.config import FEATURES, REFERENCE_PATH


def compute_drift(current_df: pd.DataFrame) -> tuple[float, dict[str, bool], Report]:
    reference_df = pd.read_csv(REFERENCE_PATH)[FEATURES]
    current_df = current_df[FEATURES]

    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference_df, current_data=current_df)

    results: dict[str, Any] = report.as_dict()

    # --- Robust extraction ---
    drifted_features: list[str] = []

    for metric in results.get("metrics", []):
        result = metric.get("result", {})
        # Common keys across versions:
        if "drift_by_columns" in result:
            drift_by_columns = result["drift_by_columns"]
            drifted_features = [
                col for col, info in drift_by_columns.items()
                if info.get("drift_detected") is True
            ]
            break

        if "drift_by_feature" in result:
            drift_by_feature = result["drift_by_feature"]
            drifted_features = [
                col for col, info in drift_by_feature.items()
                if info.get("drift_detected") is True
            ]
            break

    drift_flags = {f: (f in drifted_features) for f in FEATURES}
    drift_share = len(drifted_features) / len(FEATURES)

    return drift_share, drift_flags, report
