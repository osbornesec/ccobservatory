# Manual Database Setup for Claude Code Observatory

## Current Status

The Supabase integration tests have revealed that:

✅ **Connection to Supabase cloud project is working**
- URL: `https://znznsjgqbnljgpffalwi.supabase.co`
- Authentication: Working with both anon and service role keys
- Client creation: Successful

❌ **Database schema is not yet created**
- Tables (`projects`, `conversations`, `messages`, `tool_calls`) do not exist
- The `exec_sql` function is not available for automated migrations

## Required Manual Steps

### 1. Access the Supabase SQL Editor

1. Go to: https://app.supabase.com/project/znznsjgqbnljgpffalwi/sql
2. Login with your Supabase credentials

### 2. Execute the Database Schema

Copy and paste the following SQL into the SQL Editor and execute it:

```sql
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
    message_id TEXT NOT NULL,
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
    CONSTRAINT messages_content_length CHECK (char_length(content) <= 1000000),
    CONSTRAINT messages_unique_per_conversation UNIQUE (conversation_id, message_id)
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
DROP TRIGGER IF EXISTS update_projects_updated_at ON projects;
CREATE TRIGGER update_projects_updated_at 
    BEFORE UPDATE ON projects 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for conversations table  
DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations;
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
DROP TRIGGER IF EXISTS update_conversation_stats_on_insert ON messages;
CREATE TRIGGER update_conversation_stats_on_insert
    AFTER INSERT ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_stats();

DROP TRIGGER IF EXISTS update_conversation_stats_on_delete ON messages;
CREATE TRIGGER update_conversation_stats_on_delete
    AFTER DELETE ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_stats();

-- =============================================================================
-- TEST DATA
-- =============================================================================

-- Insert a test project
INSERT INTO projects (name, path, description) 
VALUES ('Test Project', '/test/path', 'Test project for integration validation')
ON CONFLICT (name) DO NOTHING;

-- Insert a test conversation
INSERT INTO conversations (project_id, file_path, title, session_id)
SELECT 
    id,
    '/test/path/conversation.jsonl',
    'Test Conversation',
    'test-session-123'
FROM projects 
WHERE name = 'Test Project'
ON CONFLICT (file_path) DO NOTHING;

-- Insert a test message
INSERT INTO messages (conversation_id, message_id, role, content, timestamp)
SELECT 
    c.id,
    'test-msg-1',
    'user',
    'This is a test message',
    NOW()
FROM conversations c
JOIN projects p ON c.project_id = p.id
WHERE p.name = 'Test Project'
ON CONFLICT (conversation_id, message_id) DO NOTHING;
```

### 3. Verify the Setup

After executing the SQL, run the integration test to verify everything is working:

```bash
cd /home/michael/dev/ccobservatory/backend
source venv/bin/activate
python test_integration_live.py
```

### 4. Expected Results

After successful setup, you should see:

```
🎉 ALL TESTS PASSED! Supabase integration is working correctly.
```

## Alternative: Create exec_sql Function

If you prefer automated migrations in the future, you can create the `exec_sql` function:

```sql
-- Create the exec_sql function for automated migrations
CREATE OR REPLACE FUNCTION exec_sql(sql_query text)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    EXECUTE sql_query;
    RETURN 'executed';
END;
$$;

-- Grant permissions to the service role
GRANT EXECUTE ON FUNCTION exec_sql(text) TO service_role;
```

## Files Created During Testing

The following test files were created and can be removed after verification:

- `test_integration_live.py` - Live integration test
- `test_direct_db.py` - Direct database test  
- `test_supabase_functions.py` - Function availability test
- `create_exec_sql_function.py` - Function creation script
- `run_migrations.py` - Migration runner
- `test_exec_sql_result.py` - Function result tester
- `create_tables_directly.py` - Direct table creation
- `MANUAL_DB_SETUP.md` - This file

## Next Steps

1. Execute the manual SQL setup above
2. Run the integration test to verify
3. Proceed with backend and frontend development
4. Set up automated deployment and migration processes

## Environment Configuration

Current environment is properly configured with:
- ✅ SUPABASE_URL: `https://znznsjgqbnljgpffalwi.supabase.co`
- ✅ SUPABASE_KEY: Anon key configured
- ✅ SUPABASE_SERVICE_ROLE_KEY: Service role key configured
- ✅ Database connection: Working
- ✅ Python dependencies: Installed
- ✅ Test framework: Ready