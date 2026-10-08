#!/usr/bin/env python3
"""
Standalone MapReduce Simulation in pure Python.
Demonstrates the exact Map, Shuffle & Sort, and Reduce phases.
"""
import sys
from collections import defaultdict
from pathlib import Path

def mapper(lines):
    pairs = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or line.lower().startswith("website"):
            continue
        parts = [p.strip() for p in line.replace(",", " ").split() if p.strip()]
        if len(parts) >= 2:
            t0, t1 = parts[0], parts[1]
            if t0.lower().startswith(("user", "u")) and not t1.lower().startswith(("user", "u")):
                user_id, website = t0, t1.lower()
            else:
                website, user_id = t0.lower(), t1
            pairs.append((website, user_id))
    return pairs

def shuffle_and_sort(pairs):
    grouped = defaultdict(list)
    for k, v in sorted(pairs, key=lambda x: x[0]):
        grouped[k].append(v)
    return grouped

def reducer(grouped):
    results = {}
    max_site = None
    max_count = -1
    for website, users in grouped.items():
        unique_count = len(set(users))
        results[website] = unique_count
        if unique_count > max_count:
            max_count = unique_count
            max_site = website
    return results, max_site, max_count

def main():
    dataset_path = Path(__file__).parent / "input" / "web_traffic.txt"
    if len(sys.argv) > 1:
        dataset_path = Path(sys.argv[1])

    if not dataset_path.exists():
        print(f"File not found: {dataset_path}")
        sys.exit(1)

    with open(dataset_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Phase 1: Map
    mapped = mapper(lines)
    print(f"-> Map Phase emitted {len(mapped)} key-value records.")

    # Phase 2: Shuffle & Sort
    grouped = shuffle_and_sort(mapped)
    print(f"-> Shuffle & Sort Phase partitioned into {len(grouped)} distinct website keys.")

    # Phase 3: Reduce
    counts, max_site, max_count = reducer(grouped)
    print("\n--- Website Visit Statistics (Unique Users) ---")
    for site, count in sorted(counts.items()):
        print(f"  {site:<20}: {count} unique users")

    print("\n" + "=" * 50)
    print(f"  MAXIMUM VISITED WEBSITE : {max_site}")
    print(f"  TOTAL UNIQUE USERS      : {max_count}")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    main()
