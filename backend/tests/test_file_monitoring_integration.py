"""
Integration tests for the complete file monitoring system.

Tests the end-to-end pipeline: file events -> parsing -> database storage
with performance validation and error handling scenarios.
"""

import asyncio
import json
import os
import tempfile
import time
from pathlib import Path
from uuid import uuid4
from typing import List, Dict, Any
import pytest
import asyncpg

from app.monitoring.file_monitor import FileMonitor
from app.monitoring.file_handler import ClaudeFileHandler
from app.monitoring.jsonl_parser import JSONLParser
from app.monitoring.database_writer import DatabaseWriter
from app.monitoring.performance_monitor import PerformanceMonitor
from app.models.contracts import (
    FileEvent,
    ConversationData,
    ParsedMessage,
    PerformanceMetrics,
    ComponentStatus,
)
from app.database.supabase_client import get_supabase_service_client


class TestFileMonitoringIntegration:
    """Integration tests for the complete file monitoring system."""

    @pytest.fixture
    def temp_claude_dir(self):
        """Create a temporary Claude projects directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            claude_dir = Path(temp_dir) / ".claude" / "projects"
            claude_dir.mkdir(parents=True)
            yield claude_dir

    @pytest.fixture
    def sample_jsonl_content(self):
        """Generate sample JSONL content for testing."""
        session_id = str(uuid4())
        messages = [
            {
                "uuid": str(uuid4()),
                "sessionId": session_id,
                "timestamp": "2024-01-15T10:30:00.000Z",
                "type": "message",
                "message": {
                    "role": "user",
                    "content": "Hello, can you help me with Python?",
                },
            },
            {
                "uuid": str(uuid4()),
                "sessionId": session_id,
                "timestamp": "2024-01-15T10:30:05.000Z",
                "type": "message",
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": "I'll help you with Python. Let me check the available tools.",
                        },
                        {
                            "type": "tool_use",
                            "id": "tool_123",
                            "name": "Read",
                            "input": {"file_path": "/path/to/file.py"},
                        },
                    ],
                },
            },
            {
                "uuid": str(uuid4()),
                "sessionId": session_id,
                "timestamp": "2024-01-15T10:30:10.000Z",
                "type": "message",
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "tool_123",
                            "content": "def hello_world():\n    print('Hello, World!')",
                        },
                        {
                            "type": "text",
                            "text": "Here's your Python code. I can help you improve it!",
                        },
                    ],
                },
            },
        ]
        return "\n".join(json.dumps(msg) for msg in messages)

    @pytest.fixture
    async def test_project_setup(self, clean_db):
        """Set up a test project in the database."""
        conn = clean_db

        # Create a test project
        project_data = {
            "id": str(uuid4()),
            "name": "test-project",
            "path": "/tmp/test-project",
            "description": "Test project for integration tests",
        }

        await conn.execute(
            """
            INSERT INTO projects (id, name, path, description)
            VALUES ($1, $2, $3, $4)
        """,
            project_data["id"],
            project_data["name"],
            project_data["path"],
            project_data["description"],
        )

        return project_data

    def test_file_handler_event_creation(self, temp_claude_dir):
        """Test ClaudeFileHandler creates correct FileEvent objects."""
        events_received = []

        def event_callback(file_event: FileEvent):
            events_received.append(file_event)

        handler = ClaudeFileHandler(callback=event_callback)

        # Create a test JSONL file
        test_file = temp_claude_dir / "test-conversation.jsonl"
        test_file.write_text("{'test': 'data'}")

        # Simulate watchdog events manually
        from watchdog.events import FileCreatedEvent, FileModifiedEvent

        # Test file creation
        create_event = FileCreatedEvent(str(test_file))
        handler.on_created(create_event)

        # Test file modification
        modify_event = FileModifiedEvent(str(test_file))
        handler.on_modified(modify_event)

        # Verify events were processed
        assert len(events_received) == 2
        assert events_received[0].event_type.value == "created"
        assert events_received[1].event_type.value == "modified"
        assert all(str(event.src_path).endswith(".jsonl") for event in events_received)

    def test_jsonl_parser_conversation_extraction(self, sample_jsonl_content):
        """Test JSONLParser correctly extracts conversation data."""
        parser = JSONLParser()

        # Create temporary file with sample content
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(sample_jsonl_content)
            temp_file = f.name

        try:
            # Parse the conversation
            result = parser.parse_conversation_file(temp_file)

            # Verify successful parsing
            assert isinstance(result, ConversationData)
            assert len(result.messages) == 3
            assert result.message_count == 3

            # Verify message details
            assert result.messages[0].role == "user"
            assert result.messages[1].role == "assistant"
            assert result.messages[2].role == "assistant"

            # Verify tool usage extraction
            tool_message = result.messages[1]
            assert tool_message.tool_usage is not None
            assert len(tool_message.tool_usage) == 1
            assert tool_message.tool_usage[0].tool_name == "Read"
            assert tool_message.tool_usage[0].status == "pending"

            # Verify tool result mapping
            result_message = result.messages[2]
            assert result_message.tool_usage is not None
            assert len(result_message.tool_usage) == 1
            assert result_message.tool_usage[0].status == "success"

        finally:
            os.unlink(temp_file)

    @pytest.mark.asyncio
    async def test_database_writer_conversation_storage(
        self, clean_db, test_project_setup
    ):
        """Test DatabaseWriter properly stores conversation data."""
        writer = DatabaseWriter()

        # Create test conversation data
        conversation_data = ConversationData(
            project_id=test_project_setup["id"],
            file_path="/test/integration/conversation.jsonl",
            session_id="test-session-123",
            title="Test Conversation",
            message_count=2,
            messages=[
                ParsedMessage(
                    conversation_id=uuid4(),
                    message_id="msg-1",
                    timestamp="2024-01-15T10:30:00+00:00",
                    role="user",
                    content="Hello world",
                ),
                ParsedMessage(
                    conversation_id=uuid4(),
                    message_id="msg-2",
                    timestamp="2024-01-15T10:30:05+00:00",
                    role="assistant",
                    content="Hello! How can I help you?",
                ),
            ],
        )

        # Write conversation to database
        success, conversation_id, metrics = writer.write_conversation(conversation_data)

        # Verify successful write
        assert success is True
        assert conversation_id is not None
        assert "total_write_ms" in metrics
        assert "conversation_write_ms" in metrics
        assert "messages_write_ms" in metrics

        # Verify data in database
        conn = clean_db

        # Check conversation record
        conv_record = await conn.fetchrow(
            """
            SELECT * FROM conversations WHERE id = $1
        """,
            str(conversation_id),
        )

        assert conv_record is not None
        assert conv_record["session_id"] == "test-session-123"
        assert conv_record["title"] == "Test Conversation"
        assert conv_record["message_count"] == 2

        # Check message records
        message_records = await conn.fetch(
            """
            SELECT * FROM messages WHERE conversation_id = $1 ORDER BY timestamp
        """,
            str(conversation_id),
        )

        assert len(message_records) == 2
        assert message_records[0]["role"] == "user"
        assert message_records[0]["content"] == "Hello world"
        assert message_records[1]["role"] == "assistant"
        assert message_records[1]["content"] == "Hello! How can I help you?"

    def test_performance_monitor_metrics_tracking(self):
        """Test PerformanceMonitor correctly tracks and analyzes metrics."""
        monitor = PerformanceMonitor(sla_threshold_ms=100.0)

        # Record sample metrics
        test_metrics = [
            PerformanceMetrics(
                detection_latency_ms=45.0,
                processing_latency_ms=120.0,
                throughput_msgs_per_sec=8.5,
            ),
            PerformanceMetrics(
                detection_latency_ms=67.0,
                processing_latency_ms=95.0,
                throughput_msgs_per_sec=12.3,
            ),
            PerformanceMetrics(
                detection_latency_ms=123.0,
                processing_latency_ms=200.0,
                throughput_msgs_per_sec=5.1,
            ),  # SLA violation
            PerformanceMetrics(
                detection_latency_ms=34.0,
                processing_latency_ms=80.0,
                throughput_msgs_per_sec=15.2,
            ),
            PerformanceMetrics(
                detection_latency_ms=89.0,
                processing_latency_ms=110.0,
                throughput_msgs_per_sec=9.8,
            ),
        ]

        for metrics in test_metrics:
            monitor.record_metrics(metrics)

        # Get performance summary
        summary = monitor.get_summary()

        # Verify statistics calculation
        assert (
            summary["status"] == ComponentStatus.DEGRADED.value
        )  # Due to 1 SLA violation
        assert summary["sla_compliance_rate"] == 0.8  # 4/5 compliant
        assert summary["detection_latency"]["sla_violations"] == 1
        assert summary["detection_latency"]["min"] == 34.0
        assert summary["detection_latency"]["max"] == 123.0
        assert 65.0 <= summary["detection_latency"]["mean"] <= 72.0  # Approximate check

        # Verify alerts generation
        alerts = monitor.get_alerts()
        assert len(alerts) >= 1
        assert any("SLA violation rate" in alert["message"] for alert in alerts)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_end_to_end_file_processing_pipeline(
        self, temp_claude_dir, sample_jsonl_content, clean_db, test_project_setup
    ):
        """Test complete end-to-end file processing pipeline."""
        processed_conversations = []

        def conversation_callback(conversation_data: ConversationData):
            processed_conversations.append(conversation_data)

        # Initialize file monitor with temporary directory
        monitor = FileMonitor(
            watch_path=str(temp_claude_dir), callback=conversation_callback
        )

        try:
            # Start monitoring
            monitor.start()
            assert monitor.is_running

            # Create a test JSONL file
            test_file = temp_claude_dir / "test-conversation.jsonl"
            test_file.write_text(sample_jsonl_content)

            # Give the system time to process the file
            await asyncio.sleep(0.5)

            # Verify file was processed
            assert len(processed_conversations) == 1
            conversation = processed_conversations[0]
            assert len(conversation.messages) == 3
            assert conversation.message_count == 3

            # Verify performance metrics were recorded
            stats = monitor.get_stats()
            assert stats["files_processed"] == 1
            assert stats["conversations_created"] == 1
            assert stats["processing_errors"] == 0

            # Verify performance monitoring
            perf_stats = stats["performance_stats"]
            assert perf_stats["status"] in ["ok", "no_data"]

            # Verify database was updated
            conn = clean_db
            conversations = await conn.fetch("SELECT * FROM conversations")
            messages = await conn.fetch("SELECT * FROM messages")

            assert len(conversations) >= 1
            assert len(messages) >= 3

        finally:
            monitor.stop()
            assert not monitor.is_running

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_performance_requirements_validation(self, temp_claude_dir):
        """Test that the system meets <100ms detection latency requirements."""
        detection_latencies = []

        def timing_callback(conversation_data: ConversationData):
            # This would be called after processing, so we measure differently
            pass

        monitor = FileMonitor(watch_path=str(temp_claude_dir), callback=timing_callback)

        try:
            monitor.start()

            # Create multiple test files to gather performance data
            for i in range(10):
                test_file = temp_claude_dir / f"perf-test-{i}.jsonl"

                # Record time before file creation
                start_time = time.perf_counter()

                # Create file with minimal content
                test_content = json.dumps(
                    {
                        "uuid": str(uuid4()),
                        "sessionId": f"perf-session-{i}",
                        "timestamp": "2024-01-15T10:30:00.000Z",
                        "type": "message",
                        "message": {"role": "user", "content": "Test message"},
                    }
                )
                test_file.write_text(test_content)

                # Wait a bit for processing
                await asyncio.sleep(0.2)

                # Check if performance metrics were recorded
                perf_summary = monitor.performance_monitor.get_summary()
                if perf_summary["status"] != "no_data":
                    detection_latencies.extend(
                        monitor.performance_monitor.detection_latencies
                    )

            # Analyze performance results
            if detection_latencies:
                avg_latency = sum(detection_latencies) / len(detection_latencies)
                max_latency = max(detection_latencies)
                p95_latency = sorted(detection_latencies)[
                    int(len(detection_latencies) * 0.95)
                ]

                # Performance assertions
                assert (
                    avg_latency < 50.0
                ), f"Average detection latency {avg_latency:.2f}ms exceeds 50ms target"
                assert (
                    p95_latency < 100.0
                ), f"95th percentile detection latency {p95_latency:.2f}ms exceeds 100ms SLA"

                print(f"Performance Results:")
                print(f"  Average latency: {avg_latency:.2f}ms")
                print(f"  Max latency: {max_latency:.2f}ms")
                print(f"  95th percentile: {p95_latency:.2f}ms")

        finally:
            monitor.stop()

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, temp_claude_dir):
        """Test system error handling and recovery capabilities."""
        error_count = 0

        def error_tracking_callback(conversation_data: ConversationData):
            nonlocal error_count
            error_count += 1

        monitor = FileMonitor(
            watch_path=str(temp_claude_dir), callback=error_tracking_callback
        )

        try:
            monitor.start()

            # Test 1: Invalid JSON content
            invalid_file = temp_claude_dir / "invalid.jsonl"
            invalid_file.write_text("{'invalid': json content")
            await asyncio.sleep(0.1)

            # Test 2: Missing required fields
            missing_fields_file = temp_claude_dir / "missing-fields.jsonl"
            missing_fields_file.write_text(json.dumps({"incomplete": "data"}))
            await asyncio.sleep(0.1)

            # Test 3: Valid file after errors
            valid_file = temp_claude_dir / "valid.jsonl"
            valid_content = json.dumps(
                {
                    "uuid": str(uuid4()),
                    "sessionId": "recovery-test",
                    "timestamp": "2024-01-15T10:30:00.000Z",
                    "type": "message",
                    "message": {"role": "user", "content": "Recovery test"},
                }
            )
            valid_file.write_text(valid_content)
            await asyncio.sleep(0.2)

            # Verify error handling
            stats = monitor.get_stats()
            assert (
                stats["processing_errors"] >= 2
            )  # At least 2 errors from invalid files
            assert stats["files_processed"] >= 1  # At least 1 successful processing

            # Verify system health
            health = monitor.get_health()
            assert health.service_status in [
                ComponentStatus.OK,
                ComponentStatus.DEGRADED,
            ]

            # Verify parser statistics
            parser_stats = stats["parser_stats"]
            assert parser_stats["parse_errors"] >= 1
            assert parser_stats["validation_errors"] >= 1
            assert parser_stats["messages_parsed"] >= 1

        finally:
            monitor.stop()

    def test_system_health_monitoring(self, temp_claude_dir):
        """Test comprehensive system health monitoring."""
        monitor = FileMonitor(watch_path=str(temp_claude_dir))

        try:
            monitor.start()

            # Get system health
            health = monitor.get_health()

            # Verify health structure
            assert health.service_status in [
                ComponentStatus.OK,
                ComponentStatus.DEGRADED,
                ComponentStatus.UNAVAILABLE,
            ]
            assert len(health.components) >= 3  # filesystem, observer, database

            # Check individual components
            component_names = [comp.component_name for comp in health.components]
            assert "filesystem" in component_names
            assert "observer" in component_names
            assert "database" in component_names

            # Verify filesystem component
            filesystem_comp = next(
                comp
                for comp in health.components
                if comp.component_name == "filesystem"
            )
            assert filesystem_comp.status == ComponentStatus.OK

            # Verify observer component
            observer_comp = next(
                comp for comp in health.components if comp.component_name == "observer"
            )
            assert observer_comp.status == ComponentStatus.OK

        finally:
            monitor.stop()

    def test_statistics_and_metrics_collection(self, temp_claude_dir):
        """Test comprehensive statistics collection across all components."""
        monitor = FileMonitor(watch_path=str(temp_claude_dir))

        try:
            monitor.start()

            # Get comprehensive statistics
            stats = monitor.get_stats()

            # Verify main statistics structure
            required_keys = [
                "files_processed",
                "conversations_created",
                "processing_errors",
                "uptime_seconds",
                "parser_stats",
                "database_stats",
                "performance_stats",
                "is_running",
                "watch_path",
            ]

            for key in required_keys:
                assert key in stats

            # Verify parser stats structure
            parser_stats = stats["parser_stats"]
            parser_required_keys = [
                "lines_processed",
                "messages_parsed",
                "parse_errors",
                "validation_errors",
            ]
            for key in parser_required_keys:
                assert key in parser_stats

            # Verify database stats structure
            db_stats = stats["database_stats"]
            db_required_keys = [
                "conversations_written",
                "conversations_updated",
                "messages_written",
                "write_errors",
            ]
            for key in db_required_keys:
                assert key in db_stats

            # Verify performance stats structure
            perf_stats = stats["performance_stats"]
            assert "status" in perf_stats

            # Verify stats reset functionality
            initial_files_processed = stats["files_processed"]
            monitor.reset_stats()
            reset_stats = monitor.get_stats()
            assert reset_stats["files_processed"] == 0

        finally:
            monitor.stop()


class TestFileMonitoringErrorScenarios:
    """Test error scenarios and edge cases for file monitoring."""

    def test_invalid_watch_path_handling(self):
        """Test handling of invalid watch paths."""
        # Test with non-existent path
        monitor = FileMonitor(watch_path="/non/existent/path")

        try:
            monitor.start()
            # Should create the directory or handle gracefully
            assert monitor.is_running

            health = monitor.get_health()
            # Should either be OK (if created) or have filesystem issues
            assert health.service_status in [
                ComponentStatus.OK,
                ComponentStatus.UNAVAILABLE,
            ]

        finally:
            monitor.stop()

    def test_permission_denied_scenarios(self, temp_claude_dir):
        """Test handling of permission denied scenarios."""
        # Create a file with restricted permissions
        restricted_file = temp_claude_dir / "restricted.jsonl"
        restricted_file.write_text("test content")
        restricted_file.chmod(0o000)  # No permissions

        try:
            parser = JSONLParser()
            result = parser.parse_conversation_file(str(restricted_file))

            # Should return ProcessingError for permission issues
            from app.models.contracts import ProcessingError

            assert isinstance(result, ProcessingError)
            assert (
                "Permission" in result.error_message
                or "permission" in result.error_message.lower()
            )

        finally:
            # Restore permissions for cleanup
            restricted_file.chmod(0o644)

    def test_large_file_handling(self, temp_claude_dir):
        """Test handling of large JSONL files."""
        # Create a large file with many messages
        large_file = temp_claude_dir / "large.jsonl"

        # Generate large content (1000 messages)
        messages = []
        for i in range(1000):
            message = {
                "uuid": str(uuid4()),
                "sessionId": "large-session",
                "timestamp": f"2024-01-15T10:{30 + (i % 30):02d}:00.000Z",
                "type": "message",
                "message": {
                    "role": "user" if i % 2 == 0 else "assistant",
                    "content": f"Message number {i} with some content to make it realistic",
                },
            }
            messages.append(json.dumps(message))

        large_file.write_text("\n".join(messages))

        # Test parsing large file
        parser = JSONLParser()
        start_time = time.perf_counter()
        result = parser.parse_conversation_file(str(large_file))
        end_time = time.perf_counter()

        # Verify successful parsing
        assert isinstance(result, ConversationData)
        assert len(result.messages) == 1000

        # Verify reasonable performance (should be under 5 seconds for 1000 messages)
        parse_time = end_time - start_time
        assert (
            parse_time < 5.0
        ), f"Large file parsing took {parse_time:.2f}s, exceeds 5s limit"

        print(f"Large file parsing performance: {parse_time:.3f}s for 1000 messages")


if __name__ == "__main__":
    # Run with: python -m pytest tests/test_file_monitoring_integration.py -v
    pytest.main([__file__, "-v", "--tb=short"])
