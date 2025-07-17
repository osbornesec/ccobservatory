"""
JSONLParser implementation for parsing Claude Code conversation data.

This module parses JSONL lines from Claude Code transcript files and converts
them to structured Pydantic models for database storage.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from app.models.contracts import (
    ParsedMessage,
    ConversationData,
    ToolUsage,
    ProcessingError,
)

logger = logging.getLogger(__name__)


class JSONLParser:
    """
    Parser for Claude Code JSONL transcript files.

    Converts raw JSONL lines to structured conversation data using
    our Pydantic contract models with comprehensive error handling.
    """

    def __init__(self):
        """Initialize the JSONL parser."""
        self.stats = {
            "lines_processed": 0,
            "messages_parsed": 0,
            "parse_errors": 0,
            "validation_errors": 0,
        }

        logger.info("JSONLParser initialized")

    def parse_line(self, line: str) -> Union[ParsedMessage, ProcessingError]:
        """
        Parse a single JSONL line into a ParsedMessage object.

        Args:
            line: Raw JSONL line from transcript file

        Returns:
            ParsedMessage object on success, ProcessingError on failure
        """
        self.stats["lines_processed"] += 1

        try:
            # Parse JSON
            raw_data = json.loads(line.strip())

            # Extract and validate required fields
            message = self._extract_message_data(raw_data)
            if isinstance(message, ProcessingError):
                self.stats["validation_errors"] += 1
                return message

            self.stats["messages_parsed"] += 1
            return message

        except json.JSONDecodeError as e:
            self.stats["parse_errors"] += 1
            error = ProcessingError(
                error_type="JSONDecodeError",
                error_message=f"Failed to parse JSON: {str(e)}",
                component="JSONLParser",
                original_event={"line": line[:200]},  # Truncate for logging
            )
            logger.warning(f"JSON parse error: {error}")
            return error

        except Exception as e:
            self.stats["parse_errors"] += 1
            error = ProcessingError(
                error_type="UnexpectedError",
                error_message=f"Unexpected error parsing line: {str(e)}",
                component="JSONLParser",
                original_event={"line": line[:200]},
            )
            logger.error(f"Unexpected parse error: {error}")
            return error

    def _extract_message_data(
        self, raw_data: Dict[str, Any]
    ) -> Union[ParsedMessage, ProcessingError]:
        """
        Extract and validate message data from parsed JSON.

        Args:
            raw_data: Parsed JSON data

        Returns:
            ParsedMessage object on success, ProcessingError on failure
        """
        try:
            # Validate required fields
            required_fields = ["uuid", "sessionId", "timestamp", "type", "message"]
            missing_fields = [
                field for field in required_fields if field not in raw_data
            ]

            if missing_fields:
                return ProcessingError(
                    error_type="ValidationError",
                    error_message=f"Missing required fields: {missing_fields}",
                    component="JSONLParser",
                    original_event={"data_keys": list(raw_data.keys())},
                )

            # Extract message content
            message_data = raw_data["message"]
            if not isinstance(message_data, dict) or "role" not in message_data:
                return ProcessingError(
                    error_type="ValidationError",
                    error_message="Invalid message structure - missing role",
                    component="JSONLParser",
                )

            # Parse role
            role = message_data["role"]
            if role not in ["user", "assistant"]:
                return ProcessingError(
                    error_type="ValidationError",
                    error_message=f"Invalid role: {role}. Must be 'user' or 'assistant'",
                    component="JSONLParser",
                )

            # Extract content
            content = self._extract_content(message_data.get("content", ""))

            # Extract tool usage
            tool_usage = self._extract_tool_usage(message_data.get("content", []))

            # Parse timestamp
            try:
                timestamp = datetime.fromisoformat(
                    raw_data["timestamp"].replace("Z", "+00:00")
                )
            except (ValueError, AttributeError) as e:
                return ProcessingError(
                    error_type="ValidationError",
                    error_message=f"Invalid timestamp format: {str(e)}",
                    component="JSONLParser",
                )

            # Create ParsedMessage
            return ParsedMessage(
                conversation_id=uuid4(),  # This will be set properly by the conversation aggregator
                message_id=raw_data["uuid"],
                parent_id=raw_data.get("parentUuid"),
                timestamp=timestamp,
                role=role,
                content=content,
                tool_usage=tool_usage if tool_usage else None,
            )

        except Exception as e:
            return ProcessingError(
                error_type="ExtractionError",
                error_message=f"Error extracting message data: {str(e)}",
                component="JSONLParser",
            )

    def _extract_content(self, content_data: Union[str, List[Dict[str, Any]]]) -> str:
        """
        Extract text content from message content field.

        Args:
            content_data: Content field from message (string or array)

        Returns:
            Extracted text content
        """
        if isinstance(content_data, str):
            return content_data

        if isinstance(content_data, list):
            text_parts = []
            for block in content_data:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
            return "\n".join(text_parts)

        return ""

    def _extract_tool_usage(
        self, content_data: Union[str, List[Dict[str, Any]]]
    ) -> List[ToolUsage]:
        """
        Extract tool usage information from message content.

        Args:
            content_data: Content field from message

        Returns:
            List of ToolUsage objects
        """
        if not isinstance(content_data, list):
            return []

        tools = []
        tool_calls = {}  # Track tool calls by ID

        for block in content_data:
            if not isinstance(block, dict):
                continue

            block_type = block.get("type")

            # Process tool_use blocks
            if block_type == "tool_use":
                tool_id = block.get("id")
                tool_name = block.get("name")
                tool_input = block.get("input", {})

                if tool_id and tool_name:
                    tool_usage = ToolUsage(
                        tool_name=tool_name, tool_input=tool_input, status="pending"
                    )
                    tools.append(tool_usage)
                    tool_calls[tool_id] = (
                        len(tools) - 1
                    )  # Store index for result mapping

            # Process tool_result blocks
            elif block_type == "tool_result":
                tool_use_id = block.get("tool_use_id")
                is_error = block.get("is_error", False)
                tool_output = block.get("content")

                if tool_use_id in tool_calls:
                    tool_index = tool_calls[tool_use_id]
                    tools[tool_index].tool_output = tool_output
                    tools[tool_index].status = "error" if is_error else "success"

        return tools

    def parse_conversation_file(
        self, file_path: str
    ) -> Union[ConversationData, ProcessingError]:
        """
        Parse an entire JSONL conversation file.

        Args:
            file_path: Path to the JSONL file

        Returns:
            ConversationData object on success, ProcessingError on failure
        """
        try:
            messages = []
            session_id = None
            project_id = uuid4()  # This should be determined by the file path

            with open(file_path, "r", encoding="utf-8") as file:
                for line_num, line in enumerate(file, 1):
                    if not line.strip():
                        continue

                    result = self.parse_line(line)

                    if isinstance(result, ProcessingError):
                        logger.warning(
                            f"Error parsing line {line_num} in {file_path}: {result}"
                        )
                        continue

                    # Set consistent conversation_id and extract session_id
                    if not session_id:
                        # Extract session ID from first message (this is file-specific)
                        session_id = f"file_{hash(file_path)}"  # Temporary - should be from actual data

                    messages.append(result)

            if not messages:
                return ProcessingError(
                    error_type="EmptyFile",
                    error_message=f"No valid messages found in {file_path}",
                    component="JSONLParser",
                )

            # Set conversation_id for all messages
            conversation_id = uuid4()
            for message in messages:
                message.conversation_id = conversation_id

            # Create conversation data
            conversation = ConversationData(
                id=conversation_id,
                project_id=project_id,
                file_path=file_path,
                session_id=session_id or "unknown",
                title=f"Conversation from {file_path}",
                message_count=len(messages),
                messages=messages,
            )

            logger.info(
                f"Parsed conversation with {len(messages)} messages from {file_path}"
            )
            return conversation

        except FileNotFoundError:
            return ProcessingError(
                error_type="FileNotFound",
                error_message=f"File not found: {file_path}",
                component="JSONLParser",
            )

        except PermissionError:
            return ProcessingError(
                error_type="PermissionError",
                error_message=f"Permission denied reading file: {file_path}",
                component="JSONLParser",
            )

        except Exception as e:
            return ProcessingError(
                error_type="FileProcessingError",
                error_message=f"Error processing file {file_path}: {str(e)}",
                component="JSONLParser",
            )

    def get_stats(self) -> Dict[str, int]:
        """
        Get parsing statistics.

        Returns:
            Dictionary of parsing statistics
        """
        return self.stats.copy()

    def reset_stats(self) -> None:
        """Reset parsing statistics."""
        self.stats = {
            "lines_processed": 0,
            "messages_parsed": 0,
            "parse_errors": 0,
            "validation_errors": 0,
        }
