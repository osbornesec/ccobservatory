# 🌐 WebSocket Implementation Technical Specification

## 🎯 **Executive Summary**

This specification defines the real-time communication architecture for Claude Code Observatory using WebSockets. The system provides sub-50ms message broadcasting, supports 100+ concurrent connections, implements intelligent subscription management, and ensures robust error handling with automatic reconnection capabilities.

---

## 📋 **Technical Requirements**

### **Performance Requirements**
- **Message Broadcast Latency:** <50ms (95th percentile)
- **Concurrent Connections:** 100+ simultaneous clients
- **Message Throughput:** 1,000+ messages/second
- **Connection Establishment:** <200ms handshake time
- **Memory Efficiency:** <1MB per connection

### **Reliability Requirements**
- **Connection Recovery:** Automatic reconnection with exponential backoff
- **Message Ordering:** Guaranteed sequential delivery per client
- **Heartbeat Monitoring:** 30-second ping/pong cycles
- **Graceful Degradation:** Service continues with reduced functionality
- **Data Consistency:** No message loss during normal operations

---

## 🏗️ **System Architecture**

### **Component Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                    WebSocket Server                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Connection  │  │   Message   │  │    Subscription     │  │
│  │  Manager    │──│   Router    │──│     Manager         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│         │                 │                       │         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Heartbeat   │  │  Event      │  │     Rate           │  │
│  │ Monitor     │  │ Broadcaster │  │    Limiter          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│         │                 │                       │         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Authentication │ Compression │  │    Metrics         │  │
│  │ Handler     │  │ Manager     │  │    Collector       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### **Core WebSocket Server Implementation**

