# Tasks Automation (Generic)

# Description
My repository of **automation scripts** written in **Bash**, **Python**, and **Shell** to simplify repetitive **day-to-day system administration, DevOps, and IT management tasks**. This serves as a personal toolkit for scripting, monitoring, and process optimization across Linux, Windows, and macOS environments.

# Key Features
   - ✅ **Cross-platform compatibility** (Linux, Windows, macOS)  
   - ✅ **Automated housekeeping** (log cleanup, backups, file rotation)  
   - ✅ **System health checks** for CPU, disk, and services  
   - ✅ **Email and Slack notifications** for job results or alerts  
   - ✅ **Cron-ready scripts** for unattended execution  
   - ✅ **Extensible** — add my own utilities anytime

# Technologies Used
| Category                 | Tools / Languages                                      |
|--------------------------|--------------------------------------------------------|
| **Scripting**            | Bash, Shell, Python3, PowerShell                       |
| **Scheduling**           | Cron, systemd timers                                   |
| **Notifications**        | 'mail', 'sendmail', 'smtplib', Slack webhooks          |
| **OS System Utilities**  | 'df', 'du', 'ps', 'grep', 'awk', 'find', etc.          |
| **Logging**              | Custom log rotation and timestamping                   |

# Prerequisites
Before running the scripts, make sure you have:
   - ✅ A Linux or macOS system with Bash ≥ 4.0 or Python ≥ 3.8
   - ✅ A Windows system with PowerShell ≥ 6.x
   - ✅ Proper permissions to execute scripts and access system logs  
   - ✅ Installed utilities: 'mail', 'crontab', 'gzip', 'find', 'awk', etc.  
   - ✅ Configured email relay or SMTP (for notifications)

# Repository Contents
| Folder / File   | Description                                                           |
|-----------------|-----------------------------------------------------------------------|
| 'bash/'         | Shell and Bash scripts for system tasks, cleanup, and cron jobs       |
| 'python/'       | Python utilities for monitoring, notifications, or API automation     |
| 'powershell/'   | Powershell tilities for Windows systems                               |
| 'logs/'         | Directory for output and activity logs (auto-generated)               |
| 'README.md'     | Documentation for setup, usage, and examples (this file)              |
