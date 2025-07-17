-- Migration: 004_search_capabilities.sql
-- Description: Full-text search and advanced search capabilities
-- Created: 2025-01-16
-- Dependencies: 003_security_policies.sql

-- =============================================================================
-- FULL-TEXT SEARCH CONFIGURATION
-- =============================================================================

-- Create custom text search configuration for code and technical content
CREATE TEXT SEARCH CONFIGURATION english_code (COPY = english);

-- Add custom dictionary for code terms
CREATE TEXT SEARCH DICTIONARY code_dict (
    TEMPLATE = simple,
    STOPWORDS = english,
    ACCEPT = false
);

-- Configure custom text search for technical content
ALTER TEXT SEARCH CONFIGURATION english_code
    ALTER MAPPING FOR asciiword, asciihword, hword_asciipart, word, hword, hword_part
    WITH code_dict, english_stem;

-- =============================================================================
-- SEARCH FUNCTIONS
-- =============================================================================

-- Function to search messages with ranking and highlighting
CREATE OR REPLACE FUNCTION search_messages(
    search_query TEXT,
    project_ids UUID[] DEFAULT NULL,
    conversation_ids UUID[] DEFAULT NULL,
    message_roles TEXT[] DEFAULT NULL,
    limit_count INTEGER DEFAULT 50,
    offset_count INTEGER DEFAULT 0
)
RETURNS TABLE (
    id UUID,
    conversation_id UUID,
    project_id UUID,
    role TEXT,
    content TEXT,
    timestamp TIMESTAMPTZ,
    token_count INTEGER,
    rank REAL,
    headline TEXT,
    project_name TEXT,
    conversation_title TEXT
) 
LANGUAGE plpgsql STABLE SECURITY DEFINER
AS $$
DECLARE
    ts_query tsquery;
BEGIN
    -- Convert search query to tsquery
    ts_query := websearch_to_tsquery('english_code', search_query);
    
    RETURN QUERY
    SELECT 
        m.id,
        m.conversation_id,
        c.project_id,
        m.role,
        m.content,
        m.timestamp,
        m.token_count,
        ts_rank_cd(to_tsvector('english_code', m.content), ts_query) as rank,
        ts_headline(
            'english_code',
            m.content,
            ts_query,
            'StartSel=<mark>, StopSel=</mark>, MaxWords=50, MinWords=10'
        ) as headline,
        p.name as project_name,
        c.title as conversation_title
    FROM messages m
    JOIN conversations c ON m.conversation_id = c.id
    JOIN projects p ON c.project_id = p.id
    WHERE 
        to_tsvector('english_code', m.content) @@ ts_query
        AND (project_ids IS NULL OR c.project_id = ANY(project_ids))
        AND (conversation_ids IS NULL OR m.conversation_id = ANY(conversation_ids))
        AND (message_roles IS NULL OR m.role = ANY(message_roles))
        -- Apply RLS by checking project access
        AND (
            p.metadata->>'owner_id' = auth.user_id()::text OR
            p.metadata->'shared_users' ? auth.user_id()::text OR
            auth.user_role() IN ('admin', 'service_role')
        )
    ORDER BY rank DESC, m.timestamp DESC
    LIMIT limit_count
    OFFSET offset_count;
END;
$$;

-- Function to search conversations
CREATE OR REPLACE FUNCTION search_conversations(
    search_query TEXT,
    project_ids UUID[] DEFAULT NULL,
    limit_count INTEGER DEFAULT 50,
    offset_count INTEGER DEFAULT 0
)
RETURNS TABLE (
    id UUID,
    project_id UUID,
    title TEXT,
    file_path TEXT,
    message_count INTEGER,
    created_at TIMESTAMPTZ,
    last_updated TIMESTAMPTZ,
    rank REAL,
    headline TEXT,
    project_name TEXT
) 
LANGUAGE plpgsql STABLE SECURITY DEFINER
AS $$
DECLARE
    ts_query tsquery;
