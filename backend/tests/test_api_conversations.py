"""
Test suite for Conversations API endpoints.

Following Canon TDD - implementing one test at a time.
Current test: GET /api/conversations returns list of conversations
"""
import pytest
from unittest.mock import Mock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.main import app
from app.models.contracts import APIResponse, ConversationData
from app.api.conversations import get_db_client

# Mock Supabase client for testing
def get_mock_db_client():
    """Mock database client for testing."""
    mock_client = Mock()
    return mock_client

# Override dependency for testing
app.dependency_overrides[get_db_client] = get_mock_db_client

# Test client for FastAPI
client = TestClient(app)


class TestConversationsAPI:
    """Test scenarios for Conversations API functionality."""
    
    def test_get_conversations_returns_list(self):
        """Should return list of conversations in APIResponse format."""
        # Given: API is running and conversations endpoint exists
        # When: GET request is made to /api/conversations
        response = client.get("/api/conversations")
        
        # Then: Should return 200 status with APIResponse wrapper
        assert response.status_code == 200
        
        # And: Response should be in APIResponse format
        response_data = response.json()
        assert "success" in response_data
        assert "data" in response_data
        assert response_data["success"] is True
        
        # And: Data should be a list (could be empty)
        assert isinstance(response_data["data"], list)