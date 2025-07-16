-- Migration: 003_security_policies.sql
-- Description: Row Level Security (RLS) policies for data protection
-- Created: 2025-01-16
-- Dependencies: 002_performance_indexes.sql

-- =============================================================================
-- ENABLE ROW LEVEL SECURITY
-- =============================================================================

-- Enable RLS on all tables
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE tool_calls ENABLE ROW LEVEL SECURITY;

-- =============================================================================
-- AUTHENTICATION HELPER FUNCTIONS
-- =============================================================================

-- Function to get current user ID from JWT token
CREATE OR REPLACE FUNCTION auth.user_id() 
RETURNS UUID 
LANGUAGE SQL STABLE
AS $$
    SELECT COALESCE(
        auth.uid(),
        (current_setting('request.jwt.claims', true)::json ->> 'sub')::uuid
    );
$$;

-- Function to check if user is authenticated
CREATE OR REPLACE FUNCTION auth.is_authenticated() 
RETURNS BOOLEAN 
LANGUAGE SQL STABLE
AS $$
    SELECT auth.user_id() IS NOT NULL;
$$;

-- Function to get user role from JWT token
CREATE OR REPLACE FUNCTION auth.user_role() 
RETURNS TEXT 
LANGUAGE SQL STABLE
AS $$
    SELECT COALESCE(
        auth.role(),
        current_setting('request.jwt.claims', true)::json ->> 'role'
    );
$$;

-- =============================================================================
-- PROJECTS TABLE POLICIES
-- =============================================================================

-- Policy for viewing projects
-- Users can only see projects they own or have been granted access to
CREATE POLICY "Users can view their own projects" ON projects
    FOR SELECT 
    USING (
        auth.is_authenticated() AND (
            -- Project owner check (stored in metadata)
            metadata->>'owner_id' = auth.user_id()::text OR
            -- Shared project check (stored in metadata)
            metadata->'shared_users' ? auth.user_id()::text OR
            -- Admin role can see all projects
            auth.user_role() = 'admin'
        )
    );

-- Policy for creating projects
-- Authenticated users can create projects
CREATE POLICY "Authenticated users can create projects" ON projects
    FOR INSERT 
    WITH CHECK (
        auth.is_authenticated() AND
        -- Ensure the creator is set as owner
        metadata->>'owner_id' = auth.user_id()::text
    );

-- Policy for updating projects
-- Users can update projects they own
CREATE POLICY "Users can update their own projects" ON projects
    FOR UPDATE 
    USING (
        auth.is_authenticated() AND (
            metadata->>'owner_id' = auth.user_id()::text OR
            auth.user_role() = 'admin'
        )
    )
    WITH CHECK (
        -- Prevent ownership transfer without admin role
        (metadata->>'owner_id' = auth.user_id()::text OR auth.user_role() = 'admin') AND
        -- Ensure owner_id is not removed
        metadata ? 'owner_id'
    );

-- Policy for deleting projects
-- Only project owners or admins can delete projects
CREATE POLICY "Users can delete their own projects" ON projects
    FOR DELETE 
    USING (
        auth.is_authenticated() AND (
            metadata->>'owner_id' = auth.user_id()::text OR
            auth.user_role() = 'admin'
        )
    );

-- =============================================================================
-- CONVERSATIONS TABLE POLICIES
-- =============================================================================

-- Policy for viewing conversations
-- Users can view conversations from projects they have access to
CREATE POLICY "Users can view conversations from accessible projects" ON conversations
    FOR SELECT 
    USING (
        auth.is_authenticated() AND
        project_id IN (
            SELECT id FROM projects WHERE
                metadata->>'owner_id' = auth.user_id()::text OR
                metadata->'shared_users' ? auth.user_id()::text OR
                auth.user_role() = 'admin'
        )
    );

-- Policy for creating conversations
-- Users can create conversations in projects they have access to
CREATE POLICY "Users can create conversations in accessible projects" ON conversations
    FOR INSERT 
    WITH CHECK (
        auth.is_authenticated() AND
        project_id IN (
            SELECT id FROM projects WHERE
                metadata->>'owner_id' = auth.user_id()::text OR
                metadata->'shared_users' ? auth.user_id()::text OR
                auth.user_role() = 'admin'
        )
    );

-- Policy for updating conversations
-- Users can update conversations in projects they have access to
CREATE POLICY "Users can update conversations in accessible projects" ON conversations
    FOR UPDATE 
    USING (
        auth.is_authenticated() AND
        project_id IN (
            SELECT id FROM projects WHERE
                metadata->>'owner_id' = auth.user_id()::text OR
                metadata->'shared_users' ? auth.user_id()::text OR
                auth.user_role() = 'admin'
        )
    );

