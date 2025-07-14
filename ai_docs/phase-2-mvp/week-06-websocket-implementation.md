# Week 6: WebSocket Implementation for Real-Time Communication

## Overview
Implement real-time WebSocket communication using Bun's native WebSocket support for live conversation monitoring, real-time updates, and collaborative features. This week focuses on bidirectional communication, event broadcasting, and connection management.

## Team Assignments
- **Backend Lead**: WebSocket server implementation, event system architecture
- **Full-Stack Developer**: Client-side WebSocket integration, real-time UI updates
- **Frontend Developer**: Real-time component development, state synchronization

## Daily Schedule

### Monday: WebSocket Server Foundation
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Bun WebSocket server configuration and upgrade handling
- **10:30-12:00**: Connection management and client tracking

#### Afternoon (4 hours)
- **13:00-15:00**: Basic message routing and event handling
- **15:00-17:00**: Authentication integration for WebSocket connections

### Tuesday: Event System & Broadcasting
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Event system architecture and message types
- **10:30-12:00**: Room-based broadcasting for conversation channels

#### Afternoon (4 hours)
- **13:00-15:00**: Real-time conversation updates implementation
- **15:00-17:00**: Message broadcasting and subscription management

### Wednesday: Client-Side Integration
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: JavaScript WebSocket client implementation
- **10:30-12:00**: Connection state management and reconnection logic

#### Afternoon (4 hours)
- **13:00-15:00**: Event handling and UI update mechanisms
- **15:00-17:00**: Error handling and connection recovery

### Thursday: Advanced Features
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Presence system (online users, typing indicators)
- **10:30-12:00**: Real-time analytics data streaming

#### Afternoon (4 hours)
- **13:00-15:00**: File upload progress and real-time processing updates
- **15:00-17:00**: Collaborative features (shared cursors, live editing)

### Friday: Testing & Performance Optimization
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: WebSocket connection testing and load testing
- **10:30-12:00**: Memory leak detection and connection cleanup

#### Afternoon (4 hours)
- **13:00-15:00**: Performance optimization and message compression
- **15:00-17:00**: Integration testing with existing API endpoints

## Technical Implementation Details

### WebSocket Server Configuration
```typescript
// websocket/server.ts
import { serve, ServerWebSocket } from "bun";
import { EventEmitter } from "events";
import { authWS } from "./middleware/auth";
import { ConnectionManager } from "./connection-manager";
import { EventBroadcaster } from "./event-broadcaster";

interface WebSocketData {
  userId: string;
  sessionId: string;
  subscriptions: Set<string>;
}

const connectionManager = new ConnectionManager();
const eventBroadcaster = new EventBroadcaster();

export const websocketServer = serve<WebSocketData>({
  port: process.env.WS_PORT || 3002,
  
  fetch(req, server) {
    const url = new URL(req.url);
    
    if (url.pathname === "/ws") {
      // Authenticate WebSocket connection
      const authResult = authWS(req);
      if (!authResult.success) {
        return new Response("Unauthorized", { status: 401 });
      }
      
      const upgraded = server.upgrade(req, {
        data: {
          userId: authResult.userId,
          sessionId: authResult.sessionId,
          subscriptions: new Set<string>()
        }
      });
      
      return upgraded ? undefined : new Response("Upgrade failed", { status: 400 });
    }
    
    return new Response("WebSocket endpoint not found", { status: 404 });
  },
  
  websocket: {
    maxPayloadLength: 16 * 1024 * 1024, // 16MB
    idleTimeout: 300, // 5 minutes
    backpressureLimit: 64 * 1024, // 64KB
    closeOnBackpressureLimit: false,
    perMessageDeflate: true,
    
    open(ws) {
      const { userId, sessionId } = ws.data;
      
      // Register connection
      connectionManager.addConnection(sessionId, ws);
      
      // Send initial connection confirmation
      ws.send(JSON.stringify({
        type: "connection_established",
        data: {
          sessionId,
          timestamp: new Date().toISOString()
        }
      }));
      
      // Notify presence system
      eventBroadcaster.broadcastUserPresence(userId, "online");
      
      console.log(`WebSocket connection opened: ${sessionId} (user: ${userId})`);
    },
    
    message(ws, message) {
      try {
        const data = JSON.parse(message.toString());
        handleWebSocketMessage(ws, data);
      } catch (error) {
        console.error("Invalid WebSocket message:", error);
        ws.send(JSON.stringify({
          type: "error",
          data: { message: "Invalid message format" }
        }));
      }
    },
    
    close(ws, code, message) {
      const { userId, sessionId } = ws.data;
      
      // Remove connection
      connectionManager.removeConnection(sessionId);
      
      // Update presence
      eventBroadcaster.broadcastUserPresence(userId, "offline");
      
      console.log(`WebSocket connection closed: ${sessionId} (code: ${code})`);
    },
    
    drain(ws) {
      console.log("WebSocket ready to receive more data");
    }
  }
});
```

