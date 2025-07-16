"""
Performance benchmark tests for file monitoring system.

Validates the <100ms detection latency SLA and other performance requirements
under various load conditions and scenarios.
"""

import asyncio
import json
import tempfile
import time
import statistics
from pathlib import Path
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
import pytest

from app.monitoring.file_monitor import FileMonitor
from app.monitoring.performance_monitor import PerformanceMonitor
from app.models.contracts import PerformanceMetrics, ComponentStatus


class TestPerformanceBenchmarks:
    """Performance benchmark tests for file monitoring system."""

    @pytest.fixture
    def temp_claude_dir(self):
        """Create a temporary Claude projects directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            claude_dir = Path(temp_dir) / ".claude" / "projects"
            claude_dir.mkdir(parents=True)
            yield claude_dir

    @pytest.fixture
    def sample_message_content(self):
        """Generate sample message content for performance tests."""
        return {
            "uuid": str(uuid4()),
            "sessionId": "perf-test-session",
            "timestamp": "2024-01-15T10:30:00.000Z",
            "type": "message",
            "message": {
                "role": "user",
                "content": "This is a performance test message with reasonable length content.",
            },
        }

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_single_file_detection_latency(
        self, temp_claude_dir, sample_message_content
    ):
        """Test detection latency for single file events."""
        latencies = []

        def timing_callback(conversation_data):
            # Callback is called after processing, latency measured in monitor
            pass

        monitor = FileMonitor(watch_path=str(temp_claude_dir), callback=timing_callback)

        try:
            monitor.start()
            await asyncio.sleep(0.1)  # Ensure monitor is fully started

            # Perform multiple single file tests
            for i in range(20):
                test_file = temp_claude_dir / f"single-test-{i}.jsonl"

                # Create file and measure processing
                test_file.write_text(json.dumps(sample_message_content))

                # Wait for processing
                await asyncio.sleep(0.2)

                # Collect latency data
                if monitor.performance_monitor.detection_latencies:
                    latest_latency = list(
                        monitor.performance_monitor.detection_latencies
                    )[-1]
                    latencies.append(latest_latency)

            # Analyze latency results
            if latencies:
                avg_latency = statistics.mean(latencies)
                max_latency = max(latencies)
                p95_latency = statistics.quantiles(latencies, n=20)[
                    18
                ]  # 95th percentile
                p99_latency = statistics.quantiles(latencies, n=100)[
                    98
                ]  # 99th percentile

                # Performance assertions
                assert (
                    avg_latency < 50.0
                ), f"Average latency {avg_latency:.2f}ms exceeds 50ms target"
                assert (
                    p95_latency < 100.0
                ), f"95th percentile {p95_latency:.2f}ms exceeds 100ms SLA"
                assert (
                    p99_latency < 200.0
                ), f"99th percentile {p99_latency:.2f}ms exceeds 200ms limit"

                print(f"Single File Latency Results ({len(latencies)} samples):")
                print(f"  Average: {avg_latency:.2f}ms")
                print(f"  Max: {max_latency:.2f}ms")
                print(f"  95th percentile: {p95_latency:.2f}ms")
                print(f"  99th percentile: {p99_latency:.2f}ms")

        finally:
            monitor.stop()

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_file_processing(
        self, temp_claude_dir, sample_message_content
    ):
        """Test performance under concurrent file creation load."""
        processed_count = 0
        processing_times = []

        def concurrent_callback(conversation_data):
            nonlocal processed_count
            processed_count += 1

        monitor = FileMonitor(
            watch_path=str(temp_claude_dir), callback=concurrent_callback
        )

        try:
            monitor.start()
            await asyncio.sleep(0.1)

            # Create multiple files concurrently
            start_time = time.perf_counter()

            tasks = []
            for i in range(50):  # 50 concurrent files
                task = asyncio.create_task(
                    self._create_test_file(
                        temp_claude_dir / f"concurrent-{i}.jsonl",
                        sample_message_content,
                    )
                )
                tasks.append(task)

            await asyncio.gather(*tasks)

            # Wait for all processing to complete
            max_wait_time = 10.0  # 10 seconds max wait
            wait_start = time.perf_counter()

            while (
                processed_count < 50
                and (time.perf_counter() - wait_start) < max_wait_time
            ):
                await asyncio.sleep(0.1)

            total_time = time.perf_counter() - start_time

            # Analyze concurrent processing results
            stats = monitor.get_stats()
            perf_summary = monitor.performance_monitor.get_summary()

            # Performance assertions
            throughput = processed_count / total_time
            assert (
                throughput >= 5.0
            ), f"Throughput {throughput:.1f} files/sec below 5 files/sec minimum"
            assert (
                processed_count >= 45
            ), f"Only {processed_count}/50 files processed within time limit"

            # Check that detection latency doesn't degrade significantly under load
            if perf_summary["status"] != "no_data":
                avg_latency = perf_summary["detection_latency"]["mean"]
                assert (
                    avg_latency < 150.0
                ), f"Average latency {avg_latency:.2f}ms degrades too much under load"

            print(f"Concurrent Processing Results:")
            print(f"  Files processed: {processed_count}/50")
            print(f"  Total time: {total_time:.2f}s")
            print(f"  Throughput: {throughput:.1f} files/sec")
            print(f"  Processing errors: {stats['processing_errors']}")

        finally:
            monitor.stop()

    async def _create_test_file(self, file_path: Path, content: dict):
        """Helper to create a test file asynchronously."""
        file_path.write_text(json.dumps(content))
        await asyncio.sleep(0.01)  # Small delay to simulate realistic file creation

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_large_message_processing_performance(self, temp_claude_dir):
        """Test performance with large message content."""
        # Create large message content
        large_content = {
            "uuid": str(uuid4()),
            "sessionId": "large-content-session",
            "timestamp": "2024-01-15T10:30:00.000Z",
            "type": "message",
            "message": {"role": "assistant", "content": "A" * 10000},  # 10KB of content
        }

        processing_times = []

        def timing_callback(conversation_data):
            # Processing time is captured in performance metrics
            pass

        monitor = FileMonitor(watch_path=str(temp_claude_dir), callback=timing_callback)

        try:
            monitor.start()
            await asyncio.sleep(0.1)

            # Test multiple large messages
            for i in range(10):
                test_file = temp_claude_dir / f"large-content-{i}.jsonl"

                start_time = time.perf_counter()
                test_file.write_text(json.dumps(large_content))

                # Wait for processing
                await asyncio.sleep(0.3)

                # Record processing time from performance monitor
                if monitor.performance_monitor.processing_latencies:
                    latest_processing_time = list(
                        monitor.performance_monitor.processing_latencies
                    )[-1]
                    processing_times.append(latest_processing_time)

            # Analyze large content processing
            if processing_times:
                avg_processing_time = statistics.mean(processing_times)
                max_processing_time = max(processing_times)

                # Large content should still process within reasonable time
                assert (
                    avg_processing_time < 500.0
                ), f"Large content avg processing {avg_processing_time:.2f}ms too slow"
                assert (
                    max_processing_time < 1000.0
                ), f"Large content max processing {max_processing_time:.2f}ms too slow"

                print(f"Large Content Processing Results:")
                print(f"  Average processing time: {avg_processing_time:.2f}ms")
                print(f"  Max processing time: {max_processing_time:.2f}ms")
                print(f"  Content size: ~10KB per message")

        finally:
            monitor.stop()

    @pytest.mark.performance
    def test_performance_monitor_efficiency(self):
        """Test the overhead of performance monitoring itself."""
        monitor = PerformanceMonitor(max_samples=1000)

        # Measure time to record many metrics
        start_time = time.perf_counter()

        for i in range(1000):
            metrics = PerformanceMetrics(
                detection_latency_ms=50.0 + (i % 50),
                processing_latency_ms=100.0 + (i % 100),
                throughput_msgs_per_sec=10.0 + (i % 10),
            )
            monitor.record_metrics(metrics)

        recording_time = time.perf_counter() - start_time

        # Performance monitoring should be very fast
        assert (
            recording_time < 0.1
        ), f"Recording 1000 metrics took {recording_time:.3f}s, too slow"

        # Test summary calculation performance
        start_time = time.perf_counter()
        summary = monitor.get_summary()
        summary_time = time.perf_counter() - start_time

        assert (
            summary_time < 0.05
        ), f"Summary calculation took {summary_time:.3f}s, too slow"

        # Test alerts calculation performance
        start_time = time.perf_counter()
        alerts = monitor.get_alerts()
        alerts_time = time.perf_counter() - start_time

        assert (
            alerts_time < 0.05
        ), f"Alerts calculation took {alerts_time:.3f}s, too slow"

        print(f"Performance Monitor Efficiency:")
        print(f"  Recording 1000 metrics: {recording_time:.3f}s")
        print(f"  Summary calculation: {summary_time:.3f}s")
        print(f"  Alerts calculation: {alerts_time:.3f}s")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_memory_usage_stability(
        self, temp_claude_dir, sample_message_content
    ):
        """Test memory usage remains stable during extended operation."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        monitor = FileMonitor(watch_path=str(temp_claude_dir))

        try:
            monitor.start()
            await asyncio.sleep(0.1)

            # Process many files to test memory stability
            for batch in range(10):  # 10 batches of 20 files each
                for i in range(20):
                    test_file = temp_claude_dir / f"memory-test-{batch}-{i}.jsonl"
                    test_file.write_text(json.dumps(sample_message_content))

                # Wait for batch processing
                await asyncio.sleep(1.0)

                # Check memory after each batch
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_growth = current_memory - initial_memory

                # Memory growth should be reasonable
                assert (
                    memory_growth < 100.0
                ), f"Memory grew by {memory_growth:.1f}MB after batch {batch}"

            final_memory = process.memory_info().rss / 1024 / 1024
            total_growth = final_memory - initial_memory

            print(f"Memory Usage Results:")
            print(f"  Initial memory: {initial_memory:.1f}MB")
            print(f"  Final memory: {final_memory:.1f}MB")
            print(f"  Total growth: {total_growth:.1f}MB after 200 files")

            # Total memory growth should be reasonable
            assert (
                total_growth < 50.0
            ), f"Total memory growth {total_growth:.1f}MB too high"

        finally:
            monitor.stop()

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_error_recovery_performance(self, temp_claude_dir):
        """Test performance impact of error conditions."""
        error_count = 0
        success_count = 0

        def error_tracking_callback(conversation_data):
            nonlocal success_count
            success_count += 1

        monitor = FileMonitor(
            watch_path=str(temp_claude_dir), callback=error_tracking_callback
        )

        try:
            monitor.start()
            await asyncio.sleep(0.1)

            start_time = time.perf_counter()

            # Mix of valid and invalid files
            for i in range(50):
                if i % 3 == 0:  # Every 3rd file is invalid
                    invalid_file = temp_claude_dir / f"invalid-{i}.jsonl"
                    invalid_file.write_text("invalid json content")
                else:  # Valid files
                    valid_file = temp_claude_dir / f"valid-{i}.jsonl"
                    valid_content = {
                        "uuid": str(uuid4()),
                        "sessionId": f"error-recovery-{i}",
                        "timestamp": "2024-01-15T10:30:00.000Z",
                        "type": "message",
                        "message": {"role": "user", "content": f"Valid message {i}"},
                    }
                    valid_file.write_text(json.dumps(valid_content))

            # Wait for processing
            await asyncio.sleep(3.0)

            total_time = time.perf_counter() - start_time
            stats = monitor.get_stats()

            # Performance should not degrade significantly due to errors
            total_files = 50
            processing_rate = total_files / total_time

            assert (
                processing_rate >= 10.0
            ), f"Processing rate {processing_rate:.1f} files/sec too low with errors"
            assert (
                stats["processing_errors"] >= 15
            ), "Expected errors from invalid files"
            assert (
                success_count >= 30
            ), f"Only {success_count} successful files processed"

            # System should maintain good detection latency despite errors
            perf_summary = monitor.performance_monitor.get_summary()
            if perf_summary["status"] != "no_data":
                avg_latency = perf_summary["detection_latency"]["mean"]
                assert (
                    avg_latency < 120.0
                ), f"Detection latency {avg_latency:.2f}ms degraded too much with errors"

            print(f"Error Recovery Performance:")
            print(f"  Total processing time: {total_time:.2f}s")
            print(f"  Processing rate: {processing_rate:.1f} files/sec")
            print(f"  Successful files: {success_count}")
            print(f"  Error files: {stats['processing_errors']}")

        finally:
            monitor.stop()


