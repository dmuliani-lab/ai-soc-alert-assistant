# Git და GitHub-ზე ჩაბარების ინსტრუქცია

## 1. Git repository-ის ინიციალიზაცია

პროექტის root საქაღალდეში:

```powershell
git init
```

თუ `.git` უკვე არსებობს, ეს ნაბიჯი აღარ არის საჭირო.

## 2. ფაილების დამატება

ჯერ გადაამოწმეთ:

```powershell
git status
```

შემდეგ დაამატეთ ფაილები:

```powershell
git add .
```

დარწმუნდით, რომ `.venv/`, logs და სხვა დროებითი ფაილები არ დაემატა.

## 3. მნიშვნელოვანი commit-ის შექმნა

```powershell
git commit -m "Initial AI-SOC project submission package"
```

Commit message მოკლედ უნდა აღწერდეს ცვლილებას. სასურველია რამდენიმე
ლოგიკური commit და არა ერთი გაურკვეველი commit.

## 4. GitHub repository-ის შექმნა

1. შედით GitHub-ზე.
2. აირჩიეთ **New repository**.
3. მიუთითეთ repository name, მაგალითად `ai-soc-alert-assistant`.
4. აირჩიეთ შესაბამისი visibility ლექტორის მოთხოვნის მიხედვით.
5. არ დაამატოთ ახალი README, თუ ადგილობრივ პროექტში უკვე არსებობს.
6. შექმენით repository.

## 5. Remote repository-ს დაკავშირება

```powershell
git branch -M main
git remote add origin PASTE_GITHUB_REPOSITORY_URL_HERE
```

URL ჩაანაცვლეთ თქვენი რეალური repository URL-ით.

შემოწმება:

```powershell
git remote -v
```

## 6. GitHub-ზე ატვირთვა

```powershell
git push -u origin main
```

GitHub-მა შეიძლება მოგთხოვოთ browser authentication ან Personal Access Token.
არ შეინახოთ token source code-ში.

## 7. Repository link-ის შემოწმება

1. გახსენით repository სხვა browser tab-ში.
2. შეამოწმეთ README rendering.
3. გახსენით `app/`, `src/`, `docs/`, `reports/` და `presentation/`.
4. შეამოწმეთ commit history.
5. დარწმუნდით, რომ model/report ფაილები მოთხოვნის შესაბამისად ჩანს.

## 8. GitHub link-ის Word ნაშრომში ჩასმა

დააკოპირეთ repository-ის მთავარი URL და ჩასვით:

- ნაშრომის შესაბამის დანართში;
- `GitHub Repository` ველში;
- საჭიროების შემთხვევაში პრეზენტაციის ბოლო სლაიდზე.

არ დატოვოთ `[PASTE_GITHUB_LINK_HERE]` placeholder საბოლოო ვერსიაში.

## რეკომენდებული დამატებითი commit-ები

```powershell
git add README.md docs/
git commit -m "Add technical documentation and user manual"

git add presentation/ diagrams/ screenshots/
git commit -m "Add presentation draft and project diagrams"
```

შემდეგ:

```powershell
git push
```

## სრული საწყისი ბრძანებების ბლოკი

```powershell
git init
git add .
git commit -m "Initial AI-SOC project submission package"
git branch -M main
git remote add origin PASTE_GITHUB_REPOSITORY_URL_HERE
git push -u origin main
```
