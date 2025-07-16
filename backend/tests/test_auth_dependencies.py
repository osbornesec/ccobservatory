"""
Tests for authentication FastAPI dependencies.

This module tests FastAPI dependency injection functions for authentication,
including current user extraction and permission validation.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.auth.dependencies import (
    get_current_user,
    require_auth,
    require_admin,
    validate_websocket_token,
    get_optional_current_user
)
from app.auth.middleware import AuthenticationError


class TestGetCurrentUser:
    """Test get_current_user dependency function."""

    @pytest.mark.asyncio
    async def test_get_current_user_success(self):
        """Test successful user authentication."""
        # Mock credentials
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid-jwt-token"
        )
        
        # Mock Supabase client
        mock_client = Mock()
        
        # Mock token validation
        mock_token_payload = {
            "sub": "user-123",
            "email": "test@example.com",
            "role": "user"
        }
        
        with patch('app.auth.dependencies.validate_jwt_token') as mock_validate, \
             patch('app.auth.dependencies.extract_user_info') as mock_extract:
            
            mock_validate.return_value = mock_token_payload
            mock_extract.return_value = {
                "user_id": "user-123",
                "email": "test@example.com",
                "role": "user"
            }
            
            result = await get_current_user(credentials, mock_client)
            
            assert result["user_id"] == "user-123"
            assert result["email"] == "test@example.com"
            assert result["role"] == "user"
            
            mock_validate.assert_called_once_with("valid-jwt-token", mock_client)
            mock_extract.assert_called_once_with(mock_token_payload)

    @pytest.mark.asyncio
    async def test_get_current_user_no_credentials(self):
        """Test authentication failure when no credentials provided."""
        mock_client = Mock()
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(None, mock_client)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "authorization token required" in exc_info.value.detail.lower()
        assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Test authentication failure with invalid token."""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid-token"
        )
        mock_client = Mock()
        
        with patch('app.auth.dependencies.validate_jwt_token') as mock_validate:
            mock_validate.side_effect = AuthenticationError("Invalid token")
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials, mock_client)
            
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "invalid token" in exc_info.value.detail.lower()
            assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}

    @pytest.mark.asyncio
    async def test_get_current_user_service_error(self):
        """Test handling of service errors during authentication."""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid-token"
        )
        mock_client = Mock()
        
        with patch('app.auth.dependencies.validate_jwt_token') as mock_validate:
            mock_validate.side_effect = Exception("Service error")
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials, mock_client)
            
            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "authentication service error" in exc_info.value.detail.lower()


class TestRequireAuth:
    """Test require_auth dependency function."""

    @pytest.mark.asyncio
    async def test_require_auth_success(self):
        """Test successful authentication requirement."""
        mock_user = {
            "user_id": "user-123",
            "email": "test@example.com",
            "role": "user"
        }
        
        result = await require_auth(mock_user)
        
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_require_auth_preserves_user_data(self):
        """Test that require_auth preserves all user data."""
        mock_user = {
            "user_id": "user-456",
            "email": "admin@example.com",
            "role": "admin",
            "extra_field": "extra_value"
        }
        
        result = await require_auth(mock_user)
        
        assert result == mock_user
        assert "extra_field" in result


class TestRequireAdmin:
    """Test require_admin dependency function."""

    @pytest.mark.asyncio
    async def test_require_admin_success_with_admin_role(self):
        """Test successful admin requirement with admin role."""
        mock_admin_user = {
            "user_id": "admin-123",
            "email": "admin@example.com",
            "role": "admin"
        }
        
        result = await require_admin(mock_admin_user)
        
        assert result == mock_admin_user

    @pytest.mark.asyncio
    async def test_require_admin_success_with_superadmin_role(self):
        """Test successful admin requirement with superadmin role."""
        mock_superadmin_user = {
            "user_id": "superadmin-123",
            "email": "superadmin@example.com",
            "role": "superadmin"
        }
        
        result = await require_admin(mock_superadmin_user)
        
        assert result == mock_superadmin_user

    @pytest.mark.asyncio
    async def test_require_admin_failure_with_user_role(self):
        """Test admin requirement failure with regular user role."""
        mock_user = {
            "user_id": "user-123",
            "email": "user@example.com",
            "role": "user"
        }
        
        with pytest.raises(HTTPException) as exc_info:
            await require_admin(mock_user)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "admin privileges required" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_require_admin_failure_with_missing_role(self):
        """Test admin requirement failure when role is missing."""
        mock_user = {
            "user_id": "user-123",
            "email": "user@example.com"
            # No role field - should default to 'user'
        }
        
        with pytest.raises(HTTPException) as exc_info:
            await require_admin(mock_user)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_require_admin_failure_with_unknown_role(self):
        """Test admin requirement failure with unknown role."""
        mock_user = {
            "user_id": "user-123",
            "email": "user@example.com",
            "role": "unknown"
        }
        
        with pytest.raises(HTTPException) as exc_info:
            await require_admin(mock_user)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


