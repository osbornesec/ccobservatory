# Week 6: WebSocket Implementation for Real-Time Communication - Enhanced Version

## Overview
Implement real-time WebSocket communication using Bun's native WebSocket support for live conversation monitoring, real-time updates, and collaborative features. This week focuses on bidirectional communication, event broadcasting, and connection management with enterprise-grade security, performance, and scalability.

## Team Assignments
- **Backend Lead**: WebSocket server implementation, event system architecture
- **Full-Stack Developer**: Client-side WebSocket integration, real-time UI updates
- **Frontend Developer**: Real-time component development, state synchronization

## Daily Schedule

### Monday: WebSocket Server Foundation
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Advanced Bun WebSocket server configuration with security headers
- **10:30-12:00**: Connection management with pooling and rate limiting

#### Afternoon (4 hours)
- **13:00-15:00**: Enhanced message routing and event handling with validation
- **15:00-17:00**: Multi-layer authentication integration for WebSocket connections

### Tuesday: Event System & Broadcasting
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Event system architecture with message queuing
- **10:30-12:00**: Room-based broadcasting with clustering support

#### Afternoon (4 hours)
- **13:00-15:00**: Real-time conversation updates with conflict resolution
- **15:00-17:00**: Message broadcasting with delivery guarantees

### Wednesday: Client-Side Integration
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Enhanced JavaScript WebSocket client with reconnection
- **10:30-12:00**: Connection state management and message queuing

#### Afternoon (4 hours)
- **13:00-15:00**: Event handling and optimistic UI updates
- **15:00-17:00**: Comprehensive error handling and connection recovery

### Thursday: Advanced Features
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Presence system with online status and typing indicators
- **10:30-12:00**: Real-time analytics with performance monitoring

#### Afternoon (4 hours)
- **13:00-15:00**: File upload progress and processing updates
- **15:00-17:00**: Collaborative features with operational transformation

### Friday: Testing & Performance Optimization
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Load testing with 10,000+ concurrent connections
- **10:30-12:00**: Memory optimization and connection cleanup

#### Afternoon (4 hours)
- **13:00-15:00**: Performance profiling and message compression
- **15:00-17:00**: End-to-end integration testing with API endpoints

## Technical Implementation Details

