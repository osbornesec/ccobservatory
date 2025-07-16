# 🏗️ Technical Architecture - Claude Code Observatory

## 📊 **System Architecture Overview**

### **High-Level Architecture** ✅ IMPLEMENTED

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   File System   │    │   Observatory    │    │   Dashboard     │
│     Monitor     │───▶│     Backend      │───▶│    Frontend     │
│  (Python Watch) │    │(FastAPI/WebSocket│    │  (SvelteKit)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ ~/.claude/      │    │    Database      │    │   Real-time     │
│   projects/     │    │  (Supabase)      │    │   Updates       │
│   *.jsonl       │    │  (PostgreSQL)    │    │  (WebSocket)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### **Technology Stack**

#### **Core Technologies** ✅ IMPLEMENTED
- **Backend Runtime:** Python 3.11 + FastAPI + Uvicorn
- **Frontend:** SvelteKit + TypeScript + Tailwind CSS + DaisyUI
- **Database:** Supabase (PostgreSQL) with Real-time subscriptions
- **File Monitoring:** Python Watchdog (cross-platform file watcher)
- **Real-time Communication:** WebSocket + Supabase Realtime
- **Build Tools:** Vite (frontend), Docker (containerization)

#### **Supporting Technologies** ✅ IMPLEMENTED
- **Testing:** pytest, Vitest, Playwright
- **Code Quality:** Black, Flake8, MyPy, ESLint, Prettier
- **Documentation:** TypeScript, Python docstrings
- **Containerization:** Docker multi-stage builds
- **CI/CD:** GitHub Actions with automated testing

## 🔧 **Core Components**

### **1. File System Monitor**

#### **Purpose**
Monitor `~/.claude/projects/` directory for changes to JSONL transcript files in real-time.

#### **Technology** ✅ IMPLEMENTED
- **Python Watchdog** with cross-platform file system monitoring
- **Incremental file reading** for performance optimization
- **Error recovery** for file system issues and permission errors

#### **Key Features**
- Real-time detection of new files (<100ms)
- Incremental reading of file updates
- Graceful handling of file system errors
- Support for multiple concurrent file changes
- Automatic recovery from temporary failures

#### **Implementation Details**

```typescript
// Core file monitoring interface
interface FileSystemWatcher {
  start(): Promise<void>;
  stop(): Promise<void>;
  on(event: 'file_created' | 'file_updated' | 'file_deleted', 
     handler: (event: TranscriptEvent) => void): void;
}

// File event structure
interface TranscriptEvent {
  type: 'file_created' | 'file_updated' | 'file_deleted';
  projectPath: string;
  sessionId: string;
  filePath: string;
  timestamp: number;
}
```

### **2. Observatory Backend**

#### **Purpose**
Process transcript files, manage data storage, and provide APIs for the frontend.

#### **Technology** ✅ IMPLEMENTED
- **FastAPI + Uvicorn** for async HTTP and WebSocket handling
- **Python + Pydantic** for type safety and data validation
- **Supabase (PostgreSQL)** for cloud-native data persistence

#### **Key Features**
- Real-time transcript processing
- RESTful API for data access
- WebSocket broadcasting for live updates
- Conversation parsing and analysis
- Project auto-discovery and management

#### **API Architecture**

```typescript
// Core API structure
interface APIEndpoints {
  // Conversations
  'GET /api/conversations': GetConversationsResponse;
  'GET /api/conversations/:id/messages': GetMessagesResponse;
  
  // Projects
  'GET /api/projects': GetProjectsResponse;
  'GET /api/projects/:id/analytics': GetProjectAnalyticsResponse;
  
  // Analytics
  'GET /api/analytics/overview': GetAnalyticsOverviewResponse;
  'GET /api/analytics/insights': GetInsightsResponse;
  
  // Live data
  'WS /stream': WebSocketEvents;
}
```

### **3. Dashboard Frontend**

#### **Purpose**
Provide intuitive interface for viewing conversations, analytics, and insights.

#### **Technology** ✅ IMPLEMENTED
- **SvelteKit** with TypeScript support and file-based routing
- **TypeScript** for type safety across all components
- **Tailwind CSS + DaisyUI** for responsive styling and component library
- **Vite** for optimized build tooling and hot module replacement

#### **Key Features**
- Real-time conversation viewing
- Advanced filtering and search
- Analytics dashboard with charts
- Team collaboration features
- Responsive mobile design

#### **Component Architecture**

```typescript
// Core component structure
interface ComponentHierarchy {
  App: {
    Router: {
      Dashboard: {
        ConversationViewer: Component;
        LiveStream: Component;
        Analytics: Component;
      };
      Projects: {
        ProjectList: Component;
        ProjectDetail: Component;
      };
      Settings: Component;
    };
    GlobalComponents: {
      Header: Component;
      Sidebar: Component;
      Notifications: Component;
    };
  };
}
```

### **4. Database Layer**

#### **Purpose**
Persist conversation data, analytics, and application state.

#### **Technology** ✅ IMPLEMENTED
- **Supabase (PostgreSQL)** with real-time subscriptions and built-in auth
- **Async connections** with connection pooling for performance
- **Comprehensive indexes** for query optimization and full-text search

#### **Schema Design**

```sql
-- Core tables
CREATE TABLE projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  path TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  is_active BOOLEAN DEFAULT 1
);

CREATE TABLE conversations (
  id TEXT PRIMARY KEY,
  project_id INTEGER NOT NULL,
  session_id TEXT NOT NULL,
  start_time INTEGER NOT NULL,
  end_time INTEGER,
  message_count INTEGER DEFAULT 0,
  tool_usage_count INTEGER DEFAULT 0,
  FOREIGN KEY (project_id) REFERENCES projects (id)
);

CREATE TABLE messages (
  id TEXT PRIMARY KEY,
  conversation_id TEXT NOT NULL,
  timestamp INTEGER NOT NULL,
  type TEXT NOT NULL, -- 'user', 'assistant', 'system'
  content TEXT NOT NULL,
  tool_usage JSON,
  parent_id TEXT,
  FOREIGN KEY (conversation_id) REFERENCES conversations (id),
  FOREIGN KEY (parent_id) REFERENCES messages (id)
);

CREATE TABLE analytics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER,
  metric_name TEXT NOT NULL,
  metric_value REAL NOT NULL,
  dimensions JSON,
  timestamp INTEGER NOT NULL,
  FOREIGN KEY (project_id) REFERENCES projects (id)
);
```

## 🔄 **Data Flow Architecture**

### **Real-Time Processing Pipeline**

```
1. File Change Detection
   └─ Chokidar detects .jsonl file changes
   
2. Content Parsing
   └─ Extract new messages from JSONL format
   
3. Data Processing
   └─ Parse message structure and relationships
   
4. Database Storage
   └─ Store messages, update conversation metadata
   
5. Real-Time Broadcasting
   └─ Send updates via WebSocket to connected clients
   
6. Frontend Updates
   └─ Update UI components with new data
```

### **JSONL Message Processing**

```typescript
// Claude Code JSONL message format
interface ClaudeMessage {
  uuid: string;
  sessionId: string;
  timestamp: string;
  type: 'user' | 'assistant' | 'system';
  message: {
    role: 'user' | 'assistant';
    content: string | ContentBlock[];
  };
  parentUuid?: string;
  cwd?: string;
  requestId?: string;
}

// Our normalized message format
interface NormalizedMessage {
  id: string;
  conversationId: string;
  timestamp: number;
  type: 'user' | 'assistant' | 'system';
  content: string;
  toolUse?: ToolUseBlock;
  toolResult?: ToolResultBlock;
  parentId?: string;
  metadata: MessageMetadata;
}
```

## 🔍 **Service Architecture**

### **File System Watcher Service**

```typescript
class FileSystemWatcher extends EventEmitter {
  private watcher: FSWatcher | null = null;
  private filePointers: Map<string, number> = new Map();
  
  async start(): Promise<void> {
    this.watcher = watch('~/.claude/projects/**/*.jsonl', {
      persistent: true,
      ignoreInitial: false,
      awaitWriteFinish: true
    });
    
    this.watcher
      .on('add', this.handleFileAdded.bind(this))
      .on('change', this.handleFileChanged.bind(this))
      .on('unlink', this.handleFileRemoved.bind(this));
  }
  
  private async handleFileChanged(filePath: string): Promise<void> {
    const content = await fs.readFile(filePath, 'utf-8');
    const lines = content.trim().split('\n');
    const lastPosition = this.filePointers.get(filePath) || 0;
    
    if (lines.length > lastPosition) {
      const newLines = lines.slice(lastPosition);
      await this.processNewLines(filePath, newLines);
      this.filePointers.set(filePath, lines.length);
    }
  }
}
```

### **Transcript Parser Service**

```typescript
class TranscriptParser {
  static parseMessage(rawMessage: any): ParsedMessage | null {
    // Handle different message types
    switch (rawMessage.type) {
      case 'user':
        return this.parseUserMessage(rawMessage);
      case 'assistant':
        return this.parseAssistantMessage(rawMessage);
      case 'system':
        return this.parseSystemMessage(rawMessage);
      default:
        return null;
    }
  }
  
  static extractToolUsage(message: ParsedMessage): ToolUsage | null {
    // Extract tool usage from assistant messages
    if (message.type === 'assistant' && message.toolUse) {
      return {
        toolName: message.toolUse.name,
        input: message.toolUse.input,
        toolId: message.toolUse.id
      };
    }
    return null;
  }
}
```

### **Analytics Engine**

```typescript
class AnalyticsEngine {
  async calculateConversationMetrics(
    conversationId: string
  ): Promise<ConversationMetrics> {
    return {
      duration: await this.calculateDuration(conversationId),
      messageCount: await this.getMessageCount(conversationId),
      toolUsageCount: await this.getToolUsageCount(conversationId),
      averageResponseTime: await this.getAverageResponseTime(conversationId),
      successRate: await this.calculateSuccessRate(conversationId)
    };
  }
  
  async generateInsights(
    projectId: number,
    timeRange: string
  ): Promise<Insight[]> {
    const patterns = await this.analyzeUsagePatterns(projectId, timeRange);
    return this.convertPatternsToInsights(patterns);
  }
}
```

## 🌐 **WebSocket Event Architecture**

### **Event Types**

```typescript
// Client to Server events
interface ClientEvents {
  subscribe: {
    projects: number[];
    eventTypes: string[];
  };
  unsubscribe: {
    projects: number[];
    eventTypes: string[];
  };
}

// Server to Client events
interface ServerEvents {
  new_message: {
    conversationId: string;
    message: NormalizedMessage;
    project: ProjectInfo;
  };
  conversation_start: {
    conversationId: string;
    sessionId: string;
    project: ProjectInfo;
    timestamp: number;
  };
  conversation_end: {
    conversationId: string;
    duration: number;
    messageCount: number;
    timestamp: number;
  };
  analytics_update: {
    projectId: number;
    metrics: AnalyticsUpdate;
  };
}
```

### **Real-Time Communication Flow**

```typescript
class WebSocketManager {
  private clients: Set<WebSocket> = new Set();
  
  broadcast(event: ServerEvent): void {
    const message = JSON.stringify(event);
    const clientsToRemove: WebSocket[] = [];
    
    this.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message);
      } else {
        clientsToRemove.push(client);
      }
    });
    
    clientsToRemove.forEach(client => this.clients.delete(client));
  }
  
  handleNewConnection(ws: WebSocket): void {
    this.clients.add(ws);
    
    // Send initial state
    ws.send(JSON.stringify({
      type: 'connection_established',
      data: {
        activeConversations: this.getActiveConversations(),
        projectActivity: this.getProjectActivity()
      }
    }));
  }
}
```

## 🔒 **Security Architecture**

### **Data Security**

#### **Local-First Design**
- All data stored locally by default
- No cloud dependencies required
- User controls all data access

#### **Optional Encryption**
- AES-256 encryption for sensitive projects
- User-controlled encryption keys
- Transparent encryption/decryption

### **Access Control**

```typescript
interface SecurityController {
  // File system access
  validateFilePath(path: string): boolean;
  checkFilePermissions(path: string): Promise<boolean>;
  
  // Data access
  authorizeProjectAccess(userId: string, projectId: number): boolean;
  authorizeConversationAccess(userId: string, conversationId: string): boolean;
  
  // API security
  validateRequest(request: Request): Promise<boolean>;
  rateLimit(clientId: string): boolean;
}
```

### **Privacy Controls**

```typescript
interface PrivacyManager {
  // Data anonymization
  anonymizeMessage(message: Message): Message;
  removePersonalInfo(content: string): string;
  
  // Data retention
  scheduleDataCleanup(retentionDays: number): void;
  exportUserData(userId: string): Promise<UserDataExport>;
  deleteUserData(userId: string): Promise<void>;
}
```

## 📈 **Performance Architecture**

### **Optimization Strategies**

#### **Database Performance**
- **Prepared Statements:** For frequent queries
- **Connection Pooling:** For concurrent access
- **Query Optimization:** Proper indexing strategy
- **Data Archiving:** Old data moved to separate tables

#### **Memory Management**
- **Streaming Processing:** Large files processed in chunks
- **Memory Limits:** Configurable limits for conversation storage
- **Garbage Collection:** Regular cleanup of unused data
- **Caching Strategy:** Intelligent caching of frequently accessed data

#### **Real-Time Performance**
- **Event Batching:** Group related events for efficiency
- **Debounced Updates:** Prevent excessive UI updates
- **Connection Management:** Efficient WebSocket handling
- **Message Queuing:** Handle high-volume message processing

### **Scalability Design**

```typescript
interface ScalabilityConfig {
  // File processing
  maxConcurrentFiles: number;
  batchSize: number;
  processingTimeout: number;
  
  // Database
  connectionPoolSize: number;
  queryTimeout: number;
  maxDatabaseSize: string;
  
  // WebSocket
  maxConnections: number;
  messageRateLimit: number;
  heartbeatInterval: number;
  
  // Memory
  maxMemoryUsage: string;
  gcInterval: number;
  cacheSize: number;
}
```

## 🔧 **Development Architecture**

### **Project Structure** ✅ IMPLEMENTED

```
claude-code-observatory/
├── backend/                     # Python FastAPI backend
│   ├── app/                     # Main application package
│   │   ├── api/                 # HTTP API endpoints
│   │   ├── websocket/           # WebSocket server
│   │   ├── database/            # Database layer with Supabase
│   │   ├── monitoring/          # File system monitoring
│   │   ├── analytics/           # Conversation analysis
│   │   └── auth/                # Authentication middleware
│   ├── tests/                   # Backend tests (pytest)
│   ├── requirements.txt         # Python dependencies
│   └── venv/                    # Virtual environment
├── frontend/                    # SvelteKit dashboard
│   ├── src/                     # Source code
│   │   ├── routes/              # SvelteKit file-based routing
│   │   ├── lib/                 # Shared components and utilities
│   │   ├── stores/              # Svelte stores for state management
│   │   └── app.html             # HTML template
│   ├── static/                  # Static assets
│   ├── package.json             # Node.js dependencies
│   └── svelte.config.js         # SvelteKit configuration
├── supabase/                    # Supabase configuration
│   ├── migrations/              # Database migrations (5 files)
│   ├── seed.sql                 # Database seed data
│   └── config.toml              # Supabase configuration
├── docs/                        # Documentation
├── tests/                       # Integration and E2E tests
├── scripts/                     # Build and deployment scripts
├── Makefile                     # 70+ development commands
└── docker-compose.yml           # Multi-service orchestration
```

### **Build & Deployment Pipeline** ✅ IMPLEMENTED

```bash
# Development (70+ Make commands available)
make dev                    # Start all services concurrently
make dev-backend            # Start FastAPI backend with hot reload
make dev-frontend           # Start SvelteKit dev server
make dev-supabase           # Start local Supabase instance

# Testing (Comprehensive test coverage)
make test                   # Run all tests (97 backend + frontend)
make test-backend           # Run pytest backend tests
make test-frontend          # Run Vitest frontend tests
make test-e2e              # Run Playwright end-to-end tests
make test-performance      # Run performance benchmarks
make test-watch            # Continuous testing during development

# Code Quality (Automated quality gates)
make lint                  # Run all linters (Black, Flake8, MyPy, ESLint)
make format                # Format all code (Black, Prettier)
make type-check            # TypeScript and MyPy type checking

# Production (Docker-based deployment)
make build                 # Build all components
make build-docker          # Build Docker images (371MB backend)
make deploy-docker         # Deploy to production
make ci                    # Full CI pipeline (test + lint + build)
```

---

*This technical architecture provides a comprehensive foundation for building Claude Code Observatory with proper separation of concerns, scalability considerations, and robust real-time capabilities.*