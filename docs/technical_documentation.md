# ტექნიკური დოკუმენტაცია

## 1. პროექტის აღწერა

AI-SOC Alert Assistant არის საბაკალავრო ნაშრომის ფარგლებში შექმნილი
პროტოტიპი, რომელიც აჩვენებს მანქანური სწავლების გამოყენების შესაძლებლობას
Security Operations Center-ის (SOC) ალერტების პირველადი დამუშავებისა და
პრიორიტეტიზაციისთვის. სისტემა იღებს ქსელური ალერტის რიცხვით
მახასიათებლებს, ახდენს BENIGN/ATTACK კლასიფიკაციას, ითვლის შეტევის
ალბათობას, Risk Score-სა და Risk Level-ს, აჩვენებს Feature Importance-ს და
ალერტს აკავშირებს MITRE ATT&CK-ის სასწავლო კატეგორიასთან.

პროტოტიპის ამოცანაა ანალიტიკოსის დახმარება და არა ადამიანის ჩანაცვლება.
საბოლოო გადაწყვეტილება, ინციდენტის დადასტურება და რეაგირების მოქმედებები
უნდა დარჩეს SOC ანალიტიკოსის კონტროლის ქვეშ.

## 2. სისტემის მიზანი

სისტემის ძირითადი მიზნებია:

- ალერტების პირველადი კლასიფიკაციის ავტომატიზაციის დემონსტრირება;
- შეტევის ალბათობის გასაგებ რიცხვით მაჩვენებლად წარმოდგენა;
- ალერტების Risk Score-ის მიხედვით პრიორიტეტიზაცია;
- მოდელის გადაწყვეტილების გლობალური ახსნადობის ჩვენება;
- MITRE ATT&CK კონტექსტის დამატება;
- ერთი ალერტისა და CSV batch-ის ანალიზის ერთ dashboard-ში გაერთიანება;
- მოდელის შეფასების, შედარებისა და cross-validation-ის შედეგების შენახვა.

## 3. გამოყენებული ტექნოლოგიები

- **Python** - პროექტის ძირითადი პროგრამირების ენა.
- **Pandas** - CSV მონაცემების ჩატვირთვა, გაწმენდა და ცხრილური დამუშავება.
- **NumPy** - რიცხვითი მნიშვნელობების და სპეციალური მნიშვნელობების დამუშავება.
- **Scikit-learn** - train/test დაყოფა, Random Forest, baseline მოდელები,
  მეტრიკები და Stratified K-Fold Cross-Validation.
- **Matplotlib** - Confusion Matrix-ისა და Feature Importance-ის გრაფიკები.
- **Joblib** - გაწვრთნილი მოდელისა და feature-ების თანმიმდევრობის შენახვა.
- **Streamlit** - ინტერაქტიული dashboard.
- **Altair** - dashboard-ში Feature Importance-ის ინტერაქტიული ვიზუალიზაცია.

## 4. სისტემის არქიტექტურა

სისტემა დაყოფილია რამდენიმე მარტივ ფენად:

1. **Input Layer** - `data/sample_alerts.csv`, მომხმარებლის CSV ფაილი ან
   ხელით შეყვანილი ალერტი.
2. **Data Layer** - `src/data_loader.py` ამოწმებს label სვეტს, ირჩევს რიცხვით
   feature-ებს, ცვლის უსასრულო მნიშვნელობებს და ავსებს გამოტოვებულ მონაცემებს.
3. **ML Layer** - `src/train_model.py` წვრთნის Random Forest კლასიფიკატორს.
4. **Evaluation Layer** - evaluation, model comparison, cross-validation და
   feature importance სკრიპტები ქმნის ანგარიშებს `reports/` საქაღალდეში.
5. **Decision Support Layer** - `risk_score.py`, `mitre_mapping.py` და
   `incident_response.py` მოდელის შედეგს ამატებს ოპერაციულ კონტექსტს.
6. **Presentation Layer** - `app/dashboard.py` მომხმარებელს აძლევს ხელით
   შემოწმების, CSV ატვირთვისა და შედეგების ნახვის საშუალებას.

არქიტექტურის Mermaid დიაგრამა მოცემულია
`diagrams/system_architecture.mmd` ფაილში.

## 5. მონაცემთა დამუშავების pipeline

`src/data_loader.py` ასრულებს შემდეგ მოქმედებებს:

1. კითხულობს CSV ფაილს Pandas-ის საშუალებით.
2. სვეტების სახელებიდან აშორებს ზედმეტ სივრცეებს.
3. ეძებს `label`, `Label` ან `LABEL` სვეტს.
4. `BENIGN` მნიშვნელობას გარდაქმნის `0` კლასად, სხვა label-ს კი `1` კლასად.
5. input მონაცემებიდან ტოვებს მხოლოდ რიცხვით feature-ებს.
6. `inf` და `-inf` მნიშვნელობებს გარდაქმნის `NaN`-ად.
7. გამოტოვებულ მნიშვნელობებს ავსებს მედიანით, ხოლო დარჩენილ `NaN`-ებს - ნულით.
8. აბრუნებს feature matrix-ს, label vector-ს და feature-ების სახელებს.

მოდელის მიმდინარე feature-ებია `duration`, `src_bytes`, `dst_bytes`,
`packet_count` და `error_count`. მოდელის შენახვისას feature-ების თანმიმდევრობა
ინახება `models/features.pkl` ფაილში, რათა dashboard-ის input ზუსტად დაემთხვეს
სასწავლო მონაცემებს.

## 6. მანქანური სწავლების მოდელი

მთავარი მოდელია `RandomForestClassifier`. მიმდინარე პარამეტრებია:

- `n_estimators=100`;
- `random_state=42`;
- `class_weight="balanced"` training სკრიპტში.

მონაცემები იყოფა train/test ნაწილებად `test_size=0.25` პარამეტრით და
stratification-ის გამოყენებით. გაწვრთნილი მოდელი ინახება
`models/ai_soc_model.pkl` ფაილში. Random Forest არჩეულია, რადგან იგი კარგად
მუშაობს მცირე ტაბულარულ მონაცემებზე, შეუძლია არაწრფივი დამოკიდებულებების
დამუშავება და აქვს `feature_importances_` ატრიბუტი.

## 7. Risk Score მექანიზმი

Risk Score-ის მიმდინარე ფორმულაა:

```text
Risk Score = (
    0.55 × Attack Probability
  + 0.25 × Severity
  + 0.20 × Asset Criticality
) × 100
```

პროტოტიპში `severity`-ის default მნიშვნელობაა `0.8`, ხოლო
`asset_criticality`-ის - `0.7`. მიღებული შედეგი იყოფა დონეებად:

- `Critical`: 85 ან მეტი;
- `High`: 70-დან 84.99-მდე;
- `Medium`: 40-დან 69.99-მდე;
- `Low`: 40-ზე ნაკლები.

ეს წონები სასწავლო არჩევანია. რეალურ SOC გარემოში მათი კალიბრაცია უნდა
განხორციელდეს ისტორიული ინციდენტების, ბიზნეს გავლენის, აქტივის კრიტიკულობის
და ანალიტიკოსთა feedback-ის საფუძველზე.

## 8. MITRE ATT&CK Mapping

`src/mitre_mapping.py` შეიცავს წესებზე დაფუძნებულ სასწავლო mapping-ს.
მაგალითად:

- მაღალი `packet_count`, მაღალი `src_bytes` და დაბალი `dst_bytes` უკავშირდება
  `Impact` ტაქტიკასა და DoS/DDoS-ის მსგავს ქცევას;
- მაღალი `error_count` უკავშირდება `Credential Access` ტაქტიკასა და Brute
  Force-ის მსგავს ქცევას;
- მაღალი `duration` და `packet_count` უკავშირდება `Command and Control`
  კატეგორიის საეჭვო ხანგრძლივ კომუნიკაციას.

თუ არცერთი წესი არ ემთხვევა, შედეგია `Unknown / Needs Analyst Review`.
Mapping არ არის სრულფასოვანი threat intelligence სისტემა და არ უნდა იქნას
გამოყენებული production detection rule set-ად.

## 9. Explainable AI / Feature Importance

`src/feature_importance.py` იყენებს Random Forest-ის
`feature_importances_` მნიშვნელობებს. შედეგები ინახება:

- `reports/feature_importance.csv`;
- `reports/feature_importance.png`;
- `reports/explainability_report.txt`.

Feature Importance აჩვენებს მოდელის საერთო, გლობალურ ქცევას. იგი არ აღწერს
ზუსტად, რატომ მიიღო მოდელმა გადაწყვეტილება ერთ კონკრეტულ ალერტზე. ინდივიდუალური
prediction-ის ასახსნელად მომავალში საჭიროა SHAP ან LIME.

## 10. შეფასების მეთოდოლოგია

`src/evaluate_model.py` იყენებს იმავე `random_state=42` და stratified
train/test დაყოფას. ითვლება:

- Accuracy;
- Precision;
- Recall;
- F1-score;
- Confusion Matrix;
- Classification Report.