### Connection Manager
```typescript
// websocket/connection-manager.ts
import { ServerWebSocket } from "bun";

interface WebSocketData {
  userId: string;
  sessionId: string;
  subscriptions: Set<string>;
}

export class ConnectionManager {
  private connections = new Map<string, ServerWebSocket<WebSocketData>>();
  private userConnections = new Map<string, Set<string>>();
  
  addConnection(sessionId: string, ws: ServerWebSocket<WebSocketData>) {
    this.connections.set(sessionId, ws);
    
    // Track user connections
    const userId = ws.data.userId;
    if (!this.userConnections.has(userId)) {
      this.userConnections.set(userId, new Set());
    }
    this.userConnections.get(userId)!.add(sessionId);
  }
  
  removeConnection(sessionId: string) {
    const ws = this.connections.get(sessionId);
    if (ws) {
      const userId = ws.data.userId;
      this.connections.delete(sessionId);
      
      // Update user connections
      const userSessions = this.userConnections.get(userId);
      if (userSessions) {
        userSessions.delete(sessionId);
        if (userSessions.size === 0) {
          this.userConnections.delete(userId);
        }
      }
    }
  }
  
  getConnection(sessionId: string): ServerWebSocket<WebSocketData> | undefined {
    return this.connections.get(sessionId);
  }
  
  getUserConnections(userId: string): ServerWebSocket<WebSocketData>[] {
    const sessionIds = this.userConnections.get(userId) || new Set();
    return Array.from(sessionIds)
      .map(sessionId => this.connections.get(sessionId))
      .filter(Boolean) as ServerWebSocket<WebSocketData>[];
  }
  
  getAllConnections(): ServerWebSocket<WebSocketData>[] {
    return Array.from(this.connections.values());
  }
  
  getConnectionCount(): number {
    return this.connections.size;
  }
  
  isUserOnline(userId: string): boolean {
    return this.userConnections.has(userId);
  }
}
```

### Event Broadcasting System
```typescript
// websocket/event-broadcaster.ts
import { ConnectionManager } from "./connection-manager";
import { EventEmitter } from "events";

export interface BroadcastEvent {
  type: string;
  data: any;
  timestamp: string;
  conversationId?: string;
  userId?: string;
}

export class EventBroadcaster extends EventEmitter {
  constructor(private connectionManager: ConnectionManager) {
    super();
  }
  
  // Broadcast to all connections
  broadcastToAll(event: BroadcastEvent) {
    const message = JSON.stringify(event);
    const connections = this.connectionManager.getAllConnections();
    
    connections.forEach(ws => {
      try {
        ws.send(message);
      } catch (error) {
        console.error("Failed to send message to connection:", error);
      }
    });
  }
  
  // Broadcast to specific conversation room
  broadcastToConversation(conversationId: string, event: BroadcastEvent) {
    const message = JSON.stringify({
      ...event,
      conversationId
    });
    
    const connections = this.connectionManager.getAllConnections();
    connections
      .filter(ws => ws.data.subscriptions.has(`conversation:${conversationId}`))
      .forEach(ws => {
        try {
          ws.send(message);
        } catch (error) {
          console.error("Failed to send conversation message:", error);
        }
      });
  }
  
  // Broadcast to specific user
  broadcastToUser(userId: string, event: BroadcastEvent) {
    const message = JSON.stringify(event);
    const userConnections = this.connectionManager.getUserConnections(userId);
    
    userConnections.forEach(ws => {
      try {
        ws.send(message);
      } catch (error) {
        console.error("Failed to send user message:", error);
      }
    });
  }
  
  // Specific event types
  broadcastNewMessage(conversationId: string, message: any) {
    this.broadcastToConversation(conversationId, {
      type: "new_message",
      data: message,
      timestamp: new Date().toISOString()
    });
  }
  
  broadcastConversationUpdate(conversationId: string, update: any) {
    this.broadcastToConversation(conversationId, {
      type: "conversation_updated",
      data: update,
      timestamp: new Date().toISOString()
    });
  }
  
  broadcastUserPresence(userId: string, status: "online" | "offline") {
    this.broadcastToAll({
      type: "user_presence",
      data: { userId, status },
      timestamp: new Date().toISOString(),
      userId
    });
  }
  
  broadcastTypingIndicator(conversationId: string, userId: string, isTyping: boolean) {
    this.broadcastToConversation(conversationId, {
      type: "typing_indicator",
      data: { userId, isTyping },
      timestamp: new Date().toISOString()
    });
  }
  
  broadcastFileProcessingUpdate(fileId: string, progress: number, status: string) {
    this.broadcastToAll({
      type: "file_processing_update",
      data: { fileId, progress, status },
      timestamp: new Date().toISOString()
    });
  }
}
```

