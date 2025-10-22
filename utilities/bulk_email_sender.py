#!/usr/bin/env python3

# ########################################################
# Script name: bulk_email_sender.py
# Description:
#   Automation script to send emails (with optional PDF attachments) to multiple recipients
# Features:
#   - Reads sender and recipient list from a config file (JSON or YAML)
#   - Allows optional attachment (e.g. PDF or other files)
#   - Uses secure SMTP (TLS)
#   - Works on Linux, macOS, or Windows
#   - Logs sending status to file
# Requirements:
#   pip install pyyaml
# Usage:
#   python3 bulk_email_sender.py --subject "Monthly Report" --body "Please see attached report." --attach report.pdf
# ########################################################


import smtplib
import ssl
import json
import yaml
import argparse
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime

# ======= CONFIGURATION =======
DEFAULT_CONFIG = "email_config.json"
LOG_FILE = "email_log.txt"
# =============================


def write_log(message):
    """Write message with timestamp to console and log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_config(config_file):
    """Load email configuration from JSON or YAML file."""
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file not found: {config_file}")

    with open(config_file, "r", encoding="utf-8") as f:
        if config_file.endswith(".json"):
            return json.load(f)
        elif config_file.endswith((".yml", ".yaml")):
            return yaml.safe_load(f)
        else:
            raise ValueError("Unsupported config format. Use .json or .yaml")


def create_email(sender, recipient, subject, body, attachment_path=None):
    """Create a MIME email with optional PDF attachment."""
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
        part["Content-Disposition"] = f'attachment; filename="{os.path.basename(attachment_path)}"'
        msg.attach(part)

    return msg


def send_emails(config, subject, body, attachment=None):
    """Send email to all recipients from config."""
    smtp_server = config["email"]["smtp_server"]
    smtp_port = config["email"].get("smtp_port", 587)
    sender_email = config["email"]["sender"]
    password = config["email"]["password"]
    recipients = config["recipients"]

    context = ssl.create_default_context()

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls(context=context)
        server.login(sender_email, password)

        for recipient in recipients:
            try:
                msg = create_email(sender_email, recipient, subject, body, attachment)
                server.send_message(msg)
                write_log(f"✅ Email sent to {recipient}")
            except Exception as e:
                write_log(f"❌ Failed to send email to {recipient}: {e}")


# ###############################
# MAIN
# ###############################

def main():
    parser = argparse.ArgumentParser(description="Bulk email sender with optional attachment.")
    parser.add_argument("--config", help="Path to config file", default=DEFAULT_CONFIG)
    parser.add_argument("--subject", required=True, help="Email subject line")
    parser.add_argument("--body", required=True, help="Email body text")
    parser.add_argument("--attach", help="File to attach (optional)")
    args = parser.parse_args()

    config = load_config(args.config)
    send_emails(config, args.subject, args.body, args.attach)


if __name__ == "__main__":
    main()
