#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo "Executing Problem 3: RDF Museum Management Validation"
echo "=========================================================="

if [ -f "$SCRIPT_DIR/../.venv/bin/python" ]; then
    "$SCRIPT_DIR/../.venv/bin/python" validate_and_query.py
else
    python3 validate_and_query.py
fi
