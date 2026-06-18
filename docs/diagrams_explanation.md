# არქიტექტურის დიაგრამების განმარტება

## 1. სისტემის არქიტექტურის დიაგრამა

ფაილი: `diagrams/system_architecture.mmd`

დიაგრამა აჩვენებს მონაცემის მოძრაობას მომხმარებლის input-იდან SOC
ანალიტიკოსისთვის გამზადებულ შედეგამდე.

1. **CSV Data / Manual Input** - მონაცემი შემოდის CSV ფაილიდან ან dashboard-ის
   ხელით შევსებული ფორმიდან.
2. **Data Loader / Preprocessing** - მონაცემები მოწმდება, რიცხვითი feature-ები
   ლაგდება მოდელის საჭირო თანმიმდევრობით და გამოტოვებული მნიშვნელობები
   მუშავდება.
3. **ML Model** - Random Forest აბრუნებს BENIGN/ATTACK prediction-სა და კლასის
   ალბათობებს.
4. **Attack Probability** - ATTACK კლასის ალბათობა გამოიყენება რისკის
   გამოთვლაში.
5. **Risk Score Module** - attack probability-ს ემატება severity და asset
   criticality, რის შედეგადაც მიიღება 0-100 score და risk level.
6. **MITRE ATT&CK Mapping** - input feature-ების მარტივი წესებით განისაზღვრება
   სავარაუდო tactic, technique და mapping reason.
7. **Feature Importance** - Random Forest-ის გლობალური მნიშვნელობები აჩვენებს,
   რომელი feature-ები ახდენს ყველაზე დიდ გავლენას მოდელზე.
8. **Streamlit Dashboard** - ყველა შედეგი ერთიანდება მომხმარებლის ინტერფეისში.
9. **SOC Analyst** - ანალიტიკოსი კითხულობს შედეგს და იღებს საბოლოო
   გადაწყვეტილებას.

წყვეტილი კავშირები მიუთითებს, რომ prediction, risk level, mapping და
explainability dashboard-ში ცალკე output-ებადაც ჩანს.

## 2. Use Case დიაგრამა

ფაილი: `diagrams/use_case_diagram.mmd`

მთავარი actor არის **SOC Analyst**. იგი სისტემაში ასრულებს შემდეგ მოქმედებებს:

- ერთი ალერტის ხელით შემოწმება;
- CSV ფაილის ატვირთვა;
- prediction-ის ნახვა;
- Risk Score-ის ნახვა;
- MITRE ATT&CK Mapping-ის ნახვა;
- Feature Importance-ის ნახვა;
- Evaluation Reports-ის ნახვა.

Manual Alert Check და Upload CSV მოიცავს prediction-ისა და risk score-ის
გამოთვლას. Manual Alert Check ასევე აჩვენებს MITRE mapping-სა და response
guidance-ს. დიაგრამა ხაზს უსვამს human-in-the-loop მიდგომას: სისტემა ამზადებს
ინფორმაციას, მაგრამ საბოლოო ინციდენტის გადაწყვეტილებას SOC Analyst იღებს.

## Mermaid დიაგრამების გამოყენება

`.mmd` ფაილები შეიძლება გაიხსნას Mermaid Live Editor-ში ან VS Code Mermaid
preview extension-ით. ექსპორტირებული PNG/SVG ვერსიები შეიძლება ჩაისვას
საბაკალავრო ნაშრომის დანართში და პრეზენტაციაში.
