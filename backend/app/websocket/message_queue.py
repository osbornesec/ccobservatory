"""
Message queue implementation for WebSocket broadcasting.

This module provides priority-based message queuing for WebSocket communications,
ensuring high-priority messages are delivered first while maintaining FIFO order
for messages of the same priority.
"""

import heapq
import time
from dataclasses import dataclass
from typing import Optional


class MessagePriority:
    """Message priority enumeration"""
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass
class PriorityMessage:
    """Message with priority for WebSocket broadcasting"""
    content: str
    priority: MessagePriority
    timestamp: float
    client_id: str
    
    def __lt__(self, other):
        """Lower priority value = higher priority (min heap)"""
        return self.priority.value < other.priority.value


class PriorityMessageQueue:
    """Priority message queue for WebSocket broadcasting"""
    
    def __init__(self):
        self._queue = []
        self._entry_finder = {}
        self._counter = 0
    
    def enqueue(self, message: PriorityMessage):
        """Add message to priority queue"""
        # Handle both enum-like objects and direct integer values
        priority_value = message.priority.value if hasattr(message.priority, 'value') else message.priority
        entry = [priority_value, self._counter, message]
        self._entry_finder[message.client_id] = entry
        heapq.heappush(self._queue, entry)
        self._counter += 1
    
    def dequeue(self) -> Optional[PriorityMessage]:
        """Remove and return highest priority message"""
        while self._queue:
            priority, count, message = heapq.heappop(self._queue)
            if message is not None:
                del self._entry_finder[message.client_id]
                return message
        return None
    
    def size(self) -> int:
        """Return queue size"""
        return len([entry for entry in self._queue if entry[2] is not None])
    
    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return self.size() == 0