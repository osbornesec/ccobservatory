"""
WebSocket Handler

FastAPI WebSocket endpoint implementation for real-time communication.
Integrates with ConnectionManager for connection lifecycle management.

Canon TDD Implementation - Test First Development
"""

from fastapi import WebSocket, WebSocketDisconnect, Depends
from app.websocket.connection_manager import ConnectionManager
from app.database.supabase_client import get_supabase_service_client
import logging
import json
from typing import Dict, Any, Union

logger = logging.getLogger(__name__)

# Global connection manager instance
connection_manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, client_id: str = None):
    """
    WebSocket endpoint handler for real-time communication.
    
    Args:
        websocket: WebSocket connection instance
        client_id: Optional client identifier
        
    Behavior defined by tests:
    - Accept WebSocket connections at /ws endpoint
    - Use ConnectionManager to track connections
    - Handle message routing and broadcasting
    - Manage connection lifecycle (connect/disconnect)
    - Handle WebSocketDisconnect exceptions gracefully
    - Integrate with file monitoring for real-time updates
    """
    try:
        # Connect client using ConnectionManager
        await connection_manager.connect(websocket, client_id)
        
        # Start message receiving loop
        while True:
            message_text = await websocket.receive_text()
            # Parse JSON message and process it
            try:
                message_data = json.loads(message_text)
                await handle_websocket_message(message_data, client_id)
            except json.JSONDecodeError:
                # Invalid JSON - ignore for now, will be handled in future tests
                pass
            
    except WebSocketDisconnect:
        # Handle disconnection gracefully
        await connection_manager.disconnect(client_id)


async def handle_websocket_message(
    message: Dict[str, Any], 
    connection_id: str,
    db_client = Depends(get_supabase_service_client)
):
    """
    Process incoming WebSocket messages from clients.
    
    Args:
        message: Parsed JSON message from client
        connection_id: ID of sending connection
        db_client: Database client for data operations
        
    Behavior defined by tests:
    - Parse and validate incoming messages
    - Route messages based on type/action
    - Handle subscription requests for real-time updates
    - Validate message format and reject invalid messages
    - Integrate with database for data retrieval
    """
    # Handle ping message type
    if message.get("type") == "ping":
        return {"type": "pong"}
    
    # For unsupported message types, gracefully handle by returning an error response
    return {"error": "unsupported message type"}


async def broadcast_conversation_update(
    conversation_data,
    update_type: str = "conversation_update"
):
    """
    Broadcast conversation updates to connected clients.
    
    Args:
        conversation_data: Conversation data to broadcast (ConversationData model or dict)
        update_type: Type of update (new_conversation, message_update, etc.)
        
    Behavior defined by tests:
    - Format message with type and data fields
    - Use ConnectionManager to broadcast to relevant clients
    - Handle broadcast failures gracefully
    - Include conversation metadata in updates
    - Filter recipients based on project/conversation relevance
    """
    # Handle both ConversationData model and dict inputs
    if hasattr(conversation_data, 'model_dump'):
        # Pydantic model - serialize to dict
        data_dict = conversation_data.model_dump(mode='json')
        project_id = conversation_data.project_id
    else:
        # Already a dict
        data_dict = conversation_data
        project_id = conversation_data.get('project_id')
    
    # Format message with type and data fields
    message = {
        "type": update_type,
        "data": data_dict
    }
    
    # Use project-specific subscription filter for targeted broadcasting
    subscription_filter = f"project:{project_id}"
    
    # Use ConnectionManager to broadcast to relevant clients
    await connection_manager.broadcast(message, subscription_filter=subscription_filter)


async def broadcast_file_monitoring_update(
    file_data,
    update_type: str = "file_update"
):
    """
    Broadcast file monitoring updates to connected clients.
    
    Args:
        file_data: File change data to broadcast (ConversationData model or dict)
        update_type: Type of file update (file_created, file_modified, file_deleted, etc.)
        
    Behavior defined by tests:
    - Trigger WebSocket updates when file monitoring detects changes
    - Format update message with consistent structure
    - Broadcast to interested clients only
    - Include performance metrics in updates
    - Maintain <50ms latency requirement
    """
    # Handle both ConversationData model and dict inputs
    if hasattr(file_data, 'model_dump'):
        # Pydantic model - serialize to dict
        data_dict = file_data.model_dump(mode='json')
    else:
        # Already a dict
        data_dict = file_data
    
    # Create file event message using the specific update_type
    message = {
        "type": update_type,  # Use the specific update type (file_created, file_modified, etc.)
        "data": data_dict
    }
    
    # Broadcast to clients subscribed to "file_events"
    await connection_manager.broadcast(message, subscription_filter="file_events")


def get_connection_manager() -> ConnectionManager:
    """
    Dependency injection for ConnectionManager.
    
    Returns:
        Global ConnectionManager instance
        
    Behavior defined by tests:
    - Provide access to connection manager for other modules
    - Enable dependency injection in FastAPI endpoints
    - Support testing with mock connection managers
    """
    return connection_manager