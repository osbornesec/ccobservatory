"""
Database Schema Tests - Following TDD Methodology
Tests all database constraints, relationships, and performance requirements
"""

import pytest
import asyncio
import json
from datetime import datetime, timezone
from uuid import uuid4, UUID
from typing import Dict, List, Any
import asyncpg
import time
from dataclasses import dataclass
from app.database.supabase_client import SupabaseClientManager, get_supabase_client


@dataclass
class TestProject:
    """Test project data structure"""

    name: str
    path: str
    description: str = ""
    settings: Dict = None
    metadata: Dict = None

    def __post_init__(self):
        if self.settings is None:
            self.settings = {}
        if self.metadata is None:
            self.metadata = {"owner_id": str(uuid4())}


@dataclass
class TestConversation:
    """Test conversation data structure"""

    project_id: UUID
    file_path: str
    title: str = ""
    session_id: str = ""
    metadata: Dict = None

    def __post_init__(self):
        if not self.title:
            self.title = f"Test Conversation {datetime.now().isoformat()}"
        if not self.session_id:
            self.session_id = str(uuid4())
        if self.metadata is None:
            self.metadata = {}


@dataclass
class TestMessage:
    """Test message data structure"""

    conversation_id: UUID
    role: str
    content: str
    timestamp: datetime = None
    token_count: int = 0
    parent_id: UUID = None
    depth: int = 0
    metadata: Dict = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        if self.metadata is None:
            self.metadata = {}


@dataclass
class TestToolCall:
    """Test tool call data structure"""

    message_id: UUID
    tool_name: str
    input_data: Dict = None
    output_data: str = ""
    execution_time_ms: int = None
    status: str = "success"
    metadata: Dict = None

    def __post_init__(self):
        if self.input_data is None:
            self.input_data = {}
        if self.metadata is None:
            self.metadata = {}


class DatabaseTestHelper:
    """Helper class for database testing operations"""

    def __init__(self, connection):
        self.conn = connection

    async def create_test_project(self, project_data: TestProject = None) -> UUID:
        """Create a test project and return its ID"""
        if project_data is None:
            project_data = TestProject(
                name=f"Test Project {uuid4()}", path=f"/test/path/{uuid4()}"
            )

        result = await self.conn.fetchrow(
            """
            INSERT INTO projects (name, path, description, settings, metadata)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        """,
            project_data.name,
            project_data.path,
            project_data.description,
            json.dumps(project_data.settings),
            json.dumps(project_data.metadata),
        )

        return result["id"]

    async def create_test_conversation(
        self, conversation_data: TestConversation
    ) -> UUID:
        """Create a test conversation and return its ID"""
        result = await self.conn.fetchrow(
            """
            INSERT INTO conversations (project_id, file_path, title, session_id, metadata)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        """,
            conversation_data.project_id,
            conversation_data.file_path,
            conversation_data.title,
            conversation_data.session_id,
            json.dumps(conversation_data.metadata),
        )

        return result["id"]

    async def create_test_message(self, message_data: TestMessage) -> UUID:
        """Create a test message and return its ID"""
        result = await self.conn.fetchrow(
            """
            INSERT INTO messages (conversation_id, role, content, timestamp, token_count, parent_id, depth, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
        """,
            message_data.conversation_id,
            message_data.role,
            message_data.content,
            message_data.timestamp,
            message_data.token_count,
            message_data.parent_id,
            message_data.depth,
            json.dumps(message_data.metadata),
        )

        return result["id"]

    async def create_test_tool_call(self, tool_call_data: TestToolCall) -> UUID:
        """Create a test tool call and return its ID"""
        result = await self.conn.fetchrow(
            """
            INSERT INTO tool_calls (message_id, tool_name, input_data, output_data, execution_time_ms, status, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id
        """,
            tool_call_data.message_id,
            tool_call_data.tool_name,
            json.dumps(tool_call_data.input_data),
            tool_call_data.output_data,
            tool_call_data.execution_time_ms,
            tool_call_data.status,
            json.dumps(tool_call_data.metadata),
        )

        return result["id"]


@pytest.fixture
async def db_connection():
    """Create database connection for testing"""
    # Use test database credentials
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        database="test_ccobservatory",
    )
    yield conn
    await conn.close()


