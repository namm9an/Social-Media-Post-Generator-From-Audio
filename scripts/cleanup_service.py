#!/usr/bin/env python3
"""Cleanup temporary & old files to conserve disk space."""
from __future__ import annotations

import datetime as _dt
import logging
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

UPLOAD_DIR = Path(os.getenv("UPLOAD_FOLDER", "/var/www/ai-social-generator/uploads/audio"))
TMP_DIR = Path(os.getenv("TMP_DIR", "/tmp/ai-social-generator"))
LOG_DIR = Path(os.getenv("LOG_DIR", "/var/log/ai-social-generator"))

FILE_AGE_DAYS = int(os.getenv("CLEANUP_FILE_AGE_DAYS", "7"))


def _remove_older_than(path: Path, *, days: int) -> None:
    cutoff = _dt.datetime.utcnow() - _dt.timedelta(days=days)
    for f in path.rglob("*"):
        if f.is_file():
            if _dt.datetime.utcfromtimestamp(f.stat().st_mtime) < cutoff:
                logging.info("Deleting old file: %s", f)
                f.unlink()


if __name__ == "__main__":
    for d in (UPLOAD_DIR, TMP_DIR, LOG_DIR):
        if d.exists():
            _remove_older_than(d, days=FILE_AGE_DAYS)
