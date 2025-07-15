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

## Advanced WebSocket Features

### Authentication Middleware
```typescript
// websocket/middleware/auth.ts
import { verify } from "jsonwebtoken";
import { UserRepository } from "../repositories/user-repository";

export interface AuthResult {
  success: boolean;
  userId?: string;
  sessionId?: string;
  error?: string;
}

export async function authWS(request: Request): Promise<AuthResult> {
  try {
    const url = new URL(request.url);
    const token = url.searchParams.get("token");
    
    if (!token) {
      return { success: false, error: "No token provided" };
    }
    
    const decoded = verify(token, process.env.JWT_SECRET!) as any;
    const userRepo = new UserRepository();
    const user = await userRepo.findById(decoded.userId);
    
    if (!user) {
      return { success: false, error: "User not found" };
    }
    
    return {
      success: true,
      userId: user.id,
      sessionId: generateSessionId()
    };
  } catch (error) {
    return { success: false, error: "Invalid token" };
  }
}

function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}
```

### Rate Limiting for WebSocket Messages
```typescript
// websocket/middleware/rate-limiter.ts
import { ServerWebSocket } from "bun";

interface RateLimitData {
  count: number;
  resetTime: number;
}

export class WebSocketRateLimiter {
  private limits = new Map<string, RateLimitData>();
  private readonly maxRequests = 100; // per minute
  private readonly windowMs = 60000; // 1 minute
  
  checkLimit(userId: string): boolean {
    const now = Date.now();
    const userLimit = this.limits.get(userId);
    
    if (!userLimit || now > userLimit.resetTime) {
      this.limits.set(userId, {
        count: 1,
        resetTime: now + this.windowMs
      });
      return true;
    }
    
    if (userLimit.count >= this.maxRequests) {
      return false;
    }
    
    userLimit.count++;
    return true;
  }
  
  resetLimit(userId: string) {
    this.limits.delete(userId);
  }
  
  // Clean up expired limits
  cleanup() {
    const now = Date.now();
    for (const [userId, limit] of this.limits.entries()) {
      if (now > limit.resetTime) {
        this.limits.delete(userId);
      }
    }
  }
}

export const rateLimiter = new WebSocketRateLimiter();

// Run cleanup every minute
setInterval(() => rateLimiter.cleanup(), 60000);
```

### Message Validation and Sanitization
```typescript
// websocket/middleware/validation.ts
import { z } from "zod";

const MessageSchema = z.object({
  type: z.enum([
    "subscribe", "unsubscribe", "send_message", 
    "typing_start", "typing_stop", "ping"
  ]),
  data: z.object({
    channel: z.string().optional(),
    conversationId: z.string().uuid().optional(),
    content: z.string().max(10000).optional(),
    timestamp: z.number().optional()
  })
});

export function validateMessage(message: any): { valid: boolean; error?: string; data?: any } {
  try {
    const parsed = MessageSchema.parse(message);
    return { valid: true, data: parsed };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return { valid: false, error: error.errors.map(e => e.message).join(", ") };
    }
    return { valid: false, error: "Invalid message format" };
  }
}

export function sanitizeContent(content: string): string {
  // Remove potentially harmful content
  return content
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "")
    .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, "")
    .replace(/javascript:/gi, "")
    .trim();
}
```