### Message Handling
```typescript
// websocket/message-handlers.ts
import { ServerWebSocket } from "bun";
import { EventBroadcaster } from "./event-broadcaster";

interface WebSocketData {
  userId: string;
  sessionId: string;
  subscriptions: Set<string>;
}

export async function handleWebSocketMessage(
  ws: ServerWebSocket<WebSocketData>,
  message: any
) {
  const { type, data } = message;
  
  switch (type) {
    case "subscribe":
      await handleSubscribe(ws, data);
      break;
      
    case "unsubscribe":
      await handleUnsubscribe(ws, data);
      break;
      
    case "send_message":
      await handleSendMessage(ws, data);
      break;
      
    case "typing_start":
      await handleTypingStart(ws, data);
      break;
      
    case "typing_stop":
      await handleTypingStop(ws, data);
      break;
      
    case "ping":
      await handlePing(ws, data);
      break;
      
    default:
      ws.send(JSON.stringify({
        type: "error",
        data: { message: `Unknown message type: ${type}` }
      }));
  }
}

async function handleSubscribe(ws: ServerWebSocket<WebSocketData>, data: any) {
  const { channel } = data;
  
  if (!channel) {
    ws.send(JSON.stringify({
      type: "error",
      data: { message: "Channel is required for subscription" }
    }));
    return;
  }
  
  ws.data.subscriptions.add(channel);
  
  ws.send(JSON.stringify({
    type: "subscription_confirmed",
    data: { channel }
  }));
}

async function handleUnsubscribe(ws: ServerWebSocket<WebSocketData>, data: any) {
  const { channel } = data;
  
  if (channel) {
    ws.data.subscriptions.delete(channel);
  }
  
  ws.send(JSON.stringify({
    type: "unsubscription_confirmed",
    data: { channel }
  }));
}

async function handleSendMessage(ws: ServerWebSocket<WebSocketData>, data: any) {
  const { conversationId, content } = data;
  
  if (!conversationId || !content) {
    ws.send(JSON.stringify({
      type: "error",
      data: { message: "ConversationId and content are required" }
    }));
    return;
  }
  
  // Process message through API
  try {
    const response = await fetch(`http://localhost:3001/api/conversations/${conversationId}/messages`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${await getTokenForUser(ws.data.userId)}`
      },
      body: JSON.stringify({
        content,
        role: "user",
        metadata: { source: "websocket" }
      })
    });
    
    if (response.ok) {
      const message = await response.json();
      // Message will be broadcast via API event hooks
    } else {
      throw new Error(`Failed to send message: ${response.status}`);
    }
  } catch (error) {
    ws.send(JSON.stringify({
      type: "error",
      data: { message: "Failed to send message" }
    }));
  }
}

async function handleTypingStart(ws: ServerWebSocket<WebSocketData>, data: any) {
  const { conversationId } = data;
  const eventBroadcaster = new EventBroadcaster(connectionManager);
  
  eventBroadcaster.broadcastTypingIndicator(conversationId, ws.data.userId, true);
}

