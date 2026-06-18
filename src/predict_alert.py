from pathlib import Path

import joblib
import pandas as pd

from risk_score import calculate_risk_score, get_risk_level


MODEL_PATH = Path("models/ai_soc_model.pkl")
FEATURES_PATH = Path("models/features.pkl")


def main():
    model = joblib.load(MODEL_PATH)
    feature_names = joblib.load(FEATURES_PATH)

    new_alert = {
        "duration": 13,
        "src_bytes": 13000,
        "dst_bytes": 160,
        "packet_count": 110,
        "error_count": 17,
    }

    alert_df = pd.DataFrame([new_alert])
    alert_df = alert_df.reindex(columns=feature_names, fill_value=0)

    prediction = model.predict(alert_df)[0]
    probability = model.predict_proba(alert_df)[0]

    attack_probability = probability[1]
    risk_score = calculate_risk_score(attack_probability)
    risk_level = get_risk_level(risk_score)

    print("Result:", "Possible attack" if prediction == 1 else "Normal traffic")
    print("Attack probability:", round(attack_probability, 2))
    print("Risk score:", risk_score)
    print("Risk level:", risk_level)


if __name__ == "__main__":
    main()
