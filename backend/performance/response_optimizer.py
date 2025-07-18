"""Flask response optimisation middleware (gzip + caching headers)."""
from __future__ import annotations

import functools
import gzip
import io
import logging
import zlib
from datetime import timedelta
from typing import Callable

from flask import Response, request

logger = logging.getLogger(__name__)


class ResponseOptimizer:
    """Wraps a WSGI application to compress JSON responses and set cache headers."""

    def __init__(self, app, *, compress_level: int = 6) -> None:  # WSGI app
        self.app = app
        self.compress_level = compress_level

    def __call__(self, environ, start_response):  # noqa: D401
        # Detect client gzip support
        accept_encoding = environ.get("HTTP_ACCEPT_ENCODING", "")
        gzip_supported = "gzip" in accept_encoding.lower()

        buffer: list[bytes] = []

        def _write(data: bytes):  # noqa: D401
            buffer.append(data)

        def _start_response(status, headers, exc_info=None):  # noqa: D401
            nonlocal buffer
            if gzip_supported and status.startswith("200"):  # Only compress success
                headers = [(k.lower(), v) for k, v in headers]
                # Remove existing content-length because it will change after compression
                headers = [(k, v) for k, v in headers if k != "content-length"]
                headers.append(("Content-Encoding", "gzip"))
            # Add Keep-Alive
            headers.append(("Connection", "keep-alive"))
            # Add standard caching header for static-ish json (can be tuned)
            headers.append(("Cache-Control", "no-store"))
            return start_response(status, headers, exc_info)

        result = self.app(environ, _start_response)
        data = b"".join(buffer + list(result))
        if gzip_supported:
            out = io.BytesIO()
            with gzip.GzipFile(fileobj=out, mode="wb", compresslevel=self.compress_level) as gz:
                gz.write(data)
            data = out.getvalue()
        return [data]


# Convenient factory for Flask

def init_response_optimizer(app):  # noqa: D401
    app.wsgi_app = ResponseOptimizer(app.wsgi_app)  # type: ignore[attr-defined]