### Enhanced WebSocket Server Configuration
```typescript
// websocket/server.ts
import { serve, ServerWebSocket } from "bun";
import { EventEmitter } from "events";
import { wsAuthenticator } from "./middleware/auth";
import { ConnectionPool } from "./connection-pool";
import { EventBroadcaster } from "./event-broadcaster";
import { rateLimiter } from "./middleware/rate-limiter";
import { validateMessage, sanitizeContent } from "./middleware/validation";
import { WebSocketMonitor } from "./monitoring";
import { wsLogger } from "./logger";

interface WebSocketData {
  userId: string;
  sessionId: string;
  subscriptions: Set<string>;
  userRole: string;
  permissions: string[];
  lastActivity: number;
}

const connectionPool = new ConnectionPool();
const eventBroadcaster = new EventBroadcaster(connectionPool);
const monitor = new WebSocketMonitor();

export const websocketServer = serve<WebSocketData>({
  port: process.env.WS_PORT || 3002,
  
  fetch(req, server) {
    const url = new URL(req.url);
    
    if (url.pathname === "/ws") {
      return handleWebSocketUpgrade(req, server);
    }
    
    if (url.pathname === "/health") {
      return new Response(JSON.stringify({
        status: "healthy",
        connections: connectionPool.getStats(),
        uptime: process.uptime()
      }), {
        headers: { "Content-Type": "application/json" }
      });
    }
    
    return new Response("WebSocket endpoint not found", { status: 404 });
  },
  
  websocket: {
    maxPayloadLength: 16 * 1024 * 1024, // 16MB
    idleTimeout: 300, // 5 minutes
    backpressureLimit: 64 * 1024, // 64KB
    closeOnBackpressureLimit: false,
    perMessageDeflate: true,
    compression: 'gzip',
    
    open(ws) {
      const { userId, sessionId } = ws.data;
      
      // Add to connection pool
      connectionPool.addConnection(sessionId, ws);
      
      // Record metrics
      monitor.recordConnection();
      
      // Send initial connection confirmation
      ws.send(JSON.stringify({
        type: "connection_established",
        data: {
          sessionId,
          timestamp: new Date().toISOString(),
          serverVersion: "1.0.0"
        }
      }));
      
      // Broadcast presence
      eventBroadcaster.broadcastUserPresence(userId, "online");
      
      wsLogger.info("WebSocket connection opened", {
        sessionId,
        userId,
        userRole: ws.data.userRole
      });
    },
    
    message(ws, message) {
      const startTime = Date.now();
      
      try {
        const { userId, sessionId } = ws.data;
        
        // Update activity timestamp
        connectionPool.updateActivity(sessionId);
        
        // Check rate limits
        if (!rateLimiter.checkMessageLimit(userId)) {
          ws.send(JSON.stringify({
            type: "error",
            data: { message: "Rate limit exceeded" }
          }));
          return;
        }
        
        if (!rateLimiter.checkBurstLimit(userId)) {
          ws.send(JSON.stringify({
            type: "error", 
            data: { message: "Burst limit exceeded" }
          }));
          return;
        }
        
        const data = JSON.parse(message.toString());
        
        // Validate message structure
        const validation = validateMessage(data);
        if (!validation.valid) {
          ws.send(JSON.stringify({
            type: "error",
            data: { message: validation.error }
          }));
          return;
        }
        
        // Handle message
        handleWebSocketMessage(ws, validation.data!);
        
        // Record metrics
        monitor.recordMessageReceived();
        monitor.recordLatency(Date.now() - startTime);
        
      } catch (error) {
        wsLogger.error("Message handling error", { error: error.message });
        monitor.recordError();
        
        ws.send(JSON.stringify({
          type: "error",
          data: { message: "Invalid message format" }
        }));
      }
    },
    
    close(ws, code, message) {
      const { userId, sessionId } = ws.data;
      
      // Remove from connection pool
      connectionPool.removeConnection(sessionId);
      
      // Record metrics
      monitor.recordDisconnection();
      
      // Update presence
      eventBroadcaster.broadcastUserPresence(userId, "offline");
      
      wsLogger.info("WebSocket connection closed", {
        sessionId,
        userId,
        code,
        reason: message?.toString()
      });
    },
    
    drain(ws) {
      wsLogger.debug("WebSocket ready to receive more data", {
        sessionId: ws.data.sessionId
      });
    }
  }
});

async function handleWebSocketUpgrade(req: Request, server: any) {
  // Authenticate connection
  const authResult = await wsAuthenticator.authenticateConnection(req);
  if (!authResult.success) {
    return new Response("Unauthorized", { status: 401 });
  }
  
  const upgraded = server.upgrade(req, {
    data: {
      userId: authResult.userId!,
      sessionId: authResult.sessionId!,
      subscriptions: new Set<string>(),
      userRole: authResult.userRole!,
      permissions: authResult.permissions!,
      lastActivity: Date.now()
    }
  });
  
  return upgraded ? undefined : new Response("Upgrade failed", { status: 400 });
}

// Start monitoring
monitor.startPeriodicReporting();

wsLogger.info("WebSocket server started", {
  port: process.env.WS_PORT || 3002,
  environment: process.env.NODE_ENV || "development"
});
```

