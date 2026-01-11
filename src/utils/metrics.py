import time
from collections import defaultdict

class Metrics:
    EMBEDDING_LATENCY = "embedding_latency_ms"
    QUERY_LATENCY = "query_latency_ms"
    API_CALLS = "api_calls"
    API_ERRORS = "api_errors"
    TOKENS_USED = "tokens_used"

class MetricsTracker:
    def __init__(self):
        self.counters = defaultdict(int)
        self.timers = defaultdict(list)

    def increment(self, metric: str, amount: int = 1):
        self.counters[metric] += amount

    def record(self, metric: str, value: float):
        self.timers[metric].append(value)

    def get_summary(self):
        summary = {}
        for k, v in self.counters.items():
            summary[k] = v
        for k, lst in self.timers.items():
            if lst:
                summary[f"{k}_avg"] = sum(lst) / len(lst)
                summary[f"{k}_max"] = max(lst)
        return summary

_global_tracker = MetricsTracker()

def get_metrics():
    return _global_tracker
