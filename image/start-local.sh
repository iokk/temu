#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
PYTHON_BIN="$VENV_DIR/bin/python"
PIP_BIN="$VENV_DIR/bin/pip"
PORT="${STREAMLIT_PORT:-8501}"
URL="http://127.0.0.1:${PORT}"

if command -v python3.12 >/dev/null 2>&1; then
  SYSTEM_PYTHON="python3.12"
else
  SYSTEM_PYTHON="python3"
fi

open_browser() {
  if command -v open >/dev/null 2>&1; then
    open "$URL"
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$URL" >/dev/null 2>&1 &
  fi
}

if [[ ! -d "$VENV_DIR" ]]; then
  "$SYSTEM_PYTHON" -m venv "$VENV_DIR"
fi

if [[ ! -x "$VENV_DIR/bin/streamlit" ]]; then
  "$PIP_BIN" install --upgrade pip
  "$PIP_BIN" install -r "$ROOT_DIR/requirements.txt"
fi

if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Streamlit is already running at $URL"
  open_browser
  exit 0
fi

exec "$PYTHON_BIN" "$ROOT_DIR/heartbeat_launcher.py"
