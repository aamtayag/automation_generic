#!/usr/bin/env python3

# ########################################################
# Script name: auto_google_search.py
# Description:
#   A Python tool that automates Googling and returns summarized results.
# Requirements:
#   - Python 3.8+
#   - pip install google-api-python-client
# Setup:
#   1. Create a Custom Search Engine (CSE) at https://programmablesearchengine.google.com/
#   2. Enable Custom Search API in https://console.cloud.google.com/apis/library/customsearch.googleapis.com
#   3. Create an API key from Google Cloud Console.
#   4. Add your API key and CSE ID below or via environment variables.
# Usage:
#   python3 auto_google_search.py "how to optimize mysql performance"
# ########################################################


import argparse
import os
from googleapiclient.discovery import build

# ================== CONFIGURATION ==================
# You can set these as environment variables instead of hardcoding
API_KEY = os.getenv("GOOGLE_API_KEY", "XXXXXXX")
CSE_ID = os.getenv("GOOGLE_CSE_ID", "XXXXXXX")
# ====================================================

def google_search(query, api_key=API_KEY, cse_id=CSE_ID, num=5):
    """Perform a Google search and return top results."""
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=query, cx=cse_id, num=num).execute()
    results = []

    for item in res.get("items", []):
        results.append({
            "title": item.get("title"),
            "snippet": item.get("snippet"),
            "link": item.get("link")
        })
    return results


def print_results(results, query):
    """Pretty-print the results."""
    print(f"\n Top Google search results for: '{query}'\n")
    if not results:
        print("No results found.")
        return
    for idx, r in enumerate(results, start=1):
        print(f"{idx}. {r['title']}")
        print(f"   {r['link']}")
        print(f"   {r['snippet']}\n")


# ###############################
# MAIN
# ###############################

def main():
    parser = argparse.ArgumentParser(description="Automate Google searches via API.")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--num", type=int, default=5, help="Number of results (default: 5)")
    args = parser.parse_args()

    results = google_search(args.query, num=args.num)
    print_results(results, args.query)


if __name__ == "__main__":
    main()
