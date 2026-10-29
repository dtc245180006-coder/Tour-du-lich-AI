@echo off
chcp 65001 > nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Chay: py -m venv .venv
    echo Sau do: .venv\Scripts\python.exe -m pip install -r requirements-lock.txt
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -c "import fastapi, uvicorn, sqlalchemy" >nul 2>&1
if errorlevel 1 (
    echo Thieu thu vien. Chay: .venv\Scripts\python.exe -m pip install -r requirements-lock.txt
    pause
    exit /b 1
)
echo VietJourney AI: http://127.0.0.1:8000
echo Mo dia chi tren sau khi may chu bao Application startup complete.
".venv\Scripts\python.exe" -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
pause
