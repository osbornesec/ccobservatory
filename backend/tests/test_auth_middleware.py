"""
Tests for authentication middleware and JWT validation.

This module tests JWT token validation, authentication middleware,
and integration with Supabase Auth.
"""

import pytest
import jwt
import os
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch, MagicMock

from app.auth.middleware import (
    validate_jwt_token,
    extract_user_info,
    validate_token_permissions,
    AuthenticationError,
    get_jwt_secret
)


class TestJWTValidation:
    """Test JWT token validation functionality."""

    def setup_method(self):
        """Set up test environment."""
        # Set test JWT secret
        self.test_secret = "test-jwt-secret-key"
        self.patch_secret = patch.dict(os.environ, {"SUPABASE_JWT_SECRET": self.test_secret})
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

    def test_validate_valid_token_success(self):
        """Test successful validation of valid JWT token."""
        token = self.create_test_token()
        
        result = validate_jwt_token(token)
        
        assert result["sub"] == "test-user-123"
        assert result["email"] == "test@example.com"
        assert result["role"] == "user"

    def test_validate_token_with_bearer_prefix(self):
        """Test token validation with 'Bearer ' prefix."""
        token = self.create_test_token()
        bearer_token = f"Bearer {token}"
        
        result = validate_jwt_token(bearer_token)
        
        assert result["sub"] == "test-user-123"

    def test_validate_expired_token_raises_error(self):
        """Test that expired token raises AuthenticationError."""
        token = self.create_test_token(expired=True)
        
        with pytest.raises(AuthenticationError) as exc_info:
            validate_jwt_token(token)
        
        assert "expired" in str(exc_info.value).lower()

    def test_validate_invalid_token_raises_error(self):
        """Test that invalid token raises AuthenticationError."""
        invalid_token = "invalid.jwt.token"
        
        with pytest.raises(AuthenticationError) as exc_info:
            validate_jwt_token(invalid_token)
        
        assert "invalid token" in str(exc_info.value).lower()

    def test_validate_token_without_sub_raises_error(self):
        """Test that token without user ID raises AuthenticationError."""
        # Create token without 'sub' field
        payload = {
            "email": "test@example.com",
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())
        }
        token = jwt.encode(payload, self.test_secret, algorithm="HS256")
        
        with pytest.raises(AuthenticationError) as exc_info:
            validate_jwt_token(token)
        
        assert "missing user id" in str(exc_info.value).lower()

    def test_validate_token_with_wrong_secret_raises_error(self):
        """Test that token signed with wrong secret raises AuthenticationError."""
        wrong_secret = "wrong-secret"
        payload = {
            "sub": "test-user-123",
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())
        }
        token = jwt.encode(payload, wrong_secret, algorithm="HS256")
        
        with pytest.raises(AuthenticationError):
            validate_jwt_token(token)

    @patch('app.auth.middleware.logger')
    def test_validate_token_with_supabase_client_success(self, mock_logger):
        """Test token validation with successful Supabase client validation."""
        token = self.create_test_token()
        
        # Mock Supabase client
        mock_client = Mock()
        mock_user = Mock()
        mock_user.user = Mock()
        mock_client.auth.get_user.return_value = mock_user
        
        result = validate_jwt_token(token, mock_client)
        
        assert result["sub"] == "test-user-123"
        mock_client.auth.get_user.assert_called_once_with(token)

    @patch('app.auth.middleware.logger')
    def test_validate_token_with_supabase_client_failure_continues(self, mock_logger):
        """Test that Supabase validation failure doesn't block JWT validation."""
        token = self.create_test_token()
        
        # Mock Supabase client that raises exception
        mock_client = Mock()
        mock_client.auth.get_user.side_effect = Exception("Supabase error")
        
        # Should still succeed with JWT validation only
        result = validate_jwt_token(token, mock_client)
        
        assert result["sub"] == "test-user-123"
        mock_logger.warning.assert_called_once()


