# Week 5: Backend Foundation with Bun.serve()

## Overview
Establish the core backend API foundation using Bun's high-performance server capabilities. This week focuses on creating a robust HTTP server with REST endpoints, error handling, logging, and basic authentication middleware.

## Team Assignments
- **Backend Lead**: API design, Bun.serve() configuration, middleware development
- **Full-Stack Developer**: Database integration, authentication system, API testing
- **DevOps Engineer**: Environment setup, logging configuration, performance monitoring

## Daily Schedule

### Monday: Project Setup & Server Foundation
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Environment setup and dependency installation
- **10:30-12:00**: Basic Bun.serve() configuration and project structure

#### Afternoon (4 hours)
- **13:00-15:00**: HTTP server setup with routing foundation
- **15:00-17:00**: Basic middleware implementation (CORS, body parsing)

### Tuesday: Core API Endpoints
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Health check and status endpoints
- **10:30-12:00**: Conversation management endpoints design

#### Afternoon (4 hours)
- **13:00-15:00**: Message processing endpoints
- **15:00-17:00**: File upload and JSONL handling endpoints

### Wednesday: Database Integration
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Database connection and schema setup
- **10:30-12:00**: Repository pattern implementation

#### Afternoon (4 hours)
- **13:00-15:00**: Data access layer for conversations
- **15:00-17:00**: Message and file storage operations

### Thursday: Authentication & Security
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: JWT authentication middleware
- **10:30-12:00**: User session management

#### Afternoon (4 hours)
- **13:00-15:00**: API key authentication for external access
- **15:00-17:00**: Security headers and rate limiting

### Friday: Testing & Documentation
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Unit tests for core modules
- **10:30-12:00**: Integration tests for API endpoints

#### Afternoon (4 hours)
- **13:00-15:00**: API documentation generation
- **15:00-17:00**: Performance testing and optimization

## Technical Implementation Details

### Server Configuration
```typescript
// server.ts
import { serve } from "bun";
import { cors } from "./middleware/cors";
import { logger } from "./middleware/logger";
import { auth } from "./middleware/auth";
import { router } from "./routes";

const server = serve({
  port: process.env.PORT || 3001,
  hostname: process.env.HOST || "localhost",
  development: process.env.NODE_ENV !== "production",
  
  async fetch(request, server) {
    const url = new URL(request.url);
    
    // Apply middleware
    const corsResponse = cors(request);
    if (corsResponse) return corsResponse;
    
    // Log request
    logger.info(`${request.method} ${url.pathname}`);
    
    try {
      // Route handling
      return await router.handle(request, server);
    } catch (error) {
      logger.error("Request error:", error);
      return new Response(
        JSON.stringify({ error: "Internal server error" }),
        { 
          status: 500, 
          headers: { "Content-Type": "application/json" } 
        }
      );
    }
  },
  
  error(error) {
    logger.error("Server error:", error);
    return new Response("Internal Server Error", { status: 500 });
  }
});

console.log(`🚀 Server running at ${server.url}`);
```

### Router Implementation
```typescript
// routes/index.ts
import { healthRoutes } from "./health";
import { conversationRoutes } from "./conversations";
import { messageRoutes } from "./messages";
import { fileRoutes } from "./files";

export class Router {
  private routes = new Map<string, (request: Request) => Promise<Response>>();
  
  constructor() {
    this.setupRoutes();
  }
  
  private setupRoutes() {
    // Health endpoints
    this.routes.set("GET:/health", healthRoutes.health);
    this.routes.set("GET:/health/ready", healthRoutes.ready);
    
    // Conversation endpoints
    this.routes.set("GET:/api/conversations", conversationRoutes.list);
    this.routes.set("POST:/api/conversations", conversationRoutes.create);
    this.routes.set("GET:/api/conversations/:id", conversationRoutes.get);
    
    // Message endpoints
    this.routes.set("GET:/api/conversations/:id/messages", messageRoutes.list);
    this.routes.set("POST:/api/conversations/:id/messages", messageRoutes.create);
    
    // File processing endpoints
    this.routes.set("POST:/api/files/upload", fileRoutes.upload);
    this.routes.set("POST:/api/files/process-jsonl", fileRoutes.processJsonl);
  }
  
  async handle(request: Request, server: any): Promise<Response> {
    const url = new URL(request.url);
    const routeKey = `${request.method}:${url.pathname}`;
    
    const handler = this.routes.get(routeKey);
    if (handler) {
      return await handler(request);
    }
    
    return new Response("Not Found", { status: 404 });
  }
}
```

### Database Integration
```typescript
// database/connection.ts
import { Database } from "bun:sqlite";

export class DatabaseManager {
  private db: Database;
  
  constructor(dbPath: string = "./data/observatory.db") {
    this.db = new Database(dbPath, { create: true });
    this.initialize();
  }
  
  private initialize() {
    // Create tables
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        metadata TEXT
      );
      
      CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        conversation_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        token_count INTEGER,
        metadata TEXT,
        FOREIGN KEY (conversation_id) REFERENCES conversations(id)
      );
      
      CREATE TABLE IF NOT EXISTS files (
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        size INTEGER NOT NULL,
        mime_type TEXT,
        uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        processed BOOLEAN DEFAULT FALSE
      );
    `);
  }
  
  // Conversation operations
  createConversation(data: ConversationData) {
    const stmt = this.db.prepare(`
      INSERT INTO conversations (id, title, metadata)
      VALUES (?, ?, ?)
    `);
    return stmt.run(data.id, data.title, JSON.stringify(data.metadata));
  }
  
  getConversation(id: string) {
    const stmt = this.db.prepare("SELECT * FROM conversations WHERE id = ?");
    return stmt.get(id);
  }
  
  listConversations(limit: number = 50, offset: number = 0) {
    const stmt = this.db.prepare(`
      SELECT * FROM conversations 
      ORDER BY updated_at DESC 
      LIMIT ? OFFSET ?
    `);
    return stmt.all(limit, offset);
  }
}
```

### Authentication Middleware
```typescript
// middleware/auth.ts
import jwt from "jsonwebtoken";

