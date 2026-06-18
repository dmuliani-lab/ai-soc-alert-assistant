# AI-SOC Alert Assistant - პრეზენტაციის მონახაზი

## სლაიდი 1 - AI-SOC Alert Assistant

- საბაკალავრო ნაშრომის პრაქტიკული პროტოტიპი
- მანქანური სწავლება SOC ალერტების პირველადი triage-ისთვის
- ავტორი: დავით მულიანი
- ტექნოლოგია: Python, Scikit-learn, Streamlit

**Speaker notes:**  
წარადგინეთ პროექტის სახელი და მოკლედ ახსენით, რომ მიზანია SOC ანალიტიკოსის
დახმარება ალერტების კლასიფიკაციაში, პრიორიტეტიზაციასა და ახსნადობაში. ხაზი
გაუსვით, რომ სისტემა არის საბაკალავრო პროტოტიპი და human-in-the-loop მიდგომას
იყენებს.

## სლაიდი 2 - პრობლემა: SOC Alert Fatigue

- SOC სისტემები ყოველდღიურად დიდი რაოდენობის ალერტს ქმნის
- ბევრი ალერტი false positive ან დაბალი პრიორიტეტისაა
- ანალიტიკოსის დრო იხარჯება ხელით triage-ზე
- კრიტიკული ალერტის დაგვიანება ზრდის უსაფრთხოების რისკს

**Speaker notes:**  
განმარტეთ alert fatigue-ის პრობლემა: მოცულობა, განმეორებადი შემოწმება და
პრიორიტეტიზაციის სირთულე. AI არ ცვლის ანალიტიკოსს, მაგრამ შეუძლია საწყისი
ფილტრაციისა და კონტექსტის მიწოდება.

## სლაიდი 3 - პროექტის მიზანი

- BENIGN/ATTACK კლასიფიკაციის დემონსტრირება
- Attack Probability და Risk Score
- MITRE ATT&CK კონტექსტის დამატება
- Explainable AI / Feature Importance
- ერთი ალერტისა და CSV batch-ის dashboard

**Speaker notes:**  
ჩამოაყალიბეთ პროექტის მიზანი როგორც გადაწყვეტილების მხარდაჭერის სისტემა.
აღნიშნეთ, რომ output მოიცავს prediction-ს, რისკს, mapping-სა და საწყის
რეაგირების რეკომენდაციებს.

## სლაიდი 4 - სისტემის არქიტექტურა

- CSV Data / Manual Input
- Data Loader და Preprocessing
- Random Forest ML Model
- Risk Score, MITRE Mapping, Feature Importance
- Streamlit Dashboard და SOC Analyst

[ჩასასმელია System Architecture Diagram]

**Speaker notes:**  
გაატარეთ აუდიტორია pipeline-ის მიხედვით input-იდან dashboard-მდე. ახსენით,
რომ საბოლოო გადაწყვეტილება ანალიტიკოსთან რჩება.

## სლაიდი 5 - გამოყენებული ტექნოლოგიები

- Python
- Pandas და NumPy
- Scikit-learn
- Matplotlib და Altair
- Joblib და Streamlit

**Speaker notes:**  
მოკლედ აღწერეთ თითოეული ტექნოლოგიის ფუნქცია: მონაცემები, მოდელი, გრაფიკები,
model persistence და UI. აღნიშნეთ, რომ stack შერჩეულია პროტოტიპის სიმარტივისა
და reproducibility-ისთვის.

## სლაიდი 6 - ML Pipeline

- CSV მონაცემების ჩატვირთვა
- Label-ის გარდაქმნა: BENIGN=0, ATTACK=1
- რიცხვითი feature-ების გაწმენდა
- Stratified train/test split
- Random Forest training და model artifacts

**Speaker notes:**  
ახსენით `data_loader.py` და `train_model.py`. ჩამოთვალეთ მიმდინარე feature-ები:
duration, src_bytes, dst_bytes, packet_count, error_count. მიუთითეთ, რომ model
და feature order ინახება `models/` საქაღალდეში.

