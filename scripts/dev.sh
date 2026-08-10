#!/usr/bin/env bash
# Local development launcher: starts the FastAPI backend and the Next.js frontend.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Prefer the project venv if it exists, otherwise fall back to system python.
PYBIN="$ROOT/backend/.venv/bin/python"
if [ ! -x "$PYBIN" ]; then
  PYBIN="$ROOT/backend/.venv/Scripts/python"  # Windows venv layout
fi
if [ ! -x "$PYBIN" ]; then
  PYBIN=python3
fi

# Start the backend in the background.
(cd "$ROOT/backend" && "$PYBIN" -m uvicorn app.main:app --host 0.0.0.0 --port 8000) &
BACKEND_PID=$!

cleanup() {
  echo
  echo "Shutting down..."
  kill "$BACKEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Start the frontend in the foreground (this is the exposed port).
cd "$ROOT/frontend"
npm run dev -- --port 3000
