"""
Test suite for Connection Management error handling and resilience.

Following Canon TDD methodology - implementing Tests 4.1-4.4 one at a time:
- Test 4.1: Broadcast handles client disconnection gracefully
- Test 4.2: Broadcast skips disconnected clients  
- Test 4.3: Broadcast tracks failed message deliveries
- Test 4.4: Concurrent broadcasts don't interfere

Current test: Test 4.1 - Broadcast handles client disconnection gracefully
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock
from fastapi import WebSocketDisconnect
from app.websocket.connection_manager import ConnectionManager


class TestConnectionManagement:
    """Test connection management error handling and resilience."""
    
    @pytest.mark.asyncio
    async def test_broadcast_handles_client_disconnection_gracefully(self):
        """Test 4.1: Broadcast handles client disconnection gracefully."""
        # Given a ConnectionManager with multiple clients, one of which will disconnect
        manager = ConnectionManager()
        
        # Mock WebSocket connections
        mock_websocket1 = AsyncMock()
        mock_websocket2 = AsyncMock()
        mock_websocket3 = AsyncMock()
        
        # Set up clients
        client_id1 = "client-1"
        client_id2 = "client-2"
        client_id3 = "client-3"
        
        manager.active_connections[client_id1] = mock_websocket1
        manager.active_connections[client_id2] = mock_websocket2
        manager.active_connections[client_id3] = mock_websocket3
        
        # Configure client 2 to raise WebSocketDisconnect exception
        mock_websocket2.send_text.side_effect = WebSocketDisconnect()
        
        # Create test message
        test_message = {
            "type": "conversation_update",
            "data": {"project_id": "test-project", "conversation_id": "conv-123"}
        }
        
        # When broadcast is called with a disconnected client
        await manager.broadcast(test_message)
        
        # Then broadcast should complete successfully despite client 2 disconnect
        # Client 1 should receive the message
        mock_websocket1.send_text.assert_called_once()
        sent_message_json = mock_websocket1.send_text.call_args[0][0]
        sent_message = json.loads(sent_message_json)
        assert sent_message["type"] == test_message["type"]
        assert sent_message["data"] == test_message["data"]
        
        # Client 2 should attempt to send but fail (exception raised)
        mock_websocket2.send_text.assert_called_once()
        
        # Client 3 should still receive the message
        mock_websocket3.send_text.assert_called_once()
        sent_message_json = mock_websocket3.send_text.call_args[0][0]
        sent_message = json.loads(sent_message_json)
        assert sent_message["type"] == test_message["type"]
        assert sent_message["data"] == test_message["data"]

    @pytest.mark.asyncio
    async def test_broadcast_skips_disconnected_clients(self):
        """Test 4.2: Broadcast skips disconnected clients."""
        # Given a ConnectionManager with clients where some have runtime errors
        manager = ConnectionManager()
        
        # Mock WebSocket connections
        mock_websocket1 = AsyncMock()
        mock_websocket2 = AsyncMock()
        mock_websocket3 = AsyncMock()
        
        # Set up clients
        client_id1 = "client-1"
        client_id2 = "client-2"
        client_id3 = "client-3"
        
        manager.active_connections[client_id1] = mock_websocket1
        manager.active_connections[client_id2] = mock_websocket2
        manager.active_connections[client_id3] = mock_websocket3
        
        # Configure client 2 to raise RuntimeError (general connection issue)
        mock_websocket2.send_text.side_effect = RuntimeError("Connection lost")
        
        # Create test message
        test_message = {
            "type": "system_update",
            "data": {"status": "operational"}
        }
        
        # When broadcast is called
        await manager.broadcast(test_message)
        
        # Then broadcast should skip failed clients and continue
        # Client 1 should receive the message
        mock_websocket1.send_text.assert_called_once()
        sent_message_json = mock_websocket1.send_text.call_args[0][0]
        sent_message = json.loads(sent_message_json)
        assert sent_message["type"] == test_message["type"]
        assert sent_message["data"] == test_message["data"]
        
        # Client 2 should attempt to send but fail
        mock_websocket2.send_text.assert_called_once()
        
        # Client 3 should still receive the message
        mock_websocket3.send_text.assert_called_once()
        sent_message_json = mock_websocket3.send_text.call_args[0][0]
        sent_message = json.loads(sent_message_json)
        assert sent_message["type"] == test_message["type"]
        assert sent_message["data"] == test_message["data"]

    @pytest.mark.asyncio
    async def test_broadcast_tracks_failed_message_deliveries(self):
        """Test 4.3: Broadcast tracks failed message deliveries."""
        # Given a ConnectionManager with clients where some will fail
        manager = ConnectionManager()
        
        # Mock WebSocket connections
        mock_websocket1 = AsyncMock()
        mock_websocket2 = AsyncMock()
        mock_websocket3 = AsyncMock()
        
        # Set up clients
        client_id1 = "client-1"
        client_id2 = "client-2"
        client_id3 = "client-3"
        
        manager.active_connections[client_id1] = mock_websocket1
        manager.active_connections[client_id2] = mock_websocket2
        manager.active_connections[client_id3] = mock_websocket3
        
        # Configure client 2 to fail with WebSocketDisconnect
        mock_websocket2.send_text.side_effect = WebSocketDisconnect()
        
        # Create test message
        test_message = {
            "type": "broadcast_tracking_test",
            "data": {"test_id": "track-123"}
        }
        
        # When broadcast is called
        failed_clients = await manager.broadcast(test_message)
        
        # Then broadcast should return list of failed client IDs
        assert failed_clients is not None
        assert isinstance(failed_clients, list)
        assert client_id2 in failed_clients
        assert client_id1 not in failed_clients
        assert client_id3 not in failed_clients
        
        # Verify successful clients received the message
        mock_websocket1.send_text.assert_called_once()
        mock_websocket3.send_text.assert_called_once()
        
        # Verify failed client was attempted
        mock_websocket2.send_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_concurrent_broadcasts_dont_interfere(self):
        """Test 4.4: Concurrent broadcasts don't interfere."""
        # Given a ConnectionManager with multiple clients
        manager = ConnectionManager()
        
        # Mock WebSocket connections
        mock_websocket1 = AsyncMock()
        mock_websocket2 = AsyncMock()
        mock_websocket3 = AsyncMock()
        
        # Set up clients
        client_id1 = "client-1"
        client_id2 = "client-2"
        client_id3 = "client-3"
        
        manager.active_connections[client_id1] = mock_websocket1
        manager.active_connections[client_id2] = mock_websocket2
        manager.active_connections[client_id3] = mock_websocket3
        
        # Create test messages
        message1 = {
            "type": "concurrent_test_1",
            "data": {"test_id": "concurrent-1"}
        }
        
        message2 = {
            "type": "concurrent_test_2",
            "data": {"test_id": "concurrent-2"}
        }
        
        message3 = {
            "type": "concurrent_test_3",
            "data": {"test_id": "concurrent-3"}
        }
        
        # When multiple broadcasts are run concurrently
        results = await asyncio.gather(
            manager.broadcast(message1),
            manager.broadcast(message2),
            manager.broadcast(message3),
            return_exceptions=True
        )
        
        # Then all broadcasts should complete successfully
        assert len(results) == 3
        for result in results:
            assert not isinstance(result, Exception)
            assert isinstance(result, list)  # Each should return a list of failed clients
            assert len(result) == 0  # No failures expected
        
        # Verify all clients received all messages (3 messages each)
        assert mock_websocket1.send_text.call_count == 3
        assert mock_websocket2.send_text.call_count == 3
        assert mock_websocket3.send_text.call_count == 3
        
        # Verify message content by checking the calls
        sent_messages = []
        for call in mock_websocket1.send_text.call_args_list:
            sent_messages.append(json.loads(call[0][0]))
        
        # Check that all three message types were sent
        message_types = {msg["type"] for msg in sent_messages}
        assert "concurrent_test_1" in message_types
        assert "concurrent_test_2" in message_types
        assert "concurrent_test_3" in message_types