```typescript
import WebSocket, { WebSocketServer } from 'ws';
import { createServer } from 'http';
import { EventEmitter } from 'events';

interface WebSocketConfig {
  port: number;
  maxConnections: number;
  heartbeatInterval: number;
  messageRateLimit: number;
  compressionEnabled: boolean;
  authenticationRequired: boolean;
}

interface ClientConnection {
  id: string;
  ws: WebSocket;
  subscriptions: Set<string>;
  isAlive: boolean;
  lastActivity: number;
  messageCount: number;
  rateLimitReset: number;
  metadata: ClientMetadata;
}

interface ClientMetadata {
  userAgent: string;
  ipAddress: string;
  connectedAt: number;
  projectIds: number[];
  permissions: string[];
}

class ObservatoryWebSocketServer extends EventEmitter {
  private server: WebSocketServer;
  private httpServer: any;
  private clients: Map<string, ClientConnection> = new Map();
  private subscriptions: Map<string, Set<string>> = new Map();
  private config: WebSocketConfig;
  private heartbeatInterval: NodeJS.Timeout;
  private metricsCollector: MetricsCollector;

  constructor(config: WebSocketConfig) {
    super();
    this.config = {
      port: 8080,
      maxConnections: 100,
      heartbeatInterval: 30000, // 30 seconds
      messageRateLimit: 100, // messages per minute
      compressionEnabled: true,
      authenticationRequired: true,
      ...config
    };
    
    this.metricsCollector = new MetricsCollector();
    this.setupServer();
  }

  private setupServer(): void {
    // Create HTTP server for WebSocket upgrade
    this.httpServer = createServer();
    
    // Create WebSocket server with compression
    this.server = new WebSocketServer({
      server: this.httpServer,
      perMessageDeflate: this.config.compressionEnabled ? {
        zlibDeflateOptions: {
          chunkSize: 1024,
          memLevel: 7,
          level: 3
        },
        zlibInflateOptions: {
          chunkSize: 10 * 1024
        },
        serverMaxWindowBits: 15,
        concurrencyLimit: 10,
        threshold: 1024
      } : false
    });

    this.setupEventHandlers();
    this.startHeartbeat();
  }

  private setupEventHandlers(): void {
    this.server.on('connection', this.handleConnection.bind(this));
    this.server.on('error', this.handleServerError.bind(this));
    
    this.httpServer.on('upgrade', this.handleUpgrade.bind(this));
    
    // Graceful shutdown
    process.on('SIGTERM', this.gracefulShutdown.bind(this));
    process.on('SIGINT', this.gracefulShutdown.bind(this));
  }

  private async handleUpgrade(request: any, socket: any, head: any): Promise<void> {
    try {
      // Rate limiting check
      const clientIp = this.getClientIP(request);
      if (await this.isRateLimited(clientIp)) {
        socket.write('HTTP/1.1 429 Too Many Requests\r\n\r\n');
        socket.destroy();
        return;
      }

      // Connection limit check
      if (this.clients.size >= this.config.maxConnections) {
        socket.write('HTTP/1.1 503 Service Unavailable\r\n\r\n');
        socket.destroy();
        return;
      }

      // Authentication check
      if (this.config.authenticationRequired) {
        const authResult = await this.authenticateConnection(request);
        if (!authResult.success) {
          socket.write('HTTP/1.1 401 Unauthorized\r\n\r\n');
          socket.destroy();
          return;
        }
        
        // Store auth info for later use
        request.authData = authResult.data;
      }

      // Proceed with WebSocket handshake
      this.server.handleUpgrade(request, socket, head, (ws) => {
        this.server.emit('connection', ws, request);
      });

    } catch (error) {
      console.error('Upgrade error:', error);
      socket.write('HTTP/1.1 500 Internal Server Error\r\n\r\n');
      socket.destroy();
    }
  }

  private handleConnection(ws: WebSocket, request: any): void {
    const clientId = this.generateClientId();
    const clientMetadata: ClientMetadata = {
      userAgent: request.headers['user-agent'] || 'Unknown',
      ipAddress: this.getClientIP(request),
      connectedAt: Date.now(),
      projectIds: request.authData?.projectIds || [],
      permissions: request.authData?.permissions || []
    };

    const client: ClientConnection = {
      id: clientId,
      ws,
      subscriptions: new Set(),
      isAlive: true,
      lastActivity: Date.now(),
      messageCount: 0,
      rateLimitReset: Date.now() + 60000,
      metadata: clientMetadata
    };

    this.clients.set(clientId, client);
    this.metricsCollector.recordConnection(clientId);

    // Setup client event handlers
    ws.on('error', (error) => this.handleClientError(clientId, error));
    ws.on('close', (code, reason) => this.handleClientDisconnection(clientId, code, reason));
    ws.on('message', (data, isBinary) => this.handleClientMessage(clientId, data, isBinary));
    ws.on('pong', () => this.handleClientPong(clientId));

    // Send welcome message
    this.sendToClient(clientId, {
      type: 'connection_established',
      data: {
        clientId,
        serverTime: Date.now(),
        capabilities: this.getServerCapabilities(),
        limits: {
          messageRateLimit: this.config.messageRateLimit,
          maxSubscriptions: 50
        }
      }
    });

    this.emit('client_connected', { clientId, metadata: clientMetadata });
  }

  private handleClientMessage(clientId: string, data: Buffer, isBinary: boolean): void {
    const client = this.clients.get(clientId);
    if (!client) return;

    // Rate limiting
    if (!this.checkRateLimit(client)) {
      this.sendToClient(clientId, {
        type: 'error',
        data: {
          code: 'RATE_LIMIT_EXCEEDED',
          message: 'Message rate limit exceeded'
        }
      });
      return;
    }

    client.lastActivity = Date.now();
    client.messageCount++;

    try {
      if (isBinary) {
        this.handleBinaryMessage(clientId, data);
        return;
      }

      const message = JSON.parse(data.toString('utf8'));
      this.processClientMessage(clientId, message);

    } catch (error) {
      this.sendToClient(clientId, {
        type: 'error',
        data: {
          code: 'INVALID_MESSAGE',
          message: 'Invalid message format'
        }
      });
    }
  }

  private processClientMessage(clientId: string, message: any): void {
    const client = this.clients.get(clientId);
    if (!client) return;

    switch (message.type) {
      case 'subscribe':
        this.handleSubscription(clientId, message.data);
        break;
      
      case 'unsubscribe':
        this.handleUnsubscription(clientId, message.data);
        break;
      
      case 'ping':
        this.sendToClient(clientId, { type: 'pong', data: { timestamp: Date.now() } });
        break;
      
      case 'get_active_conversations':
        this.handleGetActiveConversations(clientId, message.data);
        break;
      
      case 'get_project_activity':
        this.handleGetProjectActivity(clientId, message.data);
        break;
      
      default:
        this.sendToClient(clientId, {
          type: 'error',
          data: {
            code: 'UNKNOWN_MESSAGE_TYPE',
            message: `Unknown message type: ${message.type}`
          }
        });
    }
  }

  private handleSubscription(clientId: string, subscriptionData: any): void {
    const client = this.clients.get(clientId);
    if (!client) return;

    const { filters } = subscriptionData;
    
    // Validate subscription filters
    if (!this.validateSubscriptionFilters(filters, client.metadata.permissions)) {
      this.sendToClient(clientId, {
        type: 'subscription_error',
        data: {
          code: 'INVALID_FILTERS',
          message: 'Invalid or unauthorized subscription filters'
        }
      });
      return;
    }

    // Generate subscription key
    const subscriptionKey = this.generateSubscriptionKey(filters);
    
    // Add to client subscriptions
    client.subscriptions.add(subscriptionKey);
    
    // Add to global subscription index
    if (!this.subscriptions.has(subscriptionKey)) {
      this.subscriptions.set(subscriptionKey, new Set());
    }
    this.subscriptions.get(subscriptionKey)!.add(clientId);

    this.sendToClient(clientId, {
      type: 'subscription_confirmed',
      data: {
        subscriptionKey,
        filters
      }
    });

    this.emit('client_subscribed', { clientId, filters });
  }

  public broadcast(event: ServerEvent): void {
    const startTime = process.hrtime.bigint();
    let deliveredCount = 0;
    let failedCount = 0;

    // Find matching subscriptions
    const matchingClients = this.findMatchingClients(event);
    
    for (const clientId of matchingClients) {
      try {
        this.sendToClient(clientId, event);
        deliveredCount++;
      } catch (error) {
        failedCount++;
        console.error(`Failed to send to client ${clientId}:`, error);
      }
    }

    const endTime = process.hrtime.bigint();
    const latency = Number(endTime - startTime) / 1000000; // Convert to milliseconds

    this.metricsCollector.recordBroadcast({
      type: event.type,
      latency,
      deliveredCount,
      failedCount,
      totalClients: this.clients.size
    });

    this.emit('broadcast_completed', {
      event: event.type,
      delivered: deliveredCount,
      failed: failedCount,
      latency
    });
  }

  private findMatchingClients(event: ServerEvent): Set<string> {
    const matchingClients = new Set<string>();

    for (const [subscriptionKey, clientIds] of this.subscriptions) {
      if (this.eventMatchesSubscription(event, subscriptionKey)) {
        clientIds.forEach(clientId => matchingClients.add(clientId));
      }
    }

    return matchingClients;
  }

  private eventMatchesSubscription(event: ServerEvent, subscriptionKey: string): boolean {
    const filters = this.parseSubscriptionKey(subscriptionKey);
    
    // Check project filter
    if (filters.projectIds && filters.projectIds.length > 0) {
      const eventProjectId = this.extractProjectId(event);
      if (eventProjectId && !filters.projectIds.includes(eventProjectId)) {
        return false;
      }
    }

    // Check event type filter
    if (filters.eventTypes && filters.eventTypes.length > 0) {
      if (!filters.eventTypes.includes(event.type)) {
        return false;
      }
    }

    // Check session filter
    if (filters.sessionIds && filters.sessionIds.length > 0) {
      const eventSessionId = this.extractSessionId(event);
      if (eventSessionId && !filters.sessionIds.includes(eventSessionId)) {
        return false;
      }
    }

    return true;
  }

  private sendToClient(clientId: string, message: any): void {
    const client = this.clients.get(clientId);
    if (!client) return;

    if (client.ws.readyState !== WebSocket.OPEN) {
      this.removeClient(clientId);
      return;
    }

    try {
      const serialized = JSON.stringify(message);
      client.ws.send(serialized);
      
      this.metricsCollector.recordMessageSent(clientId, serialized.length);
    } catch (error) {
      console.error(`Failed to send message to client ${clientId}:`, error);
      this.removeClient(clientId);
    }
  }

  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      this.performHeartbeat();
    }, this.config.heartbeatInterval);
  }

  private performHeartbeat(): void {
    const now = Date.now();
    const timeoutThreshold = now - (this.config.heartbeatInterval * 2);

    for (const [clientId, client] of this.clients) {
      if (client.lastActivity < timeoutThreshold) {
        // Client is inactive, terminate connection
        this.terminateClient(clientId, 'Heartbeat timeout');
        continue;
      }

      if (client.ws.readyState === WebSocket.OPEN) {
        client.isAlive = false;
        client.ws.ping();
      }
    }

    // Clean up clients that didn't respond to ping
    setTimeout(() => {
      for (const [clientId, client] of this.clients) {
        if (!client.isAlive && client.ws.readyState === WebSocket.OPEN) {
          this.terminateClient(clientId, 'Failed to respond to ping');
        }
      }
    }, 5000); // 5 second grace period
  }

  private handleClientPong(clientId: string): void {
    const client = this.clients.get(clientId);
    if (client) {
      client.isAlive = true;
      client.lastActivity = Date.now();
    }
  }

  async start(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.httpServer.listen(this.config.port, (error: any) => {
        if (error) {
          reject(error);
        } else {
          console.log(`WebSocket server listening on port ${this.config.port}`);
          resolve();
        }
      });
    });
  }

  async stop(): Promise<void> {
    return this.gracefulShutdown();
  }

  private async gracefulShutdown(): Promise<void> {
    console.log('Initiating graceful WebSocket server shutdown...');

    // Clear heartbeat interval
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }

    // Notify all clients of shutdown
    const shutdownMessage = {
      type: 'server_shutdown',
      data: {
        message: 'Server is shutting down',
        reconnectAfter: 5000
      }
    };

    for (const [clientId] of this.clients) {
      this.sendToClient(clientId, shutdownMessage);
    }

    // Wait a bit for messages to be sent
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Close all client connections
    for (const [clientId, client] of this.clients) {
      client.ws.close(1001, 'Server shutdown');
    }

    // Close WebSocket server
    this.server.close();

    // Close HTTP server
    this.httpServer.close();

    console.log('WebSocket server shutdown complete');
  }
}
```

