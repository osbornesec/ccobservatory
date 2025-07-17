-- Seed Data for Claude Code Observatory Development
-- This file provides sample data for development and testing

-- =============================================================================
-- SAMPLE USERS (for testing RLS policies)
-- =============================================================================

-- Note: These would typically be created through Supabase Auth
-- For testing purposes, we'll create sample data with user IDs

-- =============================================================================
-- SAMPLE PROJECTS
-- =============================================================================

INSERT INTO projects (id, name, path, description, settings, metadata) VALUES
(
    '550e8400-e29b-41d4-a716-446655440001',
    'Claude Code Observatory',
    '/home/user/dev/ccobservatory',
    'The main CCO project for observability platform development',
    '{"theme": "dark", "notifications": true, "auto_refresh": 30}',
    '{"owner_id": "user1", "created_by": "Developer 1", "tags": ["development", "observability"]}'
),
(
    '550e8400-e29b-41d4-a716-446655440002',
    'Personal Assistant Bot',
    '/home/user/dev/assistant-bot',
    'Personal AI assistant with Claude Code integration',
    '{"theme": "light", "notifications": false, "auto_refresh": 60}',
    '{"owner_id": "user1", "created_by": "Developer 1", "tags": ["ai", "personal"]}'
),
(
    '550e8400-e29b-41d4-a716-446655440003',
    'Data Analysis Pipeline',
    '/home/user/projects/data-pipeline',
    'Automated data processing and analysis system',
    '{"theme": "dark", "notifications": true, "auto_refresh": 15}',
    '{"owner_id": "user2", "created_by": "Data Scientist", "tags": ["data", "automation"]}'
),
(
    '550e8400-e29b-41d4-a716-446655440004',
    'Web Scraper Tools',
    '/home/user/tools/web-scraper',
    'Collection of web scraping utilities and Claude Code helpers',
    '{"theme": "light", "notifications": true, "auto_refresh": 45}',
    '{"owner_id": "user2", "created_by": "Developer 2", "tags": ["tools", "scraping"]}'
);

-- =============================================================================
-- SAMPLE CONVERSATIONS
-- =============================================================================

INSERT INTO conversations (id, project_id, file_path, title, session_id, metadata) VALUES
(
    '660e8400-e29b-41d4-a716-446655440001',
    '550e8400-e29b-41d4-a716-446655440001',
    '/home/user/.claude/projects/ccobservatory/conversation-20250116-001.jsonl',
    'Database Schema Design Session',
    'session-20250116-001',
    '{"session_type": "development", "estimated_duration": 120, "tools_used": ["database", "schema"]}'
),
(
    '660e8400-e29b-41d4-a716-446655440002',
    '550e8400-e29b-41d4-a716-446655440001',
    '/home/user/.claude/projects/ccobservatory/conversation-20250116-002.jsonl',
    'Frontend Component Development',
    'session-20250116-002',
    '{"session_type": "frontend", "estimated_duration": 90, "tools_used": ["svelte", "typescript"]}'
),
(
    '660e8400-e29b-41d4-a716-446655440003',
    '550e8400-e29b-41d4-a716-446655440002',
    '/home/user/.claude/projects/assistant-bot/conversation-20250115-001.jsonl',
    'Bot Response Optimization',
    'session-20250115-001',
    '{"session_type": "optimization", "estimated_duration": 60, "tools_used": ["nlp", "performance"]}'
),
(
    '660e8400-e29b-41d4-a716-446655440004',
    '550e8400-e29b-41d4-a716-446655440003',
    '/home/user/.claude/projects/data-pipeline/conversation-20250114-001.jsonl',
    'Data Processing Pipeline Setup',
    'session-20250114-001',
    '{"session_type": "setup", "estimated_duration": 180, "tools_used": ["python", "pandas", "sql"]}'
);

-- =============================================================================
-- SAMPLE MESSAGES
-- =============================================================================

-- Messages for Database Schema Design Session
INSERT INTO messages (id, conversation_id, role, content, timestamp, token_count, depth, metadata) VALUES
(
    '770e8400-e29b-41d4-a716-446655440001',
    '660e8400-e29b-41d4-a716-446655440001',
    'user',
    'I need to design a comprehensive database schema for the Claude Code Observatory. The system needs to store projects, conversations, messages, and tool usage data with proper relationships and performance optimization.',
    '2025-01-16 10:00:00+00',
    45,
    0,
    '{"message_type": "requirement", "priority": "high"}'
),
(
    '770e8400-e29b-41d4-a716-446655440002',
    '660e8400-e29b-41d4-a716-446655440001',
    'assistant',
    'I''ll help you design a comprehensive database schema for the Claude Code Observatory. Let me break this down into core tables with proper relationships, constraints, and performance optimizations.',
    '2025-01-16 10:01:00+00',
    38,
    0,
    '{"message_type": "response", "generated_schema": true}'
),
(
    '770e8400-e29b-41d4-a716-446655440003',
    '660e8400-e29b-41d4-a716-446655440001',
    'user',
    'Great! Please focus on PostgreSQL/Supabase specific features including Row Level Security, real-time subscriptions, and full-text search capabilities.',
    '2025-01-16 10:05:00+00',
    28,
    0,
    '{"message_type": "clarification", "database_type": "postgresql"}'
);

