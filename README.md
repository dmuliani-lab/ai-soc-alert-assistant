# AI SOC Alert Assistant

Small starter project for classifying simple network alert records as normal traffic or a possible attack.

## Project Structure

```text
ai-soc-alert-assistant/
├── data/
│   └── sample_alerts.csv
├── src/
│   ├── train_model.py
│   ├── predict_alert.py
│   └── risk_score.py
├── models/
├── reports/
└── app/
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

If `python` does not work on Windows, try:

```bash
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

This workspace already has a working `.venv` created with Python 3.12.

## Train The Model

```bash
python src/train_model.py
```

This reads `data/sample_alerts.csv`, trains a Random Forest classifier, prints accuracy and a classification report, then saves the model to `models/ai_soc_model.pkl`.

## Predict One Alert

```bash
python src/predict_alert.py
```

This loads the saved model, predicts whether one example alert is normal or an attack, and prints attack probability, risk score, and risk level.

## Run The Dashboard

```bash
streamlit run app\dashboard.py
```

The dashboard opens at:

```text
http://localhost:8501
```

It supports manual alert checking and CSV upload for batch alert analysis.

## Run The Single-File HTML Dashboard

```bash
python -m http.server 8088 --directory app
```

Then open:

```text
http://localhost:8088/dashboard.html
```

This standalone dashboard is built with vanilla JavaScript and Chart.js.

## Repository Verification

The completed project is available on the `main` branch and includes the Streamlit dashboard, the standalone HTML dashboard, source modules, trained model artifact, evaluation reports, and dashboard screenshots.

## Create Evaluation Reports

```bash
python src\evaluate_model.py
```

This creates:

```text
reports/metrics.txt
reports/confusion_matrix.png
```

Use these files in the written project to show accuracy, precision, recall, F1-score, and the confusion matrix.

## Create Feature Importance Reports

```bash
python src\feature_importance.py
```

This creates:

```text
reports/feature_importance.csv
reports/feature_importance.png
```

Feature Importance helps explain which alert fields had the strongest influence on the Random Forest model.

## MITRE ATT&CK Mapping

პროექტში დამატებულია MITRE ATT&CK Mapping-ის სასწავლო მოდული. იგი მაღალი რისკის ალერტებს უკავშირებს შესაძლო თავდასხმის ტაქტიკებსა და ტექნიკებს.

მაგალითები:
- მაღალი `packet_count` და `src_bytes` -> Impact / DoS-like behavior
- მაღალი `error_count` -> Credential Access / Brute Force-like behavior
- მაღალი `duration` და `packet_count` -> Command and Control-like suspicious communication

ეს mapping გამოიყენება როგორც პროტოტიპის ნაწილი და რეალურ SOC გარემოში საჭიროებს უფრო ღრმა threat intelligence წყაროებთან ინტეგრაციას.

## Incident Response Recommendations

პროექტში დამატებულია რეკომენდაციების მოდული, რომელიც `risk_level`-ისა და MITRE tactic-ის მიხედვით ანალიტიკოსს აძლევს საწყის რეაგირების ნაბიჯებს.

ეს რეკომენდაციები არ ცვლის ანალიტიკოსის გადაწყვეტილებას, არამედ ეხმარება მას სწრაფ triage პროცესში.

## Project Status

Implemented:
- Machine Learning classification
- Model evaluation report
- Confusion Matrix
- Risk Score
- Risk Level
- Feature Importance
- MITRE ATT&CK Mapping
- Incident Response Recommendations
- Streamlit Dashboard

Limitations:
- The current prototype uses a small synthetic dataset.
- Accuracy is high because the dataset is simple.
- For real SOC usage, larger datasets such as CIC-IDS2017 or UNSW-NB15 are required.
