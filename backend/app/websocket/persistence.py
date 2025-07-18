"""
Message persistence for WebSocket broadcasting.

This module provides message persistence functionality for WebSocket communications,
allowing messages to be stored and retrieved for offline clients or replay scenarios.
"""

import time
import logging
import threading
from dataclasses import dataclass
from typing import Optional, List, Dict
from collections import OrderedDict


@dataclass
class PersistedMessage:
    """Persisted message for WebSocket broadcasting"""
    id: str
    content: str
    timestamp: float
    channel: str
    expires_at: Optional[float] = None


class MessagePersistence:
    """Message persistence for WebSocket broadcasting with capacity limits and error handling"""
    
    def __init__(self, max_capacity: int = 10000):
        """
        Initialize message persistence with capacity limits and thread safety.
        
        Args:
            max_capacity: Maximum number of messages to store. Defaults to 10,000.
        """
        self.max_capacity = max_capacity
        self.storage: OrderedDict[str, PersistedMessage] = OrderedDict()
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
    
    def persist_message(self, message: PersistedMessage) -> bool:
        """
        Store message in persistence layer with capacity management and error handling.
        Thread-safe operation using internal locking.
        
        Args:
            message: The message to persist
            
        Returns:
            bool: True if message was successfully persisted, False otherwise
        """
        try:
            with self._lock:
                # Check if we've reached capacity
                if len(self.storage) >= self.max_capacity:
                    if message.id not in self.storage:
                        # Remove the oldest message to make room
                        oldest_id, oldest_msg = self.storage.popitem(last=False)
                        self.logger.info(f"Storage capacity reached ({self.max_capacity}). Removed oldest message {oldest_id}")
                
                # Store the message (updates existing or adds new)
                self.storage[message.id] = message
                
                # Move to end if updating existing message to maintain LRU order
                if message.id in self.storage:
                    self.storage.move_to_end(message.id)
                
                self.logger.debug(f"Successfully persisted message {message.id} to channel {message.channel}")
                return True
            
        except Exception as e:
            self.logger.error(f"Failed to persist message {message.id}: {str(e)}", exc_info=True)
            return False
    
    def message_exists(self, message_id: str) -> bool:
        """Check if message exists in storage. Thread-safe operation."""
        with self._lock:
            return message_id in self.storage
    
    def get_messages_for_channel(self, channel: str) -> List[PersistedMessage]:
        """Get all messages for a channel. Thread-safe operation."""
        with self._lock:
            return [msg for msg in self.storage.values() if msg.channel == channel]
    
    def cleanup_expired_messages(self):
        """Remove expired messages from storage. Thread-safe operation."""
        try:
            with self._lock:
                current_time = time.time()
                expired_ids = [
                    msg_id for msg_id, msg in self.storage.items()
                    if msg.expires_at and msg.expires_at < current_time
                ]
                for msg_id in expired_ids:
                    del self.storage[msg_id]
                
                if expired_ids:
                    self.logger.info(f"Cleaned up {len(expired_ids)} expired messages")
                
        except Exception as e:
            self.logger.error(f"Error during cleanup of expired messages: {str(e)}", exc_info=True)
    
    def get_storage_stats(self) -> Dict[str, int]:
        """Get storage statistics. Thread-safe operation."""
        with self._lock:
            storage_len = len(self.storage)
            return {
                "total_messages": storage_len,
                "max_capacity": self.max_capacity,
                "available_capacity": self.max_capacity - storage_len,
                "capacity_usage_percent": int((storage_len / self.max_capacity) * 100)
            }
    
    def is_near_capacity(self, threshold_percent: float = 90.0) -> bool:
        """Check if storage is near capacity. Thread-safe operation."""
        with self._lock:
            usage_percent = (len(self.storage) / self.max_capacity) * 100
            return usage_percent >= threshold_percent