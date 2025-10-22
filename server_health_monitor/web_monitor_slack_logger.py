#!/usr/bin/env python3

# ########################################################
# Script name: web_monitor_slack_logger.py
# Description:
#   Monitors a website server and sends status notifications to Slack
#   Also logs every check result to a local log file (with color-coded icons for easier viewing)
# Features:
#   - Monitors website health (status code, latency)
#   - Sends Slack notifications when status changes (DOWN → UP or vice versa)
#   - Logs all checks with timestamps
#   - Uses defaults for URL and Slack webhook (configurable)
#   - Can accept CLI parameters for flexibility
# Requirements:
#   pip install requests
# Usage:
#   python3 web_monitor_slack_logger.py
#   python3 web_monitor_slack_logger.py --url https://example.com --webhook https://hooks.slack.com/services/xxx/yyy/zzz
# ########################################################


import requests
import time
import argparse
import datetime
import json
import os

# ============ DEFAULT SETTINGS ============
DEFAULT_URL = "https://www.dbs.com"
DEFAULT_SLACK_WEBHOOK = "https://hooks.slack.com/services/xxx/yyy/zzz"
CHECK_INTERVAL = 60  # seconds
TIMEOUT = 10         # seconds
LOG_FILE = "server_monitor.log"
# ==========================================


def write_log(message):
    """Write timestamped messages to log file and print to console."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def send_slack_notification(webhook_url, message, color="#36a64f"):
    """Send formatted message to Slack channel via webhook."""
    payload = {
        "attachments": [
            {
                "fallback": message,
                "color": color,
                "text": message,
                "footer": "Web Server Monitor",
                "ts": int(time.time())
            }
        ]
    }
    try:
        resp = requests.post(webhook_url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
        if resp.status_code != 200:
            write_log(f"⚠️ Slack webhook returned status {resp.status_code}: {resp.text}")
    except Exception as e:
        write_log(f"❌ Error sending Slack notification: {e}")


def check_website(url):
    """Perform an HTTP GET request and return (status_code, latency_ms)."""
    try:
        start_time = time.time()
        resp = requests.get(url, timeout=TIMEOUT)
        latency = round((time.time() - start_time) * 1000, 2)
        return resp.status_code, latency
    except requests.RequestException as e:
        return None, str(e)


def monitor_website(url, webhook_url):
    """Main monitoring loop with Slack alerts and logging."""
    write_log(f"🚀 Monitoring started for {url}")
    write_log(f"🔔 Slack notifications enabled: {webhook_url}")
    last_status = None

    while True:
        status_code, latency = check_website(url)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if status_code is None:
            msg = f"❌ Website DOWN: {url} | Error: {latency}"
            write_log(msg)
            if last_status != "DOWN":
                send_slack_notification(webhook_url, msg, color="#FF0000")
                last_status = "DOWN"
        else:
            msg = f"✅ Website UP: {url} | Status: {status_code} | Latency: {latency} ms"
            write_log(msg)
            if last_status != "UP":
                send_slack_notification(webhook_url, msg, color="#36a64f")
                last_status = "UP"

        time.sleep(CHECK_INTERVAL)


# ###############################
# MAIN
# ###############################

def main():
    parser = argparse.ArgumentParser(description="Monitor a website and log results while sending alerts to Slack.")
    parser.add_argument("--url", help="Website URL to monitor", default=DEFAULT_URL)
    parser.add_argument("--webhook", help="Slack Webhook URL", default=DEFAULT_SLACK_WEBHOOK)
    args = parser.parse_args()

    # Ensure log file exists
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("===== Web Server Monitor Log =====\n")

    monitor_website(args.url, args.webhook)


if __name__ == "__main__":
    main()
