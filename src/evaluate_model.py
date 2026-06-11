from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
)
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
REPORTS_DIR = Path("reports")
METRICS_PATH = REPORTS_DIR / "metrics.txt"
CONFUSION_MATRIX_PATH = REPORTS_DIR / "confusion_matrix.png"


def main():
    data = pd.read_csv(DATA_PATH)
    data["label_numeric"] = data["label"].apply(lambda value: 0 if value == "BENIGN" else 1)

    x = data[FEATURE_COLUMNS]
    y = data["label_numeric"]

    _, x_test, _, y_test = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    model = joblib.load(MODEL_PATH)
    predictions = model.predict(x_test)

    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(
        y_test,
        predictions,
        target_names=["BENIGN", "ATTACK"],
    )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with METRICS_PATH.open("w", encoding="utf-8") as file:
        file.write("AI-SOC Alert Assistant - Model Evaluation Report\n")
        file.write("=" * 55)
        file.write("\n\n")
        file.write(f"Accuracy: {accuracy}\n\n")
        file.write("Classification Report:\n")
        file.write(report)

    print("Accuracy:", accuracy)
    print(report)

    matrix = confusion_matrix(y_test, predictions)
    display = ConfusionMatrixDisplay(
        confusion_matrix=matrix,
        display_labels=["BENIGN", "ATTACK"],
    )

    display.plot()
    plt.title("Confusion Matrix - AI-SOC Alert Assistant")
    plt.tight_layout()
    plt.savefig(CONFUSION_MATRIX_PATH)
    plt.close()

    print("Results saved in the reports folder.")


if __name__ == "__main__":
    main()
