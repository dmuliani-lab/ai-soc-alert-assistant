# Live Demo სცენარი

## მიზანი და ხანგრძლივობა

სავარაუდო ხანგრძლივობა: **10-15 წუთი**.

მიზანია მოკლედ აჩვენოთ repository, გაშვების პროცესი, ერთი ალერტის ანალიზი,
CSV batch, explainability და კვლევითი ანგარიშები. დემოს დროს მუდმივად
აღნიშნეთ, რომ სისტემა არის საბაკალავრო პროტოტიპი და არა production SOC
პლატფორმა.

## 1. GitHub repository-ის გახსნა - 1 წუთი

- გახსენით repository-ის მთავარი გვერდი.
- აჩვენეთ პროექტის სახელი და ბოლო commit-ები.
- მოკლედ თქვით, რომ repository შეიცავს source code-ს, model artifacts-ს,
  reports-ს, documentation-სა და presentation draft-ს.

## 2. README-ის ჩვენება - 1 წუთი

- აჩვენეთ პროექტის აღწერა.
- ჩამოთვალეთ მთავარი ფუნქციები.
- მიუთითეთ installation და run ბრძანებები.
- აჩვენეთ limitations და future work.

## 3. პროექტის სტრუქტურა - 1 წუთი

აჩვენეთ:

- `app/` - dashboard;
- `src/` - ML და decision-support ლოგიკა;
- `data/` - sample dataset;
- `models/` - გაწვრთნილი model artifacts;
- `reports/` - კვლევითი შედეგები;
- `docs/`, `diagrams/`, `presentation/` - ჩასაბარებელი მასალები.

## 4. Virtual environment-ის გააქტიურება

```powershell
.\.venv\Scripts\Activate.ps1
```

თუ გარემო უკვე აქტიურია, აუდიტორიას აუხსენით `(.venv)` ინდიკატორი.

## 5. Dashboard-ის გაშვება - 1 წუთი

```powershell
streamlit run app\dashboard.py
```

გახსენით:

```text
http://localhost:8501
```

## 6. Manual suspicious alert check - 2 წუთი

შეიყვანეთ მაღალი რისკის მაგალითი:

```text
duration: 13
src_bytes: 13000
dst_bytes: 160
packet_count: 110
error_count: 17
```

დააჭირეთ **Run Threat Scan**.

## 7. Attack Probability-ის განმარტება

- აჩვენეთ BENIGN/ATTACK prediction.
- ახსენით, რომ probability მოდელის confidence-ის მსგავსი output-ია, მაგრამ
  არ არის ინციდენტის უტყუარი დადასტურება.
- მიუთითეთ, რომ საბოლოო გადაწყვეტილებას ანალიტიკოსი იღებს.

## 8. Risk Score-ის განმარტება

- აჩვენეთ gauge და risk level.
- ახსენით, რომ score აერთიანებს attack probability-ს, severity-ს და asset
  criticality-ს.
- აღნიშნეთ, რომ მიმდინარე წონები სასწავლოა.

## 9. MITRE ATT&CK Mapping-ის განმარტება

- აჩვენეთ tactic, technique და rationale.
- განმარტეთ, რომ mapping წესებზე დაფუძნებული სასწავლო მოდულია.
- მიუთითეთ incident-response recommendations.

## 10. CSV ფაილის ატვირთვა - 2 წუთი

- გამოიყენეთ **Load Sample Dataset** ან ატვირთეთ `data/sample_alerts.csv`.
- აჩვენეთ ATTACK, Critical, High, Medium და Low counters.

## 11. მრავალი ალერტის შედეგები

- დაალაგეთ ან გადაათვალიერეთ analysis table.
- აჩვენეთ prediction, probability, score, risk level და MITRE fields.
- გახსენით ერთი MITRE Mapping Notes expander.

## 12. Feature Importance - 1 წუთი

- გადადით Feature Importance სექციაში.
- აჩვენეთ top feature, ცხრილი და bar chart.
- ახსენით განსხვავება global Feature Importance-სა და მომავალ SHAP/LIME
  local explanation-ს შორის.

## 13. Reports საქაღალდე - 1 წუთი

აჩვენეთ `reports/` და გაუშვით საჭიროების შემთხვევაში:

```powershell
python src\evaluate_model.py
python src\model_comparison.py
python src\cross_validation.py
```

## 14. Confusion Matrix

- გახსენით `reports/confusion_matrix.png`.
- ახსენით True Positive, True Negative, False Positive და False Negative.
- ხაზი გაუსვით Recall-ისა და False Negative-ის მნიშვნელობას SOC-ში.

## 15. შეზღუდვები - 1 წუთი

- dataset მცირე და გამარტივებულია;
- მაღალი accuracy demonstration result-ია;
- MITRE mapping და Risk Score production დონეზე არ არის დაკალიბრებული;
- საჭიროა CIC-IDS2017 ან UNSW-NB15-ზე შეფასება.

## 16. მომავალი სამუშაო და დასრულება - 1 წუთი

დაასრულეთ შემდეგი მიმართულებებით:

- larger dataset;
- SHAP/LIME;
- FastAPI;
- SIEM integration;
- analyst feedback loop;
- improved MITRE ATT&CK mapping.

ბოლო წინადადება:

> AI-SOC Alert Assistant აჩვენებს, როგორ შეიძლება მანქანური სწავლების,
> რისკის პრიორიტეტიზაციისა და explainability-ის გაერთიანება SOC ანალიტიკოსის
> მხარდასაჭერად, human-in-the-loop პრინციპის დაცვით.

## დემომდე მოსამზადებელი ბრძანებები

```powershell
.\.venv\Scripts\Activate.ps1
python src\train_model.py
python src\evaluate_model.py
python src\model_comparison.py
python src\cross_validation.py
streamlit run app\dashboard.py
```
