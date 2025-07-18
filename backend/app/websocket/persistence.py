"""
Message persistence for WebSocket broadcasting.

This module provides message persistence functionality for WebSocket communications,
allowing messages to be stored and retrieved for offline clients or replay scenarios.
"""

import time
import logging
import threading
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional, List, Dict
from collections import OrderedDict
from uuid import UUID

logger = logging.getLogger(__name__)


@dataclass
class PersistedMessage:
    """Persisted message for WebSocket broadcasting.
    
    Attributes:
        id: Unique message identifier
        content: Message content (should be JSON serializable)
        timestamp: Message creation timestamp
        channel: Channel/topic for message routing
        expires_at: Optional expiration timestamp
    """
    id: str
    content: str
    timestamp: datetime
    channel: str
    expires_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate message data after initialization."""
        if not self.id.strip():
            raise ValueError("Message ID cannot be empty")
        if not self.channel.strip():
            raise ValueError("Channel cannot be empty")
        if self.expires_at and self.expires_at <= self.timestamp:
            raise ValueError("Expiration time must be after timestamp")


class MessagePersistence:
    """Message persistence for WebSocket broadcasting with capacity limits, error handling, and thread safety"""
    
    def __init__(self, max_messages: int = 10000, auto_cleanup_interval: int = 300):
        """
        Initialize message persistence with capacity limits and thread safety.
        
        Args:
            max_messages: Maximum number of messages to store. Defaults to 10,000.
            auto_cleanup_interval: Interval in seconds for automatic cleanup
        """
        self.max_messages = max_messages
        self.auto_cleanup_interval = auto_cleanup_interval
        self.storage: OrderedDict[str, PersistedMessage] = OrderedDict()
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
        self._last_cleanup = datetime.now(timezone.utc)
    
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
                if len(self.storage) >= self.max_messages:
                    if message.id not in self.storage:
                        # Remove the oldest message to make room
                        self._cleanup_oldest_messages()
                
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
    
    def cleanup_expired_messages(self) -> int:
        """Remove expired messages from storage. Thread-safe operation.

        Returns:
            Number of messages cleaned up
        """
        try:
            with self._lock:
                current_time = datetime.now(timezone.utc)
                expired_ids = [
                    msg_id for msg_id, msg in self.storage.items()
                    if msg.expires_at and msg.expires_at < current_time
                ]

                for msg_id in expired_ids:
                    del self.storage[msg_id]

                if expired_ids:
                    self.logger.info(f"Cleaned up {len(expired_ids)} expired messages")

                self._last_cleanup = current_time
                return len(expired_ids)
                
        except Exception as e:
            self.logger.error(f"Error during cleanup of expired messages: {str(e)}", exc_info=True)
            return 0

    def _cleanup_oldest_messages(self):
        """Remove oldest messages when capacity is exceeded."""
        if len(self.storage) < self.max_messages:
            return

        # Remove 10% of oldest messages
        remove_count = max(1, int(self.max_messages * 0.1))
        sorted_messages = sorted(
            self.storage.items(),
            key=lambda x: x[1].timestamp
        )

        for msg_id, _ in sorted_messages[:remove_count]:
            del self.storage[msg_id]

        self.logger.info(f"Cleaned up {remove_count} oldest messages due to capacity limit")
    
    def get_storage_stats(self) -> Dict[str, int]:
        """Get storage statistics. Thread-safe operation."""
        with self._lock:
            storage_len = len(self.storage)
            return {
                "total_messages": storage_len,
                "max_capacity": self.max_messages,
                "available_capacity": self.max_messages - storage_len,
                "capacity_usage_percent": int((storage_len / self.max_messages) * 100)
            }
    
    def is_near_capacity(self, threshold_percent: float = 90.0) -> bool:
        """Check if storage is near capacity. Thread-safe operation."""
        with self._lock:
            usage_percent = (len(self.storage) / self.max_messages) * 100
            return usage_percent >= threshold_percent