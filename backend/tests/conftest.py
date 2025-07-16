"""
Pytest configuration for database schema tests
Sets up test database and fixtures for TDD workflow
"""

import pytest
import asyncio
import asyncpg
import os
from typing import AsyncGenerator


@pytest.fixture(scope="session")
async def test_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """
    Create test database connection for the session
    Uses separate test database to avoid conflicts
    """
    # Test database configuration
    test_db_config = {
        "host": os.getenv("TEST_DB_HOST", "localhost"),
        "port": int(os.getenv("TEST_DB_PORT", "54322")),
        "user": os.getenv("TEST_DB_USER", "postgres"),
        "password": os.getenv("TEST_DB_PASSWORD", "postgres"),
        "database": os.getenv("TEST_DB_NAME", "postgres"),
    }

    # Create connection
    conn = await asyncpg.connect(**test_db_config)

    try:
        # Ensure we're in a test environment
        await conn.execute("SET application_name = 'cco_test_suite'")
        yield conn
    finally:
        await conn.close()


@pytest.fixture(scope="session")
async def setup_test_schema(test_db_connection):
    """
    Set up test schema before each test module
    Applies migrations and ensures clean state
    """
    conn = test_db_connection

    # Check if tables exist, create if needed
    tables_exist = await conn.fetchval(
        """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'projects'
        )
    """
    )

    if not tables_exist:
        # Apply migrations (in a real scenario, this would use migration files)
        await apply_test_migrations(conn)

    # Clean existing data
    await cleanup_test_data(conn)


async def apply_test_migrations(conn: asyncpg.Connection):
    """Apply database migrations for testing"""

    # Enable required extensions
    await conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    await conn.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')
    await conn.execute('CREATE EXTENSION IF NOT EXISTS "btree_gin"')

    # Create tables (simplified for testing)
    await conn.execute(
        """
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
            
            CONSTRAINT projects_name_not_empty CHECK (char_length(name) > 0),
            CONSTRAINT projects_path_not_empty CHECK (char_length(path) > 0),
            CONSTRAINT projects_name_length CHECK (char_length(name) <= 255),
            CONSTRAINT projects_description_length CHECK (char_length(description) <= 2000),
            CONSTRAINT projects_updated_after_created CHECK (updated_at >= created_at)
        )
    """
    )

    await conn.execute(
        """
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
            
            CONSTRAINT conversations_file_path_not_empty CHECK (char_length(file_path) > 0),
            CONSTRAINT conversations_message_count_positive CHECK (message_count >= 0),
            CONSTRAINT conversations_status_valid CHECK (status IN ('active', 'completed', 'archived')),
            CONSTRAINT conversations_title_length CHECK (char_length(title) <= 500),
            CONSTRAINT conversations_last_updated_after_created CHECK (last_updated >= created_at)
        )
    """
    )

    await conn.execute(
        """
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
            
            CONSTRAINT messages_role_valid CHECK (role IN ('user', 'assistant', 'system')),
            CONSTRAINT messages_content_not_empty CHECK (char_length(content) > 0),
            CONSTRAINT messages_token_count_positive CHECK (token_count >= 0),
            CONSTRAINT messages_depth_positive CHECK (depth >= 0),
            CONSTRAINT messages_content_length CHECK (char_length(content) <= 1000000)
        )
    """
    )

    await conn.execute(
        """
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
            
            CONSTRAINT tool_calls_tool_name_not_empty CHECK (char_length(tool_name) > 0),
            CONSTRAINT tool_calls_execution_time_positive CHECK (execution_time_ms IS NULL OR execution_time_ms >= 0),
            CONSTRAINT tool_calls_status_valid CHECK (status IN ('pending', 'running', 'success', 'error', 'timeout')),
            CONSTRAINT tool_calls_completed_after_started CHECK (completed_at IS NULL OR completed_at >= started_at)
        )
    """
    )

    # Create search history table for testing
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS search_history (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID,
            query TEXT NOT NULL,
            search_type TEXT NOT NULL,
            result_count INTEGER,
            execution_time_ms INTEGER,
            filters JSONB,
            timestamp TIMESTAMPTZ DEFAULT NOW()
        )
    """
    )

    # Create indexes for performance
    await conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_conversations_project_updated 
            ON conversations(project_id, last_updated DESC)
    """
    )

    await conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_messages_conversation_timestamp 
            ON messages(conversation_id, timestamp ASC)
    """
    )

    await conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_tool_calls_message_started 
            ON tool_calls(message_id, started_at DESC)
    """
    )

    # Create triggers for automatic updates
    await conn.execute(
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql'
    """
    )

    await conn.execute(
        """
        CREATE TRIGGER update_projects_updated_at 
            BEFORE UPDATE ON projects 
            FOR EACH ROW 
            EXECUTE FUNCTION update_updated_at_column()
    """
    )

    await conn.execute(
        """
        CREATE OR REPLACE FUNCTION update_conversation_stats()
        RETURNS TRIGGER AS $$
        BEGIN
            UPDATE conversations 
            SET 
                message_count = (
                    SELECT COUNT(*) 
                    FROM messages 
                    WHERE conversation_id = COALESCE(NEW.conversation_id, OLD.conversation_id)
                ),
                last_updated = NOW()
            WHERE id = COALESCE(NEW.conversation_id, OLD.conversation_id);
            
            RETURN COALESCE(NEW, OLD);
        END;
        $$ language 'plpgsql'
    """
    )

    await conn.execute(
        """
        CREATE TRIGGER update_conversation_stats_on_insert
            AFTER INSERT ON messages
            FOR EACH ROW
            EXECUTE FUNCTION update_conversation_stats()
    """
    )

    await conn.execute(
        """
        CREATE TRIGGER update_conversation_stats_on_delete
            AFTER DELETE ON messages
            FOR EACH ROW
            EXECUTE FUNCTION update_conversation_stats()
    """
    )


async def cleanup_test_data(conn: asyncpg.Connection):
    """Clean up test data between tests"""
    # Clean in reverse dependency order
    await conn.execute("DELETE FROM tool_calls")
    await conn.execute("DELETE FROM messages")
    await conn.execute("DELETE FROM conversations")
    await conn.execute("DELETE FROM projects")
    await conn.execute("DELETE FROM search_history")


@pytest.fixture
async def clean_db(test_db_connection):
    """Ensure clean database state for each test"""
    await cleanup_test_data(test_db_connection)
    yield test_db_connection
    await cleanup_test_data(test_db_connection)


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "performance: marks tests as performance tests")
    config.addinivalue_line("markers", "security: marks tests as security tests")


def pytest_collection_modifyitems(config, items):
    """Automatically mark certain tests"""
    for item in items:
        # Mark performance tests
        if "performance" in item.name.lower():
            item.add_marker(pytest.mark.performance)

        # Mark integration tests
        if "integration" in item.name.lower():
            item.add_marker(pytest.mark.integration)

        # Mark security tests
        if "security" in item.name.lower() or "rls" in item.name.lower():
            item.add_marker(pytest.mark.security)

        # Mark slow tests
        if any(
            keyword in item.name.lower() for keyword in ["bulk", "large", "concurrent"]
        ):
            item.add_marker(pytest.mark.slow)
