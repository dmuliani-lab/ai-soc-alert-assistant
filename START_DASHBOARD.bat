@echo off
cd /d "%~dp0"
start "" "http://localhost:8088/dashboard.html"
.\.venv\Scripts\python.exe -m http.server 8088 --directory app
pause
