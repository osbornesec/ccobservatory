"""
Performance and scalability tests for the websocket broadcast system.

These tests validate that the broadcast system can handle production-scale loads
without performance degradation or memory leaks, following Canon TDD methodology.

Tests 5.1-5.4: Performance & Scalability
- Test 5.1: Broadcast completes within latency target (<50ms for 100 connections)
- Test 5.2: Broadcast handles large message payloads (>1MB)
- Test 5.3: Memory usage remains stable during broadcasts
- Test 5.4: Broadcast throughput scales with connection count (linear scaling)
"""

import asyncio
import json
import time
import psutil
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List, Dict, Any

from app.websocket.broadcast import BroadcastManager


class TestPerformanceScalability:
    """Test suite for websocket broadcast performance and scalability."""
    
    @pytest.fixture
    def broadcast_manager(self):
        """Create a BroadcastManager instance for testing."""
        return BroadcastManager()
    
    @pytest.fixture
    def mock_websocket_connections(self):
        """Create mock WebSocket connections for testing."""
        def create_mock_connection(connection_id: str) -> MagicMock:
            mock_connection = MagicMock()
            mock_connection.connection_id = connection_id
            mock_connection.send = AsyncMock()
            mock_connection.closed = False
            return mock_connection
        
        return create_mock_connection
    
    @pytest.fixture
    def large_message_payload(self):
        """Create a large message payload (>1MB) for testing."""
        # Create a 1.5MB JSON payload
        large_data = {
            "type": "large_message",
            "data": "x" * (1024 * 1024),  # 1MB of data
            "additional_data": ["item"] * 50000,  # Additional data to exceed 1MB
            "timestamp": time.time()
        }
        return json.dumps(large_data)
    
    @pytest.mark.asyncio
    async def test_broadcast_completes_within_latency_target_100_connections(
        self, broadcast_manager, mock_websocket_connections
    ):
        """
        Test 5.1: Broadcast completes within latency target (<50ms for 100 connections)
        
        Validates that broadcasting a message to 100 connections completes
        within the 50ms latency requirement.
        """
        # Create 100 mock connections
        connections = []
        for i in range(100):
            connection = mock_websocket_connections(f"conn_{i}")
            connections.append(connection)
            broadcast_manager.add_connection(connection)
        
        # Test message
        test_message = {"type": "test", "data": "performance test"}
        message_json = json.dumps(test_message)
        
        # Measure broadcast latency
        start_time = time.perf_counter()
        await broadcast_manager.broadcast(message_json)
        end_time = time.perf_counter()
        
        # Calculate latency in milliseconds
        latency_ms = (end_time - start_time) * 1000
        
        # Verify all connections received the message
        for connection in connections:
            connection.send.assert_called_once_with(message_json)
        
        # Assert latency is under 50ms
        assert latency_ms < 50, f"Broadcast latency {latency_ms:.2f}ms exceeds 50ms target"
        
        # Verify all connections were processed
        assert len(connections) == 100
        
        # Clean up
        for connection in connections:
            broadcast_manager.remove_connection(connection)
    
    @pytest.mark.asyncio
    async def test_broadcast_handles_large_message_payloads(
        self, broadcast_manager, mock_websocket_connections, large_message_payload
    ):
        """
        Test 5.2: Broadcast handles large message payloads (>1MB)
        
        Validates that the broadcast system can handle large message payloads
        without performance degradation or errors.
        """
        # Create 50 mock connections for large payload testing
        connections = []
        for i in range(50):
            connection = mock_websocket_connections(f"large_conn_{i}")
            connections.append(connection)
            broadcast_manager.add_connection(connection)
        
        # Verify payload size is greater than 1MB
        payload_size_mb = len(large_message_payload.encode('utf-8')) / (1024 * 1024)
        assert payload_size_mb > 1, f"Payload size {payload_size_mb:.2f}MB should be > 1MB"
        
        # Measure broadcast performance with large payload
        start_time = time.perf_counter()
        await broadcast_manager.broadcast(large_message_payload)
        end_time = time.perf_counter()
        
        # Calculate processing time
        processing_time_ms = (end_time - start_time) * 1000
        
        # Verify all connections received the large message
        for connection in connections:
            connection.send.assert_called_once_with(large_message_payload)
        
        # Assert reasonable processing time (should be < 500ms for 50 connections)
        assert processing_time_ms < 500, f"Large payload processing time {processing_time_ms:.2f}ms too slow"
        
        # Clean up
        for connection in connections:
            broadcast_manager.remove_connection(connection)
    
    @pytest.mark.asyncio
    async def test_memory_usage_remains_stable_during_broadcasts(
        self, broadcast_manager, mock_websocket_connections
    ):
        """
        Test 5.3: Memory usage remains stable during broadcasts
        
        Validates that memory usage doesn't grow unboundedly during
        repeated broadcast operations.
        """
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Create 100 mock connections
        connections = []
        for i in range(100):
            connection = mock_websocket_connections(f"mem_conn_{i}")
            connections.append(connection)
            broadcast_manager.add_connection(connection)
        
        # Perform multiple broadcasts and track memory usage
        memory_readings = []
        test_message = json.dumps({"type": "memory_test", "data": "x" * 1000})
        
        for iteration in range(10):
            # Perform broadcast
            await broadcast_manager.broadcast(test_message)
            
            # Measure memory usage
            current_memory = process.memory_info().rss
            memory_readings.append(current_memory)
            
            # Allow some time for cleanup
            await asyncio.sleep(0.01)
        
        # Calculate memory growth
        final_memory = memory_readings[-1]
        memory_growth_mb = (final_memory - initial_memory) / (1024 * 1024)
        
        # Assert memory growth is reasonable (< 10MB for this test)
        assert memory_growth_mb < 10, f"Memory growth {memory_growth_mb:.2f}MB too high"
        
        # Check memory doesn't grow continuously
        max_memory = max(memory_readings)
        min_memory = min(memory_readings)
        memory_variation_mb = (max_memory - min_memory) / (1024 * 1024)
        
        # Memory variation should be small (< 5MB)
        assert memory_variation_mb < 5, f"Memory variation {memory_variation_mb:.2f}MB too high"
        
        # Clean up
        for connection in connections:
            broadcast_manager.remove_connection(connection)
    
    @pytest.mark.asyncio
    async def test_broadcast_throughput_scales_linearly_with_connection_count(
        self, broadcast_manager, mock_websocket_connections
    ):
        """
        Test 5.4: Broadcast throughput scales with connection count (linear scaling)
        
        Validates that broadcast throughput scales approximately linearly
        with the number of connections.
        """
        test_message = json.dumps({"type": "scaling_test", "data": "scaling"})
        scaling_results = []
        
        # Test with different connection counts: 10, 50, 100, 200
        connection_counts = [10, 50, 100, 200]
        
        for count in connection_counts:
            # Create connections for this test
            connections = []
            for i in range(count):
                connection = mock_websocket_connections(f"scale_conn_{count}_{i}")
                connections.append(connection)
                broadcast_manager.add_connection(connection)
            
            # Measure broadcast time for this connection count
            start_time = time.perf_counter()
            await broadcast_manager.broadcast(test_message)
            end_time = time.perf_counter()
            
            broadcast_time_ms = (end_time - start_time) * 1000
            throughput = count / (broadcast_time_ms / 1000)  # connections per second
            
            scaling_results.append({
                "connection_count": count,
                "broadcast_time_ms": broadcast_time_ms,
                "throughput": throughput
            })
            
            # Verify all connections received the message
            for connection in connections:
                connection.send.assert_called_once_with(test_message)
            
            # Clean up connections
            for connection in connections:
                broadcast_manager.remove_connection(connection)
        
        # Analyze scaling characteristics
        assert len(scaling_results) == 4, "Should have results for all connection counts"
        
        # Check that throughput is reasonable for all connection counts
        for result in scaling_results:
            throughput = result["throughput"]
            assert throughput > 1000, f"Throughput {throughput:.0f} conn/s too low for {result['connection_count']} connections"
        
        # Check that broadcast time increases reasonably with connection count
        # (should be roughly linear, allowing for some overhead)
        times = [r["broadcast_time_ms"] for r in scaling_results]
        counts = [r["connection_count"] for r in scaling_results]
        
        # Simple linearity check: time should increase with connection count
        # but not more than quadratically
        for i in range(1, len(times)):
            time_ratio = times[i] / times[i-1]
            count_ratio = counts[i] / counts[i-1]
            
            # Time ratio should be close to count ratio (linear scaling)
            # Allow up to 2x degradation for reasonable overhead
            assert time_ratio <= count_ratio * 2, f"Scaling degradation too high: {time_ratio:.2f}x time for {count_ratio:.2f}x connections"
        
        # Verify that the largest test (200 connections) still meets latency requirements
        largest_test = scaling_results[-1]
        assert largest_test["broadcast_time_ms"] < 100, f"200 connection broadcast time {largest_test['broadcast_time_ms']:.2f}ms too slow"