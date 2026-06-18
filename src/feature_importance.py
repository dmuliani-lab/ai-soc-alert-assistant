from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd


MODEL_PATH = Path("models/ai_soc_model.pkl")
FEATURES_PATH = Path("models/features.pkl")
REPORTS_DIR = Path("reports")
FEATURE_IMPORTANCE_CSV = REPORTS_DIR / "feature_importance.csv"
FEATURE_IMPORTANCE_PNG = REPORTS_DIR / "feature_importance.png"
EXPLAINABILITY_REPORT = REPORTS_DIR / "explainability_report.txt"


def main():
    model = joblib.load(MODEL_PATH)
    feature_names = joblib.load(FEATURES_PATH)

    if not hasattr(model, "feature_importances_"):
        raise AttributeError("The trained model does not provide feature_importances_.")

    importance_df = pd.DataFrame(
        {
            "Feature": feature_names,
            "Importance": model.feature_importances_,
        }
    ).sort_values(by="Importance", ascending=False)

    most_important = importance_df.iloc[0]

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    importance_df.to_csv(FEATURE_IMPORTANCE_CSV, index=False, encoding="utf-8")

    plt.figure(figsize=(8, 5))
    plt.barh(importance_df["Feature"], importance_df["Importance"], color="#3D9EFF")
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.title("Feature Importance - AI-SOC Alert Assistant")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(FEATURE_IMPORTANCE_PNG, dpi=160)
    plt.close()

    explanation = f"""AI-SOC Alert Assistant - Explainability Report
================================================

Most important feature: {most_important["Feature"]}
Importance value: {most_important["Importance"]:.4f}

Feature importance helps SOC analysts understand which input fields had the
strongest global influence on the Random Forest model. This makes the prototype
more transparent than a black-box prediction-only system.

Important limitation:
This is a global explanation. It describes the model's overall behavior across
the dataset, not the exact reason for one individual alert prediction.

Future work:
For local, per-alert explanations, future versions can use SHAP or LIME.
"""
    EXPLAINABILITY_REPORT.write_text(explanation, encoding="utf-8")

    print("Feature Importance:")
    print(importance_df)
    print(f"\nMost important feature: {most_important['Feature']}")
    print("Feature importance reports saved in the reports folder.")


if __name__ == "__main__":
    main()
