# Claude Code Observatory - Backend

This is the backend API server for the Claude Code Observatory (CCO) project. It provides a RESTful API and WebSocket support for real-time monitoring of Claude Code interactions.

## 🚀 Quick Start

### Prerequisites

- **Bun** runtime (latest version)
- **Node.js** 18+ (for compatibility)
- **TypeScript** 5.0+

### Installation

```bash
# Install dependencies
bun install

# Build the project
bun run build

# Start development server
bun run dev

# Start production server
bun run start
```

### Environment Configuration

Create a `.env` file in the backend directory:

```env
# Server Configuration
PORT=3000
HOST=localhost
NODE_ENV=development

# Database Configuration
DATABASE_PATH=./data/claude_observatory.db
DB_MAX_CONNECTIONS=10
DB_TIMEOUT=30000

# Claude Configuration
CLAUDE_PROJECTS_PATH=~/.claude/projects

# Security Configuration
JWT_SECRET=your-secret-key-here
JWT_EXPIRES_IN=24h
BCRYPT_SALT_ROUNDS=10

# CORS Configuration
CORS_ORIGIN=http://localhost:5173

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX=100

# WebSocket Configuration
WS_MAX_CONNECTIONS=100
WS_PING_INTERVAL=30000
WS_PONG_TIMEOUT=5000

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=3001
LOG_LEVEL=info
```

## 🏗️ Architecture

### Tech Stack

- **Runtime**: Bun (JavaScript/TypeScript runtime)
- **Language**: TypeScript with strict type checking
- **Database**: SQLite with WAL mode (via @cco/database)
- **File Monitoring**: Chokidar (via @cco/file-monitor)
- **Authentication**: JWT with bcrypt password hashing
- **WebSocket**: Native Bun WebSocket support
- **Validation**: Zod schema validation
- **Security**: Helmet, CORS, Rate limiting

### Directory Structure

```
packages/backend/src/
├── app.ts                 # Main application with Bun fetch handler
├── server.ts              # Server startup and lifecycle management
├── index.ts               # Package entry point
├── auth/                  # Authentication system
│   ├── jwt.ts            # JWT token management
│   ├── password.ts       # Password hashing with bcrypt
│   └── index.ts          # Auth module exports
├── config/               # Configuration management
│   └── index.ts          # Environment-based configuration
├── controllers/          # Business logic controllers
│   └── index.ts          # MVC pattern controllers
├── database/             # Database integration
│   └── index.ts          # @cco/database package integration
├── middleware/           # HTTP middleware stack
│   ├── auth.ts           # JWT authentication middleware
│   ├── cors.ts           # CORS handling
│   ├── helmet.ts         # Security headers
│   ├── rate-limit.ts     # IP-based rate limiting
│   ├── compression.ts    # Response compression
│   ├── logger.ts         # Request logging
│   ├── error-handler.ts  # Centralized error handling
│   └── index.ts          # Middleware orchestration
├── repositories/         # Data access layer
│   └── index.ts          # Repository pattern implementations
├── routes/               # API endpoints
│   ├── auth.ts           # Authentication routes
│   ├── conversations.ts  # Conversation management
│   ├── projects.ts       # Project management
│   ├── health.ts         # Health check endpoints
│   ├── websocket.ts      # WebSocket status endpoints
│   └── index.ts          # Route registration
├── services/             # Business services
│   ├── file-monitor.ts   # File system monitoring service
│   └── index.ts          # Service exports
├── types/                # TypeScript definitions
│   ├── api.ts            # API-specific types
│   ├── config.ts         # Configuration types
│   └── index.ts          # Type aggregation
├── utils/                # Utility functions
│   ├── logger.ts         # Structured logging
│   ├── validators.ts     # Zod validation schemas
│   ├── response.ts       # HTTP response helpers
│   └── index.ts          # Utility exports
├── validation/           # Validation middleware
│   └── index.ts          # Request validation helpers
└── websocket/            # WebSocket server
    └── index.ts          # Real-time communication
```

## 📡 API Endpoints

### Authentication