### Enhanced Connection Management with Clustering
```typescript
// websocket/cluster-manager.ts
import { EventEmitter } from "events";
import { Redis } from "ioredis";

export class ClusterManager extends EventEmitter {
  private redis: Redis;
  private nodeId: string;
  private heartbeatInterval: NodeJS.Timeout;
  
  constructor() {
    super();
    this.redis = new Redis({
      host: process.env.REDIS_HOST || "localhost",
      port: parseInt(process.env.REDIS_PORT || "6379")
    });
    this.nodeId = `node_${process.pid}_${Date.now()}`;
    this.startHeartbeat();
  }
  
  // Broadcast message across cluster
  async broadcastToCluster(channel: string, message: any) {
    await this.redis.publish(`cluster:${channel}`, JSON.stringify({
      nodeId: this.nodeId,
      timestamp: Date.now(),
      data: message
    }));
  }
  
  // Subscribe to cluster messages
  subscribeToCluster(channel: string, handler: (message: any) => void) {
    const subscriber = this.redis.duplicate();
    subscriber.subscribe(`cluster:${channel}`);
    
    subscriber.on("message", (channel, message) => {
      try {
        const parsed = JSON.parse(message);
        // Don't process messages from this node
        if (parsed.nodeId !== this.nodeId) {
          handler(parsed.data);
        }
      } catch (error) {
        console.error("Failed to parse cluster message:", error);
      }
    });
  }
  
  // Register node presence
  async registerNode() {
    await this.redis.setex(
      `nodes:${this.nodeId}`, 
      30, // 30 seconds TTL
      JSON.stringify({
        nodeId: this.nodeId,
        timestamp: Date.now(),
        connections: 0 // Updated by connection manager
      })
    );
  }
  
  // Get all active nodes
  async getActiveNodes(): Promise<string[]> {
    const keys = await this.redis.keys("nodes:*");
    return keys.map(key => key.replace("nodes:", ""));
  }
  
  private startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      this.registerNode();
    }, 15000); // Every 15 seconds
  }
  
  async shutdown() {
    clearInterval(this.heartbeatInterval);
    await this.redis.del(`nodes:${this.nodeId}`);
    this.redis.disconnect();
  }
}
```

### WebSocket Connection Pooling
```typescript
// websocket/connection-pool.ts
import { ServerWebSocket } from "bun";

interface PooledConnection {
  ws: ServerWebSocket<any>;
  lastActivity: number;
  subscriptions: Set<string>;
  metadata: Record<string, any>;
}

export class ConnectionPool {
  private connections = new Map<string, PooledConnection>();
  private userConnections = new Map<string, Set<string>>();
  private roomConnections = new Map<string, Set<string>>();
  private cleanupInterval: NodeJS.Timeout;
  
  constructor(private maxConnections = 10000) {
    this.startCleanup();
  }
  
  addConnection(sessionId: string, ws: ServerWebSocket<any>) {
    if (this.connections.size >= this.maxConnections) {
      this.evictOldestConnection();
    }
    
    const connection: PooledConnection = {
      ws,
      lastActivity: Date.now(),
      subscriptions: new Set(),
      metadata: {}
    };
    
    this.connections.set(sessionId, connection);
    this.trackUserConnection(ws.data.userId, sessionId);
  }
  
  removeConnection(sessionId: string) {
    const connection = this.connections.get(sessionId);
    if (connection) {
      // Remove from user tracking
      const userId = connection.ws.data.userId;
      const userSessions = this.userConnections.get(userId);
      if (userSessions) {
        userSessions.delete(sessionId);
        if (userSessions.size === 0) {
          this.userConnections.delete(userId);
        }
      }
      
      // Remove from room subscriptions
      connection.subscriptions.forEach(room => {
        const roomSessions = this.roomConnections.get(room);
        if (roomSessions) {
          roomSessions.delete(sessionId);
          if (roomSessions.size === 0) {
            this.roomConnections.delete(room);
          }
        }
      });
      
      this.connections.delete(sessionId);
    }
  }
  
  subscribeToRoom(sessionId: string, room: string) {
    const connection = this.connections.get(sessionId);
    if (connection) {
      connection.subscriptions.add(room);
      connection.lastActivity = Date.now();
      
      if (!this.roomConnections.has(room)) {
        this.roomConnections.set(room, new Set());
      }
      this.roomConnections.get(room)!.add(sessionId);
    }
  }
  
  unsubscribeFromRoom(sessionId: string, room: string) {
    const connection = this.connections.get(sessionId);
    if (connection) {
      connection.subscriptions.delete(room);
      
      const roomSessions = this.roomConnections.get(room);
      if (roomSessions) {
        roomSessions.delete(sessionId);
        if (roomSessions.size === 0) {
          this.roomConnections.delete(room);
        }
      }
    }
  }
  
  broadcastToRoom(room: string, message: string, excludeSessionId?: string) {
    const roomSessions = this.roomConnections.get(room);
    if (roomSessions) {
      roomSessions.forEach(sessionId => {
        if (sessionId !== excludeSessionId) {
          const connection = this.connections.get(sessionId);
          if (connection && connection.ws.readyState === 1) {
            connection.ws.send(message);
            connection.lastActivity = Date.now();
          }
        }
      });
    }
  }
  
  getUserConnections(userId: string): PooledConnection[] {
    const sessionIds = this.userConnections.get(userId) || new Set();
    return Array.from(sessionIds)
      .map(sessionId => this.connections.get(sessionId))
      .filter(Boolean) as PooledConnection[];
  }
  
  updateActivity(sessionId: string) {
    const connection = this.connections.get(sessionId);
    if (connection) {
      connection.lastActivity = Date.now();
    }
  }
  
  getStats() {
    return {
      totalConnections: this.connections.size,
      activeUsers: this.userConnections.size,
      activeRooms: this.roomConnections.size,
      maxConnections: this.maxConnections
    };
  }
  
  private trackUserConnection(userId: string, sessionId: string) {
    if (!this.userConnections.has(userId)) {
      this.userConnections.set(userId, new Set());
    }
    this.userConnections.get(userId)!.add(sessionId);
  }
  
  private evictOldestConnection() {
    let oldestSessionId: string | null = null;
    let oldestTime = Date.now();
    
    for (const [sessionId, connection] of this.connections) {
      if (connection.lastActivity < oldestTime) {
        oldestTime = connection.lastActivity;
        oldestSessionId = sessionId;
      }
    }
    
    if (oldestSessionId) {
      console.log(`Evicting oldest connection: ${oldestSessionId}`);
      const connection = this.connections.get(oldestSessionId);
      if (connection) {
        connection.ws.close(1000, "Connection evicted");
        this.removeConnection(oldestSessionId);
      }
    }
  }
  
  private startCleanup() {
    this.cleanupInterval = setInterval(() => {
      const now = Date.now();
      const timeout = 5 * 60 * 1000; // 5 minutes
      
      for (const [sessionId, connection] of this.connections) {
        if (now - connection.lastActivity > timeout) {
          console.log(`Cleaning up inactive connection: ${sessionId}`);
          connection.ws.close(1000, "Connection timeout");
          this.removeConnection(sessionId);
        }
      }
    }, 60000); // Run every minute
  }
  
  shutdown() {
    clearInterval(this.cleanupInterval);
    this.connections.forEach(connection => {
      connection.ws.close(1000, "Server shutdown");
    });
    this.connections.clear();
    this.userConnections.clear();
    this.roomConnections.clear();
  }
}
```

