# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code Observatory (CCO) is an observability platform for Claude Code interactions that provides complete conversation visibility, real-time monitoring, and actionable insights for developers and teams. The system monitors `~/.claude/projects/` directory to parse JSONL transcript files and provide comprehensive analytics.

## Development Environment

This project is now in active development phase. The comprehensive planning and documentation phase has been completed, and implementation is underway.

### Technology Stack
- **Backend**: Python (high-performance interpreted language with a rich ecosystem)
- **Database**: Supabase (managed PostgreSQL with real-time subscriptions and built-in auth)
- **Frontend**: SvelteKit + Tailwind CSS + Vite
- **File Monitoring**: Python watchdog for cross-platform file system watching
- **Real-time**: WebSocket + Supabase Realtime for live updates
- **Authentication**: Supabase Auth with JWT tokens
- **Testing**: Pytest, Vitest for frontend, Playwright for E2E
- **Build/Deploy**: Docker, Kubernetes, GitHub Actions

### Development Methodology

This project follows **TDD** approach for all development work. The methodology is enforced through the `/tdd` command and emphasizes quality, discipline, and incremental development.

#### Canon TDD Workflow
1. **Test List** - Create comprehensive test scenarios focusing on behavior (not implementation)
2. **Write One Test** - Pick exactly one test from the list and make it concrete and executable
3. **Make It Pass** - Write minimal code to make the test pass honestly (no cheating)
4. **Refactor** - Improve design while maintaining all passing tests
5. **Repeat** - Continue until test list is complete

#### Key Principles
- **Quality is Not Optional**: Take responsibility for robust, well-designed software
- **One Test at a Time**: Never write multiple tests simultaneously
- **Honest Implementation**: Make tests pass through real code, not fake results
- **Behavior-Focused**: Test scenarios describe WHAT the system should do, not HOW
- **Disciplined Refactoring**: Only refactor when all tests pass

#### Testing Framework
- **Backend**: pytest with comprehensive coverage requirements (80-90%)
- **Frontend**: Vitest with SvelteKit testing utilities
- **Integration**: Supabase + Python integration tests
- **End-to-End**: Playwright for full system testing
- **Performance**: Custom benchmarks for file detection latency (<100ms)

### Project Structure
```
claude-code-observatory/
├── backend/                    # Python backend service
│   ├── app/                    # Main application folder
│   │   ├── __init__.py         # Application package
│   │   ├── main.py             # Main application entrypoint
│   │   ├── api/                # HTTP API handlers
│   │   ├── websocket/          # WebSocket server
│   │   ├── database/           # Database layer
│   │   ├── monitoring/         # File system monitoring
│   │   ├── analytics/          # Conversation analysis
│   │   └── auth/               # Authentication middleware
│   ├── tests/                  # Backend tests
│   ├── requirements.txt        # Python dependencies
│   └── venv/                   # Virtual environment
├── frontend/                  # SvelteKit dashboard
│   ├── src/                   # Source code
│   │   ├── routes/            # SvelteKit file-based routing
│   │   ├── lib/               # Shared components and utilities
│   │   ├── stores/            # Svelte stores for state management
│   │   └── app.html           # HTML template
│   ├── static/                # Static assets
│   ├── package.json           # Node.js dependencies
│   └── svelte.config.js       # SvelteKit configuration
├── supabase/                  # Supabase configuration
│   ├── migrations/            # Database migrations
│   ├── seed.sql              # Database seed data
│   └── config.toml           # Supabase configuration
├── apps/
│   ├── desktop/              # Electron desktop app
│   └── vscode-extension/     # VS Code integration
├── docs/                     # Documentation
├── tests/                    # Integration and E2E tests
└── scripts/                  # Build and deployment scripts
```

## Core System Architecture

### High-Level Flow
1. **File System Monitor** (Python watchdog) watches `~/.claude/projects/**/*.jsonl`
2. **Python Backend** processes JSONL files and stores in Supabase (PostgreSQL)
3. **SvelteKit Frontend** displays real-time conversations via WebSocket + Supabase Realtime
4. **Analytics Engine** provides insights on conversation patterns

### Key Technical Requirements
- File detection latency <100ms (95th percentile)
- UI response time <200ms for user interactions
- Support for 1000+ concurrent file monitoring
- Real-time WebSocket updates <50ms
- 99.9% system uptime

## Development Phases

