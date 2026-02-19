from src.config import MODEL_META_PATH, MODEL_PATH
from src.train import main as train_main


def test_training_creates_artifacts():
    train_main()

    assert MODEL_PATH.exists()
    assert MODEL_META_PATH.exists()
