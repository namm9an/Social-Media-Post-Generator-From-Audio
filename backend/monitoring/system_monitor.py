"""System resource monitoring helpers."""
from __future__ import annotations

import os
import platform
import time
from dataclasses import asdict, dataclass
from typing import Dict

import psutil


@dataclass
class SystemMetrics:
    cpu_percent: float
    memory_total_mb: int
    memory_used_mb: int
    load_average_1m: float
    disk_total_gb: float
    disk_used_gb: float
    bandwidth_sent_mb: float
    bandwidth_recv_mb: float
    process_count: int

    def to_dict(self) -> Dict[str, float]:  # noqa: D401
        return asdict(self)


_prev_net = psutil.net_io_counters()
_prev_time = time.time()


def capture_metrics() -> SystemMetrics:  # noqa: D401
    global _prev_net, _prev_time

    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    load1, _, _ = psutil.getloadavg()
    disk = psutil.disk_usage("/")
    net = psutil.net_io_counters()

    now = time.time()
    elapsed = now - _prev_time if now > _prev_time else 1

    sent_mb = (net.bytes_sent - _prev_net.bytes_sent) / 1024 ** 2 / elapsed
    recv_mb = (net.bytes_recv - _prev_net.bytes_recv) / 1024 ** 2 / elapsed

    _prev_net = net
    _prev_time = now

    return SystemMetrics(
        cpu_percent=cpu,
        memory_total_mb=int(mem.total / 1024 ** 2),
        memory_used_mb=int(mem.used / 1024 ** 2),
        load_average_1m=load1,
        disk_total_gb=disk.total / 1024 ** 3,
        disk_used_gb=disk.used / 1024 ** 3,
        bandwidth_sent_mb=sent_mb,
        bandwidth_recv_mb=recv_mb,
        process_count=len(psutil.pids()),
    )
