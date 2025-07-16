-- Migration: 002_performance_indexes.sql
-- Description: Performance indexes for optimized query patterns
-- Created: 2025-01-16
-- Dependencies: 001_initial_schema.sql

-- =============================================================================
-- PRIMARY PERFORMANCE INDEXES
-- =============================================================================

-- Projects table indexes
CREATE INDEX IF NOT EXISTS idx_projects_active_activity 
    ON projects(is_active, last_activity DESC NULLS LAST)
    WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_projects_name_trgm 
    ON projects USING gin(name gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_projects_path_hash 
    ON projects USING hash(path);

-- Conversations table indexes
CREATE INDEX IF NOT EXISTS idx_conversations_project_updated 
    ON conversations(project_id, last_updated DESC);

CREATE INDEX IF NOT EXISTS idx_conversations_project_status 
    ON conversations(project_id, status) 
    WHERE status = 'active';

CREATE INDEX IF NOT EXISTS idx_conversations_file_path_hash 
    ON conversations USING hash(file_path);

CREATE INDEX IF NOT EXISTS idx_conversations_session_id 
    ON conversations(session_id) 
    WHERE session_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_conversations_created_desc 
    ON conversations(created_at DESC);

-- Messages table indexes  
CREATE INDEX IF NOT EXISTS idx_messages_conversation_timestamp 
    ON messages(conversation_id, timestamp ASC);

CREATE INDEX IF NOT EXISTS idx_messages_timestamp_desc 
    ON messages(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_messages_role_conversation 
    ON messages(role, conversation_id);

CREATE INDEX IF NOT EXISTS idx_messages_parent_depth 
    ON messages(parent_id, depth) 
    WHERE parent_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_messages_created_desc 
    ON messages(created_at DESC);

-- Partial index for root messages (no parent)
CREATE INDEX IF NOT EXISTS idx_messages_root_messages 
    ON messages(conversation_id, timestamp ASC) 
    WHERE parent_id IS NULL;

-- Tool calls table indexes
CREATE INDEX IF NOT EXISTS idx_tool_calls_message_started 
    ON tool_calls(message_id, started_at DESC);

CREATE INDEX IF NOT EXISTS idx_tool_calls_tool_name_status 
    ON tool_calls(tool_name, status);

CREATE INDEX IF NOT EXISTS idx_tool_calls_status_started 
    ON tool_calls(status, started_at DESC) 
    WHERE status IN ('running', 'pending');

CREATE INDEX IF NOT EXISTS idx_tool_calls_execution_time 
    ON tool_calls(execution_time_ms DESC NULLS LAST) 
    WHERE execution_time_ms IS NOT NULL;

-- Performance monitoring index
CREATE INDEX IF NOT EXISTS idx_tool_calls_performance 
    ON tool_calls(tool_name, execution_time_ms DESC, started_at DESC) 
    WHERE status = 'success' AND execution_time_ms IS NOT NULL;

-- =============================================================================
-- COMPOSITE INDEXES FOR COMMON QUERY PATTERNS
-- =============================================================================

-- Project dashboard queries (recent conversations)
CREATE INDEX IF NOT EXISTS idx_project_dashboard 
    ON conversations(project_id, status, last_updated DESC) 
    WHERE status = 'active';

-- Message threading queries
CREATE INDEX IF NOT EXISTS idx_message_threading 
    ON messages(conversation_id, parent_id, depth, timestamp ASC);

-- Tool usage analytics
CREATE INDEX IF NOT EXISTS idx_tool_analytics 
    ON tool_calls(tool_name, status, started_at DESC, execution_time_ms);

-- Conversation search and filtering
CREATE INDEX IF NOT EXISTS idx_conversation_search 
    ON conversations(project_id, created_at DESC, message_count DESC);

-- =============================================================================
-- GIN INDEXES FOR JSONB FIELDS
-- =============================================================================

-- Index for project settings and metadata
CREATE INDEX IF NOT EXISTS idx_projects_settings_gin 
    ON projects USING gin(settings);

CREATE INDEX IF NOT EXISTS idx_projects_metadata_gin 
    ON projects USING gin(metadata);

-- Index for conversation metadata
CREATE INDEX IF NOT EXISTS idx_conversations_metadata_gin 
    ON conversations USING gin(metadata);

-- Index for message metadata
CREATE INDEX IF NOT EXISTS idx_messages_metadata_gin 
    ON messages USING gin(metadata);

-- Index for tool call input/output data
CREATE INDEX IF NOT EXISTS idx_tool_calls_input_gin 
    ON tool_calls USING gin(input_data);

CREATE INDEX IF NOT EXISTS idx_tool_calls_metadata_gin 
    ON tool_calls USING gin(metadata);

-- =============================================================================
-- FULL-TEXT SEARCH INDEXES
-- =============================================================================

-- Full-text search index for message content
CREATE INDEX IF NOT EXISTS idx_messages_content_fts 
    ON messages USING gin(to_tsvector('english', content));

-- Full-text search index for conversation titles
CREATE INDEX IF NOT EXISTS idx_conversations_title_fts 
    ON conversations USING gin(to_tsvector('english', title)) 
    WHERE title IS NOT NULL;

-- Full-text search index for project names and descriptions
CREATE INDEX IF NOT EXISTS idx_projects_text_search 
    ON projects USING gin(
        to_tsvector('english', 
            coalesce(name, '') || ' ' || 
            coalesce(description, '')
        )
    );

-- Combined search index for messages and metadata
CREATE INDEX IF NOT EXISTS idx_messages_combined_search 
    ON messages USING gin(
        to_tsvector('english', 
            content || ' ' || 
            coalesce(metadata->>'summary', '') || ' ' ||
            coalesce(metadata->>'tags', '')
        )
    );

-- =============================================================================
-- SPECIALIZED PERFORMANCE INDEXES
-- =============================================================================

-- Index for large conversation identification
CREATE INDEX IF NOT EXISTS idx_conversations_large 
    ON conversations(message_count DESC, project_id) 
    WHERE message_count > 100;

-- Index for recent tool usage
CREATE INDEX IF NOT EXISTS idx_recent_tool_usage 
    ON tool_calls(started_at DESC, tool_name) 
    WHERE started_at >= (NOW() - interval '7 days');

-- Index for error tracking
CREATE INDEX IF NOT EXISTS idx_tool_errors 
    ON tool_calls(tool_name, started_at DESC) 
    WHERE status = 'error';

-- Index for performance monitoring
CREATE INDEX IF NOT EXISTS idx_slow_tools 
    ON tool_calls(tool_name, execution_time_ms DESC) 
    WHERE execution_time_ms > 1000; -- Tools taking more than 1 second

-- =============================================================================
-- UNIQUE INDEXES FOR DATA INTEGRITY
-- =============================================================================

-- Ensure conversation file paths are unique across all projects
-- (already handled by unique constraint, but adding for performance)
CREATE UNIQUE INDEX IF NOT EXISTS idx_conversations_file_path_unique 
    ON conversations(file_path);

-- Ensure project names are unique (case-insensitive)
CREATE UNIQUE INDEX IF NOT EXISTS idx_projects_name_unique_lower 
    ON projects(lower(name));

-- Ensure project paths are unique (normalized)
CREATE UNIQUE INDEX IF NOT EXISTS idx_projects_path_unique_normalized 
    ON projects(trim(both '/' from path));

-- =============================================================================
-- COMMENTS FOR INDEX DOCUMENTATION
-- =============================================================================

COMMENT ON INDEX idx_conversations_project_updated IS 'Optimizes project dashboard queries showing recent conversations';
COMMENT ON INDEX idx_messages_conversation_timestamp IS 'Optimizes message retrieval in chronological order';
COMMENT ON INDEX idx_tool_calls_tool_name_status IS 'Optimizes tool usage analytics and status filtering';
COMMENT ON INDEX idx_messages_content_fts IS 'Enables full-text search across message content';
COMMENT ON INDEX idx_projects_settings_gin IS 'Enables efficient queries on project configuration';

-- =============================================================================
-- INDEX USAGE MONITORING
-- =============================================================================

-- Create a view to monitor index usage statistics
CREATE OR REPLACE VIEW index_usage_stats AS
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes 
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

COMMENT ON VIEW index_usage_stats IS 'Monitor index usage patterns for performance optimization';