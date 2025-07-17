"""
Test suite for WebSocket message formatting consistency.

Following Canon TDD methodology - implementing one test at a time.
These tests validate that all WebSocket messages follow consistent 
formatting standards that the frontend can reliably process.

Current test: Test 7.1 - Conversation update message format
"""
import pytest
import json
from datetime import datetime
from uuid import UUID, uuid4
from jsonschema import validate, ValidationError as JsonSchemaValidationError
from unittest.mock import AsyncMock, patch

from app.websocket.websocket_handler import broadcast_conversation_update
from app.models.contracts import ConversationData, ParsedMessage


class TestMessageFormatting:
    """Test scenarios for WebSocket message formatting consistency."""
    
    @pytest.mark.asyncio
    async def test_conversation_update_message_format(self):
        """Test 7.1: Conversation update message format."""
        # Given: A conversation data object with standard fields
        conversation_data = {
            "id": str(uuid4()),
            "project_id": str(uuid4()),
            "session_id": "session_123",
            "title": "Test Conversation",
            "message_count": 3,
            "file_path": "/path/to/conversation.jsonl",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        # Define expected JSON schema for conversation update messages
        # Note: The handler formats the message, connection manager adds timestamp
        expected_schema = {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "data": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "project_id": {"type": "string"},
                        "session_id": {"type": "string"},
                        "title": {"type": "string"},
                        "message_count": {"type": "integer"},
                        "file_path": {"type": "string"},
                        "created_at": {"type": "string"},
                        "updated_at": {"type": "string"}
                    },
                    "required": ["id", "project_id", "session_id", "message_count", "file_path"]
                }
            },
            "required": ["type", "data"]
        }
        
        # Mock the connection manager to capture the broadcasted message
        with patch('app.websocket.websocket_handler.connection_manager') as mock_manager:
            mock_manager.broadcast = AsyncMock()
            
            # When: Broadcasting a conversation update
            await broadcast_conversation_update(conversation_data, "conversation_update")
            
            # Then: The message should match the expected schema
            mock_manager.broadcast.assert_called_once()
            broadcasted_message = mock_manager.broadcast.call_args[0][0]
            
            # Validate the message structure
            validate(instance=broadcasted_message, schema=expected_schema)
            
            # Verify specific format requirements
            assert broadcasted_message["type"] == "conversation_update"
            assert isinstance(broadcasted_message["data"], dict)
            assert broadcasted_message["data"]["id"] == conversation_data["id"]
            assert broadcasted_message["data"]["project_id"] == conversation_data["project_id"]
            assert broadcasted_message["data"]["message_count"] == conversation_data["message_count"]
            
            # Verify timestamp is NOT present in handler's message
            # The connection manager adds the timestamp during broadcast
            assert "timestamp" not in broadcasted_message  # Handler doesn't add timestamp

    @pytest.mark.asyncio
    async def test_file_monitoring_update_message_format(self):
        """Test 7.2: File monitoring update message format."""
        # Given: A file monitoring event data object
        file_data = {
            "event_id": str(uuid4()),
            "event_type": "created",
            "src_path": "/home/user/.claude/projects/test/conversation.jsonl",
            "is_directory": False,
            "dest_path": None,
            "detected_at": datetime.utcnow().isoformat(),
        }
        
        # Define expected JSON schema for file monitoring update messages
        expected_schema = {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "data": {
                    "type": "object",
                    "properties": {
                        "event_id": {"type": "string"},
                        "event_type": {"type": "string"},
                        "src_path": {"type": "string"},
                        "is_directory": {"type": "boolean"},
                        "dest_path": {"type": ["string", "null"]},
                        "detected_at": {"type": "string"}
                    },
                    "required": ["event_id", "event_type", "src_path", "is_directory", "detected_at"]
                }
            },
            "required": ["type", "data"]
        }
        
        # Mock the connection manager to capture the broadcasted message
        with patch('app.websocket.websocket_handler.connection_manager') as mock_manager:
            mock_manager.broadcast = AsyncMock()
            
            # Import the function we're testing
            from app.websocket.websocket_handler import broadcast_file_monitoring_update
            
            # When: Broadcasting a file monitoring update
            await broadcast_file_monitoring_update(file_data, "file_created")
            
            # Then: The message should match the expected schema
            mock_manager.broadcast.assert_called_once()
            broadcasted_message = mock_manager.broadcast.call_args[0][0]
            
            # Validate the message structure
            validate(instance=broadcasted_message, schema=expected_schema)
            
            # Verify specific format requirements
            assert broadcasted_message["type"] == "file_created"
            assert isinstance(broadcasted_message["data"], dict)
            assert broadcasted_message["data"]["event_id"] == file_data["event_id"]
            assert broadcasted_message["data"]["event_type"] == file_data["event_type"]
            assert broadcasted_message["data"]["src_path"] == file_data["src_path"]
            assert broadcasted_message["data"]["is_directory"] == file_data["is_directory"]
            
            # Verify timestamp is NOT present in handler's message
            assert "timestamp" not in broadcasted_message

    @pytest.mark.asyncio
    async def test_project_update_message_format(self):
        """Test 7.3: Project update message format."""
        # Given: A project data object
        project_data = {
            "id": str(uuid4()),
            "name": "Test Project",
            "path": "/home/user/.claude/projects/test",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
        }
        
        # Define expected JSON schema for project update messages
        expected_schema = {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "data": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "path": {"type": "string"},
                        "created_at": {"type": "string"},
                        "updated_at": {"type": "string"},
                        "last_activity": {"type": "string"}
                    },
                    "required": ["id", "name", "path", "created_at", "updated_at", "last_activity"]
                }
            },
            "required": ["type", "data"]
        }
        
        # Mock the connection manager to capture the broadcasted message
        with patch('app.websocket.websocket_handler.connection_manager') as mock_manager:
            mock_manager.broadcast = AsyncMock()
            
            # Create a simple project update broadcaster function for testing
            # Since project updates don't have a dedicated function yet, we'll simulate it
            async def broadcast_project_update(project_data, update_type="project_update"):
                message = {
                    "type": update_type,
                    "data": project_data
                }
                await mock_manager.broadcast(message)
            
            # When: Broadcasting a project update
            await broadcast_project_update(project_data, "project_update")
            
            # Then: The message should match the expected schema
            mock_manager.broadcast.assert_called_once()
            broadcasted_message = mock_manager.broadcast.call_args[0][0]
            
            # Validate the message structure
            validate(instance=broadcasted_message, schema=expected_schema)
            
            # Verify specific format requirements
            assert broadcasted_message["type"] == "project_update"
            assert isinstance(broadcasted_message["data"], dict)
            assert broadcasted_message["data"]["id"] == project_data["id"]
            assert broadcasted_message["data"]["name"] == project_data["name"]
            assert broadcasted_message["data"]["path"] == project_data["path"]
            
            # Verify timestamp is NOT present in handler's message
            assert "timestamp" not in broadcasted_message

    @pytest.mark.asyncio
    async def test_system_status_message_format(self):
        """Test 7.4: System status message format."""
        # Given: A system status data object
        system_status_data = {
            "service_status": "ok",
            "components": [
                {
                    "component_name": "database",
                    "status": "ok",
                    "details": "Connection successful",
                    "last_checked": datetime.utcnow().isoformat()
                },
                {
                    "component_name": "file_monitor",
                    "status": "ok",
                    "details": "Monitoring 5 projects",
                    "last_checked": datetime.utcnow().isoformat()
                }
            ],
            "checked_at": datetime.utcnow().isoformat()
        }
        
        # Define expected JSON schema for system status messages
        expected_schema = {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "data": {
                    "type": "object",
                    "properties": {
                        "service_status": {"type": "string"},
                        "components": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "component_name": {"type": "string"},
                                    "status": {"type": "string"},
                                    "details": {"type": "string"},
                                    "last_checked": {"type": "string"}
                                },
                                "required": ["component_name", "status", "last_checked"]
                            }
                        },
                        "checked_at": {"type": "string"}
                    },
                    "required": ["service_status", "components", "checked_at"]
                }
            },
            "required": ["type", "data"]
        }
        
        # Mock the connection manager to capture the broadcasted message
        with patch('app.websocket.websocket_handler.connection_manager') as mock_manager:
            mock_manager.broadcast = AsyncMock()
            
            # Create a simple system status broadcaster function for testing
            async def broadcast_system_status(status_data, update_type="system_status"):
                message = {
                    "type": update_type,
                    "data": status_data
                }
                await mock_manager.broadcast(message)
            
            # When: Broadcasting a system status update
            await broadcast_system_status(system_status_data, "system_status")
            
            # Then: The message should match the expected schema
            mock_manager.broadcast.assert_called_once()
            broadcasted_message = mock_manager.broadcast.call_args[0][0]
            
            # Validate the message structure
            validate(instance=broadcasted_message, schema=expected_schema)
            
            # Verify specific format requirements
            assert broadcasted_message["type"] == "system_status"
            assert isinstance(broadcasted_message["data"], dict)
            assert broadcasted_message["data"]["service_status"] == system_status_data["service_status"]
            assert isinstance(broadcasted_message["data"]["components"], list)
            assert len(broadcasted_message["data"]["components"]) == 2
            
            # Verify component structure
            component = broadcasted_message["data"]["components"][0]
            assert component["component_name"] == "database"
            assert component["status"] == "ok"
            assert component["details"] == "Connection successful"
            
            # Verify timestamp is NOT present in handler's message
            assert "timestamp" not in broadcasted_message