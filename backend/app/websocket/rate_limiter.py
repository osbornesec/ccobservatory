"""
Rate limiting for WebSocket broadcasting.

This module provides token bucket rate limiting functionality for WebSocket
communications, preventing client overload by controlling message throughput.
"""

import time


class TokenBucketRateLimiter:
    """Token bucket rate limiter for WebSocket broadcasting"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
    
    def allow_request(self) -> bool:
        """Check if request is allowed and consume token"""
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