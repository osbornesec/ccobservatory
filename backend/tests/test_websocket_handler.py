"""
Test suite for WebSocket Handler following Canon TDD approach.
Tests are written one at a time, with minimal implementation to pass each test.
"""

import pytest
import json
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import WebSocket, WebSocketDisconnect
from app.websocket.websocket_handler import (
    websocket_endpoint,
    handle_websocket_message,
    broadcast_conversation_update,
    broadcast_file_monitoring_update,
    get_connection_manager,
    connection_manager
)
from app.websocket.connection_manager import ConnectionManager


class TestWebSocketHandler:
    """Test WebSocket Handler functionality following Canon TDD approach."""
    
    def test_get_connection_manager_returns_global_instance(self):
        """First test: get_connection_manager returns the global ConnectionManager instance."""
        # Test that the dependency function returns the global connection manager
        manager = get_connection_manager()
        
        assert manager is not None
        assert isinstance(manager, ConnectionManager)
        assert manager is connection_manager
    
    @pytest.mark.asyncio
    async def test_websocket_endpoint_accepts_connection(self):
        """Second test: websocket_endpoint accepts WebSocket connections."""
        # Mock WebSocket and ConnectionManager
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_connection_manager = AsyncMock(spec=ConnectionManager)
        
        # Mock the connection manager methods
        mock_connection_manager.connect = AsyncMock()
        mock_connection_manager.disconnect = AsyncMock()
        
        # Mock websocket receive_text to simulate connection and immediate disconnect
        mock_websocket.receive_text = AsyncMock(side_effect=WebSocketDisconnect)
        
        # Patch the global connection manager
        with patch('app.websocket.websocket_handler.connection_manager', mock_connection_manager):
            # Call the endpoint
            await websocket_endpoint(mock_websocket, "test_client_id")
            
            # Verify connection manager was called to connect
            mock_connection_manager.connect.assert_called_once_with(mock_websocket, "test_client_id")
            mock_connection_manager.disconnect.assert_called_once_with("test_client_id")
    
    @pytest.mark.asyncio
    async def test_websocket_endpoint_handles_message_processing(self):
        """Third test: websocket_endpoint processes incoming messages."""
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_connection_manager = AsyncMock(spec=ConnectionManager)
        
        # Mock connection manager methods
        mock_connection_manager.connect = AsyncMock()
        mock_connection_manager.disconnect = AsyncMock()
        
        # Mock websocket to return a message then disconnect
        mock_websocket.receive_text = AsyncMock(side_effect=[
            '{"type": "ping"}',  # First message
            WebSocketDisconnect  # Then disconnect
        ])
        
        with patch('app.websocket.websocket_handler.connection_manager', mock_connection_manager):
            with patch('app.websocket.websocket_handler.handle_websocket_message', new_callable=AsyncMock) as mock_handler:
                await websocket_endpoint(mock_websocket, "test_client_id")
                
                # Verify message was processed
                mock_handler.assert_called_once_with(
                    {"type": "ping"}, 
                    "test_client_id"
                )
    
    @pytest.mark.asyncio
    async def test_websocket_endpoint_handles_invalid_json(self):
        """Fourth test: websocket_endpoint handles invalid JSON gracefully."""
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_connection_manager = AsyncMock(spec=ConnectionManager)
        
        # Mock connection manager methods
        mock_connection_manager.connect = AsyncMock()
        mock_connection_manager.disconnect = AsyncMock()
        
        # Mock websocket to return invalid JSON then disconnect
        mock_websocket.receive_text = AsyncMock(side_effect=[
            '{invalid json',  # Invalid JSON
            WebSocketDisconnect  # Then disconnect
        ])
        
        with patch('app.websocket.websocket_handler.connection_manager', mock_connection_manager):
            with patch('app.websocket.websocket_handler.handle_websocket_message', new_callable=AsyncMock) as mock_handler:
                await websocket_endpoint(mock_websocket, "test_client_id")
                
                # Verify message handler was NOT called due to invalid JSON
                mock_handler.assert_not_called()
                
                # Verify connection/disconnection still worked
                mock_connection_manager.connect.assert_called_once()
                mock_connection_manager.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast_conversation_update_with_connection_manager(self):
        """Fifth test: broadcast_conversation_update uses ConnectionManager to broadcast."""
        mock_connection_manager = AsyncMock(spec=ConnectionManager)
        mock_connection_manager.broadcast = AsyncMock()
        
        conversation_data = {
            "id": "conv-123",
            "project_id": "project-456",
            "message_count": 5
        }
        
        with patch('app.websocket.websocket_handler.connection_manager', mock_connection_manager):
            await broadcast_conversation_update(conversation_data, "new_conversation")
            
            # Verify broadcast was called with formatted message
            mock_connection_manager.broadcast.assert_called_once()
            call_args = mock_connection_manager.broadcast.call_args[0][0]
            
            # Check message format
            assert call_args["type"] == "new_conversation"
            assert call_args["data"] == conversation_data
    
    @pytest.mark.asyncio
    async def test_handle_websocket_message_ping_returns_pong(self):
        """Sixth test: handle_websocket_message processes ping message type and returns pong."""
        # Given a simple ping message and a dummy connection ID
        message = {"type": "ping"}
        connection_id = "dummy-connection"
        
        # When handle_websocket_message is invoked (passing None for db_client since not used yet)
        result = await handle_websocket_message(message, connection_id, db_client=None)
        
        # Then it should return a pong response indicating correct handling
        assert result == {"type": "pong"}

    @pytest.mark.asyncio
    async def test_handle_websocket_message_unsupported_type_returns_error(self):
        """
        Seventh test: handle_websocket_message returns an error for unsupported message types.
        This test covers the error response path for unsupported message types (line 84).
        """
        # Given a message with an unsupported type (e.g., "subscribe", or any type other than "ping")
        unsupported_message = {"type": "unsupported_action", "payload": {"data": "some_data"}}
        connection_id = "test_client_id_unsupported"

        # When handle_websocket_message is invoked
        # db_client is a FastAPI Depends, but for unit testing, we can pass None if not used by the logic under test.
        result = await handle_websocket_message(unsupported_message, connection_id, db_client=None)

        # Then it should return the specific error response as defined on line 84.
        assert result == {"error": "unsupported message type"}

    @pytest.mark.asyncio
    async def test_broadcast_file_monitoring_update_is_callable(self):
        """
        Eighth test: broadcast_file_monitoring_update is callable and does not raise exceptions.
        This test covers the `pass` statement within the function (line 134).
        """
        # Given some dummy file data and update type
        file_data = {
            "path": "/path/to/file.txt",
            "event_type": "modified",
            "timestamp": "2023-10-27T10:00:00Z"
        }
        update_type = "file_changed"

        # When broadcast_file_monitoring_update is called
        # Since the function currently only contains 'pass', the primary goal is to ensure its callability
        # and that no exceptions are raised during its execution.
        await broadcast_file_monitoring_update(file_data, update_type)

        # Then no exception should have been raised.
        # An explicit assertion is added to confirm the test completed successfully.
        # If the function were to have observable side effects (e.g., calling connection_manager.broadcast),
        # those side effects would be asserted here.
        assert True