# Week 11: MVP Integration & End-to-End Testing

## Overview
Integrate all Phase 2 components into a cohesive MVP system, conducting comprehensive end-to-end testing, performance optimization, and user acceptance validation. This week ensures all systems work together seamlessly to deliver a functional Claude Code Observatory MVP.

## Table of Contents
1. [Full-Stack Integration Patterns](#full-stack-integration-patterns)
2. [API Client Implementation & Error Handling](#api-client-implementation--error-handling)
3. [Real-Time Data Synchronization](#real-time-data-synchronization)
4. [Performance Monitoring & Optimization](#performance-monitoring--optimization)
5. [Production Deployment Configurations](#production-deployment-configurations)
6. [Integration Testing Strategies](#integration-testing-strategies)
7. [Team Assignments & Daily Schedule](#team-assignments--daily-schedule)
8. [Technical Implementation Details](#technical-implementation-details)

## Full-Stack Integration Patterns

### 1. Service Layer Integration Architecture

```typescript
// packages/core/src/integration/service-orchestrator.ts
import { EventEmitter } from 'events';
import { Logger } from '../utils/logger';
import { ServiceRegistry } from './service-registry';
import { HealthChecker } from './health-checker';

export interface ServiceDefinition {
  name: string;
  instance: any;
  dependencies: string[];
  healthCheck: () => Promise<boolean>;
  startup: () => Promise<void>;
  shutdown: () => Promise<void>;
}

export class ServiceOrchestrator extends EventEmitter {
  private services = new Map<string, ServiceDefinition>();
  private startupOrder: string[] = [];
  private logger = new Logger('ServiceOrchestrator');
  private healthChecker: HealthChecker;

  constructor() {
    super();
    this.healthChecker = new HealthChecker();
  }

  registerService(service: ServiceDefinition): void {
    this.services.set(service.name, service);
    this.logger.info(`Registered service: ${service.name}`);
  }

  async startServices(): Promise<void> {
    this.logger.info('Starting service orchestration...');
    
    // Calculate startup order based on dependencies
    this.startupOrder = this.calculateStartupOrder();
    
    for (const serviceName of this.startupOrder) {
      const service = this.services.get(serviceName);
      if (!service) continue;

      try {
        this.logger.info(`Starting service: ${serviceName}`);
        await service.startup();
        
        // Verify service health
        const isHealthy = await service.healthCheck();
        if (!isHealthy) {
          throw new Error(`Service ${serviceName} failed health check`);
        }
        
        this.emit('serviceStarted', { name: serviceName });
        this.logger.info(`Service ${serviceName} started successfully`);
      } catch (error) {
        this.logger.error(`Failed to start service ${serviceName}:`, error);
        throw error;
      }
    }
    
    this.logger.info('All services started successfully');
  }

  async stopServices(): Promise<void> {
    this.logger.info('Stopping services...');
    
    // Stop in reverse order
    const shutdownOrder = [...this.startupOrder].reverse();
    
    for (const serviceName of shutdownOrder) {
      const service = this.services.get(serviceName);
      if (!service) continue;

      try {
        this.logger.info(`Stopping service: ${serviceName}`);
        await service.shutdown();
        this.emit('serviceStopped', { name: serviceName });
      } catch (error) {
        this.logger.error(`Error stopping service ${serviceName}:`, error);
      }
    }
    
    this.logger.info('All services stopped');
  }

  private calculateStartupOrder(): string[] {
    const visited = new Set<string>();
    const visiting = new Set<string>();
    const order: string[] = [];

    const visit = (serviceName: string) => {
      if (visited.has(serviceName)) return;
      if (visiting.has(serviceName)) {
        throw new Error(`Circular dependency detected: ${serviceName}`);
      }

      visiting.add(serviceName);
      const service = this.services.get(serviceName);
      
      if (service) {
        for (const dependency of service.dependencies) {
          visit(dependency);
        }
      }
      
      visiting.delete(serviceName);
      visited.add(serviceName);
      order.push(serviceName);
    };

    for (const serviceName of this.services.keys()) {
      visit(serviceName);
    }

    return order;
  }
}
```

### 2. Integration Gateway Pattern

```typescript
// packages/backend/src/integration/gateway.ts
import { Request, Response, NextFunction } from 'express';
import { Logger } from '../utils/logger';
import { MetricsCollector } from '../monitoring/metrics';
import { CircuitBreaker } from '../resilience/circuit-breaker';

export interface GatewayConfig {
  timeout: number;
  retryAttempts: number;
  circuitBreakerThreshold: number;
  rateLimitPerMinute: number;
}

export class IntegrationGateway {
  private logger = new Logger('IntegrationGateway');
  private metrics = new MetricsCollector();
  private circuitBreakers = new Map<string, CircuitBreaker>();
  private rateLimitCounters = new Map<string, number>();

  constructor(private config: GatewayConfig) {}

  // Integration middleware for API endpoints
  createIntegrationMiddleware(serviceName: string) {
    return async (req: Request, res: Response, next: NextFunction) => {
      const startTime = Date.now();
      const requestId = req.headers['x-request-id'] as string || this.generateRequestId();
      
      // Set request context
      req.context = {
        requestId,
        serviceName,
        startTime,
        userId: req.user?.id
      };

      this.logger.info(`Gateway request: ${serviceName}`, {
        requestId,
        method: req.method,
        path: req.path,
        userId: req.user?.id
      });

      // Apply rate limiting
      if (this.isRateLimited(req.ip)) {
        return res.status(429).json({
          statusCode: '42900',
          message: 'Rate limit exceeded',
          requestId
        });
      }

      // Check circuit breaker
      const circuitBreaker = this.getCircuitBreaker(serviceName);
      if (circuitBreaker.isOpen()) {
        return res.status(503).json({
          statusCode: '50300',
          message: 'Service temporarily unavailable',
          requestId
        });
      }

      // Continue to next middleware
      next();
    };
  }

  // Response interceptor for consistent error handling
  createResponseInterceptor(serviceName: string) {
    return (req: Request, res: Response, next: NextFunction) => {
      const originalSend = res.send;
      const context = req.context;

      res.send = function(data) {
        const duration = Date.now() - context.startTime;
        
        // Log response
        this.logger.info(`Gateway response: ${serviceName}`, {
          requestId: context.requestId,
          statusCode: res.statusCode,
          duration
        });

        // Record metrics
        this.metrics.recordApiRequest(serviceName, {
          method: req.method,
          path: req.path,
          statusCode: res.statusCode,
          duration,
          userId: context.userId
        });

        // Update circuit breaker
        const circuitBreaker = this.getCircuitBreaker(serviceName);
        if (res.statusCode >= 500) {
          circuitBreaker.recordFailure();
        } else {
          circuitBreaker.recordSuccess();
        }

        return originalSend.call(this, data);
      }.bind(this);

      next();
    };
  }

  private isRateLimited(ip: string): boolean {
    const key = `rate_limit:${ip}`;
    const count = this.rateLimitCounters.get(key) || 0;
    
    if (count >= this.config.rateLimitPerMinute) {
      return true;
    }
    
    this.rateLimitCounters.set(key, count + 1);
    
    // Reset counter after 1 minute
    setTimeout(() => {
      this.rateLimitCounters.delete(key);
    }, 60000);
    
    return false;
  }

  private getCircuitBreaker(serviceName: string): CircuitBreaker {
    if (!this.circuitBreakers.has(serviceName)) {
      this.circuitBreakers.set(serviceName, new CircuitBreaker({
        failureThreshold: this.config.circuitBreakerThreshold,
        resetTimeout: 60000 // 1 minute
      }));
    }
    return this.circuitBreakers.get(serviceName)!;
  }

  private generateRequestId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}
```

### 3. Database Integration Layer

```typescript
// packages/database/src/integration/transaction-manager.ts
import { DatabaseConnection } from '../connection/database-connection';
import { Logger } from '../utils/logger';
import { EventEmitter } from 'events';

export interface TransactionOptions {
  timeout?: number;
  isolation?: 'READ_COMMITTED' | 'REPEATABLE_READ' | 'SERIALIZABLE';
}

export class TransactionManager extends EventEmitter {
  private logger = new Logger('TransactionManager');
  private activeTransactions = new Map<string, any>();

  constructor(private db: DatabaseConnection) {
    super();
  }

  async withTransaction<T>(
    operation: (tx: any) => Promise<T>,
    options: TransactionOptions = {}
  ): Promise<T> {
    const transactionId = this.generateTransactionId();
    const startTime = Date.now();
    
    this.logger.info(`Starting transaction ${transactionId}`, options);
    
    try {
      const tx = await this.db.beginTransaction(options);
      this.activeTransactions.set(transactionId, tx);
      
      this.emit('transactionStarted', { transactionId, options });
      
      const result = await operation(tx);
      
      await tx.commit();
      this.activeTransactions.delete(transactionId);
      
      const duration = Date.now() - startTime;
      this.logger.info(`Transaction ${transactionId} committed`, { duration });
      this.emit('transactionCommitted', { transactionId, duration });
      
      return result;
    } catch (error) {
      this.logger.error(`Transaction ${transactionId} failed:`, error);
      
      const tx = this.activeTransactions.get(transactionId);
      if (tx) {
        try {
          await tx.rollback();
          this.activeTransactions.delete(transactionId);
        } catch (rollbackError) {
          this.logger.error(`Rollback failed for transaction ${transactionId}:`, rollbackError);
        }
      }
      
      this.emit('transactionFailed', { transactionId, error });
      throw error;
    }
  }

  async withDistributedTransaction<T>(
    operations: Array<{
      database: string;
      operation: (tx: any) => Promise<any>;
    }>,
    options: TransactionOptions = {}
  ): Promise<T> {
    const transactionId = this.generateTransactionId();
    const transactions: any[] = [];
    
    this.logger.info(`Starting distributed transaction ${transactionId}`);
    
    try {
      // Begin all transactions
      for (const op of operations) {
        const tx = await this.db.beginTransaction(options);
        transactions.push({ tx, operation: op.operation, database: op.database });
      }
      
      // Execute all operations
      const results = await Promise.all(
        transactions.map(({ tx, operation }) => operation(tx))
      );
      
      // Commit all transactions
      await Promise.all(transactions.map(({ tx }) => tx.commit()));
      
      this.logger.info(`Distributed transaction ${transactionId} completed successfully`);
      return results as T;
      
    } catch (error) {
      this.logger.error(`Distributed transaction ${transactionId} failed:`, error);
      
      // Rollback all transactions
      await Promise.all(
        transactions.map(async ({ tx, database }) => {
          try {
            await tx.rollback();
          } catch (rollbackError) {
            this.logger.error(`Rollback failed for ${database}:`, rollbackError);
          }
        })
      );
      
      throw error;
    }
  }

  private generateTransactionId(): string {
    return `tx_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}
```

## API Client Implementation & Error Handling

### 1. Robust API Client with Retry Logic

```typescript
// packages/core/src/api/api-client.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { Logger } from '../utils/logger';
import { EventEmitter } from 'events';

export interface ApiClientConfig {
  baseURL: string;
  timeout: number;
  maxRetries: number;
  retryDelay: number;
  retryBackoffMultiplier: number;
}

export interface ApiError {
  statusCode: string;
  message: string;
  details?: any;
  timestamp: string;
  requestId?: string;
}

export class ApiClient extends EventEmitter {
  private client: AxiosInstance;
  private logger = new Logger('ApiClient');
  private requestQueue = new Map<string, Promise<any>>();

  constructor(private config: ApiClientConfig) {
    super();
    this.client = this.createAxiosInstance();
  }

  private createAxiosInstance(): AxiosInstance {
    const instance = axios.create({
      baseURL: this.config.baseURL,
      timeout: this.config.timeout,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'CCObservatory-Client/1.0'
      }
    });

    // Request interceptor
    instance.interceptors.request.use(
      (config) => {
        const requestId = this.generateRequestId();
        config.headers = {
          ...config.headers,
          'x-request-id': requestId
        };
        
        this.logger.info(`API Request: ${config.method?.toUpperCase()} ${config.url}`, {
          requestId,
          data: config.data
        });
        
        return config;
      },
      (error) => {
        this.logger.error('Request interceptor error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    instance.interceptors.response.use(
      (response) => {
        const requestId = response.config.headers?.['x-request-id'];
        this.logger.info(`API Response: ${response.status} ${response.config.url}`, {
          requestId,
          status: response.status
        });
        
        return response;
      },
      (error) => {
        this.handleResponseError(error);
        return Promise.reject(error);
      }
    );

    return instance;
  }

  async request<T>(
    config: AxiosRequestConfig,
    options: { dedupe?: boolean } = {}
  ): Promise<T> {
    const requestKey = this.generateRequestKey(config);
    
    // Request deduplication
    if (options.dedupe && this.requestQueue.has(requestKey)) {
      return this.requestQueue.get(requestKey);
    }

    const requestPromise = this.executeWithRetry<T>(config);
    
    if (options.dedupe) {
      this.requestQueue.set(requestKey, requestPromise);
      requestPromise.finally(() => {
        this.requestQueue.delete(requestKey);
      });
    }

    return requestPromise;
  }

  private async executeWithRetry<T>(config: AxiosRequestConfig): Promise<T> {
    let lastError: any;
    
    for (let attempt = 0; attempt <= this.config.maxRetries; attempt++) {
      try {
        const response = await this.client.request(config);
        return response.data;
      } catch (error) {
        lastError = error;
        
        if (attempt === this.config.maxRetries || !this.isRetryableError(error)) {
          throw this.normalizeError(error);
        }
        
        const delay = this.calculateRetryDelay(attempt);
        this.logger.warn(`Request failed, retrying in ${delay}ms (attempt ${attempt + 1}/${this.config.maxRetries})`, {
          error: error.message,
          config: config.url
        });
        
        await this.sleep(delay);
      }
    }
    
    throw this.normalizeError(lastError);
  }

  private isRetryableError(error: any): boolean {
    if (!error.response) return true; // Network errors
    
    const status = error.response.status;
    return status >= 500 || status === 429 || status === 408;
  }

  private calculateRetryDelay(attempt: number): number {
    const baseDelay = this.config.retryDelay;
    const backoffMultiplier = this.config.retryBackoffMultiplier;
    return baseDelay * Math.pow(backoffMultiplier, attempt);
  }

  private normalizeError(error: any): ApiError {
    const normalized: ApiError = {
      statusCode: '50000',
      message: 'Unknown error',
      timestamp: new Date().toISOString()
    };

    if (error.response) {
      // Server responded with error status
      const data = error.response.data;
      normalized.statusCode = data.statusCode || error.response.status.toString();
      normalized.message = data.message || error.response.statusText;
      normalized.details = data.details;
      normalized.requestId = data.requestId;
    } else if (error.request) {
      // Network error
      normalized.statusCode = '50001';
      normalized.message = 'Network error';
      normalized.details = { code: error.code };
    } else {
      // Other error
      normalized.message = error.message;
    }

    return normalized;
  }

  private generateRequestKey(config: AxiosRequestConfig): string {
    return `${config.method}:${config.url}:${JSON.stringify(config.data)}`;
  }

  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private handleResponseError(error: any): void {
    const requestId = error.config?.headers?.['x-request-id'];
    this.logger.error(`API Error: ${error.config?.url}`, {
      requestId,
      status: error.response?.status,
      message: error.message
    });
    
    this.emit('apiError', {
      requestId,
      url: error.config?.url,
      status: error.response?.status,
      error: error.message
    });
  }
}
```

### 2. Centralized Error Handling

```typescript
// packages/core/src/errors/error-handler.ts
import { Logger } from '../utils/logger';
import { Request, Response, NextFunction } from 'express';

export interface ErrorContext {
  requestId?: string;
  userId?: string;
  operation?: string;
  metadata?: Record<string, any>;
}

export class ErrorHandler {
  private logger = new Logger('ErrorHandler');

  handleError(error: Error, context: ErrorContext = {}): void {
    this.logger.error('Error occurred:', {
      error: error.message,
      stack: error.stack,
      ...context
    });

    // Send to error tracking service
    this.sendToErrorTracking(error, context);
    
    // Emit error event for monitoring
    this.emit('error', { error, context });
  }

  createExpressErrorHandler() {
    return (error: Error, req: Request, res: Response, next: NextFunction) => {
      const context: ErrorContext = {
        requestId: req.headers['x-request-id'] as string,
        userId: req.user?.id,
        operation: `${req.method} ${req.path}`,
        metadata: {
          userAgent: req.headers['user-agent'],
          ip: req.ip,
          body: req.body,
          query: req.query
        }
      };

      this.handleError(error, context);

      // Determine response based on error type
      if (error instanceof ValidationError) {
        return res.status(400).json({
          statusCode: '40000',
          message: 'Validation error',
          details: error.details,
          requestId: context.requestId
        });
      }

      if (error instanceof NotFoundError) {
        return res.status(404).json({
          statusCode: '40400',
          message: 'Resource not found',
          requestId: context.requestId
        });
      }

      if (error instanceof UnauthorizedError) {
        return res.status(401).json({
          statusCode: '40100',
          message: 'Unauthorized',
          requestId: context.requestId
        });
      }

      // Default server error
      res.status(500).json({
        statusCode: '50000',
        message: 'Internal server error',
        requestId: context.requestId
      });
    };
  }

  private sendToErrorTracking(error: Error, context: ErrorContext): void {
    // Implementation depends on error tracking service (e.g., Sentry)
    // This is a placeholder for the actual implementation
    console.error('Error tracked:', { error: error.message, context });
  }

  private emit(event: string, data: any): void {
    // Emit to event system for monitoring
    process.emit('error-occurred', data);
  }
}

// Custom error classes
export class ValidationError extends Error {
  constructor(public details: any) {
    super('Validation failed');
    this.name = 'ValidationError';
  }
}

export class NotFoundError extends Error {
  constructor(resource: string) {
    super(`${resource} not found`);
    this.name = 'NotFoundError';
  }
}

export class UnauthorizedError extends Error {
  constructor(message = 'Unauthorized') {
    super(message);
    this.name = 'UnauthorizedError';
  }
}
```

## Real-Time Data Synchronization

### 1. WebSocket Connection Manager

```typescript
// packages/core/src/realtime/websocket-manager.ts
import { Server as SocketIOServer } from 'socket.io';
import { Server as HTTPServer } from 'http';
import { Logger } from '../utils/logger';
import { EventEmitter } from 'events';
import { RedisAdapter } from '@socket.io/redis-adapter';
import { Redis } from 'ioredis';

export interface WebSocketConfig {
  cors: {
    origin: string | string[];
    credentials: boolean;
  };
  redis: {
    host: string;
    port: number;
    db: number;
  };
  maxConnections: number;
  heartbeatInterval: number;
}

export class WebSocketManager extends EventEmitter {
  private io: SocketIOServer;
  private logger = new Logger('WebSocketManager');
  private connectionCount = 0;
  private userSockets = new Map<string, Set<string>>();
  private redis: Redis;

  constructor(
    private httpServer: HTTPServer,
    private config: WebSocketConfig
  ) {
    super();
    this.redis = new Redis({
      host: config.redis.host,
      port: config.redis.port,
      db: config.redis.db
    });
    
    this.initializeSocketIO();
  }

  private initializeSocketIO(): void {
    this.io = new SocketIOServer(this.httpServer, {
      cors: this.config.cors,
      pingTimeout: 60000,
      pingInterval: 25000,
      transports: ['websocket', 'polling']
    });

    // Setup Redis adapter for scaling
    this.setupRedisAdapter();
    
    // Setup connection handling
    this.setupConnectionHandling();
    
    // Setup heartbeat monitoring
    this.setupHeartbeat();
  }

  private setupRedisAdapter(): void {
    const pubClient = this.redis.duplicate();
    const subClient = this.redis.duplicate();
    
    this.io.adapter(RedisAdapter(pubClient, subClient));
    this.logger.info('Redis adapter initialized for WebSocket scaling');
  }

  private setupConnectionHandling(): void {
    this.io.on('connection', (socket) => {
      this.connectionCount++;
      
      // Check connection limits
      if (this.connectionCount > this.config.maxConnections) {
        this.logger.warn(`Max connections exceeded: ${this.connectionCount}`);
        socket.emit('error', { message: 'Server overloaded' });
        socket.disconnect();
        return;
      }

      this.logger.info(`New WebSocket connection: ${socket.id}`);
      
      // Authentication
      socket.on('authenticate', async (data) => {
        try {
          const user = await this.authenticateUser(data.token);
          socket.userId = user.id;
          socket.user = user;
          
          // Track user connections
          if (!this.userSockets.has(user.id)) {
            this.userSockets.set(user.id, new Set());
          }
          this.userSockets.get(user.id)!.add(socket.id);
          
          socket.emit('authenticated', { user });
          this.logger.info(`User authenticated: ${user.id} on socket ${socket.id}`);
          
          // Join user to personal room
          socket.join(`user:${user.id}`);
          
        } catch (error) {
          this.logger.error('Authentication failed:', error);
          socket.emit('auth_error', { message: 'Authentication failed' });
          socket.disconnect();
        }
      });

      // Subscription management
      socket.on('subscribe', (data) => {
        const { channel, filters } = data;
        
        if (!socket.userId) {
          socket.emit('error', { message: 'Not authenticated' });
          return;
        }
        
        if (this.canSubscribe(socket.userId, channel)) {
          socket.join(channel);
          this.logger.info(`User ${socket.userId} subscribed to ${channel}`);
          
          // Store subscription filters
          socket.subscriptions = socket.subscriptions || {};
          socket.subscriptions[channel] = filters;
          
          socket.emit('subscribed', { channel });
        } else {
          socket.emit('subscription_error', { 
            message: 'Access denied',
            channel 
          });
        }
      });

      socket.on('unsubscribe', (data) => {
        const { channel } = data;
        socket.leave(channel);
        
        if (socket.subscriptions) {
          delete socket.subscriptions[channel];
        }
        
        socket.emit('unsubscribed', { channel });
      });

      // Typing indicators
      socket.on('typing_start', (data) => {
        const { conversationId } = data;
        socket.to(`conversation:${conversationId}`).emit('typing_indicator', {
          userId: socket.userId,
          conversationId,
          isTyping: true
        });
      });

      socket.on('typing_stop', (data) => {
        const { conversationId } = data;
        socket.to(`conversation:${conversationId}`).emit('typing_indicator', {
          userId: socket.userId,
          conversationId,
          isTyping: false
        });
      });

      // Handle disconnection
      socket.on('disconnect', () => {
        this.connectionCount--;
        
        if (socket.userId) {
          const userSockets = this.userSockets.get(socket.userId);
          if (userSockets) {
            userSockets.delete(socket.id);
            if (userSockets.size === 0) {
              this.userSockets.delete(socket.userId);
            }
          }
        }
        
        this.logger.info(`Socket disconnected: ${socket.id}`);
      });
    });
  }

  private setupHeartbeat(): void {
    setInterval(() => {
      this.io.emit('heartbeat', { timestamp: Date.now() });
    }, this.config.heartbeatInterval);
  }

  // Broadcasting methods
  async broadcastToUser(userId: string, event: string, data: any): Promise<void> {
    this.io.to(`user:${userId}`).emit(event, {
      ...data,
      timestamp: Date.now()
    });
    
    this.logger.debug(`Broadcast to user ${userId}: ${event}`);
  }

  async broadcastToChannel(channel: string, event: string, data: any, filters?: any): Promise<void> {
    if (filters) {
      // Apply filters to determine which clients should receive the message
      const sockets = await this.io.in(channel).fetchSockets();
      
      for (const socket of sockets) {
        if (this.matchesFilters(socket, filters)) {
          socket.emit(event, {
            ...data,
            timestamp: Date.now()
          });
        }
      }
    } else {
      this.io.to(channel).emit(event, {
        ...data,
        timestamp: Date.now()
      });
    }
    
    this.logger.debug(`Broadcast to channel ${channel}: ${event}`);
  }

  async broadcastToAll(event: string, data: any): Promise<void> {
    this.io.emit(event, {
      ...data,
      timestamp: Date.now()
    });
    
    this.logger.debug(`Broadcast to all: ${event}`);
  }

  private async authenticateUser(token: string): Promise<any> {
    // Implement JWT token validation
    // This is a placeholder - replace with actual authentication logic
    return { id: 'user123', name: 'Test User' };
  }

  private canSubscribe(userId: string, channel: string): boolean {
    // Implement authorization logic
    // This is a placeholder - replace with actual authorization logic
    return true;
  }

  private matchesFilters(socket: any, filters: any): boolean {
    // Implement filter matching logic
    // This is a placeholder - replace with actual filter logic
    return true;
  }

  getConnectionCount(): number {
    return this.connectionCount;
  }

  getUserConnectionCount(userId: string): number {
    return this.userSockets.get(userId)?.size || 0;
  }
}
```

### 2. Real-Time Data Sync Service

```typescript
// packages/core/src/realtime/sync-service.ts
import { EventEmitter } from 'events';
import { Logger } from '../utils/logger';
import { WebSocketManager } from './websocket-manager';
import { DatabaseConnection } from '../database/database-connection';

export interface SyncEvent {
  type: 'create' | 'update' | 'delete';
  entity: string;
  data: any;
  userId?: string;
  timestamp: number;
}

export class RealTimeSyncService extends EventEmitter {
  private logger = new Logger('RealTimeSyncService');
  private subscriptions = new Map<string, Set<string>>();

  constructor(
    private wsManager: WebSocketManager,
    private db: DatabaseConnection
  ) {
    super();
    this.setupDatabaseChangeListeners();
  }

  private setupDatabaseChangeListeners(): void {
    // Listen for database changes
    this.db.on('change', (change) => {
      this.handleDatabaseChange(change);
    });
  }

  private async handleDatabaseChange(change: any): Promise<void> {
    const syncEvent: SyncEvent = {
      type: change.operation,
      entity: change.table,
      data: change.data,
      userId: change.userId,
      timestamp: Date.now()
    };

    // Determine which channels should receive this update
    const channels = await this.determineChannels(syncEvent);
    
    for (const channel of channels) {
      await this.wsManager.broadcastToChannel(
        channel,
        this.getEventName(syncEvent),
        syncEvent
      );
    }

    this.logger.debug(`Synced change: ${syncEvent.type} ${syncEvent.entity}`);
  }

  private async determineChannels(event: SyncEvent): Promise<string[]> {
    const channels: string[] = [];
    
    switch (event.entity) {
      case 'conversations':
        channels.push(`conversation:${event.data.id}`);
        if (event.data.userId) {
          channels.push(`user:${event.data.userId}`);
        }
        break;
        
      case 'messages':
        channels.push(`conversation:${event.data.conversationId}`);
        if (event.data.userId) {
          channels.push(`user:${event.data.userId}`);
        }
        break;
        
      case 'analytics':
        channels.push('analytics:conversations');
        channels.push('analytics:messages');
        break;
        
      default:
        channels.push(`${event.entity}:changes`);
    }
    
    return channels;
  }

  private getEventName(event: SyncEvent): string {
    switch (event.type) {
      case 'create':
        return `new_${event.entity.slice(0, -1)}`; // Remove 's' from plural
      case 'update':
        return `updated_${event.entity.slice(0, -1)}`;
      case 'delete':
        return `deleted_${event.entity.slice(0, -1)}`;
      default:
        return `${event.entity}_changed`;
    }
  }

  // Manual sync trigger methods
  async syncConversation(conversationId: string, data: any): Promise<void> {
    const syncEvent: SyncEvent = {
      type: 'update',
      entity: 'conversations',
      data: { id: conversationId, ...data },
      timestamp: Date.now()
    };

    await this.wsManager.broadcastToChannel(
      `conversation:${conversationId}`,
      'updated_conversation',
      syncEvent
    );
  }

  async syncMessage(messageData: any): Promise<void> {
    const syncEvent: SyncEvent = {
      type: 'create',
      entity: 'messages',
      data: messageData,
      timestamp: Date.now()
    };

    const channels = [
      `conversation:${messageData.conversationId}`,
      `user:${messageData.userId}`
    ];

    for (const channel of channels) {
      await this.wsManager.broadcastToChannel(
        channel,
        'new_message',
        syncEvent
      );
    }
  }

  async syncAnalytics(analyticsData: any): Promise<void> {
    const syncEvent: SyncEvent = {
      type: 'update',
      entity: 'analytics',
      data: analyticsData,
      timestamp: Date.now()
    };

    await this.wsManager.broadcastToChannel(
      'analytics:conversations',
      'analytics_conversations',
      syncEvent
    );
  }
}
```

## Team Assignments
- **Full-Stack Lead**: End-to-end integration, system orchestration, deployment preparation
- **Backend Developer**: API integration testing, performance optimization, data flow validation
- **Frontend Developer**: UI/UX integration, user flow testing, responsive design validation
- **QA Engineer**: Comprehensive testing, bug tracking, acceptance criteria validation

## Daily Schedule

### Monday: System Integration & API Orchestration
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Backend service integration and health monitoring
- **10:30-12:00**: Frontend-backend API integration validation

#### Afternoon (4 hours)
- **13:00-15:00**: WebSocket real-time feature integration testing
- **15:00-17:00**: Analytics pipeline end-to-end integration

### Tuesday: User Flow & Experience Testing
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Complete user journey testing (onboarding to insights)
- **10:30-12:00**: Conversation management workflow validation

#### Afternoon (4 hours)
- **13:00-15:00**: Real-time collaboration features testing
- **15:00-17:00**: Dashboard and analytics user experience validation

### Wednesday: Performance Optimization & Load Testing
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Database query optimization and indexing
- **10:30-12:00**: Frontend performance optimization and code splitting

#### Afternoon (4 hours)
- **13:00-15:00**: Load testing with simulated user scenarios
- **15:00-17:00**: Memory usage optimization and leak detection

### Thursday: Cross-Platform & Browser Testing
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Cross-browser compatibility testing (Chrome, Firefox, Safari, Edge)
- **10:30-12:00**: Mobile and tablet responsive design validation

#### Afternoon (4 hours)
- **13:00-15:00**: Operating system compatibility testing
- **15:00-17:00**: Accessibility compliance validation (WCAG 2.1 AA)

### Friday: MVP Validation & Deployment Preparation
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Final acceptance criteria validation
- **10:30-12:00**: Security audit and vulnerability assessment

#### Afternoon (4 hours)
- **13:00-15:00**: Production deployment preparation and configuration
- **15:00-17:00**: Documentation finalization and handoff preparation

## Technical Implementation Details

### Integration Test Suite
```typescript
// tests/integration/mvp-integration.test.ts
import { describe, test, expect, beforeAll, afterAll } from 'vitest';
import { TestApplication } from './helpers/test-application';
import { TestDataGenerator } from './helpers/test-data-generator';
import { WebSocketClient } from '@/services/websocket';
import { ApiClient } from '@/services/api';

describe('MVP Integration Tests', () => {
  let app: TestApplication;
  let apiClient: ApiClient;
  let wsClient: WebSocketClient;
  let testData: TestDataGenerator;

  beforeAll(async () => {
    app = new TestApplication();
    await app.start();
    
    apiClient = new ApiClient(app.getApiUrl());
    wsClient = new WebSocketClient(app.getWsUrl());
    testData = new TestDataGenerator();
  });

  afterAll(async () => {
    await wsClient.disconnect();
    await app.stop();
  });

  describe('Complete User Journey', () => {
    test('should handle full conversation lifecycle', async () => {
      // 1. User authentication
      const user = await testData.createTestUser();
      const authToken = await apiClient.authenticate(user.credentials);
      expect(authToken).toBeDefined();

      // 2. Create conversation
      const conversationData = testData.generateConversationData();
      const conversation = await apiClient.createConversation(conversationData);
      expect(conversation.id).toBeDefined();

      // 3. Establish WebSocket connection
      await wsClient.connect(authToken);
      const connectionEstablished = await wsClient.waitForConnection();
      expect(connectionEstablished).toBe(true);

      // 4. Subscribe to conversation updates
      await wsClient.subscribe(`conversation:${conversation.id}`);

      // 5. Send messages and verify real-time updates
      const messages = testData.generateMessages(10);
      const receivedUpdates: any[] = [];

      wsClient.on('new_message', (data) => {
        receivedUpdates.push(data);
      });

      for (const messageData of messages) {
        const message = await apiClient.sendMessage(conversation.id, messageData);
        expect(message.id).toBeDefined();
      }

      // Wait for real-time updates
      await new Promise(resolve => setTimeout(resolve, 2000));
      expect(receivedUpdates).toHaveLength(messages.length);

      // 6. Verify analytics data
      const analytics = await apiClient.getConversationAnalytics(conversation.id);
      expect(analytics.messageCount).toBe(messages.length);
      expect(analytics.totalTokens).toBeGreaterThan(0);

      // 7. Test dashboard data
      const dashboardData = await apiClient.getDashboardData();
      expect(dashboardData.overview.totalConversations).toBeGreaterThan(0);
      expect(dashboardData.overview.totalMessages).toBeGreaterThan(0);
    });

    test('should handle concurrent users and conversations', async () => {
      const userCount = 5;
      const conversationsPerUser = 3;
      const messagesPerConversation = 10;

      const users = await Promise.all(
        Array.from({ length: userCount }, () => testData.createTestUser())
      );

      const authTokens = await Promise.all(
        users.map(user => apiClient.authenticate(user.credentials))
      );

      // Create conversations concurrently
      const conversationPromises = authTokens.flatMap((token, userIndex) =>
        Array.from({ length: conversationsPerUser }, async () => {
          const conversationData = testData.generateConversationData();
          return await apiClient.createConversation(conversationData, token);
        })
      );

      const conversations = await Promise.all(conversationPromises);
      expect(conversations).toHaveLength(userCount * conversationsPerUser);

      // Send messages concurrently
      const messagePromises = conversations.flatMap(conversation =>
        Array.from({ length: messagesPerConversation }, async () => {
          const messageData = testData.generateMessageData();
          return await apiClient.sendMessage(conversation.id, messageData);
        })
      );

      const messages = await Promise.all(messagePromises);
      expect(messages).toHaveLength(userCount * conversationsPerUser * messagesPerConversation);

      // Verify system metrics
      const systemMetrics = await apiClient.getSystemMetrics();
      expect(systemMetrics.totalConversations).toBeGreaterThanOrEqual(userCount * conversationsPerUser);
      expect(systemMetrics.totalMessages).toBeGreaterThanOrEqual(messages.length);
      expect(systemMetrics.activeUsers).toBeGreaterThanOrEqual(userCount);
    });
  });

  describe('Real-Time Features', () => {
    test('should handle typing indicators', async () => {
      const user1 = await testData.createTestUser();
      const user2 = await testData.createTestUser();
      
      const token1 = await apiClient.authenticate(user1.credentials);
      const token2 = await apiClient.authenticate(user2.credentials);

      const conversation = await apiClient.createConversation(
        testData.generateConversationData(),
        token1
      );

      // Connect both users
      const ws1 = new WebSocketClient(app.getWsUrl());
      const ws2 = new WebSocketClient(app.getWsUrl());

      await ws1.connect(token1);
      await ws2.connect(token2);

      await ws1.subscribe(`conversation:${conversation.id}`);
      await ws2.subscribe(`conversation:${conversation.id}`);

      // Test typing indicator
      const typingEvents: any[] = [];
      ws2.on('typing_indicator', (data) => {
        typingEvents.push(data);
      });

      // User 1 starts typing
      await ws1.send('typing_start', { conversationId: conversation.id });
      
      // Wait for event propagation
      await new Promise(resolve => setTimeout(resolve, 500));
      
      expect(typingEvents).toHaveLength(1);
      expect(typingEvents[0].userId).toBe(user1.id);
      expect(typingEvents[0].isTyping).toBe(true);

      // User 1 stops typing
      await ws1.send('typing_stop', { conversationId: conversation.id });
      
      await new Promise(resolve => setTimeout(resolve, 500));
      
      expect(typingEvents).toHaveLength(2);
      expect(typingEvents[1].isTyping).toBe(false);

      await ws1.disconnect();
      await ws2.disconnect();
    });

    test('should handle presence updates', async () => {
      const users = await Promise.all([
        testData.createTestUser(),
        testData.createTestUser(),
        testData.createTestUser()
      ]);

      const tokens = await Promise.all(
        users.map(user => apiClient.authenticate(user.credentials))
      );

      const wsClients = tokens.map(() => new WebSocketClient(app.getWsUrl()));
      
      // Connect users sequentially
      const presenceEvents: any[] = [];
      wsClients[0].on('user_presence', (data) => {
        presenceEvents.push(data);
      });

      await wsClients[0].connect(tokens[0]);

      for (let i = 1; i < wsClients.length; i++) {
        await wsClients[i].connect(tokens[i]);
        await new Promise(resolve => setTimeout(resolve, 200));
      }

      // Verify presence events were received
      expect(presenceEvents.length).toBeGreaterThan(0);
      
      // Disconnect users and verify offline events
      for (const client of wsClients) {
        await client.disconnect();
      }
    });
  });

  describe('Analytics Integration', () => {
    test('should accurately track and aggregate metrics', async () => {
      const user = await testData.createTestUser();
      const token = await apiClient.authenticate(user.credentials);

      // Create multiple conversations with varying message counts
      const conversationConfigs = [
        { messageCount: 5, tokenCount: 1000 },
        { messageCount: 10, tokenCount: 2500 },
        { messageCount: 3, tokenCount: 500 }
      ];

      const conversations = [];
      for (const config of conversationConfigs) {
        const conversation = await apiClient.createConversation(
          testData.generateConversationData(),
          token
        );

        const messages = testData.generateMessages(config.messageCount);
        for (const messageData of messages) {
          messageData.tokenCount = Math.floor(config.tokenCount / config.messageCount);
          await apiClient.sendMessage(conversation.id, messageData, token);
        }

        conversations.push({ ...conversation, ...config });
      }

      // Wait for analytics processing
      await new Promise(resolve => setTimeout(resolve, 3000));

      // Verify conversation-level metrics
      for (const conv of conversations) {
        const metrics = await apiClient.getConversationAnalytics(conv.id);
        expect(metrics.messageCount).toBe(conv.messageCount);
        expect(metrics.totalTokens).toBeCloseTo(conv.tokenCount, -2); // Within 100 tokens
      }

      // Verify user-level metrics
      const userMetrics = await apiClient.getUserMetrics(user.id);
      expect(userMetrics.conversationCount).toBe(conversationConfigs.length);
      expect(userMetrics.totalMessages).toBe(
        conversationConfigs.reduce((sum, config) => sum + config.messageCount, 0)
      );

      // Verify system-level metrics
      const systemMetrics = await apiClient.getSystemMetrics();
      expect(systemMetrics.totalConversations).toBeGreaterThanOrEqual(conversationConfigs.length);
      expect(systemMetrics.averageConversationLength).toBeGreaterThan(0);
    });

    test('should provide real-time analytics updates', async () => {
      const user = await testData.createTestUser();
      const token = await apiClient.authenticate(user.credentials);

      const wsClient = new WebSocketClient(app.getWsUrl());
      await wsClient.connect(token);

      const analyticsUpdates: any[] = [];
      wsClient.on('analytics_conversations', (data) => {
        analyticsUpdates.push(data);
      });

      // Subscribe to analytics updates
      await wsClient.subscribe('analytics:conversations');

      // Create conversation to trigger analytics update
      const conversation = await apiClient.createConversation(
        testData.generateConversationData(),
        token
      );

      // Wait for analytics update
      await new Promise(resolve => setTimeout(resolve, 2000));

      expect(analyticsUpdates.length).toBeGreaterThan(0);
      
      await wsClient.disconnect();
    });
  });

  describe('Error Handling & Recovery', () => {
    test('should handle API errors gracefully', async () => {
      // Test with invalid authentication
      const invalidClient = new ApiClient(app.getApiUrl());
      
      await expect(
        invalidClient.createConversation(testData.generateConversationData(), 'invalid-token')
      ).rejects.toThrow();

      // Test with non-existent resources
      const user = await testData.createTestUser();
      const token = await apiClient.authenticate(user.credentials);

      await expect(
        apiClient.getConversation('non-existent-id', token)
      ).rejects.toThrow();

      await expect(
        apiClient.sendMessage('non-existent-id', testData.generateMessageData(), token)
      ).rejects.toThrow();
    });

    test('should handle WebSocket connection failures', async () => {
      const user = await testData.createTestUser();
      const token = await apiClient.authenticate(user.credentials);

      const wsClient = new WebSocketClient('ws://invalid-url:9999');
      
      let connectionError = false;
      wsClient.on('error', () => {
        connectionError = true;
      });

      try {
        await wsClient.connect(token);
      } catch (error) {
        connectionError = true;
      }

      expect(connectionError).toBe(true);
    });

    test('should recover from temporary service interruptions', async () => {
      const user = await testData.createTestUser();
      const token = await apiClient.authenticate(user.credentials);

      const conversation = await apiClient.createConversation(
        testData.generateConversationData(),
        token
      );

      // Simulate service interruption by creating messages rapidly
      const rapidMessages = Array.from({ length: 50 }, () => 
        testData.generateMessageData()
      );

      const results = await Promise.allSettled(
        rapidMessages.map(messageData =>
          apiClient.sendMessage(conversation.id, messageData, token)
        )
      );

      const successful = results.filter(result => result.status === 'fulfilled');
      const failed = results.filter(result => result.status === 'rejected');

      // Most messages should succeed, some may fail due to rate limiting
      expect(successful.length).toBeGreaterThan(rapidMessages.length * 0.8);
      
      // System should remain stable
      const finalMetrics = await apiClient.getConversationAnalytics(conversation.id);
      expect(finalMetrics.messageCount).toBe(successful.length);
    });
  });
});
```

### Performance Test Suite
```typescript
// tests/performance/mvp-performance.test.ts
import { describe, test, expect } from 'vitest';
import { PerformanceTestRunner } from './helpers/performance-runner';
import { LoadTestScenario } from './helpers/load-test-scenario';

describe('MVP Performance Tests', () => {
  const perfRunner = new PerformanceTestRunner();

  test('should handle 100 concurrent users', async () => {
    const scenario = new LoadTestScenario({
      userCount: 100,
      rampUpTime: 60000, // 1 minute
      testDuration: 300000, // 5 minutes
      actions: [
        { type: 'login', weight: 1 },
        { type: 'createConversation', weight: 0.3 },
        { type: 'sendMessage', weight: 2 },
        { type: 'viewDashboard', weight: 0.5 },
        { type: 'exportData', weight: 0.1 }
      ]
    });

    const results = await perfRunner.runScenario(scenario);

    // Performance requirements
    expect(results.averageResponseTime).toBeLessThan(500); // 500ms average
    expect(results.p95ResponseTime).toBeLessThan(2000); // 2s 95th percentile
    expect(results.errorRate).toBeLessThan(0.01); // <1% error rate
    expect(results.throughput).toBeGreaterThan(10); // >10 requests/second
    
    // Resource usage
    expect(results.maxMemoryUsage).toBeLessThan(1024 * 1024 * 1024); // <1GB
    expect(results.maxCpuUsage).toBeLessThan(80); // <80% CPU

    // Database performance
    expect(results.averageDbQueryTime).toBeLessThan(100); // 100ms average
    expect(results.connectionPoolUtilization).toBeLessThan(0.8); // <80% pool usage
  });

  test('should handle large conversation processing', async () => {
    const largeConversationTest = async () => {
      const startTime = performance.now();
      
      // Create conversation with 1000 messages
      const conversation = await perfRunner.createLargeConversation({
        messageCount: 1000,
        averageMessageLength: 500,
        includeCodeBlocks: true
      });

      const processingTime = performance.now() - startTime;
      
      // Verify analytics calculation performance
      const analyticsStartTime = performance.now();
      const analytics = await perfRunner.getConversationAnalytics(conversation.id);
      const analyticsTime = performance.now() - analyticsStartTime;

      return {
        processingTime,
        analyticsTime,
        analytics
      };
    };

    const result = await largeConversationTest();

    // Processing should complete within reasonable time
    expect(result.processingTime).toBeLessThan(30000); // 30 seconds
    expect(result.analyticsTime).toBeLessThan(5000); // 5 seconds

    // Analytics should be accurate
    expect(result.analytics.messageCount).toBe(1000);
    expect(result.analytics.totalTokens).toBeGreaterThan(0);
  });

  test('should handle real-time updates under load', async () => {
    const realtimeLoadTest = async () => {
      const connectionCount = 50;
      const messageRate = 10; // messages per second per connection
      const testDuration = 60000; // 1 minute

      const connections = await perfRunner.createWebSocketConnections(connectionCount);
      
      const startTime = performance.now();
      const messagesSent: number[] = [];
      const messagesReceived: number[] = [];
      const latencies: number[] = [];

      // Start sending messages from all connections
      const sendingPromises = connections.map(async (conn, index) => {
        const conversation = await perfRunner.createConversation();
        await conn.subscribe(`conversation:${conversation.id}`);

        let sentCount = 0;
        let receivedCount = 0;

        conn.on('new_message', (data) => {
          const latency = Date.now() - data.timestamp;
          latencies.push(latency);
          receivedCount++;
        });

        const interval = setInterval(async () => {
          if (performance.now() - startTime > testDuration) {
            clearInterval(interval);
            messagesSent[index] = sentCount;
            messagesReceived[index] = receivedCount;
            return;
          }

          await conn.sendMessage(conversation.id, {
            content: `Test message ${sentCount}`,
            timestamp: Date.now()
          });
          sentCount++;
        }, 1000 / messageRate);
      });

      await Promise.all(sendingPromises);
      await perfRunner.disconnectWebSocketConnections(connections);

      return {
        totalSent: messagesSent.reduce((sum, count) => sum + count, 0),
        totalReceived: messagesReceived.reduce((sum, count) => sum + count, 0),
        averageLatency: latencies.reduce((sum, lat) => sum + lat, 0) / latencies.length,
        p95Latency: latencies.sort()[Math.floor(latencies.length * 0.95)]
      };
    };

    const result = await realtimeLoadTest();

    // Message delivery should be reliable
    expect(result.totalReceived / result.totalSent).toBeGreaterThan(0.95); // >95% delivery rate

    // Latency should be acceptable
    expect(result.averageLatency).toBeLessThan(100); // <100ms average
    expect(result.p95Latency).toBeLessThan(500); // <500ms 95th percentile
  });

  test('should handle dashboard queries under load', async () => {
    const dashboardLoadTest = async () => {
      // Pre-populate with test data
      await perfRunner.populateTestData({
        conversationCount: 1000,
        averageMessagesPerConversation: 50,
        userCount: 100,
        timeSpan: 90 // days
      });

      const concurrentQueries = 20;
      const queryTypes = [
        'getDashboardData',
        'getConversationMetrics',
        'getUserMetrics',
        'getSystemMetrics'
      ];

      const startTime = performance.now();
      const results = await Promise.all(
        Array.from({ length: concurrentQueries }, async () => {
          const queryType = queryTypes[Math.floor(Math.random() * queryTypes.length)];
          const queryStart = performance.now();
          
          try {
            await perfRunner.executeQuery(queryType);
            return performance.now() - queryStart;
          } catch (error) {
            throw new Error(`Query ${queryType} failed: ${error.message}`);
          }
        })
      );

      return {
        totalTime: performance.now() - startTime,
        averageQueryTime: results.reduce((sum, time) => sum + time, 0) / results.length,
        maxQueryTime: Math.max(...results),
        minQueryTime: Math.min(...results)
      };
    };

    const result = await dashboardLoadTest();

    // Query performance requirements
    expect(result.averageQueryTime).toBeLessThan(500); // 500ms average
    expect(result.maxQueryTime).toBeLessThan(2000); // 2s maximum
    expect(result.totalTime).toBeLessThan(10000); // 10s total for all concurrent queries
  });
});
```

### End-to-End User Flow Test
```typescript
// tests/e2e/user-flow.test.ts
import { test, expect } from '@playwright/test';

test.describe('Complete User Flow', () => {
  test('should complete full MVP user journey', async ({ page, browser }) => {
    // 1. Navigate to application
    await page.goto('/');
    await expect(page).toHaveTitle(/Claude Code Observatory/);

    // 2. User registration/login
    await page.click('[data-testid="login-button"]');
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'testpassword');
    await page.click('[data-testid="submit-login"]');

    // Wait for navigation to dashboard
    await expect(page).toHaveURL(/\/dashboard/);

    // 3. Create new conversation
    await page.click('[data-testid="new-conversation-button"]');
    await page.fill('[data-testid="conversation-title"]', 'Test Conversation');
    await page.click('[data-testid="create-conversation-submit"]');

    // Verify conversation created
    await expect(page.locator('[data-testid="conversation-title"]')).toContainText('Test Conversation');

    // 4. Send messages
    const messageInput = page.locator('[data-testid="message-input"]');
    const sendButton = page.locator('[data-testid="send-message"]');

    await messageInput.fill('Hello, this is a test message');
    await sendButton.click();

    // Verify message appears
    await expect(page.locator('[data-testid="message-list"]')).toContainText('Hello, this is a test message');

    // Send another message with code
    await messageInput.fill('Here is some code:\n\n```javascript\nconsole.log("Hello World");\n```');
    await sendButton.click();

    // Verify code block rendering
    await expect(page.locator('[data-testid="code-block"]')).toBeVisible();

    // 5. Test real-time features
    const secondBrowser = await browser.newContext();
    const secondPage = await secondBrowser.newPage();
    
    // Login with second user (simulate in real test)
    await secondPage.goto('/conversations/[conversation-id]');
    // ... authentication steps for second user
    
    // Test typing indicators
    await messageInput.click();
    await messageInput.type('Typing a message...');
    
    // Verify typing indicator appears for other user
    await expect(secondPage.locator('[data-testid="typing-indicator"]')).toBeVisible();
    
    await messageInput.press('Enter');
    
    // Verify typing indicator disappears
    await expect(secondPage.locator('[data-testid="typing-indicator"]')).not.toBeVisible();

    // 6. Navigate to analytics dashboard
    await page.click('[data-testid="analytics-nav"]');
    await expect(page).toHaveURL(/\/analytics/);

    // Verify analytics components load
    await expect(page.locator('[data-testid="metrics-cards"]')).toBeVisible();
    await expect(page.locator('[data-testid="conversation-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="message-chart"]')).toBeVisible();

    // Test chart interactions
    await page.hover('[data-testid="conversation-chart"]');
    await expect(page.locator('[data-testid="chart-tooltip"]')).toBeVisible();

    // 7. Test data export
    await page.click('[data-testid="export-button"]');
    await page.click('[data-testid="export-csv"]');

    // Verify download initiated (check for download event)
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-testid="confirm-export"]');
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toContain('.csv');

    // 8. Test responsive design
    await page.setViewportSize({ width: 768, height: 1024 }); // Tablet
    await expect(page.locator('[data-testid="mobile-nav"]')).toBeVisible();

    await page.setViewportSize({ width: 375, height: 667 }); // Mobile
    await expect(page.locator('[data-testid="mobile-menu-button"]')).toBeVisible();

    // 9. Test accessibility
    const accessibilityResults = await page.evaluate(() => {
      // Run basic accessibility checks
      const focusableElements = document.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      
      const elementsWithAriaLabels = document.querySelectorAll('[aria-label], [aria-labelledby]');
      
      return {
        focusableElementsCount: focusableElements.length,
        elementsWithAriaLabelsCount: elementsWithAriaLabels.length,
        hasSkipLink: !!document.querySelector('[data-testid="skip-link"]')
      };
    });

    expect(accessibilityResults.focusableElementsCount).toBeGreaterThan(0);
    expect(accessibilityResults.elementsWithAriaLabelsCount).toBeGreaterThan(0);
    expect(accessibilityResults.hasSkipLink).toBe(true);

    // 10. Logout
    await page.click('[data-testid="user-menu"]');
    await page.click('[data-testid="logout-button"]');
    await expect(page).toHaveURL(/\/login/);

    await secondBrowser.close();
  });

  test('should handle error scenarios gracefully', async ({ page }) => {
    await page.goto('/');

    // Test network error handling
    await page.route('**/api/**', route => route.abort());
    
    await page.click('[data-testid="login-button"]');
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'testpassword');
    await page.click('[data-testid="submit-login"]');

    // Verify error message displayed
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toContainText('Connection error');

    // Test retry functionality
    await page.unroute('**/api/**');
    await page.click('[data-testid="retry-button"]');

    // Should succeed after retry
    await expect(page).toHaveURL(/\/dashboard/);
  });
});
```

## Performance Monitoring & Optimization

### 1. Performance Monitoring System

```typescript
// packages/core/src/monitoring/performance-monitor.ts
import { EventEmitter } from 'events';
import { Logger } from '../utils/logger';
import { MetricsCollector } from './metrics-collector';

export interface PerformanceMetrics {
  timestamp: number;
  cpu: {
    usage: number;
    loadAverage: number[];
  };
  memory: {
    used: number;
    total: number;
    percentage: number;
  };
  database: {
    connections: number;
    queries: number;
    averageQueryTime: number;
  };
  api: {
    requests: number;
    averageResponseTime: number;
    errorRate: number;
  };
  websocket: {
    connections: number;
    messagesPerSecond: number;
  };
}

export class PerformanceMonitor extends EventEmitter {
  private logger = new Logger('PerformanceMonitor');
  private metrics = new MetricsCollector();
  private monitoringInterval: NodeJS.Timer;
  private performanceAlerts = new Map<string, number>();

  constructor(private intervalMs: number = 5000) {
    super();
    this.startMonitoring();
  }

  private startMonitoring(): void {
    this.monitoringInterval = setInterval(() => {
      this.collectMetrics();
    }, this.intervalMs);
    
    this.logger.info('Performance monitoring started');
  }

  private async collectMetrics(): Promise<void> {
    const metrics: PerformanceMetrics = {
      timestamp: Date.now(),
      cpu: await this.getCpuMetrics(),
      memory: await this.getMemoryMetrics(),
      database: await this.getDatabaseMetrics(),
      api: await this.getApiMetrics(),
      websocket: await this.getWebSocketMetrics()
    };

    this.metrics.record('performance', metrics);
    this.checkPerformanceAlerts(metrics);
    this.emit('metrics', metrics);
  }

  private async getCpuMetrics(): Promise<any> {
    const usage = process.cpuUsage();
    const loadAverage = require('os').loadavg();
    
    return {
      usage: (usage.user + usage.system) / 1000000, // Convert to seconds
      loadAverage
    };
  }

  private async getMemoryMetrics(): Promise<any> {
    const memoryUsage = process.memoryUsage();
    const totalMemory = require('os').totalmem();
    
    return {
      used: memoryUsage.heapUsed,
      total: totalMemory,
      percentage: (memoryUsage.heapUsed / totalMemory) * 100
    };
  }

  private async getDatabaseMetrics(): Promise<any> {
    // Get database metrics from connection pool
    return {
      connections: this.metrics.getMetric('db.connections.active') || 0,
      queries: this.metrics.getMetric('db.queries.count') || 0,
      averageQueryTime: this.metrics.getMetric('db.queries.avgTime') || 0
    };
  }

  private async getApiMetrics(): Promise<any> {
    return {
      requests: this.metrics.getMetric('api.requests.count') || 0,
      averageResponseTime: this.metrics.getMetric('api.response.avgTime') || 0,
      errorRate: this.metrics.getMetric('api.errors.rate') || 0
    };
  }

  private async getWebSocketMetrics(): Promise<any> {
    return {
      connections: this.metrics.getMetric('websocket.connections.active') || 0,
      messagesPerSecond: this.metrics.getMetric('websocket.messages.rate') || 0
    };
  }

  private checkPerformanceAlerts(metrics: PerformanceMetrics): void {
    const alerts: string[] = [];

    // Memory usage alert
    if (metrics.memory.percentage > 80) {
      alerts.push(`High memory usage: ${metrics.memory.percentage.toFixed(1)}%`);
    }

    // CPU usage alert
    if (metrics.cpu.usage > 80) {
      alerts.push(`High CPU usage: ${metrics.cpu.usage.toFixed(1)}%`);
    }

    // API response time alert
    if (metrics.api.averageResponseTime > 1000) {
      alerts.push(`Slow API response: ${metrics.api.averageResponseTime}ms`);
    }

    // Database query time alert
    if (metrics.database.averageQueryTime > 500) {
      alerts.push(`Slow database queries: ${metrics.database.averageQueryTime}ms`);
    }

    // Error rate alert
    if (metrics.api.errorRate > 0.05) {
      alerts.push(`High error rate: ${(metrics.api.errorRate * 100).toFixed(1)}%`);
    }

    for (const alert of alerts) {
      this.handlePerformanceAlert(alert, metrics);
    }
  }

  private handlePerformanceAlert(alert: string, metrics: PerformanceMetrics): void {
    const now = Date.now();
    const lastAlert = this.performanceAlerts.get(alert);
    
    // Throttle alerts (only send once per 5 minutes)
    if (!lastAlert || now - lastAlert > 300000) {
      this.performanceAlerts.set(alert, now);
      this.logger.warn(`Performance Alert: ${alert}`, { metrics });
      this.emit('performanceAlert', { alert, metrics });
    }
  }

  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.logger.info('Performance monitoring stopped');
    }
  }
}
```

### 2. Database Query Optimization

```typescript
// packages/database/src/optimization/query-optimizer.ts
import { Logger } from '../utils/logger';
import { DatabaseConnection } from '../connection/database-connection';

export interface QueryPlan {
  sql: string;
  parameters: any[];
  estimatedCost: number;
  executionTime?: number;
  optimizations: string[];
}

export class QueryOptimizer {
  private logger = new Logger('QueryOptimizer');
  private queryCache = new Map<string, any>();
  private slowQueryThreshold = 1000; // 1 second

  constructor(private db: DatabaseConnection) {}

  async optimizeQuery(sql: string, parameters: any[] = []): Promise<QueryPlan> {
    const cacheKey = this.generateCacheKey(sql, parameters);
    
    if (this.queryCache.has(cacheKey)) {
      return this.queryCache.get(cacheKey);
    }

    const plan = await this.analyzeQuery(sql, parameters);
    this.queryCache.set(cacheKey, plan);
    
    return plan;
  }

  private async analyzeQuery(sql: string, parameters: any[]): Promise<QueryPlan> {
    const startTime = Date.now();
    
    try {
      // Analyze query execution plan
      const explainResult = await this.db.query(`EXPLAIN QUERY PLAN ${sql}`, parameters);
      const estimatedCost = this.calculateQueryCost(explainResult);
      
      // Generate optimization suggestions
      const optimizations = this.generateOptimizations(sql, explainResult);
      
      const plan: QueryPlan = {
        sql,
        parameters,
        estimatedCost,
        optimizations
      };

      return plan;
    } catch (error) {
      this.logger.error('Query analysis failed:', error);
      throw error;
    }
  }

  private calculateQueryCost(explainResult: any[]): number {
    // SQLite uses different cost calculation
    // This is a simplified version
    let totalCost = 0;
    
    for (const row of explainResult) {
      if (row.detail && row.detail.includes('SCAN')) {
        totalCost += 100; // Table scan is expensive
      } else if (row.detail && row.detail.includes('SEARCH')) {
        totalCost += 10; // Index search is cheaper
      }
    }
    
    return totalCost;
  }

  private generateOptimizations(sql: string, explainResult: any[]): string[] {
    const optimizations: string[] = [];
    
    // Check for table scans
    if (explainResult.some(row => row.detail && row.detail.includes('SCAN TABLE'))) {
      optimizations.push('Consider adding indexes for frequently queried columns');
    }

    // Check for sorting
    if (explainResult.some(row => row.detail && row.detail.includes('USE TEMP B-TREE FOR ORDER BY'))) {
      optimizations.push('Consider adding index to avoid sorting');
    }

    // Check for joins
    if (sql.toUpperCase().includes('JOIN')) {
      optimizations.push('Ensure JOIN conditions use indexed columns');
    }

    // Check for subqueries
    if (sql.includes('(SELECT')) {
      optimizations.push('Consider rewriting subqueries as JOINs');
    }

    return optimizations;
  }

  async executeOptimizedQuery<T>(
    sql: string, 
    parameters: any[] = []
  ): Promise<{ results: T[], executionTime: number, plan: QueryPlan }> {
    const plan = await this.optimizeQuery(sql, parameters);
    const startTime = Date.now();
    
    try {
      const results = await this.db.query<T>(sql, parameters);
      const executionTime = Date.now() - startTime;
      
      plan.executionTime = executionTime;
      
      // Log slow queries
      if (executionTime > this.slowQueryThreshold) {
        this.logger.warn('Slow query detected:', {
          sql,
          parameters,
          executionTime,
          optimizations: plan.optimizations
        });
      }
      
      return { results, executionTime, plan };
    } catch (error) {
      this.logger.error('Optimized query execution failed:', error);
      throw error;
    }
  }

  private generateCacheKey(sql: string, parameters: any[]): string {
    return `${sql}:${JSON.stringify(parameters)}`;
  }

  // Index management
  async createOptimalIndexes(tableName: string): Promise<void> {
    this.logger.info(`Creating optimal indexes for table: ${tableName}`);
    
    const queries = await this.getFrequentQueries(tableName);
    const recommendedIndexes = this.analyzeIndexNeeds(queries);
    
    for (const indexDef of recommendedIndexes) {
      try {
        await this.db.query(indexDef.sql);
        this.logger.info(`Created index: ${indexDef.name}`);
      } catch (error) {
        this.logger.error(`Failed to create index ${indexDef.name}:`, error);
      }
    }
  }

  private async getFrequentQueries(tableName: string): Promise<any[]> {
    // This would typically come from query logs
    // For now, return common query patterns
    return [
      { sql: `SELECT * FROM ${tableName} WHERE id = ?`, frequency: 1000 },
      { sql: `SELECT * FROM ${tableName} WHERE user_id = ?`, frequency: 500 },
      { sql: `SELECT * FROM ${tableName} WHERE created_at > ?`, frequency: 300 }
    ];
  }

  private analyzeIndexNeeds(queries: any[]): Array<{name: string, sql: string}> {
    const indexes: Array<{name: string, sql: string}> = [];
    
    for (const query of queries) {
      const whereMatch = query.sql.match(/WHERE\s+(\w+)\s*=/i);
      if (whereMatch && query.frequency > 100) {
        const column = whereMatch[1];
        const tableName = this.extractTableName(query.sql);
        
        indexes.push({
          name: `idx_${tableName}_${column}`,
          sql: `CREATE INDEX IF NOT EXISTS idx_${tableName}_${column} ON ${tableName} (${column})`
        });
      }
    }
    
    return indexes;
  }

  private extractTableName(sql: string): string {
    const match = sql.match(/FROM\s+(\w+)/i);
    return match ? match[1] : 'unknown';
  }
}
```

### 3. Frontend Performance Optimization

```typescript
// packages/frontend/src/performance/performance-optimizer.ts
import { Logger } from '../utils/logger';

export interface PerformanceEntry {
  name: string;
  startTime: number;
  duration: number;
  type: 'navigation' | 'resource' | 'measure' | 'mark';
}

export class FrontendPerformanceOptimizer {
  private logger = new Logger('FrontendPerformanceOptimizer');
  private observer: PerformanceObserver;
  private metrics = new Map<string, number[]>();

  constructor() {
    this.setupPerformanceObserver();
    this.setupResourceOptimization();
  }

  private setupPerformanceObserver(): void {
    if (typeof window !== 'undefined' && 'PerformanceObserver' in window) {
      this.observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          this.processPerformanceEntry(entry);
        }
      });

      this.observer.observe({ entryTypes: ['navigation', 'resource', 'measure', 'mark'] });
    }
  }

  private processPerformanceEntry(entry: PerformanceEntry): void {
    const metricName = `${entry.type}_${entry.name}`;
    
    if (!this.metrics.has(metricName)) {
      this.metrics.set(metricName, []);
    }
    
    this.metrics.get(metricName)!.push(entry.duration);
    
    // Log slow operations
    if (entry.duration > 1000) {
      this.logger.warn(`Slow ${entry.type}: ${entry.name}`, {
        duration: entry.duration,
        startTime: entry.startTime
      });
    }
  }

  private setupResourceOptimization(): void {
    // Implement lazy loading for images
    this.setupLazyLoading();
    
    // Implement code splitting
    this.setupCodeSplitting();
    
    // Implement asset compression
    this.setupAssetOptimization();
  }

  private setupLazyLoading(): void {
    if (typeof window !== 'undefined' && 'IntersectionObserver' in window) {
      const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target as HTMLImageElement;
            img.src = img.dataset.src || '';
            img.classList.remove('lazy');
            imageObserver.unobserve(img);
          }
        });
      });

      document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
      });
    }
  }

  private setupCodeSplitting(): void {
    // Dynamic imports for route-based code splitting
    const loadComponent = async (componentName: string) => {
      const startTime = performance.now();
      
      try {
        const module = await import(`../components/${componentName}`);
        const loadTime = performance.now() - startTime;
        
        this.logger.info(`Component loaded: ${componentName}`, { loadTime });
        return module.default;
      } catch (error) {
        this.logger.error(`Failed to load component: ${componentName}`, error);
        throw error;
      }
    };

    // Cache loaded components
    const componentCache = new Map<string, any>();
    
    return {
      loadComponent: async (name: string) => {
        if (componentCache.has(name)) {
          return componentCache.get(name);
        }
        
        const component = await loadComponent(name);
        componentCache.set(name, component);
        return component;
      }
    };
  }

  private setupAssetOptimization(): void {
    // Implement service worker for caching
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js')
        .then(registration => {
          this.logger.info('Service Worker registered:', registration);
        })
        .catch(error => {
          this.logger.error('Service Worker registration failed:', error);
        });
    }
  }

  // Performance measurement utilities
  measure(name: string, fn: () => any): any {
    const startTime = performance.now();
    const result = fn();
    const endTime = performance.now();
    
    performance.mark(`${name}-start`);
    performance.mark(`${name}-end`);
    performance.measure(name, `${name}-start`, `${name}-end`);
    
    this.logger.debug(`Performance measure: ${name}`, {
      duration: endTime - startTime
    });
    
    return result;
  }

  async measureAsync(name: string, fn: () => Promise<any>): Promise<any> {
    const startTime = performance.now();
    const result = await fn();
    const endTime = performance.now();
    
    performance.mark(`${name}-start`);
    performance.mark(`${name}-end`);
    performance.measure(name, `${name}-start`, `${name}-end`);
    
    this.logger.debug(`Performance measure (async): ${name}`, {
      duration: endTime - startTime
    });
    
    return result;
  }

  // Memory optimization
  optimizeMemoryUsage(): void {
    // Debounce scroll events
    this.debounceScrollEvents();
    
    // Clean up event listeners
    this.cleanupEventListeners();
    
    // Implement virtual scrolling for large lists
    this.setupVirtualScrolling();
  }

  private debounceScrollEvents(): void {
    let scrollTimeout: NodeJS.Timeout;
    
    const handleScroll = () => {
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(() => {
        // Handle scroll event
        this.processScrollEvent();
      }, 100);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
  }

  private processScrollEvent(): void {
    // Implement scroll-based optimizations
    this.updateVisibleComponents();
    this.preloadNextPageContent();
  }

  private updateVisibleComponents(): void {
    // Update only visible components
    const visibleElements = document.querySelectorAll('[data-component]');
    
    visibleElements.forEach(element => {
      const rect = element.getBoundingClientRect();
      const isVisible = rect.top < window.innerHeight && rect.bottom > 0;
      
      if (isVisible) {
        element.classList.add('visible');
        // Trigger component update
      } else {
        element.classList.remove('visible');
      }
    });
  }

  private preloadNextPageContent(): void {
    // Implement intelligent preloading
    const scrollPosition = window.scrollY;
    const documentHeight = document.documentElement.scrollHeight;
    const windowHeight = window.innerHeight;
    
    if (scrollPosition + windowHeight > documentHeight * 0.8) {
      // Preload next page content
      this.logger.debug('Preloading next page content');
    }
  }

  private cleanupEventListeners(): void {
    // Remove unused event listeners
    const elements = document.querySelectorAll('[data-cleanup]');
    
    elements.forEach(element => {
      // Remove event listeners that are no longer needed
      element.removeEventListener('click', this.handleClick);
      element.removeEventListener('scroll', this.handleScroll);
    });
  }

  private setupVirtualScrolling(): void {
    // Implement virtual scrolling for large data sets
    const containers = document.querySelectorAll('[data-virtual-scroll]');
    
    containers.forEach(container => {
      this.initializeVirtualScroll(container as HTMLElement);
    });
  }

  private initializeVirtualScroll(container: HTMLElement): void {
    const itemHeight = 50; // Configurable
    const visibleItems = Math.ceil(container.clientHeight / itemHeight);
    const totalItems = parseInt(container.dataset.totalItems || '0');
    
    let startIndex = 0;
    
    const updateVirtualScroll = () => {
      const scrollTop = container.scrollTop;
      startIndex = Math.floor(scrollTop / itemHeight);
      
      const endIndex = Math.min(startIndex + visibleItems, totalItems);
      
      // Render only visible items
      this.renderVirtualItems(container, startIndex, endIndex);
    };

    container.addEventListener('scroll', updateVirtualScroll);
    updateVirtualScroll(); // Initial render
  }

  private renderVirtualItems(container: HTMLElement, startIndex: number, endIndex: number): void {
    // Clear existing items
    container.innerHTML = '';
    
    // Render visible items
    for (let i = startIndex; i < endIndex; i++) {
      const item = document.createElement('div');
      item.className = 'virtual-item';
      item.textContent = `Item ${i}`;
      item.style.top = `${i * 50}px`;
      container.appendChild(item);
    }
  }

  private handleClick = (event: Event) => {
    // Handle click events
  };

  private handleScroll = (event: Event) => {
    // Handle scroll events
  };

  // Performance reporting
  getPerformanceReport(): any {
    const report = {
      metrics: Object.fromEntries(this.metrics),
      vitals: this.getWebVitals(),
      resources: this.getResourceTiming(),
      navigation: this.getNavigationTiming()
    };
    
    return report;
  }

  private getWebVitals(): any {
    return {
      LCP: this.getLargestContentfulPaint(),
      FID: this.getFirstInputDelay(),
      CLS: this.getCumulativeLayoutShift()
    };
  }

  private getLargestContentfulPaint(): number {
    const lcpEntries = performance.getEntriesByType('largest-contentful-paint');
    return lcpEntries.length > 0 ? lcpEntries[lcpEntries.length - 1].startTime : 0;
  }

  private getFirstInputDelay(): number {
    const fidEntries = performance.getEntriesByType('first-input');
    return fidEntries.length > 0 ? fidEntries[0].processingStart - fidEntries[0].startTime : 0;
  }

  private getCumulativeLayoutShift(): number {
    const clsEntries = performance.getEntriesByType('layout-shift');
    return clsEntries.reduce((sum, entry) => sum + entry.value, 0);
  }

  private getResourceTiming(): any {
    const resources = performance.getEntriesByType('resource');
    return resources.map(resource => ({
      name: resource.name,
      duration: resource.duration,
      transferSize: resource.transferSize || 0
    }));
  }

  private getNavigationTiming(): any {
    const navigation = performance.getEntriesByType('navigation')[0];
    return {
      domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
      loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
      firstByte: navigation.responseStart - navigation.requestStart
    };
  }
}
```

## Production Deployment Configurations

### 1. Docker Production Configuration

```dockerfile
# Dockerfile.production
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY packages/*/package*.json ./packages/*/

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build:production