### Performance Monitoring and Metrics
```typescript
// websocket/monitoring.ts
import { EventEmitter } from "events";

export interface WebSocketMetrics {
  connections: {
    current: number;
    peak: number;
    total: number;
  };
  messages: {
    sent: number;
    received: number;
    errors: number;
  };
  latency: {
    average: number;
    p95: number;
    p99: number;
  };
  memory: {
    usage: number;
    peak: number;
  };
}

export class WebSocketMonitor extends EventEmitter {
  private metrics: WebSocketMetrics = {
    connections: { current: 0, peak: 0, total: 0 },
    messages: { sent: 0, received: 0, errors: 0 },
    latency: { average: 0, p95: 0, p99: 0 },
    memory: { usage: 0, peak: 0 }
  };
  
  private latencyBuffer: number[] = [];
  private bufferSize = 1000;
  
  recordConnection() {
    this.metrics.connections.current++;
    this.metrics.connections.total++;
    
    if (this.metrics.connections.current > this.metrics.connections.peak) {
      this.metrics.connections.peak = this.metrics.connections.current;
    }
    
    this.emit("connection", this.metrics.connections);
  }
  
  recordDisconnection() {
    this.metrics.connections.current--;
    this.emit("disconnection", this.metrics.connections);
  }
  
  recordMessageSent() {
    this.metrics.messages.sent++;
    this.emit("message_sent", this.metrics.messages);
  }
  
  recordMessageReceived() {
    this.metrics.messages.received++;
    this.emit("message_received", this.metrics.messages);
  }
  
  recordError() {
    this.metrics.messages.errors++;
    this.emit("error", this.metrics.messages);
  }
  
  recordLatency(latency: number) {
    this.latencyBuffer.push(latency);
    
    if (this.latencyBuffer.length > this.bufferSize) {
      this.latencyBuffer.shift();
    }
    
    this.calculateLatencyMetrics();
  }
  
  recordMemoryUsage() {
    const usage = process.memoryUsage();
    this.metrics.memory.usage = usage.heapUsed;
    
    if (usage.heapUsed > this.metrics.memory.peak) {
      this.metrics.memory.peak = usage.heapUsed;
    }
    
    this.emit("memory", this.metrics.memory);
  }
  
  getMetrics(): WebSocketMetrics {
    return { ...this.metrics };
  }
  
  private calculateLatencyMetrics() {
    if (this.latencyBuffer.length === 0) return;
    
    const sorted = [...this.latencyBuffer].sort((a, b) => a - b);
    const sum = sorted.reduce((acc, val) => acc + val, 0);
    
    this.metrics.latency.average = sum / sorted.length;
    this.metrics.latency.p95 = sorted[Math.floor(sorted.length * 0.95)];
    this.metrics.latency.p99 = sorted[Math.floor(sorted.length * 0.99)];
  }
  
  startPeriodicReporting(intervalMs = 30000) {
    setInterval(() => {
      this.recordMemoryUsage();
      this.emit("metrics", this.getMetrics());
    }, intervalMs);
  }
}

export const monitor = new WebSocketMonitor();
```

