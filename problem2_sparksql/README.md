# Problem #2: SparkSQL - Movie Ticket Booking

## Problem Statement
A movie booking system receives records with the schema:
`Booking_ID, Customer_ID, Movie, Theatre, Tickets, Amount`

### Required Tasks:
1. Identify bookings containing more than two tickets (`Tickets > 2`).
2. Detect duplicate Booking IDs using a Bloom Filter.
3. Create a DataFrame containing unique bookings.
4. Find the total number of tickets sold for each movie.
5. Calculate total revenue for each movie.
6. Use Spark SQL to find the highest-revenue movie.

---

## Technical Architecture & Theoretical Concepts

### 1. Bloom Filter in Distributed Systems
A Bloom Filter is a space-efficient probabilistic data structure that tests set membership with $O(1)$ query complexity:
- **No False Negatives**: If `mightContain(key) == false`, the key is guaranteed never to have been seen before.
- **Controlled False Positive Probability ($p$)**: If `mightContain(key) == true`, the element may be present or a false positive occurred.

#### Mathematical Formulation:
- Optimal number of bits:
  $$m = -\frac{n \ln(p)}{(\ln 2)^2}$$
- Optimal number of hash functions:
  $$k = \frac{m}{n} \ln(2)$$

In distributed engines like Apache Spark, Bloom Filters (`df.stat.bloomFilter` / `org.apache.spark.util.sketch.BloomFilter`) allow early filtering of non-matching records and fast duplicate interception before executing heavy shuffle joins and sorting across cluster nodes. In addition, Python streaming ingestion leverages the high-performance [`pybloom_live`](https://pypi.org/project/pybloom-live/) library (`pybloom_live.BloomFilter`).

---

## Directory Structure

```text
problem2_sparksql/
├── data/
│   └── movie_bookings.csv       # Ingestion dataset with duplicate IDs and ticket variations
├── movie_booking_analysis.py    # PySpark complete implementation solving all 6 tasks
├── run.sh                       # Execution wrapper script
└── README.md                    # Technical documentation
```

---

## Execution Guide

### Dependencies Setup

Install dependencies via `uv` or `pip`:
```bash
uv pip install -r ../requirements.txt
# or
pip install -r ../requirements.txt
```

### Running the Pipeline

Run the pipeline using the configured virtual environment wrapper:
```bash
./run.sh
```
Or directly:
```bash
python3 movie_booking_analysis.py
```

---

## Execution Results Summary

### Task 1: Bookings With Tickets > 2
Identified 10 bookings matching the condition `Tickets > 2`.

### Task 2: Duplicate Detection via Bloom Filter
- **Bloom Filter Capacity**: 1000 items, False Positive Rate: 1% ($p=0.01$).
- **Identified Duplicates**:
  - `B101` (Customer: `C101`, Movie: `MovieA`, Tickets: `2`, Amount: `$400.00`)
  - `B102` (Customer: `C102`, Movie: `MovieB`, Tickets: `4`, Amount: `$800.00`)
  - `B103` (Customer: `C103`, Movie: `MovieA`, Tickets: `3`, Amount: `$600.00`)

### Task 3: Unique Bookings DataFrame
Successfully deduplicated the initial 15 records down to 12 unique bookings.

### Task 4: Total Tickets Sold Per Movie
| Movie | Total Tickets Sold |
|---|---|
| `MovieD` | 13 |
| `MovieB` | 10 |
| `MovieA` | 9 |
| `MovieC` | 8 |

### Task 5: Total Revenue Per Movie
| Movie | Total Revenue | Total Tickets Sold | Unique Bookings Count |
|---|---|---|---|
| `MovieD` | $3,250.00 | 13 | 3 |
| `MovieB` | $2,000.00 | 10 | 3 |
| `MovieC` | $2,000.00 | 8 | 3 |
| `MovieA` | $1,900.00 | 9 | 3 |

### Task 6: Highest-Revenue Movie (Spark SQL)
```sql
SELECT Movie, SUM(Amount) AS Total_Revenue, SUM(Tickets) AS Total_Tickets_Sold, COUNT(Booking_ID) AS Total_Bookings
FROM unique_bookings
GROUP BY Movie
ORDER BY Total_Revenue DESC
LIMIT 1
```
- **Winner**: **`MovieD`**
- **Total Revenue**: **`$3,250.00`**
- **Total Tickets Sold**: **`13`**
- **Total Bookings**: **`3`**
