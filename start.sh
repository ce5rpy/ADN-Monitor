#!/bin/bash
# Start the API (PHP only). Run the frontend separately (see README).
# Usage: ./start.sh

set -e
cd "$(dirname "$0")"

echo "API running at http://0.0.0.0:8080"
echo "Run the frontend in another terminal: cd frontend && npm run dev"
echo ""

exec php -S 0.0.0.0:8080 -t backend/public backend/public/router.php
