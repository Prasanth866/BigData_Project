#!/usr/bin/env python3
"""
Problem #1 - Hadoop Streaming Mapper: Most Visited Website
Reads input lines: Website,User_ID or User_ID,Website
Emits tab-separated key-value pairs: Website \t User_ID
"""
import sys
import re

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line or line.startswith("#") or line.lower().startswith("website"):
            continue

        # Split on comma, tab, or whitespace
        parts = re.split(r'[\t,]+', line)
        if len(parts) >= 2:
            token0 = parts[0].strip()
            token1 = parts[1].strip()

            # Handle format where UserID is first column (e.g. U101, google.com)
            if re.match(r'^(user|u)\d+', token0, re.IGNORECASE) and not re.match(r'^(user|u)\d+', token1, re.IGNORECASE):
                user_id = token0
                website = token1.lower()
            else:
                website = token0.lower()
                user_id = token1

            if website and user_id:
                print(f"{website}\t{user_id}")

if __name__ == "__main__":
    main()
