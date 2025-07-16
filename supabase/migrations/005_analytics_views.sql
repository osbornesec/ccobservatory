-- Migration: 005_analytics_views.sql
-- Description: Analytics views and aggregation tables for insights
-- Created: 2025-01-16
-- Dependencies: 004_search_capabilities.sql

-- =============================================================================
-- CONVERSATION ANALYTICS VIEWS
-- =============================================================================

-- Comprehensive conversation analytics view
CREATE VIEW conversation_analytics AS
SELECT 
    c.id as conversation_id,
    c.project_id,
    c.title,
    c.file_path,
    c.created_at,
    c.last_updated,
    c.status,
    -- Message statistics
    count(m.id) as actual_message_count,
    count(CASE WHEN m.role = 'user' THEN 1 END) as user_message_count,
    count(CASE WHEN m.role = 'assistant' THEN 1 END) as assistant_message_count,
    count(CASE WHEN m.role = 'system' THEN 1 END) as system_message_count,
    -- Content statistics
    avg(length(m.content))::integer as avg_message_length,
    max(length(m.content)) as max_message_length,
    sum(m.token_count) as total_tokens,
    avg(m.token_count)::integer as avg_tokens_per_message,
    -- Timing statistics
    min(m.timestamp) as first_message_time,
    max(m.timestamp) as last_message_time,
    extract(epoch from (max(m.timestamp) - min(m.timestamp)))/60 as duration_minutes,
    -- Tool usage statistics
    count(DISTINCT tc.tool_name) as unique_tools_used,
    count(tc.id) as total_tool_calls,
    count(CASE WHEN tc.status = 'success' THEN 1 END) as successful_tool_calls,
    count(CASE WHEN tc.status = 'error' THEN 1 END) as failed_tool_calls,
    avg(tc.execution_time_ms)::integer as avg_tool_execution_time,
    -- Threading statistics
    count(CASE WHEN m.parent_id IS NULL THEN 1 END) as root_message_count,
    max(m.depth) as max_thread_depth,
    avg(m.depth)::numeric(3,1) as avg_thread_depth
FROM conversations c
LEFT JOIN messages m ON c.id = m.conversation_id
LEFT JOIN tool_calls tc ON m.id = tc.message_id
GROUP BY c.id, c.project_id, c.title, c.file_path, c.created_at, c.last_updated, c.status;

-- Project-level analytics view
CREATE VIEW project_analytics AS
SELECT 
    p.id as project_id,
    p.name as project_name,
    p.path as project_path,
    p.created_at as project_created_at,
    p.last_activity,
    p.is_active,
    -- Conversation statistics
    count(DISTINCT c.id) as total_conversations,
    count(DISTINCT CASE WHEN c.status = 'active' THEN c.id END) as active_conversations,
    count(DISTINCT CASE WHEN c.status = 'completed' THEN c.id END) as completed_conversations,
    -- Message statistics
    count(DISTINCT m.id) as total_messages,
    sum(m.token_count) as total_tokens,
    avg(length(m.content))::integer as avg_message_length,
    -- Activity statistics
    count(DISTINCT date_trunc('day', m.timestamp)) as active_days,
    count(DISTINCT date_trunc('week', m.timestamp)) as active_weeks,
    min(m.timestamp) as first_message_time,
    max(m.timestamp) as last_message_time,
    -- Tool usage statistics
    count(DISTINCT tc.tool_name) as unique_tools_used,
    count(tc.id) as total_tool_calls,
    avg(tc.execution_time_ms)::integer as avg_tool_execution_time,
    -- Recent activity
    count(CASE WHEN m.timestamp >= now() - interval '24 hours' THEN 1 END) as messages_last_24h,
    count(CASE WHEN m.timestamp >= now() - interval '7 days' THEN 1 END) as messages_last_7d,
    count(CASE WHEN m.timestamp >= now() - interval '30 days' THEN 1 END) as messages_last_30d
FROM projects p
LEFT JOIN conversations c ON p.id = c.project_id
LEFT JOIN messages m ON c.id = m.conversation_id
LEFT JOIN tool_calls tc ON m.id = tc.message_id
GROUP BY p.id, p.name, p.path, p.created_at, p.last_activity, p.is_active;

-- =============================================================================
-- TOOL USAGE ANALYTICS
-- =============================================================================

-- Tool performance analytics view
CREATE VIEW tool_analytics AS
SELECT 
    tc.tool_name,
    count(*) as total_executions,
    count(CASE WHEN tc.status = 'success' THEN 1 END) as successful_executions,
    count(CASE WHEN tc.status = 'error' THEN 1 END) as failed_executions,
    count(CASE WHEN tc.status = 'timeout' THEN 1 END) as timeout_executions,
    round((count(CASE WHEN tc.status = 'success' THEN 1 END)::numeric / count(*) * 100), 2) as success_rate,
    -- Performance metrics
    avg(tc.execution_time_ms)::integer as avg_execution_time,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY tc.execution_time_ms)::integer as median_execution_time,
    percentile_cont(0.95) WITHIN GROUP (ORDER BY tc.execution_time_ms)::integer as p95_execution_time,
    min(tc.execution_time_ms) as min_execution_time,
    max(tc.execution_time_ms) as max_execution_time,
    -- Usage patterns
    count(DISTINCT date_trunc('day', tc.started_at)) as active_days,
    count(DISTINCT tc.message_id) as unique_messages,
    count(DISTINCT m.conversation_id) as unique_conversations,
    count(DISTINCT c.project_id) as unique_projects,
    -- Recent usage
    count(CASE WHEN tc.started_at >= now() - interval '24 hours' THEN 1 END) as executions_last_24h,
    count(CASE WHEN tc.started_at >= now() - interval '7 days' THEN 1 END) as executions_last_7d,
    min(tc.started_at) as first_used,
    max(tc.started_at) as last_used
FROM tool_calls tc
JOIN messages m ON tc.message_id = m.id
JOIN conversations c ON m.conversation_id = c.id
GROUP BY tc.tool_name;

-- Tool usage over time (daily aggregation)
CREATE VIEW tool_usage_daily AS
SELECT 
    date_trunc('day', tc.started_at) as date,
    tc.tool_name,
    count(*) as execution_count,
    count(CASE WHEN tc.status = 'success' THEN 1 END) as success_count,
    count(CASE WHEN tc.status = 'error' THEN 1 END) as error_count,
    avg(tc.execution_time_ms)::integer as avg_execution_time,
    count(DISTINCT tc.message_id) as unique_messages,
    count(DISTINCT m.conversation_id) as unique_conversations
FROM tool_calls tc
JOIN messages m ON tc.message_id = m.id
WHERE tc.started_at >= now() - interval '90 days' -- Last 90 days
GROUP BY date_trunc('day', tc.started_at), tc.tool_name
ORDER BY date DESC, tc.tool_name;

-- =============================================================================
-- USER ACTIVITY ANALYTICS
-- =============================================================================

-- User activity patterns (based on project ownership)
CREATE VIEW user_activity_analytics AS
SELECT 
    p.metadata->>'owner_id' as user_id,
    count(DISTINCT p.id) as owned_projects,
    count(DISTINCT c.id) as total_conversations,
    count(DISTINCT m.id) as total_messages,
    count(DISTINCT tc.id) as total_tool_calls,
    -- Activity timeline
    min(p.created_at) as first_project_created,
    max(p.last_activity) as last_activity,
    -- Recent activity
    count(DISTINCT CASE WHEN m.timestamp >= now() - interval '24 hours' THEN m.id END) as messages_last_24h,
    count(DISTINCT CASE WHEN m.timestamp >= now() - interval '7 days' THEN m.id END) as messages_last_7d,
    count(DISTINCT CASE WHEN m.timestamp >= now() - interval '30 days' THEN m.id END) as messages_last_30d,
    -- Usage patterns
    count(DISTINCT date_trunc('day', m.timestamp)) as active_days,
    avg(length(m.content))::integer as avg_message_length,
    -- Favorite tools
    mode() WITHIN GROUP (ORDER BY tc.tool_name) as most_used_tool,
    count(DISTINCT tc.tool_name) as unique_tools_used
FROM projects p
LEFT JOIN conversations c ON p.id = c.project_id
LEFT JOIN messages m ON c.id = m.conversation_id
LEFT JOIN tool_calls tc ON m.id = tc.message_id
WHERE p.metadata->>'owner_id' IS NOT NULL
GROUP BY p.metadata->>'owner_id';

-- =============================================================================
-- TEMPORAL ANALYTICS
-- =============================================================================

-- Daily activity summary
CREATE VIEW daily_activity AS
SELECT 
    date_trunc('day', m.timestamp) as date,
    count(DISTINCT c.project_id) as active_projects,
    count(DISTINCT m.conversation_id) as active_conversations,
    count(m.id) as message_count,
    count(CASE WHEN m.role = 'user' THEN 1 END) as user_messages,
    count(CASE WHEN m.role = 'assistant' THEN 1 END) as assistant_messages,
    sum(m.token_count) as total_tokens,
    count(DISTINCT tc.tool_name) as unique_tools_used,
    count(tc.id) as tool_call_count,
    avg(tc.execution_time_ms)::integer as avg_tool_execution_time
FROM messages m
JOIN conversations c ON m.conversation_id = c.id
LEFT JOIN tool_calls tc ON m.id = tc.message_id
WHERE m.timestamp >= now() - interval '90 days'
GROUP BY date_trunc('day', m.timestamp)
ORDER BY date DESC;

-- Hourly activity patterns (last 7 days)
CREATE VIEW hourly_activity AS
SELECT 
    date_trunc('hour', m.timestamp) as hour,
    extract(hour from m.timestamp) as hour_of_day,
    extract(dow from m.timestamp) as day_of_week,
    count(m.id) as message_count,
    count(DISTINCT m.conversation_id) as active_conversations,
    count(tc.id) as tool_call_count,
    avg(length(m.content))::integer as avg_message_length
FROM messages m
LEFT JOIN tool_calls tc ON m.id = tc.message_id
WHERE m.timestamp >= now() - interval '7 days'
GROUP BY date_trunc('hour', m.timestamp), extract(hour from m.timestamp), extract(dow from m.timestamp)
ORDER BY hour DESC;

-- =============================================================================
-- PERFORMANCE ANALYTICS
-- =============================================================================

-- System performance metrics
CREATE VIEW system_performance AS
SELECT 
    'overall' as scope,
    -- Database size metrics
    pg_size_pretty(pg_database_size(current_database())) as database_size,
    (SELECT count(*) FROM projects) as total_projects,
    (SELECT count(*) FROM conversations) as total_conversations,
    (SELECT count(*) FROM messages) as total_messages,
    (SELECT count(*) FROM tool_calls) as total_tool_calls,
    -- Performance indicators
    (SELECT avg(execution_time_ms) FROM tool_calls WHERE status = 'success')::integer as avg_tool_execution_time,
    (SELECT percentile_cont(0.95) WITHIN GROUP (ORDER BY execution_time_ms) FROM tool_calls WHERE status = 'success')::integer as p95_tool_execution_time,
    -- Recent activity indicators
    (SELECT count(*) FROM messages WHERE timestamp >= now() - interval '24 hours') as messages_last_24h,
    (SELECT count(*) FROM tool_calls WHERE started_at >= now() - interval '24 hours') as tool_calls_last_24h,
    -- Error rates
    (SELECT round((count(CASE WHEN status = 'error' THEN 1 END)::numeric / count(*) * 100), 2) FROM tool_calls WHERE started_at >= now() - interval '24 hours') as error_rate_24h;

-- Table size analytics
CREATE VIEW table_analytics AS
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size,
    (SELECT count(*) FROM information_schema.columns WHERE table_schema = schemaname AND table_name = tablename) as column_count
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- =============================================================================
-- MATERIALIZED VIEWS FOR HEAVY ANALYTICS
-- =============================================================================

-- Project summary statistics (refreshed periodically)
CREATE MATERIALIZED VIEW project_summary_stats AS
SELECT 
    p.id,
    p.name,
    p.created_at,
    p.last_activity,
    count(DISTINCT c.id) as conversation_count,
    count(DISTINCT m.id) as message_count,
    sum(m.token_count) as total_tokens,
    count(DISTINCT tc.tool_name) as unique_tools,
    count(tc.id) as tool_call_count,
    max(m.timestamp) as last_message_time,
    extract(epoch from (max(m.timestamp) - min(m.timestamp)))/3600 as total_hours,
    count(DISTINCT date_trunc('day', m.timestamp)) as active_days
FROM projects p
LEFT JOIN conversations c ON p.id = c.project_id
LEFT JOIN messages m ON c.id = m.conversation_id
LEFT JOIN tool_calls tc ON m.id = tc.message_id
GROUP BY p.id, p.name, p.created_at, p.last_activity;

-- Create unique index for concurrent refresh
CREATE UNIQUE INDEX idx_project_summary_stats_id 
    ON project_summary_stats(id);

-- Tool usage trends (materialized for performance)
CREATE MATERIALIZED VIEW tool_usage_trends AS
SELECT 
    tc.tool_name,
    date_trunc('week', tc.started_at) as week,
    count(*) as execution_count,
    count(CASE WHEN tc.status = 'success' THEN 1 END) as success_count,
    round(avg(tc.execution_time_ms)::numeric, 0) as avg_execution_time,
    count(DISTINCT m.conversation_id) as unique_conversations
FROM tool_calls tc
JOIN messages m ON tc.message_id = m.id
WHERE tc.started_at >= now() - interval '1 year'
GROUP BY tc.tool_name, date_trunc('week', tc.started_at)
ORDER BY week DESC, tc.tool_name;

CREATE INDEX idx_tool_usage_trends_tool_week 
    ON tool_usage_trends(tool_name, week DESC);

-- =============================================================================
-- REFRESH FUNCTIONS
-- =============================================================================

-- Function to refresh all materialized views
CREATE OR REPLACE FUNCTION refresh_analytics_views()
RETURNS TABLE (
    view_name TEXT,
    refresh_duration INTERVAL,
    rows_updated BIGINT
) 
LANGUAGE plpgsql SECURITY DEFINER
AS $$
DECLARE
    start_time TIMESTAMPTZ;
    end_time TIMESTAMPTZ;
    row_count BIGINT;
BEGIN
    -- Refresh project summary stats
    start_time := clock_timestamp();
    REFRESH MATERIALIZED VIEW CONCURRENTLY project_summary_stats;
    end_time := clock_timestamp();
    GET DIAGNOSTICS row_count = ROW_COUNT;
    
    RETURN QUERY SELECT 'project_summary_stats'::TEXT, end_time - start_time, row_count;
    
    -- Refresh tool usage trends
    start_time := clock_timestamp();
    REFRESH MATERIALIZED VIEW CONCURRENTLY tool_usage_trends;
    end_time := clock_timestamp();
    GET DIAGNOSTICS row_count = ROW_COUNT;
    
    RETURN QUERY SELECT 'tool_usage_trends'::TEXT, end_time - start_time, row_count;
    
    -- Refresh search analytics (from previous migration)
    start_time := clock_timestamp();
    REFRESH MATERIALIZED VIEW CONCURRENTLY search_analytics;
    end_time := clock_timestamp();
    GET DIAGNOSTICS row_count = ROW_COUNT;
    
    RETURN QUERY SELECT 'search_analytics'::TEXT, end_time - start_time, row_count;
END;
$$;

-- =============================================================================
-- ANALYTICS HELPER FUNCTIONS
-- =============================================================================

-- Function to get project insights
CREATE OR REPLACE FUNCTION get_project_insights(project_uuid UUID)
RETURNS TABLE (
    insight_type TEXT,
    insight_value TEXT,
    metric_value NUMERIC,
    context JSONB
) 
LANGUAGE plpgsql STABLE SECURITY DEFINER
AS $$
DECLARE
    project_stats RECORD;
BEGIN
    -- Get project statistics
    SELECT * INTO project_stats FROM project_analytics WHERE project_id = project_uuid;
    
    IF NOT FOUND THEN
        RETURN QUERY SELECT 'error'::TEXT, 'Project not found'::TEXT, 0::NUMERIC, '{}'::JSONB;
        RETURN;
    END IF;
    
    -- Most active conversation
    RETURN QUERY
    SELECT 
        'most_active_conversation'::TEXT,
        c.title::TEXT,
        ca.actual_message_count::NUMERIC,
        jsonb_build_object(
            'conversation_id', c.id,
            'duration_minutes', ca.duration_minutes,
            'tool_calls', ca.total_tool_calls
        )
    FROM conversation_analytics ca
    JOIN conversations c ON ca.conversation_id = c.id
    WHERE c.project_id = project_uuid
    ORDER BY ca.actual_message_count DESC
    LIMIT 1;
    
    -- Most used tool
    RETURN QUERY
    SELECT 
        'most_used_tool'::TEXT,
        tc.tool_name::TEXT,
        count(*)::NUMERIC,
        jsonb_build_object(
            'success_rate', round((count(CASE WHEN tc.status = 'success' THEN 1 END)::numeric / count(*) * 100), 2),
            'avg_execution_time', avg(tc.execution_time_ms)
        )
    FROM tool_calls tc
    JOIN messages m ON tc.message_id = m.id
    JOIN conversations c ON m.conversation_id = c.id
    WHERE c.project_id = project_uuid
    GROUP BY tc.tool_name
    ORDER BY count(*) DESC
    LIMIT 1;
    
    -- Activity trend
    RETURN QUERY
    SELECT 
        'activity_trend'::TEXT,
        CASE 
            WHEN project_stats.messages_last_7d > project_stats.messages_last_30d / 4 THEN 'increasing'
            WHEN project_stats.messages_last_7d < project_stats.messages_last_30d / 6 THEN 'decreasing'
            ELSE 'stable'
        END::TEXT,
        project_stats.messages_last_7d::NUMERIC,
        jsonb_build_object(
            'messages_last_30d', project_stats.messages_last_30d,
            'active_days', project_stats.active_days
        );
END;
$$;

-- =============================================================================
-- COMMENTS FOR ANALYTICS DOCUMENTATION
-- =============================================================================

COMMENT ON VIEW conversation_analytics IS 'Comprehensive conversation-level metrics and statistics';
COMMENT ON VIEW project_analytics IS 'Project-level aggregated analytics and usage patterns';
COMMENT ON VIEW tool_analytics IS 'Tool usage and performance analytics across all projects';
COMMENT ON VIEW user_activity_analytics IS 'User behavior patterns and activity metrics';
COMMENT ON VIEW daily_activity IS 'Daily system activity and usage trends';
COMMENT ON MATERIALIZED VIEW project_summary_stats IS 'Cached project statistics for dashboard performance';
COMMENT ON FUNCTION refresh_analytics_views IS 'Refresh all materialized views for updated analytics';
COMMENT ON FUNCTION get_project_insights IS 'Generate actionable insights for a specific project';