"""Lightweight interface to ClamAV via *pyclamd* if present.

If ClamAV daemon isn't running or pyclamd isn't installed, the scanner will
fallback to a *no-op* that logs a warning.  This keeps the application running
in development environments while providing real scanning in production.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Final

logger = logging.getLogger(__name__)

try:
    import pyclamd  # type: ignore

    _CD = pyclamd.ClamdAgnostic()
    if not _CD.ping():
        raise RuntimeError("ClamAV daemon not responding")

    def scan_file(path: str | Path) -> None:  # noqa: D401
        """Raise ``ValueError`` if *path* is infected."""
        result = _CD.scan_file(str(path))
        if result:
            sig = result[str(path)][1]
            raise ValueError(f"Virus detected ({sig}) in file: {path}")

    ACTIVE: Final[bool] = True
except Exception as exc:  # pragma: no cover – falls back if not available

    logger.warning("Virus scanner disabled: %s", exc)

    def scan_file(path):  # type: ignore[override]  # noqa: D401
        """No-op scanner used when ClamAV unavailable."""
        return None

    ACTIVE: Final[bool] = False
