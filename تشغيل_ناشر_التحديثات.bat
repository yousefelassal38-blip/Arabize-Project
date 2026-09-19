@echo off
chcp 65001 >nul
cd /d "%~dp0Publisher"
where py >nul 2>nul
if errorlevel 1 (set "PY=python") else (set "PY=py -3")
%PY% -m pip install -r "..\Arabize_Data\requirements.txt" >nul
%PY% publisher.py
if errorlevel 1 pause
