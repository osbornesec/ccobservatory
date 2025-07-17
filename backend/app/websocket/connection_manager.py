"""
WebSocket Connection Manager for Claude Code Observatory.

Handles WebSocket connections, subscriptions, and real-time broadcasting.
"""
import json
import uuid
from datetime import datetime
from typing import Dict, Set, List, Optional
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect
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

    async def connect(self, websocket: WebSocket, subscriptions: List[str] = None) -> str:
        """Connect a new WebSocket client."""
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
        
        # Store client metadata
        self.client_metadata[client_id] = {
            "connected_at": datetime.utcnow(),
            "subscriptions": subscriptions,
            "message_count": 0
        }
        
        # Send connection confirmation
        await self._send_to_client(client_id, {
            "type": "connection_established",
            "data": {
                "client_id": client_id,
                "subscriptions": subscriptions,
                "server_time": datetime.utcnow().isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info(f"WebSocket client {client_id} connected")
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

    async def broadcast(self, message: dict, subscription_filter: Optional[str] = None):
        """Broadcast a message to connected clients.
        
        Args:
            message: JSON message to broadcast containing type and data
            subscription_filter: Optional filter (e.g., "conversation:123")
            
        Returns:
            List of client IDs that failed to receive the message
        """
        # Track failed clients
        failed_clients = []
        
        # Ensure consistent message format with timestamp
        broadcast_message = {
            "type": message.get("type", "unknown"),
            "data": message.get("data", {}),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            message_json = json.dumps(broadcast_message)
        except (TypeError, ValueError) as e:
            logger.error(f"JSON serialization error: {e}")
            return []  # Return empty list for failed serialization
        
        # If no filter, send to all clients (existing behavior)
        if subscription_filter is None:
            for client_id, websocket in self.active_connections.items():
                try:
                    await websocket.send_text(message_json)
                except (WebSocketDisconnect, RuntimeError):
                    # Client disconnected or connection error, track failure and continue
                    failed_clients.append(client_id)
                    continue
        else:
            # Collect all client IDs that should receive this message
            target_clients = set()
            
            # Special case: "all_conversations" filter sends to ALL connected clients
            if subscription_filter == "all_conversations":
                target_clients.update(self.active_connections.keys())
            else:
                # Add clients subscribed to the specific filter
                if subscription_filter in self.subscriptions:
                    target_clients.update(self.subscriptions[subscription_filter])
                
                # Add clients subscribed to "all_conversations" (they get all messages)
                if "all_conversations" in self.subscriptions:
                    target_clients.update(self.subscriptions["all_conversations"])
            
            # Send to all target clients
            for client_id in target_clients:
                if client_id in self.active_connections:
                    websocket = self.active_connections[client_id]
                    try:
                        await websocket.send_text(message_json)
                    except (WebSocketDisconnect, RuntimeError):
                        # Client disconnected or connection error, track failure and continue
                        failed_clients.append(client_id)
                        continue
        
        # Return list of failed clients
        return failed_clients


# Global connection manager instance
connection_manager = ConnectionManager()