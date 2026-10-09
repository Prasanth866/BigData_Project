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
from pathlib import Path

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pybloom_live import BloomFilter
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum, count, desc
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType


def main():
    script_dir = Path(__file__).resolve().parent
    data_path = script_dir / "data" / "movie_bookings.csv"

    if not data_path.exists():
        print(f"Error: Data file not found at {data_path}")
        sys.exit(1)

    print("=" * 80)
    print("         SPARK SQL: MOVIE TICKET BOOKING SYSTEM ANALYSIS")
    print("=" * 80)

    spark = SparkSession.builder \
        .appName("MovieTicketBookingAnalysis") \
        .master("local[*]") \
        .config("spark.ui.enabled", "false") \
        .config("spark.sql.shuffle.partitions", "2") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

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

    print("=" * 80)
    print("TASK 1: Bookings Containing More Than Two Tickets (Tickets > 2)")
    print("=" * 80)
    df_more_than_2 = raw_df.filter(col("Tickets") > 2)
    print(f"Found {df_more_than_2.count()} bookings with Tickets > 2:")
    df_more_than_2.show(truncate=False)

    print("=" * 80)
    print("TASK 2: Detect Duplicate Booking IDs Using a Bloom Filter")
    print("=" * 80)

    spark_bf = raw_df._jdf.stat().bloomFilter("Booking_ID", 1000, 0.01)
    print(f"-> Spark Native Bloom Filter constructed:")
    print(f"   - Class: {spark_bf.getClass().getName()}")
    print(f"   - Bit size (m): {spark_bf.bitSize()} bits")
    print(f"   - Expected Items (n): 1000, False Positive Probability (p): 0.01")
    print(f"   - Membership check 'B101': {spark_bf.mightContain('B101')}")
    print(f"   - Membership check 'NONEXISTENT_KEY': {spark_bf.mightContain('NONEXISTENT_KEY')}")

    bloom_filter = BloomFilter(capacity=1000, error_rate=0.01)
    print(f"\n-> pybloom_live Bloom Filter initialized:")
    print(f"   - Class: {type(bloom_filter).__module__}.{type(bloom_filter).__name__}")
    print(f"   - Capacity (n): {bloom_filter.capacity}, Error Rate (p): {bloom_filter.error_rate}")
    print(f"   - Bit Array Size (m): {bloom_filter.num_bits} bits")
    print(f"   - Number of Hash Functions / Slices (k): {bloom_filter.num_slices}")

    rows = raw_df.collect()

    flagged_duplicates = []
    seen_ids = set()

    print(f"\n-> Streaming records through Bloom Filter to intercept duplicates:")
    for row in rows:
        b_id = row["Booking_ID"]
        if b_id in bloom_filter:
            flagged_duplicates.append(row)
        else:
            bloom_filter.add(b_id)
        seen_ids.add(b_id)

    print(f"   - Total rows evaluated:   {len(rows)}")
    print(f"   - Unique Booking IDs:     {len(seen_ids)}")
    print(f"   - Flagged Duplicate Rows: {len(flagged_duplicates)}")
    print(f"   - Filter element count:   {len(bloom_filter)}")

    if flagged_duplicates:
        print("\nDetected Duplicate Bookings (Intercepted by Bloom Filter):")
        print(f"{'Booking_ID':<12} {'Customer_ID':<12} {'Movie':<10} {'Theatre':<10} {'Tickets':<8} {'Amount':<8}")
        print("-" * 64)
        for dup in flagged_duplicates:
            print(f"{dup['Booking_ID']:<12} {dup['Customer_ID']:<12} {dup['Movie']:<10} {dup['Theatre']:<10} {dup['Tickets']:<8} ${dup['Amount']:<8.2f}")
    print()

    print("=" * 80)
    print("TASK 3: Create a DataFrame Containing Unique Bookings")
    print("=" * 80)
    unique_df = raw_df.dropDuplicates(["Booking_ID"])
    print(f"Unique Bookings Count: {unique_df.count()} (Reduced from {raw_df.count()} raw records)")
    unique_df.sort("Booking_ID").show(truncate=False)

    unique_df.createOrReplaceTempView("unique_bookings")

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
