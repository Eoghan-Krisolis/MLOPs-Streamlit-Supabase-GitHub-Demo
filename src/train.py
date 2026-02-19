from __future__ import annotations

import json
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, OrdinalEncoder
from sklearn.utils.class_weight import compute_sample_weight
from src.transformers import clamp_age, clamp_motor_value, fix_gender


from src.config import (
    DATASET_PATH,
    FEATURES,
    MODEL_DIR,
    MODEL_META_PATH,
    MODEL_PATH,
    TARGET,
)


# -----------------------------
# 1) Data Loading / Cleaning
# -----------------------------
def load_dataset(path: str | None = None) -> pd.DataFrame:
    """
    Loads the initial dataset from CSV.
    Assumes the dataset already exists.
    """
    p = DATASET_PATH if path is None else path
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"{DATASET_PATH} not found.")
    return pd.read_csv(p)


def clean_target(y: pd.Series) -> pd.Series:
    """
    Converts short codes to readable labels.
    """
    return y.replace({"P": "Phone", "E": "Email", "S": "SMS"})


def split_data(df: pd.DataFrame):
    """
    Returns stratified train/test split.
    """
    X = df[FEATURES].copy()
    y = clean_target(df[TARGET].copy())

    return train_test_split(X, y, test_size=0.2, random_state=123, stratify=y)


# -----------------------------
# 2) Preprocessing
# -----------------------------



def build_preprocessor() -> ColumnTransformer:
    """
    Defines preprocessing for each feature group using sklearn pipelines.
    """

    # Column groups
    age_col = ["Age"]
    motor_value_col = ["MotorValue"]

    other_numeric = ["HealthDependentsAdults", "HealthDependentsKids"]
    credit_card = ["CreditCardType"]

    types = ["MotorType", "HealthType", "TravelType"]
    binary = ["MotorInsurance", "HealthInsurance", "TravelInsurance"]

    gender = ["Gender"]
    other_cat = ["Location"]

    # --- Transformers ---

    age_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("clamp", FunctionTransformer(clamp_age)),
        ]
    )

    motor_value_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("clamp", FunctionTransformer(clamp_motor_value)
),
        ]
    )

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value=0)),
        ]
    )

    onehot_missing = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    onehot_none = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="none")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    binary_transformer = Pipeline(
        steps=[
            (
                "ordinal",
                OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1),
            )
        ]
    )

    gender_transformer = Pipeline(
        steps=[
            ("fix_gender", FunctionTransformer(fix_gender)),
            (
                "ordinal",
                OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1),
            ),
        ]
    )

    other_cat_transformer = Pipeline(
        steps=[
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    # ColumnTransformer
    preprocessor = ColumnTransformer(
        transformers=[
            ("age", age_transformer, age_col),
            ("motor_value", motor_value_transformer, motor_value_col),
            ("num", numeric_transformer, other_numeric),
            ("credit", onehot_missing, credit_card),
            ("types", onehot_none, types),
            ("binary", binary_transformer, binary),
            ("gender", gender_transformer, gender),
            ("other_cat", other_cat_transformer, other_cat),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )

    return preprocessor


# -----------------------------
# 3) Model
# -----------------------------
def build_model() -> GradientBoostingClassifier:
    """
    Defines the ML model. Gradient Boosting is a strong baseline.
    """
    return GradientBoostingClassifier(
        n_estimators=100,
        min_samples_split=70,
        learning_rate=0.07,
        n_iter_no_change=10,
        random_state=123,
    )


def build_pipeline() -> Pipeline:
    """
    Full pipeline = preprocessing + classifier.
    """
    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            ("classifier", build_model()),
        ]
    )


# -----------------------------
# 4) Training / Evaluation
# -----------------------------
def fit_pipeline(pipeline: Pipeline, X_train: pd.DataFrame, y_train: pd.Series) -> Pipeline:
    """
    Fits the model using sample weights for class imbalance.
    """
    sample_weight = compute_sample_weight(class_weight="balanced", y=y_train)
    pipeline.fit(X_train, y_train, classifier__sample_weight=sample_weight)
    return pipeline


def evaluate(pipeline: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> float:
    """
    Balanced accuracy is suitable for class imbalance.
    """
    preds = pipeline.predict(X_test)
    return float(balanced_accuracy_score(y_test, preds))


# -----------------------------
# 5) Saving Artifacts
# -----------------------------
def save_artifacts(pipeline: Pipeline, score: float) -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(pipeline, MODEL_PATH)

    meta = {
        "model_version": datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S"),
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "balanced_accuracy": score,
        "features": FEATURES,
        "target": TARGET,
        "model_type": "GradientBoostingClassifier",
    }

    MODEL_META_PATH.write_text(json.dumps(meta, indent=2), encoding="utf-8")


# -----------------------------
# 6) Main Entry Point
# -----------------------------
def main() -> None:
    df = load_dataset()

    X_train, X_test, y_train, y_test = split_data(df)

    pipeline = build_pipeline()
    pipeline = fit_pipeline(pipeline, X_train, y_train)

    score = evaluate(pipeline, X_test, y_test)

    save_artifacts(pipeline, score)

    print("Training complete.")
    print(f"Balanced Accuracy: {score:.4f}")


if __name__ == "__main__":
    main()
