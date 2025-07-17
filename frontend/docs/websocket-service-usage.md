# WebSocket Service Usage Guide

This document provides comprehensive guidance on using the WebSocket memory management services in the Claude Code Observatory frontend application.

## Overview

The WebSocket service layer consists of three main components:
- **WebSocketClient**: Low-level WebSocket connection management with automatic reconnection
- **DashboardService**: High-level service for dashboard data and WebSocket integration
- **ApiClient**: HTTP API communication for REST endpoints

## Core Features

### Memory Management
- Automatic cleanup on navigation and component destruction
- Prevention of memory leaks through proper event listener management
- Resource cleanup with multiple fallback strategies

### Connection Resilience
- Automatic reconnection with exponential backoff and jitter
- Connection state monitoring and health checks
- Graceful error handling and recovery

### Lifecycle Management
- SvelteKit navigation hooks integration
- Component destruction cleanup
- Browser unload event handling

## WebSocket Client Usage

### Basic Connection

```typescript
import { wsClient } from '$lib/api/websocket';

// Connect to WebSocket
wsClient.connect();

// Check connection status
if (wsClient.isConnected) {
  console.log('WebSocket is connected');
}

// Get detailed connection status
const status = wsClient.getConnectionStatus();
console.log('Connection attempts:', status.attempts);
console.log('Connected:', status.connected);
```

### Message Handling

```typescript
// Subscribe to specific message types
const unsubscribe = wsClient.on<ConversationUpdateMessage>('conversation_update', (data) => {
  console.log('Conversation updated:', data);
  // Update your UI state
});

// Subscribe to connection events
wsClient.on('connection:connected', () => {
  console.log('WebSocket connected');
});

wsClient.on('connection:disconnected', () => {
  console.log('WebSocket disconnected');
});

wsClient.on('connection:error', (error) => {
  console.error('WebSocket error:', error);
});

// Clean up subscription when component unmounts
onDestroy(() => {
  unsubscribe();
});
```

### Manual Cleanup

```typescript
// Disconnect WebSocket
wsClient.disconnect();

// Complete cleanup (destroys instance)
wsClient.destroy();
```

## Dashboard Service Usage

### Component Integration

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { dashboardService } from '$lib/api/dashboard';
  import { conversations, projects, connectionStatus } from '$lib/stores/conversations';

  let analytics = null;
  let loading = true;
  let error = null;

  onMount(async () => {
    try {
      const result = await dashboardService.initialize();
      analytics = result.analytics;
      loading = false;
    } catch (err) {
      error = err.message;
      loading = false;
    }
  });

  // Reactive connection status
  $: isConnected = $connectionStatus === 'connected';
</script>

