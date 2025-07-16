# API Foundation Endpoints Feature

## Goal
Implement basic API endpoints for conversations and projects with WebSocket real-time foundation to achieve +4 points toward Week 1 completion (93% → 97%).

## Architecture Decisions

### FastAPI Patterns
- Use `APIRouter` with prefix `/api` for organization
- Follow existing dependency injection patterns from `main.py`
- Use `get_supabase_service_client()` for database operations
- Implement `APIResponse[T]` wrapper for consistent responses
- Follow existing error handling with `ProcessingError`

### Database Integration
- Leverage existing `supabase_client.py` infrastructure
- Use existing data models from `models/contracts.py`
- Follow patterns from `DatabaseWriter` for operations
- Implement proper error handling and retry logic

### WebSocket Architecture
- Create `ConnectionManager` class for WebSocket lifecycle
- Integrate with file monitoring for real-time updates
- Use JSON message format for structured communication
- Handle connection management (connect/disconnect/broadcast)

## Implementation Scope
1. **API Endpoints** (2 points):
   - `GET /api/conversations` - List all conversations
   - `GET /api/conversations/{id}` - Get conversation with messages
   - `GET /api/projects` - List all projects
   - `GET /api/projects/{id}` - Get project details

2. **WebSocket Foundation** (2 points):
   - Basic connection management
   - Real-time conversation updates
   - Integration with file monitoring system
   - Message broadcasting to connected clients

## Quality Requirements
- Follow Canon TDD with comprehensive test scenarios
- Maintain 85% backend test coverage
- Use existing Pydantic models for type safety
- Implement proper error handling and validation
- Performance targets: <200ms API response time

## Integration Points
- Existing `main.py` FastAPI application
- Existing `supabase_client.py` database layer
- Existing `models/contracts.py` data models
- File monitoring system for real-time updates