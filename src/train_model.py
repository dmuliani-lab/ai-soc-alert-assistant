from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split


FEATURE_COLUMNS = [
    "duration",
    "src_bytes",
    "dst_bytes",
    "packet_count",
    "error_count",
]

DATA_PATH = Path("data/sample_alerts.csv")
MODEL_PATH = Path("models/ai_soc_model.pkl")


def main():
    data = pd.read_csv(DATA_PATH)

    print("Data loaded successfully")
    print(data.head())

    data["label_numeric"] = data["label"].apply(lambda value: 0 if value == "BENIGN" else 1)

    x = data[FEATURE_COLUMNS]
    y = data["label_numeric"]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
    )
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)

    print("\nAccuracy:", accuracy)
    print("\nClassification Report:")
    print(classification_report(y_test, predictions, target_names=["BENIGN", "ATTACK"]))

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print(f"\nModel saved successfully to {MODEL_PATH}")


if __name__ == "__main__":
    main()