#### `POST /auth/login`
User authentication with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "role": "user",
      "createdAt": "2023-01-01T00:00:00.000Z"
    },
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 86400
  }
}
```

#### `POST /auth/register`
User registration with email and password.

#### `POST /auth/refresh`
Refresh JWT access token.

#### `GET /auth/profile` (Protected)
Get current user profile.

### Projects

#### `GET /api/projects`
List all projects with pagination.

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20)
- `sort`: Sort field (default: 'updatedAt')
- `order`: Sort order ('asc' or 'desc', default: 'desc')

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "proj_123",
      "name": "My Project",
      "description": "Project description",
      "claudePath": "/path/to/claude/project",
      "settings": {},
      "createdAt": "2023-01-01T00:00:00.000Z",
      "updatedAt": "2023-01-01T00:00:00.000Z",
      "conversationCount": 15,
      "lastActivity": "2023-01-01T00:00:00.000Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "pages": 1,
    "hasNext": false,
    "hasPrev": false
  }
}
```

#### `GET /api/projects/:id`
Get specific project details.

#### `POST /api/projects` (Protected)
Create a new project.

#### `PUT /api/projects/:id` (Protected)
Update project details.

#### `DELETE /api/projects/:id` (Protected)
Delete a project.

### Conversations

#### `GET /api/conversations`
List conversations with filtering and pagination.

**Query Parameters:**
- `projectId`: Filter by project ID
- `status`: Filter by status ('active', 'completed', 'error')
- `startDate`: Filter by start date
- `endDate`: Filter by end date
- `page`: Page number
- `limit`: Items per page

#### `GET /api/conversations/:id`
Get conversation details.

#### `GET /api/conversations/:id/messages`
Get conversation messages.

#### `GET /api/conversations/:id/analytics`
Get conversation analytics.

### Health & Monitoring

#### `GET /health`
Basic health check.

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2023-01-01T00:00:00.000Z",
    "uptime": 3600,
    "version": "1.0.0",
    "services": {
      "database": "healthy",
      "fileMonitor": "healthy",
      "websocket": "healthy"
    }
  }
}
```

#### `GET /health/ready`
Readiness check for deployment.

### WebSocket Status

#### `GET /api/websocket/status`
Get WebSocket server status.

#### `GET /api/websocket/clients`
Get connected WebSocket clients (admin only).

## 🔌 WebSocket Support

### Connection

Connect to WebSocket at `ws://localhost:3000/ws`

### Message Types

#### Client → Server

**Subscribe to Channel:**
```json
{
  "type": "subscribe",
  "channel": "conversations"
}
```

**Unsubscribe from Channel:**
```json
{
  "type": "unsubscribe",
  "channel": "conversations"
}
```

**Pong Response:**
```json
{
  "type": "pong",
  "timestamp": 1640995200000
}
```

#### Server → Client

**Welcome Message:**
```json
{
  "type": "welcome",
  "clientId": "client_123",
  "timestamp": 1640995200000
}
```

**Ping:**
```json
{
  "type": "ping",
  "timestamp": 1640995200000
}
```

**Broadcast:**
```json
{
  "type": "broadcast",
  "channel": "conversations",
  "data": {
    "event": "conversation_updated",
    "conversation": { ... }
  },
  "timestamp": 1640995200000
}
```

### Available Channels

- `conversations`: Real-time conversation updates
- `projects`: Project changes
- `files`: File system events
- `system`: System notifications

## 🔒 Security

### Authentication

- JWT-based authentication with configurable expiration
- Password hashing using bcrypt with configurable salt rounds
- Refresh token support for extended sessions

### Security Headers

- XSS protection
- CSRF protection
- Content type sniffing protection
- Clickjacking protection
- HTTPS enforcement in production

### Rate Limiting

- IP-based rate limiting
- Configurable windows and limits
- Different limits for different endpoints

### Input Validation

- Schema validation using Zod
- Request body size limits
- Parameter sanitization

## 🛠️ Development

### Scripts

```bash
# Development
bun run dev          # Start with hot reload
bun run build        # Build for production
bun run start        # Start production server

# Testing
bun run test         # Run tests
bun run test:watch   # Run tests in watch mode

# Code Quality
bun run lint         # Run ESLint
bun run lint:fix     # Fix ESLint issues
bun run type-check   # TypeScript type checking

# Utilities
bun run clean        # Clean build artifacts
```