ტექსტური შედეგები ინახება `reports/metrics.txt`-ში, ხოლო ვიზუალური Confusion
Matrix - `reports/confusion_matrix.png`-ში. კიბერუსაფრთხოების კონტექსტში
განსაკუთრებული ყურადღება უნდა მიექცეს Recall-სა და False Negative-ებს, რადგან
რეალური შეტევის გამოტოვება მაღალი რისკის მატარებელია.

## 11. Model Comparison

`src/model_comparison.py` ადარებს ოთხ ალგორითმს:

- Logistic Regression;
- Decision Tree;
- Random Forest;
- Gradient Boosting.

ყველა მოდელი ფასდება ერთსა და იმავე train/test დაყოფაზე Accuracy, Precision,
Recall, F1-score და confusion matrix-ის კომპონენტებით. შედეგები ინახება
`reports/model_comparison.csv` და `reports/model_comparison.txt` ფაილებში.
Baseline მოდელები საჭიროა იმის საჩვენებლად, რომ მთავარი მოდელის არჩევანი
შედარებით ანალიზს ეფუძნება.

## 12. Cross-validation

`src/cross_validation.py` იყენებს `StratifiedKFold`-ს shuffle-ით და
`random_state=42`-ით. fold-ების რაოდენობა დინამიკურად შეირჩევა უმცირესი
კლასის ზომის მიხედვით: თუ კლასში მინიმუმ 5 ჩანაწერია, გამოიყენება 5 fold;
სხვა შემთხვევაში fold-ების რაოდენობა უდრის უმცირესი კლასის ზომას.

თითოეულ fold-ზე ითვლება Accuracy, Precision, Recall და F1. საბოლოო ანგარიშში
იწერება საშუალო და სტანდარტული გადახრა. შედეგები ინახება
`reports/cross_validation_results.csv` და `.txt` ფაილებში.

## 13. Dashboard-ის აღწერა

`app/dashboard.py` აერთიანებს:

- ერთი ალერტის ხელით შეყვანას;
- BENIGN/ATTACK prediction-ს;
- Attack Probability-ის ჩვენებას;
- Risk Score gauge-სა და Risk Level-ს;
- MITRE ATT&CK tactic/technique/reason ველებს;
- incident-response რეკომენდაციებს;
- CSV batch upload-ს;
- ალერტების შეჯამებას და ცხრილს;
- Feature Importance-ის ცხრილსა და გრაფიკს;
- Model Comparison, Cross-validation და Evaluation ანგარიშების ნახვას.

Dashboard მუშაობს ლოკალურად Streamlit-ის საშუალებით და ჩვეულებრივ იხსნება
`http://localhost:8501` მისამართზე.

## 14. ინსტალაცია და კონფიგურაცია

რეკომენდებულია Python 3.10 ან უფრო ახალი თავსებადი ვერსია და virtual
environment. პროექტის root საქაღალდეში უნდა შეიქმნას `.venv`, გააქტიურდეს და
დაინსტალირდეს `requirements.txt`.

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Command Prompt:

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

## 15. გაშვების ბრძანებები

```powershell
python src\train_model.py
python src\evaluate_model.py
python src\model_comparison.py
python src\cross_validation.py
python src\feature_importance.py
streamlit run app\dashboard.py
```

სკრიპტები უნდა გაეშვას repository root-დან, რადგან ფაილების relative paths
ამ საქაღალდეს ეყრდნობა.

## 16. შეზღუდვები

- dataset მცირე და ხელოვნურად გამარტივებულია;
- მაღალი accuracy არ ნიშნავს production SOC-ში დადასტურებულ ეფექტიანობას;
- შეფასების sample მცირეა და მეტრიკები შეიძლება არასტაბილური იყოს;
- Feature Importance მხოლოდ გლობალური ახსნაა;
- MITRE ATT&CK Mapping წესებზე დაფუძნებული სასწავლო მექანიზმია;
- Risk Score-ის წონები რეალური SOC მონაცემებით არ არის კალიბრირებული;
- სისტემა არ არის ინტეგრირებული SIEM-თან;
- არ არსებობს authentication, persistent database ან production monitoring.

## 17. მომავალი გაუმჯობესებები

- CIC-IDS2017 ან UNSW-NB15 მონაცემებზე შეფასება;
- SHAP/LIME local explanation;
- FastAPI backend;
- რეალურ SIEM-თან ინტეგრაცია;
- analyst feedback loop;
- MITRE ATT&CK ტექნიკების გაფართოებული mapping;
- model drift monitoring და model versioning;
- რეალური აქტივის, მომხმარებლისა და ბიზნეს გავლენის კონტექსტი.

## 18. GitHub Repository Link

GitHub Repository:
[PASTE_GITHUB_LINK_HERE]
