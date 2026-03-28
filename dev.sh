#!/usr/bin/env bash
# dev.sh — Start both frontend and backend dev servers.
# Press Ctrl+C to stop both.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

(cd "$SCRIPT_DIR/backend" && uv run -m uvicorn evinha.main:app --port 8080 --reload) &
BACKEND_PID=$!

(cd "$SCRIPT_DIR/frontend" && mise exec -- npm run dev) &
FRONTEND_PID=$!

echo "Backend (PID $BACKEND_PID) on :8080, Frontend (PID $FRONTEND_PID) on :5173"
echo "Press Ctrl+C to stop both..."

cleanup() {
    echo "Stopping both servers..."
    kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null
    wait "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null
    echo "Both servers stopped."
}

trap cleanup INT TERM
wait "$BACKEND_PID" "$FRONTEND_PID"