### Advanced Authentication Middleware
```typescript
// websocket/middleware/auth.ts
import { verify } from "jsonwebtoken";
import { UserRepository } from "../repositories/user-repository";
import { RateLimiter } from "./rate-limiter";
import { wsLogger } from "../logger";

export interface AuthResult {
  success: boolean;
  userId?: string;
  sessionId?: string;
  userRole?: string;
  permissions?: string[];
  error?: string;
}

export interface AuthenticatedUser {
  id: string;
  email: string;
  role: string;
  permissions: string[];
  lastActivity: Date;
}

export class WebSocketAuthenticator {
  private userRepo: UserRepository;
  private rateLimiter: RateLimiter;
  private activeSessions = new Map<string, AuthenticatedUser>();
  
  constructor() {
    this.userRepo = new UserRepository();
    this.rateLimiter = new RateLimiter();
  }
  
  async authenticateConnection(request: Request): Promise<AuthResult> {
    const clientIP = this.getClientIP(request);
    
    // Check rate limits
    if (!this.rateLimiter.checkConnectionLimit(clientIP)) {
      wsLogger.warn("Connection rate limit exceeded", { clientIP });
      return { success: false, error: "Rate limit exceeded" };
    }
    
    try {
      const token = this.extractToken(request);
      if (!token) {
        return { success: false, error: "No token provided" };
      }
      
      // Verify JWT token
      const decoded = verify(token, process.env.JWT_SECRET!) as any;
      
      // Check token expiration
      if (decoded.exp && decoded.exp < Date.now() / 1000) {
        return { success: false, error: "Token expired" };
      }
      
      // Get user from database
      const user = await this.userRepo.findById(decoded.userId);
      if (!user || !user.active) {
        return { success: false, error: "User not found or inactive" };
      }
      
      // Check user permissions
      const permissions = await this.userRepo.getUserPermissions(user.id);
      if (!permissions.includes("websocket:connect")) {
        return { success: false, error: "Insufficient permissions" };
      }
      
      const sessionId = this.generateSessionId();
      
      // Store session
      this.activeSessions.set(sessionId, {
        id: user.id,
        email: user.email,
        role: user.role,
        permissions,
        lastActivity: new Date()
      });
      
      wsLogger.info("WebSocket authentication successful", {
        userId: user.id,
        sessionId,
        clientIP
      });
      
      return {
        success: true,
        userId: user.id,
        sessionId,
        userRole: user.role,
        permissions
      };
      
    } catch (error) {
      wsLogger.error("Authentication error", { error: error.message, clientIP });
      return { success: false, error: "Authentication failed" };
    }
  }
  
  async validateSession(sessionId: string): Promise<AuthenticatedUser | null> {
    const session = this.activeSessions.get(sessionId);
    if (!session) {
      return null;
    }
    
    // Check session timeout (1 hour)
    const sessionTimeout = 60 * 60 * 1000;
    if (Date.now() - session.lastActivity.getTime() > sessionTimeout) {
      this.activeSessions.delete(sessionId);
      return null;
    }
    
    // Update last activity
    session.lastActivity = new Date();
    return session;
  }
  
  revokeSession(sessionId: string): void {
    this.activeSessions.delete(sessionId);
    wsLogger.info("Session revoked", { sessionId });
  }
  
  getUserPermissions(sessionId: string): string[] {
    const session = this.activeSessions.get(sessionId);
    return session ? session.permissions : [];
  }
  
  hasPermission(sessionId: string, permission: string): boolean {
    const permissions = this.getUserPermissions(sessionId);
    return permissions.includes(permission);
  }
  
  private extractToken(request: Request): string | null {
    const url = new URL(request.url);
    
    // Check query parameter first
    const queryToken = url.searchParams.get("token");
    if (queryToken) return queryToken;
    
    // Check Authorization header
    const authHeader = request.headers.get("Authorization");
    if (authHeader && authHeader.startsWith("Bearer ")) {
      return authHeader.substring(7);
    }
    
    return null;
  }
  
  private getClientIP(request: Request): string {
    const xForwardedFor = request.headers.get("X-Forwarded-For");
    if (xForwardedFor) {
      return xForwardedFor.split(",")[0].trim();
    }
    
    const xRealIP = request.headers.get("X-Real-IP");
    if (xRealIP) {
      return xRealIP;
    }
    
    return "unknown";
  }
  
  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  // Cleanup expired sessions
  cleanupExpiredSessions(): void {
    const now = Date.now();
    const sessionTimeout = 60 * 60 * 1000; // 1 hour
    
    for (const [sessionId, session] of this.activeSessions) {
      if (now - session.lastActivity.getTime() > sessionTimeout) {
        this.activeSessions.delete(sessionId);
        wsLogger.info("Expired session cleaned up", { sessionId });
      }
    }
  }
  
  getActiveSessionCount(): number {
    return this.activeSessions.size;
  }
}

export const wsAuthenticator = new WebSocketAuthenticator();

// Cleanup expired sessions every 15 minutes
setInterval(() => wsAuthenticator.cleanupExpiredSessions(), 15 * 60 * 1000);
```

