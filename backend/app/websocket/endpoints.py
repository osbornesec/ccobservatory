"""
WebSocket endpoints for Claude Code Observatory.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import List, Optional
import logging

from .connection_manager import connection_manager
from app.auth.dependencies import validate_websocket_token
from app.auth.middleware import AuthenticationError
from app.database.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: Optional[str] = Query(None)):
    """
    WebSocket endpoint for real-time communication with authentication.
    
    Args:
        websocket: WebSocket connection
        token: JWT authentication token passed as query parameter
    """
    client_id = None
    user_info = None
    
    try:
        # Authenticate user before accepting connection
        if not token:
            logger.warning("WebSocket connection attempt without authentication token")
            await websocket.close(code=1008, reason="Authentication required")
            return
        
        try:
            # Validate authentication token
            supabase_client = get_supabase_client()
            user_info = validate_websocket_token(token, supabase_client)
            logger.info(f"WebSocket authentication successful for user: {user_info.get('user_id')}")
            
        except AuthenticationError as e:
            logger.warning(f"WebSocket authentication failed: {e}")
            await websocket.close(code=1008, reason="Authentication failed")
            return
        except Exception as e:
            logger.error(f"WebSocket authentication error: {e}")
            await websocket.close(code=1011, reason="Authentication service error")
            return
        
        # Connect the authenticated client
        client_id = await connection_manager.connect(websocket, user_info)
        logger.info(f"WebSocket client {client_id} connected for user {user_info.get('user_id')}")
        
        # Keep connection alive and handle messages
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            # For now, just echo or handle ping/pong
            # In future iterations, this will handle real-time data updates
            
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
    finally:
        if client_id:
            connection_manager.disconnect(client_id)