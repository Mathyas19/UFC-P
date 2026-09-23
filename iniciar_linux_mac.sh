#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if [ ! -x ".venv/bin/python" ]; then
  python3 -m venv .venv
fi
.venv/bin/python -m pip install -r requirements.txt

if [ ! -f ".env" ]; then
  read -r -s -p "Cole o token do bot e pressione Enter: " TOKEN
  echo
  printf 'DISCORD_TOKEN=%s\n' "$TOKEN" > .env
fi

.venv/bin/python bot.py