---

## 🔧 **Message Types and Events**

### **Client-to-Server Messages**

```typescript
interface ClientToServerMessages {
  subscribe: {
    type: 'subscribe';
    data: {
      filters: SubscriptionFilters;
      clientInfo?: {
        name: string;
        version: string;
      };
    };
  };

  unsubscribe: {
    type: 'unsubscribe';
    data: {
      subscriptionKey?: string;
      filters?: SubscriptionFilters;
    };
  };

  ping: {
    type: 'ping';
    data: {
      timestamp: number;
    };
  };

  get_active_conversations: {
    type: 'get_active_conversations';
    data: {
      projectId?: number;
      limit?: number;
    };
  };

  get_project_activity: {
    type: 'get_project_activity';
    data: {
      projectId: number;
      timeRange?: {
        start: number;
        end: number;
      };
    };
  };
}

interface SubscriptionFilters {
  projectIds?: number[];
  eventTypes?: string[];
  sessionIds?: string[];
  messageTypes?: ('user' | 'assistant' | 'system')[];
  toolNames?: string[];
}
```

### **Server-to-Client Events**

```typescript
interface ServerToClientEvents {
  // Connection events
  connection_established: {
    type: 'connection_established';
    data: {
      clientId: string;
      serverTime: number;
      capabilities: ServerCapabilities;
      limits: ConnectionLimits;
    };
    timestamp: number;
  };

  // Conversation events
  conversation_started: {
    type: 'conversation_started';
    data: {
      conversationId: string;
      sessionId: string;
      projectId: number;
      projectName: string;
      startTime: number;
    };
    timestamp: number;
  };

  conversation_ended: {
    type: 'conversation_ended';
    data: {
      conversationId: string;
      duration: number;
      messageCount: number;
      toolUsageCount: number;
      endTime: number;
    };
    timestamp: number;
  };

  // Message events
  message_added: {
    type: 'message_added';
    data: {
      conversationId: string;
      message: NormalizedMessage;
      projectInfo: ProjectInfo;
      isLatest: boolean;
    };
    timestamp: number;
  };

  // Project events
  project_discovered: {
    type: 'project_discovered';
    data: {
      project: Project;
      conversationCount: number;
      lastActivity: number;
    };
    timestamp: number;
  };

  project_updated: {
    type: 'project_updated';
    data: {
      projectId: number;
      changes: ProjectChanges;
      newActivity: boolean;
    };
    timestamp: number;
  };

  // Analytics events
  analytics_update: {
    type: 'analytics_update';
    data: {
      projectId: number;
      metrics: AnalyticsMetrics;
      period: string;
    };
    timestamp: number;
  };

  // System events
  error: {
    type: 'error';
    data: {
      code: string;
      message: string;
      details?: any;
    };
    timestamp: number;
  };

  server_shutdown: {
    type: 'server_shutdown';
    data: {
      message: string;
      reconnectAfter: number;
    };
    timestamp: number;
  };
}
```

