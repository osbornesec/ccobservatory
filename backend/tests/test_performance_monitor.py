"""
Test suite for PerformanceMonitor following Canon TDD approach.
Tests written one at a time, with minimal implementation to pass each test.
"""

import pytest
from app.monitoring.performance_monitor import PerformanceMonitor
from app.models.contracts import PerformanceMetrics


class TestPerformanceMonitor:
    """Test PerformanceMonitor functionality following Canon TDD approach."""
    
    @pytest.fixture
    def performance_monitor(self):
        """Create a new PerformanceMonitor instance for each test."""
        return PerformanceMonitor()
    
    def test_record_and_retrieve_metrics_successfully(self, performance_monitor):
        """First test: PerformanceMonitor records and retrieves metrics successfully."""
        # Create a PerformanceMetrics instance with latency measurements
        metrics = PerformanceMetrics(
            detection_latency_ms=50.0,
            processing_latency_ms=100.0,
            throughput_msgs_per_sec=10.0
        )
        
        # Record the metrics
        performance_monitor.record_metrics(metrics)
        
        # Retrieve the summary statistics after recording one metric
        summary = performance_monitor.get_summary()
        
        # Check that the summary contains expected structure
        assert isinstance(summary, dict), "Summary should be a dictionary"
        assert "detection_latency" in summary, "Summary should contain detection_latency"
        assert "processing_latency" in summary, "Summary should contain processing_latency"
        assert "throughput" in summary, "Summary should contain throughput"
    
    def test_record_metrics_with_sla_violation_tracks_violation_count(self, performance_monitor):
        """Second test: PerformanceMonitor correctly tracks SLA violations when detection latency exceeds threshold."""
        # Record metrics with detection_latency_ms > threshold (default 100ms)
        # Use 150ms to clearly exceed the 100ms default threshold
        violation_metrics = PerformanceMetrics(
            detection_latency_ms=150.0,  # Exceeds default 100ms threshold
            processing_latency_ms=80.0,
            throughput_msgs_per_sec=8.0
        )
        
        performance_monitor.record_metrics(violation_metrics)
        
        # Verify that SLA violations are tracked in the summary
        summary = performance_monitor.get_summary()
        
        assert "detection_latency" in summary, "Summary should contain detection_latency section"
        assert "sla_violations" in summary["detection_latency"], "Detection latency summary should contain sla_violations count"
        assert summary["detection_latency"]["sla_violations"] == 1, f"Expected 1 SLA violation, but got {summary['detection_latency']['sla_violations']}"
    
    def test_get_alerts_returns_warning_for_high_violation_rate(self, performance_monitor):
        """Third test: PerformanceMonitor generates alerts for high SLA violation rates."""
        # Record multiple metrics with high violation rate (> 5% violation rate triggers alert)
        # Record 20 total metrics with 2 violations (10% violation rate) to trigger high violation rate alert
        
        # First, record 18 metrics within SLA (< 100ms)
        for i in range(18):
            within_sla_metrics = PerformanceMetrics(
                detection_latency_ms=50.0 + i,  # 50-67ms range
                processing_latency_ms=70.0,
                throughput_msgs_per_sec=12.0
            )
            performance_monitor.record_metrics(within_sla_metrics)
        
        # Then record 2 metrics that violate SLA (> 100ms default threshold)
        violation_metrics_1 = PerformanceMetrics(
            detection_latency_ms=150.0,  # Exceeds 100ms threshold
            processing_latency_ms=80.0,
            throughput_msgs_per_sec=8.0
        )
        violation_metrics_2 = PerformanceMetrics(
            detection_latency_ms=180.0,  # Exceeds 100ms threshold
            processing_latency_ms=90.0,
            throughput_msgs_per_sec=7.0
        )
        performance_monitor.record_metrics(violation_metrics_1)
        performance_monitor.record_metrics(violation_metrics_2)
        
        # Get alerts and verify structure and content
        alerts = performance_monitor.get_alerts()
        
        # Should have at least one alert for high violation rate
        assert len(alerts) > 0, "Expected at least one alert for high violation rate"
        
        # Check that one of the alerts is for SLA compliance
        sla_alerts = [alert for alert in alerts if alert.get("component") == "sla_compliance"]
        assert len(sla_alerts) > 0, "Expected at least one alert for sla_compliance component"
        
        # Verify alert structure
        first_alert = sla_alerts[0]
        assert "level" in first_alert, "Alert should have 'level' field"
        assert "component" in first_alert, "Alert should have 'component' field"
        assert "message" in first_alert, "Alert should have 'message' field"
        assert "timestamp" in first_alert, "Alert should have 'timestamp' field"
        
        # Verify alert content
        assert first_alert["level"] == "error", f"Expected alert level 'error', but got '{first_alert['level']}'"
        assert first_alert["component"] == "sla_compliance", f"Expected component 'sla_compliance', but got '{first_alert['component']}'"
        assert "violation rate" in first_alert["message"], f"Alert message should mention violation rate: {first_alert['message']}"
    
    def test_reset_stats_clears_all_statistics_and_samples(self, performance_monitor):
        """Fourth test: PerformanceMonitor reset_stats clears all statistics and samples."""
        import time
        from datetime import datetime
        
        # Store the initial reset time to verify it changes later
        initial_stats = performance_monitor.get_summary()
        initial_reset_time = datetime.fromisoformat(initial_stats["last_reset"]) if isinstance(initial_stats["last_reset"], str) else initial_stats["last_reset"]
        
        # Record several metrics to populate statistics
        metrics_1 = PerformanceMetrics(
            detection_latency_ms=75.0,
            processing_latency_ms=85.0,
            throughput_msgs_per_sec=15.0
        )
        metrics_2 = PerformanceMetrics(
            detection_latency_ms=120.0,  # SLA violation
            processing_latency_ms=95.0,
            throughput_msgs_per_sec=10.0
        )
        
        performance_monitor.record_metrics(metrics_1)
        performance_monitor.record_metrics(metrics_2)
        
        # Add a small delay to ensure the last_reset timestamp will be updated
        time.sleep(0.01)
        
        # Verify that statistics are populated (pre-condition check)
        pre_reset_stats = performance_monitor.get_summary()
        assert pre_reset_stats["samples"]["total"] > 0, "Pre-condition: Total samples should be populated"
        assert pre_reset_stats["detection_latency"]["sla_violations"] > 0, "Pre-condition: SLA violations should be populated"
        assert len(performance_monitor.detection_latencies) > 0, "Pre-condition: Detection latencies should be populated"
        assert len(performance_monitor.processing_latencies) > 0, "Pre-condition: Processing latencies should be populated"
        assert len(performance_monitor.throughput_samples) > 0, "Pre-condition: Throughput samples should be populated"
        
        # Call reset_stats()
        performance_monitor.reset_stats()
        
        # Verify that all statistics are cleared to zero
        post_reset_stats = performance_monitor.get_summary()
        assert post_reset_stats["status"] == "no_data", "Post-reset: Status should be 'no_data'"
        assert post_reset_stats["total_samples"] == 0, "Post-reset: Total samples should be zero"
        assert post_reset_stats["sla_violations"] == 0, "Post-reset: SLA violations should be zero"
        assert len(performance_monitor.detection_latencies) == 0, "Post-reset: Detection latencies deque should be empty"
        assert len(performance_monitor.processing_latencies) == 0, "Post-reset: Processing latencies deque should be empty"
        assert len(performance_monitor.throughput_samples) == 0, "Post-reset: Throughput samples deque should be empty"
        
        # Verify that last_reset timestamp is updated
        post_reset_time = datetime.fromisoformat(post_reset_stats["last_reset"]) if isinstance(post_reset_stats["last_reset"], str) else post_reset_stats["last_reset"]
        assert post_reset_time > initial_reset_time, "Post-reset: last_reset timestamp should be updated to a later time"