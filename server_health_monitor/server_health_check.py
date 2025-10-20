#!/usr/bin/env python3

# ===========================================================================
# Author: Arnold Aristotle Tayag
# Date created: 02-Feb-2020
# Purpose:
#   Server Health Check Script for Linux
#   Checks CPU, memory, disk usage, load average, uptime, and network connectivity.
#   Optionally sends report via email or Slack webhook.
# Runtime:
#   Automate via Cron every day at 1 in the morning:
#   0 1 * * * /usr/bin/env python3 /home/atayag/server_health_check.py >> /var/log/server_health_$(date +\%Y-\%m-\%d_\%H-\%M-\%S).log 2>&1
# For update:
#   EMAIL_SENDER = "arnoldtayag@uob.com"
#   EMAIL_PASSWORD = "your_app_password"
#   EMAIL_RECEIVER = "alvintan@uob.com"
#   SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/XXXX/YYYY/ZZZZ"
# ===========================================================================

import psutil
import platform
import socket
import smtplib
import requests
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# =========================
# Configuration
# =========================

EMAIL_ENABLED = True            # or False
SLACK_ENABLED = False           # or True

# Email Settings
SMTP_SERVER = "smtp.uob.com"
SMTP_PORT = 587
EMAIL_SENDER = "arnoldtayag@uob.com"
EMAIL_PASSWORD = "app_token_key"
EMAIL_RECEIVER = "alvintan@uob.com"

# Slack Webhook URL, CHANGE THIS IF USED!!!
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/XXXX/YYYY/ZZZZ"


# =========================
# Health Check Functions
# =========================

def check_uptime():
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    return str(timedelta(seconds=int(uptime.total_seconds())))

def check_cpu():
    return psutil.cpu_percent(interval=1)

def check_memory():
    mem = psutil.virtual_memory()
    return mem.percent, mem.total // (1024**3), mem.available // (1024**3)

def check_disk():
    usage_info = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            usage_info.append({
                'mountpoint': partition.mountpoint,
                'total_GB': usage.total // (1024**3),
                'used_percent': usage.percent
            })
        except PermissionError:
            continue
    return usage_info

def check_load():
    if hasattr(psutil, "getloadavg"):
        load1, load5, load15 = psutil.getloadavg()
        return (load1, load5, load15, psutil.cpu_count())
    return (0, 0, 0, psutil.cpu_count())

def check_network(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


# =========================
# Report Generation
# =========================

def generate_report():
    hostname = platform.node()
    os_info = f"{platform.system()} {platform.release()}"
    uptime = check_uptime()
    net_status = "Online" if check_network() else "Offline"
    cpu = check_cpu()
    mem_percent, total_mem, avail_mem = check_memory()
    load1, load5, load15, cores = check_load()
    disk_info = check_disk()

    report = []
    report.append("=" * 60)
    report.append(f"SERVER HEALTH STATUS REPORT — {hostname}")
    report.append("=" * 60)
    report.append(f"OS / Kernel     : {os_info}")
    report.append(f"Uptime          : {uptime}")
    report.append(f"Network Status  : {net_status}")
    report.append("-" * 60)
    report.append(f"CPU Usage       : {cpu}%")
    report.append(f"Memory Usage    : {mem_percent}%  ({avail_mem} GB free / {total_mem} GB total)")
    report.append(f"Load Average    : {load1:.2f}, {load5:.2f}, {load15:.2f} (Cores: {cores})")
    report.append("\nDisk Usage:")
    for d in disk_info:
        report.append(f" - {d['mountpoint']}: {d['used_percent']}% used ({d['total_GB']} GB total)")
    report.append("=" * 60)
    report.append("Health check completed.")
    report.append("=" * 60)

    return "\n".join(report)


# =========================
# Email Notification
# =========================

def send_email(subject, body):
    """Send report via email."""
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

        print("Email report sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")


def send_slack_notification(message):
    """Send report to Slack via webhook."""
    try:
        payload = {"text": f"```{message}```"}
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        if response.status_code == 200:
            print("Slack notification sent successfully.")
        else:
            print(f"Slack notification failed: {response.text}")
    except Exception as e:
        print(f"Error sending Slack message: {e}")


# =========================
# Main
# =========================

def main():
    report = generate_report()
    print(report)

    if EMAIL_ENABLED:
        send_email("Server Health Report", report)

    if SLACK_ENABLED:
        send_slack_notification(report)


if __name__ == "__main__":
    main()