### Client-Side Reconnection with Exponential Backoff
```typescript
// client/enhanced-websocket-client.ts
export interface WebSocketClientOptions {
  url: string;
  token: string;
  maxReconnectAttempts?: number;
  initialReconnectDelay?: number;
  maxReconnectDelay?: number;
  heartbeatInterval?: number;
  messageQueueSize?: number;
}

export class EnhancedWebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private messageQueue: Array<{ type: string; data: any }> = [];
  private eventHandlers = new Map<string, Function[]>();
  private connectionState: 'connecting' | 'connected' | 'disconnected' | 'reconnecting' = 'disconnected';
  
  constructor(private options: WebSocketClientOptions) {
    this.options = {
      maxReconnectAttempts: 5,
      initialReconnectDelay: 1000,
      maxReconnectDelay: 30000,
      heartbeatInterval: 30000,
      messageQueueSize: 100,
      ...options
    };
  }
  
  async connect(): Promise<void> {
    if (this.connectionState === 'connecting' || this.connectionState === 'connected') {
      return;
    }
    
    this.connectionState = 'connecting';
    this.emit('connecting');
    
    return new Promise((resolve, reject) => {
      try {
        const url = new URL(this.options.url);
        url.searchParams.set('token', this.options.token);
        
        this.ws = new WebSocket(url.toString());
        
        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.connectionState = 'connected';
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          this.flushMessageQueue();
          this.emit('connected');
          resolve();
        };
        
        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Failed to parse message:', error);
            this.emit('error', error);
          }
        };
        
        this.ws.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason);
          this.connectionState = 'disconnected';
          this.stopHeartbeat();
          this.emit('disconnected', { code: event.code, reason: event.reason });
          
          if (event.code !== 1000 && this.reconnectAttempts < this.options.maxReconnectAttempts!) {
            this.scheduleReconnect();
          }
        };
        
        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.emit('error', error);
          reject(error);
        };
        
        // Connection timeout
        setTimeout(() => {
          if (this.connectionState === 'connecting') {
            this.ws?.close();
            reject(new Error('Connection timeout'));
          }
        }, 10000);
        
      } catch (error) {
        this.connectionState = 'disconnected';
        reject(error);
      }
    });
  }
  
  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
    }
    
    this.connectionState = 'disconnected';
    this.stopHeartbeat();
    this.emit('disconnected', { code: 1000, reason: 'Client disconnect' });
  }
  
  send(type: string, data: any) {
    const message = { type, data };
    
    if (this.connectionState === 'connected' && this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      this.queueMessage(message);
    }
  }
  
  subscribe(channel: string) {
    this.send('subscribe', { channel });
  }
  
  unsubscribe(channel: string) {
    this.send('unsubscribe', { channel });
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
  
  getConnectionState(): string {
    return this.connectionState;
  }
  
  private handleMessage(message: any) {
    const { type, data } = message;
    
    // Handle pong responses
    if (type === 'pong') {
      return;
    }
    
    this.emit(type, data);
  }
  
  private emit(eventType: string, data?: any) {
    const handlers = this.eventHandlers.get(eventType) || [];
    handlers.forEach(handler => {
      try {
        handler(data);
      } catch (error) {
        console.error('Error in event handler:', error);
      }
    });
  }
  
  private scheduleReconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }
    
    this.reconnectAttempts++;
    this.connectionState = 'reconnecting';
    
    const delay = Math.min(
      this.options.initialReconnectDelay! * Math.pow(2, this.reconnectAttempts - 1),
      this.options.maxReconnectDelay!
    );
    
    console.log(`Scheduling reconnect attempt ${this.reconnectAttempts} in ${delay}ms`);
    this.emit('reconnecting', { attempt: this.reconnectAttempts, delay });
    
    this.reconnectTimer = setTimeout(() => {
      this.connect().catch(error => {
        console.error('Reconnect failed:', error);
        if (this.reconnectAttempts < this.options.maxReconnectAttempts!) {
          this.scheduleReconnect();
        } else {
          this.emit('max_reconnect_attempts');
        }
      });
    }, delay);
  }
  
  private startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      if (this.connectionState === 'connected') {
        this.send('ping', { timestamp: Date.now() });
      }
    }, this.options.heartbeatInterval!);
  }
  
  private stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }
  
  private queueMessage(message: { type: string; data: any }) {
    if (this.messageQueue.length >= this.options.messageQueueSize!) {
      this.messageQueue.shift(); // Remove oldest message
    }
    
    this.messageQueue.push(message);
  }
  
  private flushMessageQueue() {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift()!;
      this.send(message.type, message.data);
    }
  }
}
```

