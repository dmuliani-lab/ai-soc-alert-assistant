from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

from data_loader import load_alert_data


MODEL_PATH = Path("models/ai_soc_model.pkl")
FEATURES_PATH = Path("models/features.pkl")


def main():
    x, y, feature_names = load_alert_data()

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
        class_weight="balanced",
    )
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(
        y_test,
        predictions,
        target_names=["BENIGN", "ATTACK"],
        zero_division=0,
    )

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(feature_names, FEATURES_PATH)

    print("AI-SOC Alert Assistant - Training Summary")
    print("=" * 48)
    print(f"Samples: {len(x)}")
    print(f"Features: {len(feature_names)}")
    print(f"Feature names: {', '.join(feature_names)}")
    print(f"Main model: Random Forest")
    print(f"Test accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(report)
    print(f"Model saved to: {MODEL_PATH}")
    print(f"Feature names saved to: {FEATURES_PATH}")


if __name__ == "__main__":
    main()
