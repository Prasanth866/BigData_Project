#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Suppress local loopback and JVM incubator warnings
export SPARK_LOCAL_IP="127.0.0.1"
export PYTHONWARNINGS="ignore"

echo "=========================================================="
echo "Executing Problem 2: SparkSQL Movie Ticket Booking"
echo "=========================================================="

if [ -f "$SCRIPT_DIR/../.venv/bin/python" ]; then
    "$SCRIPT_DIR/../.venv/bin/python" movie_booking_analysis.py 2> >(grep -v -E "incubator|log4j|NativeCodeLoader|Utils: Set SPARK_LOCAL_IP" >&2)
else
    python3 movie_booking_analysis.py 2> >(grep -v -E "incubator|log4j|NativeCodeLoader|Utils: Set SPARK_LOCAL_IP" >&2)
fi
