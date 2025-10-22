#!/usr/bin/env python3

# ########################################################
# Script name: web_scraper_logger.py
# Description:
#   A Python automation script that scrapes headlines or key information from
#   any given website URL and logs the extracted content to a local log file
# Features:
#   - Accepts a website URL as input (or uses default)
#   - Extracts main headings (h1–h3) and meta descriptions
#   - Writes the results to a timestamped log file
#   - Handles errors and network timeouts gracefully
# Requirements:
#   pip install requests beautifulsoup4
# Usage:
#   python3 web_scraper_logger.py
#   python3 web_scraper_logger.py --url https://edition.cnn.com
# ########################################################

import requests
from bs4 import BeautifulSoup
import argparse
import datetime
import os

# ============ DEFAULT SETTINGS ============
DEFAULT_URL = "https://edition.cnn.com"     # Default website to scrape
OUTPUT_DIR = "scrape_logs.log"
# ==========================================


def log_message(message, logfile):
    """Write timestamped message to the log file and print to console."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def scrape_website(url):
    """Scrape the given URL for headlines or key text content."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; WebScraperBot/1.0)"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Collect key data
        headlines = []
        for tag in ["h1", "h2", "h3"]:
            for elem in soup.find_all(tag):
                text = elem.get_text(strip=True)
                if text and len(text) > 5:
                    headlines.append(text)

        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = meta_desc["content"] if meta_desc and "content" in meta_desc.attrs else "N/A"

        return {
            "url": url,
            "status": "SUCCESS",
            "headline_count": len(headlines),
            "description": description,
            "headlines": headlines[:15]  # limit to top 15 for readability
        }

    except requests.exceptions.RequestException as e:
        return {"url": url, "status": "ERROR", "error": str(e)}


# ###############################
# MAIN
# ###############################

def main():
    parser = argparse.ArgumentParser(description="Scrape headlines and info from a website.")
    parser.add_argument("--url", help="Website URL to scrape", default=DEFAULT_URL)
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    logfile = os.path.join(
        OUTPUT_DIR,
        f"scrape_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    )

    log_message(f"🚀 Starting scrape for: {args.url}", logfile)

    result = scrape_website(args.url)
    if result["status"] == "SUCCESS":
        log_message(f"✅ Successfully scraped {result['headline_count']} headlines", logfile)
        log_message(f"📝 Meta Description: {result['description']}", logfile)
        log_message("\nTop Headlines Extracted:", logfile)
        for i, headline in enumerate(result["headlines"], 1):
            log_message(f"{i}. {headline}", logfile)
    else:
        log_message(f"❌ Failed to scrape {args.url} - {result['error']}", logfile)

    log_message("📁 Results saved to: " + logfile, logfile)


if __name__ == "__main__":
    main()
