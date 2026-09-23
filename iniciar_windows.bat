@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt

if not exist ".env" (
    set /p "TOKEN=Cole o token do bot e pressione Enter: "
    >.env echo DISCORD_TOKEN=%TOKEN%
)

.venv\Scripts\python.exe bot.py
pause
