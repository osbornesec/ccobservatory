# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code Observatory (CCO) is an observability platform for Claude Code interactions that provides complete conversation visibility, real-time monitoring, and actionable insights for developers and teams. The system monitors `~/.claude/projects/` directory to parse JSONL transcript files and provide comprehensive analytics.

## Development Environment

This project is currently in the planning and documentation phase. No code implementation has been started yet.

### Technology Stack (Planned)
- **Runtime**: Bun (JavaScript/TypeScript runtime)
- **Backend**: Bun server with TypeScript, SQLite (WAL mode), WebSocket
- **Frontend**: Vue 3 + TypeScript + Tailwind CSS + Vite
- **File Monitoring**: Chokidar for real-time file system watching
- **Database**: SQLite with prepared statements and indexes
- **Testing**: Jest/Vitest, Playwright for E2E
- **Build/Deploy**: Docker, Kubernetes, GitHub Actions

### Project Structure (Planned)
```
claude-code-observatory/
├── packages/
│   ├── core/                    # Shared utilities and types
│   ├── file-monitor/           # File system monitoring
│   ├── backend/                # API server and data processing
│   ├── frontend/               # Vue.js dashboard
│   └── cli/                    # Command-line interface
├── apps/
│   ├── desktop/                # Electron desktop app
│   └── vscode-extension/       # VS Code integration
├── docs/                       # Documentation
├── tests/                      # Integration and E2E tests
└── scripts/                    # Build and deployment scripts
```

## Core System Architecture

### High-Level Flow
1. **File System Monitor** (Chokidar) watches `~/.claude/projects/**/*.jsonl`
2. **Observatory Backend** processes JSONL files and stores in SQLite
3. **Dashboard Frontend** displays real-time conversations via WebSocket
4. **Analytics Engine** provides insights on conversation patterns

### Key Technical Requirements
- File detection latency <100ms (95th percentile)
- UI response time <200ms for user interactions
- Support for 1000+ concurrent file monitoring
- Real-time WebSocket updates <50ms
- 99.9% system uptime

## Development Phases

### Phase 1: Foundation (Weeks 1-8)
- Monorepo setup with TypeScript and testing framework
- File system monitoring with Chokidar
- JSONL parsing and SQLite storage
- Basic Vue 3 dashboard with real-time updates
- End-to-end integration testing

### Phase 2: Enhanced Features (Weeks 9-16)
- AI-powered conversation analysis
- Advanced analytics dashboard
- Team collaboration features
- Performance optimization

### Phase 3: Enterprise & Scaling (Weeks 17-24)
- Enterprise security and compliance
- Integration ecosystem (VS Code, GitHub, Slack)
- Production deployment capabilities

## Common Development Commands

*Note: These commands are planned but not yet implemented*

```bash
# Development
npm run dev:all          # Start all services concurrently
npm run dev:backend      # Start backend with hot reload
npm run dev:frontend     # Start frontend dev server

# Testing
npm run test:unit        # Run unit tests for all packages
npm run test:integration # Run integration tests
npm run test:e2e        # Run end-to-end tests
npm run test:performance # Run performance benchmarks

# Build
npm run build:production # Build optimized production bundles
npm run package:desktop  # Package Electron desktop app
npm run package:extension # Package VS Code extension
```

## Key Features

### File System Monitoring
- Real-time detection of JSONL file changes
- Incremental reading for performance
- Cross-platform compatibility (Windows, macOS, Linux)
- Graceful error recovery

### Data Processing
- Parse Claude Code JSONL message format
- Extract tool usage and conversation threading
- Store normalized data in SQLite
- Real-time WebSocket broadcasting

### Dashboard Features
- Live conversation viewing
- Project auto-discovery and switching
- Search across all conversations
- Analytics with charts and insights
- Team collaboration (planned)

## Success Criteria

### Technical Goals
- <100ms file detection latency
- 99.9% system uptime
- Support for 10,000+ conversations
- Real-time updates with <50ms latency

### User Experience Goals
- Zero-configuration setup
- >90% user satisfaction rating
- <5 minutes time to first value
- >80% feature adoption rate

## Documentation Structure

The `/docs` directory contains comprehensive planning documents:
- `01-project-charter.md` - Executive summary and project goals
- `02-technical-architecture.md` - System design and architecture
- `03-feature-specifications.md` - Detailed feature requirements
- `07-implementation-roadmap.md` - Development phases and timeline

The `/ai_docs` directory contains AI-specific planning and task management documentation.

## Security & Privacy

- Local-first architecture (no cloud dependencies required)
- Optional AES-256 encryption for sensitive projects
- User-controlled data access and retention
- File system permissions validation
- Privacy controls for data anonymization