@pytest.fixture
async def db_helper(db_connection):
    """Database test helper instance"""
    return DatabaseTestHelper(db_connection)


@pytest.fixture(autouse=True)
async def cleanup_database(db_connection):
    """Clean up test data after each test"""
    yield
    # Clean up in reverse dependency order
    await db_connection.execute("DELETE FROM tool_calls")
    await db_connection.execute("DELETE FROM messages")
    await db_connection.execute("DELETE FROM conversations")
    await db_connection.execute("DELETE FROM projects")


class TestProjectsTable:
    """Test cases for projects table"""

    async def test_create_project_with_valid_data(self, db_helper):
        """Should create project with valid data and auto-generate fields"""
        project_data = TestProject(
            name="Valid Project", path="/valid/path", description="Test description"
        )

        project_id = await db_helper.create_test_project(project_data)

        # Verify project was created
        assert project_id is not None
        assert isinstance(project_id, UUID)

        # Verify all fields were set correctly
        result = await db_helper.conn.fetchrow(
            "SELECT * FROM projects WHERE id = $1", project_id
        )

        assert result["name"] == project_data.name
        assert result["path"] == project_data.path
        assert result["description"] == project_data.description
        assert result["created_at"] is not None
        assert result["updated_at"] is not None
        assert result["is_active"] == True
        assert json.loads(result["settings"]) == project_data.settings
        assert json.loads(result["metadata"]) == project_data.metadata

    async def test_project_name_uniqueness_constraint(self, db_helper):
        """Should reject duplicate project names"""
        project_data = TestProject(name="Unique Name", path="/path1")
        await db_helper.create_test_project(project_data)

        # Try to create another project with same name
        duplicate_project = TestProject(name="Unique Name", path="/path2")

        with pytest.raises(asyncpg.UniqueViolationError):
            await db_helper.create_test_project(duplicate_project)

    async def test_project_path_uniqueness_constraint(self, db_helper):
        """Should reject duplicate project paths"""
        project_data = TestProject(name="Name1", path="/unique/path")
        await db_helper.create_test_project(project_data)

        # Try to create another project with same path
        duplicate_project = TestProject(name="Name2", path="/unique/path")

        with pytest.raises(asyncpg.UniqueViolationError):
            await db_helper.create_test_project(duplicate_project)

    async def test_project_empty_name_constraint(self, db_helper):
        """Should reject empty project names"""
        with pytest.raises(asyncpg.CheckViolationError):
            await db_helper.conn.execute(
                """
                INSERT INTO projects (name, path) VALUES ('', '/test/path')
            """
            )

    async def test_project_empty_path_constraint(self, db_helper):
        """Should reject empty project paths"""
        with pytest.raises(asyncpg.CheckViolationError):
            await db_helper.conn.execute(
                """
                INSERT INTO projects (name, path) VALUES ('Test Name', '')
            """
            )

    async def test_project_name_length_constraint(self, db_helper):
        """Should reject project names exceeding 255 characters"""
        long_name = "a" * 256  # 256 characters

        with pytest.raises(asyncpg.CheckViolationError):
            await db_helper.conn.execute(
                """
                INSERT INTO projects (name, path) VALUES ($1, '/test/path')
            """,
                long_name,
            )

    async def test_project_description_length_constraint(self, db_helper):
        """Should reject descriptions exceeding 2000 characters"""
        long_description = "a" * 2001  # 2001 characters

        with pytest.raises(asyncpg.CheckViolationError):
            await db_helper.conn.execute(
                """
                INSERT INTO projects (name, path, description) VALUES ('Test', '/path', $1)
            """,
                long_description,
            )

    async def test_project_updated_at_trigger(self, db_helper):
        """Should update updated_at timestamp on modification"""
        project_id = await db_helper.create_test_project()

        # Get initial updated_at
        initial = await db_helper.conn.fetchrow(
            "SELECT updated_at FROM projects WHERE id = $1", project_id
        )

        # Wait a moment then update
        await asyncio.sleep(0.1)
        await db_helper.conn.execute(
            """
            UPDATE projects SET description = 'Updated description' WHERE id = $1
        """,
            project_id,
        )

        # Verify updated_at changed
        updated = await db_helper.conn.fetchrow(
            "SELECT updated_at FROM projects WHERE id = $1", project_id
        )

        assert updated["updated_at"] > initial["updated_at"]


