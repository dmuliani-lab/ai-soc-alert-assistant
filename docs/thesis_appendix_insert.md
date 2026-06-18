# საბაკალავრო ნაშრომში ჩასასმელი დანართები

## დანართი E. მომხმარებლის სახელმძღვანელო

AI-SOC Alert Assistant-ის მომხმარებლის ინტერფეისი შექმნილია Streamlit-ის
საშუალებით. სისტემის გასაშვებად პროექტის root საქაღალდეში აქტიურდება virtual
environment და სრულდება `streamlit run app/dashboard.py` ბრძანება.
Dashboard ხელმისაწვდომია `http://localhost:8501` მისამართზე.

მომხმარებელს შეუძლია ერთი ალერტის ხელით შემოწმება ან CSV ფაილის ატვირთვა.
ხელით შემოწმებისას ივსება `duration`, `src_bytes`, `dst_bytes`,
`packet_count` და `error_count`. სისტემა აჩვენებს BENIGN/ATTACK prediction-ს,
Attack Probability-ს, Risk Score-ს, Risk Level-ს, MITRE ATT&CK Mapping-სა და
საწყის response recommendations-ს.

CSV batch რეჟიმში იგივე ანალიზი სრულდება რამდენიმე ჩანაწერზე. შედეგების
ცხრილი იძლევა ალერტების პრიორიტეტების შედარების საშუალებას. Dashboard ასევე
აჩვენებს Feature Importance-ს, model comparison-ს, cross-validation-სა და
evaluation report-ს.

[ჩასასმელია Dashboard მთავარი გვერდის Screenshot]

[ჩასასმელია Manual Alert Check შედეგის Screenshot]

[ჩასასმელია CSV Upload შედეგის Screenshot]

## დანართი F. სისტემის არქიტექტურის დიაგრამები

სისტემის pipeline იწყება CSV ან ხელით შეყვანილი მონაცემით. Data Loader
ასრულებს მონაცემთა წინასწარ დამუშავებას, რის შემდეგაც Random Forest მოდელი
აბრუნებს კლასსა და შეტევის ალბათობას. Attack Probability გამოიყენება Risk
Score-ის გამოსათვლელად. შედეგს ემატება MITRE ATT&CK Mapping,
Feature Importance და incident-response რეკომენდაციები. საბოლოო ინფორმაცია
ერთიანდება Streamlit Dashboard-ში და გადაეცემა SOC ანალიტიკოსს.

Use Case დიაგრამაში მთავარი actor არის SOC Analyst. მისი ძირითადი მოქმედებებია
Manual Alert Check, Upload CSV, View Prediction, View Risk Score, View MITRE
ATT&CK Mapping, View Feature Importance და View Evaluation Reports.

[ჩასასმელია System Architecture Diagram]

[ჩასასმელია Use Case Diagram]

## დანართი G. ჩასაბარებელი ბმულები და მასალები

GitHub Repository:
[PASTE_GITHUB_LINK_HERE]

პროექტის ლოკალურად გაშვების ბრძანება:

```text
streamlit run app/dashboard.py
```

ძირითადი ფაილები:

- README.md
- requirements.txt
- app/dashboard.py
- src/train_model.py
- src/evaluate_model.py
- src/model_comparison.py
- src/cross_validation.py
- reports/metrics.txt
- reports/confusion_matrix.png
- reports/feature_importance.png

დამატებითი დოკუმენტაცია ხელმისაწვდომია `docs/` საქაღალდეში, ხოლო
საპრეზენტაციო მასალები - `presentation/` საქაღალდეში.
