# მომხმარებლის სახელმძღვანელო

## 1. Dashboard-ის გახსნა

გახსენით terminal პროექტის root საქაღალდეში, გააქტიურეთ virtual environment
და გაუშვით:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app\dashboard.py
```

ბრაუზერში გახსენით `http://localhost:8501`.

[ჩასასმელია Screenshot 1: Dashboard მთავარი გვერდი]

## 2. ერთი ალერტის ხელით შემოწმება

1. გადადით **Manual Alert Scan** სექციაში.
2. შეიყვანეთ `duration`, `src_bytes`, `dst_bytes`, `packet_count` და
   `error_count`.
3. დააჭირეთ **Run Threat Scan** ღილაკს.
4. დაელოდეთ prediction-ისა და Risk Score-ის გამოჩენას.

ხელით შეყვანილი მნიშვნელობები უნდა იყოს არაუარყოფითი რიცხვები.

[ჩასასმელია Screenshot 2: Manual Alert Check შედეგი]

## 3. CSV ფაილის ატვირთვა

1. გადადით **CSV Batch Analysis** სექციაში.
2. აირჩიეთ CSV ფაილი ან დააჭირეთ **Load Sample Dataset**.
3. CSV უნდა შეიცავდეს საჭირო feature სვეტებს.
4. ატვირთვის შემდეგ სისტემა დაამუშავებს ყველა ჩანაწერს.
5. ეკრანზე გამოჩნდება alert summary და დეტალური ცხრილი.

აუცილებელი სვეტებია:

```text
duration, src_bytes, dst_bytes, packet_count, error_count
```

[ჩასასმელია Screenshot 3: CSV Upload შედეგი]

## 4. შედეგების წაკითხვა

ძირითადი output ველებია:

- **Prediction** - `BENIGN` ან `ATTACK`;
- **Attack Probability** - მოდელის მიერ შეფასებული შეტევის ალბათობა;
- **Risk Score** - 0-100 დიაპაზონის პრიორიტეტიზაციის მაჩვენებელი;
- **Risk Level** - Low, Medium, High ან Critical;
- **MITRE Tactic/Technique** - სასწავლო mapping;
- **Detection Rationale** - mapping-ის მიზეზი;
- **Response Guidance** - საწყისი რეაგირების რეკომენდაციები.

შედეგი არის გადაწყვეტილების მხარდაჭერა. საბოლოო შეფასება ანალიტიკოსმა უნდა
გააკეთოს დამატებითი logs-ისა და ორგანიზაციული კონტექსტის საფუძველზე.

## 5. Risk Score-ის მნიშვნელობა

Risk Score აერთიანებს Attack Probability-ს, Severity-ს და Asset Criticality-ს.
მაღალი score ნიშნავს, რომ ალერტს უფრო სწრაფი ანალიტიკური ყურადღება სჭირდება.
იგი არ არის ინციდენტის ავტომატური დადასტურება.

## 6. Risk Level-ის განმარტება

- **Low** - დაბალი პრიორიტეტი; საჭიროა ჩვეულებრივი მონიტორინგი.
- **Medium** - საჭიროა დამატებითი კონტექსტის შემოწმება.
- **High** - რეკომენდებულია სწრაფი განხილვა და შესაძლო escalation.
- **Critical** - რეკომენდებულია დაუყოვნებლივი განხილვა.

დონეები ეფუძნება პროტოტიპის threshold-ებს და რეალურ ორგანიზაციაში უნდა
დარეგულირდეს.

## 7. MITRE ATT&CK Mapping-ის ნახვა

Manual Alert Scan-ის შედეგებში ჩანს tactic, technique და mapping reason.
CSV შედეგებში შესაბამისი ველები მოთავსებულია ცხრილში, ხოლო პირველი რამდენიმე
ალერტისთვის დამატებითი განმარტება ჩანს expander-ებში.

Mapping არის წესებზე დაფუძნებული სასწავლო მექანიზმი და არა სრული MITRE ATT&CK
coverage.

## 8. Feature Importance-ის ნახვა

გადადით **Feature Importance** სექციაში. აქ ჩანს:

- ყველაზე მნიშვნელოვანი feature;
- feature-ების ცხრილი;
- მნიშვნელობების bar chart;
- მოდელის გლობალური ახსნადობის მოკლე განმარტება.

[ჩასასმელია Screenshot 4: Feature Importance გრაფიკი]

## 9. Evaluation Reports-ის ნახვა

Dashboard-ის **Research Results** სექცია აჩვენებს:

- Model Comparison-ის ცხრილს;
- Stratified K-Fold Cross-Validation-ის შედეგებს;
- Evaluation Report-ის ტექსტს.

სრული ფაილები ხელმისაწვდომია `reports/` საქაღალდეში.

[ჩასასმელია Screenshot 5: Confusion Matrix]

## 10. სისტემის შეზღუდვები

- dataset მცირე და გამარტივებულია;
- მაღალი accuracy მხოლოდ demonstration result-ია;
- MITRE mapping წესებზეა დაფუძნებული;
- Feature Importance არის გლობალური და არა კონკრეტული ალერტის ახსნა;
- Risk Score-ის წონები რეალური SOC მონაცემებით არ არის კალიბრირებული;
- სისტემა არ ასრულებს ავტომატურ block/isolation მოქმედებებს;
- production გამოყენებამდე საჭიროა უფრო დიდი dataset, უსაფრთხოების ტესტირება,
  SIEM integration და analyst validation.
