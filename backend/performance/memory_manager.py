"""Runtime memory management helpers for AI models.

These utilities are used by the application to keep the resident set size
below production thresholds.  They can be integrated with monitoring tools to
raise alerts when usage grows unexpectedly, indicating memory leaks.
"""
from __future__ import annotations

import gc
import logging
import os
import threading
import time
from dataclasses import dataclass
from typing import Callable, Dict

import psutil

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration dataclass (values in MiB)
# ---------------------------------------------------------------------------


@dataclass
class MemoryThresholds:
    warning: int = int(os.getenv("MEMORY_WARN_THRESHOLD_MB", "1024"))  # 1 GiB
    critical: int = int(os.getenv("MEMORY_CRIT_THRESHOLD_MB", "2048"))  # 2 GiB


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


class MemoryManager(threading.Thread):
    """Background thread that monitors process memory usage."""

    def __init__(
        self,
        thresholds: MemoryThresholds | None = None,
        interval: int = 30,
        cleanup_callback: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(daemon=True)
        self.thresholds = thresholds or MemoryThresholds()
        self.interval = interval
        self.cleanup_callback = cleanup_callback or gc.collect
        self._stop = threading.Event()

    @property
    def memory_mb(self) -> int:
        proc = psutil.Process(os.getpid())
        return int(proc.memory_info().rss / 1024 ** 2)

    def aggressive_cleanup(self):
        """Perform aggressive memory cleanup"""
        try:
            # Force multiple garbage collections
            for _ in range(3):
                gc.collect()
            
            # Clean up torch cache if available
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize()
            except ImportError:
                pass
            
            # Try to cleanup FLAN-T5 service if available
            try:
                from services.text_generation.flan_t5_service import flan_t5_service
                flan_t5_service.aggressive_cleanup()
            except ImportError:
                pass
            
            logger.info("Aggressive memory cleanup completed")
            
        except Exception as e:
            logger.error(f"Aggressive cleanup failed: {e}")
    
    def run(self) -> None:  # noqa: D401
        logger.info("MemoryManager started – monitoring every %s s", self.interval)
        while not self._stop.is_set():
            usage = self.memory_mb
            if usage >= self.thresholds.critical:
                logger.error("Critical memory usage: %s MiB – initiating cleanup", usage)
                self.aggressive_cleanup()
            elif usage >= self.thresholds.warning:
                logger.warning("High memory usage: %s MiB", usage)
                self.cleanup_callback()
            else:
                # Only log normal usage occasionally to reduce log noise
                if usage % 100 == 0 or usage > 500:  # Log every 100MB or if over 500MB
                    logger.info("Normal memory usage: %s MiB", usage)
            time.sleep(self.interval)

    def stop(self) -> None:
        self._stop.set()


# Registry of loaded models (name -> unload callable)
_LOADED_MODELS: Dict[str, Callable[[], None]] = {}


def register_model(name: str, unload_fn: Callable[[], None]) -> None:
    """Register a model *name* alongside an *unload_fn* for later unloading."""
    _LOADED_MODELS[name] = unload_fn


def unload_unused_models(active: set[str]) -> None:
    """Unload any models that are not currently *active* to save memory."""
    for name in list(_LOADED_MODELS):
        if name not in active:
            try:
                _LOADED_MODELS.pop(name)()
                logger.info("Unloaded model '%s' to free memory", name)
            except Exception as exc:  # pragma: no cover
                logger.exception("Failed to unload model %s: %s", name, exc)
