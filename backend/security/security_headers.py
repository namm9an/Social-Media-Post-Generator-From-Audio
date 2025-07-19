"""Apply secure HTTP headers & force HTTPS in production using Flask-Talisman."""
from __future__ import annotations

import os
from typing import Mapping

from flask import Flask
from flask_talisman import Talisman

DEFAULT_CSP: Mapping[str, str] = {
    "default-src": "'self'",
    "img-src":     "'self' data:",
    "media-src":   "'self'",
    "script-src":  "'self' https://cdn.jsdelivr.net",
    "style-src":   "'self' 'unsafe-inline' https://cdn.jsdelivr.net",
    "object-src":  "'none'",
}


def init_security_headers(app: Flask) -> Talisman:  # noqa: D401
    """Attach :class:`~flask_talisman.Talisman` to *app* with strict policy."""
    force_https = os.getenv("FORCE_HTTPS", "False").lower() in {"1", "true", "yes"}
    try:
        talisman = Talisman(
            app,
            content_security_policy=DEFAULT_CSP,
            force_https=force_https,
            strict_transport_security=True,
        )
    except TypeError:
        # Fallback for older versions of Flask-Talisman
        talisman = Talisman(
            app,
            csp=DEFAULT_CSP,
            force_https=force_https,
        )
    return talisman
