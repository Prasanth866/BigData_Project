#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

INPUT_FILE="${1:-input/web_traffic.txt}"
OUTPUT_DIR="${2:-output/hadoop_result}"

if [ ! -f "dist/most-visited-website.jar" ]; then
    echo "JAR not found. Compiling first..."
    ./compile.sh
fi

echo "=========================================================="
echo "Running Hadoop MapReduce: Most Visited Website"
echo "Input:  $INPUT_FILE"
echo "Output: $OUTPUT_DIR"
echo "=========================================================="

rm -rf "$OUTPUT_DIR"

hadoop jar dist/most-visited-website.jar com.bigdata.mapreduce.MostVisitedWebsite \
  -Dfs.defaultFS=file:/// \
  -Dmapreduce.framework.name=local \
  "$INPUT_FILE" "$OUTPUT_DIR"

echo ""
echo "=========================================================="
echo "Job Output (part-r-00000):"
echo "=========================================================="
cat "$OUTPUT_DIR"/part-r-00000
