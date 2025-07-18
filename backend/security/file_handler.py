"""Secure file handling utilities.

Key responsibilities:
1. Verify uploads using magic numbers (content-based detection).
2. Store files outside web root in a dedicated uploads directory.
3. Provide quarantine path for suspicious files.
4. Log all file operations.
"""
from __future__ import annotations

import logging
import os
import shutil
import uuid
from pathlib import Path
from typing import Tuple

import magic  # type: ignore

from backend.security.input_validator import sanitise_filename, validate_audio_file

logger = logging.getLogger(__name__)

UPLOAD_ROOT = Path(os.getenv("UPLOAD_FOLDER", "../uploads/audio")).resolve()
QUARANTINE_ROOT = Path(os.getenv("QUARANTINE_FOLDER", "../uploads/quarantine")).resolve()

UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
QUARANTINE_ROOT.mkdir(parents=True, exist_ok=True)


def _store_file(file_stream, filename: str) -> Path:
    path = UPLOAD_ROOT / filename
    with path.open("wb") as f:
        shutil.copyfileobj(file_stream, f)
    return path


def save_secure_file(file_storage) -> Tuple[bool, str]:
    """Save an uploaded file securely.

    Returns a tuple (success, file_id or error_message).
    """
    # Sanitise & generate unique filename
    safe_name = sanitise_filename(file_storage.filename)
    file_id = uuid.uuid4().hex
    final_name = f"{file_id}_{safe_name}"

    try:
        path = _store_file(file_storage.stream, final_name)
        from backend.security.virus_scanner import scan_file
        # Virus scan first
        scan_file(path)
        # Validate magic header
        validate_audio_file(path)
        logger.info("Secure upload saved: %s", path)
        return True, file_id
    except Exception as exc:  # pragma: no cover
        logger.exception("File failed validation – moving to quarantine: %s", exc)
        quarantine_path = QUARANTINE_ROOT / final_name
        shutil.move(str(path), quarantine_path, copy_function=shutil.copy2)
        return False, str(exc)
