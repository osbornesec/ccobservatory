"""
Shared data contracts and models for Claude Code Observatory.

This module defines the Pydantic models that serve as contracts between
all components of the file monitoring system. These models ensure type safety,
validation, and consistent data structures across parallel development.
"""

from __future__ import annotations
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Generic, Literal, Optional, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator, DirectoryPath
from pydantic_core import PydanticCustomError

# --- Base Models & Configuration ---


class ContractBase(BaseModel):
    """Base model with shared configuration for all contract models."""

    model_config = ConfigDict(
        from_attributes=True,  # Allows creating models from ORM objects/other classes
        populate_by_name=True,  # Allows using aliases for field names
        use_enum_values=True,  # Serializes enums to their values
        validate_assignment=True,  # Re-validates model on field assignment
    )


class DBMixin(ContractBase):
    """
    Mixin for database-managed fields that are common to all persisted entities.
    Includes primary key and timestamp fields managed by PostgreSQL.
    """

    id: UUID = Field(..., description="Primary key (database-generated)")
    created_at: datetime = Field(
        ..., description="Record creation timestamp (database-generated)"
    )
    updated_at: datetime = Field(
        ..., description="Record last update timestamp (database-generated)"
    )


# --- File System Event Models ---


class FileSystemEventType(str, Enum):
    """Controlled vocabulary for watchdog file system events."""

    CREATED = "created"
    DELETED = "deleted"
    MODIFIED = "modified"
    MOVED = "moved"


class FileEvent(ContractBase):
    """
    Represents a file system event detected by watchdog.
    This is the initial data packet that triggers processing pipelines.

    Performance requirement: Events must be processed within <100ms of detection.
    """

    event_id: UUID = Field(
        default_factory=uuid4, description="Unique identifier for this event"
    )
    event_type: FileSystemEventType = Field(
        ..., description="Type of file system event"
    )
    src_path: Path = Field(..., description="Source file path that triggered the event")
    is_directory: bool = Field(
        default=False, description="Whether the path is a directory"
    )
    dest_path: Optional[Path] = Field(
        default=None, description="Destination path for moved events"
    )
    detected_at: datetime = Field(
        default_factory=datetime.utcnow, description="When the event was detected"
    )

    @model_validator(mode='after')
    def validate_dest_path_for_moved_event(self):
        """Enforce that dest_path is only present for 'moved' events."""
        if self.event_type == FileSystemEventType.MOVED and self.dest_path is None:
            raise PydanticCustomError(
                "dest_path_required",
                "dest_path is required for moved events"
            )
        if self.event_type != FileSystemEventType.MOVED and self.dest_path is not None:
            raise PydanticCustomError(
                "dest_path_not_allowed",
                "dest_path is only allowed for moved events"
            )
        return self


# --- Claude Conversation Models ---


class ToolUsage(ContractBase):
    """
    Represents a single tool invocation within a message.
    Maps to the 'tool_usage' JSONB column in the 'messages' table.
    """

    tool_name: str = Field(..., description="Name of the tool that was invoked")
    tool_input: dict[str, Any] = Field(
        ..., description="Input parameters passed to the tool"
    )
    tool_output: Optional[dict[str, Any]] = Field(
        default=None, description="Output returned by the tool"
    )
    status: Optional[Literal["pending", "success", "error"]] = Field(
        default=None, description="Execution status"
    )


class ParsedMessage(ContractBase):
    """
    Represents a single message from a parsed conversation file.
    Designed to map directly to the 'messages' table schema.
    """

    id: Optional[UUID] = Field(
        default=None, description="Database-generated primary key"
    )
    conversation_id: UUID = Field(..., description="Foreign key to conversations table")
    message_id: str = Field(..., description="Unique message ID from source JSONL data")
    parent_id: Optional[str] = Field(
        default=None, description="Parent message ID for threading"
    )
    timestamp: datetime = Field(..., description="When the message was created")
    role: Literal["user", "assistant"] = Field(..., description="Message author role")
    content: str = Field(..., description="Message content text")
    tool_usage: Optional[list[ToolUsage]] = Field(
        default=None, description="Tools used in this message"
    )


