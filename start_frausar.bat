@echo off
chcp 65001 > nul
title FRAUSAR One-Click Starter

echo 🤖 FRAUSAR One-Click Starter
echo ==========================

REM Wechsle ins Skript-Verzeichnis
cd /d "%~dp0"

echo 📁 Arbeitsverzeichnis: %cd%

REM Prüfe ob Python verfügbar ist
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python gefunden
    python start_frausar_oneclick.py
) else (
    python3 --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Python3 gefunden  
        python3 start_frausar_oneclick.py
    ) else (
        echo ❌ Python nicht gefunden!
        echo Bitte installieren Sie Python3 von https://python.org
        echo.
        pause
        exit /b 1
    )
)

echo.
echo 🎉 FRAUSAR Setup abgeschlossen!
pause 