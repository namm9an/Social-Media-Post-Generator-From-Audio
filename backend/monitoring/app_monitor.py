"""Application monitoring utilities – exposes metrics & health info."""
from __future__ import annotations

import logging
import time
from statistics import mean
from typing import Dict, List

logger = logging.getLogger(__name__)


class MetricStore:
    """In-memory store for simple time-series metrics."""

    def __init__(self) -> None:
        self.response_times: List[float] = []
        self.errors: int = 0
        self.request_count: int = 0

    # ---------------------------------------------------------------------
    # API
    # ---------------------------------------------------------------------

    def record_request(self, duration: float, *, error: bool) -> None:
        self.request_count += 1
        self.response_times.append(duration)
        if error:
            self.errors += 1

    # ------------------------- Exposed metrics ---------------------------

    @property
    def avg_response_ms(self) -> float:
        return mean(self.response_times) * 1000 if self.response_times else 0.0

    @property
    def error_rate(self) -> float:
        if self.request_count == 0:
            return 0.0
        return self.errors / self.request_count


metric_store = MetricStore()


# ---------------------------------------------------------------------------
# Flask integration helpers
# ---------------------------------------------------------------------------


def register_middleware(app):  # noqa: D401
    """Attach before/after request hooks to *app* for automatic metrics."""

    @app.before_request
    def _start_timer():  # noqa: D401, WPS430
        # type: ignore[unused-variable]
        request_ctx = getattr(app, "_request_ctx_stack", None)
        if request_ctx:  # pragma: no cover – Flask <2.3
            request_ctx.top.start_time = time.perf_counter()
        else:
            from flask import g

            g.start_time = time.perf_counter()

    @app.after_request
    def _record_metrics(response):  # noqa: D401
        from flask import g, request

        start_time = getattr(g, "start_time", None)
        if start_time is None:
            return response
        duration = time.perf_counter() - start_time
        metric_store.record_request(duration, error=response.status_code >= 500)
        # Attach Server-Timing header for easy client-side inspection
        response.headers["Server-Timing"] = f"app;dur={duration * 1000:.2f}"  # ms
        # CORS for Server-Timing (Firefox)
        response.headers.setdefault("Access-Control-Expose-Headers", "Server-Timing")
        return response
