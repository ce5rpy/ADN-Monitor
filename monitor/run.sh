#!/bin/bash
# Run the monitor from monitor/. Config: adn-mon.yaml in this folder or --config.
# Usage: ./run.sh [--config /path/to/adn-mon.yaml]

cd "$(dirname "$0")"
exec python3 monitor.py "$@"
