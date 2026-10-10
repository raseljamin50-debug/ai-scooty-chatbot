#!/usr/bin/env bash
# AI Scooty chatbot - Linux / macOS quick start
cd "$(dirname "$0")"
export SUPPORT_PHONE="${SUPPORT_PHONE:-+880-XXXX-XXXXXX}"   # put the real support number here
if [ ! -d .venv ]; then
  python3.13 -m venv .venv 2>/dev/null || python3 -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
else
  source .venv/bin/activate
fi
python tools/build_dataset.py
python run.py
