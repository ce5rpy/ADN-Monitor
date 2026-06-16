#!/bin/bash
# Run monitor.py from monitor/. Loads repo root .env inside Python if present.
# Usage: ./run.sh [--host HOST] [--port PORT]

cd "$(dirname "$0")"
exec python3 monitor.py "$@"
