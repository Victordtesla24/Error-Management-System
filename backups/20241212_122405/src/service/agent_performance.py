import time
from contextlib import contextmanager
from dataclasses import dataclass
from logging import getLogger
from typing import Any, Dict

logger = getLogger(__name__)


@dataclass
class PerformanceResult:
    status: str
    metrics: Dict[str, Any] = None


@contextmanager
def timeout_context(seconds: int):
    """Context manager for timing out operations"""
    import signal

    def timeout_handler(signum, frame):
        raise TimeoutError("Operation timed out")

    original_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, original_handler)


class AgentPerformanceMonitor:
    def analyze_performance(self, timeout=55):
        time.time()
        try:
            with timeout_context(timeout):
                metrics = self.collect_metrics()
                analysis = self.process_metrics(metrics)
                return analysis
        except TimeoutError:
            logger.error("Performance analysis timed out")
            return PerformanceResult(status="timeout")
