"""
Message persistence for WebSocket broadcasting.

This module provides message persistence functionality for WebSocket communications,
allowing messages to be stored and retrieved for offline clients or replay scenarios.
"""

import time
from dataclasses import dataclass
from typing import Optional, List, Dict


from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional, List, Dict
from uuid import UUID

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
    """Message persistence for WebSocket broadcasting"""
    
    def __init__(self):
        self.storage: Dict[str, PersistedMessage] = {}
    
    def persist_message(self, message: PersistedMessage) -> bool:
        """Store message in persistence layer"""
        self.storage[message.id] = message
        return True
    
    def message_exists(self, message_id: str) -> bool:
        """Check if message exists in storage"""
        return message_id in self.storage
    
    def get_messages_for_channel(self, channel: str) -> List[PersistedMessage]:
        """Get all messages for a channel"""
        return [msg for msg in self.storage.values() if msg.channel == channel]
    
# Add at the top of the file
import threading
from datetime import datetime, timezone

class MessagePersistence:
    def __init__(self, max_messages: int = 10000, auto_cleanup_interval: int = 300):
        # ... existing initialization ...
        self._lock = threading.Lock()

    def cleanup_expired_messages(self):
        """Remove expired messages from storage.

        Returns:
            Number of messages cleaned up
        """
        with self._lock:
            current_time = datetime.now(timezone.utc)
            expired_ids = [
                msg_id for msg_id, msg in self.storage.items()
                if msg.expires_at and msg.expires_at < current_time
            ]

            for msg_id in expired_ids:
                del self.storage[msg_id]

            if expired_ids:
                logger.info(f"Cleaned up {len(expired_ids)} expired messages")

            self._last_cleanup = current_time
            return len(expired_ids)

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

        logger.info(f"Cleaned up {remove_count} oldest messages due to capacity limit")