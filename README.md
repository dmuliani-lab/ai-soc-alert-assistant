# AI-SOC Alert Assistant

AI-SOC Alert Assistant is a bachelor thesis prototype that demonstrates how
machine learning can support Security Operations Center (SOC) analysts. The
system classifies simplified network alerts, estimates attack probability,
calculates a risk score, assigns a risk level, shows global feature importance,
and maps suspicious behavior to educational MITRE ATT&CK tactics.

The project is designed as a beginner-friendly academic prototype. It supports
analyst triage and explanation, but it is not a production SIEM, threat
intelligence platform, or autonomous incident-response system.

## Main Features

- Manual alert check
- CSV alert upload and batch analysis
- Attack probability prediction
- Risk Score calculation
- Risk Level classification: Low, Medium, High, or Critical
- Feature Importance / Explainable AI
- MITRE ATT&CK Mapping
- Model Evaluation
- Model Comparison
- Stratified K-Fold Cross-validation
- Streamlit Dashboard
- Initial incident-response recommendations

## Technologies

- Python
- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- Joblib
- Streamlit
- Altair

## Project Structure

```text
ai-soc-alert-assistant/
├── app/
│   ├── dashboard.py                 # Interactive Streamlit dashboard
│   └── dashboard.html               # Standalone dashboard prototype
├── data/
│   └── sample_alerts.csv            # Small demonstration dataset
├── diagrams/
│   ├── system_architecture.mmd       # Mermaid architecture diagram
│   └── use_case_diagram.mmd          # Mermaid analyst use cases
├── docs/
│   ├── technical_documentation.md    # Detailed technical documentation
│   ├── installation_guide.md         # Installation and troubleshooting
│   ├── user_manual.md                # Dashboard user manual
│   └── ...                           # Demo, Git, appendix, and checklist files
├── models/
│   ├── ai_soc_model.pkl              # Trained Random Forest model
│   └── features.pkl                  # Saved model feature order
├── presentation/
│   ├── slide_content.md              # Georgian 12-slide presentation draft
│   └── AI_SOC_Final_Presentation_DRAFT.pptx
├── reports/
│   ├── metrics.txt
│   ├── confusion_matrix.png
│   ├── feature_importance.csv
│   ├── feature_importance.png
│   ├── model_comparison.csv
│   ├── model_comparison.txt
│   ├── cross_validation_results.csv
│   ├── cross_validation_results.txt
│   ├── explainability_report.txt
│   └── practical_summary.txt
├── screenshots/
│   └── README.md                     # Required screenshot capture guide
├── src/
│   ├── data_loader.py                # CSV loading and preprocessing
│   ├── train_model.py                # Random Forest training
│   ├── predict_alert.py              # Single-alert command-line example
│   ├── evaluate_model.py             # Metrics and confusion matrix
│   ├── model_comparison.py            # Baseline/model comparison
│   ├── cross_validation.py            # Stratified cross-validation
│   ├── feature_importance.py          # Global explainability artifacts
│   ├── risk_score.py                  # Risk Score and level rules
│   ├── mitre_mapping.py               # Educational MITRE mapping rules
│   └── incident_response.py           # Response recommendations
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation

Run the commands from the repository root.

### Quick Start (PowerShell)

Copy these commands exactly:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src\train_model.py
python src\evaluate_model.py
python src\feature_importance.py
streamlit run app\dashboard.py
```

### PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Command Prompt

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

## Train the Model

```powershell
python src\train_model.py
```

The script trains the main Random Forest classifier and saves:

```text
models/ai_soc_model.pkl
models/features.pkl
```

## Evaluate the Model

```powershell
python src\evaluate_model.py
```

## Run Model Comparison

```powershell
python src\model_comparison.py
```

This compares Logistic Regression, Decision Tree, Random Forest, and Gradient
Boosting on the same train/test split.

## Run Cross-validation

```powershell
python src\cross_validation.py
```

The script uses Stratified K-Fold and selects a valid number of folds based on
the smallest class in the demonstration dataset.

## Generate Feature Importance

```powershell
python src\feature_importance.py
```

## Run the Dashboard

```powershell
streamlit run app\dashboard.py
```

Expected local URL:

```text
http://localhost:8501
```

## Generated Reports

- `reports/metrics.txt`
- `reports/confusion_matrix.png`
- `reports/feature_importance.csv`
- `reports/feature_importance.png`
- `reports/model_comparison.csv`
- `reports/model_comparison.txt`
- `reports/cross_validation_results.csv`
- `reports/cross_validation_results.txt`
- `reports/explainability_report.txt`
- `reports/practical_summary.txt`

The repository may also contain dashboard screenshots generated during local
testing. They should not be confused with the final screenshots that must be
captured for the thesis appendix and presentation.

## Risk Score

The prototype combines model output and simple SOC context:

```text
Risk Score = (
    0.55 × Attack Probability
  + 0.25 × Severity
  + 0.20 × Asset Criticality
) × 100
```

Default demonstration values are used for severity and asset criticality.
Production weights would require validation with historical incidents,
business impact, asset context, and analyst feedback.

## Limitations

- The current dataset is small, simplified, and intended for demonstration.
- High accuracy can result from the small artificial dataset and is not proof
  of production-level SOC performance.
- The current global Feature Importance output does not explain one individual
  prediction.
- MITRE ATT&CK Mapping uses simple educational rules, not a complete threat
  intelligence or detection engineering system.
- Risk Score weights are manually selected and have not been calibrated with
  real organizational incident data.
- Stronger scientific evaluation should use larger datasets such as
  CIC-IDS2017 or UNSW-NB15.

## Future Work

- Evaluate and retrain with a larger, realistic dataset
- Add SHAP/LIME local explanations
- Add FastAPI integration
- Integrate with a real SIEM or alert pipeline
- Add an analyst feedback loop
- Improve MITRE ATT&CK mapping and technique coverage
- Add model versioning, drift monitoring, and experiment tracking

## Documentation

Detailed Georgian documentation is available in `docs/`, including the
technical document, installation guide, user manual, demo script, Git
submission instructions, diagrams explanation, and final checklist.

## Final Submission Materials

- [Final presentation draft](presentation/AI_SOC_Final_Presentation_DRAFT.pptx)
- [Technical documentation](docs/technical_documentation.md)
- [Dashboard screenshot guide](screenshots/README.md)
- [System architecture diagram](diagrams/system_architecture.mmd)
- [Use case diagram](diagrams/use_case_diagram.mmd)

## GitHub Repository

https://github.com/dmuliani-lab/ai-soc-alert-assistant