# Production stage
FROM node:18-alpine AS production

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create app user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001

WORKDIR /app

# Copy built application
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/package*.json ./

# Environment variables
ENV NODE_ENV=production
ENV PORT=3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD node healthcheck.js

# Switch to non-root user
USER nodejs

# Expose port
EXPOSE 3000

# Start application
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "dist/index.js"]
```

### 2. Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ccobservatory-backend
  namespace: ccobservatory
  labels:
    app: ccobservatory-backend
    version: v1.0.0
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ccobservatory-backend
  template:
    metadata:
      labels:
        app: ccobservatory-backend
        version: v1.0.0
    spec:
      containers:
      - name: backend
        image: ccobservatory/backend:v1.0.0
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: ccobservatory-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: ccobservatory-secrets
              key: redis-url
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: ccobservatory-secrets
              key: jwt-secret
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: config
          mountPath: /app/config
          readOnly: true
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: config
        configMap:
          name: ccobservatory-config
      - name: logs
        emptyDir: {}
      imagePullSecrets:
      - name: registry-credentials
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        fsGroup: 1001
---
apiVersion: v1
kind: Service
metadata:
  name: ccobservatory-backend-service
  namespace: ccobservatory
spec:
  selector:
    app: ccobservatory-backend
  ports:
  - port: 80
    targetPort: 3000
    protocol: TCP
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ccobservatory-ingress
  namespace: ccobservatory
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.ccobservatory.com
    secretName: ccobservatory-tls
  rules:
  - host: api.ccobservatory.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ccobservatory-backend-service
            port:
              number: 80
```

