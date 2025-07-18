"""Input validation & sanitisation utilities.

Because file uploads are a primary attack vector, we validate both the
*content* and *metadata* of incoming files.  Validation failures raise
:class:`ValueError` with a human-readable explanation that can be surfaced to
clients.
"""
from __future__ import annotations

import os
import pathlib
import re
import uuid
from typing import Iterable

import magic  # python-magic – *not* file-magic
from werkzeug.utils import secure_filename

AUDIO_MIME_TYPES: set[str] = {
    "audio/mpeg",
    "audio/wav",
    "audio/x-wav",
    "audio/x-wave",
    "audio/vnd.wave",
    "audio/ogg",
    "audio/flac",
}

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _is_allowed_audio(mime_type: str) -> bool:
    return mime_type.lower() in AUDIO_MIME_TYPES


# ---------------------------------------------------------------------------
# Public validation API
# ---------------------------------------------------------------------------


def sanitise_filename(filename: str) -> str:  # noqa: D401
    """Return a filesystem-safe version of *filename*.

    Uses :func:`werkzeug.utils.secure_filename` and appends a UUID if the name
    would otherwise be empty.
    """
    filename = secure_filename(filename)
    if not filename:
        filename = f"upload_{uuid.uuid4().hex}"
    return filename


def validate_upload_path(upload_dir: str, filename: str) -> pathlib.Path:
    """Prevent path-traversal by ensuring *filename* resides in *upload_dir*."""
    upload_dir_path = pathlib.Path(upload_dir).resolve()
    full_path = (upload_dir_path / filename).resolve()
    if not str(full_path).startswith(str(upload_dir_path)):
        raise ValueError("Invalid file path; potential path traversal attempt detected.")
    return full_path


HEADER_BYTES = 2048  # Read first 2 KiB for mime-sniffing


def validate_audio_file(path: str | os.PathLike[str]) -> None:
    """Validate that *path* points to a genuine audio file by header sniffing."""
    mime = magic.from_file(str(path), mime=True)
    if not _is_allowed_audio(mime):
        raise ValueError(f"Unsupported or invalid audio mime-type detected: {mime}")


JSON_KEY_RE = re.compile(r"^[a-zA-Z0-9_]+$")


def validate_json_keys(data: dict[str, object], *, allowed: Iterable[str] | None = None) -> None:
    """Validate keys of incoming JSON payloads.

    Ensures keys are alphanumeric/underscore, preventing prototype pollution &
    other common attacks.  Optional *allowed* restricts keys strictly.
    """
    for key in data:
        if not JSON_KEY_RE.fullmatch(key):
            raise ValueError(f"Illegal JSON key: {key}")
    if allowed is not None:
        extra = set(data) - set(allowed)
        if extra:
            raise ValueError(f"Unexpected JSON fields: {', '.join(extra)}")