-- Messages for Frontend Component Development
INSERT INTO messages (id, conversation_id, role, content, timestamp, token_count, depth, metadata) VALUES
(
    '770e8400-e29b-41d4-a716-446655440004',
    '660e8400-e29b-41d4-a716-446655440002',
    'user',
    'I want to create a SvelteKit dashboard component that displays real-time conversation data from the Supabase backend. It should show active conversations, message counts, and tool usage statistics.',
    '2025-01-16 14:00:00+00',
    42,
    0,
    '{"message_type": "feature_request", "component_type": "dashboard"}'
),
(
    '770e8400-e29b-41d4-a716-446655440005',
    '660e8400-e29b-41d4-a716-446655440002',
    'assistant',
    'I''ll help you create a real-time SvelteKit dashboard component. Let''s build this with Supabase real-time subscriptions, Tailwind CSS for styling, and proper TypeScript types.',
    '2025-01-16 14:02:00+00',
    35,
    0,
    '{"message_type": "implementation_plan", "technologies": ["svelte", "supabase", "tailwind"]}'
);

-- Messages for Bot Response Optimization
INSERT INTO messages (id, conversation_id, role, content, timestamp, token_count, depth, metadata) VALUES
(
    '770e8400-e29b-41d4-a716-446655440006',
    '660e8400-e29b-41d4-a716-446655440003',
    'user',
    'The assistant bot is taking too long to respond to user queries. I need to optimize the response generation and implement caching for common queries.',
    '2025-01-15 16:30:00+00',
    32,
    0,
    '{"message_type": "performance_issue", "current_response_time": "3000ms"}'
),
(
    '770e8400-e29b-41d4-a716-446655440007',
    '660e8400-e29b-41d4-a716-446655440003',
    'assistant',
    'Let''s optimize your bot''s response time. I''ll help implement response caching, query optimization, and parallel processing for faster performance.',
    '2025-01-15 16:32:00+00',
    29,
    0,
    '{"message_type": "optimization_plan", "target_response_time": "500ms"}'
);

-- =============================================================================
-- SAMPLE TOOL CALLS
-- =============================================================================

INSERT INTO tool_calls (id, message_id, tool_name, input_data, output_data, execution_time_ms, status, metadata) VALUES
(
    '880e8400-e29b-41d4-a716-446655440001',
    '770e8400-e29b-41d4-a716-446655440002',
    'Read',
    '{"file_path": "/home/user/dev/ccobservatory/docs/database-architecture.md"}',
    'Successfully read database architecture documentation with 2000+ lines of content describing table relationships and performance requirements.',
    150,
    'success',
    '{"file_size": 15420, "read_lines": 2045}'
),
(
    '880e8400-e29b-41d4-a716-446655440002',
    '770e8400-e29b-41d4-a716-446655440002',
    'Write',
    '{"file_path": "/home/user/dev/ccobservatory/supabase/migrations/001_initial_schema.sql", "content": "-- Migration: 001_initial_schema.sql..."}',
    'Created initial database schema migration with core tables: projects, conversations, messages, tool_calls',
    280,
    'success',
    '{"file_size": 8940, "lines_written": 195}'
),
(
    '880e8400-e29b-41d4-a716-446655440003',
    '770e8400-e29b-41d4-a716-446655440005',
    'Bash',
    '{"command": "npm create svelte@latest dashboard --template skeleton --types typescript", "description": "Create SvelteKit project"}',
    'Successfully created SvelteKit project with TypeScript support and skeleton template',
    2100,
    'success',
    '{"exit_code": 0, "dependencies_installed": 45}'
),
(
    '880e8400-e29b-41d4-a716-446655440004',
    '770e8400-e29b-41d4-a716-446655440005',
    'Edit',
    '{"file_path": "/home/user/dev/ccobservatory/frontend/src/routes/+page.svelte", "old_string": "<h1>Welcome to SvelteKit</h1>", "new_string": "<h1>Claude Code Observatory Dashboard</h1>"}',
    'Updated main page title to reflect the CCO dashboard',
    95,
    'success',
    '{"changes": 1, "file_modified": true}'
),
(
    '880e8400-e29b-41d4-a716-446655440005',
    '770e8400-e29b-41d4-a716-446655440007',
    'Grep',
    '{"pattern": "response.*time", "path": "/home/user/dev/assistant-bot", "output_mode": "content"}',
    'Found 15 occurrences of response time related code across 8 files',
    220,
    'success',
    '{"matches": 15, "files": 8, "search_pattern": "response.*time"}'
),
(
    '880e8400-e29b-41d4-a716-446655440006',
    '770e8400-e29b-41d4-a716-446655440007',
    'MultiEdit',
    '{"file_path": "/home/user/dev/assistant-bot/src/cache.py", "edits": [{"old_string": "cache_ttl = 3600", "new_string": "cache_ttl = 300"}]}',
    'Reduced cache TTL from 1 hour to 5 minutes for faster cache invalidation',
    85,
    'success',
    '{"edits_applied": 1, "cache_optimization": true}'
);

