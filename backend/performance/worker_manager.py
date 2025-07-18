"""Simple threaded worker pool for concurrent request processing.

In production you'd typically use Celery/RQ/Kafka etc., but for the scope of
this project we implement a lightweight in-process queue so we can avoid extra
dependencies while still handling background jobs like transcription & text
generation without blocking the main Flask worker.
"""
from __future__ import annotations

import logging
import queue
import threading
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 300  # seconds


@dataclass
class Job:
    func: Callable[[], None]
    timeout: int = DEFAULT_TIMEOUT
    description: str = "anonymous job"


class Worker(threading.Thread):
    def __init__(self, job_queue: "queue.Queue[Job]", *, idx: int) -> None:
        super().__init__(daemon=True)
        self.job_queue = job_queue
        self.idx = idx
        self._stop = threading.Event()

    def run(self) -> None:  # noqa: D401
        logger.info("Worker-%s started", self.idx)
        while not self._stop.is_set():
            try:
                job = self.job_queue.get(timeout=1)
            except queue.Empty:
                continue
            start = time.time()
            logger.info("Worker-%s: starting job – %s", self.idx, job.description)
            try:
                job.func()
            except Exception as exc:  # pragma: no cover
                logger.exception("Worker-%s: job failed – %s", self.idx, exc)
            finally:
                duration = time.time() - start
                logger.info("Worker-%s: finished job – %s in %.2fs", self.idx, job.description, duration)
                self.job_queue.task_done()

    def stop(self) -> None:
        self._stop.set()


class WorkerManager:
    def __init__(self, max_workers: int = 4) -> None:
        self.job_queue: "queue.Queue[Job]" = queue.Queue()
        self.workers = [Worker(self.job_queue, idx=i + 1) for i in range(max_workers)]

        for w in self.workers:
            w.start()
        logger.info("Worker pool initialised with %s workers", max_workers)

    def submit_job(self, func: Callable[[], None], *, timeout: int = DEFAULT_TIMEOUT, description: str | None = None) -> None:
        if description is None:
            description = func.__name__
        self.job_queue.put(Job(func=func, timeout=timeout, description=description))

    def shutdown(self) -> None:
        logger.info("Shutting down worker pool")
        for w in self.workers:
            w.stop()
        for w in self.workers:
            w.join()
