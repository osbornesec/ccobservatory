"""
Test scenarios for shared data contracts and models.

These tests validate the Pydantic models that serve as contracts between
components, ensuring type safety and validation rules work correctly.
"""

import pytest
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from pydantic import ValidationError

from app.models.contracts import (
    FileSystemEventType,
    FileEvent,
    ToolUsage,
    ParsedMessage,
    ConversationData,
    ProjectCreate,
    Project,
    PerformanceMetrics,
    ProcessingError,
    ComponentStatus,
    ComponentHealth,
    SystemHealth,
    APIResponse,
)


class TestFileEvent:
    """Test scenarios for FileEvent model."""

    def test_valid_created_event(self):
        """Should create valid file creation event."""
        event = FileEvent(
            event_type=FileSystemEventType.CREATED,
            src_path=Path("/home/user/.claude/projects/test/conversation.jsonl"),
            is_directory=False,
        )

        assert event.event_type == FileSystemEventType.CREATED
        assert event.src_path.name == "conversation.jsonl"
        assert not event.is_directory
        assert event.dest_path is None
        assert isinstance(event.event_id, type(uuid4()))
        assert isinstance(event.detected_at, datetime)

    def test_valid_moved_event_with_dest_path(self):
        """Should create valid file move event with destination path."""
        event = FileEvent(
            event_type=FileSystemEventType.MOVED,
            src_path=Path("/old/path/file.jsonl"),
            dest_path=Path("/new/path/file.jsonl"),
        )

        assert event.event_type == FileSystemEventType.MOVED
        assert event.dest_path is not None
        assert event.dest_path.name == "file.jsonl"

    def test_moved_event_without_dest_path_fails(self):
        """Should fail validation for moved event without dest_path."""
        with pytest.raises(ValidationError) as exc_info:
            FileEvent(
                event_type=FileSystemEventType.MOVED,
                src_path=Path("/old/path/file.jsonl"),
                # Missing dest_path
            )

        assert "dest_path is required for moved events" in str(exc_info.value)

    def test_non_moved_event_with_dest_path_fails(self):
        """Should fail validation for non-moved event with dest_path."""
        with pytest.raises(ValidationError) as exc_info:
            FileEvent(
                event_type=FileSystemEventType.CREATED,
                src_path=Path("/path/file.jsonl"),
                dest_path=Path("/other/path/file.jsonl"),  # Invalid for created event
            )

        assert "dest_path is only allowed for moved events" in str(exc_info.value)


class TestToolUsage:
    """Test scenarios for ToolUsage model."""

    def test_valid_tool_usage(self):
        """Should create valid tool usage with all fields."""
        tool = ToolUsage(
            tool_name="file_reader",
            tool_input={"file_path": "/test/file.txt", "encoding": "utf-8"},
            tool_output={"content": "file contents", "lines": 10},
            status="success",
        )

        assert tool.tool_name == "file_reader"
        assert "file_path" in tool.tool_input
        assert tool.status == "success"

    def test_minimal_tool_usage(self):
        """Should create valid tool usage with only required fields."""
        tool = ToolUsage(
            tool_name="grep", tool_input={"pattern": "error", "file": "log.txt"}
        )

        assert tool.tool_name == "grep"
        assert tool.tool_output is None
        assert tool.status is None


class TestParsedMessage:
    """Test scenarios for ParsedMessage model."""

    def test_valid_user_message(self):
        """Should create valid user message."""
        conversation_id = uuid4()
        message = ParsedMessage(
            conversation_id=conversation_id,
            message_id="msg_123",
            timestamp=datetime.now(timezone.utc),
            role="user",
            content="Hello, can you help me with this code?",
        )

        assert message.conversation_id == conversation_id
        assert message.role == "user"
        assert message.parent_id is None
        assert message.tool_usage is None

    def test_valid_assistant_message_with_tools(self):
        """Should create valid assistant message with tool usage."""
        tools = [
            ToolUsage(
                tool_name="code_analyzer",
                tool_input={"language": "python", "code": "print('hello')"},
            )
        ]

        message = ParsedMessage(
            conversation_id=uuid4(),
            message_id="msg_456",
            timestamp=datetime.now(timezone.utc),
            role="assistant",
            content="I'll analyze your code.",
            tool_usage=tools,
        )

        assert message.role == "assistant"
        assert len(message.tool_usage) == 1
        assert message.tool_usage[0].tool_name == "code_analyzer"

    def test_invalid_role_fails(self):
        """Should fail validation for invalid role."""
        with pytest.raises(ValidationError):
            ParsedMessage(
                conversation_id=uuid4(),
                message_id="msg_789",
                timestamp=datetime.now(timezone.utc),
                role="system",  # Invalid role
                content="System message",
            )