class TestPerformanceRegressionDetection:
    """Tests to detect performance regressions in the file monitoring system."""

    @pytest.mark.performance
    def test_baseline_performance_characteristics(self):
        """Establish baseline performance characteristics for regression testing."""
        monitor = PerformanceMonitor()

        # Simulate baseline performance metrics
        baseline_metrics = [
            PerformanceMetrics(
                detection_latency_ms=45.0,
                processing_latency_ms=85.0,
                throughput_msgs_per_sec=12.0,
            ),
            PerformanceMetrics(
                detection_latency_ms=52.0,
                processing_latency_ms=92.0,
                throughput_msgs_per_sec=11.5,
            ),
            PerformanceMetrics(
                detection_latency_ms=38.0,
                processing_latency_ms=78.0,
                throughput_msgs_per_sec=13.2,
            ),
            PerformanceMetrics(
                detection_latency_ms=47.0,
                processing_latency_ms=88.0,
                throughput_msgs_per_sec=12.8,
            ),
            PerformanceMetrics(
                detection_latency_ms=41.0,
                processing_latency_ms=82.0,
                throughput_msgs_per_sec=12.5,
            ),
        ]

        for metrics in baseline_metrics:
            monitor.record_metrics(metrics)

        summary = monitor.get_summary()

        # Record baseline characteristics for future regression testing
        baseline = {
            "detection_latency_p95": summary["detection_latency"]["p95"],
            "processing_latency_mean": summary["processing_latency"]["mean"],
            "throughput_mean": summary["throughput"]["mean"],
        }

        # Baseline assertions (these values should be achievable consistently)
        assert baseline["detection_latency_p95"] < 60.0
        assert baseline["processing_latency_mean"] < 100.0
        assert baseline["throughput_mean"] > 10.0

        print(f"Baseline Performance Characteristics:")
        print(f"  Detection latency P95: {baseline['detection_latency_p95']:.2f}ms")
        print(f"  Processing latency mean: {baseline['processing_latency_mean']:.2f}ms")
        print(f"  Throughput mean: {baseline['throughput_mean']:.1f} msg/s")

        # These could be stored for future regression testing
        return baseline


if __name__ == "__main__":
    # Run with: python -m pytest tests/test_performance_benchmarks.py -v -m performance
    pytest.main([__file__, "-v", "-m", "performance", "--tb=short"])
