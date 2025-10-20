#!/usr/bin/env python3

# ===========================================================================
# Author: Arnold Aristotle Tayag
# Date created: 27-Mar-2020
# Purpose:
#   Deletes log files older than 3 months (90 days)
#   from /var/log and emails a summary report.
# Runtime:
#   Automate via Cron every 15 days at 1 in the morning:
#   0 1 1,16 * * /usr/bin/env python3 /path/to/cleanup_old_logs.py >> /var/log/cleanup_logs_$(date +\%Y-\%m-\%d).log 2>&1
# For update:
#   EMAIL_SENDER = "arnoldtayag@uob.com"
#   EMAIL_PASSWORD = "your_app_password"
#   EMAIL_RECEIVER = "alvintan@uob.com"
# ===========================================================================

import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta


# ==========================
# CONFIGURATION
# ==========================

# Directory to clean
LOG_DIR = "/var/log"

# Age threshold in days (3 months ≈ 90 days)
DAYS_THRESHOLD = 90

# Email Settings
EMAIL_ENABLED = True        # or False
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "arnoldtayag@uob.com"
EMAIL_PASSWORD = "app_token_key"
EMAIL_RECEIVER = "arnoldtayag@uob.com"


# ==========================
# CORE FUNCTIONALITY
# ==========================

def find_old_logs(directory, days_old):
    """Find files older than N days."""
    now = time.time()
    cutoff = now - (days_old * 86400)
    old_files = []

    for root, _, files in os.walk(directory):
        for f in files:
            path = os.path.join(root, f)
            try:
                if os.path.isfile(path) and os.stat(path).st_mtime < cutoff:
                    old_files.append(path)
            except FileNotFoundError:
                continue
    return old_files


def delete_files(file_list):
    """Delete specified files and return count."""
    deleted = []
    for file_path in file_list:
        try:
            os.remove(file_path)
            deleted.append(file_path)
        except PermissionError:
            print(f"Permission denied: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")
    return deleted


def generate_report(deleted_files):
    """Generate a text report of deleted files."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_lines = [
        "=" * 60,
        f"LOG CLEANUP REPORT — {timestamp}",
        "=" * 60,
        f"Directory Scanned : {LOG_DIR}",
        f"Files older than  : {DAYS_THRESHOLD} days",
        "-" * 60
    ]

    if deleted_files:
        report_lines.append(f"Deleted {len(deleted_files)} old log files:")
        for f in deleted_files:
            report_lines.append(f" - {f}")
    else:
        report_lines.append("No old log files found to delete.")

    report_lines.append("=" * 60)
    return "\n".join(report_lines)


# ==============================
# EMAIL NOTIFICATION
# ==============================

def send_email(subject, body):
    """Send email notification."""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)

        print("Email notification sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")


# =========================
# Main
# =========================

def main():
    print(f"Scanning {LOG_DIR} for logs older than {DAYS_THRESHOLD} days...")
    old_files = find_old_logs(LOG_DIR, DAYS_THRESHOLD)

    deleted_files = []
    if old_files:
        print(f"Found {len(old_files)} old logs. Deleting...")
        deleted_files = delete_files(old_files)
    else:
        print("No old logs found.")

    report = generate_report(deleted_files)
    print(report)

    if EMAIL_ENABLED:
        send_email("Log Cleanup Report", report)


if __name__ == "__main__":
   main()