### Vue.js Integration Example
```vue
<!-- frontend/components/WebSocketManager.vue -->
<template>
  <div class="ws-status">
    <div class="status-indicator" :class="connectionState">
      <span class="dot"></span>
      {{ connectionState }}
    </div>
    <div v-if="connectionState === 'reconnecting'" class="reconnect-info">
      Reconnecting... ({{ reconnectAttempt }}/{{ maxReconnectAttempts }})
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { EnhancedWebSocketClient } from '../utils/websocket-client';

const connectionState = ref('disconnected');
const reconnectAttempt = ref(0);
const maxReconnectAttempts = ref(5);

let wsClient: EnhancedWebSocketClient | null = null;

const emit = defineEmits(['message', 'connected', 'disconnected', 'error']);

onMounted(async () => {
  const token = localStorage.getItem('auth_token');
  if (!token) {
    emit('error', new Error('No authentication token found'));
    return;
  }
  
  wsClient = new EnhancedWebSocketClient({
    url: 'ws://localhost:3002/ws',
    token,
    maxReconnectAttempts: 5,
    initialReconnectDelay: 1000,
    maxReconnectDelay: 30000,
    heartbeatInterval: 30000
  });
  
  // Event handlers
  wsClient.on('connecting', () => {
    connectionState.value = 'connecting';
  });
  
  wsClient.on('connected', () => {
    connectionState.value = 'connected';
    emit('connected');
  });
  
  wsClient.on('disconnected', (data) => {
    connectionState.value = 'disconnected';
    emit('disconnected', data);
  });
  
  wsClient.on('reconnecting', (data) => {
    connectionState.value = 'reconnecting';
    reconnectAttempt.value = data.attempt;
  });
  
  wsClient.on('max_reconnect_attempts', () => {
    emit('error', new Error('Max reconnection attempts reached'));
  });
  
  wsClient.on('error', (error) => {
    emit('error', error);
  });
  
  // Message handlers
  wsClient.on('new_message', (data) => {
    emit('message', { type: 'new_message', data });
  });
  
  wsClient.on('conversation_updated', (data) => {
    emit('message', { type: 'conversation_updated', data });
  });
  
  wsClient.on('user_presence', (data) => {
    emit('message', { type: 'user_presence', data });
  });
  
  wsClient.on('typing_indicator', (data) => {
    emit('message', { type: 'typing_indicator', data });
  });
  
  try {
    await wsClient.connect();
  } catch (error) {
    emit('error', error);
  }
});

onUnmounted(() => {
  if (wsClient) {
    wsClient.disconnect();
  }
});

// Expose methods for parent components
defineExpose({
  send: (type: string, data: any) => wsClient?.send(type, data),
  subscribe: (channel: string) => wsClient?.subscribe(channel),
  unsubscribe: (channel: string) => wsClient?.unsubscribe(channel),
  getConnectionState: () => wsClient?.getConnectionState()
});
</script>

<style scoped>
.ws-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  font-size: 12px;
  border-radius: 4px;
  background: #f8f9fa;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #6c757d;
}

.connected .dot {
  background: #28a745;
}

.connecting .dot {
  background: #ffc107;
  animation: pulse 1s infinite;
}

.reconnecting .dot {
  background: #fd7e14;
  animation: pulse 1s infinite;
}

.disconnected .dot {
  background: #dc3545;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.reconnect-info {
  color: #fd7e14;
  font-size: 11px;
}
</style>
```

