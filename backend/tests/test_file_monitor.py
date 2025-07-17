"""
Test suite for File Monitor following Canon TDD approach.
Tests written one at a time, with minimal implementation to pass each test.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4
from unittest.mock import MagicMock, patch
from app.monitoring.file_monitor import FileMonitor, FileMonitorError
from app.monitoring.database_writer import DatabaseWriter


class TestFileMonitor:
    """Test FileMonitor functionality following Canon TDD approach."""

    def setup_method(self):
        """Setup method to create test fixtures."""
        import tempfile
        self.temp_dir = tempfile.mkdtemp()
        self.watch_path = self.temp_dir
        
    def teardown_method(self):
        """Cleanup method to remove temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch.dict('os.environ', {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-key',
        'SUPABASE_SERVICE_ROLE_KEY': 'test-service-key'
    })
    def test_monitor_initial_state_is_not_running(self):
        """First test: Monitor is not running immediately after initialization."""
        with patch('app.monitoring.file_monitor.DatabaseWriter') as mock_db_writer_class:
            with patch('app.monitoring.file_monitor.JSONLParser') as mock_parser_class:
                with patch('app.monitoring.file_monitor.PerformanceMonitor') as mock_perf_class:
                    with patch('app.monitoring.file_monitor.ClaudeFileHandler') as mock_handler_class:
                        monitor = FileMonitor(self.watch_path)
                        assert monitor._running is False, "Monitor should not be running initially."

    @patch.dict('os.environ', {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-key',
        'SUPABASE_SERVICE_ROLE_KEY': 'test-service-key'
    })
    def test_monitor_can_be_started_and_stopped_and_updates_running_state(self):
        """Second test: Monitor can be started and stopped, updating _running state."""
        with patch('app.monitoring.file_monitor.DatabaseWriter') as mock_db_writer_class:
            with patch('app.monitoring.file_monitor.JSONLParser') as mock_parser_class:
                with patch('app.monitoring.file_monitor.PerformanceMonitor') as mock_perf_class:
                    with patch('app.monitoring.file_monitor.ClaudeFileHandler') as mock_handler_class:
                        with patch('app.monitoring.file_monitor.Observer') as mock_observer_class:
                            monitor = FileMonitor(self.watch_path)

                            # Assert initial state (should be False)
                            assert monitor._running is False, "Monitor should not be running before start()."

                            # Call start() and assert state changes to True
                            monitor.start()
                            assert monitor._running is True, "Monitor should be running after start()."

                            # Call stop() and assert state changes back to False
                            monitor.stop()
                            assert monitor._running is False, "Monitor should not be running after stop()."

    @patch.dict('os.environ', {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-key',
        'SUPABASE_SERVICE_ROLE_KEY': 'test-service-key'
    })
    def test_monitor_start_already_running_logs_warning(self):
        """Third test: Starting monitor when already running logs warning."""
        with patch('app.monitoring.file_monitor.DatabaseWriter'):
            with patch('app.monitoring.file_monitor.JSONLParser'):
                with patch('app.monitoring.file_monitor.PerformanceMonitor'):
                    with patch('app.monitoring.file_monitor.ClaudeFileHandler'):
                        with patch('app.monitoring.file_monitor.Observer'):
                            with patch('app.monitoring.file_monitor.logger') as mock_logger:
                                monitor = FileMonitor(self.watch_path)
                                
                                # Start monitor first time
                                monitor.start()
                                assert monitor._running is True
                                
                                # Try to start again - should log warning
                                monitor.start()
                                mock_logger.warning.assert_called_with("FileMonitor is already running")

    @patch.dict('os.environ', {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-key',
        'SUPABASE_SERVICE_ROLE_KEY': 'test-service-key'
    })
    def test_monitor_stop_not_running_logs_warning(self):
        """Fourth test: Stopping monitor when not running logs warning."""
        with patch('app.monitoring.file_monitor.DatabaseWriter'):
            with patch('app.monitoring.file_monitor.JSONLParser'):
                with patch('app.monitoring.file_monitor.PerformanceMonitor'):
                    with patch('app.monitoring.file_monitor.ClaudeFileHandler'):
                        with patch('app.monitoring.file_monitor.logger') as mock_logger:
                            monitor = FileMonitor(self.watch_path)
                            
                            # Try to stop when not running - should log warning
                            monitor.stop()
                            mock_logger.warning.assert_called_with("FileMonitor is not running")

    @patch.dict('os.environ', {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-key',
        'SUPABASE_SERVICE_ROLE_KEY': 'test-service-key'
    })
    def test_monitor_start_creates_missing_watch_directory(self):
        """Fifth test: Monitor creates watch directory if it doesn't exist."""
        with patch('app.monitoring.file_monitor.DatabaseWriter'):
            with patch('app.monitoring.file_monitor.JSONLParser'):
                with patch('app.monitoring.file_monitor.PerformanceMonitor'):
                    with patch('app.monitoring.file_monitor.ClaudeFileHandler'):
                        with patch('app.monitoring.file_monitor.Observer'):
                            with patch('app.monitoring.file_monitor.logger') as mock_logger:
                                # Create monitor with non-existent path
                                non_existent_path = "/tmp/non_existent_dir"
                                monitor = FileMonitor(non_existent_path)
                                
                                # Mock the pathlib.Path.exists() to return False
                                with patch('pathlib.Path.exists', return_value=False):
                                    with patch('pathlib.Path.mkdir') as mock_mkdir:
                                        monitor.start()
                                        
                                        # Verify directory creation was attempted
                                        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
                                        
                                        # Check that both log messages are called
                                        mock_logger.info.assert_any_call(f"Created watch directory: {monitor.watch_path}")
                                        mock_logger.info.assert_any_call(f"FileMonitor started, monitoring {monitor.watch_path} recursively")
    
    def test_handle_file_event_processes_file_successfully(self):
        """Seventh test: _handle_file_event processes file event successfully."""
        with patch.dict('os.environ', {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_KEY': 'test-key',
            'SUPABASE_SERVICE_ROLE_KEY': 'test-service-key'
        }):
            with patch('app.monitoring.file_monitor.PerformanceMonitor') as mock_perf:
                with patch('app.monitoring.file_monitor.DatabaseWriter') as mock_db_writer:
                    with patch('app.monitoring.file_monitor.JSONLParser') as mock_parser:
                        with patch('app.monitoring.file_monitor.ClaudeFileHandler'):
                            # Create monitor
                            monitor = FileMonitor("/tmp/test_dir")
                            
                            # Mock parser to return successful conversation data
                            from app.models.contracts import ConversationData
                            conversation_data = ConversationData(
                                project_id=uuid4(),
                                file_path="/test/file_monitor/conversation.jsonl",
                                session_id="test-session",
                                title="Test Conversation",
                                message_count=1,
                                messages=[]
                            )
                            monitor.jsonl_parser.parse_conversation_file.return_value = conversation_data
                            
                            # Mock database writer to return success
                            conversation_id = uuid4()
                            monitor.database_writer.write_conversation.return_value = (True, conversation_id, {"total_write_ms": 100.0})
                            
                            # Create file event
                            from app.models.contracts import FileEvent, FileSystemEventType
                            from pathlib import Path
                            file_event = FileEvent(
                                event_type=FileSystemEventType.CREATED,
                                src_path=Path("/tmp/test_dir/test.jsonl"),
                                is_directory=False,
                                detected_at=datetime.now(timezone.utc)
                            )
                            
                            # Call the method under test
                            monitor._handle_file_event(file_event)
                            
                            # Verify parser was called
                            monitor.jsonl_parser.parse_conversation_file.assert_called_once_with("/tmp/test_dir/test.jsonl")
                            
                            # Verify database writer was called
                            monitor.database_writer.write_conversation.assert_called_once_with(conversation_data)
                            
                            # Verify performance monitor was called
                            monitor.performance_monitor.record_metrics.assert_called_once()
                            
                            # Verify statistics were updated
                            assert monitor.stats["files_processed"] == 1
                            assert monitor.stats["conversations_created"] == 1

    @patch.dict('os.environ', {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-key',
        'SUPABASE_SERVICE_ROLE_KEY': 'test-service-key'
    })
    def test_handle_file_event_skips_non_jsonl_files(self):
        """Eighth test: _handle_file_event skips files that are not JSONL."""
        with patch('app.monitoring.file_monitor.PerformanceMonitor'):
            with patch('app.monitoring.file_monitor.DatabaseWriter'):
                with patch('app.monitoring.file_monitor.JSONLParser'):
                    with patch('app.monitoring.file_monitor.ClaudeFileHandler'):
                        # Create monitor
                        monitor = FileMonitor("/tmp/test_dir")
                        
                        # Create file event for non-JSONL file
                        from app.models.contracts import FileEvent, FileSystemEventType
                        from pathlib import Path
                        file_event = FileEvent(
                            event_type=FileSystemEventType.CREATED,
                            src_path=Path("/tmp/test_dir/test.txt"),
                            is_directory=False,
                            detected_at=datetime.now(timezone.utc)
                        )
                        
                        # Call the method under test
                        monitor._handle_file_event(file_event)
                        
                        # Verify parser was not called
                        monitor.jsonl_parser.parse_conversation_file.assert_not_called()
                        
                        # Verify database writer was not called
                        monitor.database_writer.write_conversation.assert_not_called()
                        
                        # Verify statistics were not updated
                        assert monitor.stats["files_processed"] == 0
                        assert monitor.stats["conversations_created"] == 0

    @patch.dict('os.environ', {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-key',
        'SUPABASE_SERVICE_ROLE_KEY': 'test-service-key'
    })
    def test_handle_file_event_skips_deleted_events(self):
        """Ninth test: _handle_file_event skips deleted events."""
        with patch('app.monitoring.file_monitor.PerformanceMonitor'):
            with patch('app.monitoring.file_monitor.DatabaseWriter'):
                with patch('app.monitoring.file_monitor.JSONLParser'):
                    with patch('app.monitoring.file_monitor.ClaudeFileHandler'):
                        # Create monitor
                        monitor = FileMonitor("/tmp/test_dir")
                        
                        # Create file event for deleted event
                        from app.models.contracts import FileEvent, FileSystemEventType
                        from pathlib import Path
                        file_event = FileEvent(
                            event_type=FileSystemEventType.DELETED,
                            src_path=Path("/tmp/test_dir/test.jsonl"),
                            is_directory=False,
                            detected_at=datetime.now(timezone.utc)
                        )
                        
                        # Call the method under test
                        monitor._handle_file_event(file_event)
                        
                        # Verify parser was not called
                        monitor.jsonl_parser.parse_conversation_file.assert_not_called()
                        
                        # Verify database writer was not called
                        monitor.database_writer.write_conversation.assert_not_called()
                        
                        # Verify statistics were not updated
                        assert monitor.stats["files_processed"] == 0
                        assert monitor.stats["conversations_created"] == 0

    @patch.dict('os.environ', {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-key',
        'SUPABASE_SERVICE_ROLE_KEY': 'test-service-key'
    })
    def test_handle_file_event_handles_parsing_error(self):
        """Tenth test: _handle_file_event handles parsing errors gracefully."""
        with patch('app.monitoring.file_monitor.PerformanceMonitor'):
            with patch('app.monitoring.file_monitor.DatabaseWriter'):
                with patch('app.monitoring.file_monitor.JSONLParser'):
                    with patch('app.monitoring.file_monitor.ClaudeFileHandler'):
                        # Create monitor
                        monitor = FileMonitor("/tmp/test_dir")
                        
                        # Mock parser to return ProcessingError
                        from app.models.contracts import ProcessingError
                        parsing_error = ProcessingError(
                            error_type="ParsingError",
                            error_message="Failed to parse JSONL file",
                            component="JSONLParser"
                        )
                        monitor.jsonl_parser.parse_conversation_file.return_value = parsing_error
                        
                        # Create file event
                        from app.models.contracts import FileEvent, FileSystemEventType
                        from pathlib import Path
                        file_event = FileEvent(
                            event_type=FileSystemEventType.CREATED,
                            src_path=Path("/tmp/test_dir/test.jsonl"),
                            is_directory=False,
                            detected_at=datetime.now(timezone.utc)
                        )
                        
                        # Call the method under test
                        monitor._handle_file_event(file_event)
                        
                        # Verify parser was called
                        monitor.jsonl_parser.parse_conversation_file.assert_called_once_with("/tmp/test_dir/test.jsonl")
                        
                        # Verify database writer was not called
                        monitor.database_writer.write_conversation.assert_not_called()
                        
                        # Verify error statistics were updated
                        assert monitor.stats["processing_errors"] == 1
                        assert monitor.stats["files_processed"] == 0
                        assert monitor.stats["conversations_created"] == 0

    @patch.dict('os.environ', {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-key',
        'SUPABASE_SERVICE_ROLE_KEY': 'test-service-key'
    })
    def test_handle_file_event_handles_database_write_failure(self):
        """Eleventh test: _handle_file_event handles database write failures."""
        with patch('app.monitoring.file_monitor.PerformanceMonitor'):
            with patch('app.monitoring.file_monitor.DatabaseWriter'):
                with patch('app.monitoring.file_monitor.JSONLParser'):
                    with patch('app.monitoring.file_monitor.ClaudeFileHandler'):
                        # Create monitor
                        monitor = FileMonitor("/tmp/test_dir")
                        
                        # Mock parser to return successful conversation data
                        from app.models.contracts import ConversationData
                        conversation_data = ConversationData(
                            project_id=uuid4(),
                            file_path="/test/file_monitor/failure_conversation.jsonl",
                            session_id="test-session",
                            title="Test Conversation",
                            message_count=1,
                            messages=[]
                        )
                        monitor.jsonl_parser.parse_conversation_file.return_value = conversation_data
                        
                        # Mock database writer to return failure
                        monitor.database_writer.write_conversation.return_value = (False, None, {})
                        
                        # Create file event
                        from app.models.contracts import FileEvent, FileSystemEventType
                        from pathlib import Path
                        file_event = FileEvent(
                            event_type=FileSystemEventType.CREATED,
                            src_path=Path("/tmp/test_dir/test.jsonl"),
                            is_directory=False,
                            detected_at=datetime.now(timezone.utc)
                        )
                        
                        # Call the method under test
                        monitor._handle_file_event(file_event)
                        
                        # Verify parser was called
                        monitor.jsonl_parser.parse_conversation_file.assert_called_once_with("/tmp/test_dir/test.jsonl")
                        
                        # Verify database writer was called
                        monitor.database_writer.write_conversation.assert_called_once_with(conversation_data)
                        
                        # Verify error statistics were updated
                        assert monitor.stats["processing_errors"] == 1
                        assert monitor.stats["files_processed"] == 0
                        assert monitor.stats["conversations_created"] == 0

    @patch.dict('os.environ', {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-key',
        'SUPABASE_SERVICE_ROLE_KEY': 'test-service-key'
    })
    def test_monitor_start_handles_observer_startup_error(self):
        """Sixth test: Monitor handles observer startup errors gracefully."""
        with patch('app.monitoring.file_monitor.DatabaseWriter'):
            with patch('app.monitoring.file_monitor.JSONLParser'):
                with patch('app.monitoring.file_monitor.PerformanceMonitor'):
                    with patch('app.monitoring.file_monitor.ClaudeFileHandler'):
                        with patch('app.monitoring.file_monitor.Observer') as mock_observer_class:
                            # Mock observer to raise exception during start
                            mock_observer = mock_observer_class.return_value
                            mock_observer.start.side_effect = Exception("Observer startup failed")
                            
                            monitor = FileMonitor(self.watch_path)
                            
                            # Starting should raise FileMonitorError
                            with pytest.raises(FileMonitorError) as exc_info:
                                monitor.start()
                            
                            assert exc_info.value.error_type == "StartupError"
                            assert "Observer startup failed" in str(exc_info.value)

    @patch.dict('os.environ', {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-key',
        'SUPABASE_SERVICE_ROLE_KEY': 'test-service-key'
    })
    def test_get_health_returns_system_health_with_components(self):
        """Twelfth test: get_health returns SystemHealth with component statuses."""
        with patch('app.monitoring.file_monitor.PerformanceMonitor'):
            with patch('app.monitoring.file_monitor.DatabaseWriter'):
                with patch('app.monitoring.file_monitor.JSONLParser'):
                    with patch('app.monitoring.file_monitor.ClaudeFileHandler'):
                        # Create monitor
                        monitor = FileMonitor("/tmp/test_dir")
                        
                        # Mock path exists to return True
                        with patch('pathlib.Path.exists', return_value=True):
                            with patch('os.access', return_value=True):
                                # Call the method under test
                                health = monitor.get_health()
                                
                                # Verify health object structure
                                from app.models.contracts import SystemHealth, ComponentStatus
                                assert isinstance(health, SystemHealth)
                                assert health.service_status in ["ok", "degraded", "unavailable"]
                                assert isinstance(health.components, list)
                                assert len(health.components) == 3  # filesystem, observer, database
                                
                                # Verify component names
                                component_names = [comp.component_name for comp in health.components]
                                assert "filesystem" in component_names
                                assert "observer" in component_names
                                assert "database" in component_names

    @patch.dict('os.environ', {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-key',
        'SUPABASE_SERVICE_ROLE_KEY': 'test-service-key'
    })
    def test_get_stats_returns_comprehensive_statistics(self):
        """Thirteenth test: get_stats returns comprehensive monitoring statistics."""
        with patch('app.monitoring.file_monitor.PerformanceMonitor'):
            with patch('app.monitoring.file_monitor.DatabaseWriter'):
                with patch('app.monitoring.file_monitor.JSONLParser'):
                    with patch('app.monitoring.file_monitor.ClaudeFileHandler'):
                        # Create monitor
                        monitor = FileMonitor("/tmp/test_dir")
                        
                        # Mock component stats
                        monitor.jsonl_parser.get_stats.return_value = {"files_parsed": 5}
                        monitor.database_writer.get_stats.return_value = {"conversations_written": 3}
                        monitor.performance_monitor.get_summary.return_value = {"avg_latency": 50.0}
                        
                        # Call the method under test
                        stats = monitor.get_stats()
                        
                        # Verify stats structure
                        assert isinstance(stats, dict)
                        assert "files_processed" in stats
                        assert "conversations_created" in stats
                        assert "processing_errors" in stats
                        assert "uptime_seconds" in stats
                        assert "parser_stats" in stats
                        assert "database_stats" in stats
                        assert "performance_stats" in stats
                        assert "is_running" in stats
                        assert "watch_path" in stats
                        
                        # Verify component stats are included
                        assert stats["parser_stats"] == {"files_parsed": 5}
                        assert stats["database_stats"] == {"conversations_written": 3}
                        assert stats["performance_stats"] == {"avg_latency": 50.0}
                        assert stats["is_running"] == monitor._running

    @patch.dict('os.environ', {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-key',
        'SUPABASE_SERVICE_ROLE_KEY': 'test-service-key'
    })
    def test_reset_stats_clears_all_statistics(self):
        """Fourteenth test: reset_stats clears all monitoring statistics."""
        with patch('app.monitoring.file_monitor.PerformanceMonitor'):
            with patch('app.monitoring.file_monitor.DatabaseWriter'):
                with patch('app.monitoring.file_monitor.JSONLParser'):
                    with patch('app.monitoring.file_monitor.ClaudeFileHandler'):
                        # Create monitor
                        monitor = FileMonitor("/tmp/test_dir")
                        
                        # Set some stats
                        monitor.stats["files_processed"] = 5
                        monitor.stats["conversations_created"] = 3
                        monitor.stats["processing_errors"] = 2
                        
                        # Call the method under test
                        monitor.reset_stats()
                        
                        # Verify stats are reset
                        assert monitor.stats["files_processed"] == 0
                        assert monitor.stats["conversations_created"] == 0
                        assert monitor.stats["processing_errors"] == 0
                        assert monitor.stats["uptime_seconds"] == 0
                        
                        # Verify component reset methods were called
                        monitor.jsonl_parser.reset_stats.assert_called_once()
                        monitor.database_writer.reset_stats.assert_called_once()
                        monitor.performance_monitor.reset_stats.assert_called_once()

    @patch.dict('os.environ', {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-key',
        'SUPABASE_SERVICE_ROLE_KEY': 'test-service-key'
    })
    def test_is_running_property_returns_current_state(self):
        """Fifteenth test: is_running property returns current running state."""
        with patch('app.monitoring.file_monitor.PerformanceMonitor'):
            with patch('app.monitoring.file_monitor.DatabaseWriter'):
                with patch('app.monitoring.file_monitor.JSONLParser'):
                    with patch('app.monitoring.file_monitor.ClaudeFileHandler'):
                        # Create monitor
                        monitor = FileMonitor("/tmp/test_dir")
                        
                        # Initially should be False
                        assert monitor.is_running is False
                        
                        # Set running state
                        monitor._running = True
                        assert monitor.is_running is True
                        
                        # Set back to False
                        monitor._running = False
                        assert monitor.is_running is False

    @patch.dict('os.environ', {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-key',
        'SUPABASE_SERVICE_ROLE_KEY': 'test-service-key'
    })
    def test_context_manager_starts_and_stops_monitor(self):
        """Sixteenth test: Context manager starts and stops monitor properly."""
        with patch('app.monitoring.file_monitor.PerformanceMonitor'):
            with patch('app.monitoring.file_monitor.DatabaseWriter'):
                with patch('app.monitoring.file_monitor.JSONLParser'):
                    with patch('app.monitoring.file_monitor.ClaudeFileHandler'):
                        with patch('app.monitoring.file_monitor.Observer'):
                            # Create monitor
                            monitor = FileMonitor("/tmp/test_dir")
                            
                            # Use context manager
                            with monitor as context_monitor:
                                # Verify it's the same instance
                                assert context_monitor is monitor
                                # Verify it's running
                                assert monitor._running is True
                            
                            # Verify it's stopped after context exit
                            assert monitor._running is False