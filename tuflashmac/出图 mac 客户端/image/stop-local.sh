#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$ROOT_DIR/.runtime/launcher.pid"
STATUS_FILE="$ROOT_DIR/.runtime/launcher-status.json"

if [[ -f "$PID_FILE" ]]; then
  PID="$(cat "$PID_FILE")"
else
  PID=""
fi

if [[ -n "$PID" ]] && kill -0 "$PID" >/dev/null 2>&1; then
  kill "$PID"
  echo "Stopped launcher process $PID"
else
  STREAMLIT_PID="$(lsof -ti tcp:8501 -sTCP:LISTEN || true)"
  if [[ -n "$STREAMLIT_PID" ]]; then
    kill "$STREAMLIT_PID"
    echo "Stopped Streamlit process $STREAMLIT_PID"
  else
    echo "No running launcher or Streamlit process found."
  fi
fi

rm -f "$PID_FILE" "$STATUS_FILE"