### 3. Production Configuration Management

```typescript
// packages/core/src/config/production-config.ts
import { Logger } from '../utils/logger';

export interface ProductionConfig {
  server: {
    port: number;
    host: string;
    env: string;
    cors: {
      origin: string[];
      credentials: boolean;
    };
  };
  database: {
    url: string;
    ssl: boolean;
    poolSize: number;
    connectionTimeout: number;
    idleTimeout: number;
  };
  redis: {
    url: string;
    db: number;
    keyPrefix: string;
    retryAttempts: number;
  };
  security: {
    jwtSecret: string;
    jwtExpiration: string;
    bcryptRounds: number;
    rateLimitWindowMs: number;
    rateLimitMax: number;
  };
  monitoring: {
    enabled: boolean;
    metricsPort: number;
    healthCheckPath: string;
    logLevel: string;
  };
  features: {
    realTimeEnabled: boolean;
    analyticsEnabled: boolean;
    fileUploadEnabled: boolean;
    maxFileSize: number;
  };
}

export class ProductionConfigManager {
  private logger = new Logger('ProductionConfigManager');
  private config: ProductionConfig;

  constructor() {
    this.config = this.loadConfiguration();
    this.validateConfiguration();
  }

  private loadConfiguration(): ProductionConfig {
    const requiredEnvVars = [
      'DATABASE_URL',
      'REDIS_URL',
      'JWT_SECRET'
    ];

    // Check for required environment variables
    for (const envVar of requiredEnvVars) {
      if (!process.env[envVar]) {
        throw new Error(`Required environment variable ${envVar} is not set`);
      }
    }

    return {
      server: {
        port: parseInt(process.env.PORT || '3000'),
        host: process.env.HOST || '0.0.0.0',
        env: process.env.NODE_ENV || 'production',
        cors: {
          origin: process.env.CORS_ORIGIN ? process.env.CORS_ORIGIN.split(',') : ['https://ccobservatory.com'],
          credentials: process.env.CORS_CREDENTIALS === 'true'
        }
      },
      database: {
        url: process.env.DATABASE_URL!,
        ssl: process.env.DATABASE_SSL === 'true',
        poolSize: parseInt(process.env.DATABASE_POOL_SIZE || '10'),
        connectionTimeout: parseInt(process.env.DATABASE_CONNECTION_TIMEOUT || '30000'),
        idleTimeout: parseInt(process.env.DATABASE_IDLE_TIMEOUT || '10000')
      },
      redis: {
        url: process.env.REDIS_URL!,
        db: parseInt(process.env.REDIS_DB || '0'),
        keyPrefix: process.env.REDIS_KEY_PREFIX || 'cco:',
        retryAttempts: parseInt(process.env.REDIS_RETRY_ATTEMPTS || '3')
      },
      security: {
        jwtSecret: process.env.JWT_SECRET!,
        jwtExpiration: process.env.JWT_EXPIRATION || '24h',
        bcryptRounds: parseInt(process.env.BCRYPT_ROUNDS || '12'),
        rateLimitWindowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '900000'), // 15 minutes
        rateLimitMax: parseInt(process.env.RATE_LIMIT_MAX || '100')
      },
      monitoring: {
        enabled: process.env.MONITORING_ENABLED !== 'false',
        metricsPort: parseInt(process.env.METRICS_PORT || '9090'),
        healthCheckPath: process.env.HEALTH_CHECK_PATH || '/health',
        logLevel: process.env.LOG_LEVEL || 'info'
      },
      features: {
        realTimeEnabled: process.env.REALTIME_ENABLED !== 'false',
        analyticsEnabled: process.env.ANALYTICS_ENABLED !== 'false',
        fileUploadEnabled: process.env.FILE_UPLOAD_ENABLED !== 'false',
        maxFileSize: parseInt(process.env.MAX_FILE_SIZE || '10485760') // 10MB
      }
    };
  }

  private validateConfiguration(): void {
    const errors: string[] = [];

    // Server validation
    if (this.config.server.port < 1 || this.config.server.port > 65535) {
      errors.push('Invalid server port');
    }

    // Database validation
    if (!this.config.database.url.startsWith('sqlite:') && !this.config.database.url.startsWith('postgres:')) {
      errors.push('Invalid database URL format');
    }

    // Redis validation
    if (!this.config.redis.url.startsWith('redis:')) {
      errors.push('Invalid Redis URL format');
    }

    // Security validation
    if (this.config.security.jwtSecret.length < 32) {
      errors.push('JWT secret must be at least 32 characters long');
    }

    if (this.config.security.bcryptRounds < 10 || this.config.security.bcryptRounds > 15) {
      errors.push('Bcrypt rounds must be between 10 and 15');
    }

    if (errors.length > 0) {
      this.logger.error('Configuration validation failed:', errors);
      throw new Error(`Configuration validation failed: ${errors.join(', ')}`);
    }

    this.logger.info('Configuration validated successfully');
  }

  getConfig(): ProductionConfig {
    return this.config;
  }

  // Environment-specific getters
  isDevelopment(): boolean {
    return this.config.server.env === 'development';
  }

  isProduction(): boolean {
    return this.config.server.env === 'production';
  }

  isTesting(): boolean {
    return this.config.server.env === 'test';
  }

  // Feature flags
  isFeatureEnabled(feature: keyof ProductionConfig['features']): boolean {
    return this.config.features[feature] as boolean;
  }
}

// Singleton instance
export const productionConfig = new ProductionConfigManager();
```