### Advanced Rate Limiting System
```typescript
// websocket/middleware/rate-limiter.ts
import { ServerWebSocket } from "bun";
import { wsLogger } from "../logger";

interface RateLimitData {
  count: number;
  resetTime: number;
  blocked: boolean;
  blockExpiry?: number;
}

interface ConnectionLimitData {
  count: number;
  lastConnection: number;
}

export class RateLimiter {
  private messageLimits = new Map<string, RateLimitData>();
  private connectionLimits = new Map<string, ConnectionLimitData>();
  
  // Rate limit configurations
  private readonly config = {
    messages: {
      maxRequests: 100,
      windowMs: 60000, // 1 minute
      blockDuration: 300000, // 5 minutes
      burstLimit: 10 // messages per second
    },
    connections: {
      maxPerIP: 10,
      maxPerUser: 5,
      windowMs: 60000
    }
  };
  
  checkMessageLimit(userId: string): boolean {
    const now = Date.now();
    const userLimit = this.messageLimits.get(userId);
    
    // Check if user is blocked
    if (userLimit?.blocked && userLimit.blockExpiry && now < userLimit.blockExpiry) {
      wsLogger.warn("User is blocked from sending messages", { userId });
      return false;
    }
    
    // Reset expired limits
    if (!userLimit || now > userLimit.resetTime) {
      this.messageLimits.set(userId, {
        count: 1,
        resetTime: now + this.config.messages.windowMs,
        blocked: false
      });
      return true;
    }
    
    // Check rate limit
    if (userLimit.count >= this.config.messages.maxRequests) {
      // Block user for exceeding limit
      userLimit.blocked = true;
      userLimit.blockExpiry = now + this.config.messages.blockDuration;
      
      wsLogger.warn("User exceeded message rate limit", { 
        userId, 
        count: userLimit.count,
        maxRequests: this.config.messages.maxRequests
      });
      
      return false;
    }
    
    userLimit.count++;
    return true;
  }
  
  checkConnectionLimit(clientIP: string): boolean {
    const now = Date.now();
    const ipLimit = this.connectionLimits.get(clientIP);
    
    // Reset expired limits
    if (!ipLimit || now > ipLimit.lastConnection + this.config.connections.windowMs) {
      this.connectionLimits.set(clientIP, {
        count: 1,
        lastConnection: now
      });
      return true;
    }
    
    // Check connection limit
    if (ipLimit.count >= this.config.connections.maxPerIP) {
      wsLogger.warn("IP exceeded connection limit", { 
        clientIP, 
        count: ipLimit.count,
        maxConnections: this.config.connections.maxPerIP
      });
      return false;
    }
    
    ipLimit.count++;
    ipLimit.lastConnection = now;
    return true;
  }
  
  checkBurstLimit(userId: string): boolean {
    const now = Date.now();
    const key = `burst_${userId}`;
    const burstData = this.messageLimits.get(key);
    
    if (!burstData || now > burstData.resetTime) {
      this.messageLimits.set(key, {
        count: 1,
        resetTime: now + 1000, // 1 second window
        blocked: false
      });
      return true;
    }
    
    if (burstData.count >= this.config.messages.burstLimit) {
      wsLogger.warn("User exceeded burst limit", { userId });
      return false;
    }
    
    burstData.count++;
    return true;
  }
  
  resetUserLimit(userId: string): void {
    this.messageLimits.delete(userId);
    this.messageLimits.delete(`burst_${userId}`);
    wsLogger.info("User rate limit reset", { userId });
  }
  
  unblockUser(userId: string): void {
    const userLimit = this.messageLimits.get(userId);
    if (userLimit) {
      userLimit.blocked = false;
      userLimit.blockExpiry = undefined;
      wsLogger.info("User unblocked", { userId });
    }
  }
  
  getUserLimitStatus(userId: string): {
    count: number;
    limit: number;
    resetTime: number;
    blocked: boolean;
  } {
    const userLimit = this.messageLimits.get(userId);
    
    return {
      count: userLimit?.count || 0,
      limit: this.config.messages.maxRequests,
      resetTime: userLimit?.resetTime || 0,
      blocked: userLimit?.blocked || false
    };
  }
  
  getConnectionStats(): {
    totalConnections: number;
    uniqueIPs: number;
    blockedIPs: number;
  } {
    const now = Date.now();
    const activeConnections = Array.from(this.connectionLimits.entries())
      .filter(([_, limit]) => now <= limit.lastConnection + this.config.connections.windowMs);
    
    return {
      totalConnections: activeConnections.reduce((sum, [_, limit]) => sum + limit.count, 0),
      uniqueIPs: activeConnections.length,
      blockedIPs: activeConnections.filter(([_, limit]) => 
        limit.count >= this.config.connections.maxPerIP
      ).length
    };
  }
  
  // Clean up expired limits
  cleanup(): void {
    const now = Date.now();
    
    // Clean up message limits
    for (const [userId, limit] of this.messageLimits.entries()) {
      if (now > limit.resetTime && (!limit.blocked || (limit.blockExpiry && now > limit.blockExpiry))) {
        this.messageLimits.delete(userId);
      }
    }
    
    // Clean up connection limits
    for (const [clientIP, limit] of this.connectionLimits.entries()) {
      if (now > limit.lastConnection + this.config.connections.windowMs) {
        this.connectionLimits.delete(clientIP);
      }
    }
  }
  
  // Update configuration
  updateConfig(config: Partial<typeof this.config>): void {
    Object.assign(this.config, config);
    wsLogger.info("Rate limiter configuration updated", { config: this.config });
  }
}

export const rateLimiter = new RateLimiter();

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
    "typing_start", "typing_stop", "ping",
    "join_room", "leave_room", "presence_update"
  ]),
  data: z.object({
    channel: z.string().optional(),
    conversationId: z.string().uuid().optional(),
    content: z.string().max(10000).optional(),
    timestamp: z.number().optional(),
    room: z.string().optional(),
    metadata: z.record(z.any()).optional()
  })
});

export function validateMessage(message: any): { valid: boolean; error?: string; data?: any } {
  try {
    const parsed = MessageSchema.parse(message);
    
    // Additional validation
    if (parsed.data.content) {
      parsed.data.content = sanitizeContent(parsed.data.content);
    }
    
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
    .replace(/on\w+\s*=/gi, "")
    .trim();
}

export function validateChannelName(channel: string): boolean {
  // Only allow alphanumeric characters, underscores, and hyphens
  return /^[a-zA-Z0-9_-]+$/.test(channel);
}

export function validateConversationId(id: string): boolean {
  // UUID v4 format
  return /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(id);
}
```

