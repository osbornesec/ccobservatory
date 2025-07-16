"""
ClaudeFileHandler implementation for processing watchdog file system events.

This module provides the event handler that filters and processes .jsonl files
from Claude Code projects with sub-100ms latency requirements.
"""

import logging
import os
from pathlib import Path
from typing import Optional

from watchdog.events import (
    FileSystemEventHandler,
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileMovedEvent,
)

from app.models.contracts import FileEvent, FileSystemEventType, ProcessingError

logger = logging.getLogger(__name__)


class ClaudeFileHandler(FileSystemEventHandler):
    """
    Watchdog event handler for Claude Code JSONL transcript files.

    Filters for .jsonl files in ~/.claude/projects/** paths and converts
    filesystem events to structured FileEvent objects for processing.

    Performance requirement: Process events within <100ms of detection.
    """

    def __init__(self, callback=None):
        """
        Initialize the Claude file handler.

        Args:
            callback: Optional callback function to receive FileEvent objects.
                     Should accept FileEvent as parameter.
        """
        super().__init__()
        self.callback = callback
        self._claude_projects_path = Path.home() / ".claude" / "projects"

        logger.info(
            f"ClaudeFileHandler initialized, monitoring: {self._claude_projects_path}"
        )

    def _is_relevant_file(self, file_path: str) -> bool:
        """
        Check if the file is a relevant .jsonl file in Claude projects directory.

        Args:
            file_path: Path to the file that triggered the event

        Returns:
            True if file should be processed, False otherwise
        """
        try:
            path = Path(file_path)

            # Check file extension
            if path.suffix.lower() != ".jsonl":
                return False

            # Check if file is within Claude projects directory
            try:
                path.resolve().relative_to(self._claude_projects_path.resolve())
                return True
            except ValueError:
                # Path is not relative to Claude projects directory
                return False

        except Exception as e:
            logger.warning(f"Error checking file relevance for {file_path}: {e}")
            return False

    def _create_file_event(
        self,
        event_type: FileSystemEventType,
        src_path: str,
        dest_path: Optional[str] = None,
        is_directory: bool = False,
    ) -> Optional[FileEvent]:
        """
        Create a FileEvent object from filesystem event data.

        Args:
            event_type: Type of filesystem event
            src_path: Source file path
            dest_path: Destination path (for moved events)
            is_directory: Whether the path is a directory

        Returns:
            FileEvent object or None if creation fails
        """
        try:
            file_event = FileEvent(
                event_type=event_type,
                src_path=Path(src_path),
                dest_path=Path(dest_path) if dest_path else None,
                is_directory=is_directory,
            )

            logger.debug(f"Created FileEvent: {event_type} for {src_path}")
            return file_event

        except Exception as e:
            logger.error(f"Failed to create FileEvent: {e}")
            return None

    def _handle_event(self, file_event: FileEvent) -> None:
        """
        Handle a processed FileEvent by calling the callback if available.

        Args:
            file_event: The FileEvent to handle
        """
        try:
            if self.callback:
                self.callback(file_event)
            else:
                logger.debug(
                    f"No callback registered for event: {file_event.event_type}"
                )

        except Exception as e:
            error = ProcessingError(
                error_type="CallbackError",
                error_message=f"Error in event callback: {str(e)}",
                component="ClaudeFileHandler",
                original_event={
                    "event_type": file_event.event_type.value,
                    "src_path": str(file_event.src_path),
                },
            )
            logger.error(f"Callback error: {error}")

    def on_created(self, event: FileCreatedEvent) -> None:
        """
        Handle file/directory creation events.

        Args:
            event: The file creation event from watchdog
        """
        if not event.is_directory and self._is_relevant_file(event.src_path):
            file_event = self._create_file_event(
                event_type=FileSystemEventType.CREATED,
                src_path=event.src_path,
                is_directory=event.is_directory,
            )

            if file_event:
                logger.info(f"File created: {event.src_path}")
                self._handle_event(file_event)

    def on_deleted(self, event: FileDeletedEvent) -> None:
        """
        Handle file/directory deletion events.

        Args:
            event: The file deletion event from watchdog
        """
        if not event.is_directory and self._is_relevant_file(event.src_path):
            file_event = self._create_file_event(
                event_type=FileSystemEventType.DELETED,
                src_path=event.src_path,
                is_directory=event.is_directory,
            )

            if file_event:
                logger.info(f"File deleted: {event.src_path}")
                self._handle_event(file_event)

    def on_modified(self, event: FileModifiedEvent) -> None:
        """
        Handle file/directory modification events.

        Args:
            event: The file modification event from watchdog
        """
        if not event.is_directory and self._is_relevant_file(event.src_path):
            file_event = self._create_file_event(
                event_type=FileSystemEventType.MODIFIED,
                src_path=event.src_path,
                is_directory=event.is_directory,
            )

            if file_event:
                logger.debug(f"File modified: {event.src_path}")
                self._handle_event(file_event)

    def on_moved(self, event: FileMovedEvent) -> None:
        """
        Handle file/directory move events.

        Args:
            event: The file move event from watchdog
        """
        # Check if either source or destination is relevant
        src_relevant = self._is_relevant_file(event.src_path)
        dest_relevant = self._is_relevant_file(event.dest_path)

        if not event.is_directory and (src_relevant or dest_relevant):
            file_event = self._create_file_event(
                event_type=FileSystemEventType.MOVED,
                src_path=event.src_path,
                dest_path=event.dest_path,
                is_directory=event.is_directory,
            )

            if file_event:
                logger.info(f"File moved: {event.src_path} -> {event.dest_path}")
                self._handle_event(file_event)
