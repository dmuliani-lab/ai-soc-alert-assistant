from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_DATA_PATH = Path("data/sample_alerts.csv")
LABEL_CANDIDATES = ["label", "Label", "LABEL"]


def load_alert_data(data_path=DEFAULT_DATA_PATH):
    """Load alert CSV data and return numeric features, labels, and feature names."""
    data_path = Path(data_path)
    data = pd.read_csv(data_path)
    data.columns = data.columns.str.strip()

    label_column = next((column for column in LABEL_CANDIDATES if column in data.columns), None)
    if label_column is None:
        raise ValueError("The dataset must contain a label column named 'label' or 'Label'.")

    labels = data[label_column].astype(str).str.strip().str.upper()
    y = labels.apply(lambda value: 0 if value == "BENIGN" else 1)

    feature_data = data.drop(columns=[label_column])
    feature_data = feature_data.select_dtypes(include=["number"]).copy()
    if feature_data.empty:
        raise ValueError("No numeric feature columns were found in the dataset.")

    feature_data = feature_data.replace([np.inf, -np.inf], np.nan)
    feature_data = feature_data.fillna(feature_data.median(numeric_only=True))
    feature_data = feature_data.fillna(0)

    feature_names = feature_data.columns.tolist()
    return feature_data, y, feature_names
