#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

INPUT_FILE="${1:-input/web_traffic.txt}"

echo "=========================================================="
echo "Running Hadoop Streaming Simulation (UNIX Pipeline)"
echo "Input: $INPUT_FILE"
echo "=========================================================="

python3 scripts/mapper.py < "$INPUT_FILE" | sort | python3 scripts/reducer.py