### Enhanced Connection Management with Clustering
```typescript
// websocket/cluster-manager.ts
import { EventEmitter } from "events";
import { Redis } from "ioredis";
import { wsLogger } from "./logger";

export class ClusterManager extends EventEmitter {
  private redis: Redis;
  private subscriber: Redis;
  private nodeId: string;
  private heartbeatInterval: NodeJS.Timeout;
  private nodeStats = {
    connections: 0,
    messages: 0,
    cpu: 0,
    memory: 0
  };
  
  constructor() {
    super();
    this.redis = new Redis({
      host: process.env.REDIS_HOST || "localhost",
      port: parseInt(process.env.REDIS_PORT || "6379"),
      retryDelayOnFailover: 100,
      maxRetriesPerRequest: 3
    });
    
    this.subscriber = this.redis.duplicate();
    this.nodeId = `node_${process.pid}_${Date.now()}`;
    this.setupEventHandlers();
    this.startHeartbeat();
  }
  
  private setupEventHandlers(): void {
    this.redis.on("error", (error) => {
      wsLogger.error("Redis connection error", { error: error.message });
    });
    
    this.redis.on("connect", () => {
      wsLogger.info("Redis connected", { nodeId: this.nodeId });
    });
    
    this.subscriber.on("message", (channel, message) => {
      try {
        const parsed = JSON.parse(message);
        // Don't process messages from this node
        if (parsed.nodeId !== this.nodeId) {
          this.handleClusterMessage(channel, parsed);
        }
      } catch (error) {
        wsLogger.error("Failed to parse cluster message", { error: error.message });
      }
    });
  }
  
  private handleClusterMessage(channel: string, message: any): void {
    const { type, data } = message;
    
    switch (type) {
      case "broadcast":
        this.emit("broadcast", data);
        break;
      case "user_message":
        this.emit("user_message", data);
        break;
      case "presence_update":
        this.emit("presence_update", data);
        break;
      case "node_stats":
        this.emit("node_stats", data);
        break;
      default:
        wsLogger.warn("Unknown cluster message type", { type, channel });
    }
  }
  
  // Broadcast message across cluster
  async broadcastToCluster(channel: string, type: string, data: any): Promise<void> {
    try {
      await this.redis.publish(`cluster:${channel}`, JSON.stringify({
        nodeId: this.nodeId,
        timestamp: Date.now(),
        type,
        data
      }));
    } catch (error) {
      wsLogger.error("Failed to broadcast cluster message", { error: error.message });
    }
  }
  
  // Subscribe to cluster messages
  async subscribeToCluster(channel: string): Promise<void> {
    try {
      await this.subscriber.subscribe(`cluster:${channel}`);
      wsLogger.info("Subscribed to cluster channel", { channel, nodeId: this.nodeId });
    } catch (error) {
      wsLogger.error("Failed to subscribe to cluster channel", { error: error.message });
    }
  }
  
  // Register node presence
  async registerNode(): Promise<void> {
    try {
      await this.redis.setex(
        `nodes:${this.nodeId}`, 
        30, // 30 seconds TTL
        JSON.stringify({
          nodeId: this.nodeId,
          timestamp: Date.now(),
          stats: this.nodeStats
        })
      );
    } catch (error) {
      wsLogger.error("Failed to register node", { error: error.message });
    }
  }
  
  // Get all active nodes
  async getActiveNodes(): Promise<string[]> {
    try {
      const keys = await this.redis.keys("nodes:*");
      return keys.map(key => key.replace("nodes:", ""));
    } catch (error) {
      wsLogger.error("Failed to get active nodes", { error: error.message });
      return [];
    }
  }
  
  // Update node statistics
  updateNodeStats(stats: Partial<typeof this.nodeStats>): void {
    Object.assign(this.nodeStats, stats);
  }
  
  // Get cluster statistics
  async getClusterStats(): Promise<any> {
    try {
      const nodeKeys = await this.redis.keys("nodes:*");
      const pipeline = this.redis.pipeline();
      
      nodeKeys.forEach(key => {
        pipeline.get(key);
      });
      
      const results = await pipeline.exec();
      const nodes = results
        ?.filter(([err, result]) => !err && result)
        .map(([_, result]) => JSON.parse(result as string));
      
      return {
        totalNodes: nodes?.length || 0,
        totalConnections: nodes?.reduce((sum, node) => sum + node.stats.connections, 0) || 0,
        totalMessages: nodes?.reduce((sum, node) => sum + node.stats.messages, 0) || 0,
        nodes: nodes || []
      };
    } catch (error) {
      wsLogger.error("Failed to get cluster stats", { error: error.message });
      return { totalNodes: 0, totalConnections: 0, totalMessages: 0, nodes: [] };
    }
  }
  
  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      this.registerNode();
    }, 15000); // Every 15 seconds
  }
  
  async shutdown(): Promise<void> {
    clearInterval(this.heartbeatInterval);
    
    try {
      await this.redis.del(`nodes:${this.nodeId}`);
      await this.broadcastToCluster("system", "node_shutdown", { nodeId: this.nodeId });
      
      this.redis.disconnect();
      this.subscriber.disconnect();
      
      wsLogger.info("Cluster manager shut down", { nodeId: this.nodeId });
    } catch (error) {
      wsLogger.error("Error during cluster shutdown", { error: error.message });
    }
  }
}
```

