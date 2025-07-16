"""
WebSocket Connection Manager for Claude Code Observatory.

Handles WebSocket connections, subscriptions, and real-time broadcasting.
"""
import json
import uuid
from datetime import datetime
from typing import Dict, Set, List
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections with subscription-based broadcasting.
    """
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[str]] = {
            "all_conversations": set(),
            "project_updates": set(),
            "file_events": set(),
        }
        self.client_metadata: Dict[str, dict] = {}

    async def connect(self, websocket: WebSocket, user_info: dict = None, subscriptions: List[str] = None) -> str:
        """Connect a new WebSocket client with user authentication."""
        await websocket.accept()
        
        client_id = str(uuid.uuid4())
        self.active_connections[client_id] = websocket
        
        # Default subscriptions
        if not subscriptions:
            subscriptions = ["all_conversations", "file_events"]
        
        # Add to subscription groups
        for subscription in subscriptions:
            if subscription in self.subscriptions:
                self.subscriptions[subscription].add(client_id)
        
        # Store client metadata with user info
        self.client_metadata[client_id] = {
            "connected_at": datetime.utcnow(),
            "subscriptions": subscriptions,
            "message_count": 0,
            "user_info": user_info or {}
        }
        
        # Send connection confirmation
        await self._send_to_client(client_id, {
            "type": "connection_established",
            "data": {
                "client_id": client_id,
                "subscriptions": subscriptions,
                "server_time": datetime.utcnow().isoformat(),
                "user_id": user_info.get('user_id') if user_info else None
            },
            "timestamp": datetime.utcnow().isoformat()
        })
        
        user_id = user_info.get('user_id') if user_info else 'anonymous'
        logger.info(f"WebSocket client {client_id} connected for user {user_id}")
        return client_id

    def disconnect(self, client_id: str):
        """Disconnect a WebSocket client."""
        # Remove from all subscription groups
        for subscription_set in self.subscriptions.values():
            subscription_set.discard(client_id)
        
        # Clean up metadata
        self.active_connections.pop(client_id, None)
        self.client_metadata.pop(client_id, None)
        
        logger.info(f"WebSocket client {client_id} disconnected")

    async def _send_to_client(self, client_id: str, message: dict):
        """Send message to specific client."""
        websocket = self.active_connections.get(client_id)
        if not websocket:
            raise ValueError(f"Client {client_id} not found")
        
        await websocket.send_text(json.dumps(message))
        
        # Update client metrics
        if client_id in self.client_metadata:
            self.client_metadata[client_id]["message_count"] += 1


# Global connection manager instance
connection_manager = ConnectionManager()