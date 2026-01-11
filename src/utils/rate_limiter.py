import time
import threading

# Simple token bucket rate limiter for OpenAI API calls

class RateLimiter:
    def __init__(self, max_calls: int = 60, interval_seconds: int = 60):
        self.max_calls = max_calls
        self.interval = interval_seconds
        self.lock = threading.Lock()
        self.call_times = []  # timestamps of recent calls

    def wait_if_needed(self):
        with self.lock:
            now = time.time()
            # Remove timestamps older than interval
            self.call_times = [t for t in self.call_times if now - t < self.interval]
            if len(self.call_times) >= self.max_calls:
                # Need to wait until earliest call expires
                earliest = self.call_times[0]
                wait_time = self.interval - (now - earliest) + 0.1
                if wait_time > 0:
                    time.sleep(wait_time)
            # Record this call
            self.call_times.append(time.time())

def with_retry(max_retries: int = 3, backoff_factor: float = 1.5):
    """Decorator to retry a function on exception with exponential backoff"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            delay = 1.0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if retries >= max_retries:
                        raise
                    time.sleep(delay)
                    delay *= backoff_factor
                    retries += 1
        return wrapper
    return decorator

# Global singleton
_global_rate_limiter = None

def get_rate_limiter(max_calls: int = 60, interval_seconds: int = 60):
    """Get or create global rate limiter instance"""
    global _global_rate_limiter
    if _global_rate_limiter is None:
        _global_rate_limiter = RateLimiter(max_calls, interval_seconds)
    return _global_rate_limiter

