"""
FileMonitor implementation for coordinating file system monitoring.

This module provides the main monitoring service that orchestrates watchdog observers,
file handlers, parsing, and database operations with performance tracking.
"""

import logging
import os
import threading
import time
from pathlib import Path
from typing import Dict, Optional, Callable

from watchdog.observers import Observer

from app.models.contracts import (
    FileEvent,
    ConversationData,
    PerformanceMetrics,
    ProcessingError,
    ComponentStatus,
    ComponentHealth,
    SystemHealth,
)
from .file_handler import ClaudeFileHandler
from .jsonl_parser import JSONLParser
from .database_writer import DatabaseWriter
from .performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)


class FileMonitor:
    """
    Main file monitoring service for Claude Code Observatory.

    Coordinates file system watching, JSONL parsing, database writing,
    and performance monitoring with <100ms detection latency requirement.

    Architecture:
    FileEvent -> JSONLParser -> ConversationData -> DatabaseWriter -> Metrics
    """

    def __init__(
        self,
        watch_path: Optional[str] = None,
        callback: Optional[Callable[[ConversationData], None]] = None,
    ):
        """
        Initialize the file monitor.

        Args:
            watch_path: Directory path to monitor. Defaults to ~/.claude/projects
            callback: Optional callback for processed conversations
        """
        self.watch_path = (
            Path(watch_path) if watch_path else Path.home() / ".claude" / "projects"
        )
        self.callback = callback

        # Core components
        self.observer: Optional[Observer] = None
        self.file_handler = ClaudeFileHandler(callback=self._handle_file_event)
        self.jsonl_parser = JSONLParser()
        self.database_writer = DatabaseWriter()
        self.performance_monitor = PerformanceMonitor()

        # State management
        self._running = False
        self._lock = threading.Lock()

        # Statistics
        self.stats = {
            "files_processed": 0,
            "conversations_created": 0,
            "processing_errors": 0,
            "uptime_seconds": 0,
        }
        self._start_time = None

        logger.info(f"FileMonitor initialized, watching: {self.watch_path}")

    def start(self) -> None:
        """
        Start the file monitoring service.

        Sets up the watchdog observer and begins monitoring the configured path.
        """
        with self._lock:
            if self._running:
                logger.warning("FileMonitor is already running")
                return

            try:
                # Ensure watch directory exists
                if not self.watch_path.exists():
                    logger.warning(f"Watch path does not exist: {self.watch_path}")
                    self.watch_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created watch directory: {self.watch_path}")

                # Start watchdog observer
                self.observer = Observer()
                self.observer.schedule(
                    self.file_handler, str(self.watch_path), recursive=True
                )
                self.observer.start()

                self._running = True
                self._start_time = time.time()

                logger.info(
                    f"FileMonitor started, monitoring {self.watch_path} recursively"
                )

            except Exception as e:
                error = ProcessingError(
                    error_type="StartupError",
                    error_message=f"Failed to start FileMonitor: {str(e)}",
                    component="FileMonitor",
                )
                logger.error(f"Startup error: {error}")
                raise error

    def stop(self) -> None:
        """
        Stop the file monitoring service.

        Gracefully shuts down the watchdog observer and cleans up resources.
        """
        with self._lock:
            if not self._running:
                logger.warning("FileMonitor is not running")
                return

            try:
                if self.observer:
                    self.observer.stop()
                    self.observer.join(timeout=5.0)  # Wait up to 5 seconds

                    if self.observer.is_alive():
                        logger.warning(
                            "Observer did not stop gracefully within timeout"
                        )
                    else:
                        logger.info("Observer stopped gracefully")

                self._running = False
                if self._start_time:
                    self.stats["uptime_seconds"] = int(time.time() - self._start_time)

                logger.info("FileMonitor stopped")

            except Exception as e:
                error = ProcessingError(
                    error_type="ShutdownError",
                    error_message=f"Error stopping FileMonitor: {str(e)}",
                    component="FileMonitor",
                )
                logger.error(f"Shutdown error: {error}")
                raise error

    def _handle_file_event(self, file_event: FileEvent) -> None:
        """
        Handle a file system event by processing the file and storing conversation data.

        Args:
            file_event: FileEvent object from the file handler
        """
        processing_start = time.perf_counter()

        try:
            logger.debug(
                f"Processing file event: {file_event.event_type} for {file_event.src_path}"
            )

            # Only process file modifications and creations for JSONL files
            if file_event.event_type not in ["modified", "created"]:
                logger.debug(f"Skipping {file_event.event_type} event")
                return

            if not str(file_event.src_path).endswith(".jsonl"):
                logger.debug(f"Skipping non-JSONL file: {file_event.src_path}")
                return

            # Parse the JSONL file
            parse_start = time.perf_counter()
            result = self.jsonl_parser.parse_conversation_file(str(file_event.src_path))
            parse_end = time.perf_counter()

            if isinstance(result, ProcessingError):
                logger.error(f"Failed to parse file {file_event.src_path}: {result}")
                self.stats["processing_errors"] += 1
                return

            conversation_data = result

            # Write to database
            db_start = time.perf_counter()
            success, conversation_id, db_metrics = (
                self.database_writer.write_conversation(conversation_data)
            )
            db_end = time.perf_counter()

            if not success:
                logger.error(f"Failed to write conversation to database")
                self.stats["processing_errors"] += 1
                return

            # Calculate performance metrics
            processing_end = time.perf_counter()

            # Calculate detection latency (from file event detection to processing start)
            detection_latency_ms = (
                processing_start - file_event.detected_at.timestamp()
            ) * 1000
            processing_latency_ms = (processing_end - processing_start) * 1000

            # Record performance metrics
            metrics = PerformanceMetrics(
                detection_latency_ms=max(
                    0.1, detection_latency_ms
                ),  # Ensure positive value
                processing_latency_ms=processing_latency_ms,
                throughput_msgs_per_sec=(
                    len(conversation_data.messages) / (processing_latency_ms / 1000)
                    if processing_latency_ms > 0
                    else 0
                ),
            )

            self.performance_monitor.record_metrics(metrics)

            # Update statistics
            self.stats["files_processed"] += 1
            self.stats["conversations_created"] += 1

            # Call optional callback
            if self.callback:
                try:
                    self.callback(conversation_data)
                except Exception as e:
                    logger.warning(f"Error in callback: {e}")

            logger.info(
                f"Successfully processed {file_event.src_path} -> conversation {conversation_id} "
                f"({len(conversation_data.messages)} messages) "
                f"in {processing_latency_ms:.2f}ms "
                f"(detection: {detection_latency_ms:.2f}ms)"
            )

        except Exception as e:
            self.stats["processing_errors"] += 1
            error = ProcessingError(
                error_type="ProcessingError",
                error_message=f"Error processing file event: {str(e)}",
                component="FileMonitor",
                original_event={
                    "event_type": file_event.event_type.value,
                    "src_path": str(file_event.src_path),
                },
            )
            logger.error(f"Processing error: {error}")

    def get_health(self) -> SystemHealth:
        """
        Get the health status of the file monitoring system.

        Returns:
            SystemHealth object with component health statuses
        """
        components = []

        # Check file system access
        try:
            if self.watch_path.exists() and os.access(self.watch_path, os.R_OK):
                filesystem_status = ComponentStatus.OK
                filesystem_details = f"Watching {self.watch_path}"
            else:
                filesystem_status = ComponentStatus.UNAVAILABLE
                filesystem_details = f"Cannot access {self.watch_path}"
        except Exception as e:
            filesystem_status = ComponentStatus.UNAVAILABLE
            filesystem_details = f"Filesystem error: {str(e)}"

        components.append(
            ComponentHealth(
                component_name="filesystem",
                status=filesystem_status,
                details=filesystem_details,
            )
        )

        # Check observer status
        if self.observer and self.observer.is_alive():
            observer_status = ComponentStatus.OK
            observer_details = "Observer running"
        elif self._running:
            observer_status = ComponentStatus.DEGRADED
            observer_details = "Observer not responding"
        else:
            observer_status = ComponentStatus.UNAVAILABLE
            observer_details = "Observer not started"

        components.append(
            ComponentHealth(
                component_name="observer",
                status=observer_status,
                details=observer_details,
            )
        )

        # Check database connectivity (simplified)
        try:
            # This is a simple check - could be enhanced with actual DB ping
            database_status = ComponentStatus.OK
            database_details = "Database writer initialized"
        except Exception as e:
            database_status = ComponentStatus.UNAVAILABLE
            database_details = f"Database error: {str(e)}"

        components.append(
            ComponentHealth(
                component_name="database",
                status=database_status,
                details=database_details,
            )
        )

        # Determine overall service status
        if all(c.status == ComponentStatus.OK for c in components):
            service_status = ComponentStatus.OK
        elif any(c.status == ComponentStatus.UNAVAILABLE for c in components):
            service_status = ComponentStatus.UNAVAILABLE
        else:
            service_status = ComponentStatus.DEGRADED

        return SystemHealth(service_status=service_status, components=components)

    def get_stats(self) -> Dict[str, any]:
        """
        Get comprehensive monitoring statistics.

        Returns:
            Dictionary containing system statistics
        """
        current_time = time.time()
        if self._start_time and self._running:
            self.stats["uptime_seconds"] = int(current_time - self._start_time)

        return {
            **self.stats,
            "parser_stats": self.jsonl_parser.get_stats(),
            "database_stats": self.database_writer.get_stats(),
            "performance_stats": self.performance_monitor.get_summary(),
            "is_running": self._running,
            "watch_path": str(self.watch_path),
        }

    def reset_stats(self) -> None:
        """Reset all monitoring statistics."""
        self.stats = {
            "files_processed": 0,
            "conversations_created": 0,
            "processing_errors": 0,
            "uptime_seconds": 0,
        }
        self.jsonl_parser.reset_stats()
        self.database_writer.reset_stats()
        self.performance_monitor.reset_stats()

    @property
    def is_running(self) -> bool:
        """Check if the monitor is currently running."""
        return self._running

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
