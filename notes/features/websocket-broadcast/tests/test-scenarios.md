# WebSocket Broadcast Test Scenarios

## Overview
This document outlines comprehensive test scenarios for implementing WebSocket broadcast functionality in the Claude Code Observatory. Tests focus on BEHAVIOR, not implementation details, following Canon TDD principles.

## Key Requirements
- ConnectionManager needs a broadcast() method that's currently missing
- Integration with existing file monitoring system
- Subscription-based filtering (conversation:123, project:456, all_conversations)
- Real-time updates <50ms latency target
- Handle multiple concurrent connections gracefully

## Test Scenarios (Behavior-Focused)

### 1. Basic Broadcasting Tests

#### 1.1 ConnectionManager has broadcast method
**Behavior**: ConnectionManager should provide a broadcast() method that can send messages to all connected clients

#### 1.2 Broadcast sends message to all connected clients
**Behavior**: When broadcast() is called with a message, all currently connected WebSocket clients should receive the message

#### 1.3 Broadcast handles empty connection list
**Behavior**: When broadcast() is called with no connected clients, it should complete without errors

#### 1.4 Broadcast message format is consistent
**Behavior**: All broadcast messages should follow a consistent JSON structure with type, data, and timestamp fields

### 2. Subscription-Based Filtering Tests

#### 2.1 Broadcast to specific subscription group
**Behavior**: When broadcast() is called with a subscription filter, only clients subscribed to that specific group should receive the message

#### 2.2 Client receives only subscribed messages
**Behavior**: A client subscribed to "conversation:123" should only receive messages tagged for that conversation or "all_conversations"

#### 2.3 Multiple subscription support
**Behavior**: A client can subscribe to multiple channels (e.g., "conversation:123" and "project:456") and receive messages from all subscribed channels

#### 2.4 Subscription filtering for conversation updates
**Behavior**: When broadcasting conversation updates, only clients subscribed to that specific conversation or "all_conversations" should receive the update

#### 2.5 Subscription filtering for project updates
**Behavior**: When broadcasting project updates, only clients subscribed to that specific project or "project_updates" should receive the update

#### 2.6 Subscription filtering for file events
**Behavior**: When broadcasting file monitoring events, only clients subscribed to "file_events" should receive the update

### 3. File Monitoring Integration Tests

#### 3.1 File monitoring triggers WebSocket broadcast
**Behavior**: When file monitoring detects a new JSONL file, it should trigger a WebSocket broadcast to notify connected clients

#### 3.2 Conversation creation broadcasts to subscribed clients
**Behavior**: When a new conversation is created from file monitoring, clients subscribed to "all_conversations" should receive the new conversation data

#### 3.3 File monitoring broadcast includes conversation metadata
**Behavior**: When file monitoring triggers a broadcast, the message should include conversation ID, project ID, message count, and timestamp

#### 3.4 Multiple file events broadcast efficiently
**Behavior**: When multiple file events occur rapidly, broadcasts should be efficient and not overwhelm connected clients

#### 3.5 File monitoring broadcast respects latency requirements
**Behavior**: From file detection to WebSocket broadcast completion should be <50ms in 95% of cases

### 4. Connection Management Tests

#### 4.1 Broadcast handles client disconnection gracefully
**Behavior**: When a client disconnects during broadcast, the broadcast should continue to other clients without errors

#### 4.2 Broadcast skips disconnected clients
**Behavior**: Disconnected clients should be automatically removed from broadcast recipients without manual intervention

#### 4.3 Broadcast tracks failed message deliveries
**Behavior**: When message delivery fails to a client, the system should log the failure and continue with other clients

#### 4.4 Concurrent broadcasts don't interfere
**Behavior**: Multiple simultaneous broadcasts should not interfere with each other or corrupt message delivery

### 5. Performance and Scalability Tests

#### 5.1 Broadcast completes within latency target
**Behavior**: Broadcasting to all connected clients should complete within 50ms target for up to 100 concurrent connections

#### 5.2 Broadcast handles large message payloads
**Behavior**: Broadcasting messages with large conversation data (>1MB) should complete without timeouts or errors

#### 5.3 Memory usage remains stable during broadcasts
**Behavior**: Repeated broadcasts should not cause memory leaks or accumulate resources

