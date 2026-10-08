#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "================================================================================"
echo "          BIG DATA LAB ASSIGNMENT: AUTOMATED TEST & VERIFICATION SUITE         "
echo "================================================================================"

export SPARK_LOCAL_IP="127.0.0.1"
export PYTHONWARNINGS="ignore"

echo ""
echo ">>> [1/3] Executing Problem 1: Hadoop MapReduce (Most Visited Website)..."
echo "--------------------------------------------------------------------------------"
cd "$ROOT_DIR/problem1_mapreduce"
./run_hadoop.sh

echo ""
echo ">>> [2/3] Executing Problem 2: Spark SQL (Movie Ticket Booking)..."
echo "--------------------------------------------------------------------------------"
cd "$ROOT_DIR/problem2_sparksql"
./run.sh

echo ""
echo ">>> [3/3] Executing Problem 3: RDF/RDFS Semantic Knowledge Base (Museum)..."
echo "--------------------------------------------------------------------------------"
cd "$ROOT_DIR/problem3_rdf_museum"
./run.sh

echo ""
echo "================================================================================"
echo "          ALL THREE PROBLEMS EXECUTED AND VERIFIED SUCCESSFULLY!                "
echo "================================================================================"