### WebSocket Connection Pooling
```typescript
// websocket/connection-pool.ts
import { ServerWebSocket } from "bun";
import { wsLogger } from "./logger";

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
  
  addConnection(sessionId: string, ws: ServerWebSocket<any>): void {
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
    
    wsLogger.debug("Connection added to pool", { 
      sessionId, 
      userId: ws.data.userId, 
      totalConnections: this.connections.size 
    });
  }
  
  removeConnection(sessionId: string): void {
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
      
      wsLogger.debug("Connection removed from pool", { 
        sessionId, 
        userId, 
        totalConnections: this.connections.size 
      });
    }
  }
  
  subscribeToRoom(sessionId: string, room: string): boolean {
    const connection = this.connections.get(sessionId);
    if (!connection) {
      return false;
    }
    
    connection.subscriptions.add(room);
    connection.lastActivity = Date.now();
    
    if (!this.roomConnections.has(room)) {
      this.roomConnections.set(room, new Set());
    }
    this.roomConnections.get(room)!.add(sessionId);
    
    wsLogger.debug("Connection subscribed to room", { sessionId, room });
    return true;
  }
  
  unsubscribeFromRoom(sessionId: string, room: string): boolean {
    const connection = this.connections.get(sessionId);
    if (!connection) {
      return false;
    }
    
    connection.subscriptions.delete(room);
    
    const roomSessions = this.roomConnections.get(room);
    if (roomSessions) {
      roomSessions.delete(sessionId);
      if (roomSessions.size === 0) {
        this.roomConnections.delete(room);
      }
    }
    
    wsLogger.debug("Connection unsubscribed from room", { sessionId, room });
    return true;
  }
  
  broadcastToRoom(room: string, message: string, excludeSessionId?: string): number {
    const roomSessions = this.roomConnections.get(room);
    if (!roomSessions) {
      return 0;
    }
    
    let sentCount = 0;
    roomSessions.forEach(sessionId => {
      if (sessionId !== excludeSessionId) {
        const connection = this.connections.get(sessionId);
        if (connection && connection.ws.readyState === 1) {
          try {
            connection.ws.send(message);
            connection.lastActivity = Date.now();
            sentCount++;
          } catch (error) {
            wsLogger.error("Failed to send message to connection", { 
              sessionId, 
              error: error.message 
            });
          }
        }
      }
    });
    
    return sentCount;
  }
  
  broadcastToUser(userId: string, message: string): number {
    const sessionIds = this.userConnections.get(userId);
    if (!sessionIds) {
      return 0;
    }
    
    let sentCount = 0;
    sessionIds.forEach(sessionId => {
      const connection = this.connections.get(sessionId);
      if (connection && connection.ws.readyState === 1) {
        try {
          connection.ws.send(message);
          connection.lastActivity = Date.now();
          sentCount++;
        } catch (error) {
          wsLogger.error("Failed to send message to user connection", { 
            userId, 
            sessionId, 
            error: error.message 
          });
        }
      }
    });
    
    return sentCount;
  }
  
  getUserConnections(userId: string): PooledConnection[] {
    const sessionIds = this.userConnections.get(userId) || new Set();
    return Array.from(sessionIds)
      .map(sessionId => this.connections.get(sessionId))
      .filter(Boolean) as PooledConnection[];
  }
  
  updateActivity(sessionId: string): void {
    const connection = this.connections.get(sessionId);
    if (connection) {
      connection.lastActivity = Date.now();
    }
  }
  
  setConnectionMetadata(sessionId: string, key: string, value: any): void {
    const connection = this.connections.get(sessionId);
    if (connection) {
      connection.metadata[key] = value;
    }
  }
  
  getConnectionMetadata(sessionId: string, key: string): any {
    const connection = this.connections.get(sessionId);
    return connection?.metadata[key];
  }
  
  getStats(): {
    totalConnections: number;
    activeUsers: number;
    activeRooms: number;
    maxConnections: number;
    memoryUsage: number;
  } {
    return {
      totalConnections: this.connections.size,
      activeUsers: this.userConnections.size,
      activeRooms: this.roomConnections.size,
      maxConnections: this.maxConnections,
      memoryUsage: process.memoryUsage().heapUsed
    };
  }
  
  private trackUserConnection(userId: string, sessionId: string): void {
    if (!this.userConnections.has(userId)) {
      this.userConnections.set(userId, new Set());
    }
    this.userConnections.get(userId)!.add(sessionId);
  }
  
  private evictOldestConnection(): void {
    let oldestSessionId: string | null = null;
    let oldestTime = Date.now();
    
    for (const [sessionId, connection] of this.connections) {
      if (connection.lastActivity < oldestTime) {
        oldestTime = connection.lastActivity;
        oldestSessionId = sessionId;
      }
    }
    
    if (oldestSessionId) {
      wsLogger.info("Evicting oldest connection", { sessionId: oldestSessionId });
      const connection = this.connections.get(oldestSessionId);
      if (connection) {
        connection.ws.close(1000, "Connection evicted");
        this.removeConnection(oldestSessionId);
      }
    }
  }
  
  private startCleanup(): void {
    this.cleanupInterval = setInterval(() => {
      const now = Date.now();
      const timeout = 5 * 60 * 1000; // 5 minutes
      
      for (const [sessionId, connection] of this.connections) {
        if (now - connection.lastActivity > timeout) {
          wsLogger.info("Cleaning up inactive connection", { sessionId });
          connection.ws.close(1000, "Connection timeout");
          this.removeConnection(sessionId);
        }
      }
    }, 60000); // Run every minute
  }
  
  shutdown(): void {
    clearInterval(this.cleanupInterval);
    
    this.connections.forEach(connection => {
      connection.ws.close(1000, "Server shutdown");
    });
    
    this.connections.clear();
    this.userConnections.clear();
    this.roomConnections.clear();
    
    wsLogger.info("Connection pool shut down");
  }
}
```

