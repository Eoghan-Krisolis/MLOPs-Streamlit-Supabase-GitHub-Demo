from src.train import main as train_main
from src.config import MODEL_PATH, MODEL_META_PATH


def test_training_creates_artifacts():
    train_main()

    assert MODEL_PATH.exists()
    assert MODEL_META_PATH.exists()