BEGIN
    ts_query := websearch_to_tsquery('english_code', search_query);
    
    RETURN QUERY
    SELECT 
        c.id,
        c.project_id,
        c.title,
        c.file_path,
        c.message_count,
        c.created_at,
        c.last_updated,
        ts_rank_cd(
            to_tsvector('english_code', coalesce(c.title, '') || ' ' || c.file_path),
            ts_query
        ) as rank,
        ts_headline(
            'english_code',
            coalesce(c.title, c.file_path),
            ts_query,
            'StartSel=<mark>, StopSel=</mark>, MaxWords=20'
        ) as headline,
        p.name as project_name
    FROM conversations c
    JOIN projects p ON c.project_id = p.id
    WHERE 
        (
            to_tsvector('english_code', coalesce(c.title, '')) @@ ts_query OR
            to_tsvector('english_code', c.file_path) @@ ts_query
        )
        AND (project_ids IS NULL OR c.project_id = ANY(project_ids))
        -- Apply RLS
        AND (
            p.metadata->>'owner_id' = auth.user_id()::text OR
            p.metadata->'shared_users' ? auth.user_id()::text OR
            auth.user_role() IN ('admin', 'service_role')
        )
    ORDER BY rank DESC, c.last_updated DESC
    LIMIT limit_count
    OFFSET offset_count;
END;
$$;

-- Function to search projects
CREATE OR REPLACE FUNCTION search_projects(
    search_query TEXT,
    limit_count INTEGER DEFAULT 50,
    offset_count INTEGER DEFAULT 0
)
RETURNS TABLE (
    id UUID,
    name TEXT,
    description TEXT,
    path TEXT,
    last_activity TIMESTAMPTZ,
    conversation_count BIGINT,
    rank REAL,
    headline TEXT
) 
LANGUAGE plpgsql STABLE SECURITY DEFINER
AS $$
DECLARE
    ts_query tsquery;
BEGIN
    ts_query := websearch_to_tsquery('english_code', search_query);
    
    RETURN QUERY
    SELECT 
        p.id,
        p.name,
        p.description,
        p.path,
        p.last_activity,
        count(c.id) as conversation_count,
        ts_rank_cd(
            to_tsvector('english_code', 
                p.name || ' ' || coalesce(p.description, '') || ' ' || p.path
            ),
            ts_query
        ) as rank,
        ts_headline(
            'english_code',
            p.name || ' ' || coalesce(p.description, ''),
            ts_query,
            'StartSel=<mark>, StopSel=</mark>, MaxWords=30'
        ) as headline
    FROM projects p
    LEFT JOIN conversations c ON p.id = c.project_id
    WHERE 
        to_tsvector('english_code', 
            p.name || ' ' || coalesce(p.description, '') || ' ' || p.path
        ) @@ ts_query
        -- Apply RLS
        AND (
            p.metadata->>'owner_id' = auth.user_id()::text OR
            p.metadata->'shared_users' ? auth.user_id()::text OR
            auth.user_role() IN ('admin', 'service_role')
        )
    GROUP BY p.id, p.name, p.description, p.path, p.last_activity
    ORDER BY rank DESC, p.last_activity DESC NULLS LAST
    LIMIT limit_count
    OFFSET offset_count;
END;
$$;

-- =============================================================================
-- ADVANCED SEARCH CAPABILITIES
-- =============================================================================

-- Function for semantic/similarity search
CREATE OR REPLACE FUNCTION similar_messages(
    target_content TEXT,
    conversation_ids UUID[] DEFAULT NULL,
    similarity_threshold REAL DEFAULT 0.3,
    limit_count INTEGER DEFAULT 20
)
RETURNS TABLE (
    id UUID,
    conversation_id UUID,
    content TEXT,
    similarity REAL,
    timestamp TIMESTAMPTZ
) 
LANGUAGE plpgsql STABLE SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        m.id,
        m.conversation_id,
        m.content,
        similarity(m.content, target_content) as similarity,
        m.timestamp
    FROM messages m
    JOIN conversations c ON m.conversation_id = c.id
    JOIN projects p ON c.project_id = p.id
    WHERE 
        similarity(m.content, target_content) > similarity_threshold
        AND (conversation_ids IS NULL OR m.conversation_id = ANY(conversation_ids))
        -- Apply RLS
        AND (
            p.metadata->>'owner_id' = auth.user_id()::text OR
            p.metadata->'shared_users' ? auth.user_id()::text OR
            auth.user_role() IN ('admin', 'service_role')
        )
    ORDER BY similarity DESC, m.timestamp DESC
    LIMIT limit_count;
END;
$$;

-- Function to search tool usage patterns
CREATE OR REPLACE FUNCTION search_tool_usage(
    tool_name_pattern TEXT DEFAULT NULL,
    project_ids UUID[] DEFAULT NULL,
    status_filter TEXT[] DEFAULT NULL,
    date_from TIMESTAMPTZ DEFAULT NULL,
    date_to TIMESTAMPTZ DEFAULT NULL,
    limit_count INTEGER DEFAULT 100
)
RETURNS TABLE (
    tool_call_id UUID,
    message_id UUID,
    conversation_id UUID,
    project_id UUID,
    tool_name TEXT,
    status TEXT,
    execution_time_ms INTEGER,
    started_at TIMESTAMPTZ,
    input_data JSONB,
    project_name TEXT
) 
LANGUAGE plpgsql STABLE SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        tc.id as tool_call_id,
        tc.message_id,
        m.conversation_id,
        c.project_id,
        tc.tool_name,
        tc.status,
        tc.execution_time_ms,
        tc.started_at,
        tc.input_data,
        p.name as project_name
    FROM tool_calls tc
    JOIN messages m ON tc.message_id = m.id
    JOIN conversations c ON m.conversation_id = c.id
    JOIN projects p ON c.project_id = p.id
    WHERE 
        (tool_name_pattern IS NULL OR tc.tool_name ILIKE tool_name_pattern)
        AND (project_ids IS NULL OR c.project_id = ANY(project_ids))
        AND (status_filter IS NULL OR tc.status = ANY(status_filter))
        AND (date_from IS NULL OR tc.started_at >= date_from)
        AND (date_to IS NULL OR tc.started_at <= date_to)
        -- Apply RLS
        AND (
            p.metadata->>'owner_id' = auth.user_id()::text OR
            p.metadata->'shared_users' ? auth.user_id()::text OR
            auth.user_role() IN ('admin', 'service_role')
        )
    ORDER BY tc.started_at DESC
    LIMIT limit_count;
END;
$$;

-- =============================================================================
-- SEARCH ANALYTICS AND INSIGHTS
-- =============================================================================

-- Function to get search suggestions based on common terms
CREATE OR REPLACE FUNCTION get_search_suggestions(
    partial_query TEXT,
    suggestion_type TEXT DEFAULT 'message', -- 'message', 'tool', 'project'
    limit_count INTEGER DEFAULT 10
)
RETURNS TABLE (
    suggestion TEXT,
    frequency BIGINT,
    context TEXT
) 
LANGUAGE plpgsql STABLE SECURITY DEFINER
AS $$
BEGIN
    IF suggestion_type = 'message' THEN
        RETURN QUERY
        WITH word_frequencies AS (
            SELECT 
                word,
                count(*) as freq,
                'message content' as ctx
            FROM (
                SELECT unnest(tsvector_to_array(to_tsvector('english_code', content))) as word
                FROM messages m
                JOIN conversations c ON m.conversation_id = c.id
                JOIN projects p ON c.project_id = p.id
                WHERE 
                    -- Apply RLS
                    (
                        p.metadata->>'owner_id' = auth.user_id()::text OR
                        p.metadata->'shared_users' ? auth.user_id()::text OR
                        auth.user_role() IN ('admin', 'service_role')
                    )
            ) words
            WHERE word ILIKE partial_query || '%'
            GROUP BY word
        )
        SELECT word, freq, ctx FROM word_frequencies
        ORDER BY freq DESC, word
        LIMIT limit_count;
        
    ELSIF suggestion_type = 'tool' THEN
        RETURN QUERY
        SELECT 
            tc.tool_name as suggestion,
            count(*)::bigint as frequency,
            'tool name' as context
        FROM tool_calls tc
        JOIN messages m ON tc.message_id = m.id
        JOIN conversations c ON m.conversation_id = c.id
        JOIN projects p ON c.project_id = p.id
        WHERE 
            tc.tool_name ILIKE partial_query || '%'
            -- Apply RLS
            AND (
                p.metadata->>'owner_id' = auth.user_id()::text OR
                p.metadata->'shared_users' ? auth.user_id()::text OR
                auth.user_role() IN ('admin', 'service_role')
            )
        GROUP BY tc.tool_name
        ORDER BY frequency DESC, tc.tool_name
        LIMIT limit_count;
        
    ELSIF suggestion_type = 'project' THEN
        RETURN QUERY
        SELECT 
            p.name as suggestion,
            count(c.id)::bigint as frequency,
            'project name' as context
        FROM projects p
        LEFT JOIN conversations c ON p.id = c.project_id
        WHERE 
            p.name ILIKE partial_query || '%'
            -- Apply RLS
            AND (
                p.metadata->>'owner_id' = auth.user_id()::text OR
                p.metadata->'shared_users' ? auth.user_id()::text OR
                auth.user_role() IN ('admin', 'service_role')
            )
        GROUP BY p.name
        ORDER BY frequency DESC, p.name
        LIMIT limit_count;
    END IF;
END;
$$;

-- =============================================================================
-- SEARCH MATERIALIZED VIEWS
-- =============================================================================

-- Materialized view for search analytics
CREATE MATERIALIZED VIEW search_analytics AS
SELECT 
    p.id as project_id,
    p.name as project_name,
    count(DISTINCT c.id) as conversation_count,
    count(DISTINCT m.id) as message_count,
    count(DISTINCT tc.id) as tool_call_count,
    array_agg(DISTINCT tc.tool_name) FILTER (WHERE tc.tool_name IS NOT NULL) as used_tools,
    max(m.timestamp) as last_message_time,
    avg(length(m.content))::integer as avg_message_length,
    count(DISTINCT date_trunc('day', m.timestamp)) as active_days
FROM projects p
LEFT JOIN conversations c ON p.id = c.project_id
LEFT JOIN messages m ON c.id = m.conversation_id
LEFT JOIN tool_calls tc ON m.id = tc.message_id
GROUP BY p.id, p.name;

-- Create index on materialized view
CREATE UNIQUE INDEX idx_search_analytics_project_id 
    ON search_analytics(project_id);

CREATE INDEX idx_search_analytics_stats 
    ON search_analytics(message_count DESC, conversation_count DESC);

-- Function to refresh search analytics
CREATE OR REPLACE FUNCTION refresh_search_analytics()
RETURNS void 
LANGUAGE plpgsql SECURITY DEFINER
AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY search_analytics;
END;
$$;

-- =============================================================================
-- SEARCH HISTORY AND OPTIMIZATION
-- =============================================================================

-- Table to track search queries for optimization
CREATE TABLE IF NOT EXISTS search_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    query TEXT NOT NULL,
    search_type TEXT NOT NULL, -- 'message', 'conversation', 'project', 'tool'
    result_count INTEGER,
    execution_time_ms INTEGER,
    filters JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Index for search history analysis
CREATE INDEX idx_search_history_user_time 
    ON search_history(user_id, timestamp DESC);

CREATE INDEX idx_search_history_query_trgm 
    ON search_history USING gin(query gin_trgm_ops);

-- Function to log search queries
CREATE OR REPLACE FUNCTION log_search_query(
    query_text TEXT,
    search_type_param TEXT,
    result_count_param INTEGER,
    execution_time_param INTEGER,
    filters_param JSONB DEFAULT '{}'
)
RETURNS void 
LANGUAGE plpgsql SECURITY DEFINER
AS $$
BEGIN
    INSERT INTO search_history (
        user_id,
        query,
        search_type,
        result_count,
        execution_time_ms,
        filters
    ) VALUES (
        auth.user_id(),
        query_text,
        search_type_param,
        result_count_param,
        execution_time_param,
        filters_param
    );
END;
$$;

-- =============================================================================
-- COMMENTS FOR SEARCH DOCUMENTATION
-- =============================================================================

COMMENT ON FUNCTION search_messages IS 
    'Full-text search across message content with ranking and highlighting';

COMMENT ON FUNCTION search_conversations IS 
    'Search conversations by title and file path';

COMMENT ON FUNCTION search_projects IS 
    'Search projects by name, description, and path';

COMMENT ON FUNCTION similar_messages IS 
    'Find messages similar to target content using trigram similarity';

COMMENT ON FUNCTION search_tool_usage IS 
    'Search and analyze tool usage patterns across projects';

COMMENT ON FUNCTION get_search_suggestions IS 
    'Generate search suggestions based on user query patterns';

COMMENT ON MATERIALIZED VIEW search_analytics IS 
    'Aggregated statistics for search performance optimization';

COMMENT ON TABLE search_history IS 
    'Track search queries for analytics and optimization';