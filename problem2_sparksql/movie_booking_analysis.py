#!/usr/bin/env python3
"""
Problem #2: SparkSQL - Movie Ticket Booking Analysis
=====================================================
Tasks:
  1. Identify bookings containing more than two tickets.
  2. Detect duplicate Booking IDs using a Bloom Filter.
  3. Create a DataFrame containing unique bookings.
  4. Find the total number of tickets sold for each movie.
  5. Calculate total revenue for each movie.
  6. Use Spark SQL to find the highest-revenue movie.
"""

import os
import sys
import math
import hashlib
from pathlib import Path

# Ensure worker processes use the current Python interpreter
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum, count, desc
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType


class CustomBloomFilter:
    """
    In-memory Bloom Filter implementation to demonstrate the exact
    probabilistic data structure mechanics alongside Spark's native BloomFilter.
    
    Mathematical Specifications:
      - Optimal bit array size: m = - (n * ln(p)) / (ln(2)^2)
      - Optimal hash functions: k = (m / n) * ln(2)
      - Double hashing scheme: g_i(x) = (h1(x) + i * h2(x)) mod m
    """
    def __init__(self, expected_items: int = 1000, false_positive_rate: float = 0.01):
        self.n = max(expected_items, 1)
        self.p = false_positive_rate
        # Calculate optimal m and k
        self.m = int(- (self.n * math.log(self.p)) / (math.log(2) ** 2))
        self.k = max(1, int((self.m / self.n) * math.log(2)))
        self.bit_array = [0] * self.m

    def _hashes(self, item: str):
        # Generate k independent hash values using double hashing (Kirsch-Mitzenmacher technique)
        h1 = int(hashlib.md5(item.encode('utf-8')).hexdigest(), 16)
        h2 = int(hashlib.sha256(item.encode('utf-8')).hexdigest(), 16)
        for i in range(self.k):
            yield (h1 + i * h2) % self.m

    def add(self, item: str):
        for bit_index in self._hashes(item):
            self.bit_array[bit_index] = 1

    def might_contain(self, item: str) -> bool:
        return all(self.bit_array[bit_index] == 1 for bit_index in self._hashes(item))