### 4. Health Check System

```typescript
// packages/core/src/health/health-checker.ts
import { Logger } from '../utils/logger';
import { DatabaseConnection } from '../database/database-connection';
import { Redis } from 'ioredis';

export interface HealthCheck {
  name: string;
  status: 'healthy' | 'unhealthy' | 'degraded';
  message: string;
  responseTime: number;
  timestamp: number;
}

export interface HealthReport {
  status: 'healthy' | 'unhealthy' | 'degraded';
  checks: HealthCheck[];
  uptime: number;
  timestamp: number;
}

export class HealthChecker {
  private logger = new Logger('HealthChecker');
  private checks = new Map<string, () => Promise<HealthCheck>>();

  constructor() {
    this.registerDefaultChecks();
  }

  private registerDefaultChecks(): void {
    this.registerCheck('database', this.checkDatabase.bind(this));
    this.registerCheck('redis', this.checkRedis.bind(this));
    this.registerCheck('memory', this.checkMemory.bind(this));
    this.registerCheck('disk', this.checkDisk.bind(this));
  }

  registerCheck(name: string, check: () => Promise<HealthCheck>): void {
    this.checks.set(name, check);
  }

  async performHealthCheck(): Promise<HealthReport> {
    const startTime = Date.now();
    const checkResults: HealthCheck[] = [];

    for (const [name, check] of this.checks) {
      try {
        const result = await check();
        checkResults.push(result);
      } catch (error) {
        checkResults.push({
          name,
          status: 'unhealthy',
          message: error.message,
          responseTime: Date.now() - startTime,
          timestamp: Date.now()
        });
      }
    }

    const overallStatus = this.determineOverallStatus(checkResults);
    
    return {
      status: overallStatus,
      checks: checkResults,
      uptime: process.uptime(),
      timestamp: Date.now()
    };
  }

  private determineOverallStatus(checks: HealthCheck[]): 'healthy' | 'unhealthy' | 'degraded' {
    const unhealthyChecks = checks.filter(c => c.status === 'unhealthy');
    const degradedChecks = checks.filter(c => c.status === 'degraded');

    if (unhealthyChecks.length > 0) {
      return 'unhealthy';
    }

    if (degradedChecks.length > 0) {
      return 'degraded';
    }

    return 'healthy';
  }

  private async checkDatabase(): Promise<HealthCheck> {
    const startTime = Date.now();
    
    try {
      // Perform a simple query
      const db = new DatabaseConnection();
      await db.query('SELECT 1');
      
      return {
        name: 'database',
        status: 'healthy',
        message: 'Database connection successful',
        responseTime: Date.now() - startTime,
        timestamp: Date.now()
      };
    } catch (error) {
      return {
        name: 'database',
        status: 'unhealthy',
        message: `Database connection failed: ${error.message}`,
        responseTime: Date.now() - startTime,
        timestamp: Date.now()
      };
    }
  }

  private async checkRedis(): Promise<HealthCheck> {
    const startTime = Date.now();
    
    try {
      const redis = new Redis(process.env.REDIS_URL!);
      await redis.ping();
      redis.disconnect();
      
      return {
        name: 'redis',
        status: 'healthy',
        message: 'Redis connection successful',
        responseTime: Date.now() - startTime,
        timestamp: Date.now()
      };
    } catch (error) {
      return {
        name: 'redis',
        status: 'unhealthy',
        message: `Redis connection failed: ${error.message}`,
        responseTime: Date.now() - startTime,
        timestamp: Date.now()
      };
    }
  }

  private async checkMemory(): Promise<HealthCheck> {
    const startTime = Date.now();
    
    try {
      const memoryUsage = process.memoryUsage();
      const totalMemory = require('os').totalmem();
      const usedMemory = memoryUsage.heapUsed;
      const memoryPercentage = (usedMemory / totalMemory) * 100;
      
      let status: 'healthy' | 'degraded' | 'unhealthy' = 'healthy';
      let message = `Memory usage: ${memoryPercentage.toFixed(1)}%`;
      
      if (memoryPercentage > 90) {
        status = 'unhealthy';
        message = `Critical memory usage: ${memoryPercentage.toFixed(1)}%`;
      } else if (memoryPercentage > 80) {
        status = 'degraded';
        message = `High memory usage: ${memoryPercentage.toFixed(1)}%`;
      }
      
      return {
        name: 'memory',
        status,
        message,
        responseTime: Date.now() - startTime,
        timestamp: Date.now()
      };
    } catch (error) {
      return {
        name: 'memory',
        status: 'unhealthy',
        message: `Memory check failed: ${error.message}`,
        responseTime: Date.now() - startTime,
        timestamp: Date.now()
      };
    }
  }

  private async checkDisk(): Promise<HealthCheck> {
    const startTime = Date.now();
    
    try {
      const fs = require('fs');
      const stats = fs.statSync(process.cwd());
      
      // This is a simplified disk check
      // In production, you'd want to check actual disk usage
      return {
        name: 'disk',
        status: 'healthy',
        message: 'Disk space available',
        responseTime: Date.now() - startTime,
        timestamp: Date.now()
      };
    } catch (error) {
      return {
        name: 'disk',
        status: 'unhealthy',
        message: `Disk check failed: ${error.message}`,
        responseTime: Date.now() - startTime,
        timestamp: Date.now()
      };
    }
  }
}
```

