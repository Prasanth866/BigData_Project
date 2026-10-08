#!/usr/bin/env python3
"""
Problem #1 - Hadoop Streaming Reducer: Most Visited Website
Receives sorted input (Website \t User_ID) from Mapper / Shuffle stage.
Deduplicates User_IDs per Website using a set, calculates unique user counts,
and emits both per-website unique counts and the globally most visited website.
"""
import sys

def main():
    current_website = None
    unique_users = set()

    max_website = None
    max_user_count = -1

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split('\t', 1)
        if len(parts) != 2:
            continue

        website, user_id = parts[0].strip(), parts[1].strip()

        if current_website == website:
            unique_users.add(user_id)
        else:
            if current_website is not None:
                count = len(unique_users)
                print(f"{current_website}\t{count}")
                if count > max_user_count:
                    max_user_count = count
                    max_website = current_website

            current_website = website
            unique_users = {user_id}

    # Process final website
    if current_website is not None:
        count = len(unique_users)
        print(f"{current_website}\t{count}")
        if count > max_user_count:
            max_user_count = count
            max_website = current_website

    # Output the maximum visited website
    if max_website is not None:
        print("=" * 45)
        print(f"MAXIMUM_VISITED_WEBSITE:\t{max_website}\t(Unique Users: {max_user_count})")
        print("=" * 45)

if __name__ == "__main__":
    main()