#### 5.4 Broadcast throughput scales with connection count
**Behavior**: Broadcast performance should degrade gracefully as connection count increases (linear scaling)

### 6. Error Handling Tests

#### 6.1 Broadcast handles WebSocket send errors
**Behavior**: When WebSocket.send_text() fails for a client, the broadcast should continue to other clients

#### 6.2 Broadcast handles JSON serialization errors
**Behavior**: When message data cannot be serialized to JSON, broadcast should fail gracefully with appropriate error logging

#### 6.3 Broadcast handles network timeout errors
**Behavior**: When a client connection times out during broadcast, the system should detect and handle the timeout

#### 6.4 Broadcast recovers from partial failures
**Behavior**: When some clients fail to receive a broadcast, the system should retry or handle the failure without affecting other clients

### 7. Message Types and Formatting Tests

#### 7.1 Conversation update message format
**Behavior**: Conversation update broadcasts should include type="conversation_update", conversation data, and timestamp

#### 7.2 File monitoring update message format
**Behavior**: File monitoring broadcasts should include type="file_update", file path, event type, and timestamp

#### 7.3 Project update message format
**Behavior**: Project update broadcasts should include type="project_update", project data, and timestamp

#### 7.4 System status message format
**Behavior**: System status broadcasts should include type="system_status", health data, and timestamp

### 8. Integration with Existing WebSocket Handler Tests

#### 8.1 websocket_handler.broadcast_conversation_update uses ConnectionManager.broadcast
**Behavior**: The broadcast_conversation_update function should call ConnectionManager.broadcast() with properly formatted message

#### 8.2 websocket_handler.broadcast_file_monitoring_update uses ConnectionManager.broadcast
**Behavior**: The broadcast_file_monitoring_update function should call ConnectionManager.broadcast() with properly formatted message

#### 8.3 WebSocket endpoint integrates with broadcast system
**Behavior**: The WebSocket endpoint should be able to receive broadcast messages and relay them to connected clients

### 9. Real-time Update Tests

#### 9.1 Real-time conversation updates
**Behavior**: When a conversation is updated, all subscribed clients should receive the update within 50ms

#### 9.2 Real-time file monitoring updates
**Behavior**: When file monitoring detects changes, subscribed clients should receive updates within 50ms

#### 9.3 Real-time project status updates
**Behavior**: When project status changes, subscribed clients should receive updates within 50ms

### 10. Advanced Broadcast Features Tests

#### 10.1 Broadcast with message priority
**Behavior**: High-priority messages (errors, system alerts) should be delivered before normal-priority messages

#### 10.2 Broadcast with message persistence
**Behavior**: Important broadcasts should be stored and delivered to clients that connect after the broadcast

#### 10.3 Broadcast with rate limiting
**Behavior**: Rapid broadcasts should be rate-limited to prevent overwhelming clients

#### 10.4 Broadcast with compression
**Behavior**: Large broadcast messages should be compressed to improve delivery performance

## Test Implementation Notes

### Canon TDD Approach
- Pick ONE test scenario at a time
- Write the specific test case
- Make it pass with minimal code
- Refactor if needed
- Move to next test

### Test Organization
- Unit tests for ConnectionManager.broadcast() method
- Integration tests for file monitoring → WebSocket broadcast flow
- Performance tests for latency requirements
- Error handling tests for resilience

### Mock Requirements
- Mock WebSocket connections for broadcast testing
- Mock file monitoring events for integration testing
- Mock Supabase client for database operations
- Performance timing mocks for latency testing

### Metrics to Track
- Broadcast completion time
- Message delivery success rate
- Client connection stability
- Memory usage during broadcasts
- Error rates and types

## Implementation Priority
1. **Core broadcast functionality** (Tests 1.1-1.4)
2. **Subscription filtering** (Tests 2.1-2.6)
3. **File monitoring integration** (Tests 3.1-3.5)
4. **Error handling** (Tests 6.1-6.4)
5. **Performance optimization** (Tests 5.1-5.4)
6. **Advanced features** (Tests 10.1-10.4)

## Success Criteria
- All broadcast tests pass
- <50ms latency for real-time updates
- Graceful handling of 100+ concurrent connections
- Zero message loss during normal operations
- Proper integration with existing file monitoring system