-- =============================================================================
-- SAMPLE ANALYTICS DATA
-- =============================================================================

-- Update projects with activity timestamps
UPDATE projects SET last_activity = NOW() - INTERVAL '2 hours' WHERE name = 'Claude Code Observatory';
UPDATE projects SET last_activity = NOW() - INTERVAL '1 day' WHERE name = 'Personal Assistant Bot';
UPDATE projects SET last_activity = NOW() - INTERVAL '2 days' WHERE name = 'Data Analysis Pipeline';
UPDATE projects SET last_activity = NOW() - INTERVAL '1 week' WHERE name = 'Web Scraper Tools';

-- Update conversation statistics
UPDATE conversations SET 
    message_count = (SELECT COUNT(*) FROM messages WHERE conversation_id = conversations.id),
    last_updated = (SELECT MAX(timestamp) FROM messages WHERE conversation_id = conversations.id);

-- =============================================================================
-- SAMPLE SEARCH HISTORY (for testing search analytics)
-- =============================================================================

INSERT INTO search_history (user_id, query, search_type, result_count, execution_time_ms, filters) VALUES
('user1', 'database schema', 'message', 12, 45, '{"project_id": "550e8400-e29b-41d4-a716-446655440001"}'),
('user1', 'svelte component', 'message', 8, 32, '{"role": "assistant"}'),
('user1', 'performance optimization', 'message', 15, 67, '{}'),
('user2', 'data pipeline', 'conversation', 3, 28, '{"project_id": "550e8400-e29b-41d4-a716-446655440003"}'),
('user2', 'web scraping', 'tool', 5, 18, '{"tool_name": "Bash"}');

-- =============================================================================
-- REFRESH MATERIALIZED VIEWS
-- =============================================================================

-- Refresh materialized views with initial data
REFRESH MATERIALIZED VIEW project_summary_stats;
REFRESH MATERIALIZED VIEW tool_usage_trends;
REFRESH MATERIALIZED VIEW search_analytics;

-- =============================================================================
-- SAMPLE AUDIT LOG ENTRIES
-- =============================================================================

INSERT INTO audit_log (table_name, operation, user_id, user_role, record_id, new_values) VALUES
('projects', 'INSERT', 'user1', 'authenticated', '550e8400-e29b-41d4-a716-446655440001', '{"name": "Claude Code Observatory", "action": "project_created"}'),
('conversations', 'INSERT', 'user1', 'authenticated', '660e8400-e29b-41d4-a716-446655440001', '{"title": "Database Schema Design Session", "action": "conversation_started"}'),
('messages', 'INSERT', 'user1', 'authenticated', '770e8400-e29b-41d4-a716-446655440001', '{"role": "user", "action": "message_sent"}');

-- =============================================================================
-- COMMENTS
-- =============================================================================

COMMENT ON SCHEMA public IS 'Sample data for Claude Code Observatory development and testing';

-- Display summary of seeded data
DO $$
BEGIN
    RAISE NOTICE 'Seed data loaded successfully:';
    RAISE NOTICE '- Projects: %', (SELECT COUNT(*) FROM projects);
    RAISE NOTICE '- Conversations: %', (SELECT COUNT(*) FROM conversations);
    RAISE NOTICE '- Messages: %', (SELECT COUNT(*) FROM messages);
    RAISE NOTICE '- Tool Calls: %', (SELECT COUNT(*) FROM tool_calls);
    RAISE NOTICE '- Search History: %', (SELECT COUNT(*) FROM search_history);
    RAISE NOTICE '- Audit Log Entries: %', (SELECT COUNT(*) FROM audit_log);
END $$;