"""
Test suite for ConnectionManager.broadcast() method following Canon TDD approach.
Tests are written one at a time, with minimal implementation to pass each test.
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from app.websocket.connection_manager import ConnectionManager


class TestConnectionManagerBroadcast:
    """Test ConnectionManager broadcast functionality following Canon TDD approach."""
    
    def test_connection_manager_has_broadcast_method(self):
        """Test 1.1: ConnectionManager has broadcast method."""
        # Given a ConnectionManager instance
        manager = ConnectionManager()
        
        # Then it should have a broadcast method
        assert hasattr(manager, 'broadcast')
        assert callable(getattr(manager, 'broadcast'))

    @pytest.mark.asyncio
    async def test_broadcast_sends_message_to_all_connected_clients(self):
        """Test 1.2: Broadcast sends message to all connected clients."""
        # Given a ConnectionManager with multiple connected clients
        manager = ConnectionManager()
        
        # Mock WebSocket connections
        mock_websocket1 = AsyncMock()
        mock_websocket2 = AsyncMock()
        mock_websocket3 = AsyncMock()
        
        # Add connections to the manager
        client_id1 = "client-1"
        client_id2 = "client-2"
        client_id3 = "client-3"
        
        manager.active_connections[client_id1] = mock_websocket1
        manager.active_connections[client_id2] = mock_websocket2
        manager.active_connections[client_id3] = mock_websocket3
        
        # Create test message
        test_message = {
            "type": "conversation_update",
            "data": {"project_id": "test-project", "conversation_id": "conv-123"}
        }
        
        # When broadcast is called
        await manager.broadcast(test_message)
        
        # Then all connected clients should receive the message
        mock_websocket1.send_text.assert_called_once()
        mock_websocket2.send_text.assert_called_once()
        mock_websocket3.send_text.assert_called_once()
        
        # Verify message structure (all clients should receive the same message)
        sent_message_json = mock_websocket1.send_text.call_args[0][0]
        sent_message = json.loads(sent_message_json)
        
        # Verify the message contains original data plus timestamp
        assert sent_message["type"] == test_message["type"]
        assert sent_message["data"] == test_message["data"]
        assert "timestamp" in sent_message

    @pytest.mark.asyncio
    async def test_broadcast_handles_empty_connection_list(self):
        """Test 1.3: Broadcast handles empty connection list."""
        # Given a ConnectionManager with no connected clients
        manager = ConnectionManager()
        
        # Ensure no connections are present
        assert len(manager.active_connections) == 0
        
        # Create test message
        test_message = {
            "type": "conversation_update",
            "data": {"project_id": "test-project", "conversation_id": "conv-123"}
        }
        
        # When broadcast is called with no connections
        # Then it should complete without raising exceptions
        await manager.broadcast(test_message)

    @pytest.mark.asyncio
    async def test_broadcast_message_format_is_consistent(self):
        """Test 1.4: Broadcast message format is consistent."""
        # Given a ConnectionManager with a connected client
        manager = ConnectionManager()
        
        # Mock WebSocket connection
        mock_websocket = AsyncMock()
        client_id = "client-1"
        manager.active_connections[client_id] = mock_websocket
        
        # Create test message
        test_message = {
            "type": "conversation_update",
            "data": {"project_id": "test-project", "conversation_id": "conv-123"}
        }
        
        # When broadcast is called
        await manager.broadcast(test_message)
        
        # Then the message should be sent with consistent JSON structure
        mock_websocket.send_text.assert_called_once()
        sent_message_json = mock_websocket.send_text.call_args[0][0]
        sent_message = json.loads(sent_message_json)
        
        # Verify required fields are present
        assert "type" in sent_message
        assert "data" in sent_message
        assert "timestamp" in sent_message
        
        # Verify field types
        assert isinstance(sent_message["type"], str)
        assert isinstance(sent_message["data"], dict)
        assert isinstance(sent_message["timestamp"], (int, float, str))
        
        # Verify original message content is preserved
        assert sent_message["type"] == test_message["type"]
        assert sent_message["data"] == test_message["data"]

    @pytest.mark.asyncio
    async def test_broadcast_to_specific_subscription_group(self):
        """Test 2.1: Broadcast to specific subscription group."""
        # Given a ConnectionManager with multiple clients with different subscriptions
        manager = ConnectionManager()
        
        # Mock WebSocket connections
        mock_websocket1 = AsyncMock()
        mock_websocket2 = AsyncMock()
        mock_websocket3 = AsyncMock()
        
        # Set up clients with different subscriptions
        client_id1 = "client-1"
        client_id2 = "client-2"
        client_id3 = "client-3"
        
        manager.active_connections[client_id1] = mock_websocket1
        manager.active_connections[client_id2] = mock_websocket2
        manager.active_connections[client_id3] = mock_websocket3
        
        # Client 1: subscribed to "conversation:123"
        manager.subscriptions["conversation:123"] = {client_id1}
        
        # Client 2: subscribed to "project:456"
        manager.subscriptions["project:456"] = {client_id2}
        
        # Client 3: subscribed to both
        manager.subscriptions["conversation:123"].add(client_id3)
        manager.subscriptions["project:456"] = manager.subscriptions.get("project:456", set())
        manager.subscriptions["project:456"].add(client_id3)
        
        # Create test message
        test_message = {
            "type": "conversation_update",
            "data": {"conversation_id": "conv-123"}
        }
        
        # When broadcast is called with subscription filter
        await manager.broadcast(test_message, subscription_filter="conversation:123")
        
        # Then only clients subscribed to "conversation:123" should receive the message
        mock_websocket1.send_text.assert_called_once()  # Client 1 should receive
        mock_websocket2.send_text.assert_not_called()   # Client 2 should NOT receive
        mock_websocket3.send_text.assert_called_once()  # Client 3 should receive
        
        # Verify message content for receiving clients
        sent_message_json = mock_websocket1.send_text.call_args[0][0]
        sent_message = json.loads(sent_message_json)
        
        assert sent_message["type"] == test_message["type"]
        assert sent_message["data"] == test_message["data"]
        assert "timestamp" in sent_message

    @pytest.mark.asyncio
    async def test_client_receives_only_subscribed_messages(self):
        """Test 2.2: Client receives only subscribed messages."""
        # Given a ConnectionManager with a client subscribed to "conversation:123"
        manager = ConnectionManager()
        
        # Mock WebSocket connection for our test client
        mock_websocket = AsyncMock()
        client_id = "client-1"
        
        manager.active_connections[client_id] = mock_websocket
        
        # Subscribe client to "conversation:123"
        manager.subscriptions["conversation:123"] = {client_id}
        
        # Create test messages for different subscription targets
        message_for_123 = {
            "type": "conversation_update",
            "data": {"conversation_id": "conv-123"}
        }
        
        message_for_456 = {
            "type": "conversation_update", 
            "data": {"conversation_id": "conv-456"}
        }
        
        message_for_all = {
            "type": "system_update",
            "data": {"status": "maintenance"}
        }
        
        # When multiple broadcasts are sent
        await manager.broadcast(message_for_123, subscription_filter="conversation:123")
        await manager.broadcast(message_for_456, subscription_filter="conversation:456")
        await manager.broadcast(message_for_all, subscription_filter="all_conversations")
        
        # Then the client should receive only messages for its subscription and "all_conversations"
        # Should receive: conversation:123 + all_conversations = 2 messages total
        assert mock_websocket.send_text.call_count == 2
        
        # Verify the first message (conversation:123)
        first_call = mock_websocket.send_text.call_args_list[0][0][0]
        first_message = json.loads(first_call)
        assert first_message["type"] == message_for_123["type"]
        assert first_message["data"] == message_for_123["data"]
        
        # Verify the second message (all_conversations)
        second_call = mock_websocket.send_text.call_args_list[1][0][0]
        second_message = json.loads(second_call)
        assert second_message["type"] == message_for_all["type"]
        assert second_message["data"] == message_for_all["data"]

    @pytest.mark.asyncio
    async def test_client_can_subscribe_to_multiple_channels(self):
        """Test 2.3: Multiple subscription support - A client can subscribe to multiple channels and receive messages from all subscribed channels."""
        # Given a ConnectionManager with a client subscribed to multiple channels
        manager = ConnectionManager()
        
        # Mock WebSocket connection for our test client
        mock_websocket = AsyncMock()
        client_id = "client-1"
        
        manager.active_connections[client_id] = mock_websocket
        
        # Subscribe client to multiple channels
        manager.subscriptions["conversation:123"] = {client_id}
        manager.subscriptions["project:456"] = {client_id}
        manager.subscriptions["file_events"] = {client_id}
        
        # Create test messages for different subscription targets
        message_for_conv = {
            "type": "conversation_update",
            "data": {"conversation_id": "conv-123"}
        }
        
        message_for_project = {
            "type": "project_update",
            "data": {"project_id": "proj-456"}
        }
        
        message_for_files = {
            "type": "file_event",
            "data": {"file_path": "/path/to/file.jsonl"}
        }
        
        # When broadcasts are sent to all subscribed channels
        await manager.broadcast(message_for_conv, subscription_filter="conversation:123")
        await manager.broadcast(message_for_project, subscription_filter="project:456")
        await manager.broadcast(message_for_files, subscription_filter="file_events")
        
        # Then the client should receive messages from all subscribed channels
        assert mock_websocket.send_text.call_count == 3
        
        # Verify each message was received correctly
        call_args = mock_websocket.send_text.call_args_list
        
        # First message (conversation)
        first_message = json.loads(call_args[0][0][0])
        assert first_message["type"] == message_for_conv["type"]
        assert first_message["data"] == message_for_conv["data"]
        
        # Second message (project)
        second_message = json.loads(call_args[1][0][0])
        assert second_message["type"] == message_for_project["type"]
        assert second_message["data"] == message_for_project["data"]
        
        # Third message (file events)
        third_message = json.loads(call_args[2][0][0])
        assert third_message["type"] == message_for_files["type"]
        assert third_message["data"] == message_for_files["data"]

    @pytest.mark.asyncio
    async def test_subscription_filtering_for_conversation_updates(self):
        """Test 2.4: Subscription filtering for conversation updates."""
        # Given a ConnectionManager with clients subscribed to different conversations
        manager = ConnectionManager()
        
        # Mock WebSocket connections
        mock_websocket1 = AsyncMock()
        mock_websocket2 = AsyncMock()
        mock_websocket3 = AsyncMock()
        
        client_id1 = "client-1"
        client_id2 = "client-2"  
        client_id3 = "client-3"
        
        manager.active_connections[client_id1] = mock_websocket1
        manager.active_connections[client_id2] = mock_websocket2
        manager.active_connections[client_id3] = mock_websocket3
        
        # Subscribe clients to different conversations
        manager.subscriptions["conversation:abc"] = {client_id1, client_id3}
        manager.subscriptions["conversation:def"] = {client_id2}
        
        # Create conversation update messages
        conv_abc_message = {
            "type": "conversation_update",
            "data": {
                "conversation_id": "abc",
                "message_count": 5,
                "last_updated": "2024-01-01T12:00:00Z"
            }
        }
        
        conv_def_message = {
            "type": "conversation_update",
            "data": {
                "conversation_id": "def",
                "message_count": 3,
                "last_updated": "2024-01-01T12:15:00Z"
            }
        }
        
        # When conversation updates are broadcast with filtering
        await manager.broadcast(conv_abc_message, subscription_filter="conversation:abc")
        await manager.broadcast(conv_def_message, subscription_filter="conversation:def")
        
        # Then only subscribed clients should receive their respective updates
        # Client 1: subscribed to conversation:abc
        mock_websocket1.send_text.assert_called_once()
        received_message1 = json.loads(mock_websocket1.send_text.call_args[0][0])
        assert received_message1["type"] == conv_abc_message["type"]
        assert received_message1["data"]["conversation_id"] == "abc"
        
        # Client 2: subscribed to conversation:def
        mock_websocket2.send_text.assert_called_once()
        received_message2 = json.loads(mock_websocket2.send_text.call_args[0][0])
        assert received_message2["type"] == conv_def_message["type"]
        assert received_message2["data"]["conversation_id"] == "def"
        
        # Client 3: subscribed to conversation:abc (should receive abc message)
        mock_websocket3.send_text.assert_called_once()
        received_message3 = json.loads(mock_websocket3.send_text.call_args[0][0])
        assert received_message3["type"] == conv_abc_message["type"]
        assert received_message3["data"]["conversation_id"] == "abc"

    @pytest.mark.asyncio
    async def test_subscription_filtering_for_project_updates(self):
        """Test 2.5: Subscription filtering for project updates."""
        # Given a ConnectionManager with clients subscribed to different projects
        manager = ConnectionManager()
        
        # Mock WebSocket connections
        mock_websocket1 = AsyncMock()
        mock_websocket2 = AsyncMock()
        mock_websocket3 = AsyncMock()
        
        client_id1 = "client-1"
        client_id2 = "client-2"
        client_id3 = "client-3"
        
        manager.active_connections[client_id1] = mock_websocket1
        manager.active_connections[client_id2] = mock_websocket2
        manager.active_connections[client_id3] = mock_websocket3
        
        # Subscribe clients to different projects
        manager.subscriptions["project:webapp"] = {client_id1}
        manager.subscriptions["project:api"] = {client_id2, client_id3}
        
        # Create project update messages
        webapp_project_message = {
            "type": "project_update",
            "data": {
                "project_id": "webapp",
                "status": "active",
                "conversation_count": 15,
                "last_activity": "2024-01-01T14:30:00Z"
            }
        }
        
        api_project_message = {
            "type": "project_update",
            "data": {
                "project_id": "api",
                "status": "archived",
                "conversation_count": 8,
                "last_activity": "2024-01-01T10:00:00Z"
            }
        }
        
        # When project updates are broadcast with filtering
        await manager.broadcast(webapp_project_message, subscription_filter="project:webapp")
        await manager.broadcast(api_project_message, subscription_filter="project:api")
        
        # Then only subscribed clients should receive their respective updates
        # Client 1: subscribed to project:webapp
        mock_websocket1.send_text.assert_called_once()
        received_message1 = json.loads(mock_websocket1.send_text.call_args[0][0])
        assert received_message1["type"] == webapp_project_message["type"]
        assert received_message1["data"]["project_id"] == "webapp"
        assert received_message1["data"]["conversation_count"] == 15
        
        # Client 2: subscribed to project:api
        mock_websocket2.send_text.assert_called_once()
        received_message2 = json.loads(mock_websocket2.send_text.call_args[0][0])
        assert received_message2["type"] == api_project_message["type"]
        assert received_message2["data"]["project_id"] == "api"
        assert received_message2["data"]["status"] == "archived"
        
        # Client 3: also subscribed to project:api
        mock_websocket3.send_text.assert_called_once()
        received_message3 = json.loads(mock_websocket3.send_text.call_args[0][0])
        assert received_message3["type"] == api_project_message["type"]
        assert received_message3["data"]["project_id"] == "api"
        assert received_message3["data"]["status"] == "archived"

    @pytest.mark.asyncio
    async def test_subscription_filtering_for_file_events(self):
        """Test 2.6: Subscription filtering for file events."""
        # Given a ConnectionManager with clients subscribed to different file event types
        manager = ConnectionManager()
        
        # Mock WebSocket connections
        mock_websocket1 = AsyncMock()
        mock_websocket2 = AsyncMock()
        mock_websocket3 = AsyncMock()
        
        client_id1 = "client-1"
        client_id2 = "client-2"
        client_id3 = "client-3"
        
        manager.active_connections[client_id1] = mock_websocket1
        manager.active_connections[client_id2] = mock_websocket2
        manager.active_connections[client_id3] = mock_websocket3
        
        # Subscribe clients to different file event subscriptions
        manager.subscriptions["file_events"] = {client_id1, client_id2}
        manager.subscriptions["file_events:webapp"] = {client_id2}
        manager.subscriptions["file_events:api"] = {client_id3}
        
        # Create file event messages
        general_file_event = {
            "type": "file_event",
            "data": {
                "event_type": "created",
                "file_path": "/general/path/conversation.jsonl",
                "timestamp": "2024-01-01T15:00:00Z"
            }
        }
        
        webapp_file_event = {
            "type": "file_event",
            "data": {
                "event_type": "modified",
                "file_path": "/webapp/project/chat.jsonl",
                "project_id": "webapp",
                "timestamp": "2024-01-01T15:30:00Z"
            }
        }
        
        api_file_event = {
            "type": "file_event",
            "data": {
                "event_type": "deleted",
                "file_path": "/api/project/old_conv.jsonl",
                "project_id": "api",
                "timestamp": "2024-01-01T16:00:00Z"
            }
        }
        
        # When file events are broadcast with filtering
        await manager.broadcast(general_file_event, subscription_filter="file_events")
        await manager.broadcast(webapp_file_event, subscription_filter="file_events:webapp")
        await manager.broadcast(api_file_event, subscription_filter="file_events:api")
        
        # Then only subscribed clients should receive their respective events
        # Client 1: subscribed to general file_events only
        mock_websocket1.send_text.assert_called_once()
        received_message1 = json.loads(mock_websocket1.send_text.call_args[0][0])
        assert received_message1["type"] == general_file_event["type"]
        assert received_message1["data"]["event_type"] == "created"
        assert "/general/path/" in received_message1["data"]["file_path"]
        
        # Client 2: subscribed to both general file_events and webapp-specific
        assert mock_websocket2.send_text.call_count == 2
        call_args = mock_websocket2.send_text.call_args_list
        
        # First call should be general file event
        first_message = json.loads(call_args[0][0][0])
        assert first_message["type"] == general_file_event["type"]
        assert first_message["data"]["event_type"] == "created"
        
        # Second call should be webapp file event
        second_message = json.loads(call_args[1][0][0])
        assert second_message["type"] == webapp_file_event["type"]
        assert second_message["data"]["event_type"] == "modified"
        assert second_message["data"]["project_id"] == "webapp"
        
        # Client 3: subscribed to api file events only
        mock_websocket3.send_text.assert_called_once()
        received_message3 = json.loads(mock_websocket3.send_text.call_args[0][0])
        assert received_message3["type"] == api_file_event["type"]
        assert received_message3["data"]["event_type"] == "deleted"
        assert received_message3["data"]["project_id"] == "api"