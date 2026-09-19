@echo off
chcp 65001 >nul
cd /d "%~dp0Arabize_Data"
where py >nul 2>nul
if errorlevel 1 (set "PY=python") else (set "PY=py -3")
%PY% -c "import customtkinter,cryptography" >nul 2>nul
if errorlevel 1 %PY% -m pip install -r requirements.txt
%PY% launcher.py
if errorlevel 1 pause