-- Policy for deleting conversations
-- Users can delete conversations from projects they own
CREATE POLICY "Users can delete conversations from owned projects" ON conversations
    FOR DELETE 
    USING (
        auth.is_authenticated() AND
        project_id IN (
            SELECT id FROM projects WHERE
                metadata->>'owner_id' = auth.user_id()::text OR
                auth.user_role() = 'admin'
        )
    );

-- =============================================================================
-- MESSAGES TABLE POLICIES
-- =============================================================================

-- Policy for viewing messages
-- Users can view messages from conversations in accessible projects
CREATE POLICY "Users can view messages from accessible conversations" ON messages
    FOR SELECT 
    USING (
        auth.is_authenticated() AND
        conversation_id IN (
            SELECT c.id FROM conversations c
            JOIN projects p ON c.project_id = p.id
            WHERE 
                p.metadata->>'owner_id' = auth.user_id()::text OR
                p.metadata->'shared_users' ? auth.user_id()::text OR
                auth.user_role() = 'admin'
        )
    );

-- Policy for creating messages
-- Users can create messages in conversations from accessible projects
CREATE POLICY "Users can create messages in accessible conversations" ON messages
    FOR INSERT 
    WITH CHECK (
        auth.is_authenticated() AND
        conversation_id IN (
            SELECT c.id FROM conversations c
            JOIN projects p ON c.project_id = p.id
            WHERE 
                p.metadata->>'owner_id' = auth.user_id()::text OR
                p.metadata->'shared_users' ? auth.user_id()::text OR
                auth.user_role() = 'admin'
        )
    );

-- Policy for updating messages
-- Users can update messages in conversations from accessible projects
CREATE POLICY "Users can update messages in accessible conversations" ON messages
    FOR UPDATE 
    USING (
        auth.is_authenticated() AND
        conversation_id IN (
            SELECT c.id FROM conversations c
            JOIN projects p ON c.project_id = p.id
            WHERE 
                p.metadata->>'owner_id' = auth.user_id()::text OR
                p.metadata->'shared_users' ? auth.user_id()::text OR
                auth.user_role() = 'admin'
        )
    );

-- Policy for deleting messages
-- Users can delete messages from conversations in owned projects
CREATE POLICY "Users can delete messages from owned conversations" ON messages
    FOR DELETE 
    USING (
        auth.is_authenticated() AND
        conversation_id IN (
            SELECT c.id FROM conversations c
            JOIN projects p ON c.project_id = p.id
            WHERE 
                p.metadata->>'owner_id' = auth.user_id()::text OR
                auth.user_role() = 'admin'
        )
    );

-- =============================================================================
-- TOOL_CALLS TABLE POLICIES
-- =============================================================================

-- Policy for viewing tool calls
-- Users can view tool calls from messages in accessible conversations
CREATE POLICY "Users can view tool calls from accessible messages" ON tool_calls
    FOR SELECT 
    USING (
        auth.is_authenticated() AND
        message_id IN (
            SELECT m.id FROM messages m
            JOIN conversations c ON m.conversation_id = c.id
            JOIN projects p ON c.project_id = p.id
            WHERE 
                p.metadata->>'owner_id' = auth.user_id()::text OR
                p.metadata->'shared_users' ? auth.user_id()::text OR
                auth.user_role() = 'admin'
        )
    );

-- Policy for creating tool calls
-- Users can create tool calls for messages in accessible conversations
CREATE POLICY "Users can create tool calls for accessible messages" ON tool_calls
    FOR INSERT 
    WITH CHECK (
        auth.is_authenticated() AND
        message_id IN (
            SELECT m.id FROM messages m
            JOIN conversations c ON m.conversation_id = c.id
            JOIN projects p ON c.project_id = p.id
            WHERE 
                p.metadata->>'owner_id' = auth.user_id()::text OR
                p.metadata->'shared_users' ? auth.user_id()::text OR
                auth.user_role() = 'admin'
        )
    );

-- Policy for updating tool calls
-- Users can update tool calls for messages in accessible conversations
CREATE POLICY "Users can update tool calls for accessible messages" ON tool_calls
    FOR UPDATE 
    USING (
        auth.is_authenticated() AND
        message_id IN (
            SELECT m.id FROM messages m
            JOIN conversations c ON m.conversation_id = c.id
            JOIN projects p ON c.project_id = p.id
            WHERE 
                p.metadata->>'owner_id' = auth.user_id()::text OR
                p.metadata->'shared_users' ? auth.user_id()::text OR
                auth.user_role() = 'admin'
        )
    );

