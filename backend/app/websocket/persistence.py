"""
Message persistence for WebSocket broadcasting.

This module provides message persistence functionality for WebSocket communications,
allowing messages to be stored and retrieved for offline clients or replay scenarios.
"""

import time
from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass
class PersistedMessage:
    """Persisted message for WebSocket broadcasting"""
    id: str
    content: str
    timestamp: float
    channel: str
    expires_at: Optional[float] = None


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
    
    def cleanup_expired_messages(self):
        """Remove expired messages from storage"""
        current_time = time.time()
        expired_ids = [
            msg_id for msg_id, msg in self.storage.items()
            if msg.expires_at and msg.expires_at < current_time
        ]
        for msg_id in expired_ids:
            del self.storage[msg_id]