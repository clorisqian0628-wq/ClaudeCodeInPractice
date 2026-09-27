#!/bin/zsh
# Called by cron on weekday mornings. Runs the morning-brief skill headless.
cd "$(dirname "$0")"
mkdir -p logs
~/.local/bin/claude -p "Run the morning-brief skill." \
  --allowedTools "Skill" "Agent" "Read" "Write" \
    "Bash(.venv/bin/python -W ignore fetch.py)" \
    "Bash(.venv/bin/pip install -r requirements.txt)" \
    "Bash(date +%F)" \
  >> "logs/$(date +%F).log" 2>&1
