from src.config import MODEL_META_PATH, MODEL_PATH
from src.inference import predict
from src.train import main as train_main


def test_inference_multiclass_smoke():
    train_main()

    assert MODEL_PATH.exists()
    assert MODEL_META_PATH.exists()

    features = {
        "Age": 35,
        "MotorValue": 15000,
        "HealthDependentsAdults": 1,
        "HealthDependentsKids": 0,
        "CreditCardType": "Visa",
        "MotorType": "Single",
        "HealthType": "Level3",
        "TravelType": "Premium",
        "MotorInsurance": "Yes",
        "HealthInsurance": "No",
        "TravelInsurance": "No",
        "Gender": "male",
        "Location": "Urban",
    }

    label, proba_map = predict(features)

    assert isinstance(label, str)
    assert isinstance(proba_map, dict)
    assert len(proba_map) == 3
    assert abs(sum(proba_map.values()) - 1.0) < 1e-6
