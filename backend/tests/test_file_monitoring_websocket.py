"""
Test file monitoring WebSocket integration.

This test verifies that file monitoring events trigger WebSocket broadcasts
to subscribed clients.
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.websocket.connection_manager import ConnectionManager
from app.models.contracts import ConversationData
from app.websocket.connection_manager import ConnectionManager
from app.models.contracts import ConversationData


class TestFileMonitoringWebSocket:
    """Test integration between file monitoring and WebSocket broadcasting."""
    
    @pytest.mark.asyncio
    async def test_file_monitoring_triggers_websocket_broadcast(self):
        """
        BEHAVIOR: When file monitoring detects a new JSONL file,
        it should trigger a WebSocket broadcast to notify connected clients.
        """
        # Arrange
        mock_connection_manager = AsyncMock(spec=ConnectionManager)
        mock_connection_manager.broadcast = AsyncMock()
        
        # Patch the connection_manager to use our mock
        from app.websocket import websocket_handler
        with patch.object(websocket_handler, 'connection_manager', mock_connection_manager):
            
            # Act
            # Call the actual broadcast_file_monitoring_update function (currently stub)
            await websocket_handler.broadcast_file_monitoring_update(
                file_data={
                    "file_path": "/tmp/test_claude_projects/test_project/conversation.jsonl",
                    "conversation_id": "test-conv-123",
                    "project_id": "test-project-456"
                },
                update_type="file_created"
            )
            
            # Assert
            # Verify that ConnectionManager.broadcast was called with "file_events" filter
            mock_connection_manager.broadcast.assert_called_once()
            
            # Verify the call was made with the correct subscription filter
            call_args = mock_connection_manager.broadcast.call_args
            assert call_args.kwargs['subscription_filter'] == "file_events"
            
            # Verify the message structure
            message = call_args.args[0]
            assert message["type"] == "file_created"
            assert "file_path" in message["data"]

    @pytest.mark.asyncio
    async def test_conversation_update_broadcasts_to_project_subscribers(self):
        """
        BEHAVIOR: When a conversation is updated, the broadcast should be filtered
        to clients subscribed to that specific project.
        """
        # Arrange
        mock_connection_manager = AsyncMock(spec=ConnectionManager)
        mock_connection_manager.broadcast = AsyncMock()
        
        test_project_id = uuid4()
        
        # Using the ConversationData model directly makes our test data robust
        # and aligned with our system's contracts.
        conversation_payload = ConversationData(
            project_id=test_project_id,
            file_path=f"/fake/projects/{test_project_id}/conversation.jsonl",
            session_id="fake-session-123"
        )

        # Patch the connection_manager to use our mock
        from app.websocket import websocket_handler
        with patch.object(websocket_handler, 'connection_manager', mock_connection_manager):
            
            # Act
            await websocket_handler.broadcast_conversation_update(
                conversation_data=conversation_payload,
                update_type="new_conversation"
            )
            
            # Assert
            mock_connection_manager.broadcast.assert_called_once()
            
            call_args = mock_connection_manager.broadcast.call_args
            
            # 1. Verify the subscription filter is correctly formatted and used
            expected_filter = f"project:{test_project_id}"
            assert 'subscription_filter' in call_args.kwargs, "The 'subscription_filter' keyword argument is missing."
            assert call_args.kwargs['subscription_filter'] == expected_filter
            
            # 2. Verify the message payload is correct
            message = call_args.args[0]
            assert message["type"] == "new_conversation"
            # Pydantic's model_dump(mode='json') will convert UUID to str
            assert message["data"]["project_id"] == str(test_project_id)

    @pytest.mark.asyncio
    async def test_file_monitoring_broadcast_includes_conversation_metadata(self):
        """
        BEHAVIOR: A file monitoring broadcast for a conversation file should
        include the full, serialized conversation metadata.
        """
        # Arrange
        mock_connection_manager = AsyncMock(spec=ConnectionManager)
        mock_connection_manager.broadcast = AsyncMock()

        test_project_id = uuid4()
        test_conversation_id = uuid4()

        # This represents the fully parsed data that should be broadcast.
        conversation_payload = ConversationData(
            id=test_conversation_id,
            project_id=test_project_id,
            file_path=f"/fake/projects/{test_project_id}/conversation.jsonl",
            session_id="fake-session-456",
            message_count=10,
            title="Test Conversation Title"
        )

        # Patch the connection_manager
        from app.websocket import websocket_handler
        with patch.object(websocket_handler, 'connection_manager', mock_connection_manager):

            # Act
            await websocket_handler.broadcast_file_monitoring_update(
                file_data=conversation_payload,  # Pass the Pydantic model instance
                update_type="file_modified"
            )

            # Assert
            mock_connection_manager.broadcast.assert_called_once()

            call_args = mock_connection_manager.broadcast.call_args
            message = call_args.args[0]
            broadcast_data = message["data"]

            # 1. Verify the message type is correctly constructed from the update_type
            assert message["type"] == "file_modified"

            # 2. Verify the subscription filter is for general file events
            assert call_args.kwargs['subscription_filter'] == "file_events"

            # 3. Verify the payload is a serialized dictionary and contains expected metadata
            assert isinstance(broadcast_data, dict)
            assert broadcast_data["id"] == str(test_conversation_id)
            assert broadcast_data["project_id"] == str(test_project_id)
            assert broadcast_data["message_count"] == 10
            assert broadcast_data["title"] == "Test Conversation Title"

    @pytest.mark.asyncio
    async def test_multiple_file_events_broadcast_efficiently(self):
        """
        BEHAVIOR: The system should handle multiple, concurrent file monitoring
        events and broadcast them without blocking or dropping events.
        """
        # Arrange
        mock_connection_manager = AsyncMock(spec=ConnectionManager)
        mock_connection_manager.broadcast = AsyncMock()
        
        event_count = 10
        # Create multiple conversation events for concurrent broadcasting
        conversation_events = []
        for i in range(event_count):
            conversation_data = ConversationData(
                id=uuid4(),
                project_id=uuid4(),
                file_path=f"/path/to/file_{i}.jsonl",
                session_id=f"session_{i}",
                message_count=i + 1,
                title=f"Conversation {i}"
            )
            conversation_events.append(conversation_data)
        
        from app.websocket import websocket_handler
        with patch.object(websocket_handler, 'connection_manager', mock_connection_manager):
            # Act
            # Use asyncio.gather to trigger multiple broadcasts concurrently
            broadcast_tasks = [
                websocket_handler.broadcast_file_monitoring_update(
                    file_data=event,
                    update_type="file_created"
                )
                for event in conversation_events
            ]
            await asyncio.gather(*broadcast_tasks)
            
            # Assert
            # Verify that broadcast was called for each event
            assert mock_connection_manager.broadcast.call_count == event_count
            
            # Verify each call was made with the correct subscription filter
            for call in mock_connection_manager.broadcast.call_args_list:
                assert call.kwargs['subscription_filter'] == "file_events"
                message = call.args[0]
                assert message["type"] == "file_created"
                assert "id" in message["data"]
                assert "project_id" in message["data"]
                assert "file_path" in message["data"]
            
            # Verify that all unique conversations were broadcast
            broadcast_ids = set()
            for call in mock_connection_manager.broadcast.call_args_list:
                message = call.args[0]
                broadcast_ids.add(message["data"]["id"])
            
            expected_ids = {str(event.id) for event in conversation_events}
            assert broadcast_ids == expected_ids

    @pytest.mark.asyncio
    async def test_file_monitoring_broadcast_respects_latency_requirements(self):
        """
        BEHAVIOR: The broadcast function for file monitoring updates should
        execute within the 50ms latency requirement specified in its docstring.
        NOTE: This test can be sensitive to system load and is best for detecting
        major performance regressions.
        """
        # Arrange
        mock_connection_manager = AsyncMock(spec=ConnectionManager)
        
        # Simulate a realistic but fast broadcast operation (e.g., 10ms I/O wait)
        # This makes the test more meaningful than mocking an instantaneous operation.
        async def fake_broadcast(*args, **kwargs):
            await asyncio.sleep(0.01)  # 10ms simulated I/O delay
        
        mock_connection_manager.broadcast = fake_broadcast
        
        # Test data for latency measurement
        conversation_data = ConversationData(
            id=uuid4(),
            project_id=uuid4(),
            file_path="/path/to/latency_test.jsonl",
            session_id="latency-test-session",
            message_count=5,
            title="Latency Test Conversation"
        )
        
        latency_requirement_sec = 0.050  # 50ms
        
        from app.websocket import websocket_handler
        with patch.object(websocket_handler, 'connection_manager', mock_connection_manager):
            # Act
            start_time = time.perf_counter()
            await websocket_handler.broadcast_file_monitoring_update(
                file_data=conversation_data,
                update_type="file_created"
            )
            end_time = time.perf_counter()
            
            duration = end_time - start_time
            
            # Assert
            # The test measures the overhead of the handler function itself,
            # plus the simulated 10ms broadcast time.
            assert duration < latency_requirement_sec
            print(f"\nBroadcast handler latency: {duration*1000:.2f}ms (Requirement: < {latency_requirement_sec*1000}ms)")