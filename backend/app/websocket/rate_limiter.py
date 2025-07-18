"""
Rate limiting for WebSocket broadcasting.

This module provides token bucket rate limiting functionality for WebSocket
communications, preventing client overload by controlling message throughput.
"""

import time


class TokenBucketRateLimiter:
    """Token bucket rate limiter for WebSocket broadcasting.

    Args:
        capacity: Maximum number of tokens in the bucket
        refill_rate: Rate at which tokens are replenished (tokens per second)

    Raises:
        ValueError: If capacity <= 0 or refill_rate <= 0
    """

    def __init__(self, capacity: int, refill_rate: float) -> None:
        if capacity <= 0:
            raise ValueError("Capacity must be greater than 0")
        if refill_rate <= 0:
            raise ValueError("Refill rate must be greater than 0")

        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = time.time()
    
import threading

class TokenBucketRateLimiter:
    def __init__(self, capacity: int, refill_rate: float) -> None:
        # ... existing validation ...
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = time.time()
        self._lock = threading.Lock()

    def allow_request(self) -> bool:
        """Check if request is allowed and consume token"""
        with self._lock:
            self.refill_tokens()
            
            if self.tokens > 0:
                self.tokens -= 1
                return True
            return False
    
    def refill_tokens(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.refill_rate
        
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now