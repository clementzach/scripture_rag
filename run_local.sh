#!/usr/bin/env bash
set -euo pipefail

# Simple helper to run the Flask app locally
# Creates a local venv (./.venv) if missing, installs deps, and starts the app.

PY=python3

if ! command -v ${PY} >/dev/null 2>&1; then
  echo "python3 not found on PATH" >&2
  exit 1
fi

if [ ! -d .venv ]; then
  echo "Creating virtual environment in .venv..."
  ${PY} -m venv .venv
fi

source .venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip >/dev/null
pip install -r requirements.txt

echo "Starting app on http://127.0.0.1:5000 ..."
exec ${PY} app.py