class TestConversationsTable:
    """Test cases for conversations table"""

    async def test_create_conversation_with_valid_data(self, db_helper):
        """Should create conversation with valid data and foreign key"""
        project_id = await db_helper.create_test_project()
        conversation_data = TestConversation(
            project_id=project_id, file_path="/test/conversation.jsonl"
        )

        conversation_id = await db_helper.create_test_conversation(conversation_data)

        # Verify conversation was created
        assert conversation_id is not None

        result = await db_helper.conn.fetchrow(
            "SELECT * FROM conversations WHERE id = $1", conversation_id
        )

        assert result["project_id"] == project_id
        assert result["file_path"] == conversation_data.file_path
        assert result["title"] == conversation_data.title
        assert result["message_count"] == 0
        assert result["status"] == "active"

    async def test_conversation_foreign_key_constraint(self, db_helper):
        """Should reject invalid project_id references"""
        invalid_project_id = uuid4()
        conversation_data = TestConversation(
            project_id=invalid_project_id, file_path="/test/conversation.jsonl"
        )

        with pytest.raises(asyncpg.ForeignKeyViolationError):
            await db_helper.create_test_conversation(conversation_data)

    async def test_conversation_file_path_uniqueness(self, db_helper):
        """Should enforce unique file_path constraint"""
        project_id = await db_helper.create_test_project()

        conversation1 = TestConversation(
            project_id=project_id, file_path="/unique/path.jsonl"
        )
        await db_helper.create_test_conversation(conversation1)

        # Try to create another conversation with same file path
        conversation2 = TestConversation(
            project_id=project_id, file_path="/unique/path.jsonl"
        )

        with pytest.raises(asyncpg.UniqueViolationError):
            await db_helper.create_test_conversation(conversation2)

    async def test_conversation_cascade_delete(self, db_helper):
        """Should delete conversations when parent project is deleted"""
        project_id = await db_helper.create_test_project()
        conversation_id = await db_helper.create_test_conversation(
            TestConversation(project_id=project_id, file_path="/test.jsonl")
        )

        # Delete the project
        await db_helper.conn.execute("DELETE FROM projects WHERE id = $1", project_id)

        # Verify conversation was also deleted
        result = await db_helper.conn.fetchrow(
            "SELECT id FROM conversations WHERE id = $1", conversation_id
        )
        assert result is None

    async def test_conversation_status_constraint(self, db_helper):
        """Should enforce valid status values"""
        project_id = await db_helper.create_test_project()

        with pytest.raises(asyncpg.CheckViolationError):
            await db_helper.conn.execute(
                """
                INSERT INTO conversations (project_id, file_path, status)
                VALUES ($1, '/test.jsonl', 'invalid_status')
            """,
                project_id,
            )


