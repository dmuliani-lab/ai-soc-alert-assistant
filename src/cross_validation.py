from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import make_scorer, precision_score, recall_score
from sklearn.model_selection import StratifiedKFold, cross_validate

from data_loader import load_alert_data


REPORTS_DIR = Path("reports")
CSV_PATH = REPORTS_DIR / "cross_validation_results.csv"
TXT_PATH = REPORTS_DIR / "cross_validation_results.txt"


def get_fold_count(y):
    smallest_class_count = int(y.value_counts().min())
    if smallest_class_count < 2:
        return 0
    return 5 if smallest_class_count >= 5 else smallest_class_count


def main():
    x, y, _ = load_alert_data()
    folds = get_fold_count(y)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    if folds < 2:
        message = (
            "Cross-validation could not be performed because the smallest class "
            "contains fewer than 2 samples."
        )
        pd.DataFrame([{"message": message}]).to_csv(CSV_PATH, index=False)
        TXT_PATH.write_text(message + "\n", encoding="utf-8")
        print(message)
        return

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=42)
    scoring = {
        "accuracy": "accuracy",
        "precision": make_scorer(precision_score, zero_division=0),
        "recall": make_scorer(recall_score, zero_division=0),
        "f1": "f1",
    }

    scores = cross_validate(model, x, y, cv=cv, scoring=scoring)
    rows = []
    for metric in scoring:
        values = scores[f"test_{metric}"]
        rows.append(
            {
                "metric": metric,
                "mean": values.mean(),
                "std": values.std(),
                "folds": folds,
            }
        )

    results_df = pd.DataFrame(rows)
    results_df.to_csv(CSV_PATH, index=False)

    report_text = "AI-SOC Alert Assistant - Stratified K-Fold Cross-Validation\n"
    report_text += "=" * 66 + "\n\n"
    report_text += f"Number of folds: {folds}\n\n"
    report_text += results_df.to_string(index=False)
    TXT_PATH.write_text(report_text + "\n", encoding="utf-8")

    print(report_text)
    print(f"\nSaved: {CSV_PATH}")
    print(f"Saved: {TXT_PATH}")


if __name__ == "__main__":
    main()
