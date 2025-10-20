#!/usr/bin/env python3

# ===========================================================================
# Author: Arnold Aristotle Tayag
# Date created: 01-Nov-2019
# Purpose:
#   Checks if Oracle, MySQL, or MariaDB services are running,
#   and sends an email notification if any is down.
# Runtime:
#   Automate via Cron every hour eveyr day:
#   0 * * * * /usr/bin/env python3 /home/atayag/check_db_services.py >> /var/log/db_service_check_$(date +\%Y-\%m-\%d_\%H-\%M-\%S).log 2>&1
# For update:
#   EMAIL_SENDER = "arnoldtayag@uob.com"
#   EMAIL_PASSWORD = "your_app_password"
#   EMAIL_RECEIVER = "alvintan@uob.com"
# ===========================================================================

import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


# ==============================
# CONFIGURATION
# ==============================

# Services to monitor
# You can customize this per server by removing service NOT running in server
SERVICES = [
   "OracleServiceORCL",      # Oracle DB Service
   # "mysqld",                 # MySQL Server
   # "mariadb.service"         # MariaDB Server
]

# Email settings
EMAIL_ENABLED = True
SMTP_SERVER = "smtp.uobcom"
SMTP_PORT = 587
EMAIL_SENDER = "arnoldtayag@uob.com"
EMAIL_PASSWORD = "app_token_key"
EMAIL_RECEIVER = "arnoldtayag@uob.com"


# ==============================
# SERVICE CHECK LOGIC
# ==============================

def is_service_active(service_name):
    """
    Check if a service is active using systemctl or ps.
    Returns True if running, False otherwise.
    """
    try:
        # First try systemctl (modern Linux)
        cmd = ["systemctl", "is-active", service_name]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip() == "active":
            return True

        # Fallback check using ps if systemctl fails
        cmd = ["ps", "-ef"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if service_name.lower() in result.stdout.lower():
            return True
    except Exception:
        pass
    return False


def check_services():
    """Check all services and return a dict of statuses."""
    status_report = {}
    for service in SERVICES:
        status_report[service] = "Running" if is_service_active(service) else "Stopped ❌"
    return status_report


def generate_report(statuses):
    """Generate a text report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "=" * 60,
        f"DATABASE SERVICE STATUS REPORT — {timestamp}",
        "=" * 60,
    ]
    for service, status in statuses.items():
        lines.append(f"{service:<10}: {status}")
    lines.append("=" * 60)
    return "\n".join(lines)


# ==============================
# EMAIL NOTIFICATION
# ==============================

def send_email(subject, body):
    """Send an email alert."""
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

        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")


# ==============================
# MAIN
# ==============================

def main():
    statuses = check_services()
    report = generate_report(statuses)
    print(report)

    # Determine if any service is down
    down_services = [s for s, status in statuses.items() if "Stopped" in status]

    if EMAIL_ENABLED:
        if down_services:
            subject = f"ALERT: Database service(s) down: {', '.join(down_services)}"
        else:
            subject = "All database services are running normally"

        send_email(subject, report)


if __name__ == "__main__":
   main()