class TestMessagesTable:
    """Test cases for messages table"""

    async def test_create_message_with_valid_data(self, db_helper):
        """Should create message with valid data and foreign key"""
        project_id = await db_helper.create_test_project()
        conversation_id = await db_helper.create_test_conversation(
            TestConversation(project_id=project_id, file_path="/test.jsonl")
        )

        message_data = TestMessage(
            conversation_id=conversation_id,
            role="user",
            content="Test message content",
            token_count=10,
        )

        message_id = await db_helper.create_test_message(message_data)

        # Verify message was created
        assert message_id is not None

        result = await db_helper.conn.fetchrow(
            "SELECT * FROM messages WHERE id = $1", message_id
        )

        assert result["conversation_id"] == conversation_id
        assert result["role"] == message_data.role
        assert result["content"] == message_data.content
        assert result["token_count"] == message_data.token_count
        assert result["depth"] == 0

    async def test_message_role_constraint(self, db_helper):
        """Should enforce valid role values"""
        project_id = await db_helper.create_test_project()
        conversation_id = await db_helper.create_test_conversation(
            TestConversation(project_id=project_id, file_path="/test.jsonl")
        )

        with pytest.raises(asyncpg.CheckViolationError):
            await db_helper.conn.execute(
                """
                INSERT INTO messages (conversation_id, role, content, timestamp)
                VALUES ($1, 'invalid_role', 'content', NOW())
            """,
                conversation_id,
            )

    async def test_message_empty_content_constraint(self, db_helper):
        """Should reject empty message content"""
        project_id = await db_helper.create_test_project()
        conversation_id = await db_helper.create_test_conversation(
            TestConversation(project_id=project_id, file_path="/test.jsonl")
        )

        with pytest.raises(asyncpg.CheckViolationError):
            await db_helper.conn.execute(
                """
                INSERT INTO messages (conversation_id, role, content, timestamp)
                VALUES ($1, 'user', '', NOW())
            """,
                conversation_id,
            )

    async def test_message_token_count_constraint(self, db_helper):
        """Should reject negative token counts"""
        project_id = await db_helper.create_test_project()
        conversation_id = await db_helper.create_test_conversation(
            TestConversation(project_id=project_id, file_path="/test.jsonl")
        )

        with pytest.raises(asyncpg.CheckViolationError):
            await db_helper.conn.execute(
                """
                INSERT INTO messages (conversation_id, role, content, timestamp, token_count)
                VALUES ($1, 'user', 'content', NOW(), -1)
            """,
                conversation_id,
            )

    async def test_message_threading_relationships(self, db_helper):
        """Should handle parent-child message relationships correctly"""
        project_id = await db_helper.create_test_project()
        conversation_id = await db_helper.create_test_conversation(
            TestConversation(project_id=project_id, file_path="/test.jsonl")
        )

        # Create parent message
        parent_data = TestMessage(
            conversation_id=conversation_id, role="user", content="Parent message"
        )
        parent_id = await db_helper.create_test_message(parent_data)

        # Create child message
        child_data = TestMessage(
            conversation_id=conversation_id,
            role="assistant",
            content="Child message",
            parent_id=parent_id,
            depth=1,
        )
        child_id = await db_helper.create_test_message(child_data)

        # Verify relationship
        result = await db_helper.conn.fetchrow(
            "SELECT parent_id, depth FROM messages WHERE id = $1", child_id
        )

        assert result["parent_id"] == parent_id
        assert result["depth"] == 1

    async def test_message_cascade_delete(self, db_helper):
        """Should delete messages when parent conversation is deleted"""
        project_id = await db_helper.create_test_project()
        conversation_id = await db_helper.create_test_conversation(
            TestConversation(project_id=project_id, file_path="/test.jsonl")
        )

        message_id = await db_helper.create_test_message(
            TestMessage(conversation_id=conversation_id, role="user", content="Test")
        )

        # Delete the conversation
        await db_helper.conn.execute(
            "DELETE FROM conversations WHERE id = $1", conversation_id
        )

        # Verify message was also deleted
        result = await db_helper.conn.fetchrow(
            "SELECT id FROM messages WHERE id = $1", message_id
        )
        assert result is None

    async def test_conversation_stats_trigger(self, db_helper):
        """Should update conversation stats when messages are added/removed"""
        project_id = await db_helper.create_test_project()
        conversation_id = await db_helper.create_test_conversation(
            TestConversation(project_id=project_id, file_path="/test.jsonl")
        )

        # Check initial message count
        result = await db_helper.conn.fetchrow(
            "SELECT message_count FROM conversations WHERE id = $1", conversation_id
        )
        assert result["message_count"] == 0

        # Add a message
        message_id = await db_helper.create_test_message(
            TestMessage(conversation_id=conversation_id, role="user", content="Test")
        )

        # Check updated message count
        result = await db_helper.conn.fetchrow(
            "SELECT message_count FROM conversations WHERE id = $1", conversation_id
        )
        assert result["message_count"] == 1

        # Delete the message
        await db_helper.conn.execute("DELETE FROM messages WHERE id = $1", message_id)

        # Check message count decreased
        result = await db_helper.conn.fetchrow(
            "SELECT message_count FROM conversations WHERE id = $1", conversation_id
        )
        assert result["message_count"] == 0


