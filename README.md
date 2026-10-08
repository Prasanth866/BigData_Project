# Big Data Engineering Laboratory Solutions

This repository provides comprehensive, production-grade solutions for all three problems specified in [`problems.txt`](file:///Users/prasanth/Desktop/Projects/BigData/problems.txt). Each problem is solved in a dedicated, self-contained directory with full source code, datasets, execution scripts, and technical documentation.

---

## Directory Overview

| Directory | Topic / Technology | Problem Addressed | Status |
|---|---|---|---|
| [`problem1_mapreduce/`](file:///Users/prasanth/Desktop/Projects/BigData/problem1_mapreduce) | **Hadoop MapReduce (Java & Python)** | Most Visited Website (Unique User Tracking & Global Maximum Finding) | Tested & Verified |
| [`problem2_sparksql/`](file:///Users/prasanth/Desktop/Projects/BigData/problem2_sparksql) | **Apache Spark & Spark SQL** | Movie Ticket Booking (Bloom Filter Duplicate Detection & Analytics) | Tested & Verified |
| [`problem3_rdf_museum/`](file:///Users/prasanth/Desktop/Projects/BigData/problem3_rdf_museum) | **Semantic Web / RDF / RDFS / SPARQL** | Museum Knowledge Base (Ontology Design, Reasoning & Queries) | Tested & Verified |

---

## One-Click Master Execution

To build, execute, and verify all three problem pipelines sequentially:

```bash
./run_all.sh
```

---

## Problem Summaries

### 1. Problem #1: Most Visited Website (`problem1_mapreduce/`)
- **Implementations**:
  - `MostVisitedWebsite.java`: Single-pass MapReduce with cleanup global maximum extraction.
  - `TwoStageMostVisitedWebsite.java`: Enterprise two-stage pipeline for massive-scale distributed datasets.
  - `mapper.py` & `reducer.py`: UNIX streaming / Hadoop Streaming compatible scripts.
  - `run_local.py`: Pure Python standalone simulator.
- **Key Concepts**: MapReduce shuffle and sort, user deduplication via in-memory sets, reducer cleanup phase aggregation, ToolRunner CLI integration.
- **Winner in Sample Run**: `google.com` (9 unique users).

### 2. Problem #2: SparkSQL - Movie Ticket Booking (`problem2_sparksql/`)
- **Implementation**: `movie_booking_analysis.py` (PySpark + Spark SQL).
- **Tasks Solved**:
  1. Identified bookings with `Tickets > 2`.
  2. Implemented Bloom Filter duplicate detection (demonstrating both Apache Spark's native `BloomFilterImplV2` and custom double-hashed Bloom Filter mechanics).
  3. Created deduplicated DataFrame containing unique bookings.
  4. Calculated total tickets sold per movie (`groupBy` + SQL).
  5. Computed total revenue per movie.
  6. Used Spark SQL to identify the highest-revenue movie.
- **Winner in Sample Run**: `MovieD` ($3,250.00 revenue, 13 tickets sold).

### 3. Problem #3: RDF Museum Management (`problem3_rdf_museum/`)
- **Deliverables**:
  - `ontology/museum.ttl`: Clean W3C Turtle representation.
  - `ontology/museum.rdf`: Standard W3C RDF/XML interchange format.
  - `ontology/museum.nt`: Canonical W3C N-Triples format.
  - `queries/*.rq`: SPARQL queries covering artwork relationships, RDFS subclass entailment, and metadata annotations.
  - `validate_and_query.py`: Python validation and SPARQL execution script with RDFS inference engine.
  - `SOLUTION_REPORT.md`: Comprehensive academic and technical report answering Questions 1 through 7 with formal ontological justifications and tables.
