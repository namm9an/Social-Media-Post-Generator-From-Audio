"""Rate limiting utility for production security.

Uses Flask-Limiter to protect API endpoints from abuse and denial-of-service
attacks.  The limits are deliberately conservative and can be tuned via
environment variables or configuration files.

To keep things flexible, every endpoint can have its own limit while a global
limit applies to all endpoints.  Trusted IPs can be whitelisted via the
RATE_LIMIT_WHITELIST environment variable (comma-separated list).
"""
from __future__ import annotations

import os
from typing import List

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def _parse_whitelist(env_value: str | None) -> List[str]:
    """Parse the comma-separated whitelist env variable into a clean list."""
    if not env_value:
        return []
    return [ip.strip() for ip in env_value.split(",") if ip.strip()]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def init_rate_limiter(app: Flask) -> Limiter:  # noqa: D401
    """Initialise & attach a :class:`~flask_limiter.Limiter` instance to *app*.

    The configuration is intentionally hard-coded to sane production defaults
    but can be overridden via environment variables:

    * ``GLOBAL_RATE_LIMIT`` (default: ``"100 per hour"``)
    * ``UPLOAD_RATE_LIMIT`` (default: ``"5 per minute"``)
    * ``TRANSCRIBE_RATE_LIMIT`` (default: ``"3 per minute"``)
    * ``GENERATE_RATE_LIMIT`` (default: ``"10 per minute"``)
    * ``RATE_LIMIT_WHITELIST`` – comma-separated list of IP addresses that are
      completely exempt from the limiter (e.g., internal load balancers).
    """

    global_limit = os.getenv("GLOBAL_RATE_LIMIT", "100 per hour")
    upload_limit = os.getenv("UPLOAD_RATE_LIMIT", "5 per minute")
    transcribe_limit = os.getenv("TRANSCRIBE_RATE_LIMIT", "3 per minute")
    generate_limit = os.getenv("GENERATE_RATE_LIMIT", "10 per minute")

    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[global_limit],
        storage_uri=os.getenv("RATE_LIMIT_STORAGE_URI", "memory://"),
        headers_enabled=True,
    )

    # Whitelist handling – iterate after limiter initialisation so the config
    # object exists.
    whitelist = set(_parse_whitelist(os.getenv("RATE_LIMIT_WHITELIST")))
    for ip in whitelist:
        limiter.request_filter(lambda: get_remote_address() == ip)  # type: ignore[arg-type]

    # ---------------------------------------------------------------------
    # Endpoint-specific limits – functions must already be registered on the
    # Flask application before this initialiser is called.  Therefore the
    # initialiser should run *after* all view functions are defined but
    # *before* the app starts serving requests.
    # ---------------------------------------------------------------------
    endpts = app.view_functions
    if "upload_file" in endpts:
        limiter.limit(upload_limit)(endpts["upload_file"])
    if "transcribe_audio" in endpts:
        limiter.limit(transcribe_limit)(endpts["transcribe_audio"])
    if "generate_posts" in endpts:
        limiter.limit(generate_limit)(endpts["generate_posts"])

    return limiter