class TestToolCallsTable:
    """Test cases for tool_calls table"""

    async def test_create_tool_call_with_valid_data(self, db_helper):
        """Should create tool call with valid data and foreign key"""
        project_id = await db_helper.create_test_project()
        conversation_id = await db_helper.create_test_conversation(
            TestConversation(project_id=project_id, file_path="/test.jsonl")
        )
        message_id = await db_helper.create_test_message(
            TestMessage(conversation_id=conversation_id, role="user", content="Test")
        )

        tool_call_data = TestToolCall(
            message_id=message_id,
            tool_name="test_tool",
            input_data={"param": "value"},
            output_data="success",
            execution_time_ms=150,
        )

        tool_call_id = await db_helper.create_test_tool_call(tool_call_data)

        # Verify tool call was created
        assert tool_call_id is not None

        result = await db_helper.conn.fetchrow(
            "SELECT * FROM tool_calls WHERE id = $1", tool_call_id
        )

        assert result["message_id"] == message_id
        assert result["tool_name"] == tool_call_data.tool_name
        assert json.loads(result["input_data"]) == tool_call_data.input_data
        assert result["output_data"] == tool_call_data.output_data
        assert result["execution_time_ms"] == tool_call_data.execution_time_ms
        assert result["status"] == "success"

    async def test_tool_call_foreign_key_constraint(self, db_helper):
        """Should reject invalid message_id references"""
        invalid_message_id = uuid4()

        with pytest.raises(asyncpg.ForeignKeyViolationError):
            await db_helper.conn.execute(
                """
                INSERT INTO tool_calls (message_id, tool_name)
                VALUES ($1, 'test_tool')
            """,
                invalid_message_id,
            )

    async def test_tool_call_empty_name_constraint(self, db_helper):
        """Should reject empty tool names"""
        project_id = await db_helper.create_test_project()
        conversation_id = await db_helper.create_test_conversation(
            TestConversation(project_id=project_id, file_path="/test.jsonl")
        )
        message_id = await db_helper.create_test_message(
            TestMessage(conversation_id=conversation_id, role="user", content="Test")
        )

        with pytest.raises(asyncpg.CheckViolationError):
            await db_helper.conn.execute(
                """
                INSERT INTO tool_calls (message_id, tool_name)
                VALUES ($1, '')
            """,
                message_id,
            )

    async def test_tool_call_execution_time_constraint(self, db_helper):
        """Should reject negative execution times"""
        project_id = await db_helper.create_test_project()
        conversation_id = await db_helper.create_test_conversation(
            TestConversation(project_id=project_id, file_path="/test.jsonl")
        )
        message_id = await db_helper.create_test_message(
            TestMessage(conversation_id=conversation_id, role="user", content="Test")
        )

        with pytest.raises(asyncpg.CheckViolationError):
            await db_helper.conn.execute(
                """
                INSERT INTO tool_calls (message_id, tool_name, execution_time_ms)
                VALUES ($1, 'test_tool', -1)
            """,
                message_id,
            )

    async def test_tool_call_status_constraint(self, db_helper):
        """Should enforce valid status values"""
        project_id = await db_helper.create_test_project()
        conversation_id = await db_helper.create_test_conversation(
            TestConversation(project_id=project_id, file_path="/test.jsonl")
        )
        message_id = await db_helper.create_test_message(
            TestMessage(conversation_id=conversation_id, role="user", content="Test")
        )

        with pytest.raises(asyncpg.CheckViolationError):
            await db_helper.conn.execute(
                """
                INSERT INTO tool_calls (message_id, tool_name, status)
                VALUES ($1, 'test_tool', 'invalid_status')
            """,
                message_id,
            )


