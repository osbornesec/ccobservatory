-- Migration: 001_initial_schema.sql
-- Description: Core database schema for Claude Code Observatory
-- Created: 2025-01-16
-- Dependencies: None

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- =============================================================================
-- CORE TABLES
-- =============================================================================

-- Projects table: Root entity for organizing Claude Code projects
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    path TEXT NOT NULL UNIQUE,
    description TEXT,
    settings JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    
    -- Constraints
    CONSTRAINT projects_name_not_empty CHECK (char_length(name) > 0),
    CONSTRAINT projects_path_not_empty CHECK (char_length(path) > 0),
    CONSTRAINT projects_name_length CHECK (char_length(name) <= 255),
    CONSTRAINT projects_description_length CHECK (char_length(description) <= 2000),
    CONSTRAINT projects_updated_after_created CHECK (updated_at >= created_at)
);

-- Conversations table: Groups related messages in a Claude Code session
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL UNIQUE,
    title TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    message_count INTEGER DEFAULT 0,
    session_id TEXT,
    status TEXT DEFAULT 'active',
    metadata JSONB DEFAULT '{}',
    
    -- Constraints  
    CONSTRAINT conversations_file_path_not_empty CHECK (char_length(file_path) > 0),
    CONSTRAINT conversations_message_count_positive CHECK (message_count >= 0),
    CONSTRAINT conversations_status_valid CHECK (status IN ('active', 'completed', 'archived')),
    CONSTRAINT conversations_title_length CHECK (char_length(title) <= 500),
    CONSTRAINT conversations_last_updated_after_created CHECK (last_updated >= created_at)
);

-- Messages table: Individual conversation messages
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    token_count INTEGER DEFAULT 0,
    parent_id UUID REFERENCES messages(id) ON DELETE SET NULL,
    depth INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT messages_role_valid CHECK (role IN ('user', 'assistant', 'system')),
    CONSTRAINT messages_content_not_empty CHECK (char_length(content) > 0),
    CONSTRAINT messages_token_count_positive CHECK (token_count >= 0),
    CONSTRAINT messages_depth_positive CHECK (depth >= 0),
    CONSTRAINT messages_content_length CHECK (char_length(content) <= 1000000) -- 1MB limit
);

-- Tool calls table: Track tool usage and execution details
CREATE TABLE IF NOT EXISTS tool_calls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    tool_name TEXT NOT NULL,
    input_data JSONB,
    output_data TEXT,
    execution_time_ms INTEGER,
    status TEXT DEFAULT 'pending',
    error_message TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    
    -- Constraints
    CONSTRAINT tool_calls_tool_name_not_empty CHECK (char_length(tool_name) > 0),
    CONSTRAINT tool_calls_execution_time_positive CHECK (execution_time_ms IS NULL OR execution_time_ms >= 0),
    CONSTRAINT tool_calls_status_valid CHECK (status IN ('pending', 'running', 'success', 'error', 'timeout')),
    CONSTRAINT tool_calls_completed_after_started CHECK (completed_at IS NULL OR completed_at >= started_at)
);

-- =============================================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for projects table
CREATE TRIGGER update_projects_updated_at 
    BEFORE UPDATE ON projects 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for conversations table  
CREATE TRIGGER update_conversations_updated_at 
    BEFORE UPDATE ON conversations 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Function to update conversation message count and last_updated
CREATE OR REPLACE FUNCTION update_conversation_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Update message count and last_updated for the conversation
    UPDATE conversations 
    SET 
        message_count = (
            SELECT COUNT(*) 
            FROM messages 
            WHERE conversation_id = COALESCE(NEW.conversation_id, OLD.conversation_id)
        ),
        last_updated = NOW()
    WHERE id = COALESCE(NEW.conversation_id, OLD.conversation_id);
    
    -- Update project last_activity
    UPDATE projects 
    SET last_activity = NOW()
    WHERE id = (
        SELECT project_id 
        FROM conversations 
        WHERE id = COALESCE(NEW.conversation_id, OLD.conversation_id)
    );
    
    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

-- Triggers for message statistics
CREATE TRIGGER update_conversation_stats_on_insert
    AFTER INSERT ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_stats();

CREATE TRIGGER update_conversation_stats_on_delete
    AFTER DELETE ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_stats();

-- =============================================================================
-- COMMENTS FOR DOCUMENTATION
-- =============================================================================

COMMENT ON TABLE projects IS 'Root entity for organizing Claude Code projects and their conversations';
COMMENT ON COLUMN projects.name IS 'Human-readable project name, must be unique';
COMMENT ON COLUMN projects.path IS 'File system path to the project directory, must be unique';
COMMENT ON COLUMN projects.settings IS 'Project-specific configuration and preferences';
COMMENT ON COLUMN projects.metadata IS 'Extensible metadata for additional project information';
COMMENT ON COLUMN projects.last_activity IS 'Timestamp of most recent activity in this project';

COMMENT ON TABLE conversations IS 'Groups related messages from a single Claude Code session';
COMMENT ON COLUMN conversations.file_path IS 'Absolute path to the JSONL conversation file';
COMMENT ON COLUMN conversations.title IS 'Auto-generated or user-provided conversation title';
COMMENT ON COLUMN conversations.message_count IS 'Cached count of messages in this conversation';
COMMENT ON COLUMN conversations.session_id IS 'Claude Code session identifier';

COMMENT ON TABLE messages IS 'Individual messages within a conversation';
COMMENT ON COLUMN messages.role IS 'Message sender: user, assistant, or system';
COMMENT ON COLUMN messages.content IS 'Full message content text';
COMMENT ON COLUMN messages.token_count IS 'Number of tokens in the message';
COMMENT ON COLUMN messages.parent_id IS 'Reference to parent message for threading';
COMMENT ON COLUMN messages.depth IS 'Threading depth level (0 for root messages)';

COMMENT ON TABLE tool_calls IS 'Track tool usage and execution details within messages';
COMMENT ON COLUMN tool_calls.tool_name IS 'Name of the tool that was executed';
COMMENT ON COLUMN tool_calls.input_data IS 'Parameters passed to the tool';
COMMENT ON COLUMN tool_calls.output_data IS 'Result returned by the tool';
COMMENT ON COLUMN tool_calls.execution_time_ms IS 'Tool execution duration in milliseconds';
COMMENT ON COLUMN tool_calls.status IS 'Execution status: pending, running, success, error, timeout';