---

## 🔒 **Security and Authentication**

### **Authentication Handler**

```typescript
class WebSocketAuthHandler {
  private jwtSecret: string;
  private sessionManager: SessionManager;

  constructor(jwtSecret: string, sessionManager: SessionManager) {
    this.jwtSecret = jwtSecret;
    this.sessionManager = sessionManager;
  }

  async authenticateConnection(request: any): Promise<AuthResult> {
    try {
      // Extract token from query params or headers
      const token = this.extractToken(request);
      
      if (!token) {
        return {
          success: false,
          error: 'Missing authentication token'
        };
      }

      // Verify JWT token
      const decoded = this.verifyJWT(token);
      
      if (!decoded) {
        return {
          success: false,
          error: 'Invalid authentication token'
        };
      }

      // Check session validity
      const session = await this.sessionManager.getSession(decoded.sessionId);
      
      if (!session || session.expired) {
        return {
          success: false,
          error: 'Session expired'
        };
      }

      // Get user permissions
      const permissions = await this.getUserPermissions(decoded.userId);
      
      return {
        success: true,
        data: {
          userId: decoded.userId,
          sessionId: decoded.sessionId,
          projectIds: permissions.projectIds,
          permissions: permissions.permissions
        }
      };

    } catch (error) {
      return {
        success: false,
        error: 'Authentication failed'
      };
    }
  }

  private extractToken(request: any): string | null {
    // Check query parameters first
    const url = new URL(request.url, 'ws://localhost');
    const tokenFromQuery = url.searchParams.get('token');
    
    if (tokenFromQuery) {
      return tokenFromQuery;
    }

    // Check Authorization header
    const authHeader = request.headers.authorization;
    if (authHeader && authHeader.startsWith('Bearer ')) {
      return authHeader.substring(7);
    }

    return null;
  }

  private verifyJWT(token: string): any {
    try {
      return jwt.verify(token, this.jwtSecret);
    } catch {
      return null;
    }
  }

  private async getUserPermissions(userId: string): Promise<UserPermissions> {
    // Implementation would fetch from database
    return {
      projectIds: [1, 2, 3], // Projects user has access to
      permissions: ['read', 'write', 'subscribe']
    };
  }
}
```

