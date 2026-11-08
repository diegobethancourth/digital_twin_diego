@echo off
rem Starts the digital twin server and opens the browser
cd /d "%~dp0"
where py >nul 2>nul && (set PY=py) || (set PY=python)
start "" /b powershell -NoProfile -Command "Start-Sleep 2; Start-Process 'http://localhost:8000/?device=Mazak'"
%PY% serve.py
pause