class TestPerformanceRequirements:
    """Test cases for performance requirements"""

    async def test_query_response_time_projects(self, db_helper):
        """Should query projects in < 50ms"""
        # Create test data
        for i in range(100):
            await db_helper.create_test_project(
                TestProject(name=f"Project {i}", path=f"/path/{i}")
            )

        # Measure query time
        start_time = time.time()
        await db_helper.conn.fetch("SELECT * FROM projects WHERE is_active = true")
        execution_time = (time.time() - start_time) * 1000  # Convert to ms

        assert (
            execution_time < 50
        ), f"Query took {execution_time:.2f}ms, should be < 50ms"

    async def test_bulk_message_insert_performance(self, db_helper):
        """Should handle 1000 message inserts in < 5 seconds"""
        project_id = await db_helper.create_test_project()
        conversation_id = await db_helper.create_test_conversation(
            TestConversation(project_id=project_id, file_path="/test.jsonl")
        )

        # Prepare bulk insert data
        messages = []
        for i in range(1000):
            messages.append(
                (
                    conversation_id,
                    "user" if i % 2 == 0 else "assistant",
                    f"Message content {i}",
                    datetime.now(timezone.utc),
                    10,
                    0,
                    json.dumps({}),
                )
            )

        # Measure bulk insert time
        start_time = time.time()

        async with db_helper.conn.transaction():
            await db_helper.conn.executemany(
                """
                INSERT INTO messages (conversation_id, role, content, timestamp, token_count, depth, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
                messages,
            )

        execution_time = time.time() - start_time

        assert (
            execution_time < 5.0
        ), f"Bulk insert took {execution_time:.2f}s, should be < 5s"

    async def test_conversation_lookup_performance(self, db_helper):
        """Should lookup conversations by project in < 50ms"""
        project_id = await db_helper.create_test_project()

        # Create test conversations
        for i in range(50):
            await db_helper.create_test_conversation(
                TestConversation(project_id=project_id, file_path=f"/test/{i}.jsonl")
            )

        # Measure query time
        start_time = time.time()
        await db_helper.conn.fetch(
            "SELECT * FROM conversations WHERE project_id = $1 ORDER BY last_updated DESC",
            project_id,
        )
        execution_time = (time.time() - start_time) * 1000

        assert (
            execution_time < 50
        ), f"Query took {execution_time:.2f}ms, should be < 50ms"

    async def test_tool_call_analytics_performance(self, db_helper):
        """Should generate tool analytics in < 100ms"""
        # Create test data with tool calls
        project_id = await db_helper.create_test_project()
        conversation_id = await db_helper.create_test_conversation(
            TestConversation(project_id=project_id, file_path="/test.jsonl")
        )

        # Create messages with tool calls
        for i in range(100):
            message_id = await db_helper.create_test_message(
                TestMessage(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=f"Response {i}",
                )
            )

            await db_helper.create_test_tool_call(
                TestToolCall(
                    message_id=message_id,
                    tool_name=f"tool_{i % 10}",  # 10 different tools
                    execution_time_ms=100 + (i % 50),
                )
            )

        # Measure analytics query time
        start_time = time.time()
        await db_helper.conn.fetch(
            """
            SELECT tool_name, COUNT(*), AVG(execution_time_ms)
            FROM tool_calls tc
            JOIN messages m ON tc.message_id = m.id
            JOIN conversations c ON m.conversation_id = c.id
            WHERE c.project_id = $1
            GROUP BY tool_name
        """,
            project_id,
        )
        execution_time = (time.time() - start_time) * 1000

        assert (
            execution_time < 100
        ), f"Analytics query took {execution_time:.2f}ms, should be < 100ms"


class TestFullTextSearch:
    """Test cases for full-text search functionality"""

    async def test_message_content_search(self, db_helper):
        """Should find messages containing search terms"""
        project_id = await db_helper.create_test_project()
        conversation_id = await db_helper.create_test_conversation(
            TestConversation(project_id=project_id, file_path="/test.jsonl")
        )

        # Create messages with searchable content
        searchable_content = [
            "This is about database optimization",
            "Let's discuss API performance",
            "Database queries need optimization",
            "API endpoints should be fast",
        ]

        message_ids = []
        for content in searchable_content:
            message_id = await db_helper.create_test_message(
                TestMessage(
                    conversation_id=conversation_id, role="user", content=content
                )
            )
            message_ids.append(message_id)

        # Test search functionality
        results = await db_helper.conn.fetch(
            """
            SELECT id, content, ts_rank_cd(to_tsvector('english', content), query) as rank
            FROM messages, to_tsquery('english', 'database') as query
            WHERE to_tsvector('english', content) @@ query
            ORDER BY rank DESC
        """
        )

        assert len(results) == 2  # Should find 2 messages with "database"
        assert "database" in results[0]["content"].lower()
        assert "database" in results[1]["content"].lower()

    async def test_search_performance_requirement(self, db_helper):
        """Should perform searches in < 500ms on large dataset"""
        project_id = await db_helper.create_test_project()
        conversation_id = await db_helper.create_test_conversation(
            TestConversation(project_id=project_id, file_path="/test.jsonl")
        )

        # Create large dataset
        for i in range(1000):
            content = f"Message {i} about various topics including performance, optimization, search, and databases"
            await db_helper.create_test_message(
                TestMessage(
                    conversation_id=conversation_id, role="user", content=content
                )
            )

        # Measure search performance
        start_time = time.time()
        await db_helper.conn.fetch(
            """
            SELECT id, content, ts_rank_cd(to_tsvector('english', content), query) as rank
            FROM messages, to_tsquery('english', 'performance & optimization') as query
            WHERE to_tsvector('english', content) @@ query
            ORDER BY rank DESC
            LIMIT 20
        """
        )
        execution_time = (time.time() - start_time) * 1000

        assert (
            execution_time < 500
        ), f"Search took {execution_time:.2f}ms, should be < 500ms"


class TestDataIntegrity:
    """Test cases for data integrity and constraints"""

    async def test_project_deletion_cascade(self, db_helper):
        """Should cascade delete all related data when project is deleted"""
        project_id = await db_helper.create_test_project()
        conversation_id = await db_helper.create_test_conversation(
            TestConversation(project_id=project_id, file_path="/test.jsonl")
        )
        message_id = await db_helper.create_test_message(
            TestMessage(conversation_id=conversation_id, role="user", content="Test")
        )
        tool_call_id = await db_helper.create_test_tool_call(
            TestToolCall(message_id=message_id, tool_name="test_tool")
        )

        # Delete the project
        await db_helper.conn.execute("DELETE FROM projects WHERE id = $1", project_id)

        # Verify all related data was deleted
        conversation_count = await db_helper.conn.fetchval(
            "SELECT COUNT(*) FROM conversations WHERE id = $1", conversation_id
        )
        message_count = await db_helper.conn.fetchval(
            "SELECT COUNT(*) FROM messages WHERE id = $1", message_id
        )
        tool_call_count = await db_helper.conn.fetchval(
            "SELECT COUNT(*) FROM tool_calls WHERE id = $1", tool_call_id
        )

        assert conversation_count == 0
        assert message_count == 0
        assert tool_call_count == 0

    async def test_message_parent_relationship_integrity(self, db_helper):
        """Should handle parent message deletion gracefully"""
        project_id = await db_helper.create_test_project()
        conversation_id = await db_helper.create_test_conversation(
            TestConversation(project_id=project_id, file_path="/test.jsonl")
        )

        # Create parent and child messages
        parent_id = await db_helper.create_test_message(
            TestMessage(conversation_id=conversation_id, role="user", content="Parent")
        )
        child_id = await db_helper.create_test_message(
            TestMessage(
                conversation_id=conversation_id,
                role="assistant",
                content="Child",
                parent_id=parent_id,
                depth=1,
            )
        )

        # Delete parent message
        await db_helper.conn.execute("DELETE FROM messages WHERE id = $1", parent_id)

        # Verify child message parent_id was set to NULL
        result = await db_helper.conn.fetchrow(
            "SELECT parent_id FROM messages WHERE id = $1", child_id
        )
        assert result["parent_id"] is None

    async def test_concurrent_message_insertion(self, db_helper):
        """Should handle concurrent operations safely"""
        project_id = await db_helper.create_test_project()
        conversation_id = await db_helper.create_test_conversation(
            TestConversation(project_id=project_id, file_path="/test.jsonl")
        )

        # Create multiple concurrent message insertions
        async def insert_message(index):
            return await db_helper.create_test_message(
                TestMessage(
                    conversation_id=conversation_id,
                    role="user",
                    content=f"Concurrent message {index}",
                )
            )

        # Run 10 concurrent insertions
        tasks = [insert_message(i) for i in range(10)]
        message_ids = await asyncio.gather(*tasks)

        # Verify all messages were created
        assert len(message_ids) == 10
        assert len(set(message_ids)) == 10  # All IDs should be unique

        # Verify conversation message count was updated correctly
        result = await db_helper.conn.fetchrow(
            "SELECT message_count FROM conversations WHERE id = $1", conversation_id
        )
        assert result["message_count"] == 10
