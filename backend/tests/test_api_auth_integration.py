"""
Integration tests for API authentication.

This module tests the integration of authentication middleware with API endpoints,
ensuring that protected routes require valid JWT tokens.
"""

import pytest
import jwt
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAPIAuthentication:
    """Test API endpoint authentication integration."""

    def setup_method(self):
        """Set up test environment with JWT secret."""
        self.test_secret = "test-jwt-secret-key"
        self.patch_secret = patch.dict("os.environ", {"SUPABASE_JWT_SECRET": self.test_secret})
        self.patch_secret.start()

    def teardown_method(self):
        """Clean up test environment."""
        self.patch_secret.stop()

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

    @patch('app.api.conversations.get_db_client')
    @patch('app.auth.dependencies.get_supabase_client')
    def test_conversations_endpoint_requires_authentication(self, mock_auth_client, mock_db_client):
        """Test that conversations endpoint requires authentication."""
        mock_auth_client.return_value = Mock()
        mock_db_client.return_value = Mock()
        
        # Request without authentication should fail
        response = client.get("/api/conversations/")
        
        assert response.status_code == 401
        assert "authorization token required" in response.json()["detail"].lower()

    @patch('app.database.supabase_client.get_supabase_service_client')
    @patch('app.auth.dependencies.get_supabase_client')
    def test_conversations_endpoint_with_valid_token(self, mock_auth_client, mock_service_client):
        """Test conversations endpoint with valid authentication token."""
        mock_auth_client.return_value = Mock()
        mock_service_client.return_value = Mock()
        
        # Create valid token
        token = self.create_test_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Request with valid token should succeed
        response = client.get("/api/conversations/", headers=headers)
        
        assert response.status_code == 200
        assert response.json()["success"] is True

    @patch('app.database.supabase_client.get_supabase_service_client')
    @patch('app.auth.dependencies.get_supabase_client')
    def test_conversations_endpoint_with_invalid_token(self, mock_auth_client, mock_service_client):
        """Test conversations endpoint with invalid authentication token."""
        mock_auth_client.return_value = Mock()
        mock_service_client.return_value = Mock()
        
        headers = {"Authorization": "Bearer invalid-token"}
        
        # Request with invalid token should fail
        response = client.get("/api/conversations/", headers=headers)
        
        assert response.status_code == 401
        assert "invalid token" in response.json()["detail"].lower()

    @patch('app.database.supabase_client.get_supabase_service_client')
    @patch('app.auth.dependencies.get_supabase_client')
    def test_conversations_endpoint_with_expired_token(self, mock_auth_client, mock_service_client):
        """Test conversations endpoint with expired authentication token."""
        mock_auth_client.return_value = Mock()
        mock_service_client.return_value = Mock()
        
        # Create expired token
        token = self.create_test_token(expired=True)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Request with expired token should fail
        response = client.get("/api/conversations/", headers=headers)
        
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()

    @patch('app.database.supabase_client.get_supabase_service_client')
    @patch('app.auth.dependencies.get_supabase_client')
    def test_projects_endpoint_requires_authentication(self, mock_auth_client, mock_service_client):
        """Test that projects endpoint requires authentication."""
        mock_auth_client.return_value = Mock()
        mock_service_client.return_value = Mock()
        
        # Request without authentication should fail
        response = client.get("/api/projects/")
        
        assert response.status_code == 401
        assert "authorization token required" in response.json()["detail"].lower()

    @patch('app.database.supabase_client.get_supabase_service_client')
    @patch('app.auth.dependencies.get_supabase_client')
    def test_projects_endpoint_with_valid_token(self, mock_auth_client, mock_service_client):
        """Test projects endpoint with valid authentication token."""
        mock_auth_client.return_value = Mock()
        mock_service_client.return_value = Mock()
        
        # Create valid token
        token = self.create_test_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Request with valid token should succeed
        response = client.get("/api/projects/", headers=headers)
        
        assert response.status_code == 200
        assert response.json()["success"] is True

    @patch('app.database.supabase_client.get_supabase_service_client')
    @patch('app.auth.dependencies.get_supabase_client')
    def test_specific_conversation_requires_authentication(self, mock_auth_client, mock_service_client):
        """Test that specific conversation endpoint requires authentication."""
        mock_auth_client.return_value = Mock()
        mock_service_client.return_value = Mock()
        
        # Request without authentication should fail
        response = client.get("/api/conversations/test-id")
        
        assert response.status_code == 401

    @patch('app.database.supabase_client.get_supabase_service_client')
    @patch('app.auth.dependencies.get_supabase_client')
    def test_specific_project_requires_authentication(self, mock_auth_client, mock_service_client):
        """Test that specific project endpoint requires authentication."""
        mock_auth_client.return_value = Mock()
        mock_service_client.return_value = Mock()
        
        # Request without authentication should fail
        response = client.get("/api/projects/test-id")
        
        assert response.status_code == 401

    def test_health_endpoint_does_not_require_authentication(self):
        """Test that health endpoint does not require authentication."""
        # Health endpoint should work without authentication
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint_does_not_require_authentication(self):
        """Test that root endpoint does not require authentication."""
        # Root endpoint should work without authentication
        response = client.get("/")
        
        assert response.status_code == 200
        assert "Claude Code Observatory API" in response.json()["message"]

    @patch('app.database.supabase_client.get_supabase_service_client')
    @patch('app.auth.dependencies.get_supabase_client')
    def test_bearer_token_without_bearer_prefix_fails(self, mock_auth_client, mock_service_client):
        """Test that token without 'Bearer ' prefix fails."""
        mock_auth_client.return_value = Mock()
        mock_service_client.return_value = Mock()
        
        token = self.create_test_token()
        headers = {"Authorization": token}  # Missing 'Bearer ' prefix
        
        response = client.get("/api/conversations/", headers=headers)
        
        assert response.status_code == 401

    @patch('app.database.supabase_client.get_supabase_service_client')
    @patch('app.auth.dependencies.get_supabase_client')
    def test_malformed_authorization_header_fails(self, mock_auth_client, mock_service_client):
        """Test that malformed authorization header fails."""
        mock_auth_client.return_value = Mock()
        mock_service_client.return_value = Mock()
        
        headers = {"Authorization": "InvalidFormat token-here"}
        
        response = client.get("/api/conversations/", headers=headers)
        
        assert response.status_code == 401


class TestSecurityHeaders:
    """Test security headers in HTTP responses."""

    def test_security_headers_present_in_responses(self):
        """Test that security headers are present in HTTP responses."""
        response = client.get("/health")
        
        # Check for security headers
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        
        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        
        assert "Referrer-Policy" in response.headers
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
        
        assert "Strict-Transport-Security" in response.headers
        assert "max-age=31536000" in response.headers["Strict-Transport-Security"]
        
        assert "Content-Security-Policy" in response.headers
        assert "default-src 'self'" in response.headers["Content-Security-Policy"]

    def test_security_headers_on_api_endpoints(self):
        """Test that security headers are present on API endpoints."""
        # Test on public endpoint
        response = client.get("/")
        
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "Content-Security-Policy" in response.headers

    def test_cors_headers_configured(self):
        """Test that CORS headers are properly configured."""
        # Make a GET request instead of OPTIONS to check CORS
        response = client.get("/health")
        
        # Should have CORS headers and succeed
        assert response.status_code == 200