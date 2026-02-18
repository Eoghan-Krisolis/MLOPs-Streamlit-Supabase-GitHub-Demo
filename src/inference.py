from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd

from src.config import FEATURES, MODEL_META_PATH, MODEL_PATH
from src.supabase import insert_prediction


# -----------------------------
# 1) Load Artifacts
# -----------------------------
def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Model not trained yet. Run: python -m src.train")
    return joblib.load(MODEL_PATH)


def load_model_meta() -> dict:
    if not MODEL_META_PATH.exists():
        raise FileNotFoundError("model_meta.json not found. Train the model first.")
    return json.loads(MODEL_META_PATH.read_text(encoding="utf-8"))


def get_model_version(meta: dict) -> str:
    return str(meta.get("model_version", "unknown"))


# -----------------------------
# 2) Prediction Logic
# -----------------------------
def make_input_df(features: Dict[str, float | int]) -> pd.DataFrame:
    """
    Ensures input matches training schema.
    """
    return pd.DataFrame([{k: features[k] for k in FEATURES}])


def predict_proba_and_label(model, X: pd.DataFrame) -> Tuple[str, Dict[str, float]]:
    """
    Returns:
    - predicted label (string)
    - dict of {class_name: probability}
    """
    proba = model.predict_proba(X)[0]  # shape = (n_classes,)
    classes = list(model.classes_)     # e.g. ["Email", "Phone", "SMS"]

    proba_map = {cls: float(p) for cls, p in zip(classes, proba)}
    predicted_label = classes[int(np.argmax(proba))]

    return predicted_label, proba_map


# -----------------------------
# 3) Logging
# -----------------------------
def build_prediction_row(
    features: Dict[str, float | int],
    predicted_label: str,
    proba_map: Dict[str, float],
    model_version: str,
) -> dict:
    """
    Creates a row compatible with Supabase storage.
    """
    row = {
        "request_id": str(uuid.uuid4()),
        "ts": datetime.now(timezone.utc).isoformat(),
        "model_version": model_version,
        **features,
        "predicted_label": predicted_label,
    }

    # Store probabilities in separate columns if possible (recommended)
    # If your classes differ, these keys must match your schema.
    row["proba_email"] = proba_map.get("Email")
    row["proba_phone"] = proba_map.get("Phone")
    row["proba_sms"] = proba_map.get("SMS")

    return row


# -----------------------------
# 4) Public API
# -----------------------------
def predict(features: Dict[str, float | int]) -> Tuple[str, Dict[str, float]]:
    """
    Main inference entrypoint.

    Returns:
    - predicted label (string)
    - probability map for all classes
    """
    model = load_model()
    meta = load_model_meta()

    X = make_input_df(features)
    predicted_label, proba_map = predict_proba_and_label(model, X)

    # best effort logging to Supabase
    row = build_prediction_row(
        features=features,
        predicted_label=predicted_label,
        proba_map=proba_map,
        model_version=get_model_version(meta),
    )

    try:
        insert_prediction(row)
    except Exception:
        # never break inference UX if logging fails
        pass

    return predicted_label, proba_map
