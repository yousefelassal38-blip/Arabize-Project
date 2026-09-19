@echo off
setlocal EnableExtensions
cd /d "%~dp0Arabize_Data"
where py >nul 2>nul
if errorlevel 1 (
 echo Python 3 is required.
 pause
 exit /b 1
)
py -3 -c "import customtkinter" >nul 2>nul
if errorlevel 1 py -3 -m pip install -r requirements.txt
py -3 launcher.py
if errorlevel 1 pause
