# WebSocket Broadcast Feature

## Overview
This feature implements WebSocket broadcast functionality for the Claude Code Observatory, enabling real-time communication between the backend and connected clients.

## Current State
- **Status**: Ready for Canon TDD implementation
- **Missing**: ConnectionManager.broadcast() method
- **Dependencies**: Existing WebSocket infrastructure (ConnectionManager, websocket_handler)

## Key Components

### ConnectionManager.broadcast() Method
**Purpose**: Send messages to all connected clients or filtered subsets based on subscriptions

**Current Issue**: Referenced in `websocket_handler.py` line 112 but not implemented

**Required Behavior**:
```python
async def broadcast(
    self,
    message: dict,
    subscription_filter: Optional[str] = None
) -> None:
    """
    Broadcast message to connected clients.
    
    Args:
        message: JSON message to broadcast
        subscription_filter: Optional filter (e.g., "conversation:123")
    """
```

### File Monitoring Integration
**Purpose**: Trigger WebSocket broadcasts when file monitoring detects changes

**Integration Points**:
- `FileMonitor._handle_file_event()` should trigger broadcasts
- `broadcast_file_monitoring_update()` needs implementation
- `broadcast_conversation_update()` needs ConnectionManager.broadcast() call

### Subscription System
**Purpose**: Filter broadcasts to relevant clients only

**Subscription Types**:
- `all_conversations` - All conversation updates
- `conversation:123` - Specific conversation updates
- `project:456` - Specific project updates
- `file_events` - File monitoring events

## Canon TDD Implementation Plan

### Phase 1: Core Broadcast Method (Tests 1.1-1.4)
1. **Test**: ConnectionManager has broadcast method
2. **Test**: Broadcast sends message to all connected clients
3. **Test**: Broadcast handles empty connection list
4. **Test**: Broadcast message format is consistent

### Phase 2: Subscription Filtering (Tests 2.1-2.6)
1. **Test**: Broadcast to specific subscription group
2. **Test**: Client receives only subscribed messages
3. **Test**: Multiple subscription support
4. **Test**: Subscription filtering for different update types

### Phase 3: File Monitoring Integration (Tests 3.1-3.5)
1. **Test**: File monitoring triggers WebSocket broadcast
2. **Test**: Conversation creation broadcasts to subscribed clients
3. **Test**: File monitoring broadcast includes conversation metadata
4. **Test**: Multiple file events broadcast efficiently
5. **Test**: File monitoring broadcast respects latency requirements

### Phase 4: Error Handling and Performance (Tests 6.1-6.4, 5.1-5.4)
1. **Test**: Broadcast handles client disconnection gracefully
2. **Test**: Broadcast completes within latency target
3. **Test**: Error recovery and resilience
4. **Test**: Performance optimization

## Technical Requirements

### Performance
- Broadcast completion: <50ms for 100 concurrent connections
- Message delivery: 99.9% success rate
- Memory usage: Stable during repeated broadcasts
- Latency: File detection to broadcast <50ms

### Error Handling
- Graceful client disconnection handling
- JSON serialization error recovery
- Network timeout handling
- Partial failure recovery

### Integration
- File monitoring system integration
- Existing WebSocket handler compatibility
- Supabase database integration
- Performance monitoring integration

## Implementation Dependencies

### Required Imports
```python
import json
import asyncio
import logging
from typing import Dict, Set, List, Optional
from datetime import datetime
```

### Integration Points
- `app.websocket.connection_manager.ConnectionManager`
- `app.websocket.websocket_handler.broadcast_*_update` functions
- `app.monitoring.file_monitor.FileMonitor`
- `app.models.contracts.ConversationData`

## Success Criteria
- All test scenarios pass
- <50ms broadcast latency achieved
- Graceful handling of 100+ concurrent connections
- Zero message loss during normal operations
- Seamless integration with file monitoring system

## Development Notes
- Follow Canon TDD: One test at a time
- Use existing ConnectionManager structure
- Maintain compatibility with current WebSocket infrastructure
- Focus on behavior, not implementation details
- Test subscription filtering thoroughly