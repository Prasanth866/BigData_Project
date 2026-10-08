#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo "Compiling Hadoop MapReduce Classes for Problem 1..."
echo "=========================================================="

mkdir -p build dist

# Locate Hadoop classpath
if command -v hadoop &> /dev/null; then
    HADOOP_CP="$(hadoop classpath)"
else
    echo "ERROR: 'hadoop' command not found in PATH."
    exit 1
fi

javac -classpath "$HADOOP_CP" -d build src/com/bigdata/mapreduce/*.java
jar cvf dist/most-visited-website.jar -C build/ .

echo "Compilation successful! Artifact created at: dist/most-visited-website.jar"