### **Rate Limiting**

```typescript
class RateLimiter {
  private limits: Map<string, RateLimitInfo> = new Map();
  private config: RateLimitConfig;

  constructor(config: RateLimitConfig) {
    this.config = {
      maxRequestsPerMinute: 100,
      maxConnectionsPerIP: 10,
      burstLimit: 20,
      windowSizeMs: 60000,
      ...config
    };
  }

  async checkRateLimit(clientIP: string, clientId?: string): Promise<RateLimitResult> {
    const now = Date.now();
    const key = clientId || clientIP;
    
    let limitInfo = this.limits.get(key);
    
    if (!limitInfo) {
      limitInfo = {
        requests: 0,
        windowStart: now,
        lastRequest: 0,
        burstCount: 0
      };
      this.limits.set(key, limitInfo);
    }

    // Reset window if expired
    if (now - limitInfo.windowStart >= this.config.windowSizeMs) {
      limitInfo.requests = 0;
      limitInfo.windowStart = now;
      limitInfo.burstCount = 0;
    }

    // Check burst limit
    const timeSinceLastRequest = now - limitInfo.lastRequest;
    if (timeSinceLastRequest < 1000) { // Less than 1 second
      limitInfo.burstCount++;
      if (limitInfo.burstCount > this.config.burstLimit) {
        return {
          allowed: false,
          retryAfter: 1000 - timeSinceLastRequest
        };
      }
    } else {
      limitInfo.burstCount = 0;
    }

    // Check rate limit
    if (limitInfo.requests >= this.config.maxRequestsPerMinute) {
      const resetTime = limitInfo.windowStart + this.config.windowSizeMs;
      return {
        allowed: false,
        retryAfter: resetTime - now
      };
    }

    // Update counters
    limitInfo.requests++;
    limitInfo.lastRequest = now;

    return {
      allowed: true,
      remaining: this.config.maxRequestsPerMinute - limitInfo.requests,
      resetTime: limitInfo.windowStart + this.config.windowSizeMs
    };
  }

  cleanup(): void {
    const now = Date.now();
    const expiredThreshold = now - (this.config.windowSizeMs * 2);

    for (const [key, limitInfo] of this.limits) {
      if (limitInfo.windowStart < expiredThreshold) {
        this.limits.delete(key);
      }
    }
  }
}
```

---

## 📊 **Performance Monitoring**