async function handleTypingStop(ws: ServerWebSocket<WebSocketData>, data: any) {
  const { conversationId } = data;
  const eventBroadcaster = new EventBroadcaster(connectionManager);
  
  eventBroadcaster.broadcastTypingIndicator(conversationId, ws.data.userId, false);
}

async function handlePing(ws: ServerWebSocket<WebSocketData>, data: any) {
  ws.send(JSON.stringify({
    type: "pong",
    data: { timestamp: new Date().toISOString() }
  }));
}
```

### Client-Side WebSocket Implementation
```typescript
// client/websocket-client.ts
export class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private eventHandlers = new Map<string, Function[]>();
  
  constructor(
    private url: string,
    private token: string
  ) {}
  
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(`${this.url}?token=${this.token}`);
        
        this.ws.onopen = () => {
          console.log("WebSocket connected");
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          resolve();
        };
        
        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error("Failed to parse WebSocket message:", error);
          }
        };
        
        this.ws.onclose = (event) => {
          console.log("WebSocket disconnected:", event.code);
          this.stopHeartbeat();
          
          if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
          }
        };
        
        this.ws.onerror = (error) => {
          console.error("WebSocket error:", error);
          reject(error);
        };
        
      } catch (error) {
        reject(error);
      }
    });
  }
  
  disconnect() {
    if (this.ws) {
      this.ws.close(1000, "Client disconnect");
      this.ws = null;
    }
    this.stopHeartbeat();
  }
  
  send(type: string, data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, data }));
    } else {
      console.warn("WebSocket not connected, message queued");
      // TODO: Implement message queuing
    }
  }
  
  subscribe(channel: string) {
    this.send("subscribe", { channel });
  }
  
  unsubscribe(channel: string) {
    this.send("unsubscribe", { channel });
  }
  
  on(eventType: string, handler: Function) {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, []);
    }
    this.eventHandlers.get(eventType)!.push(handler);
  }
  
  off(eventType: string, handler: Function) {
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }
  
  private handleMessage(message: any) {
    const { type, data } = message;
    const handlers = this.eventHandlers.get(type) || [];
    
    handlers.forEach(handler => {
      try {
        handler(data);
      } catch (error) {
        console.error("Error in event handler:", error);
      }
    });
  }
  
  private scheduleReconnect() {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`Scheduling reconnect attempt ${this.reconnectAttempts} in ${delay}ms`);
    
    setTimeout(() => {
      this.connect().catch(error => {
        console.error("Reconnect failed:", error);
      });
    }, delay);
  }
  
  private startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      this.send("ping", { timestamp: Date.now() });
    }, 30000); // 30 seconds
  }
  
  private stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }
}
```

## Performance Requirements
- **Connection Capacity**: Support 1000+ concurrent WebSocket connections
- **Message Latency**: Real-time messages delivered within 50ms
- **Memory Usage**: Efficient connection tracking with minimal memory overhead
- **Throughput**: Handle 10,000 messages per second
- **Connection Recovery**: Automatic reconnection within 5 seconds

## Acceptance Criteria
- [ ] WebSocket server integrated with Bun.serve()
- [ ] Connection management and user tracking
- [ ] Room-based subscription system for conversations
- [ ] Real-time message broadcasting
- [ ] Client-side WebSocket integration with reconnection
- [ ] Authentication integration for WebSocket connections
- [ ] Typing indicators and presence system
- [ ] File processing progress updates
- [ ] Comprehensive error handling and recovery
- [ ] Performance testing meets requirements

## Testing Procedures
1. **Connection Testing**: Test WebSocket connection establishment and cleanup
2. **Load Testing**: Verify performance with 1000+ concurrent connections
3. **Message Testing**: Test message delivery and ordering
4. **Reconnection Testing**: Test automatic reconnection scenarios
5. **Integration Testing**: Test with existing API endpoints

## Integration Points
- **Week 5**: Backend API for message processing
- **Week 7**: Frontend real-time UI components
- **Week 9**: Analytics real-time data streaming

## Security Considerations
- Token-based authentication for WebSocket connections
- Rate limiting for message sending
- Input validation for all WebSocket messages
- Connection cleanup to prevent memory leaks

## Monitoring & Logging
- Connection metrics (count, duration, errors)
- Message throughput and latency monitoring
- Memory usage tracking
- Error rate monitoring with alerting