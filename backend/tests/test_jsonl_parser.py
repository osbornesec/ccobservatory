"""
Test suite for JSONLParser following Canon TDD approach.
Tests written one at a time, with minimal implementation to pass each test.
"""

import json
import pytest
from pathlib import Path
from app.monitoring.jsonl_parser import JSONLParser
from app.models.contracts import ConversationData, ProcessingError


class TestJSONLParser:
    """Test JSONLParser functionality following Canon TDD approach."""
    
    @pytest.fixture
    def valid_jsonl_file(self, tmp_path: Path) -> Path:
        """Create a temporary JSONL file with valid Claude Code message format."""
        # Create a valid JSONL line representing a Claude Code message with required fields
        message_data = {
            "uuid": "msg-001",
            "sessionId": "session-123",
            "timestamp": "2024-01-15T10:30:00Z",
            "type": "user",
            "message": {
                "role": "user",
                "content": "Hello, this is a test message."
            }
        }
        
        file_path = tmp_path / "conversation.jsonl"
        # Write one line for simplicity
        file_path.write_text(json.dumps(message_data) + "\n")
        return file_path
    
    def test_parse_valid_jsonl_file_returns_conversation_data(self, valid_jsonl_file: Path):
        """First test: JSONLParser successfully parses valid JSONL conversation file."""
        parser = JSONLParser()
        result = parser.parse_conversation_file(str(valid_jsonl_file))
        
        # Verify that we have a ConversationData object (not ProcessingError)
        assert isinstance(result, ConversationData), "Expected ConversationData object"
        assert not isinstance(result, ProcessingError), "Should not return ProcessingError for valid file"
        
        # Verify that basic structure is present
        assert hasattr(result, 'messages'), "ConversationData should have messages attribute"
        assert isinstance(result.messages, list), "Messages should be a list"
    
    def test_parse_malformed_json_line_returns_processing_error(self):
        """Second test: parse_line correctly handles malformed JSON and returns ProcessingError."""
        parser = JSONLParser()
        # A deliberately malformed JSON string (missing closing brace and quote)
        malformed_json_line = '{"id": "msg-123", "content": "hello world'
        
        result = parser.parse_line(malformed_json_line)
        
        assert isinstance(result, ProcessingError), f"Expected ProcessingError, but got {type(result).__name__}"
        assert result.error_type == "JSONDecodeError", f"Expected error_type 'JSONDecodeError', but got '{result.error_type}'"
        assert result.component == "JSONLParser", f"Expected component 'JSONLParser', but got '{result.component}'"
    
    def test_parse_line_with_missing_required_fields_returns_validation_error(self):
        """Third test: parse_line returns ValidationError when required fields are missing."""
        # Create valid JSON structure but missing a required field (sessionId)
        valid_json_template = {
            "uuid": "msg-001",
            "timestamp": "2024-01-15T10:30:00Z",
            "type": "user",
            "message": {
                "role": "user",
                "content": "Hello, this is a test message."
            }
            # Missing "sessionId" field
        }
        
        jsonl_line = json.dumps(valid_json_template)
        parser = JSONLParser()
        
        result = parser.parse_line(jsonl_line)
        
        assert isinstance(result, ProcessingError), f"Expected ProcessingError, but got {type(result).__name__}"
        assert result.error_type == "ValidationError", f"Expected error_type 'ValidationError', but got '{result.error_type}'"
        assert result.component == "JSONLParser", f"Expected component 'JSONLParser', but got '{result.component}'"
        assert "sessionId" in result.error_message, f"Error message should mention missing 'sessionId' field: {result.error_message}"
    
    def test_parser_tracks_statistics_correctly(self):
        """Fourth test: JSONLParser correctly tracks parsing statistics."""
        parser = JSONLParser()
        
        # Parse multiple lines: some valid, some invalid
        # Valid line
        valid_line = json.dumps({
            "uuid": "msg-001",
            "sessionId": "session-123",
            "timestamp": "2024-01-15T10:30:00Z",
            "type": "user",
            "message": {"role": "user", "content": "Hello"}
        })
        
        # Malformed JSON line
        malformed_line = '{"uuid": "msg-002", "sessionId": "session-123"'  # Missing closing brace
        
        # Line with missing required field
        missing_field_line = json.dumps({
            "uuid": "msg-003",
            "timestamp": "2024-01-15T10:30:00Z",
            "type": "user",
            "message": {"role": "user", "content": "Hello"}
            # Missing sessionId
        })
        
        # Parse the lines
        parser.parse_line(valid_line)        # Should increment lines_processed and messages_parsed
        parser.parse_line(malformed_line)    # Should increment lines_processed and parse_errors
        parser.parse_line(missing_field_line) # Should increment lines_processed and validation_errors
        
        # Check statistics
        stats = parser.get_stats()
        
        assert stats["lines_processed"] == 3, f"Expected 3 lines processed, got {stats['lines_processed']}"
        assert stats["messages_parsed"] == 1, f"Expected 1 message parsed, got {stats['messages_parsed']}"
        assert stats["parse_errors"] == 1, f"Expected 1 parse error, got {stats['parse_errors']}"
        assert stats["validation_errors"] == 1, f"Expected 1 validation error, got {stats['validation_errors']}"
        
        # Test reset_stats
        parser.reset_stats()
        reset_stats = parser.get_stats()
        
        assert reset_stats["lines_processed"] == 0, "lines_processed was not reset to 0"
        assert reset_stats["messages_parsed"] == 0, "messages_parsed was not reset to 0"
        assert reset_stats["parse_errors"] == 0, "parse_errors was not reset to 0"
        assert reset_stats["validation_errors"] == 0, "validation_errors was not reset to 0"