# Claude Code Observatory

<div align="center">

![Logo Placeholder](https://via.placeholder.com/200x100/2563eb/ffffff?text=CCO)

**The definitive observability platform for Claude Code interactions**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![SvelteKit](https://img.shields.io/badge/SvelteKit-Latest-orange.svg)](https://kit.svelte.dev/)
[![Supabase](https://img.shields.io/badge/Supabase-Database-green.svg)](https://supabase.com/)

</div>

## 🎯 Overview

Claude Code Observatory (CCO) provides complete conversation visibility, real-time monitoring, and actionable insights for developers and teams using Claude Code. The system monitors `~/.claude/projects/` directory to parse JSONL transcript files and provide comprehensive analytics.

### Key Features

- **100% Conversation Capture** - Complete visibility into Claude Code interactions
- **Real-time Monitoring** - Live updates via WebSocket connections
- **Zero Configuration** - Automatic project discovery and setup
- **Advanced Analytics** - Insights into conversation patterns and tool usage
- **Team Collaboration** - Share insights and learn from development patterns

## 🏗️ Technology Stack

### Backend (Python)
- **Framework**: FastAPI with async/await support
- **Database**: Supabase (managed PostgreSQL)
- **File Monitoring**: Python `watchdog` for cross-platform file system watching
- **WebSocket**: Native FastAPI WebSocket support
- **Testing**: pytest with comprehensive coverage (80-90% target)
- **Container**: Docker with multi-stage builds

### Frontend (SvelteKit + TypeScript)
- **Framework**: SvelteKit with TypeScript
- **Styling**: Tailwind CSS + DaisyUI components
- **Build Tool**: Vite for fast development and building
- **Testing**: Vitest for unit testing, Playwright for E2E
- **State Management**: Svelte stores with Supabase Realtime
- **Accessibility**: WCAG 2.1 AA compliance with comprehensive a11y features

### Database & Infrastructure
- **Primary Database**: Supabase (PostgreSQL with real-time subscriptions)
- **Authentication**: Supabase Auth with JWT tokens
- **Real-time**: Supabase Realtime + WebSocket for live updates
- **File Storage**: Local file system monitoring
- **Deployment**: Docker + Kubernetes, GitHub Actions CI/CD

### Development Methodology
- **TDD**: Canon TDD approach with disciplined test-first development
- **Testing**: 80-90% code coverage with performance benchmarks
- **Quality**: ESLint, Prettier, Pylint, Black formatting
- **Monitoring**: Real-time performance monitoring with <100ms file detection latency

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Supabase CLI (optional, for local development)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/osbornesec/ccobservatory.git
   cd ccobservatory
   ```

2. **Start all services**
   ```bash
   make dev
   ```

3. **Or start individual services**
   ```bash
   # Backend (Python FastAPI)
   make dev-backend
   
   # Frontend (SvelteKit)
   make dev-frontend
   
   # Local Supabase (optional)
   make dev-supabase
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Environment Setup

Copy the environment template and configure:

```bash
# Backend
cp backend/env.template backend/.env

# Frontend (if needed)
cp frontend/.env.example frontend/.env
```

## 📁 Project Structure

```
claude-code-observatory/
├── backend/                    # Python FastAPI backend
│   ├── app/                    # Main application
│   │   ├── api/                # HTTP API endpoints
│   │   ├── monitoring/         # File system monitoring
│   │   ├── database/           # Database layer (Supabase)
│   │   ├── websocket/          # WebSocket server
│   │   └── analytics/          # Conversation analysis
│   ├── tests/                  # Backend tests (pytest)
│   └── requirements.txt        # Python dependencies
├── frontend/                   # SvelteKit frontend
│   ├── src/
│   │   ├── routes/             # SvelteKit file-based routing
│   │   ├── lib/                # Shared components and utilities
│   │   │   ├── components/     # Svelte components
│   │   │   ├── stores/         # Svelte stores
│   │   │   └── api/            # API client
│   │   └── app.html            # HTML template
│   ├── static/                 # Static assets
│   └── package.json            # Node.js dependencies
├── supabase/                   # Supabase configuration
│   ├── migrations/             # Database migrations
│   └── config.toml             # Supabase settings
├── docs/                       # Comprehensive documentation
└── scripts/                    # Build and deployment scripts
```

## 🧪 Testing & Development

### Backend Testing (Canon TDD)
```bash
# Run all backend tests
make test-backend

# Run with coverage
make test-coverage

# Run specific test file
pytest backend/tests/test_file_monitor.py -v

# Performance benchmarks
make test-performance
```

### Frontend Testing
```bash
# Run all frontend tests
make test-frontend

# Unit tests (Vitest)
npm run test

# E2E tests (Playwright)
npm run test:e2e

# Test coverage
npm run test:coverage
```

### Development Workflow

The project follows **Canon TDD** methodology:

1. **Test List** - Create comprehensive test scenarios
2. **Write One Test** - Pick exactly one test and make it concrete
3. **Make It Pass** - Write minimal code to pass the test
4. **Refactor** - Improve design while maintaining tests
5. **Repeat** - Continue until feature complete

### Code Quality

```bash
# Lint and format
make lint                  # All components
make lint-backend         # Python (black, pylint)
make lint-frontend        # TypeScript (eslint, prettier)

# Type checking
make typecheck            # All components
make typecheck-backend    # Python (mypy)
make typecheck-frontend   # TypeScript (tsc)
```

## 📊 System Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph "Developer Machine"
        FS[File System<br/>~/.claude/projects/*.jsonl]
        FM[File Monitor<br/>Python watchdog]
    end
    
    subgraph "CCO Backend"
        API[FastAPI Server<br/>Port 8000]
        WS[WebSocket Server<br/>Real-time updates]
        JSONL[JSONL Parser<br/>Conversation processor]
        ANALYTICS[Analytics Engine<br/>Pattern analysis]
    end
    
    subgraph "Database Layer"
        SUPA[(Supabase<br/>PostgreSQL + Realtime)]
        CACHE[Redis Cache<br/>Optional]
    end
    
    subgraph "Frontend"
        SVELTE[SvelteKit App<br/>Port 5173]
        STORES[Svelte Stores<br/>State management]
        COMPONENTS[UI Components<br/>Tailwind + DaisyUI]
    end
    
    FS --> FM
    FM --> JSONL
    JSONL --> API
    API --> SUPA
    API --> WS
    WS --> SVELTE
    SUPA --> SVELTE
    SVELTE --> STORES
    STORES --> COMPONENTS
    ANALYTICS --> SUPA
    SUPA -.-> CACHE
```

### Data Flow Architecture

```mermaid
sequenceDiagram
    participant Claude as Claude Code
    participant FS as File System
    participant Monitor as File Monitor
    participant Parser as JSONL Parser
    participant API as FastAPI Backend
    participant DB as Supabase DB
    participant WS as WebSocket
    participant Frontend as SvelteKit Frontend
    
    Claude->>FS: Writes conversation.jsonl
    FS->>Monitor: File change event
    Monitor->>Parser: Parse JSONL content
    Parser->>API: Structured conversation data
    API->>DB: Store conversation + metadata
    DB->>API: Confirm storage
    API->>WS: Broadcast update event
    WS->>Frontend: Real-time conversation update
    Frontend->>Frontend: Update UI components
    
    Note over DB, Frontend: Supabase Realtime<br/>for live updates
```

### Component Interaction Map

```mermaid
graph LR
    subgraph "Monitoring Layer"
        FM[File Monitor<br/>watchdog]
        FH[File Handler<br/>JSONL processor]
        PM[Performance Monitor<br/>Metrics tracking]
    end
    
    subgraph "API Layer"
        CONV[Conversations API<br/>/api/conversations]
        PROJ[Projects API<br/>/api/projects]
        SEARCH[Search API<br/>/api/search]
        HEALTH[Health Check<br/>/health]
    end
    
    subgraph "WebSocket Layer"
        CONN[Connection Manager<br/>Client connections]
        HANDLER[Message Handler<br/>Event routing]
        BROADCAST[Broadcast Service<br/>Real-time updates]
    end
    
    subgraph "Frontend Components"
        DASHBOARD[Dashboard<br/>Main analytics view]
        CONVERSATION[Conversation Viewer<br/>Detailed view]
        SIDEBAR[Sidebar Navigation<br/>Project switching]
        HEADER[Header Component<br/>Navigation + theme]
    end
    
    FM --> FH
    FH --> CONV
    CONV --> CONN
    CONN --> HANDLER
    HANDLER --> BROADCAST
    BROADCAST --> DASHBOARD
    PROJ --> SIDEBAR
    SEARCH --> CONVERSATION
    PM --> HEALTH
```

### Database Schema Overview

```mermaid
erDiagram
    PROJECTS ||--o{ CONVERSATIONS : contains
    CONVERSATIONS ||--o{ MESSAGES : includes
    CONVERSATIONS ||--o{ TOOL_CALLS : uses
    MESSAGES ||--o{ TOOL_CALLS : triggers
    
    PROJECTS {
        uuid id PK
        string name
        string path
        timestamp created_at
        timestamp updated_at
        json metadata
    }
    
    CONVERSATIONS {
        uuid id PK
        uuid project_id FK
        string title
        timestamp started_at
        timestamp ended_at
        integer message_count
        integer tool_call_count
        json metadata
    }
    
    MESSAGES {
        uuid id PK
        uuid conversation_id FK
        string role
        text content
        timestamp created_at
        json metadata
    }
    
    TOOL_CALLS {
        uuid id PK
        uuid conversation_id FK
        uuid message_id FK
        string tool_name
        json parameters
        json result
        timestamp created_at
        float duration_ms
    }
```

### Development Workflow (TDD)

```mermaid
flowchart TD
    START([Start Feature Development]) --> TESTLIST[Create Test List<br/>Behavior scenarios]
    TESTLIST --> ONETEST[Write ONE Test<br/>Make it concrete]
    ONETEST --> RUN1[Run Test<br/>Watch it FAIL]
    RUN1 --> FAIL{Test Fails?}
    FAIL -->|Yes| IMPLEMENT[Write Minimal Code<br/>Make test pass]
    FAIL -->|No| ERROR[❌ Test should fail first!<br/>Fix the test]
    ERROR --> ONETEST
    IMPLEMENT --> RUN2[Run Test<br/>Watch it PASS]
    RUN2 --> PASS{Test Passes?}
    PASS -->|No| DEBUG[Debug Implementation<br/>Fix the code]
    DEBUG --> RUN2
    PASS -->|Yes| REFACTOR[Refactor Code<br/>Improve design]
    REFACTOR --> RUNALL[Run ALL Tests<br/>Ensure no regression]
    RUNALL --> ALLPASS{All Pass?}
    ALLPASS -->|No| FIXREGRESSION[Fix Regression<br/>Maintain all tests]
    FIXREGRESSION --> RUNALL
    ALLPASS -->|Yes| MORETESTS{More Tests<br/>in List?}
    MORETESTS -->|Yes| ONETEST
    MORETESTS -->|No| COMPLETE([Feature Complete!])
```

### Deployment Architecture

```mermaid
graph TB
    subgraph "Development"
        DEV[Local Development<br/>make dev]
        TEST[Testing Pipeline<br/>pytest + vitest]
    end
    
    subgraph "CI/CD Pipeline"
        GHA[GitHub Actions<br/>Automated testing]
        BUILD[Docker Build<br/>Multi-stage images]
        DEPLOY[Deploy to K8s<br/>Production ready]
    end
    
    subgraph "Production Environment"
        LB[Load Balancer<br/>Traffic distribution]
        BACKEND[Backend Pods<br/>FastAPI instances]
        FRONTEND[Frontend Pods<br/>SvelteKit static]
        DB[Supabase Cloud<br/>Managed PostgreSQL]
    end
    
    DEV --> TEST
    TEST --> GHA
    GHA --> BUILD
    BUILD --> DEPLOY
    DEPLOY --> LB
    LB --> BACKEND
    LB --> FRONTEND
    BACKEND --> DB
    FRONTEND --> DB
```

### Core Components

1. **File Monitor** - Python watchdog monitors `~/.claude/projects/**/*.jsonl`
2. **FastAPI Backend** - Processes JSONL files, stores in Supabase
3. **SvelteKit Frontend** - Real-time dashboard with Supabase Realtime
4. **Analytics Engine** - Conversation pattern analysis and insights

## 🚢 Deployment

### Production Deployment

```bash
# Build production images
make build

# Deploy to Kubernetes
make deploy-prod

# Or deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables

Key configuration variables:

```bash
# Backend (.env)
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_key
CLAUDE_PROJECTS_PATH=~/.claude/projects

# Frontend (.env)
PUBLIC_SUPABASE_URL=your_supabase_url
PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

## 📈 Performance Targets

- **File Detection Latency**: <100ms (95th percentile)
- **UI Response Time**: <200ms for user interactions
- **System Uptime**: 99.9% availability
- **WebSocket Updates**: <50ms latency
- **Concurrent Monitoring**: 1000+ files
- **Test Coverage**: 80-90% across all components

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch** following Canon TDD methodology
3. **Write tests first**, then implement features
4. **Ensure all tests pass** and coverage requirements are met
5. **Submit a pull request** with comprehensive description

### Development Setup

```bash
# Install dependencies
make install

# Setup development environment
make setup-dev

# Run development servers
make dev

# Run tests continuously during development
make test-watch
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Full documentation](./docs/README.md)
- **Issues**: [GitHub Issues](https://github.com/osbornesec/ccobservatory/issues)
- **Discussions**: [GitHub Discussions](https://github.com/osbornesec/ccobservatory/discussions)

---

<div align="center">

**Built with ❤️ for the Claude Code community**

[Documentation](./docs/README.md) • [Contributing](./CONTRIBUTING.md) • [Changelog](./CHANGELOG.md)

</div>