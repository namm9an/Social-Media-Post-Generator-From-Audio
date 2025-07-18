#!/usr/bin/env python3
"""Disaster recovery helper – automate system restoration steps."""
from __future__ import annotations

import logging
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

BACKUP_DIR = Path("/var/backups/ai-social-generator")
TARGET_DIR = Path("/var/www/ai-social-generator")


def restore_latest_backup() -> None:
    backups = sorted(BACKUP_DIR.glob("backup_*.tar.gz"), reverse=True)
    if not backups:
        raise RuntimeError("No backups found to restore.")

    latest = backups[0]
    logging.info("Restoring backup: %s", latest)

    subprocess.run(["tar", "-xzf", str(latest), "-C", "/"], check=True)


def restart_services() -> None:
    logging.info("Restarting supervisor-managed services")
    subprocess.run(["sudo", "supervisorctl", "restart", "all"], check=True)


if __name__ == "__main__":
    restore_latest_backup()
    restart_services()
