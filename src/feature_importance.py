from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd


FEATURE_COLUMNS = [
    "duration",
    "src_bytes",
    "dst_bytes",
    "packet_count",
    "error_count",
]

MODEL_PATH = Path("models/ai_soc_model.pkl")
REPORTS_DIR = Path("reports")
FEATURE_IMPORTANCE_CSV = REPORTS_DIR / "feature_importance.csv"
FEATURE_IMPORTANCE_PNG = REPORTS_DIR / "feature_importance.png"


def main():
    model = joblib.load(MODEL_PATH)
    importances = model.feature_importances_

    importance_df = pd.DataFrame(
        {
            "Feature": FEATURE_COLUMNS,
            "Importance": importances,
        }
    ).sort_values(by="Importance", ascending=False)

    print("Feature Importance:")
    print(importance_df)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    importance_df.to_csv(
        FEATURE_IMPORTANCE_CSV,
        index=False,
        encoding="utf-8",
    )

    plt.figure(figsize=(8, 5))
    plt.barh(importance_df["Feature"], importance_df["Importance"])
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.title("Feature Importance - AI-SOC Alert Assistant")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(FEATURE_IMPORTANCE_PNG)
    plt.close()

    print("Feature Importance saved in the reports folder.")


if __name__ == "__main__":
    main()
