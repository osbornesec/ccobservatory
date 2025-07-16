"""
Shared data models and contracts for Claude Code Observatory.

This module contains Pydantic models that define the data contracts between
all components of the system, enabling type-safe parallel development.
"""

from .contracts import (
    # Base models
    ContractBase,
    DBMixin,
    # File system models
    FileSystemEventType,
    FileEvent,
    # Claude conversation models
    ToolUsage,
    ParsedMessage,
    ConversationData,
    # Project models
    ProjectBase,
    ProjectCreate,
    Project,
    # Performance and monitoring models
    PerformanceMetrics,
    ProcessingError,
    # Health check models
    ComponentStatus,
    ComponentHealth,
    SystemHealth,
    # API response models
    APIResponse,
)

__all__ = [
    "ContractBase",
    "DBMixin",
    "FileSystemEventType",
    "FileEvent",
    "ToolUsage",
    "ParsedMessage",
    "ConversationData",
    "ProjectBase",
    "ProjectCreate",
    "Project",
    "PerformanceMetrics",
    "ProcessingError",
    "ComponentStatus",
    "ComponentHealth",
    "SystemHealth",
    "APIResponse",
]