### **Metrics Collection**

```typescript
class WebSocketMetricsCollector {
  private metrics: WebSocketMetrics = {
    connections: {
      total: 0,
      active: 0,
      peak: 0
    },
    messages: {
      sent: 0,
      received: 0,
      failed: 0,
      avgLatency: 0
    },
    subscriptions: {
      total: 0,
      active: 0
    },
    errors: {
      count: 0,
      types: new Map()
    }
  };

  recordConnection(clientId: string): void {
    this.metrics.connections.total++;
    this.metrics.connections.active++;
    
    if (this.metrics.connections.active > this.metrics.connections.peak) {
      this.metrics.connections.peak = this.metrics.connections.active;
    }
  }

  recordDisconnection(clientId: string): void {
    this.metrics.connections.active = Math.max(0, this.metrics.connections.active - 1);
  }

  recordMessageSent(clientId: string, messageSize: number): void {
    this.metrics.messages.sent++;
  }

  recordMessageReceived(clientId: string, messageSize: number): void {
    this.metrics.messages.received++;
  }

  recordBroadcast(broadcastInfo: BroadcastInfo): void {
    this.metrics.messages.sent += broadcastInfo.deliveredCount;
    this.metrics.messages.failed += broadcastInfo.failedCount;
    
    // Update average latency (simple moving average)
    const currentAvg = this.metrics.messages.avgLatency;
    const newCount = this.metrics.messages.sent;
    this.metrics.messages.avgLatency = 
      (currentAvg * (newCount - broadcastInfo.deliveredCount) + 
       broadcastInfo.latency * broadcastInfo.deliveredCount) / newCount;
  }

  recordError(error: Error, context: string): void {
    this.metrics.errors.count++;
    
    const errorType = error.constructor.name;
    const currentCount = this.metrics.errors.types.get(errorType) || 0;
    this.metrics.errors.types.set(errorType, currentCount + 1);
  }

  getMetrics(): WebSocketMetrics {
    return { ...this.metrics };
  }

  generateReport(): MetricsReport {
    const uptime = process.uptime();
    const memoryUsage = process.memoryUsage();
    
    return {
      timestamp: Date.now(),
      uptime,
      memoryUsage,
      websocket: this.metrics,
      performance: {
        connectionsPerSecond: this.metrics.connections.total / uptime,
        messagesPerSecond: this.metrics.messages.sent / uptime,
        errorRate: this.metrics.errors.count / this.metrics.messages.sent,
        avgLatency: this.metrics.messages.avgLatency
      }
    };
  }
}
```

### **Health Monitoring**

```typescript
class WebSocketHealthMonitor {
  private server: ObservatoryWebSocketServer;
  private metrics: WebSocketMetricsCollector;
  private healthCheckInterval: NodeJS.Timeout;

  constructor(server: ObservatoryWebSocketServer, metrics: WebSocketMetricsCollector) {
    this.server = server;
    this.metrics = metrics;
  }

  startMonitoring(): void {
    this.healthCheckInterval = setInterval(() => {
      this.performHealthCheck();
    }, 30000); // Every 30 seconds
  }

  stopMonitoring(): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }
  }

  performHealthCheck(): HealthStatus {
    const metrics = this.metrics.getMetrics();
    const memoryUsage = process.memoryUsage();
    
    const health: HealthStatus = {
      status: 'healthy',
      checks: [],
      timestamp: Date.now()
    };

    // Check memory usage
    const memoryUsageMB = memoryUsage.heapUsed / 1024 / 1024;
    if (memoryUsageMB > 1024) { // 1GB
      health.status = 'warning';
      health.checks.push({
        name: 'memory_usage',
        status: 'warning',
        message: `High memory usage: ${memoryUsageMB.toFixed(2)}MB`
      });
    }

    // Check error rate
    const errorRate = metrics.errors.count / metrics.messages.sent;
    if (errorRate > 0.05) { // 5%
      health.status = 'unhealthy';
      health.checks.push({
        name: 'error_rate',
        status: 'critical',
        message: `High error rate: ${(errorRate * 100).toFixed(2)}%`
      });
    }

    // Check average latency
    if (metrics.messages.avgLatency > 100) { // 100ms
      health.status = health.status === 'healthy' ? 'warning' : health.status;
      health.checks.push({
        name: 'latency',
        status: 'warning',
        message: `High average latency: ${metrics.messages.avgLatency.toFixed(2)}ms`
      });
    }

    // Check connection count
    if (metrics.connections.active === 0) {
      health.checks.push({
        name: 'connections',
        status: 'info',
        message: 'No active connections'
      });
    }

    return health;
  }
}
```

