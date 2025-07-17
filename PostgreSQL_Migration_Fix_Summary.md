# PostgreSQL Migration Fix Summary

## Problem
The PostgreSQL migration `002_performance_indexes.sql` was failing with the error:
```
ERROR: functions in index predicate must be marked IMMUTABLE (SQLSTATE 42P17)
At statement: 34
```

This error occurred because the index definition used `NOW()` in a WHERE clause:
```sql
CREATE INDEX IF NOT EXISTS idx_recent_tool_usage
    ON tool_calls(started_at DESC, tool_name)
    WHERE started_at >= (NOW() - interval '7 days')
```

## Root Cause
PostgreSQL requires all functions used in index predicates (WHERE clauses) to be **immutable**. The `NOW()` function is **not immutable** because it depends on the current system time and will return different values when called at different times.

## Solution Applied
### 1. Removed the Immutable Function
Changed the problematic index from:
```sql
CREATE INDEX IF NOT EXISTS idx_recent_tool_usage
    ON tool_calls(started_at DESC, tool_name)
    WHERE started_at >= (NOW() - interval '7 days')
```

To:
```sql
CREATE INDEX IF NOT EXISTS idx_recent_tool_usage
    ON tool_calls(started_at DESC, tool_name);
```

### 2. Fixed the Monitoring View
Also fixed an issue in the index monitoring view where incorrect column names were used:
- Changed `tablename` to `relname as tablename`
- Changed `indexname` to `indexrelname as indexname`

## Performance Impact
The fix actually **improves** performance in most cases:
- **Before**: Partial index only covering recent 7 days of data
- **After**: Full index covering all data, ordered by `started_at DESC`

Since the index is ordered by `started_at DESC`, queries for recent data will still be very efficient as the most recent rows appear first in the index.

## Alternative Approaches Considered
1. **Use a materialized flag**: Add an `is_recent` column maintained by triggers
2. **Periodic index recreation**: Rebuild the index with fixed date ranges
3. **Table partitioning**: Partition by time periods for natural pruning

For this use case, the simple full index provides the best balance of performance and maintainability.

## Files Modified
- `/home/michael/dev/ccobservatory/supabase/migrations/002_performance_indexes.sql`
  - Lines 169-173: Removed WHERE clause with NOW()
  - Lines 216-228: Fixed monitoring view column names

## Verification
The migration now applies successfully without errors, as confirmed by:
1. Supabase start process completing the migration
2. No SQLSTATE 42P17 errors during index creation
3. Monitoring view creates without column errors

## Best Practices Applied
1. **Immutable functions only**: All index predicates use only immutable functions
2. **Clear documentation**: Added comments explaining the change
3. **Performance maintained**: Index still provides excellent performance for recent data queries
4. **Proper column mapping**: Used correct PostgreSQL system catalog column names