## Integration Testing Strategies

### 1. Contract Testing with Pact

```typescript
// packages/core/tests/contracts/api-consumer.pact.test.ts
import { PactV3, MatchersV3 } from '@pact-foundation/pact';
import { ApiClient } from '../../src/api/api-client';

const { like, eachLike } = MatchersV3;

describe('API Consumer Contract Tests', () => {
  const provider = new PactV3({
    consumer: 'CCObservatory-Frontend',
    provider: 'CCObservatory-Backend',
    port: 1234,
    dir: './pacts'
  });

  const apiClient = new ApiClient({
    baseURL: 'http://localhost:1234',
    timeout: 5000,
    maxRetries: 3,
    retryDelay: 1000,
    retryBackoffMultiplier: 2
  });

  describe('Conversations API', () => {
    test('should get conversation list', async () => {
      await provider
        .given('conversations exist')
        .uponReceiving('a request for conversations')
        .withRequest({
          method: 'GET',
          path: '/api/conversations',
          headers: {
            'Authorization': like('Bearer token123'),
            'Content-Type': 'application/json'
          }
        })
        .willRespondWith({
          status: 200,
          headers: {
            'Content-Type': 'application/json'
          },
          body: {
            statusCode: '10000',
            message: 'success',
            data: eachLike({
              id: like('conv_123'),
              title: like('Test Conversation'),
              messageCount: like(5),
              createdAt: like('2023-01-01T00:00:00.000Z'),
              updatedAt: like('2023-01-01T00:00:00.000Z')
            })
          }
        });

      const response = await apiClient.request({
        method: 'GET',
        url: '/api/conversations',
        headers: {
          'Authorization': 'Bearer token123'
        }
      });

      expect(response.statusCode).toBe('10000');
      expect(response.data).toHaveLength(1);
      expect(response.data[0]).toMatchObject({
        id: expect.any(String),
        title: expect.any(String),
        messageCount: expect.any(Number)
      });
    });

    test('should create a conversation', async () => {
      await provider
        .given('user is authenticated')
        .uponReceiving('a request to create a conversation')
        .withRequest({
          method: 'POST',
          path: '/api/conversations',
          headers: {
            'Authorization': like('Bearer token123'),
            'Content-Type': 'application/json'
          },
          body: {
            title: like('New Conversation'),
            description: like('A test conversation')
          }
        })
        .willRespondWith({
          status: 201,
          headers: {
            'Content-Type': 'application/json'
          },
          body: {
            statusCode: '10000',
            message: 'Conversation created successfully',
            data: {
              id: like('conv_456'),
              title: like('New Conversation'),
              description: like('A test conversation'),
              messageCount: like(0),
              createdAt: like('2023-01-01T00:00:00.000Z'),
              updatedAt: like('2023-01-01T00:00:00.000Z')
            }
          }
        });

      const response = await apiClient.request({
        method: 'POST',
        url: '/api/conversations',
        headers: {
          'Authorization': 'Bearer token123'
        },
        data: {
          title: 'New Conversation',
          description: 'A test conversation'
        }
      });

      expect(response.statusCode).toBe('10000');
      expect(response.data.title).toBe('New Conversation');
      expect(response.data.messageCount).toBe(0);
    });
  });

  describe('Messages API', () => {
    test('should get messages for a conversation', async () => {
      await provider
        .given('conversation conv_123 exists with messages')
        .uponReceiving('a request for messages')
        .withRequest({
          method: 'GET',
          path: '/api/conversations/conv_123/messages',
          headers: {
            'Authorization': like('Bearer token123'),
            'Content-Type': 'application/json'
          },
          query: {
            page: like('1'),
            limit: like('20')
          }
        })
        .willRespondWith({
          status: 200,
          headers: {
            'Content-Type': 'application/json'
          },
          body: {
            statusCode: '10000',
            message: 'success',
            data: {
              messages: eachLike({
                id: like('msg_123'),
                content: like('Hello World'),
                role: like('user'),
                tokenCount: like(2),
                createdAt: like('2023-01-01T00:00:00.000Z')
              }),
              pagination: {
                page: like(1),
                limit: like(20),
                total: like(5),
                totalPages: like(1)
              }
            }
          }
        });

      const response = await apiClient.request({
        method: 'GET',
        url: '/api/conversations/conv_123/messages',
        headers: {
          'Authorization': 'Bearer token123'
        },
        params: {
          page: 1,
          limit: 20
        }
      });

      expect(response.statusCode).toBe('10000');
      expect(response.data.messages).toHaveLength(1);
      expect(response.data.pagination.total).toBe(5);
    });
  });

  describe('Analytics API', () => {
    test('should get conversation analytics', async () => {
      await provider
        .given('analytics data exists')
        .uponReceiving('a request for conversation analytics')
        .withRequest({
          method: 'GET',
          path: '/api/analytics/conversations',
          headers: {
            'Authorization': like('Bearer token123'),
            'Content-Type': 'application/json'
          },
          query: {
            period: like('7d')
          }
        })
        .willRespondWith({
          status: 200,
          headers: {
            'Content-Type': 'application/json'
          },
          body: {
            statusCode: '10000',
            message: 'success',
            data: {
              overview: {
                totalConversations: like(100),
                totalMessages: like(500),
                averageMessagesPerConversation: like(5.0),
                totalTokens: like(10000)
              },
              trends: eachLike({
                date: like('2023-01-01'),
                conversations: like(15),
                messages: like(75),
                tokens: like(1500)
              })
            }
          }
        });

      const response = await apiClient.request({
        method: 'GET',
        url: '/api/analytics/conversations',
        headers: {
          'Authorization': 'Bearer token123'
        },
        params: {
          period: '7d'
        }
      });

      expect(response.statusCode).toBe('10000');
      expect(response.data.overview.totalConversations).toBe(100);
      expect(response.data.trends).toHaveLength(1);
    });
  });
});
```

