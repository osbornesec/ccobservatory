"""
Simplified integration tests for API authentication.

Tests the integration of authentication middleware with API endpoints.
"""

import pytest
import jwt
import os
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient


class TestAPIAuthenticationSimple:
    """Test API endpoint authentication with proper mocking."""

    def setup_method(self):
        """Set up test environment with JWT secret."""
        self.test_secret = "test-jwt-secret-key"
        os.environ["SUPABASE_JWT_SECRET"] = self.test_secret

    def teardown_method(self):
        """Clean up test environment."""
        if "SUPABASE_JWT_SECRET" in os.environ:
            del os.environ["SUPABASE_JWT_SECRET"]

    def create_test_token(
        self, 
        user_id: str = "test-user-123",
        email: str = "test@example.com", 
        role: str = "user",
        expired: bool = False
    ) -> str:
        """Create a test JWT token."""
        now = datetime.now(timezone.utc)
        exp_time = now - timedelta(hours=1) if expired else now + timedelta(hours=1)
        
        payload = {
            "sub": user_id,
            "email": email,
            "role": role,
            "aud": "authenticated",
            "exp": int(exp_time.timestamp()),
            "iat": int(now.timestamp()),
            "iss": "https://test.supabase.co/auth/v1"
        }
        
        return jwt.encode(payload, self.test_secret, algorithm="HS256")

    def test_authentication_middleware_validates_tokens(self):
        """Test that authentication middleware properly validates JWT tokens."""
        from app.auth.middleware import validate_jwt_token
        
        # Test valid token
        valid_token = self.create_test_token()
        payload = validate_jwt_token(valid_token)
        assert payload["sub"] == "test-user-123"
        
        # Test invalid token
        from app.auth.middleware import AuthenticationError
        with pytest.raises(AuthenticationError):
            validate_jwt_token("invalid-token")

    def test_auth_dependencies_work_correctly(self):
        """Test that auth dependencies function correctly."""
        from app.auth.dependencies import validate_websocket_token
        from app.auth.middleware import AuthenticationError
        
        # Test valid token
        valid_token = self.create_test_token()
        user_info = validate_websocket_token(valid_token)
        assert user_info["user_id"] == "test-user-123"
        
        # Test invalid token
        with pytest.raises(AuthenticationError):
            validate_websocket_token("invalid-token")

    @patch('app.api.conversations.get_db_client')
    @patch('app.auth.dependencies.get_supabase_client') 
    def test_api_endpoints_require_authentication(self, mock_auth_client, mock_db_client):
        """Test that API endpoints require authentication."""
        from app.main import app
        
        # Setup mocks
        mock_auth_client.return_value = Mock()
        mock_db_client.return_value = Mock()
        
        client = TestClient(app)
        
        # Test without token - should fail
        response = client.get("/api/conversations/")
        assert response.status_code == 401
        
        # Test with valid token - should succeed  
        token = self.create_test_token()
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/conversations/", headers=headers)
        assert response.status_code == 200

    @patch('app.api.projects.get_db_client')
    @patch('app.auth.dependencies.get_supabase_client')
    def test_projects_endpoint_authentication(self, mock_auth_client, mock_db_client):
        """Test projects endpoint authentication."""
        from app.main import app
        
        # Setup mocks
        mock_auth_client.return_value = Mock()
        mock_db_client.return_value = Mock()
        
        client = TestClient(app)
        
        # Test without token - should fail
        response = client.get("/api/projects/")
        assert response.status_code == 401
        
        # Test with valid token - should succeed
        token = self.create_test_token()
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/projects/", headers=headers)
        assert response.status_code == 200

    def test_public_endpoints_work_without_auth(self):
        """Test that public endpoints work without authentication."""
        from app.main import app
        
        client = TestClient(app)
        
        # Health endpoint should work
        response = client.get("/health")
        assert response.status_code == 200
        
        # Root endpoint should work
        response = client.get("/")
        assert response.status_code == 200

    def test_security_headers_are_present(self):
        """Test that security headers are present in responses."""
        from app.main import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        # Check for security headers
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        
        assert "Content-Security-Policy" in response.headers


class TestWebSocketAuthenticationSimple:
    """Test WebSocket authentication functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.test_secret = "test-jwt-secret-key"
        os.environ["SUPABASE_JWT_SECRET"] = self.test_secret

    def teardown_method(self):
        """Clean up test environment."""
        if "SUPABASE_JWT_SECRET" in os.environ:
            del os.environ["SUPABASE_JWT_SECRET"]

    def create_test_token(self, user_id: str = "test-user-123", expired: bool = False) -> str:
        """Create a test JWT token."""
        now = datetime.now(timezone.utc)
        exp_time = now - timedelta(hours=1) if expired else now + timedelta(hours=1)
        
        payload = {
            "sub": user_id,
            "email": "test@example.com",
            "role": "user",
            "exp": int(exp_time.timestamp()),
            "iat": int(now.timestamp()),
        }
        
        return jwt.encode(payload, self.test_secret, algorithm="HS256")

    def test_websocket_token_validation(self):
        """Test WebSocket token validation."""
        from app.auth.dependencies import validate_websocket_token
        from app.auth.middleware import AuthenticationError
        
        # Test valid token
        valid_token = self.create_test_token()
        user_info = validate_websocket_token(valid_token)
        assert user_info["user_id"] == "test-user-123"
        
        # Test expired token
        expired_token = self.create_test_token(expired=True)
        with pytest.raises(AuthenticationError):
            validate_websocket_token(expired_token)
        
        # Test invalid token
        with pytest.raises(AuthenticationError):
            validate_websocket_token("invalid-token")

    def test_connection_manager_handles_user_info(self):
        """Test that connection manager properly handles user information."""
        from app.websocket.connection_manager import ConnectionManager
        from unittest.mock import Mock, AsyncMock
        import asyncio
        
        manager = ConnectionManager()
        mock_websocket = Mock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_text = AsyncMock()
        
        user_info = {
            "user_id": "test-user-123",
            "email": "test@example.com",
            "role": "user"
        }
        
        async def test_connect():
            client_id = await manager.connect(mock_websocket, user_info)
            assert client_id in manager.client_metadata
            assert manager.client_metadata[client_id]["user_info"] == user_info
            return client_id
        
        # Run the async test
        client_id = asyncio.run(test_connect())
        assert client_id is not None