{#if loading}
  <div>Loading dashboard...</div>
{:else if error}
  <div class="error">
    Error: {error}
    <button on:click={() => dashboardService.retryLoad()}>
      Retry
    </button>
  </div>
{:else}
  <div>
    <p>Connection: {isConnected ? 'Connected' : 'Disconnected'}</p>
    <p>Total Conversations: {analytics.total_conversations}</p>
    
    <!-- Display conversations from store -->
    {#each $conversations as conversation}
      <div>{conversation.title}</div>
    {/each}
  </div>
{/if}
```

### Using the Hook Pattern

```typescript
import { useDashboard } from '$lib/api/dashboard';

export function createDashboardComponent() {
  const dashboard = useDashboard();
  
  return {
    initialize: dashboard.initialize,
    connectionState: dashboard.connectionState,
    reconnect: dashboard.reconnect
  };
}
```

### Creating Multiple Service Instances

```typescript
import { createDashboardService } from '$lib/api/dashboard';

// Create a new dashboard service instance
// Automatically cleans up when component is destroyed
const dashboard = createDashboardService();

// Initialize the service
await dashboard.initialize();
```

## API Client Usage

### Basic HTTP Requests

```typescript
import { apiClient } from '$lib/api/client';

// GET request
const projects = await apiClient.get('/projects');

// POST request
const newProject = await apiClient.post('/projects', {
  name: 'My Project',
  path: '/path/to/project'
});

// PUT request
const updatedProject = await apiClient.put(`/projects/${id}`, updateData);

// DELETE request
await apiClient.delete(`/projects/${id}`);
```

### Using Convenience Methods

```typescript
import { api } from '$lib/api/client';

// Projects
const projects = await api.getProjects();
const project = await api.getProject('project-id');

// Conversations
const conversations = await api.getConversations(1, 20); // page, perPage
const conversation = await api.getConversation('conv-id');

// Analytics
const analytics = await api.getAnalytics('7d'); // time range

// Search
const results = await api.search('query', { type: 'conversation' });
```

### Error Handling

```typescript
import { isApiError, getErrorMessage } from '$lib/api/client';

try {
  const data = await apiClient.get('/endpoint');
} catch (error) {
  if (isApiError(error)) {
    console.log('API Error:', error.status, error.message);
    console.log('Error code:', error.code);
    console.log('Details:', error.details);
  } else {
    console.log('Other error:', getErrorMessage(error));
  }
}
```

## Memory Management Best Practices

### Component-Level Cleanup

```svelte
<script lang="ts">
  import { onDestroy } from 'svelte';
  import { wsClient } from '$lib/api/websocket';

  let unsubscribers = [];

  // Subscribe to events
  unsubscribers.push(
    wsClient.on('message_type', handleMessage),
    wsClient.on('connection:connected', handleConnect)
  );

  // Cleanup on component destruction
  onDestroy(() => {
    unsubscribers.forEach(unsubscribe => unsubscribe());
  });
</script>
```

### Navigation Cleanup

The WebSocket client automatically handles navigation cleanup using SvelteKit's `beforeNavigate` hook:

```typescript
// This is handled automatically in WebSocketClient
import { beforeNavigate } from '$app/navigation';

beforeNavigate(() => {
  // WebSocket cleanup happens automatically
});
```

### Browser Unload Cleanup

```typescript
// Automatic cleanup on browser unload (handled in WebSocketClient)
window.addEventListener('beforeunload', () => {
  wsClient.disconnect();
});

window.addEventListener('pagehide', () => {
  wsClient.disconnect();
});
```

## Configuration

### WebSocket Configuration

```typescript
// In $lib/config.ts
export const config = {
  wsUrl: 'ws://localhost:3000/ws',
  reconnectInterval: 1000, // Base reconnection interval (ms)
  maxReconnectAttempts: 5,
  heartbeatInterval: 30000, // Heartbeat interval (ms)
  enableRealTime: true
};
```

### Custom WebSocket Client

```typescript
import { WebSocketClient } from '$lib/api/websocket';

const customClient = new WebSocketClient({
  url: 'ws://custom-server.com/ws',
  reconnectInterval: 2000,
  maxReconnectAttempts: 10,
  heartbeatInterval: 60000
});
```

## Testing

### Unit Testing WebSocket Client

```typescript
import { describe, it, expect, vi } from 'vitest';
import { WebSocketClient } from '$lib/api/websocket';

describe('WebSocketClient', () => {
  it('should connect and handle messages', async () => {
    const client = new WebSocketClient();
    const handler = vi.fn();
    
    client.on('test_message', handler);
    client.connect();
    
    // Simulate receiving a message
    const message = {
      type: 'test_message',
      data: { test: true },
      timestamp: Date.now()
    };
    
    // Test message handling
    expect(handler).toHaveBeenCalledWith({ test: true });
  });
});
```

### Integration Testing

See `frontend/src/tests/integration/websocket-resilience.test.ts` for comprehensive integration test examples covering:

- Connection resilience and reconnection
- Message handling and error recovery
- Memory management and cleanup
- Stress testing and performance
- Navigation lifecycle management

## Common Patterns

### Real-time Data Updates

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { conversations } from '$lib/stores/conversations';
  import { wsClient } from '$lib/api/websocket';

  onMount(() => {
    // Subscribe to real-time conversation updates
    const unsubscribe = wsClient.on('conversation_update', (data) => {
      conversations.updateConversation(data.id, data);
    });

    return unsubscribe;
  });
</script>
```

### Connection Status Indicators

```svelte
<script lang="ts">
  import { connectionStatus } from '$lib/stores/conversations';
  import { dashboardService } from '$lib/api/dashboard';

  $: connectionIcon = {
    connected: '🟢',
    disconnected: '🔴',
    connecting: '🟡'
  }[$connectionStatus] || '⚪';

  function handleReconnect() {
    dashboardService.reconnectWebSocket();
  }
</script>

<div class="connection-status">
  <span>{connectionIcon} {$connectionStatus}</span>
  {#if $connectionStatus !== 'connected'}
    <button on:click={handleReconnect}>Reconnect</button>
  {/if}
</div>
```

### Error Recovery

```svelte
<script lang="ts">
  import { dashboardService } from '$lib/api/dashboard';

  let lastError = null;
  let retryCount = 0;

  // Subscribe to connection state changes
  dashboardService.connectionState.subscribe(state => {
    if (state.status === 'error') {
      lastError = state.lastError;
    }
  });

  async function handleRetry() {
    try {
      retryCount++;
      await dashboardService.retryLoad();
      lastError = null;
      retryCount = 0;
    } catch (error) {
      lastError = error.message;
    }
  }
</script>

{#if lastError}
  <div class="error-banner">
    <p>Connection error: {lastError}</p>
    <button on:click={handleRetry} disabled={retryCount >= 3}>
      Retry {retryCount > 0 ? `(${retryCount})` : ''}
    </button>
  </div>
{/if}
```

## Performance Considerations

### Message Throttling

```typescript
import { debounce } from '$lib/utils';

// Debounce frequent updates
const debouncedHandler = debounce((data) => {
  updateUI(data);
}, 100);

wsClient.on('frequent_updates', debouncedHandler);
```

### Memory Monitoring

```typescript
// Monitor WebSocket memory usage in development
if (import.meta.env.DEV) {
  setInterval(() => {
    const status = wsClient.getConnectionStatus();
    console.log('WebSocket status:', status);
    console.log('Memory usage:', performance.memory);
  }, 10000);
}
```

## Security Considerations

### Message Validation

```typescript
wsClient.on('sensitive_data', (data) => {
  // Validate incoming data
  if (!isValidMessageFormat(data)) {
    console.warn('Invalid message format received');
    return;
  }
  
  // Sanitize data before use
  const sanitizedData = sanitizeData(data);
  processData(sanitizedData);
});
```

### Connection Security

```typescript
// Use secure WebSocket connections in production
const wsUrl = import.meta.env.PROD 
  ? 'wss://secure-server.com/ws'
  : 'ws://localhost:3000/ws';
```

## Troubleshooting

### Common Issues

1. **Connection Failures**: Check network connectivity and server availability
2. **Memory Leaks**: Ensure proper cleanup of event listeners
3. **Reconnection Problems**: Verify exponential backoff configuration
4. **Message Loss**: Implement message acknowledgment patterns

### Debug Mode

```typescript
// Enable debug logging
import { config } from '$lib/config';

// Set log level to debug
config.logLevel = 'debug';

// Monitor WebSocket events
wsClient.on('*', (type, data) => {
  console.log(`WebSocket event: ${type}`, data);
});
```

### Health Monitoring

```typescript
// Monitor connection health
setInterval(() => {
  const status = wsClient.getConnectionStatus();
  if (!status.connected && status.attempts > 3) {
    console.warn('WebSocket connection unstable');
    // Implement fallback strategies
  }
}, 30000);
```

This documentation provides comprehensive guidance for using the WebSocket services effectively while maintaining proper memory management and connection resilience.