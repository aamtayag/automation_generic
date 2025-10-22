#!/usr/bin/env python3

# ########################################################
# Script name: multi_site_web_monitor.py
# Description:
#   Monitors multiple websites and sends status notifications to Slack
# Features:
#   - Supports multiple websites (loaded from JSON or YAML config)
#   - Each site can have its own Slack webhook
#   - Logs all status changes and results locally
#   - Sends Slack notifications when a site goes DOWN or recovers
#   - Configurable interval, timeouts, and defaults
# Requirements:
#   pip install requests pyyaml
#Usage:
#   python3 multi_site_web_monitor.py
#   python3 multi_site_web_monitor.py --config sites.json
#   python3 multi_site_web_monitor.py --config sites.yaml
# ########################################################

import requests
import time
import datetime
import json
import yaml
import argparse
import os

# ======= CONFIGURATION =======
DEFAULT_CONFIG = "sites.json"           # List of sites to monitor
LOG_FILE = "multi_site_monitor.log"     # Log file
CHECK_INTERVAL = 60                     # seconds between checks
TIMEOUT = 10                            # request timeout in seconds
# =============================


def write_log(message):
    """Write message to console and to the log file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def send_slack_notification(webhook_url, message, color="#36a64f"):
    """Send a formatted message to a Slack channel."""
    payload = {
        "attachments": [
            {
                "fallback": message,
                "color": color,
                "text": message,
                "footer": "Multi-Site Web Monitor",
                "ts": int(time.time())
            }
        ]
    }
    try:
        response = requests.post(webhook_url, json=payload, timeout=TIMEOUT)
        if response.status_code != 200:
            write_log(f"⚠️ Slack webhook failed ({response.status_code}): {response.text}")
    except Exception as e:
        write_log(f"❌ Slack send error: {e}")


def check_website(url):
    """Perform an HTTP GET request to check website health."""
    try:
        start = time.time()
        response = requests.get(url, timeout=TIMEOUT)
        latency = round((time.time() - start) * 1000, 2)  # milliseconds
        return response.status_code, latency
    except requests.RequestException as e:
        return None, str(e)


def load_config(config_file):
    """Load JSON or YAML configuration."""
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file not found: {config_file}")

    with open(config_file, "r", encoding="utf-8") as f:
        if config_file.endswith(".json"):
            return json.load(f)
        elif config_file.endswith((".yml", ".yaml")):
            return yaml.safe_load(f)
        else:
            raise ValueError("Unsupported config file type. Use .json or .yaml")


def monitor_sites(config):
    """Main monitoring loop for all sites."""
    last_status = {}  # Track UP/DOWN per site

    write_log(f"🚀 Starting multi-site monitoring for {len(config['sites'])} websites")

    while True:
        for site in config["sites"]:
            url = site["url"]
            webhook = site["webhook"]
            name = site.get("name", url)

            status_code, latency = check_website(url)
            if status_code is None:
                msg = f"❌ {name} is DOWN | {url} | Error: {latency}"
                write_log(msg)
                if last_status.get(url) != "DOWN":
                    send_slack_notification(webhook, msg, color="#FF0000")
                    last_status[url] = "DOWN"
            else:
                msg = f"✅ {name} is UP | Status {status_code} | {latency} ms"
                write_log(msg)
                if last_status.get(url) != "UP":
                    send_slack_notification(webhook, msg, color="#36a64f")
                    last_status[url] = "UP"

        time.sleep(config.get("interval", CHECK_INTERVAL))


# ###############################
# MAIN
# ###############################

def main():
    parser = argparse.ArgumentParser(description="Monitor multiple websites and send Slack alerts.")
    parser.add_argument("--config", help="Path to JSON or YAML config file", default=DEFAULT_CONFIG)
    args = parser.parse_args()

    config = load_config(args.config)
    os.makedirs(os.path.dirname(LOG_FILE) or ".", exist_ok=True)

    monitor_sites(config)


if __name__ == "__main__":
    main()
