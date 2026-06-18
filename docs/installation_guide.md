# ინსტალაციის სახელმძღვანელო

## 1. Python-ის ინსტალაცია

1. ჩამოტვირთეთ Python ოფიციალური საიტიდან.
2. ინსტალაციისას მონიშნეთ `Add Python to PATH`.
3. გახსენით PowerShell ან Command Prompt და შეამოწმეთ:

```powershell
python --version
pip --version
```

რეკომენდებულია Python 3.10 ან უფრო ახალი თავსებადი ვერსია.

## 2. პროექტის გახსნა VS Code-ში

1. დააინსტალირეთ Visual Studio Code.
2. გახსენით VS Code.
3. აირჩიეთ **File > Open Folder**.
4. მიუთითეთ `ai-soc-alert-assistant` საქაღალდე.
5. გახსენით **Terminal > New Terminal**.

ყველა ბრძანება შეასრულეთ პროექტის root საქაღალდიდან.

## 3. Virtual environment-ის შექმნა

```powershell
python -m venv .venv
```

ეს ბრძანება შექმნის იზოლირებულ Python გარემოს `.venv` საქაღალდეში.

## 4. Virtual environment-ის გააქტიურება

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

წარმატებული გააქტიურების შემდეგ terminal-ის დასაწყისში გამოჩნდება
`(.venv)`.

თუ PowerShell script execution დაბლოკილია, მიმდინარე მომხმარებლისთვის
შეასრულეთ:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

შემდეგ დახურეთ და თავიდან გახსენით terminal.

## 5. დამოკიდებულებების ინსტალაცია

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

შემოწმება:

```powershell
pip list
```

## 6. მოდელის გაწვრთნა

```powershell
python src\train_model.py
```

წარმატებული გაშვების შემდეგ უნდა არსებობდეს:

```text
models/ai_soc_model.pkl
models/features.pkl
```

## 7. შეფასების გაშვება

```powershell
python src\evaluate_model.py
python src\model_comparison.py
python src\cross_validation.py
python src\feature_importance.py
```

შედეგები შეინახება `reports/` საქაღალდეში.

## 8. Dashboard-ის გაშვება

```powershell
streamlit run app\dashboard.py
```

Streamlit terminal-ში დაბეჭდავს Local URL-ს.

## 9. localhost URL-ის გახსნა

ბრაუზერში გახსენით:

```text
http://localhost:8501
```

თუ ბრაუზერი ავტომატურად არ გაიხსნა, URL ხელით ჩაწერეთ.

Dashboard-ის გასაჩერებლად terminal-ში დააჭირეთ `Ctrl+C`.

## 10. გავრცელებული შეცდომები და გამოსწორება

### `python` ბრძანება ვერ მოიძებნა

- გადაამოწმეთ Python-ის ინსტალაცია.
- თავიდან დააინსტალირეთ და მონიშნეთ `Add Python to PATH`.
- სცადეთ `py --version` და საჭიროების შემთხვევაში `py -m venv .venv`.

### PowerShell არ რთავს Activate.ps1-ს

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

ან გამოიყენეთ Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

### `ModuleNotFoundError`

დარწმუნდით, რომ virtual environment გააქტიურებულია და გაუშვით:

```powershell
pip install -r requirements.txt
```

### Model file was not found

ჯერ გაწვრთენით მოდელი:

```powershell
python src\train_model.py
```

### CSV file is missing required columns

CSV უნდა შეიცავდეს მოდელის feature-ებს:

```text
duration, src_bytes, dst_bytes, packet_count, error_count
```

Training CSV-ს ასევე სჭირდება `label` სვეტი.

### Port 8501 დაკავებულია

```powershell
streamlit run app\dashboard.py --server.port 8502
```

შემდეგ გახსენით `http://localhost:8502`.

### ბრძანება გაეშვა არასწორი საქაღალდიდან

გადადით repository root-ში, სადაც `README.md`, `app/`, `src/` და
`requirements.txt` მდებარეობს, და ბრძანება თავიდან გაუშვით.
