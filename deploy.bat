@echo off
REM ============================================================
REM  Wingato Open - push this project to your GitHub repo
REM  Run this AFTER you have created an EMPTY repo on github.com
REM ============================================================
cd /d "%~dp0"

where git >nul 2>nul
if errorlevel 1 (
    echo Git is not installed. Get it from https://git-scm.com/downloads
    pause
    exit /b 1
)

if not exist ".git" (
    git init
    git branch -M main
)

git add .
git commit -m "Wingato Open"

echo.
echo Paste your GitHub repo URL, e.g.
echo    https://github.com/yourname/wingato-open.git
echo.
set /p REMOTE=Repo URL: 

git remote remove origin 2>nul
git remote add origin %REMOTE%
git push -u origin main

echo.
echo If the push succeeded, go to render.com - New - Blueprint - pick this repo.
echo.
pause