## Security Considerations

### Comprehensive Security Measures
- **Authentication**: JWT token-based authentication with token validation
- **Authorization**: Role-based access control for different WebSocket channels
- **Rate Limiting**: Per-user message rate limiting to prevent spam
- **Input Validation**: Schema validation for all incoming messages
- **Content Sanitization**: XSS prevention for message content
- **Connection Limits**: Maximum connection limits per user and globally
- **Secure Headers**: Proper CORS and security headers
- **Encryption**: TLS/SSL for production WebSocket connections
- **Session Management**: Secure session handling with proper cleanup
- **Audit Logging**: Security event logging and monitoring

### Additional Security Headers
```typescript
// websocket/security.ts
export function addSecurityHeaders(response: Response): Response {
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-XSS-Protection', '1; mode=block');
  response.headers.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  response.headers.set('Content-Security-Policy', "default-src 'self'");
  return response;
}
```

## Monitoring & Logging

### Comprehensive Monitoring System
```typescript
// websocket/logger.ts
import { createLogger, format, transports } from 'winston';

export const wsLogger = createLogger({
  level: 'info',
  format: format.combine(
    format.timestamp(),
    format.errors({ stack: true }),
    format.json()
  ),
  defaultMeta: { service: 'websocket-server' },
  transports: [
    new transports.File({ filename: 'logs/websocket-error.log', level: 'error' }),
    new transports.File({ filename: 'logs/websocket-combined.log' }),
    new transports.Console({
      format: format.combine(
        format.colorize(),
        format.simple()
      )
    })
  ]
});

// Metrics collection
export interface WebSocketMetrics {
  connectionsPerSecond: number;
  messagesPerSecond: number;
  averageLatency: number;
  errorRate: number;
  memoryUsage: number;
}

export function collectMetrics(): WebSocketMetrics {
  return {
    connectionsPerSecond: monitor.getConnectionRate(),
    messagesPerSecond: monitor.getMessageRate(),
    averageLatency: monitor.getAverageLatency(),
    errorRate: monitor.getErrorRate(),
    memoryUsage: process.memoryUsage().heapUsed
  };
}
```

### Alerting System
```typescript
// websocket/alerting.ts
export class AlertingSystem {
  private thresholds = {
    maxConnections: 1000,
    maxLatency: 1000, // ms
    maxErrorRate: 0.05, // 5%
    maxMemoryUsage: 1024 * 1024 * 1024 // 1GB
  };
  
  checkAlerts(metrics: WebSocketMetrics) {
    if (metrics.connectionsPerSecond > this.thresholds.maxConnections) {
      this.sendAlert('High connection rate', metrics);
    }
    
    if (metrics.averageLatency > this.thresholds.maxLatency) {
      this.sendAlert('High latency detected', metrics);
    }
    
    if (metrics.errorRate > this.thresholds.maxErrorRate) {
      this.sendAlert('High error rate', metrics);
    }
    
    if (metrics.memoryUsage > this.thresholds.maxMemoryUsage) {
      this.sendAlert('High memory usage', metrics);
    }
  }
  
  private sendAlert(message: string, metrics: WebSocketMetrics) {
    // Implement alerting logic (email, Slack, etc.)
    console.error(`ALERT: ${message}`, metrics);
  }
}
```