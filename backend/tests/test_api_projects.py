"""
Test suite for Projects API endpoints.

Following Canon TDD - implementing one test at a time.
Current test: GET /api/projects returns list of projects
"""
import pytest
from unittest.mock import Mock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.main import app
from app.models.contracts import APIResponse, Project
from app.api.projects import get_db_client

# Mock Supabase client for testing
def get_mock_db_client():
    """Mock database client for testing."""
    mock_client = Mock()
    return mock_client

# Override dependency for testing
app.dependency_overrides[get_db_client] = get_mock_db_client

# Test client for FastAPI
client = TestClient(app)


class TestProjectsAPI:
    """Test scenarios for Projects API functionality."""
    
    def test_get_projects_returns_list(self):
        """Should return list of projects in APIResponse format."""
        # Given: API is running and projects endpoint exists
        # When: GET request is made to /api/projects
        response = client.get("/api/projects")
        
        # Then: Should return 200 status with APIResponse wrapper
        assert response.status_code == 200
        
        # And: Response should be in APIResponse format
        response_data = response.json()
        assert "success" in response_data
        assert "data" in response_data
        assert response_data["success"] is True
        
        # And: Data should be a list (could be empty)
        assert isinstance(response_data["data"], list)
    
    def test_get_project_by_id_returns_project(self):
        """Should return specific project in APIResponse format."""
        # Given: API is running and project ID endpoint exists
        project_id = "123e4567-e89b-12d3-a456-426614174000"
        
        # When: GET request is made to /api/projects/{id}
        response = client.get(f"/api/projects/{project_id}")
        
        # Then: Should return 200 status with APIResponse wrapper
        assert response.status_code == 200
        
        # And: Response should be in APIResponse format
        response_data = response.json()
        assert "success" in response_data
        assert "data" in response_data
        assert response_data["success"] is True
        
        # And: Data should be a project object (or null if not found)
        # For now, allowing None for non-existent projects
        data = response_data["data"]
        assert data is None or isinstance(data, dict)