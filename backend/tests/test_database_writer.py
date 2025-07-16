"""
Test suite for Database Writer following Canon TDD approach.
Tests written one at a time, with minimal implementation to pass each test.
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from uuid import UUID, uuid4

from app.monitoring.database_writer import DatabaseWriter
from app.models.contracts import ConversationData, ParsedMessage
from supabase import Client


class TestDatabaseWriter:
    """Test DatabaseWriter functionality following Canon TDD approach."""
    
    def test_database_writer_initialization(self):
        """First test: DatabaseWriter initializes its attributes correctly."""
        mock_supabase_client = Mock(spec=Client)
        
        writer = DatabaseWriter(client=mock_supabase_client)
        
        # Assert that the client dependency is correctly assigned
        assert writer._client is mock_supabase_client, \
            "The _client attribute should be the client passed during initialization."
        
        # Assert that stats is initialized as a dictionary
        assert isinstance(writer.stats, dict), \
            "The stats attribute should be initialized as a dictionary."
        
        # Assert that stats contains expected keys
        assert "conversations_written" in writer.stats, \
            "The stats should contain conversations_written counter."
        assert "conversations_updated" in writer.stats, \
            "The stats should contain conversations_updated counter."
    
    def test_write_conversation_handles_conversationdata_successfully(self):
        """Second test: write_conversation method handles ConversationData correctly."""
        # Create a sample ConversationData object
        project_id = uuid4()
        conversation_data = ConversationData(
            project_id=project_id,
            session_id="test-session-123",
            title="Test Conversation",
            message_count=2,
            messages=[]
        )
        
        # Create mock Supabase client
        mock_client = MagicMock()
        
        # Create DatabaseWriter with mock client
        writer = DatabaseWriter(client=mock_client)
        
        # Mock the _write_conversation_record method to return a UUID
        expected_conversation_id = uuid4()
        writer._write_conversation_record = MagicMock(return_value=expected_conversation_id)
        
        # Call the method under test
        success, conversation_id, db_metrics = writer.write_conversation(conversation_data)
        
        # Assert the basic successful path expectations
        assert success is True, "Expected success to be True"
        assert conversation_id == expected_conversation_id, "Expected conversation_id to match returned UUID"
        assert isinstance(db_metrics, dict), "Expected db_metrics to be a dict"
        assert "total_write_ms" in db_metrics, "Expected db_metrics to contain total_write_ms"

    def test_write_conversation_handles_processing_error(self):
        """Third test: write_conversation handles ProcessingError exceptions."""
        # Create a sample ConversationData object
        project_id = uuid4()
        conversation_data = ConversationData(
            project_id=project_id,
            session_id="test-session-456",
            title="Test Conversation with Error",
            message_count=1,
            messages=[]
        )
        
        # Create mock Supabase client
        mock_client = MagicMock()
        
        # Create DatabaseWriter with mock client
        writer = DatabaseWriter(client=mock_client)
        
        # Mock the _write_conversation_record method to raise a regular Exception
        # Since ProcessingError is a Pydantic model but the code tries to raise it
        # For testing purposes, we'll test the exception handling path
        writer._write_conversation_record = MagicMock(side_effect=Exception("Database error"))
        
        # Test that exception is handled and DatabaseWriterError is raised
        from app.monitoring.database_writer import DatabaseWriterError
        try:
            writer.write_conversation(conversation_data)
            assert False, "Expected DatabaseWriterError to be raised"
        except DatabaseWriterError as e:
            assert e.processing_error.error_type == "UnexpectedDatabaseError"
            assert "Database error" in e.processing_error.error_message
            assert writer.stats["write_errors"] == 1

    def test_write_conversation_handles_unexpected_error(self):
        """Fourth test: write_conversation handles unexpected exceptions."""
        # Create a sample ConversationData object
        project_id = uuid4()
        conversation_data = ConversationData(
            project_id=project_id,
            session_id="test-session-789",
            title="Test Conversation with Unexpected Error",
            message_count=1,
            messages=[]
        )
        
        # Create mock Supabase client
        mock_client = MagicMock()
        
        # Create DatabaseWriter with mock client
        writer = DatabaseWriter(client=mock_client)
        
        # Mock the _write_conversation_record method to raise unexpected exception
        writer._write_conversation_record = MagicMock(side_effect=ValueError("Unexpected error"))
        
        # Test that exception is handled and DatabaseWriterError is raised
        from app.monitoring.database_writer import DatabaseWriterError
        try:
            writer.write_conversation(conversation_data)
            assert False, "Expected DatabaseWriterError to be raised"
        except DatabaseWriterError as e:
            assert e.processing_error.error_type == "UnexpectedDatabaseError"
            assert "Unexpected error writing conversation" in e.processing_error.error_message
            assert writer.stats["write_errors"] == 1

    def test_write_conversation_with_messages_calls_batch_upsert(self):
        """Fifth test: write_conversation calls _batch_upsert_messages when messages exist."""
        # Create sample messages
        from app.models.contracts import ParsedMessage
        from datetime import datetime, timezone
        
        conversation_id = uuid4()
        message1 = ParsedMessage(
            conversation_id=conversation_id,
            message_id="test-msg-1",
            role="user",
            content="Test message 1",
            timestamp=datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        )
        message2 = ParsedMessage(
            conversation_id=conversation_id,
            message_id="test-msg-2",
            role="assistant", 
            content="Test message 2",
            timestamp=datetime(2023, 1, 1, 0, 1, 0, tzinfo=timezone.utc)
        )
        
        # Create ConversationData with messages
        project_id = uuid4()
        conversation_data = ConversationData(
            project_id=project_id,
            session_id="test-session-with-messages",
            title="Test Conversation with Messages",
            message_count=2,
            messages=[message1, message2]
        )
        
        # Create mock Supabase client
        mock_client = MagicMock()
        
        # Create DatabaseWriter with mock client
        writer = DatabaseWriter(client=mock_client)
        
        # Mock the internal methods
        expected_conversation_id = uuid4()
        writer._write_conversation_record = MagicMock(return_value=expected_conversation_id)
        writer._batch_upsert_messages = MagicMock()
        
        # Call the method under test
        success, conversation_id, db_metrics = writer.write_conversation(conversation_data)
        
        # Verify that _batch_upsert_messages was called
        writer._batch_upsert_messages.assert_called_once_with(expected_conversation_id, conversation_data.messages)
        
        # Verify message stats were updated
        assert writer.stats["messages_written"] == 2
        assert "messages_write_ms" in db_metrics
    
    def test_write_conversation_record_retry_on_transient_api_error(self):
        """Sixth test: _write_conversation_record retries on transient API error and succeeds."""
        # Create a sample ConversationData object
        project_id = uuid4()
        conversation_data = ConversationData(
            project_id=project_id,
            session_id="test-session-retry",
            title="Test Conversation for Retry Logic",
            message_count=0,
            messages=[]
        )
        
        # Create mock Supabase client
        mock_client = MagicMock()
        
        # Create DatabaseWriter with mock client
        writer = DatabaseWriter(client=mock_client)
        
        # Mock the table operations to simulate transient error then success
        from postgrest import APIError
        
        # First call fails with APIError (transient)
        # Second call succeeds
        mock_table = MagicMock()
        mock_client.table.return_value = mock_table
        
        # Mock the select query (check for existing conversation)
        mock_select = MagicMock()
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_select
        mock_select.limit.return_value = mock_select
        
        # Mock response for existing conversation check (no existing record)
        mock_execute_response = MagicMock()
        mock_execute_response.data = []  # No existing conversation
        mock_select.execute.return_value = mock_execute_response
        
        # Mock the insert operation - first call fails, second succeeds
        mock_insert = MagicMock()
        mock_table.insert.return_value = mock_insert
        
        # Configure side effects: first call raises APIError, second succeeds
        mock_insert.execute.side_effect = [
            APIError({"message": "Temporary database error"}),  # First attempt fails
            MagicMock(data=[{"id": str(uuid4())}])  # Second attempt succeeds
        ]
        
        # Call the method under test
        conversation_id = writer._write_conversation_record(conversation_data)
        
        # Verify retry behavior
        assert mock_insert.execute.call_count == 2, "Expected exactly 2 calls (1 failure + 1 success)"
        assert isinstance(conversation_id, UUID), "Should return a valid UUID"
        assert writer.stats["conversations_written"] == 1, "Should increment conversations_written counter"
    
    def test_write_conversation_record_updates_existing_conversation(self):
        """Seventh test: _write_conversation_record updates existing conversation instead of inserting new one."""
        # Create a sample ConversationData object
        project_id = uuid4()
        conversation_data = ConversationData(
            project_id=project_id,
            session_id="test-session-update",
            title="Updated Test Conversation",
            message_count=5,
            messages=[]
        )
        
        # Create mock Supabase client
        mock_client = MagicMock()
        
        # Create DatabaseWriter with mock client
        writer = DatabaseWriter(client=mock_client)
        
        # Mock the table operations to simulate existing conversation
        mock_table = MagicMock()
        mock_client.table.return_value = mock_table
        
        # Mock the select query (check for existing conversation)
        mock_select = MagicMock()
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_select
        mock_select.limit.return_value = mock_select
        
        # Mock response for existing conversation check (existing record found)
        existing_conversation_id = uuid4()
        mock_execute_response = MagicMock()
        mock_execute_response.data = [{"id": str(existing_conversation_id)}]  # Existing conversation
        mock_select.execute.return_value = mock_execute_response
        
        # Mock the update operation
        mock_update = MagicMock()
        mock_table.update.return_value = mock_update
        mock_update.eq.return_value = mock_update
        mock_update.execute.return_value = MagicMock(data=[{"id": str(existing_conversation_id)}])
        
        # Call the method under test
        conversation_id = writer._write_conversation_record(conversation_data)
        
        # Verify update behavior
        mock_table.update.assert_called_once()  # Should call update, not insert
        mock_update.eq.assert_called_once_with("id", str(existing_conversation_id))
        mock_update.execute.assert_called_once()
        
        # Verify that insert was NOT called
        mock_table.insert.assert_not_called()
        
        # Verify return value and stats
        assert conversation_id == existing_conversation_id, "Should return the existing conversation ID"
        assert writer.stats["conversations_updated"] == 1, "Should increment conversations_updated counter"
        assert writer.stats["conversations_written"] == 0, "Should not increment conversations_written counter"
    
    def test_batch_upsert_messages_handles_empty_messages_list(self):
        """Eighth test: _batch_upsert_messages handles empty messages list gracefully."""
        # Create mock Supabase client
        mock_client = MagicMock()
        
        # Create DatabaseWriter with mock client
        writer = DatabaseWriter(client=mock_client)
        
        # Create a conversation ID
        conversation_id = uuid4()
        
        # Call the method with empty messages list
        writer._batch_upsert_messages(conversation_id, [])
        
        # Verify that no database operations were attempted
        mock_client.table.assert_not_called()
        
        # Verify that no errors were raised (method should return early)
    
    def test_batch_upsert_messages_successfully_upserts_messages(self):
        """Ninth test: _batch_upsert_messages successfully upserts messages to database."""
        # Create mock Supabase client
        mock_client = MagicMock()
        
        # Create DatabaseWriter with mock client
        writer = DatabaseWriter(client=mock_client)
        
        # Create sample messages
        from datetime import datetime, timezone
        conversation_id = uuid4()
        messages = [
            ParsedMessage(
                conversation_id=conversation_id,
                message_id="msg-1",
                role="user",
                content="Test message 1",
                timestamp=datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
            ),
            ParsedMessage(
                conversation_id=conversation_id,
                message_id="msg-2",
                role="assistant",
                content="Test message 2",
                timestamp=datetime(2023, 1, 1, 0, 1, 0, tzinfo=timezone.utc)
            )
        ]
        
        # Mock the table operations
        mock_table = MagicMock()
        mock_client.table.return_value = mock_table
        
        # Mock the upsert operation
        mock_upsert = MagicMock()
        mock_table.upsert.return_value = mock_upsert
        mock_upsert.execute.return_value = MagicMock(data=[{"id": "1"}, {"id": "2"}])
        
        # Call the method under test
        writer._batch_upsert_messages(conversation_id, messages)
        
        # Verify upsert operation was called
        mock_table.upsert.assert_called_once()
        mock_upsert.execute.assert_called_once()
        
        # Verify the correct table was accessed
        mock_client.table.assert_called_once_with("messages")
        
        # Verify upsert was called with correct parameters
        upsert_call_args = mock_table.upsert.call_args
        assert upsert_call_args[1]["on_conflict"] == "conversation_id, message_id"
        
        # Verify payload structure
        payload = upsert_call_args[0][0]
        assert len(payload) == 2
        assert payload[0]["message_id"] == "msg-1"
        assert payload[0]["role"] == "user"
        assert payload[0]["content"] == "Test message 1"
        assert payload[1]["message_id"] == "msg-2"
        assert payload[1]["role"] == "assistant"
        assert payload[1]["content"] == "Test message 2"
    
    def test_get_stats_returns_copy_of_stats(self):
        """Tenth test: get_stats returns a copy of current statistics."""
        # Create mock Supabase client
        mock_client = MagicMock()
        
        # Create DatabaseWriter with mock client
        writer = DatabaseWriter(client=mock_client)
        
        # Modify some stats
        writer.stats["conversations_written"] = 5
        writer.stats["messages_written"] = 10
        
        # Get stats
        stats = writer.get_stats()
        
        # Verify stats are correct
        assert stats["conversations_written"] == 5
        assert stats["messages_written"] == 10
        
        # Verify it's a copy (modifying returned stats doesn't affect original)
        stats["conversations_written"] = 999
        assert writer.stats["conversations_written"] == 5, "Should not modify original stats"
    
    def test_reset_stats_resets_all_counters_to_zero(self):
        """Eleventh test: reset_stats resets all statistics counters to zero."""
        # Create mock Supabase client
        mock_client = MagicMock()
        
        # Create DatabaseWriter with mock client
        writer = DatabaseWriter(client=mock_client)
        
        # Set some stats
        writer.stats["conversations_written"] = 5
        writer.stats["conversations_updated"] = 3
        writer.stats["messages_written"] = 10
        writer.stats["write_errors"] = 2
        
        # Reset stats
        writer.reset_stats()
        
        # Verify all stats are reset to zero
        assert writer.stats["conversations_written"] == 0
        assert writer.stats["conversations_updated"] == 0
        assert writer.stats["messages_written"] == 0
        assert writer.stats["write_errors"] == 0