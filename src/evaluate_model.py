from pathlib import Path

import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

from data_loader import load_alert_data


MODEL_PATH = Path("models/ai_soc_model.pkl")
REPORTS_DIR = Path("reports")
METRICS_PATH = REPORTS_DIR / "metrics.txt"
CONFUSION_MATRIX_PATH = REPORTS_DIR / "confusion_matrix.png"

LIMITATION_NOTE = (
    "The current dataset is small and simplified. High accuracy may be caused by "
    "the small artificial sample dataset. For stronger scientific conclusions, "
    "a larger dataset such as CIC-IDS2017 or UNSW-NB15 should be used."
)


def main():
    x, y, _ = load_alert_data()
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
    precision = precision_score(y_test, predictions, zero_division=0)
    recall = recall_score(y_test, predictions, zero_division=0)
    f1 = f1_score(y_test, predictions, zero_division=0)
    matrix = confusion_matrix(y_test, predictions, labels=[0, 1])
    report = classification_report(
        y_test,
        predictions,
        target_names=["BENIGN", "ATTACK"],
        zero_division=0,
    )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with METRICS_PATH.open("w", encoding="utf-8") as file:
        file.write("AI-SOC Alert Assistant - Model Evaluation Report\n")
        file.write("=" * 55 + "\n\n")
        file.write(f"Accuracy: {accuracy:.4f}\n")
        file.write(f"Precision: {precision:.4f}\n")
        file.write(f"Recall: {recall:.4f}\n")
        file.write(f"F1-score: {f1:.4f}\n\n")
        file.write("Confusion Matrix [BENIGN, ATTACK]:\n")
        file.write(str(matrix))
        file.write("\n\nClassification Report:\n")
        file.write(report)
        file.write("\n\nLimitations Note:\n")
        file.write(LIMITATION_NOTE + "\n")

    display = ConfusionMatrixDisplay(
        confusion_matrix=matrix,
        display_labels=["BENIGN", "ATTACK"],
    )
    display.plot(cmap="Blues")
    plt.title("Confusion Matrix - AI-SOC Alert Assistant")
    plt.tight_layout()
    plt.savefig(CONFUSION_MATRIX_PATH, dpi=160)
    plt.close()

    print("Accuracy:", round(accuracy, 4))
    print("Precision:", round(precision, 4))
    print("Recall:", round(recall, 4))
    print("F1-score:", round(f1, 4))
    print("\nClassification Report:")
    print(report)
    print("Results saved in the reports folder.")


if __name__ == "__main__":
    main()
