#!/usr/bin/env python3

# ########################################################
# Script name: sync_repos_to_github.py
# Description:
#   Automates synchronization (push) of multiple local git repositories to GitHub
# Features:
#   - Reads list of repositories and GitHub URLs from config.json
#   - Commits and pushes changes automatically
#   - Logs results for each repo (with color coding icons for easier view)
#   - Skips repos with no changes
#   - Configurable branch (default: main)
# Usage:
#   python3 sync_repos_to_github.py
# Requirements:
#   pip install GitPython
# ########################################################

import os
import json
import datetime
from git import Repo, GitCommandError

CONFIG_FILE = "config.json"
LOG_FILE = "sync_log.txt"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"Config file '{CONFIG_FILE}' not found.")
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{timestamp}] {message}"
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

def sync_repo(local_path, remote_url, branch="main"):
    try:
        if not os.path.isdir(local_path):
            log(f"❌ Skipped: Local path not found: {local_path}")
            return

        repo = Repo(local_path)

        if repo.is_dirty(untracked_files=True):
            repo.git.add(A=True)
            repo.index.commit("Automated sync commit")

        origin = repo.remotes.origin if "origin" in [r.name for r in repo.remotes] else None
        if not origin:
            repo.create_remote("origin", remote_url)
            origin = repo.remotes.origin

        # Pull latest changes first (handle merge conflicts manually)
        try:
            origin.pull(branch)
        except GitCommandError as e:
            log(f"⚠️ Pull warning in {local_path}: {e}")

        origin.push(branch)
        log(f"✅ Synced: {local_path} → {remote_url}")

    except Exception as e:
        log(f"❌ Error syncing {local_path}: {str(e)}")


# ###############################
# MAIN
# ###############################

def main():
    try:
        config = load_config()
        log("===== Starting repository synchronization =====")
        for repo in config.get("repositories", []):
            local = repo.get("local_path")
            remote = repo.get("remote_url")
            branch = repo.get("branch", "main")
            log(f"🔄 Syncing: {local}")
            sync_repo(local, remote, branch)
        log("===== Synchronization complete =====")
    except Exception as e:
        log(f"💥 Fatal error: {e}")

if __name__ == "__main__":
    main()
