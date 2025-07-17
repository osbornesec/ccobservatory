"""
WebSocket Handler Integration Tests

Tests 8.1-8.2: Integration between websocket_handler functions and ConnectionManager.broadcast

Canon TDD Implementation - Test First Development
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.websocket.websocket_handler import broadcast_conversation_update, broadcast_file_monitoring_update


class TestWebSocketHandlerIntegration:
    """Integration tests for websocket_handler functions with ConnectionManager."""
    
    @pytest.mark.asyncio
    async def test_broadcast_conversation_update_uses_connection_manager_broadcast(self):
        """Test 8.1: websocket_handler.broadcast_conversation_update uses ConnectionManager.broadcast"""
        # Arrange
        conversation_data = {
            "id": "conv_123",
            "project_id": "proj_456",
            "title": "Test Conversation",
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]
        }
        
        # Mock ConnectionManager.broadcast
        with patch('app.websocket.websocket_handler.connection_manager') as mock_manager:
            mock_manager.broadcast = AsyncMock()
            
            # Act
            await broadcast_conversation_update(conversation_data, update_type="conversation_update")
            
            # Assert
            mock_manager.broadcast.assert_called_once()
            call_args = mock_manager.broadcast.call_args
            
            # Verify message structure
            message = call_args[0][0]  # First positional argument
            assert message["type"] == "conversation_update"
            assert message["data"] == conversation_data
            
            # Verify subscription filter
            subscription_filter = call_args[1]["subscription_filter"]
            assert subscription_filter == "project:proj_456"

    @pytest.mark.asyncio
    async def test_broadcast_file_monitoring_update_uses_connection_manager_broadcast(self):
        """Test 8.2: websocket_handler.broadcast_file_monitoring_update uses ConnectionManager.broadcast"""
        # Arrange
        file_data = {
            "file_path": "/home/user/.claude/projects/test_project/conversation_001.jsonl",
            "file_size": 1024,
            "modification_time": "2024-01-15T10:30:00Z",
            "event_type": "file_modified",
            "project_id": "test_project"
        }
        
        # Mock ConnectionManager.broadcast
        with patch('app.websocket.websocket_handler.connection_manager') as mock_manager:
            mock_manager.broadcast = AsyncMock()
            
            # Act
            await broadcast_file_monitoring_update(file_data, update_type="file_modified")
            
            # Assert
            mock_manager.broadcast.assert_called_once()
            call_args = mock_manager.broadcast.call_args
            
            # Verify message structure
            message = call_args[0][0]  # First positional argument
            assert message["type"] == "file_modified"
            assert message["data"] == file_data
            
            # Verify subscription filter
            subscription_filter = call_args[1]["subscription_filter"]
            assert subscription_filter == "file_events"

    @pytest.mark.asyncio
    async def test_broadcast_conversation_update_with_pydantic_model_integration(self):
        """Test 8.1 extended: broadcast_conversation_update handles Pydantic models properly"""
        # Arrange
        mock_conversation_model = MagicMock()
        mock_conversation_model.model_dump.return_value = {
            "id": "conv_789",
            "project_id": "proj_123",
            "title": "Model Conversation"
        }
        mock_conversation_model.project_id = "proj_123"
        
        # Mock ConnectionManager.broadcast
        with patch('app.websocket.websocket_handler.connection_manager') as mock_manager:
            mock_manager.broadcast = AsyncMock()
            
            # Act
            await broadcast_conversation_update(mock_conversation_model, update_type="new_conversation")
            
            # Assert
            mock_manager.broadcast.assert_called_once()
            call_args = mock_manager.broadcast.call_args
            
            # Verify Pydantic model was properly serialized
            message = call_args[0][0]
            assert message["type"] == "new_conversation"
            assert message["data"]["id"] == "conv_789"
            assert message["data"]["project_id"] == "proj_123"
            
            # Verify subscription filter uses model's project_id
            subscription_filter = call_args[1]["subscription_filter"]
            assert subscription_filter == "project:proj_123"
            
            # Verify model_dump was called with JSON mode
            mock_conversation_model.model_dump.assert_called_once_with(mode='json')

    @pytest.mark.asyncio
    async def test_broadcast_file_monitoring_update_with_different_event_types(self):
        """Test 8.2 extended: broadcast_file_monitoring_update handles different event types"""
        # Arrange
        file_data = {
            "file_path": "/home/user/.claude/projects/test_project/conversation_002.jsonl",
            "file_size": 2048,
            "modification_time": "2024-01-15T11:00:00Z",
            "event_type": "file_created",
            "project_id": "test_project"
        }
        
        # Mock ConnectionManager.broadcast
        with patch('app.websocket.websocket_handler.connection_manager') as mock_manager:
            mock_manager.broadcast = AsyncMock()
            
            # Act
            await broadcast_file_monitoring_update(file_data, update_type="file_created")
            
            # Assert
            mock_manager.broadcast.assert_called_once()
            call_args = mock_manager.broadcast.call_args
            
            # Verify event type is preserved in message
            message = call_args[0][0]
            assert message["type"] == "file_created"
            assert message["data"]["event_type"] == "file_created"
            
            # Verify subscription filter remains consistent
            subscription_filter = call_args[1]["subscription_filter"]
            assert subscription_filter == "file_events"

    @pytest.mark.asyncio
    async def test_broadcast_conversation_update_parameter_passing_integration(self):
        """Test 8.1 extended: verify correct parameter passing to ConnectionManager.broadcast"""
        # Arrange
        conversation_data = {
            "id": "conv_params",
            "project_id": "proj_params",
            "title": "Parameter Test",
            "status": "active"
        }
        
        # Mock ConnectionManager.broadcast
        with patch('app.websocket.websocket_handler.connection_manager') as mock_manager:
            mock_manager.broadcast = AsyncMock()
            
            # Act
            await broadcast_conversation_update(conversation_data, update_type="message_update")
            
            # Assert
            mock_manager.broadcast.assert_called_once()
            call_args = mock_manager.broadcast.call_args
            
            # Verify message parameter structure
            message = call_args[0][0]
            assert isinstance(message, dict)
            assert "type" in message
            assert "data" in message
            assert message["type"] == "message_update"
            assert message["data"]["id"] == "conv_params"
            assert message["data"]["status"] == "active"
            
            # Verify subscription_filter parameter
            kwargs = call_args[1]
            assert "subscription_filter" in kwargs
            assert kwargs["subscription_filter"] == "project:proj_params"

    @pytest.mark.asyncio
    async def test_broadcast_file_monitoring_update_parameter_passing_integration(self):
        """Test 8.2 extended: verify correct parameter passing to ConnectionManager.broadcast"""
        # Arrange
        file_data = {
            "file_path": "/test/path/file.jsonl",
            "file_size": 4096,
            "modification_time": "2024-01-15T12:00:00Z",
            "event_type": "file_deleted",
            "project_id": "param_test_project"
        }
        
        # Mock ConnectionManager.broadcast
        with patch('app.websocket.websocket_handler.connection_manager') as mock_manager:
            mock_manager.broadcast = AsyncMock()
            
            # Act
            await broadcast_file_monitoring_update(file_data, update_type="file_deleted")
            
            # Assert
            mock_manager.broadcast.assert_called_once()
            call_args = mock_manager.broadcast.call_args
            
            # Verify message parameter structure
            message = call_args[0][0]
            assert isinstance(message, dict)
            assert "type" in message
            assert "data" in message
            assert message["type"] == "file_deleted"
            assert message["data"]["file_path"] == "/test/path/file.jsonl"
            assert message["data"]["file_size"] == 4096
            
            # Verify subscription_filter parameter
            kwargs = call_args[1]
            assert "subscription_filter" in kwargs
            assert kwargs["subscription_filter"] == "file_events"