---

## 🌐 **Client-Side Implementation**

### **WebSocket Client with Reconnection**

```typescript
class ObservatoryWebSocketClient extends EventEmitter {
  private ws: WebSocket | null = null;
  private url: string;
  private options: ClientOptions;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 1000;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private isManualClose = false;

  constructor(url: string, options: ClientOptions = {}) {
    super();
    this.url = url;
    this.options = {
      autoReconnect: true,
      heartbeatInterval: 30000,
      maxReconnectDelay: 30000,
      ...options
    };
  }

  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url, this.options.protocols);
        
        this.ws.onopen = () => {
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          this.emit('connected');
          resolve();
        };

        this.ws.onmessage = (event) => {
          this.handleMessage(event);
        };

        this.ws.onclose = (event) => {
          this.handleClose(event);
        };

        this.ws.onerror = (error) => {
          this.emit('error', error);
          reject(error);
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const message = JSON.parse(event.data);
      this.emit('message', message);
      
      // Handle specific message types
      switch (message.type) {
        case 'connection_established':
          this.emit('connection_established', message.data);
          break;
        case 'pong':
          this.emit('pong', message.data);
          break;
        case 'error':
          this.emit('server_error', message.data);
          break;
        default:
          this.emit(message.type, message.data);
      }
    } catch (error) {
      this.emit('error', new Error('Failed to parse message'));
    }
  }

  private handleClose(event: CloseEvent): void {
    this.stopHeartbeat();
    this.emit('disconnected', { code: event.code, reason: event.reason });

    if (!this.isManualClose && this.options.autoReconnect) {
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      this.emit('reconnect_failed');
      return;
    }

    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts),
      this.options.maxReconnectDelay!
    );

    this.reconnectAttempts++;
    
    setTimeout(() => {
      this.emit('reconnecting', { attempt: this.reconnectAttempts });
      this.connect().catch(() => {
        // Will retry again due to close event
      });
    }, delay);
  }

  private startHeartbeat(): void {
    if (this.options.heartbeatInterval && this.options.heartbeatInterval > 0) {
      this.heartbeatInterval = setInterval(() => {
        this.ping();
      }, this.options.heartbeatInterval);
    }
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  public send(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      throw new Error('WebSocket is not connected');
    }
  }

  public subscribe(filters: SubscriptionFilters): void {
    this.send({
      type: 'subscribe',
      data: { filters }
    });
  }

  public unsubscribe(filters?: SubscriptionFilters): void {
    this.send({
      type: 'unsubscribe',
      data: { filters }
    });
  }

  public ping(): void {
    this.send({
      type: 'ping',
      data: { timestamp: Date.now() }
    });
  }

  public close(): void {
    this.isManualClose = true;
    this.stopHeartbeat();
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
    }
  }

  public isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}
```

---

## 🧪 **Testing Strategy**

### **WebSocket Integration Tests**