### Development Workflow

1. **Start Development Server**
   ```bash
   bun run dev
   ```

2. **Make Changes**
   - Edit files in `src/`
   - Server automatically restarts on changes

3. **Test Changes**
   ```bash
   bun run test
   ```

4. **Check Code Quality**
   ```bash
   bun run lint
   bun run type-check
   ```

### Adding New Routes

1. **Create Route File**
   ```typescript
   // src/routes/my-route.ts
   import type { APIRequest, APIResponse } from '@/types/api';
   
   const myHandler = async (req: APIRequest, res: APIResponse) => {
     // Implementation
   };
   
   export const myRoutes = new Map([
     ['GET /api/my-endpoint', myHandler]
   ]);
   ```

2. **Register Route**
   ```typescript
   // src/routes/index.ts
   import { myRoutes } from './my-route';
   
   export const setupRoutes = (routes) => {
     // ... existing routes
     myRoutes.forEach((handler, path) => {
       routes.set(path, handler);
     });
   };
   ```

### Adding Middleware

1. **Create Middleware**
   ```typescript
   // src/middleware/my-middleware.ts
   import type { APIRequest, APIResponse } from '@/types/api';
   
   export const myMiddleware = (req: APIRequest, res: APIResponse, next: () => void) => {
     // Implementation
     next();
   };
   ```

2. **Register Middleware**
   ```typescript
   // src/middleware/index.ts
   import { myMiddleware } from './my-middleware';
   
   export const setupMiddleware = (middleware) => {
     // ... existing middleware
     middleware.push(myMiddleware);
   };
   ```

## 📊 Monitoring

### Health Checks

- `/health` - Basic health status
- `/health/ready` - Service readiness for load balancers
- Built-in uptime and memory monitoring

### Metrics

- Request/response times
- Error rates
- WebSocket connection counts
- Database query performance

### Logging

- Structured JSON logging
- Configurable log levels
- Request/response logging
- Error tracking

## 🧪 Testing

### Unit Tests

```bash
bun run test
```

### Integration Tests

```bash
bun run test:integration
```

### Load Testing

```bash
bun run test:load
```

## 🚀 Production Deployment

### Environment Variables

Ensure all production environment variables are set:

```env
NODE_ENV=production
PORT=3000
DATABASE_PATH=/data/claude_observatory.db
JWT_SECRET=your-production-secret
CORS_ORIGIN=https://yourdomain.com
```

### Build and Start

```bash
bun run build
bun run start
```

### Health Checks

- Health endpoint: `GET /health`
- Readiness endpoint: `GET /health/ready`

### Monitoring

- Enable metrics: `ENABLE_METRICS=true`
- Metrics port: `METRICS_PORT=3001`
- Log level: `LOG_LEVEL=warn`

## 📈 Performance

### Database Optimization

- SQLite WAL mode for better concurrency
- Prepared statements for query optimization
- Connection pooling
- Proper indexing

### Caching

- In-memory caching for frequently accessed data
- Redis support for distributed caching
- HTTP response caching

### WebSocket Performance

- Connection pooling
- Message compression
- Efficient channel management
- Automatic cleanup of inactive connections

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Check `DATABASE_PATH` environment variable
   - Ensure database file permissions
   - Verify WAL mode is enabled

2. **WebSocket Connection Problems**
   - Check `WS_MAX_CONNECTIONS` limit
   - Verify WebSocket upgrade headers
   - Check client authentication

3. **File Monitoring Issues**
   - Verify `CLAUDE_PROJECTS_PATH` exists
   - Check file permissions
   - Ensure file watcher is running

### Debug Mode

Enable debug logging:

```env
LOG_LEVEL=debug
```

### Performance Monitoring

Enable metrics collection:

```env
ENABLE_METRICS=true
METRICS_PORT=3001
```

## 📚 API Documentation

For detailed API documentation, see:
- [OpenAPI/Swagger Documentation](./docs/api.md)
- [WebSocket API](./docs/websocket.md)
- [Authentication Guide](./docs/auth.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run linting and type checking
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.