class TestValidateWebSocketToken:
    """Test WebSocket token validation function."""

    def test_validate_websocket_token_success(self):
        """Test successful WebSocket token validation."""
        test_token = "valid-jwt-token"
        mock_client = Mock()
        
        mock_token_payload = {
            "sub": "user-123",
            "email": "test@example.com",
            "role": "user"
        }
        
        with patch('app.auth.dependencies.validate_jwt_token') as mock_validate, \
             patch('app.auth.dependencies.extract_user_info') as mock_extract:
            
            mock_validate.return_value = mock_token_payload
            mock_extract.return_value = {
                "user_id": "user-123",
                "email": "test@example.com",
                "role": "user"
            }
            
            result = validate_websocket_token(test_token, mock_client)
            
            assert result["user_id"] == "user-123"
            assert result["email"] == "test@example.com"
            assert result["role"] == "user"
            
            mock_validate.assert_called_once_with(test_token, mock_client)
            mock_extract.assert_called_once_with(mock_token_payload)

    def test_validate_websocket_token_authentication_error(self):
        """Test WebSocket token validation with authentication error."""
        test_token = "invalid-token"
        
        with patch('app.auth.dependencies.validate_jwt_token') as mock_validate:
            mock_validate.side_effect = AuthenticationError("Invalid token")
            
            with pytest.raises(AuthenticationError):
                validate_websocket_token(test_token)

    def test_validate_websocket_token_general_error(self):
        """Test WebSocket token validation with general error."""
        test_token = "problematic-token"
        
        with patch('app.auth.dependencies.validate_jwt_token') as mock_validate:
            mock_validate.side_effect = Exception("Service error")
            
            with pytest.raises(AuthenticationError) as exc_info:
                validate_websocket_token(test_token)
            
            assert "websocket authentication failed" in str(exc_info.value).lower()

    def test_validate_websocket_token_without_client(self):
        """Test WebSocket token validation without Supabase client."""
        test_token = "valid-jwt-token"
        
        mock_token_payload = {
            "sub": "user-123",
            "email": "test@example.com",
            "role": "user"
        }
        
        with patch('app.auth.dependencies.validate_jwt_token') as mock_validate, \
             patch('app.auth.dependencies.extract_user_info') as mock_extract:
            
            mock_validate.return_value = mock_token_payload
            mock_extract.return_value = {
                "user_id": "user-123",
                "email": "test@example.com",
                "role": "user"
            }
            
            result = validate_websocket_token(test_token)
            
            assert result["user_id"] == "user-123"
            
            mock_validate.assert_called_once_with(test_token, None)


class TestGetOptionalCurrentUser:
    """Test get_optional_current_user dependency function."""

    def test_get_optional_current_user_success(self):
        """Test successful optional user authentication."""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid-jwt-token"
        )
        mock_client = Mock()
        
        mock_token_payload = {
            "sub": "user-123",
            "email": "test@example.com",
            "role": "user"
        }
        
        with patch('app.auth.dependencies.validate_jwt_token') as mock_validate, \
             patch('app.auth.dependencies.extract_user_info') as mock_extract:
            
            mock_validate.return_value = mock_token_payload
            mock_extract.return_value = {
                "user_id": "user-123",
                "email": "test@example.com",
                "role": "user"
            }
            
            result = get_optional_current_user(credentials, mock_client)
            
            assert result["user_id"] == "user-123"
            assert result["email"] == "test@example.com"
            assert result["role"] == "user"

    def test_get_optional_current_user_no_credentials(self):
        """Test optional authentication with no credentials returns None."""
        mock_client = Mock()
        
        result = get_optional_current_user(None, mock_client)
        
        assert result is None

    def test_get_optional_current_user_invalid_token(self):
        """Test optional authentication with invalid token returns None."""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid-token"
        )
        mock_client = Mock()
        
        with patch('app.auth.dependencies.validate_jwt_token') as mock_validate:
            mock_validate.side_effect = AuthenticationError("Invalid token")
            
            result = get_optional_current_user(credentials, mock_client)
            
            assert result is None

    def test_get_optional_current_user_service_error(self):
        """Test optional authentication with service error returns None."""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid-token"
        )
        mock_client = Mock()
        
        with patch('app.auth.dependencies.validate_jwt_token') as mock_validate:
            mock_validate.side_effect = Exception("Service error")
            
            result = get_optional_current_user(credentials, mock_client)
            
            assert result is None