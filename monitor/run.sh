#!/bin/bash
# Run the monitor from monitor/. Config: adn-monitor.yaml in this folder or ADN_CONFIG_PATH.
# Loads .env from project root if present (same as backend/frontend).
# Usage: ./run.sh [--config /path/to/adn-monitor.yaml]

cd "$(dirname "$0")"
ROOT_ENV="$(dirname "$0")/../.env"
if [ -f "$ROOT_ENV" ]; then
  set -a
  # shellcheck source=/dev/null
  . "$ROOT_ENV"
  set +a
fi
exec python3 monitor.py "$@"
