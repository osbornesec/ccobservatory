"""
High-performance broadcast manager for Claude Code Observatory.

Provides efficient message broadcasting to WebSocket connections
with performance optimizations for large-scale deployments.
"""

import asyncio
import json
import time
from typing import Dict, List, Set, Optional, Any
import logging

logger = logging.getLogger(__name__)


class BroadcastManager:
    """
    High-performance broadcast manager for WebSocket connections.
    
    Optimized for low-latency message broadcasting with support for
    large payloads and high connection counts.
    """
    
    def __init__(self):
        self.connections: Dict[str, Any] = {}
        self.connection_count = 0
        self._lock = asyncio.Lock()
    
    def add_connection(self, connection: Any) -> None:
        """Add a connection to the broadcast manager."""
        connection_id = getattr(connection, 'connection_id', str(id(connection)))
        self.connections[connection_id] = connection
        self.connection_count += 1
    
    def remove_connection(self, connection: Any) -> None:
        """Remove a connection from the broadcast manager."""
        connection_id = getattr(connection, 'connection_id', str(id(connection)))
        if connection_id in self.connections:
            del self.connections[connection_id]
            self.connection_count -= 1
    
    async def broadcast(self, message: str) -> List[str]:
        """
        Broadcast a message to all connected clients.
        
        Args:
            message: JSON string message to broadcast
            
        Returns:
            List of connection IDs that failed to receive the message
        """
        if not self.connections:
            return []
        
        failed_connections = []
        
        # Use asyncio.gather for concurrent message sending
        async def send_to_connection(connection_id: str, connection: Any) -> Optional[str]:
            try:
                if hasattr(connection, 'closed') and connection.closed:
                    return connection_id
                    
async def send_to_connection(connection_id: str, connection: Any) -> Optional[str]:
    try:
        if hasattr(connection, 'closed') and connection.closed:
            return connection_id

        if not hasattr(connection, 'send'):
            logger.error(f"Connection {connection_id} does not have send method")
            return connection_id

        await connection.send(message)
        return None
    except Exception as e:
        logger.warning(f"Failed to send message to connection {connection_id}: {e}")
        return connection_id
                return None
            except Exception as e:
                logger.warning(f"Failed to send message to connection {connection_id}: {e}")
                return connection_id
        
        # Create tasks for all connections
        tasks = [
            send_to_connection(conn_id, conn)
            for conn_id, conn in self.connections.items()
        ]
        
        # Execute all sends concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect failed connections
        for result in results:
            if isinstance(result, str):  # Failed connection ID
                failed_connections.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Broadcast error: {result}")
        
        return failed_connections