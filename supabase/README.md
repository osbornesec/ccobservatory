# Supabase Database Schema for Claude Code Observatory

This directory contains the complete database schema, migrations, and configuration for the Claude Code Observatory project using Supabase (PostgreSQL).

## Overview

The database schema is designed for high-performance storage and analysis of Claude Code conversations, with emphasis on:

- **Real-time capabilities** via Supabase Realtime
- **Row Level Security (RLS)** for data isolation
- **Full-text search** across conversation content
- **Analytics and insights** through materialized views
- **Performance optimization** with strategic indexing

## Architecture

### Core Tables

1. **`projects`** - Root entities organizing Claude Code projects
2. **`conversations`** - Groups of related messages from single sessions
3. **`messages`** - Individual conversation messages with threading support
4. **`tool_calls`** - Detailed tool usage tracking and performance metrics

### Supporting Tables

- **`search_history`** - Query analytics and optimization
- **`audit_log`** - Security and compliance tracking

### Views and Analytics

- **`conversation_analytics`** - Comprehensive conversation metrics
- **`project_analytics`** - Project-level usage patterns
- **`tool_analytics`** - Tool performance and usage statistics
- **`user_activity_analytics`** - User behavior patterns

## Migration Files

### 001_initial_schema.sql
Core database tables, constraints, triggers, and basic relationships.

**Key features:**
- UUID primary keys with automatic generation
- Comprehensive check constraints for data validation
- Foreign key relationships with appropriate cascade behavior
- Automatic timestamp management via triggers
- JSON/JSONB fields for flexible metadata storage

### 002_performance_indexes.sql
Strategic indexes for query optimization and performance.

**Key features:**
- Composite indexes for common query patterns
- GIN indexes for JSONB fields and full-text search
- Partial indexes for filtered queries
- Performance monitoring views

### 003_security_policies.sql
Row Level Security (RLS) policies for data protection.

**Key features:**
- User-based data isolation
- Project ownership and sharing mechanisms
- Service role bypass for system operations
- Audit logging for sensitive operations
- Supabase Realtime integration with security

### 004_search_capabilities.sql
Full-text search and advanced search functionality.

**Key features:**
- Custom text search configuration for technical content
- Search functions with ranking and highlighting
- Similarity search capabilities
- Search analytics and suggestions
- Materialized views for search optimization

### 005_analytics_views.sql
Analytics views and aggregation tables for insights.

**Key features:**
- Comprehensive analytics views
- Materialized views for performance
- Temporal analytics (daily/hourly patterns)
- Performance monitoring
- Insight generation functions

## Configuration

### config.toml
Supabase local development configuration with CCO-specific settings.

### seed.sql
Sample data for development and testing, including:
- Example projects with different use cases
- Realistic conversation data
- Tool usage examples
- Search history samples
- Analytics seed data

## Setup Instructions

### Prerequisites

1. Install Supabase CLI:
   ```bash
   npm install -g @supabase/cli
   ```

2. Ensure Docker is running for local development

### Local Development Setup

1. Initialize Supabase in your project:
   ```bash
   cd /path/to/ccobservatory
   supabase init
   ```

2. Start local Supabase services:
   ```bash
   supabase start
   ```

3. Apply migrations:
   ```bash
   supabase db reset
   ```

4. Verify setup:
   ```bash
   supabase status
   ```

### Production Deployment

1. Create Supabase project at [supabase.com](https://supabase.com)

2. Link local project:
   ```bash
   supabase link --project-ref YOUR_PROJECT_REF
   ```

3. Deploy migrations:
   ```bash
   supabase db push
   ```

4. Set up environment variables in your application:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   ```

## Performance Characteristics

### Query Performance Targets

- **Project queries**: < 50ms
- **Conversation retrieval**: < 100ms  
- **Message search**: < 500ms
- **Analytics queries**: < 1000ms

### Scalability

- **Projects**: 10,000+ per instance
- **Conversations**: 100,000+ per project
- **Messages**: 1,000,000+ per project
- **Concurrent users**: 100+ simultaneous

### Storage

- **Database size**: Optimized for 10GB+ databases
- **Message content**: Up to 1MB per message
- **Tool data**: Unlimited JSON storage in tool calls

## Security Features

### Row Level Security (RLS)

- **Project isolation**: Users can only access their own projects
- **Shared access**: Support for project sharing between users
- **Role-based access**: Admin and service role privileges
- **API security**: Integration with Supabase Auth

### Audit Logging

- **Sensitive operations**: Project creation, deletion, sharing
- **User tracking**: All operations linked to authenticated users
- **Compliance**: Full audit trail for security reviews

### Data Protection

- **Encryption**: All data encrypted at rest via Supabase
- **API keys**: Secure key rotation and management
- **Network security**: HTTPS/TLS for all communications

## Development Workflow

### Testing

Run the comprehensive test suite:

```bash
cd backend
python -m pytest tests/test_database_schema.py -v
```

Test specific categories:
```bash
# Performance tests
pytest -m performance

# Security tests  
pytest -m security

# Integration tests
pytest -m integration
```

### Schema Changes

1. Create new migration file:
   ```bash
   supabase migration new your_migration_name
   ```

2. Write migration SQL in the generated file

3. Test locally:
   ```bash
   supabase db reset
   ```

4. Deploy to production:
   ```bash
   supabase db push
   ```

### Monitoring

Use the built-in analytics views:

```sql
-- Check system performance
SELECT * FROM system_performance;

-- Monitor index usage
SELECT * FROM index_usage_stats;

-- Review table sizes
SELECT * FROM table_analytics;
```

## Troubleshooting

### Common Issues

1. **Migration failures**: Check constraint violations in migration logs
2. **Performance issues**: Review `index_usage_stats` and add missing indexes
3. **RLS problems**: Verify user authentication and policy logic
4. **Search issues**: Check text search configuration and indexes

### Debug Queries

```sql
-- Check foreign key relationships
SELECT * FROM information_schema.table_constraints 
WHERE constraint_type = 'FOREIGN KEY';

-- Verify RLS policies
SELECT * FROM pg_policies;

-- Monitor active connections
SELECT * FROM pg_stat_activity;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Contributing

When adding new features:

1. Follow TDD methodology - write tests first
2. Update migration files incrementally
3. Document performance implications
4. Test RLS policies thoroughly
5. Update analytics views if needed

## Support

For issues with the database schema:

1. Check the test suite for examples
2. Review migration files for constraints
3. Consult Supabase documentation for platform-specific features
4. Use the provided seed data for development and testing