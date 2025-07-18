#!/usr/bin/env python3
"""Simple daily backup script for application data.

This script creates timestamped tar.gz archives of the *uploads* and *config*
directories and rotates old backups according to a retention policy.

Usage (cron):
    0 2 * * * /usr/bin/python3 /var/www/ai-social-generator/scripts/backup_system.py
"""
from __future__ import annotations

import datetime as _dt
import logging
import os
import shutil
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

BACKUP_DIR = Path(os.getenv("BACKUP_DIR", "/var/backups/ai-social-generator"))
SOURCE_DIRS = [
    Path(os.getenv("UPLOAD_FOLDER", "/var/www/ai-social-generator/uploads")),
    Path("/etc/ai-social-generator"),
]
RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", "14"))


def _create_backup() -> Path:
    ts = _dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    archive_name = BACKUP_DIR / f"backup_{ts}.tar.gz"
    logging.info("Creating backup: %s", archive_name)

    with subprocess.Popen([
        "tar",
        "-czf",
        str(archive_name),
        *map(str, SOURCE_DIRS),
    ]) as proc:
        proc.wait()
        if proc.returncode != 0:
            raise RuntimeError("Backup creation failed")
    return archive_name


def _cleanup_old_backups() -> None:
    threshold = _dt.datetime.utcnow() - _dt.timedelta(days=RETENTION_DAYS)
    for f in BACKUP_DIR.glob("backup_*.tar.gz"):
        ts_part = f.stem.split("_")[1]
        try:
            ts = _dt.datetime.strptime(ts_part, "%Y%m%dT%H%M%SZ")
        except ValueError:
            continue
        if ts < threshold:
            logging.info("Deleting old backup: %s", f)
            f.unlink()


if __name__ == "__main__":
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    _create_backup()
    _cleanup_old_backups()
