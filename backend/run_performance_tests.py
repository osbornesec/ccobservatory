#!/usr/bin/env python3
"""
Performance Test Runner for Claude Code Observatory
Tests 5.1-5.4: Performance & Scalability

This script runs the performance and scalability tests independently
of the full test suite to avoid dependency issues.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import json
import time
import psutil
from unittest.mock import AsyncMock, MagicMock
from app.websocket.broadcast import BroadcastManager


def create_mock_connection(connection_id: str):
    """Create a mock WebSocket connection for testing."""
    mock_connection = MagicMock()
    mock_connection.connection_id = connection_id
    mock_connection.send = AsyncMock()
    mock_connection.closed = False
    return mock_connection


async def test_5_1_broadcast_latency():
    """Test 5.1: Broadcast completes within latency target (<50ms for 100 connections)"""
    print("Running Test 5.1: Broadcast Latency Target")
    
    broadcast_manager = BroadcastManager()
    
    # Create 100 mock connections
    connections = []
    for i in range(100):
        connection = create_mock_connection(f"conn_{i}")
        connections.append(connection)
        broadcast_manager.add_connection(connection)
    
    # Test message
    test_message = json.dumps({"type": "test", "data": "performance test"})
    
    # Measure broadcast latency
    start_time = time.perf_counter()
    await broadcast_manager.broadcast(test_message)
    end_time = time.perf_counter()
    
    latency_ms = (end_time - start_time) * 1000
    
    # Verify all connections received the message
    for connection in connections:
        assert connection.send.called, f"Connection {connection.connection_id} did not receive message"
    
    # Assert latency is under 50ms
    assert latency_ms < 50, f"Broadcast latency {latency_ms:.2f}ms exceeds 50ms target"
    
    print(f"✓ PASSED: Broadcast latency {latency_ms:.2f}ms < 50ms target")
    
    # Clean up
    for connection in connections:
        broadcast_manager.remove_connection(connection)
    
    return True


async def test_5_2_large_payload():
    """Test 5.2: Broadcast handles large message payloads (>1MB)"""
    print("Running Test 5.2: Large Message Payload Handling")
    
    broadcast_manager = BroadcastManager()
    
    # Create 50 mock connections
    connections = []
    for i in range(50):
        connection = create_mock_connection(f"large_conn_{i}")
        connections.append(connection)
        broadcast_manager.add_connection(connection)
    
    # Create large payload
    large_data = {
        "type": "large_message",
        "data": "x" * (1024 * 1024),  # 1MB of data
        "additional_data": ["item"] * 50000,  # Additional data
        "timestamp": time.time()
    }
    large_message = json.dumps(large_data)
    
    payload_size_mb = len(large_message.encode('utf-8')) / (1024 * 1024)
    assert payload_size_mb > 1, f"Payload size {payload_size_mb:.2f}MB should be > 1MB"
    
    # Measure processing time
    start_time = time.perf_counter()
    await broadcast_manager.broadcast(large_message)
    end_time = time.perf_counter()
    
    processing_time_ms = (end_time - start_time) * 1000
    
    # Verify all connections received the message
    for connection in connections:
        assert connection.send.called, f"Connection {connection.connection_id} did not receive message"
    
    # Assert reasonable processing time
    assert processing_time_ms < 500, f"Processing time {processing_time_ms:.2f}ms too slow"
    
    print(f"✓ PASSED: Large payload ({payload_size_mb:.2f}MB) processed in {processing_time_ms:.2f}ms < 500ms")
    
    # Clean up
    for connection in connections:
        broadcast_manager.remove_connection(connection)
    
    return True


async def test_5_3_memory_stability():
    """Test 5.3: Memory usage remains stable during broadcasts"""
    print("Running Test 5.3: Memory Usage Stability")
    
    broadcast_manager = BroadcastManager()
    
    # Get initial memory
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    
    # Create 100 mock connections
    connections = []
    for i in range(100):
        connection = create_mock_connection(f"mem_conn_{i}")
        connections.append(connection)
        broadcast_manager.add_connection(connection)
    
    # Perform multiple broadcasts
    memory_readings = []
    test_message = json.dumps({"type": "memory_test", "data": "x" * 1000})
    
    for iteration in range(10):
        await broadcast_manager.broadcast(test_message)
        memory_readings.append(process.memory_info().rss)
        await asyncio.sleep(0.01)
    
    # Calculate memory metrics
    final_memory = memory_readings[-1]
    memory_growth_mb = (final_memory - initial_memory) / (1024 * 1024)
    memory_variation_mb = (max(memory_readings) - min(memory_readings)) / (1024 * 1024)
    
    # Assert memory stability
    assert memory_growth_mb < 10, f"Memory growth {memory_growth_mb:.2f}MB too high"
    assert memory_variation_mb < 5, f"Memory variation {memory_variation_mb:.2f}MB too high"
    
    print(f"✓ PASSED: Memory stable - growth {memory_growth_mb:.2f}MB < 10MB, variation {memory_variation_mb:.2f}MB < 5MB")
    
    # Clean up
    for connection in connections:
        broadcast_manager.remove_connection(connection)
    
    return True


async def test_5_4_linear_scaling():
    """Test 5.4: Broadcast throughput scales with connection count (linear scaling)"""
    print("Running Test 5.4: Linear Scaling Characteristics")
    
    broadcast_manager = BroadcastManager()
    
    test_message = json.dumps({"type": "scaling_test", "data": "scaling"})
    scaling_results = []
    
    # Test with different connection counts
    for count in [10, 50, 100, 200]:
        connections = []
        for i in range(count):
            connection = create_mock_connection(f"scale_conn_{count}_{i}")
            connections.append(connection)
            broadcast_manager.add_connection(connection)
        
        # Measure broadcast time
        start_time = time.perf_counter()
        await broadcast_manager.broadcast(test_message)
        end_time = time.perf_counter()
        
        broadcast_time_ms = (end_time - start_time) * 1000
        throughput = count / (broadcast_time_ms / 1000)
        
        scaling_results.append({
            "connection_count": count,
            "broadcast_time_ms": broadcast_time_ms,
            "throughput": throughput
        })
        
        # Verify all connections received the message
        for connection in connections:
            assert connection.send.called, f"Connection {connection.connection_id} did not receive message"
        
        # Clean up
        for connection in connections:
            broadcast_manager.remove_connection(connection)
    
    # Verify scaling characteristics
    for result in scaling_results:
        throughput = result["throughput"]
        assert throughput > 1000, f"Throughput {throughput:.0f} conn/s too low"
    
    # Check linear scaling
    times = [r["broadcast_time_ms"] for r in scaling_results]
    counts = [r["connection_count"] for r in scaling_results]
    
    for i in range(1, len(times)):
        time_ratio = times[i] / times[i-1]
        count_ratio = counts[i] / counts[i-1]
        assert time_ratio <= count_ratio * 2, f"Scaling degradation too high"
    
    # Verify 200 connection performance
    largest_test = scaling_results[-1]
    assert largest_test["broadcast_time_ms"] < 100, f"200 connection broadcast too slow"
    
    print("✓ PASSED: Linear scaling verified")
    for result in scaling_results:
        print(f"  - {result['connection_count']} connections: {result['broadcast_time_ms']:.2f}ms ({result['throughput']:.0f} conn/s)")
    
    return True


async def run_all_tests():
    """Run all performance and scalability tests."""
    print("=" * 70)
    print("Claude Code Observatory - Performance & Scalability Tests")
    print("Tests 5.1-5.4: Following Canon TDD Methodology")
    print("=" * 70)
    
    results = []
    
    try:
        # Run Test 5.1
        results.append(await test_5_1_broadcast_latency())
        print()
        
        # Run Test 5.2
        results.append(await test_5_2_large_payload())
        print()
        
        # Run Test 5.3
        results.append(await test_5_3_memory_stability())
        print()
        
        # Run Test 5.4
        results.append(await test_5_4_linear_scaling())
        print()
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        return False
    
    # Summary
    print("=" * 70)
    if all(results):
        print("✅ ALL TESTS PASSED: Performance & Scalability Requirements Met")
        print()
        print("Requirements Verified:")
        print("  ✓ Broadcast latency < 50ms for 100 connections")
        print("  ✓ Large payloads (>1MB) handled efficiently")
        print("  ✓ Memory usage remains stable during broadcasts")
        print("  ✓ Linear scaling with connection count")
        print()
        print("The websocket broadcast system is ready for production deployment.")
    else:
        print("❌ SOME TESTS FAILED: Review implementation")
    
    print("=" * 70)
    return all(results)


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)