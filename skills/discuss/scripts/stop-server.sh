#!/usr/bin/env bash
# Stop the discuss visual companion server and clean up
# Usage: stop-server.sh <session_dir>
#
# Kills the server process. Sessions are expected to live under /tmp,
# so stopping the server normally removes the temporary session directory.

SESSION_DIR="$1"

if [[ -z "$SESSION_DIR" ]]; then
  echo '{"error": "Usage: stop-server.sh <session_dir>"}'
  exit 1
fi

STATE_DIR="${SESSION_DIR}/state"
PID_FILE="${STATE_DIR}/server.pid"

if [[ -f "$PID_FILE" ]]; then
  pid=$(cat "$PID_FILE")

  # Try to stop gracefully, fallback to force if still alive
  kill "$pid" 2>/dev/null || true

  # Wait for graceful shutdown (up to ~2s)
  for i in {1..20}; do
    if ! kill -0 "$pid" 2>/dev/null; then
      break
    fi
    sleep 0.1
  done

  # If still running, escalate to SIGKILL
  if kill -0 "$pid" 2>/dev/null; then
    kill -9 "$pid" 2>/dev/null || true

    # Give SIGKILL a moment to take effect
    sleep 0.1
  fi

  if kill -0 "$pid" 2>/dev/null; then
    echo '{"status": "failed", "error": "process still running"}'
    exit 1
  fi

  rm -f "$PID_FILE" "${STATE_DIR}/server.log"

  cleanup="skipped"
  case "$SESSION_DIR" in
    /tmp/discuss-*)
      rm -rf "$SESSION_DIR"
      cleanup="removed"
      ;;
  esac

  echo "{\"status\": \"stopped\", \"cleanup\": \"$cleanup\"}"
else
  echo '{"status": "not_running"}'
fi
