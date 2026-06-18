from pathlib import Path

import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from data_loader import load_alert_data


REPORTS_DIR = Path("reports")
CSV_PATH = REPORTS_DIR / "model_comparison.csv"
TXT_PATH = REPORTS_DIR / "model_comparison.txt"


def evaluate_model(name, model, x_train, x_test, y_train, y_test):
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    tn, fp, fn, tp = confusion_matrix(y_test, predictions, labels=[0, 1]).ravel()
    return {
        "model": name,
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(y_test, predictions, zero_division=0),
        "recall": recall_score(y_test, predictions, zero_division=0),
        "f1_score": f1_score(y_test, predictions, zero_division=0),
        "true_negative": tn,
        "false_positive": fp,
        "false_negative": fn,
        "true_positive": tp,
    }


def main():
    x, y, _ = load_alert_data()
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.25, random_state=42, stratify=y
    )

    models = [
        ("Logistic Regression", LogisticRegression(max_iter=1000, random_state=42)),
        ("Decision Tree", DecisionTreeClassifier(random_state=42)),
        ("Random Forest", RandomForestClassifier(n_estimators=100, random_state=42)),
        ("Gradient Boosting", GradientBoostingClassifier(random_state=42)),
    ]

    results = [evaluate_model(name, model, x_train, x_test, y_train, y_test) for name, model in models]
    results_df = pd.DataFrame(results)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(CSV_PATH, index=False)

    report_text = "AI-SOC Alert Assistant - Model Comparison\n"
    report_text += "=" * 52 + "\n\n"
    report_text += results_df.to_string(index=False)
    TXT_PATH.write_text(report_text + "\n", encoding="utf-8")

    print(report_text)
    print(f"\nSaved: {CSV_PATH}")
    print(f"Saved: {TXT_PATH}")


if __name__ == "__main__":
    main()
