# Problem #1: Most Visited Website (Hadoop MapReduce)

## Problem Statement
Given Website and User ID information, identify the website visited by the maximum number of unique users using a MapReduce program.

---

## Architectural Design

### 1. Mapper Phase
- **Input Key**: Line byte offset (`LongWritable`)
- **Input Value**: Raw text record e.g., `google.com,U101` or `U101\tgoogle.com` (`Text`)
- **Processing**:
  - Cleans and splits input tokens.
  - Normalizes website URL (lowercase, trimmed).
  - Handles variable column order (auto-detects user ID vs website).
- **Map Output Key**: `Website` (`Text`)
- **Map Output Value**: `User_ID` (`Text`)

### 2. Shuffle & Sort Phase
- MapReduce framework routes and groups all records having identical `Website` keys to the same Reducer.

### 3. Reducer Phase
- **Reducer Input**: `<Website, Iterable<User_ID>>`
- **Processing**:
  - Adds each `User_ID` into an in-memory `Set<String>` (or secondary aggregation) to deduplicate repeat visits by the same user.
  - Computes `uniqueUsers.size()`.
  - Emits `<Website, DistinctCount>`.
  - In `cleanup()`, identifies the global maximum website and emits the winner.

---

## Project Structure

```text
problem1_mapreduce/
├── src/com/bigdata/mapreduce/
│   ├── MostVisitedWebsite.java         # Single-pass MapReduce with cleanup global-max tracking
│   └── TwoStageMostVisitedWebsite.java # Two-stage enterprise MapReduce pipeline
├── scripts/
│   ├── mapper.py                       # Hadoop Streaming Mapper
│   └── reducer.py                      # Hadoop Streaming Reducer
├── input/
│   └── web_traffic.txt                 # Test dataset with realistic multi-user visits
├── output/                             # Generated job outputs
├── compile.sh                          # Compilation script for Java classes into JAR
├── run_hadoop.sh                       # Hadoop runner (local & cluster compatible)
├── run_streaming.sh                    # UNIX streaming simulation runner
├── run_local.py                        # Standalone Python simulator
└── README.md
```

---

## Execution Guide

### Option A: Standard Hadoop MapReduce (Java)
1. Compile the Java classes into a JAR:
   ```bash
   ./compile.sh
   ```
2. Run the Hadoop MapReduce job:
   ```bash
   ./run_hadoop.sh
   ```
   Or run the two-stage pipeline directly:
   ```bash
   hadoop jar dist/most-visited-website.jar com.bigdata.mapreduce.TwoStageMostVisitedWebsite \
     -Dfs.defaultFS=file:/// -Dmapreduce.framework.name=local \
     input/web_traffic.txt output/two_stage_result
   ```

### Option B: Hadoop Streaming Pipeline (Python)
Run using the standard UNIX pipe simulation (identical to `hadoop-streaming.jar`):
```bash
./run_streaming.sh
```

### Option C: Standalone Python Simulator
Run directly without any Hadoop installation:
```bash
python3 run_local.py
```

---

## Sample Execution Results

From `output/hadoop_result/part-r-00000`:
```text
amazon.com	2
facebook.com	3
google.com	9
netflix.com	3
twitter.com	2
wikipedia.org	2
youtube.com	5
----------------------------------------	0
MAXIMUM_VISITED_WEBSITE: google.com	9
----------------------------------------	0
```
**Conclusion:** `google.com` was visited by the maximum number of unique users (9 unique users).