## სლაიდი 7 - Risk Score

- Attack Probability - 55%
- Severity - 25%
- Asset Criticality - 20%
- დონეები: Low, Medium, High, Critical
- მიზანი: ალერტების პრიორიტეტიზაცია

```text
Risk Score = (0.55P + 0.25S + 0.20A) × 100
```

**Speaker notes:**  
განმარტეთ ფორმულა და threshold-ები. აღნიშნეთ, რომ წონები სასწავლოა და რეალურ
SOC-ში ისტორიული ინციდენტებითა და analyst feedback-ით უნდა დაკალიბრდეს.

## სლაიდი 8 - MITRE ATT&CK Mapping

- წესებზე დაფუძნებული სასწავლო mapping
- Impact / DoS-DDoS-like behavior
- Credential Access / Brute Force-like behavior
- Command and Control / persistent communication
- Unknown შემთხვევაში საჭიროა Analyst Review

**Speaker notes:**  
აჩვენეთ, როგორ ემატება model prediction-ს ოპერაციული კონტექსტი. მკაფიოდ
თქვით, რომ ეს არ არის სრული threat intelligence ან production detection
engine.

## სლაიდი 9 - Explainable AI / Feature Importance

- Random Forest-ის გლობალური feature importance
- ყველაზე გავლენიანი input field-ების ranking
- black-box რისკის შემცირება
- analyst trust და შედეგის ინტერპრეტაცია
- მომავალი: SHAP/LIME local explanation

[ჩასასმელია Feature Importance Screenshot]

**Speaker notes:**  
განასხვავეთ global და local explanation. მიმდინარე პროტოტიპი აღწერს მოდელის
საერთო ქცევას; კონკრეტული ალერტის ზუსტი ახსნისთვის საჭიროა SHAP ან LIME.

## სლაიდი 10 - შეფასების შედეგები

- Accuracy, Precision, Recall და F1-score
- Confusion Matrix
- ოთხი მოდელის შედარება
- Stratified K-Fold Cross-Validation
- შედეგების ინტერპრეტაცია შეზღუდვებთან ერთად

[ჩასასმელია Confusion Matrix Screenshot]

**Speaker notes:**  
აჩვენეთ რეალური reports ფაილებიდან მიღებული შედეგები. განსაკუთრებით ახსენით
Recall და False Negative. მაღალი accuracy არ წარმოადგინოთ production proof-ად,
რადგან dataset მცირეა.

## სლაიდი 11 - Dashboard Demo

- Manual Alert Scan
- Attack Probability და Risk gauge
- MITRE ATT&CK და response guidance
- CSV Batch Analysis
- Feature Importance და Research Results

[ჩასასმელია Dashboard Screenshot]

**Speaker notes:**  
გადადით live demo-ზე. ჯერ გაუშვით ერთი საეჭვო ალერტი, შემდეგ sample CSV.
აჩვენეთ risk score, mapping, multiple alert table და reports.

## სლაიდი 12 - შეზღუდვები და მომავალი სამუშაო

- მცირე და გამარტივებული dataset
- CIC-IDS2017 / UNSW-NB15-ზე შეფასება
- SHAP/LIME local explanation
- FastAPI და SIEM integration
- Analyst feedback loop და გაუმჯობესებული MITRE mapping

**Speaker notes:**  
დაასრულეთ რეალისტური შეზღუდვებით. მთავარი დასკვნაა, რომ პროექტი აჩვენებს
AI-ის, Risk Score-ის, MITRE ATT&CK-ისა და explainability-ის ერთიან გამოყენებას
SOC triage-ის მხარდასაჭერად, თუმცა production დანერგვას დამატებითი მონაცემები,
ტესტირება და უსაფრთხოების კონტროლები სჭირდება.