### 2. API Integration Testing

```typescript
// packages/backend/tests/integration/api-integration.test.ts
import { describe, test, expect, beforeAll, afterAll } from 'vitest';
import { TestServer } from '../helpers/test-server';
import { DatabaseTestHelper } from '../helpers/database-test-helper';
import { ApiTestClient } from '../helpers/api-test-client';

describe('API Integration Tests', () => {
  let testServer: TestServer;
  let dbHelper: DatabaseTestHelper;
  let apiClient: ApiTestClient;

  beforeAll(async () => {
    testServer = new TestServer();
    await testServer.start();
    
    dbHelper = new DatabaseTestHelper();
    await dbHelper.setup();
    
    apiClient = new ApiTestClient(testServer.getBaseUrl());
  });

  afterAll(async () => {
    await dbHelper.cleanup();
    await testServer.stop();
  });

  describe('Authentication Flow', () => {
    test('should handle complete authentication flow', async () => {
      // 1. User signup
      const signupData = {
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      };

      const signupResponse = await apiClient.post('/auth/signup', signupData);
      expect(signupResponse.status).toBe(201);
      expect(signupResponse.data.statusCode).toBe('10000');
      expect(signupResponse.data.data.user.email).toBe(signupData.email);
      expect(signupResponse.data.data.tokens.accessToken).toBeDefined();

      const { accessToken } = signupResponse.data.data.tokens;

      // 2. Access protected resource
      const profileResponse = await apiClient.get('/profile/me', {
        headers: { Authorization: `Bearer ${accessToken}` }
      });
      expect(profileResponse.status).toBe(200);
      expect(profileResponse.data.data.email).toBe(signupData.email);

      // 3. Token refresh
      const refreshResponse = await apiClient.post('/auth/refresh', {
        refreshToken: signupResponse.data.data.tokens.refreshToken
      });
      expect(refreshResponse.status).toBe(200);
      expect(refreshResponse.data.data.accessToken).toBeDefined();

      // 4. Logout
      const logoutResponse = await apiClient.post('/auth/logout', {}, {
        headers: { Authorization: `Bearer ${accessToken}` }
      });
      expect(logoutResponse.status).toBe(200);

      // 5. Verify token is invalidated
      const protectedResponse = await apiClient.get('/profile/me', {
        headers: { Authorization: `Bearer ${accessToken}` }
      });
      expect(protectedResponse.status).toBe(401);
    });
  });

  describe('Conversation Management', () => {
    let authToken: string;
    let userId: string;

    beforeAll(async () => {
      // Setup authenticated user
      const user = await dbHelper.createUser({
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      });
      userId = user.id;
      authToken = await apiClient.authenticateUser(user);
    });

    test('should handle conversation CRUD operations', async () => {
      // Create conversation
      const createData = {
        title: 'Test Conversation',
        description: 'A test conversation'
      };

      const createResponse = await apiClient.post('/conversations', createData, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      expect(createResponse.status).toBe(201);
      expect(createResponse.data.data.title).toBe(createData.title);

      const conversationId = createResponse.data.data.id;

      // Read conversation
      const readResponse = await apiClient.get(`/conversations/${conversationId}`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      expect(readResponse.status).toBe(200);
      expect(readResponse.data.data.id).toBe(conversationId);

      // Update conversation
      const updateData = { title: 'Updated Conversation' };
      const updateResponse = await apiClient.put(`/conversations/${conversationId}`, updateData, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      expect(updateResponse.status).toBe(200);
      expect(updateResponse.data.data.title).toBe(updateData.title);

      // List conversations
      const listResponse = await apiClient.get('/conversations', {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      expect(listResponse.status).toBe(200);
      expect(listResponse.data.data).toHaveLength(1);

      // Delete conversation
      const deleteResponse = await apiClient.delete(`/conversations/${conversationId}`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      expect(deleteResponse.status).toBe(200);

      // Verify deletion
      const verifyResponse = await apiClient.get(`/conversations/${conversationId}`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      expect(verifyResponse.status).toBe(404);
    });
  });

  describe('Message Management', () => {
    let authToken: string;
    let conversationId: string;

    beforeAll(async () => {
      const user = await dbHelper.createUser({
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      });
      authToken = await apiClient.authenticateUser(user);

      const conversation = await dbHelper.createConversation({
        userId: user.id,
        title: 'Test Conversation'
      });
      conversationId = conversation.id;
    });

    test('should handle message operations', async () => {
      // Send message
      const messageData = {
        content: 'Hello, this is a test message',
        role: 'user'
      };

      const createResponse = await apiClient.post(`/conversations/${conversationId}/messages`, messageData, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      expect(createResponse.status).toBe(201);
      expect(createResponse.data.data.content).toBe(messageData.content);

      const messageId = createResponse.data.data.id;

      // Get messages
      const listResponse = await apiClient.get(`/conversations/${conversationId}/messages`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      expect(listResponse.status).toBe(200);
      expect(listResponse.data.data.messages).toHaveLength(1);

      // Get specific message
      const getResponse = await apiClient.get(`/conversations/${conversationId}/messages/${messageId}`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      expect(getResponse.status).toBe(200);
      expect(getResponse.data.data.content).toBe(messageData.content);

      // Update message
      const updateData = { content: 'Updated message content' };
      const updateResponse = await apiClient.put(`/conversations/${conversationId}/messages/${messageId}`, updateData, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      expect(updateResponse.status).toBe(200);
      expect(updateResponse.data.data.content).toBe(updateData.content);

      // Delete message
      const deleteResponse = await apiClient.delete(`/conversations/${conversationId}/messages/${messageId}`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      expect(deleteResponse.status).toBe(200);
    });
  });

  describe('Analytics Integration', () => {
    let authToken: string;
    let conversationId: string;

    beforeAll(async () => {
      const user = await dbHelper.createUser({
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      });
      authToken = await apiClient.authenticateUser(user);

      const conversation = await dbHelper.createConversation({
        userId: user.id,
        title: 'Test Conversation'
      });
      conversationId = conversation.id;

      // Create test messages
      await dbHelper.createMessages(conversationId, [
        { content: 'Message 1', role: 'user', tokenCount: 5 },
        { content: 'Message 2', role: 'assistant', tokenCount: 10 },
        { content: 'Message 3', role: 'user', tokenCount: 3 }
      ]);
    });

    test('should provide analytics data', async () => {
      // Get overview analytics
      const overviewResponse = await apiClient.get('/analytics/overview', {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      expect(overviewResponse.status).toBe(200);
      expect(overviewResponse.data.data.totalConversations).toBe(1);
      expect(overviewResponse.data.data.totalMessages).toBe(3);
      expect(overviewResponse.data.data.totalTokens).toBe(18);

      // Get conversation analytics
      const conversationAnalytics = await apiClient.get('/analytics/conversations', {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      expect(conversationAnalytics.status).toBe(200);
      expect(conversationAnalytics.data.data.trends).toBeDefined();

      // Get specific conversation analytics
      const specificAnalytics = await apiClient.get(`/analytics/conversations/${conversationId}`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      expect(specificAnalytics.status).toBe(200);
      expect(specificAnalytics.data.data.messageCount).toBe(3);
      expect(specificAnalytics.data.data.tokenCount).toBe(18);
    });
  });

  describe('Error Handling', () => {
    test('should handle validation errors', async () => {
      // Invalid signup data
      const invalidSignupData = {
        name: '', // Required field
        email: 'invalid-email', // Invalid format
        password: '123' // Too short
      };

      const signupResponse = await apiClient.post('/auth/signup', invalidSignupData);
      expect(signupResponse.status).toBe(400);
      expect(signupResponse.data.statusCode).toBe('40000');
      expect(signupResponse.data.details).toBeDefined();
    });

    test('should handle authentication errors', async () => {
      // Access protected resource without token
      const noTokenResponse = await apiClient.get('/profile/me');
      expect(noTokenResponse.status).toBe(401);

      // Access with invalid token
      const invalidTokenResponse = await apiClient.get('/profile/me', {
        headers: { Authorization: 'Bearer invalid-token' }
      });
      expect(invalidTokenResponse.status).toBe(401);
    });

    test('should handle not found errors', async () => {
      const user = await dbHelper.createUser({
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      });
      const authToken = await apiClient.authenticateUser(user);

      // Non-existent conversation
      const notFoundResponse = await apiClient.get('/conversations/non-existent-id', {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      expect(notFoundResponse.status).toBe(404);
      expect(notFoundResponse.data.statusCode).toBe('40400');
    });

    test('should handle rate limiting', async () => {
      const user = await dbHelper.createUser({
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      });
      const authToken = await apiClient.authenticateUser(user);

      // Make many requests quickly
      const requests = Array.from({ length: 110 }, () =>
        apiClient.get('/conversations', {
          headers: { Authorization: `Bearer ${authToken}` }
        })
      );

      const responses = await Promise.allSettled(requests);
      const rateLimitedResponses = responses.filter(
        result => result.status === 'fulfilled' && result.value.status === 429
      );

      expect(rateLimitedResponses.length).toBeGreaterThan(0);
    });
  });
});
```

