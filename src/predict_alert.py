from pathlib import Path

import joblib
import pandas as pd

from risk_score import calculate_risk_score, get_risk_level


FEATURE_COLUMNS = [
    "duration",
    "src_bytes",
    "dst_bytes",
    "packet_count",
    "error_count",
]

MODEL_PATH = Path("models/ai_soc_model.pkl")


def main():
    model = joblib.load(MODEL_PATH)

    new_alert = {
        "duration": 13,
        "src_bytes": 13000,
        "dst_bytes": 160,
        "packet_count": 110,
        "error_count": 17,
    }

    alert_df = pd.DataFrame([new_alert], columns=FEATURE_COLUMNS)

    prediction = model.predict(alert_df)[0]
    probability = model.predict_proba(alert_df)[0]

    attack_probability = probability[1]
    risk_score = calculate_risk_score(attack_probability)
    risk_level = get_risk_level(risk_score)

    if prediction == 1:
        print("Result: Possible attack")
    else:
        print("Result: Normal traffic")

    print("Attack probability:", round(attack_probability, 2))
    print("Risk score:", risk_score)
    print("Risk level:", risk_level)


if __name__ == "__main__":
    main()