class TestUserInfoExtraction:
    """Test user information extraction from JWT payload."""

    def test_extract_user_info_with_all_fields(self):
        """Test extracting user info with all available fields."""
        payload = {
            "sub": "user-123",
            "email": "test@example.com",
            "role": "admin",
            "aud": "authenticated",
            "exp": 1234567890,
            "iat": 1234567890,
            "iss": "https://test.supabase.co/auth/v1"
        }
        
        result = extract_user_info(payload)
        
        assert result["user_id"] == "user-123"
        assert result["email"] == "test@example.com"
        assert result["role"] == "admin"
        assert result["aud"] == "authenticated"
        assert result["exp"] == 1234567890
        assert result["iat"] == 1234567890
        assert result["iss"] == "https://test.supabase.co/auth/v1"

    def test_extract_user_info_with_minimal_fields(self):
        """Test extracting user info with minimal required fields."""
        payload = {
            "sub": "user-123"
        }
        
        result = extract_user_info(payload)
        
        assert result["user_id"] == "user-123"
        assert result["email"] is None
        assert result["role"] == "user"  # Default role
        assert result["aud"] is None


class TestTokenPermissions:
    """Test token permission validation."""

    def test_validate_user_role_permissions(self):
        """Test permission validation for user role."""
        payload = {"role": "user"}
        
        # User can access user-level resources
        assert validate_token_permissions(payload, "user") is True
        
        # User cannot access admin-level resources
        assert validate_token_permissions(payload, "admin") is False

    def test_validate_admin_role_permissions(self):
        """Test permission validation for admin role."""
        payload = {"role": "admin"}
        
        # Admin can access user-level resources
        assert validate_token_permissions(payload, "user") is True
        
        # Admin can access admin-level resources
        assert validate_token_permissions(payload, "admin") is True
        
        # Admin cannot access superadmin-level resources
        assert validate_token_permissions(payload, "superadmin") is False

    def test_validate_superadmin_role_permissions(self):
        """Test permission validation for superadmin role."""
        payload = {"role": "superadmin"}
        
        # Superadmin can access all levels
        assert validate_token_permissions(payload, "user") is True
        assert validate_token_permissions(payload, "admin") is True
        assert validate_token_permissions(payload, "superadmin") is True

    def test_validate_permissions_with_missing_role(self):
        """Test permission validation when role is missing (defaults to user)."""
        payload = {}
        
        # Should default to user permissions
        assert validate_token_permissions(payload, "user") is True
        assert validate_token_permissions(payload, "admin") is False

    def test_validate_permissions_with_unknown_role(self):
        """Test permission validation with unknown role."""
        payload = {"role": "unknown"}
        
        # Unknown role should default to user level (0)
        assert validate_token_permissions(payload, "user") is True
        assert validate_token_permissions(payload, "admin") is False


class TestJWTSecretConfiguration:
    """Test JWT secret key configuration."""

    def test_get_jwt_secret_from_environment(self):
        """Test getting JWT secret from environment variable."""
        test_secret = "test-jwt-secret"
        
        with patch.dict(os.environ, {"SUPABASE_JWT_SECRET": test_secret}):
            result = get_jwt_secret()
            assert result == test_secret

    def test_get_jwt_secret_fallback_to_anon_key(self):
        """Test fallback to anon key when JWT secret not set."""
        test_anon_key = "test-anon-key"
        
        with patch.dict(os.environ, {"SUPABASE_KEY": test_anon_key}, clear=True):
            result = get_jwt_secret()
            assert result == test_anon_key

    def test_get_jwt_secret_raises_error_when_not_configured(self):
        """Test error when neither JWT secret nor anon key is configured."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                get_jwt_secret()
            
            assert "required" in str(exc_info.value).lower()


class TestAuthenticationErrorHandling:
    """Test authentication error handling scenarios."""

    def test_authentication_error_creation(self):
        """Test creating AuthenticationError with message."""
        error_message = "Token validation failed"
        error = AuthenticationError(error_message)
        
        assert str(error) == error_message
        assert isinstance(error, Exception)

    def test_authentication_error_inheritance(self):
        """Test that AuthenticationError is proper Exception subclass."""
        error = AuthenticationError("test")
        
        assert isinstance(error, Exception)
        assert isinstance(error, AuthenticationError)