### 3. Database Integration Testing

```typescript
// packages/database/tests/integration/database-integration.test.ts
import { describe, test, expect, beforeAll, afterAll } from 'vitest';
import { DatabaseConnection } from '../../src/connection/database-connection';
import { TransactionManager } from '../../src/integration/transaction-manager';
import { ConversationRepository } from '../../src/repositories/conversation-repository';
import { MessageRepository } from '../../src/repositories/message-repository';
import { UserRepository } from '../../src/repositories/user-repository';

describe('Database Integration Tests', () => {
  let db: DatabaseConnection;
  let transactionManager: TransactionManager;
  let conversationRepo: ConversationRepository;
  let messageRepo: MessageRepository;
  let userRepo: UserRepository;

  beforeAll(async () => {
    db = new DatabaseConnection();
    await db.connect();
    
    transactionManager = new TransactionManager(db);
    conversationRepo = new ConversationRepository(db);
    messageRepo = new MessageRepository(db);
    userRepo = new UserRepository(db);

    // Run migrations
    await db.runMigrations();
  });

  afterAll(async () => {
    await db.close();
  });

  describe('Transaction Management', () => {
    test('should handle successful transaction', async () => {
      const result = await transactionManager.withTransaction(async (tx) => {
        // Create user
        const user = await userRepo.create({
          name: 'Test User',
          email: 'test@example.com',
          password: 'hashed_password'
        }, tx);

        // Create conversation
        const conversation = await conversationRepo.create({
          userId: user.id,
          title: 'Test Conversation'
        }, tx);

        // Create message
        const message = await messageRepo.create({
          conversationId: conversation.id,
          content: 'Test message',
          role: 'user',
          tokenCount: 5
        }, tx);

        return { user, conversation, message };
      });

      expect(result.user.id).toBeDefined();
      expect(result.conversation.id).toBeDefined();
      expect(result.message.id).toBeDefined();

      // Verify data persisted
      const persistedUser = await userRepo.findById(result.user.id);
      expect(persistedUser).toBeDefined();
      expect(persistedUser.email).toBe('test@example.com');

      const persistedConversation = await conversationRepo.findById(result.conversation.id);
      expect(persistedConversation).toBeDefined();
      expect(persistedConversation.title).toBe('Test Conversation');

      const persistedMessage = await messageRepo.findById(result.message.id);
      expect(persistedMessage).toBeDefined();
      expect(persistedMessage.content).toBe('Test message');
    });

    test('should handle transaction rollback on error', async () => {
      const initialUserCount = await userRepo.count();
      const initialConversationCount = await conversationRepo.count();

      await expect(
        transactionManager.withTransaction(async (tx) => {
          // Create user
          const user = await userRepo.create({
            name: 'Test User',
            email: 'rollback@example.com',
            password: 'hashed_password'
          }, tx);

          // Create conversation
          await conversationRepo.create({
            userId: user.id,
            title: 'Test Conversation'
          }, tx);

          // Simulate error
          throw new Error('Transaction should rollback');
        })
      ).rejects.toThrow('Transaction should rollback');

      // Verify rollback
      const finalUserCount = await userRepo.count();
      const finalConversationCount = await conversationRepo.count();

      expect(finalUserCount).toBe(initialUserCount);
      expect(finalConversationCount).toBe(initialConversationCount);

      // Verify specific data doesn't exist
      const user = await userRepo.findByEmail('rollback@example.com');
      expect(user).toBeNull();
    });
  });

  describe('Cross-Repository Operations', () => {
    test('should handle complex queries across repositories', async () => {
      // Create test data
      const user = await userRepo.create({
        name: 'Test User',
        email: 'complex@example.com',
        password: 'hashed_password'
      });

      const conversation1 = await conversationRepo.create({
        userId: user.id,
        title: 'Conversation 1'
      });

      const conversation2 = await conversationRepo.create({
        userId: user.id,
        title: 'Conversation 2'
      });

      // Add messages to conversations
      await messageRepo.create({
        conversationId: conversation1.id,
        content: 'Message 1',
        role: 'user',
        tokenCount: 5
      });

      await messageRepo.create({
        conversationId: conversation1.id,
        content: 'Message 2',
        role: 'assistant',
        tokenCount: 10
      });

      await messageRepo.create({
        conversationId: conversation2.id,
        content: 'Message 3',
        role: 'user',
        tokenCount: 3
      });

      // Test cross-repository queries
      const userWithConversations = await userRepo.findByIdWithConversations(user.id);
      expect(userWithConversations.conversations).toHaveLength(2);

      const conversationWithMessages = await conversationRepo.findByIdWithMessages(conversation1.id);
      expect(conversationWithMessages.messages).toHaveLength(2);

      const userMessageCount = await messageRepo.countByUserId(user.id);
      expect(userMessageCount).toBe(3);

      const userTokenCount = await messageRepo.getTotalTokensByUserId(user.id);
      expect(userTokenCount).toBe(18);
    });

    test('should handle concurrent operations', async () => {
      const user = await userRepo.create({
        name: 'Concurrent User',
        email: 'concurrent@example.com',
        password: 'hashed_password'
      });

      const conversation = await conversationRepo.create({
        userId: user.id,
        title: 'Concurrent Conversation'
      });

      // Create messages concurrently
      const messagePromises = Array.from({ length: 10 }, (_, i) =>
        messageRepo.create({
          conversationId: conversation.id,
          content: `Concurrent message ${i + 1}`,
          role: i % 2 === 0 ? 'user' : 'assistant',
          tokenCount: Math.floor(Math.random() * 10) + 1
        })
      );

      const messages = await Promise.all(messagePromises);
      expect(messages).toHaveLength(10);

      // Verify all messages were created
      const conversationMessages = await messageRepo.findByConversationId(conversation.id);
      expect(conversationMessages).toHaveLength(10);

      // Verify message order
      const sortedMessages = conversationMessages.sort((a, b) => 
        new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
      );
      expect(sortedMessages[0].content).toBe('Concurrent message 1');
      expect(sortedMessages[9].content).toBe('Concurrent message 10');
    });
  });

  describe('Data Consistency', () => {
    test('should maintain referential integrity', async () => {
      const user = await userRepo.create({
        name: 'Integrity User',
        email: 'integrity@example.com',
        password: 'hashed_password'
      });

      const conversation = await conversationRepo.create({
        userId: user.id,
        title: 'Integrity Conversation'
      });

      const message = await messageRepo.create({
        conversationId: conversation.id,
        content: 'Integrity message',
        role: 'user',
        tokenCount: 5
      });

      // Try to delete user (should fail due to foreign key constraint)
      await expect(userRepo.delete(user.id)).rejects.toThrow();

      // Try to delete conversation (should fail due to foreign key constraint)
      await expect(conversationRepo.delete(conversation.id)).rejects.toThrow();

      // Delete message first
      await messageRepo.delete(message.id);

      // Now delete conversation
      await conversationRepo.delete(conversation.id);

      // Now delete user
      await userRepo.delete(user.id);

      // Verify deletions
      const deletedUser = await userRepo.findById(user.id);
      expect(deletedUser).toBeNull();

      const deletedConversation = await conversationRepo.findById(conversation.id);
      expect(deletedConversation).toBeNull();

      const deletedMessage = await messageRepo.findById(message.id);
      expect(deletedMessage).toBeNull();
    });

    test('should handle unique constraints', async () => {
      await userRepo.create({
        name: 'Unique User',
        email: 'unique@example.com',
        password: 'hashed_password'
      });

      // Try to create user with same email
      await expect(
        userRepo.create({
          name: 'Another User',
          email: 'unique@example.com',
          password: 'hashed_password'
        })
      ).rejects.toThrow();
    });
  });

  describe('Performance Testing', () => {
    test('should handle bulk operations efficiently', async () => {
      const user = await userRepo.create({
        name: 'Bulk User',
        email: 'bulk@example.com',
        password: 'hashed_password'
      });

      const conversation = await conversationRepo.create({
        userId: user.id,
        title: 'Bulk Conversation'
      });

      // Test bulk insert performance
      const startTime = Date.now();
      
      const bulkMessages = Array.from({ length: 1000 }, (_, i) => ({
        conversationId: conversation.id,
        content: `Bulk message ${i + 1}`,
        role: i % 2 === 0 ? 'user' : 'assistant',
        tokenCount: Math.floor(Math.random() * 10) + 1
      }));

      await messageRepo.bulkCreate(bulkMessages);
      
      const endTime = Date.now();
      const duration = endTime - startTime;

      // Should complete within reasonable time (adjust based on requirements)
      expect(duration).toBeLessThan(5000); // 5 seconds

      // Verify all messages were inserted
      const messageCount = await messageRepo.countByConversationId(conversation.id);
      expect(messageCount).toBe(1000);
    });

    test('should handle complex queries efficiently', async () => {
      // Create test data
      const users = await Promise.all(
        Array.from({ length: 10 }, (_, i) =>
          userRepo.create({
            name: `Performance User ${i + 1}`,
            email: `perf${i + 1}@example.com`,
            password: 'hashed_password'
          })
        )
      );

      const conversations = await Promise.all(
        users.flatMap(user =>
          Array.from({ length: 5 }, (_, i) =>
            conversationRepo.create({
              userId: user.id,
              title: `Performance Conversation ${i + 1}`
            })
          )
        )
      );

      // Add messages to conversations
      await Promise.all(
        conversations.flatMap(conversation =>
          Array.from({ length: 20 }, (_, i) =>
            messageRepo.create({
              conversationId: conversation.id,
              content: `Performance message ${i + 1}`,
              role: i % 2 === 0 ? 'user' : 'assistant',
              tokenCount: Math.floor(Math.random() * 10) + 1
            })
          )
        )
      );

      // Test complex query performance
      const startTime = Date.now();
      
      const analytics = await db.query(`
        SELECT 
          u.id as user_id,
          u.name as user_name,
          COUNT(DISTINCT c.id) as conversation_count,
          COUNT(m.id) as message_count,
          SUM(m.token_count) as total_tokens,
          AVG(m.token_count) as avg_tokens_per_message
        FROM users u
        LEFT JOIN conversations c ON u.id = c.user_id
        LEFT JOIN messages m ON c.id = m.conversation_id
        WHERE u.email LIKE 'perf%@example.com'
        GROUP BY u.id, u.name
        ORDER BY total_tokens DESC
      `);
      
      const endTime = Date.now();
      const duration = endTime - startTime;

      // Should complete within reasonable time
      expect(duration).toBeLessThan(1000); // 1 second

      // Verify results
      expect(analytics).toHaveLength(10);
      expect(analytics[0].conversation_count).toBe(5);
      expect(analytics[0].message_count).toBe(100);
    });
  });
});
```

