"""Wall-time and peak-RSS measurement for training/inference cost reporting."""

import threading
import time
from contextlib import contextmanager

import psutil


class _Usage:
    elapsed_s: float = 0.0
    peak_rss_mb: float = 0.0  # process-wide peak during the block
    delta_rss_mb: float = 0.0  # peak minus RSS at block entry: the block's own footprint


@contextmanager
def measure(sample_interval_s: float = 0.05):
    """Measure wall time and peak process RSS (sampled) inside the block.

    RSS is process-wide, so run one model at a time for meaningful numbers.
    """
    proc = psutil.Process()
    usage = _Usage()
    start_rss = proc.memory_info().rss
    peak = start_rss
    stop = threading.Event()

    def _sample():
        nonlocal peak
        while not stop.is_set():
            peak = max(peak, proc.memory_info().rss)
            stop.wait(sample_interval_s)

    sampler = threading.Thread(target=_sample, daemon=True)
    start = time.perf_counter()
    sampler.start()
    try:
        yield usage
    finally:
        stop.set()
        sampler.join()
        usage.elapsed_s = time.perf_counter() - start
        final_peak = max(peak, proc.memory_info().rss)
        usage.peak_rss_mb = final_peak / 1e6
        usage.delta_rss_mb = (final_peak - start_rss) / 1e6
