#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Starting Hatchr backend (FastAPI) on :8000..."
(
  cd "$ROOT_DIR/backend"
  # If uvicorn isn't on PATH, try python -m uvicorn
  if command -v uvicorn >/dev/null 2>&1; then
    uvicorn main:app --host 127.0.0.1 --port 8000 &
  else
    python3 -m uvicorn main:app --host 127.0.0.1 --port 8000 &
  fi
) 
BACK_PID=$!

trap 'echo "Shutting down..."; kill $BACK_PID 2>/dev/null || true' EXIT INT TERM

# Wait a moment and health check
sleep 2
if curl -sf http://127.0.0.1:8000/ >/dev/null; then
  echo "Backend OK at http://127.0.0.1:8000"
else
  echo "[WARN] Backend did not respond on :8000 (is Python deps installed?)."
  echo "Try:  cd backend && pip install -r requirements.txt"
fi

echo "Starting Hatchr frontend (Vite) on :3001..."
(
  cd "$ROOT_DIR/frontend2/Figmahatchr-main"
  npm run dev
)