### Performance Monitoring and Metrics
```typescript
// websocket/monitoring.ts
import { EventEmitter } from "events";
import { wsLogger } from "./logger";

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
  
  recordConnection(): void {
    this.metrics.connections.current++;
    this.metrics.connections.total++;
    
    if (this.metrics.connections.current > this.metrics.connections.peak) {
      this.metrics.connections.peak = this.metrics.connections.current;
    }
    
    this.emit("connection", this.metrics.connections);
  }
  
  recordDisconnection(): void {
    this.metrics.connections.current--;
    this.emit("disconnection", this.metrics.connections);
  }
  
  recordMessageSent(): void {
    this.metrics.messages.sent++;
    this.emit("message_sent", this.metrics.messages);
  }
  
  recordMessageReceived(): void {
    this.metrics.messages.received++;
    this.emit("message_received", this.metrics.messages);
  }
  
  recordError(): void {
    this.metrics.messages.errors++;
    this.emit("error", this.metrics.messages);
  }
  
  recordLatency(latency: number): void {
    this.latencyBuffer.push(latency);
    
    if (this.latencyBuffer.length > this.bufferSize) {
      this.latencyBuffer.shift();
    }
    
    this.calculateLatencyMetrics();
  }
  
  recordMemoryUsage(): void {
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
  
  private calculateLatencyMetrics(): void {
    if (this.latencyBuffer.length === 0) return;
    
    const sorted = [...this.latencyBuffer].sort((a, b) => a - b);
    const sum = sorted.reduce((acc, val) => acc + val, 0);
    
    this.metrics.latency.average = sum / sorted.length;
    this.metrics.latency.p95 = sorted[Math.floor(sorted.length * 0.95)];
    this.metrics.latency.p99 = sorted[Math.floor(sorted.length * 0.99)];
  }
  
  startPeriodicReporting(intervalMs = 30000): void {
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
  
  disconnect(): void {
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
  
  send(type: string, data: any): void {
    const message = { type, data };
    
    if (this.connectionState === 'connected' && this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      this.queueMessage(message);
    }
  }
  
  subscribe(channel: string): void {
    this.send('subscribe', { channel });
  }
  
  unsubscribe(channel: string): void {
    this.send('unsubscribe', { channel });
  }
  
  on(eventType: string, handler: Function): void {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, []);
    }
    this.eventHandlers.get(eventType)!.push(handler);
  }
  
  off(eventType: string, handler: Function): void {
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
  
  private handleMessage(message: any): void {
    const { type, data } = message;
    
    // Handle pong responses
    if (type === 'pong') {
      return;
    }
    
    this.emit(type, data);
  }
  
  private emit(eventType: string, data?: any): void {
    const handlers = this.eventHandlers.get(eventType) || [];
    handlers.forEach(handler => {
      try {
        handler(data);
      } catch (error) {
        console.error('Error in event handler:', error);
      }
    });
  }
  
  private scheduleReconnect(): void {
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
  
  private startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      if (this.connectionState === 'connected') {
        this.send('ping', { timestamp: Date.now() });
      }
    }, this.options.heartbeatInterval!);
  }
  
  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }
  
  private queueMessage(message: { type: string; data: any }): void {
    if (this.messageQueue.length >= this.options.messageQueueSize!) {
      this.messageQueue.shift(); // Remove oldest message
    }
    
    this.messageQueue.push(message);
  }
  
  private flushMessageQueue(): void {
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
    <div v-if="showStats" class="stats">
      <div>Messages: {{ stats.messages }}</div>
      <div>Latency: {{ stats.latency }}ms</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { EnhancedWebSocketClient } from '../utils/websocket-client';

const connectionState = ref('disconnected');
const reconnectAttempt = ref(0);
const maxReconnectAttempts = ref(5);
const showStats = ref(false);
const stats = ref({
  messages: 0,
  latency: 0
});

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
    stats.value.messages++;
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
  getConnectionState: () => wsClient?.getConnectionState(),
  toggleStats: () => showStats.value = !showStats.value
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

.stats {
  display: flex;
  gap: 8px;
  font-size: 10px;
  color: #6c757d;
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

## Performance Requirements
- **Connection Capacity**: Support 10,000+ concurrent WebSocket connections
- **Message Latency**: Real-time messages delivered within 50ms
- **Memory Usage**: Efficient connection tracking with minimal memory overhead
- **Throughput**: Handle 50,000 messages per second
- **Connection Recovery**: Automatic reconnection within 5 seconds
- **Clustering**: Horizontal scaling support with Redis

## Acceptance Criteria
- [ ] WebSocket server integrated with Bun.serve()
- [ ] Advanced connection management with pooling
- [ ] Room-based subscription system for conversations
- [ ] Real-time message broadcasting with clustering
- [ ] Client-side WebSocket integration with reconnection
- [ ] Multi-layer authentication integration
- [ ] Typing indicators and presence system
- [ ] File processing progress updates
- [ ] Comprehensive error handling and recovery
- [ ] Performance testing meets enterprise requirements
- [ ] Security audit passed
- [ ] Monitoring and alerting system operational

## Testing Procedures
1. **Connection Testing**: Test WebSocket connection establishment and cleanup
2. **Load Testing**: Verify performance with 10,000+ concurrent connections
3. **Message Testing**: Test message delivery, ordering, and reliability
4. **Reconnection Testing**: Test automatic reconnection scenarios
5. **Security Testing**: Penetration testing and vulnerability assessment
6. **Integration Testing**: Test with existing API endpoints
7. **Clustering Testing**: Test multi-node deployment and failover

## Integration Points
- **Week 5**: Backend API for message processing
- **Week 7**: Frontend real-time UI components
- **Week 9**: Analytics real-time data streaming
- **Redis**: For clustering and session management
- **Monitoring**: Integration with existing monitoring infrastructure

This enhanced WebSocket implementation provides enterprise-grade real-time communication with comprehensive security, monitoring, and scalability features suitable for production deployment.