```typescript
describe('WebSocket Integration Tests', () => {
  let server: ObservatoryWebSocketServer;
  let client: ObservatoryWebSocketClient;

  beforeAll(async () => {
    server = new ObservatoryWebSocketServer({
      port: 8081,
      authenticationRequired: false
    });
    await server.start();
  });

  afterAll(async () => {
    await server.stop();
  });

  beforeEach(async () => {
    client = new ObservatoryWebSocketClient('ws://localhost:8081');
    await client.connect();
  });

  afterEach(() => {
    client.close();
  });

  describe('Connection Management', () => {
    it('should establish connection successfully', async () => {
      const connectionEvent = await waitForEvent(client, 'connection_established');
      expect(connectionEvent.clientId).toBeDefined();
      expect(connectionEvent.serverTime).toBeCloseTo(Date.now(), -2);
    });

    it('should handle reconnection after disconnection', async () => {
      // Force disconnect
      client.ws.close();
      
      const reconnectEvent = await waitForEvent(client, 'reconnecting');
      expect(reconnectEvent.attempt).toBe(1);
      
      const connectedEvent = await waitForEvent(client, 'connected');
      expect(client.isConnected()).toBe(true);
    });
  });

  describe('Message Broadcasting', () => {
    it('should broadcast messages to subscribed clients', async () => {
      // Subscribe to project events
      client.subscribe({
        projectIds: [1],
        eventTypes: ['message_added']
      });

      await waitForEvent(client, 'subscription_confirmed');

      // Simulate a message added event
      const testEvent = {
        type: 'message_added',
        data: {
          conversationId: 'test-conv-1',
          message: {
            id: 'msg-1',
            content: 'Hello world',
            type: 'user'
          },
          projectInfo: { id: 1, name: 'Test Project' }
        },
        timestamp: Date.now()
      };

      server.broadcast(testEvent);

      const receivedEvent = await waitForEvent(client, 'message_added');
      expect(receivedEvent.conversationId).toBe('test-conv-1');
      expect(receivedEvent.message.content).toBe('Hello world');
    });

    it('should handle broadcast latency requirements', async () => {
      const clients = [];
      const messagePromises = [];

      // Create 50 concurrent clients
      for (let i = 0; i < 50; i++) {
        const testClient = new ObservatoryWebSocketClient('ws://localhost:8081');
        await testClient.connect();
        
        testClient.subscribe({
          eventTypes: ['test_event']
        });
        
        clients.push(testClient);
        messagePromises.push(waitForEvent(testClient, 'test_event'));
      }

      const startTime = Date.now();

      // Broadcast test event
      server.broadcast({
        type: 'test_event',
        data: { message: 'Performance test' },
        timestamp: Date.now()
      });

      // Wait for all clients to receive message
      await Promise.all(messagePromises);
      
      const totalLatency = Date.now() - startTime;
      
      // Should complete within 50ms
      expect(totalLatency).toBeLessThan(50);

      // Cleanup
      clients.forEach(client => client.close());
    });
  });

  describe('Subscription Management', () => {
    it('should filter events based on subscriptions', async () => {
      let receivedMessages = 0;
      
      client.on('message_added', () => {
        receivedMessages++;
      });

      // Subscribe only to project 1
      client.subscribe({
        projectIds: [1],
        eventTypes: ['message_added']
      });

      await waitForEvent(client, 'subscription_confirmed');

      // Send events for different projects
      server.broadcast(createTestEvent('message_added', { projectId: 1 }));
      server.broadcast(createTestEvent('message_added', { projectId: 2 }));
      server.broadcast(createTestEvent('message_added', { projectId: 1 }));

      await sleep(100);

      // Should only receive events for project 1
      expect(receivedMessages).toBe(2);
    });
  });

  describe('Error Handling', () => {
    it('should handle malformed messages gracefully', async () => {
      const errorPromise = waitForEvent(client, 'server_error');
      
      // Send invalid JSON
      client.ws.send('invalid json');
      
      const error = await errorPromise;
      expect(error.code).toBe('INVALID_MESSAGE');
    });

    it('should enforce rate limiting', async () => {
      const promises = [];
      
      // Send 200 messages rapidly (exceeding limit)
      for (let i = 0; i < 200; i++) {
        promises.push(
          client.send({
            type: 'ping',
            data: { timestamp: Date.now() }
          })
        );
      }

      const errorPromise = waitForEvent(client, 'server_error');
      const error = await errorPromise;
      
      expect(error.code).toBe('RATE_LIMIT_EXCEEDED');
    });
  });
});
```

---

## 🚀 **Deployment Configuration**

### **Production WebSocket Configuration**

```typescript
const productionConfig: WebSocketConfig = {
  port: parseInt(process.env.WS_PORT || '8080'),
  maxConnections: parseInt(process.env.WS_MAX_CONNECTIONS || '1000'),
  heartbeatInterval: 30000,
  messageRateLimit: 100,
  compressionEnabled: true,
  authenticationRequired: true,
  cors: {
    origin: process.env.ALLOWED_ORIGINS?.split(',') || ['https://ccobservatory.com'],
    credentials: true
  },
  ssl: process.env.NODE_ENV === 'production' ? {
    cert: fs.readFileSync(process.env.SSL_CERT_PATH!),
    key: fs.readFileSync(process.env.SSL_KEY_PATH!)
  } : undefined,
  monitoring: {
    enabled: true,
    metricsInterval: 60000,
    healthCheckInterval: 30000,
    alertThresholds: {
      memoryUsageMB: 1024,
      errorRate: 0.05,
      avgLatencyMs: 100
    }
  },
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    enableAccessLog: true,
    enableErrorLog: true
  }
};
```

This comprehensive WebSocket implementation specification provides the foundation for reliable, high-performance real-time communication in the Claude Code Observatory project.