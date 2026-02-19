import pandas as pd

from monitoring.drift import compute_drift
from src.config import DATASET_PATH, FEATURES


def test_drift_computation_smoke():
    df = pd.read_csv(DATASET_PATH)

    # Simulate "current" by sampling some rows
    current_df = df.sample(n=200, random_state=42).copy()

    drift_share, drift_flags, report = compute_drift(current_df)

    assert 0.0 <= drift_share <= 1.0
    assert isinstance(drift_flags, dict)
    assert set(drift_flags.keys()) == set(FEATURES)

    # report should be an Evidently Report object
    assert report is not None