class ConversationData(ContractBase):
    """
    Represents the full metadata and content of a conversation.
    Maps to the 'conversations' table and includes related messages.
    """

    id: Optional[UUID] = Field(
        default=None, description="Database-generated primary key"
    )
    project_id: UUID = Field(..., description="Foreign key to projects table")
    session_id: str = Field(..., description="Claude Code session identifier")
    title: Optional[str] = Field(
        default=None, description="Conversation title (may be derived)"
    )
    message_count: int = Field(
        default=0, ge=0, description="Number of messages in conversation"
    )
    messages: list[ParsedMessage] = Field(
        default_factory=list, description="Messages in conversation"
    )
    created_at: Optional[datetime] = Field(
        default=None, description="Database-generated creation time"
    )
    updated_at: Optional[datetime] = Field(
        default=None, description="Database-generated update time"
    )


# --- Project Models ---


class ProjectBase(ContractBase):
    """Base fields for project models."""

    name: str = Field(
        ..., min_length=1, max_length=100, description="User-defined project name"
    )
    path: DirectoryPath = Field(
        ..., description="Absolute path to project directory being monitored"
    )


class ProjectCreate(ProjectBase):
    """Model for creating a new project via API."""

    pass


class Project(DBMixin, ProjectBase):
    """
    Full project model representing a record from the 'projects' table.
    Includes all database-managed fields.
    """

    last_activity: datetime = Field(
        ..., description="Timestamp of last detected activity"
    )


# --- Performance & Error Models ---


class PerformanceMetrics(ContractBase):
    """
    Represents performance metrics for monitoring the system.
    Maps to the 'performance_metrics' table.

    Note: We intentionally do not validate latency < 100ms here to allow
    recording of performance degradation events for monitoring and alerting.
    """

    id: Optional[UUID] = Field(
        default=None, description="Database-generated primary key"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When metrics were recorded"
    )
    detection_latency_ms: float = Field(
        ..., gt=0, description="Time from file event to detection"
    )
    processing_latency_ms: float = Field(
        ..., gt=0, description="Time to parse and process the file"
    )
    throughput_msgs_per_sec: float = Field(
        ..., ge=0, description="Messages processed per second"
    )


class ProcessingError(ContractBase):
    """
    Structured error model for handling and logging failures in the processing pipeline.
    Provides consistent error reporting across all components.
    """

    error_type: str = Field(
        ..., description="Error category (e.g., 'ParsingError', 'ValidationError')"
    )
    error_message: str = Field(..., description="Human-readable error description")
    failed_at: datetime = Field(
        default_factory=datetime.utcnow, description="When the error occurred"
    )
    original_event: Optional[dict[str, Any]] = Field(
        default=None, description="Raw event that caused failure"
    )
    component: Optional[str] = Field(
        default=None, description="Component where error occurred"
    )


# --- Health Check Models ---


class ComponentStatus(str, Enum):
    """Enumeration for the health status of a component."""

    OK = "ok"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class ComponentHealth(ContractBase):
    """Represents the health of a single system component or dependency."""

    component_name: str = Field(
        ..., description="Name of component (e.g., 'database', 'filesystem')"
    )
    status: ComponentStatus = Field(
        ..., description="Operational status of the component"
    )
    details: Optional[str] = Field(
        default=None, description="Additional details, especially for non-OK status"
    )
    last_checked: datetime = Field(
        default_factory=datetime.utcnow, description="When health was last checked"
    )


class SystemHealth(ContractBase):
    """Represents the overall health of the service."""

    service_status: ComponentStatus = Field(
        ..., description="Overall service status derived from components"
    )
    components: list[ComponentHealth] = Field(
        ..., description="Health status of individual components"
    )
    checked_at: datetime = Field(
        default_factory=datetime.utcnow, description="When system health was assessed"
    )


# --- API Response Models ---

T = TypeVar("T")


class APIResponse(ContractBase, Generic[T]):
    """
    Standardized API response wrapper for consistent client communication.
    Provides clear structure for both success and failure responses.
    """

    success: bool = Field(default=True, description="Whether the operation succeeded")
    data: Optional[T] = Field(
        default=None, description="Response data (for successful operations)"
    )
    error: Optional[ProcessingError] = Field(
        default=None, description="Error details (for failed operations)"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )
