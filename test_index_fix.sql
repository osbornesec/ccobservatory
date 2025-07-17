-- Test script to verify that the fixed index works properly
-- This should run without errors now

-- Test the problematic index that was causing the error
CREATE INDEX IF NOT EXISTS idx_recent_tool_usage_test
    ON tool_calls(started_at DESC, tool_name);

-- Test the monitoring view
CREATE OR REPLACE VIEW index_usage_stats_test AS
SELECT 
    schemaname,
    relname as tablename,
    indexrelname as indexname,
    idx_tup_read,
    idx_tup_fetch,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes 
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- If we reach here, the fix worked
SELECT 'Migration fix successful - no immutable function errors' AS result;