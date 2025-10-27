#!/opt/anaconda3/bin/python3

# ########################################################
# Script name: log_summarizer.py
# Description:
#   A Python tool that reads and summarizes lengthy log files.
# Features:
#   - Detects and counts ERROR, WARNING, INFO, DEBUG entries
#   - Extracts timestamps, error messages, and key events
#   - Identifies recurring errors or exceptions
#   - Outputs a human-readable summary (console or file)
#   - Supports filtering by keyword or date range
#   - Handles large log files efficiently (streaming mode)
# Usage:
#  python3 log_summarizer.py /var/log/syslog
#  python3 log_summarizer.py app.log --keyword "database"
#  python3 log_summarizer.py app.log --start "2025-10-20 00:00:00" --end "2025-10-22 23:59:59"
#  python3 log_summarizer.py app.log --output summary.txt
# ########################################################


import re
import argparse
from collections import Counter, defaultdict
from datetime import datetime

# Regex patterns for timestamps and log levels
TIMESTAMP_PATTERN = re.compile(r'\b(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})\b')
LEVEL_PATTERN = re.compile(r'\b(INFO|WARN|WARNING|ERROR|DEBUG|CRITICAL)\b')

def parse_log_line(line):
    """Extract timestamp, log level, and message from a log line."""
    ts_match = TIMESTAMP_PATTERN.search(line)
    level_match = LEVEL_PATTERN.search(line)
    timestamp = ts_match.group(1) if ts_match else None
    level = level_match.group(1) if level_match else "UNKNOWN"
    message = line.strip()
    return timestamp, level, message

def summarize_log(file_path, keyword=None, start_date=None, end_date=None, output=None):
    level_counts = Counter()
    error_messages = defaultdict(int)
    total_lines = 0
    first_ts = None
    last_ts = None

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            total_lines += 1
            ts, level, msg = parse_log_line(line)
            level_counts[level] += 1

            # Set time window
            if ts:
                ts_obj = datetime.fromisoformat(ts.replace("T", " "))
                if not first_ts:
                    first_ts = ts_obj
                last_ts = ts_obj
                if start_date and ts_obj < start_date:
                    continue
                if end_date and ts_obj > end_date:
                    continue

            if keyword and keyword.lower() not in msg.lower():
                continue

            if level in ("ERROR", "CRITICAL"):
                # Extract key phrase of the error
                short_msg = " ".join(msg.split()[1:8])
                error_messages[short_msg] += 1

    # Prepare summary
    summary_lines = [
        f"===== LOG SUMMARY =====",
        f"File: {file_path}",
        f"Time span: {first_ts} → {last_ts}" if first_ts else "Time span: N/A",
        f"Total lines processed: {total_lines}",
        "",
        f"Log Level Counts:",
    ]
    for level, count in level_counts.items():
        summary_lines.append(f"  {level}: {count}")

    summary_lines.append("\nTop 5 Repeated Error Messages:")
    for msg, count in Counter(error_messages).most_common(5):
        summary_lines.append(f"  ({count}x) {msg}")

    summary_text = "\n".join(summary_lines)

    if output:
        with open(output, 'w', encoding='utf-8') as f_out:
            f_out.write(summary_text)
        print(f"Summary written to {output}")
    else:
        print(summary_text)


# ###############################
# MAIN
# ###############################

def main():
    parser = argparse.ArgumentParser(description="Summarize and extract key info from log files.")
    parser.add_argument("logfile", help="Path to the log file to analyze.")
    parser.add_argument("--keyword", help="Filter log lines containing this keyword.")
    parser.add_argument("--start", help="Start date (YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("--end", help="End date (YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("--output", help="Path to save the summary.")
    args = parser.parse_args()

    start_date = datetime.fromisoformat(args.start) if args.start else None
    end_date = datetime.fromisoformat(args.end) if args.end else None

    summarize_log(args.logfile, args.keyword, start_date, end_date, args.output)


if __name__ == "__main__":
    main()