### Phase 1: Foundation (Weeks 1-8)
- Python backend setup with module structure and Canon TDD testing framework
- File system monitoring with Python watchdog (TDD-driven implementation)
- JSONL parsing and Supabase storage (comprehensive test coverage)
- Basic SvelteKit dashboard with real-time updates
- End-to-end integration testing with performance benchmarks

### Phase 2: Enhanced Features (Weeks 9-16)
- AI-powered conversation analysis
- Advanced analytics dashboard
- Team collaboration features with Supabase Auth
- Performance optimization

### Phase 3: Enterprise & Scaling (Weeks 17-24)
- Enterprise security and compliance
- Integration ecosystem (VS Code, GitHub, Slack)
- Production deployment capabilities

## Common Development Commands

```bash
# Development
make dev                 # Start all services concurrently
make dev-backend         # Start Python backend with hot reload
make dev-frontend        # Start SvelteKit dev server
make dev-supabase        # Start local Supabase instance

# Testing (Canon TDD)
make test                # Run tests for all components
make test-backend        # Run Python backend tests (pytest)
make test-frontend       # Run SvelteKit frontend tests (Vitest)
make test-integration    # Run integration tests
make test-e2e           # Run end-to-end tests (Playwright)
make test-performance    # Run performance benchmarks
make test-watch          # Continuous testing during TDD cycles
make test-coverage       # Generate coverage reports

# Build
make build               # Build all components
make build-backend       # Build Python backend distribution
make build-frontend      # Build SvelteKit frontend
make build-docker        # Build Docker images
make package-desktop     # Package Electron desktop app
make package-extension   # Package VS Code extension

# Database
make db-reset            # Reset Supabase database
make db-migrate          # Run database migrations
make db-seed             # Seed database with test data

# TDD Development Workflow
/tdd                     # Activate Canon TDD development mode
                         # - Enforces Test List → Write One Test → Make It Pass → Refactor cycle
                         # - Creates feature branches and notes automatically
                         # - Validates test discipline and quality gates
```

## Key Features

### File System Monitoring
- Real-time detection of JSONL file changes with Python watchdog
- Incremental reading for performance
- Cross-platform compatibility (Windows, macOS, Linux)
- Graceful error recovery

### Data Processing
- Parse Claude Code JSONL message format with Python
- Extract tool usage and conversation threading
- Store normalized data in Supabase (PostgreSQL)
- Real-time WebSocket broadcasting + Supabase Realtime

### Dashboard Features
- Live conversation viewing with SvelteKit
- Project auto-discovery and switching
- Search across all conversations with PostgreSQL full-text search
- Analytics with charts and insights
- Team collaboration with Supabase Auth

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

The `/notes/features/` directory contains TDD development notes:
- `[FeatureName]/README.md` - Feature overview and design decisions
- `[FeatureName]/tests/test-scenarios.md` - Comprehensive test lists for Canon TDD cycles
- Progress tracking and implementation notes for each feature branch

## Security & Privacy

- Local-first architecture (no cloud dependencies required)
- Optional AES-256 encryption for sensitive projects
- User-controlled data access and retention
- File system permissions validation
- Privacy controls for data anonymization

## Lessons Learned

### Canon TDD Discipline Violations (Week 1 Development)

**Critical Issue**: During Week 1 component testing implementation, I violated core Canon TDD principles by:

1. **Writing Multiple Tests at Once**: Created comprehensive test files with 20-40 tests instead of writing exactly ONE test at a time
2. **Skipping the TDD Cycle**: Never ran individual tests through the "Write One Test → Make It Pass → Refactor" cycle
3. **Creating Full Test Suites Upfront**: Built entire test files instead of incrementally developing tests and implementation together

**Why This Matters**: 
- Canon TDD's power comes from the disciplined cycle that forces focus on each behavior individually
- Writing multiple tests at once leads to over-engineering and loss of immediate feedback
- The incremental design evolution is lost when skipping the proper cycle
- Prevents the natural emergence of minimal, well-designed implementations

**Correct Canon TDD Process**:
1. Pick ONE specific test scenario (e.g., "Header displays application title")
2. Write ONLY that test
3. Run it and watch it fail
4. Write minimal code to make it pass
5. Refactor if needed while maintaining all passing tests
6. Then move to the next single test

**Key Reminder**: Even when using parallel subagents for efficiency, each agent must follow the Canon TDD cycle of one test at a time, not create comprehensive test suites upfront.

**Impact**: This violation led to creating test files that couldn't run due to configuration issues, and missing the iterative design benefits that Canon TDD provides.