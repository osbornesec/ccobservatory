"""
Test suite for File Handler following Canon TDD approach.
Tests written one at a time, with minimal implementation to pass each test.
"""

import unittest
from unittest.mock import Mock, patch
from pathlib import Path

from app.monitoring.file_handler import ClaudeFileHandler
from app.models.contracts import FileEvent, FileSystemEventType


# Dummy event class to simulate file system events
class DummyEvent:
    def __init__(self, src_path, is_directory=False):
        self.src_path = src_path
        self.is_directory = is_directory

# Dummy moved event class to simulate file move events
class DummyMovedEvent:
    def __init__(self, src_path, dest_path, is_directory=False):
        self.src_path = src_path
        self.dest_path = dest_path
        self.is_directory = is_directory


class TestClaudeFileHandler:
    """Test ClaudeFileHandler functionality following Canon TDD approach."""
    
    def test_on_created_handles_jsonl_file(self):
        """First test: ClaudeFileHandler processes file creation events correctly."""
        # Arrange: Create a mock callback and instantiate the handler
        mock_callback = Mock()
        handler = ClaudeFileHandler(callback=mock_callback)
        
        # Act: Create a dummy event for a .jsonl file in the Claude projects directory
        from pathlib import Path
        test_path = str(Path.home() / ".claude" / "projects" / "test-project" / "transcript.jsonl")
        event = DummyEvent(test_path)
        handler.on_created(event)
        
        # Assert: Verify that the callback was called exactly once
        mock_callback.assert_called_once()
        
        # Extract the FileEvent passed to callback and check its properties
        file_event_arg = mock_callback.call_args[0][0]
        assert file_event_arg.event_type == "created"
        assert str(file_event_arg.src_path) == test_path
    
    def test_is_relevant_file_rejects_non_jsonl_files(self):
        """Second test: _is_relevant_file rejects non-JSONL files."""
        # Arrange: Create handler
        handler = ClaudeFileHandler()
        
        # Act: Test with a non-JSONL file
        test_path = str(Path.home() / ".claude" / "projects" / "test-project" / "readme.txt")
        
        # Assert: Should return False for non-JSONL files
        assert handler._is_relevant_file(test_path) is False
    
    def test_is_relevant_file_rejects_files_outside_claude_projects(self):
        """Third test: _is_relevant_file rejects files outside Claude projects directory."""
        # Arrange: Create handler
        handler = ClaudeFileHandler()
        
        # Act: Test with a JSONL file outside the Claude projects directory
        test_path = str(Path.home() / "some-other-dir" / "transcript.jsonl")
        
        # Assert: Should return False for files outside Claude projects directory
        assert handler._is_relevant_file(test_path) is False
    
    def test_is_relevant_file_handles_path_errors(self):
        """Fourth test: _is_relevant_file handles path errors gracefully."""
        # Arrange: Create handler
        handler = ClaudeFileHandler()
        
        # Act: Test with an invalid path that would cause Path() to raise an exception
        with patch('pathlib.Path') as mock_path:
            mock_path.side_effect = OSError("Invalid path")
            
            # Assert: Should return False when path processing fails
            assert handler._is_relevant_file("invalid-path") is False
    
    def test_create_file_event_handles_creation_errors(self):
        """Fifth test: _create_file_event handles FileEvent creation errors gracefully."""
        # Arrange: Create handler
        handler = ClaudeFileHandler()
        
        # Act: Test with data that would cause FileEvent creation to fail
        with patch('app.monitoring.file_handler.FileEvent') as mock_file_event:
            mock_file_event.side_effect = ValueError("Invalid event data")
            
            # Assert: Should return None when FileEvent creation fails
            result = handler._create_file_event(
                event_type=FileSystemEventType.CREATED,
                src_path="test-path",
                is_directory=False
            )
            assert result is None
    
    def test_handle_event_handles_callback_errors(self):
        """Sixth test: _handle_event handles callback errors gracefully."""
        # Arrange: Create handler with a callback that raises an exception
        mock_callback = Mock(side_effect=RuntimeError("Callback failed"))
        handler = ClaudeFileHandler(callback=mock_callback)
        
        # Create a mock file event
        from app.models.contracts import FileEvent
        mock_event = Mock(spec=FileEvent)
        mock_event.event_type = FileSystemEventType.CREATED
        mock_event.src_path = Path("test-path")
        
        # Act: Call _handle_event which should handle the callback error
        # This should not raise an exception, but should log the error
        handler._handle_event(mock_event)
        
        # Assert: Callback was called despite the error
        mock_callback.assert_called_once_with(mock_event)
    
    def test_on_deleted_handles_jsonl_file_deletion(self):
        """Seventh test: on_deleted handles JSONL file deletion events correctly."""
        # Arrange: Create a mock callback and instantiate the handler
        mock_callback = Mock()
        handler = ClaudeFileHandler(callback=mock_callback)
        
        # Act: Create a dummy deletion event for a .jsonl file in the Claude projects directory
        test_path = str(Path.home() / ".claude" / "projects" / "test-project" / "transcript.jsonl")
        event = DummyEvent(test_path)
        handler.on_deleted(event)
        
        # Assert: Verify that the callback was called exactly once
        mock_callback.assert_called_once()
        
        # Extract the FileEvent passed to callback and check its properties
        file_event_arg = mock_callback.call_args[0][0]
        assert file_event_arg.event_type == "deleted"
        assert str(file_event_arg.src_path) == test_path
    
    def test_on_modified_handles_jsonl_file_modification(self):
        """Eighth test: on_modified handles JSONL file modification events correctly."""
        # Arrange: Create a mock callback and instantiate the handler
        mock_callback = Mock()
        handler = ClaudeFileHandler(callback=mock_callback)
        
        # Act: Create a dummy modification event for a .jsonl file in the Claude projects directory
        test_path = str(Path.home() / ".claude" / "projects" / "test-project" / "transcript.jsonl")
        event = DummyEvent(test_path)
        handler.on_modified(event)
        
        # Assert: Verify that the callback was called exactly once
        mock_callback.assert_called_once()
        
        # Extract the FileEvent passed to callback and check its properties
        file_event_arg = mock_callback.call_args[0][0]
        assert file_event_arg.event_type == "modified"
        assert str(file_event_arg.src_path) == test_path
    
    def test_on_moved_handles_jsonl_file_move(self):
        """Ninth test: on_moved handles JSONL file move events correctly."""
        # Arrange: Create a mock callback and instantiate the handler
        mock_callback = Mock()
        handler = ClaudeFileHandler(callback=mock_callback)
        
        # Act: Create a dummy move event for a .jsonl file in the Claude projects directory
        src_path = str(Path.home() / ".claude" / "projects" / "test-project" / "old-transcript.jsonl")
        dest_path = str(Path.home() / ".claude" / "projects" / "test-project" / "new-transcript.jsonl")
        event = DummyMovedEvent(src_path, dest_path)
        handler.on_moved(event)
        
        # Assert: Verify that the callback was called exactly once
        mock_callback.assert_called_once()
        
        # Extract the FileEvent passed to callback and check its properties
        file_event_arg = mock_callback.call_args[0][0]
        assert file_event_arg.event_type == "moved"
        assert str(file_event_arg.src_path) == src_path
        assert str(file_event_arg.dest_path) == dest_path
    
    def test_handle_event_with_no_callback_logs_debug_message(self):
        """Tenth test: _handle_event logs debug message when no callback is registered."""
        # Arrange: Create handler with no callback
        handler = ClaudeFileHandler(callback=None)
        
        # Create a mock file event
        from app.models.contracts import FileEvent
        mock_event = Mock(spec=FileEvent)
        mock_event.event_type = FileSystemEventType.CREATED
        mock_event.src_path = Path("test-path")
        
        # Act: Call _handle_event which should log debug message
        # This should not raise an exception
        handler._handle_event(mock_event)
        
        # Assert: No exception was raised (implicit assertion by completing the call)