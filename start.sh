#!/bin/bash
# Start unified monitor API from repo root.
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT/monitor"
exec python3 monitor.py "$@"
