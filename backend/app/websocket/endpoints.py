"""
WebSocket endpoints for Claude Code Observatory.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Optional
import logging

from .connection_manager import connection_manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time communication.
    """
    client_id = None
    
    try:
        # Connect the client
        client_id = await connection_manager.connect(websocket)
        
        # Keep connection alive and handle messages
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            # For now, just echo or handle ping/pong
            
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
    finally:
        if client_id:
            connection_manager.disconnect(client_id)