export interface AuthenticatedRequest extends Request {
  user?: {
    id: string;
    email: string;
    permissions: string[];
  };
}

export async function auth(request: Request): Promise<Response | null> {
  const authHeader = request.headers.get("Authorization");
  
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return new Response(
      JSON.stringify({ error: "Authentication required" }),
      { status: 401, headers: { "Content-Type": "application/json" } }
    );
  }
  
  const token = authHeader.substring(7);
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as any;
    
    // Attach user info to request (in production, store this differently)
    (request as any).user = {
      id: decoded.sub,
      email: decoded.email,
      permissions: decoded.permissions || []
    };
    
    return null; // Continue to next middleware
  } catch (error) {
    return new Response(
      JSON.stringify({ error: "Invalid token" }),
      { status: 401, headers: { "Content-Type": "application/json" } }
    );
  }
}
```

### Conversation Routes
```typescript
// routes/conversations.ts
import { DatabaseManager } from "../database/connection";
import { v4 as uuidv4 } from "uuid";

const db = new DatabaseManager();

export const conversationRoutes = {
  async list(request: Request): Promise<Response> {
    const url = new URL(request.url);
    const limit = parseInt(url.searchParams.get("limit") || "50");
    const offset = parseInt(url.searchParams.get("offset") || "0");
    
    try {
      const conversations = db.listConversations(limit, offset);
      return new Response(JSON.stringify(conversations), {
        headers: { "Content-Type": "application/json" }
      });
    } catch (error) {
      return new Response(
        JSON.stringify({ error: "Failed to fetch conversations" }),
        { status: 500, headers: { "Content-Type": "application/json" } }
      );
    }
  },
  
  async create(request: Request): Promise<Response> {
    try {
      const body = await request.json();
      const conversation = {
        id: uuidv4(),
        title: body.title || "New Conversation",
        metadata: body.metadata || {}
      };
      
      db.createConversation(conversation);
      
      return new Response(JSON.stringify(conversation), {
        status: 201,
        headers: { "Content-Type": "application/json" }
      });
    } catch (error) {
      return new Response(
        JSON.stringify({ error: "Failed to create conversation" }),
        { status: 500, headers: { "Content-Type": "application/json" } }
      );
    }
  },
  
  async get(request: Request): Promise<Response> {
    const url = new URL(request.url);
    const id = url.pathname.split("/").pop();
    
    if (!id) {
      return new Response(
        JSON.stringify({ error: "Conversation ID required" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }
    
    try {
      const conversation = db.getConversation(id);
      if (!conversation) {
        return new Response(
          JSON.stringify({ error: "Conversation not found" }),
          { status: 404, headers: { "Content-Type": "application/json" } }
        );
      }
      
      return new Response(JSON.stringify(conversation), {
        headers: { "Content-Type": "application/json" }
      });
    } catch (error) {
      return new Response(
        JSON.stringify({ error: "Failed to fetch conversation" }),
        { status: 500, headers: { "Content-Type": "application/json" } }
      );
    }
  }
};
```

## Performance Requirements
- **Response Time**: API endpoints must respond within 200ms for simple queries
- **Throughput**: Handle 1000 concurrent requests
- **Memory Usage**: Keep memory usage under 512MB during normal operation
- **Database**: All database operations should complete within 100ms

## Acceptance Criteria
- [ ] Bun.serve() HTTP server running and responding to requests
- [ ] REST API endpoints for conversations, messages, and files
- [ ] SQLite database integration with proper schema
- [ ] JWT-based authentication middleware
- [ ] CORS and security headers configured
- [ ] Comprehensive error handling and logging
- [ ] API documentation generated and accessible
- [ ] Unit and integration tests passing (>85% coverage)
- [ ] Performance benchmarks meeting requirements

## Testing Procedures
1. **Unit Tests**: Test individual modules and functions
2. **Integration Tests**: Test API endpoints end-to-end
3. **Load Testing**: Verify performance under concurrent load
4. **Security Testing**: Validate authentication and authorization
5. **Database Testing**: Verify data integrity and transaction handling

## Integration Points
- **Week 6**: WebSocket server integration for real-time features
- **Week 7**: Frontend API consumption
- **Phase 1**: File monitoring system data ingestion

## Documentation Requirements
- API endpoint documentation with request/response examples
- Authentication flow documentation
- Database schema documentation
- Deployment and configuration guide
- Performance tuning guide

## Risk Mitigation
- **Database Performance**: Implement connection pooling and query optimization
- **Memory Leaks**: Regular memory profiling and garbage collection monitoring
- **Security**: Regular security audits and dependency updates
- **Scalability**: Design for horizontal scaling from day one