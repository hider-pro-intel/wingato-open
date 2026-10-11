@echo off
REM Wingato Open - one-click launcher for Windows
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Python is not installed. Get it from https://www.python.org/downloads/
    echo Tick "Add Python to PATH" during install.
    pause
    exit /b 1
)

if not exist ".venv" python -m venv .venv
call .venv\Scripts\activate.bat
pip install -q -r requirements.txt

echo.
echo   Wingato Open is starting at:  http://127.0.0.1:5000
echo   Open that in your browser. Press Ctrl+C here to stop.
echo.
python app.py
pause
