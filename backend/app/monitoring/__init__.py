"""
File monitoring module for Claude Code Observatory.

This module provides real-time file system monitoring for Claude Code JSONL transcript files,
with sub-100ms detection latency and comprehensive error handling.

Components:
- ClaudeFileHandler: Watchdog event handler for .jsonl files
- FileMonitor: Main monitoring service using watchdog Observer
- JSONLParser: Parse Claude Code conversation data from JSONL lines
- DatabaseWriter: Supabase integration for storing parsed data
- PerformanceMonitor: Metrics collection for latency requirements
"""

from .file_handler import ClaudeFileHandler
from .file_monitor import FileMonitor
from .jsonl_parser import JSONLParser
from .database_writer import DatabaseWriter
from .performance_monitor import PerformanceMonitor

__all__ = [
    "ClaudeFileHandler",
    "FileMonitor",
    "JSONLParser",
    "DatabaseWriter",
    "PerformanceMonitor",
]