-- Policy for deleting tool calls
-- Users can delete tool calls from messages in owned conversations
CREATE POLICY "Users can delete tool calls from owned messages" ON tool_calls
    FOR DELETE 
    USING (
        auth.is_authenticated() AND
        message_id IN (
            SELECT m.id FROM messages m
            JOIN conversations c ON m.conversation_id = c.id
            JOIN projects p ON c.project_id = p.id
            WHERE 
                p.metadata->>'owner_id' = auth.user_id()::text OR
                auth.user_role() = 'admin'
        )
    );

-- =============================================================================
-- SERVICE ROLE POLICIES (BYPASS RLS)
-- =============================================================================

-- Allow service role to bypass RLS for system operations
-- These policies enable the backend to perform administrative tasks

CREATE POLICY "Service role can access all projects" ON projects
    FOR ALL 
    USING (auth.user_role() = 'service_role')
    WITH CHECK (auth.user_role() = 'service_role');

CREATE POLICY "Service role can access all conversations" ON conversations
    FOR ALL 
    USING (auth.user_role() = 'service_role')
    WITH CHECK (auth.user_role() = 'service_role');

CREATE POLICY "Service role can access all messages" ON messages
    FOR ALL 
    USING (auth.user_role() = 'service_role')
    WITH CHECK (auth.user_role() = 'service_role');

CREATE POLICY "Service role can access all tool calls" ON tool_calls
    FOR ALL 
    USING (auth.user_role() = 'service_role')
    WITH CHECK (auth.user_role() = 'service_role');

-- =============================================================================
-- AUDIT LOGGING
-- =============================================================================

-- Create audit log table for sensitive operations
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,
    user_id UUID,
    user_role TEXT,
    record_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS on audit log
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- Only admins and service role can view audit logs
CREATE POLICY "Admins can view audit logs" ON audit_log
    FOR SELECT 
    USING (
        auth.is_authenticated() AND
        auth.user_role() IN ('admin', 'service_role')
    );

-- Function to log audit events
CREATE OR REPLACE FUNCTION log_audit_event()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (
        table_name,
        operation,
        user_id,
        user_role,
        record_id,
        old_values,
        new_values
    ) VALUES (
        TG_TABLE_NAME,
        TG_OP,
        auth.user_id(),
        auth.user_role(),
        COALESCE(NEW.id, OLD.id),
        CASE WHEN TG_OP = 'DELETE' THEN to_jsonb(OLD) ELSE NULL END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN to_jsonb(NEW) ELSE NULL END
    );
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create audit triggers for sensitive operations
CREATE TRIGGER audit_projects_changes
    AFTER INSERT OR UPDATE OR DELETE ON projects
    FOR EACH ROW EXECUTE FUNCTION log_audit_event();

-- =============================================================================
-- REAL-TIME PUBLICATION SETTINGS
-- =============================================================================

-- Configure Supabase Realtime publications with RLS filtering
-- This ensures real-time events respect the same security policies

-- Enable realtime for all tables
ALTER PUBLICATION supabase_realtime ADD TABLE projects;
ALTER PUBLICATION supabase_realtime ADD TABLE conversations;
ALTER PUBLICATION supabase_realtime ADD TABLE messages;
ALTER PUBLICATION supabase_realtime ADD TABLE tool_calls;

-- =============================================================================
-- SECURITY HELPER VIEWS
-- =============================================================================

-- View for users to see their accessible projects
CREATE VIEW user_projects AS
SELECT p.* FROM projects p
WHERE 
    p.metadata->>'owner_id' = auth.user_id()::text OR
    p.metadata->'shared_users' ? auth.user_id()::text;

-- View for users to see their accessible conversations
CREATE VIEW user_conversations AS
SELECT c.* FROM conversations c
JOIN projects p ON c.project_id = p.id
WHERE 
    p.metadata->>'owner_id' = auth.user_id()::text OR
    p.metadata->'shared_users' ? auth.user_id()::text;

-- Set RLS on views
ALTER VIEW user_projects SET (security_barrier = true);
ALTER VIEW user_conversations SET (security_barrier = true);

-- =============================================================================
-- COMMENTS FOR SECURITY DOCUMENTATION
-- =============================================================================

COMMENT ON POLICY "Users can view their own projects" ON projects IS 
    'Allows users to view projects they own or have been shared with them';

COMMENT ON POLICY "Users can view conversations from accessible projects" ON conversations IS 
    'Inherits project-level permissions for conversation access';

COMMENT ON FUNCTION auth.user_id() IS 
    'Extracts user ID from JWT token for RLS policies';

COMMENT ON TABLE audit_log IS 
    'Tracks sensitive operations for security monitoring and compliance';