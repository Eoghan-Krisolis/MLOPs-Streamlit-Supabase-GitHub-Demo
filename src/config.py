from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "data"
MODEL_DIR = ROOT / "models"
MONITORING_DIR = ROOT / "monitoring"

DATASET_PATH = DATA_DIR / "InsureABC_Channel_Data.csv"
MODEL_PATH = MODEL_DIR / "model.joblib"
MODEL_META_PATH = MODEL_DIR / "model_meta.json"

FEATURES = [
    "CreditCardType",
    "Gender",
    "Age",
    "Location",
    "MotorInsurance",
    "MotorValue",
    "MotorType",
    "HealthInsurance",
    "HealthType",
    "HealthDependentsAdults",
    "HealthDependentsKids",
    "TravelInsurance",
    "TravelType",
]
TARGET = "PrefChannel"