def main():
    script_dir = Path(__file__).resolve().parent
    data_path = script_dir / "data" / "movie_bookings.csv"

    if not data_path.exists():
        print(f"Error: Data file not found at {data_path}")
        sys.exit(1)

    print("=" * 80)
    print("         SPARK SQL: MOVIE TICKET BOOKING SYSTEM ANALYSIS")
    print("=" * 80)

    # Initialize SparkSession
    spark = SparkSession.builder \
        .appName("MovieTicketBookingAnalysis") \
        .master("local[*]") \
        .config("spark.ui.enabled", "false") \
        .config("spark.sql.shuffle.partitions", "2") \
        .getOrCreate()

    # Set log level to WARN
    spark.sparkContext.setLogLevel("WARN")

    # Define schema explicitly
    schema = StructType([
        StructField("Booking_ID", StringType(), False),
        StructField("Customer_ID", StringType(), False),
        StructField("Movie", StringType(), False),
        StructField("Theatre", StringType(), False),
        StructField("Tickets", IntegerType(), False),
        StructField("Amount", DoubleType(), False),
    ])

    print(f"\n[INFO] Loading dataset from: {data_path.name}")
    raw_df = spark.read \
        .option("header", "true") \
        .schema(schema) \
        .csv(str(data_path))

    print(f"\n--- Ingested Raw Bookings (Total Records: {raw_df.count()}) ---")
    raw_df.show(truncate=False)

    # =========================================================================
    # TASK 1: Identify bookings containing more than two tickets
    # =========================================================================
    print("=" * 80)
    print("TASK 1: Bookings Containing More Than Two Tickets (Tickets > 2)")
    print("=" * 80)
    df_more_than_2 = raw_df.filter(col("Tickets") > 2)
    print(f"Found {df_more_than_2.count()} bookings with Tickets > 2:")
    df_more_than_2.show(truncate=False)

    # =========================================================================
    # TASK 2: Detect duplicate Booking IDs using a Bloom Filter
    # =========================================================================
    print("=" * 80)
    print("TASK 2: Detect Duplicate Booking IDs Using a Bloom Filter")
    print("=" * 80)
    
    # Method 2.A: Apache Spark native Sketch BloomFilter (org.apache.spark.util.sketch.BloomFilter)
    spark_bf = raw_df._jdf.stat().bloomFilter("Booking_ID", 1000, 0.01)
    print(f"-> Spark Native Bloom Filter constructed:")
    print(f"   - Class: {spark_bf.getClass().getName()}")
    print(f"   - Bit size (m): {spark_bf.bitSize()} bits")
    print(f"   - Expected Items (n): 1000, False Positive Probability (p): 0.01")
    print(f"   - Membership check 'B101': {spark_bf.mightContain('B101')}")
    print(f"   - Membership check 'NONEXISTENT_KEY': {spark_bf.mightContain('NONEXISTENT_KEY')}")

    # Method 2.B: Duplicate Detection Stream using Bloom Filter
    # As bookings stream in, query Bloom Filter: if might_contain is true, it is flagged as duplicate!
    bloom_filter = CustomBloomFilter(expected_items=1000, false_positive_rate=0.01)
    rows = raw_df.collect()

    flagged_duplicates = []
    seen_ids = set()

    print(f"\n-> Streaming records through Bloom Filter to intercept duplicates:")
    for row in rows:
        b_id = row["Booking_ID"]
        if bloom_filter.might_contain(b_id):
            # Bloom filter flagged this key as already observed
            flagged_duplicates.append(row)
        else:
            bloom_filter.add(b_id)
        seen_ids.add(b_id)

    print(f"   - Total rows evaluated:   {len(rows)}")
    print(f"   - Unique Booking IDs:     {len(seen_ids)}")
    print(f"   - Flagged Duplicate Rows: {len(flagged_duplicates)}")

    if flagged_duplicates:
        print("\nDetected Duplicate Bookings (Intercepted by Bloom Filter):")
        print(f"{'Booking_ID':<12} {'Customer_ID':<12} {'Movie':<10} {'Theatre':<10} {'Tickets':<8} {'Amount':<8}")
        print("-" * 64)
        for dup in flagged_duplicates:
            print(f"{dup['Booking_ID']:<12} {dup['Customer_ID']:<12} {dup['Movie']:<10} {dup['Theatre']:<10} {dup['Tickets']:<8} ${dup['Amount']:<8.2f}")
    print()

    # =========================================================================
    # TASK 3: Create a DataFrame containing unique bookings
    # =========================================================================
    print("=" * 80)
    print("TASK 3: Create a DataFrame Containing Unique Bookings")
    print("=" * 80)
    unique_df = raw_df.dropDuplicates(["Booking_ID"])
    print(f"Unique Bookings Count: {unique_df.count()} (Reduced from {raw_df.count()} raw records)")
    unique_df.sort("Booking_ID").show(truncate=False)

    # Register temporary SQL view
    unique_df.createOrReplaceTempView("unique_bookings")

    # =========================================================================
    # TASK 4: Find the total number of tickets sold for each movie
    # =========================================================================
    print("=" * 80)
    print("TASK 4: Total Number of Tickets Sold For Each Movie")
    print("=" * 80)
    tickets_per_movie_df = unique_df.groupBy("Movie") \
        .agg(spark_sum("Tickets").alias("Total_Tickets_Sold")) \
        .orderBy(desc("Total_Tickets_Sold"))

    print("Result (DataFrame API):")
    tickets_per_movie_df.show(truncate=False)

    print("Verification via Spark SQL:")
    spark.sql("""
        SELECT Movie, SUM(Tickets) AS Total_Tickets_Sold
        FROM unique_bookings
        GROUP BY Movie
        ORDER BY Total_Tickets_Sold DESC
    """).show(truncate=False)

    # =========================================================================
    # TASK 5: Calculate total revenue for each movie
    # =========================================================================
    print("=" * 80)
    print("TASK 5: Calculate Total Revenue For Each Movie")
    print("=" * 80)
    revenue_per_movie_df = unique_df.groupBy("Movie") \
        .agg(
            spark_sum("Amount").alias("Total_Revenue"),
            spark_sum("Tickets").alias("Total_Tickets_Sold"),
            count("Booking_ID").alias("Unique_Bookings_Count")
        ) \
        .orderBy(desc("Total_Revenue"))

    print("Result (DataFrame API):")
    revenue_per_movie_df.show(truncate=False)

    print("Verification via Spark SQL:")
    spark.sql("""
        SELECT 
            Movie, 
            SUM(Amount) AS Total_Revenue,
            SUM(Tickets) AS Total_Tickets_Sold,
            COUNT(Booking_ID) AS Total_Bookings
        FROM unique_bookings
        GROUP BY Movie
        ORDER BY Total_Revenue DESC
    """).show(truncate=False)

    # =========================================================================
    # TASK 6: Use Spark SQL to find the highest-revenue movie
    # =========================================================================
    print("=" * 80)
    print("TASK 6: Use Spark SQL To Find The Highest-Revenue Movie")
    print("=" * 80)

    highest_revenue_query = """
        SELECT 
            Movie,
            SUM(Amount) AS Total_Revenue,
            SUM(Tickets) AS Total_Tickets_Sold,
            COUNT(Booking_ID) AS Total_Bookings
        FROM unique_bookings
        GROUP BY Movie
        ORDER BY Total_Revenue DESC
        LIMIT 1
    """
    highest_rev_df = spark.sql(highest_revenue_query)
    print("Spark SQL Query Result:")
    highest_rev_df.show(truncate=False)

    winner = highest_rev_df.first()
    if winner:
        print("+" + "-" * 78 + "+")
        print(f"| HIGHEST-REVENUE MOVIE WINNER: {winner['Movie']:<47} |")
        print(f"| Total Revenue Generated     : ${winner['Total_Revenue']:<47,.2f} |")
        print(f"| Total Tickets Sold          : {winner['Total_Tickets_Sold']:<47} |")
        print(f"| Unique Bookings Processed   : {winner['Total_Bookings']:<47} |")
        print("+" + "-" * 78 + "+")

    spark.stop()
    print("\n[INFO] All tasks completed successfully.")


if __name__ == "__main__":
    main()