## Performance Requirements
- **Page Load Time**: Initial page load within 3 seconds
- **API Response Time**: All API calls respond within 500ms
- **Real-time Latency**: WebSocket messages delivered within 100ms
- **Concurrent Users**: Support 100+ concurrent users
- **Memory Usage**: Client-side memory under 150MB, server under 1GB

## Acceptance Criteria
- [ ] Complete end-to-end user journey functional
- [ ] All Phase 2 components integrated and working
- [ ] Real-time features working across multiple users
- [ ] Analytics dashboard displaying accurate data
- [ ] Performance requirements met under load
- [ ] Cross-browser compatibility verified
- [ ] Mobile and tablet responsiveness validated
- [ ] Accessibility compliance (WCAG 2.1 AA) achieved
- [ ] Security audit completed with no critical issues
- [ ] MVP ready for production deployment

## Testing Procedures
1. **Integration Testing**: Complete system integration validation
2. **User Acceptance Testing**: End-to-end user flow validation
3. **Performance Testing**: Load and stress testing under realistic conditions
4. **Cross-Platform Testing**: Browser and device compatibility validation
5. **Security Testing**: Vulnerability assessment and penetration testing
6. **Accessibility Testing**: WCAG compliance and assistive technology testing

## Integration Points
- **All Phase 2 Weeks**: Complete system integration
- **Phase 1 Components**: File monitoring and data ingestion integration
- **External Services**: Authentication, monitoring, and logging integration

## Deployment Preparation
- Production environment configuration
- Database migration scripts
- Environment variable documentation
- Monitoring and alerting setup
- Backup and recovery procedures
- SSL certificate configuration
- CDN setup for static assets
- Load balancer configuration

## Risk Mitigation
- **Performance Bottlenecks**: Comprehensive load testing and optimization
- **Integration Issues**: Thorough cross-component testing
- **Security Vulnerabilities**: Multiple security audits and penetration testing
- **Browser Compatibility**: Extensive cross-browser testing
- **Data Integrity**: Database transaction testing and backup validation

## Success Metrics
- **Functionality**: 100% of acceptance criteria met
- **Performance**: All performance benchmarks achieved
- **Quality**: Zero critical bugs, <5 minor bugs
- **User Experience**: Smooth user flows with <2% error rate
- **Compatibility**: Works across 95% of target browsers/devices

## Post-Integration Tasks
- Performance monitoring setup
- User feedback collection system
- Error tracking and logging
- Documentation finalization
- Team handoff and knowledge transfer
- Production deployment checklist
- Rollback procedures documentation