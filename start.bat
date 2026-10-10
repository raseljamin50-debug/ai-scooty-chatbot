@echo off
REM ===== AI Scooty chatbot - Windows quick start =====
REM Double-click this file. First time it creates a virtual environment and installs everything.
cd /d "%~dp0"

REM >>> put the real customer support phone number here <<<
set SUPPORT_PHONE=+8801722222874

if not exist .venv (
  echo Creating virtual environment...
  py -3.13 -m venv .venv || python -m venv .venv
  call .venv\Scripts\activate.bat
  python -m pip install --upgrade pip
  pip install -r requirements.txt
) else (
  call .venv\Scripts\activate.bat
)

python tools\build_dataset.py
python run.py
pause