class TestConversationData:
    """Test scenarios for ConversationData model."""

    def test_valid_conversation_with_messages(self):
        """Should create valid conversation with multiple messages."""
        project_id = uuid4()

        messages = [
            ParsedMessage(
                conversation_id=uuid4(),
                message_id="msg_1",
                timestamp=datetime.now(timezone.utc),
                role="user",
                content="Hello",
            ),
            ParsedMessage(
                conversation_id=uuid4(),
                message_id="msg_2",
                timestamp=datetime.now(timezone.utc),
                role="assistant",
                content="Hi there!",
            ),
        ]

        conversation = ConversationData(
            project_id=project_id,
            file_path="/test/path/conversation.jsonl",
            session_id="session_abc123",
            title="Test Conversation",
            message_count=2,
            messages=messages,
        )

        assert conversation.project_id == project_id
        assert conversation.message_count == 2
        assert len(conversation.messages) == 2
        assert conversation.messages[0].role == "user"

    def test_negative_message_count_fails(self):
        """Should fail validation for negative message count."""
        with pytest.raises(ValidationError):
            ConversationData(
                project_id=uuid4(),
                file_path="/test/invalid/conversation.jsonl",
                session_id="session_123",
                message_count=-1,  # Invalid negative count
            )


class TestProjectModels:
    """Test scenarios for Project models."""

    def test_valid_project_create(self):
        """Should create valid ProjectCreate model."""
        project = ProjectCreate(
            name="My Project", path=Path.cwd()  # Use current directory as valid path
        )

        assert project.name == "My Project"
        assert project.path.exists()

    def test_invalid_empty_name_fails(self):
        """Should fail validation for empty project name."""
        with pytest.raises(ValidationError):
            ProjectCreate(name="", path=Path.cwd())  # Invalid empty name

    def test_invalid_path_fails(self):
        """Should fail validation for non-existent directory path."""
        with pytest.raises(ValidationError):
            ProjectCreate(
                name="Test Project",
                path=Path("/non/existent/directory"),  # Invalid path
            )


class TestPerformanceMetrics:
    """Test scenarios for PerformanceMetrics model."""

    def test_valid_performance_metrics(self):
        """Should create valid performance metrics."""
        metrics = PerformanceMetrics(
            detection_latency_ms=50.5,
            processing_latency_ms=25.0,
            throughput_msgs_per_sec=100.0,
        )

        assert metrics.detection_latency_ms == 50.5
        assert metrics.processing_latency_ms == 25.0
        assert metrics.throughput_msgs_per_sec == 100.0
        assert isinstance(metrics.timestamp, datetime)

    def test_negative_latency_fails(self):
        """Should fail validation for negative latency values."""
        with pytest.raises(ValidationError):
            PerformanceMetrics(
                detection_latency_ms=-10.0,  # Invalid negative value
                processing_latency_ms=25.0,
                throughput_msgs_per_sec=100.0,
            )

    def test_high_latency_allowed(self):
        """Should allow high latency values for monitoring degradation."""
        # This test confirms we can record performance degradation events
        metrics = PerformanceMetrics(
            detection_latency_ms=500.0,  # Above 100ms threshold
            processing_latency_ms=200.0,
            throughput_msgs_per_sec=10.0,
        )

        assert metrics.detection_latency_ms == 500.0  # Should not fail validation


class TestHealthModels:
    """Test scenarios for health check models."""

    def test_valid_component_health(self):
        """Should create valid component health status."""
        health = ComponentHealth(
            component_name="database",
            status=ComponentStatus.OK,
            details="Connection successful",
        )

        assert health.component_name == "database"
        assert health.status == ComponentStatus.OK
        assert health.details == "Connection successful"
        assert isinstance(health.last_checked, datetime)

    def test_valid_system_health(self):
        """Should create valid system health with multiple components."""
        components = [
            ComponentHealth(component_name="database", status=ComponentStatus.OK),
            ComponentHealth(
                component_name="filesystem",
                status=ComponentStatus.DEGRADED,
                details="High disk usage",
            ),
        ]

        system_health = SystemHealth(
            service_status=ComponentStatus.DEGRADED, components=components
        )

        assert system_health.service_status == ComponentStatus.DEGRADED
        assert len(system_health.components) == 2
        assert system_health.components[1].status == ComponentStatus.DEGRADED


class TestAPIResponse:
    """Test scenarios for API response wrapper."""

    def test_successful_response(self):
        """Should create successful API response."""
        project = ProjectCreate(name="Test", path=Path.cwd())
        response = APIResponse[ProjectCreate](success=True, data=project)

        assert response.success is True
        assert response.data.name == "Test"
        assert response.error is None
        assert isinstance(response.timestamp, datetime)

    def test_error_response(self):
        """Should create error API response."""
        error = ProcessingError(
            error_type="ValidationError", error_message="Invalid input data"
        )

        response = APIResponse[None](success=False, error=error)

        assert response.success is False
        assert response.data is None
        assert response.error.error_type == "ValidationError"
