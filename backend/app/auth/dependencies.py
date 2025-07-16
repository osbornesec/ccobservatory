"""
FastAPI dependencies for authentication and authorization.

This module provides dependency injection functions for authenticating
API requests and WebSocket connections using JWT tokens.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
from supabase import Client

from .middleware import validate_jwt_token, extract_user_info, AuthenticationError
from app.database.supabase_client import get_supabase_client

# FastAPI security scheme for Bearer token authentication
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    supabase_client: Client = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    FastAPI dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token credentials
        supabase_client: Supabase client for additional validation
        
    Returns:
        Dict containing authenticated user information
        
    Raises:
        HTTPException: 401 if authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Validate JWT token
        token_payload = validate_jwt_token(credentials.credentials, supabase_client)
        
        # Extract user information
        user_info = extract_user_info(token_payload)
        
        return user_info
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )


async def require_auth(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    FastAPI dependency that requires authentication.
    
    This is an alias for get_current_user but with a more explicit name
    for routes that simply require any authenticated user.
    
    Args:
        current_user: Current authenticated user from get_current_user
        
    Returns:
        Dict containing authenticated user information
    """
    return current_user


async def require_admin(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    FastAPI dependency that requires admin role.
    
    Args:
        current_user: Current authenticated user from get_current_user
        
    Returns:
        Dict containing authenticated admin user information
        
    Raises:
        HTTPException: 403 if user is not an admin
    """
    user_role = current_user.get('role', 'user')
    
    if user_role not in ['admin', 'superadmin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return current_user


def validate_websocket_token(token: str, supabase_client: Optional[Client] = None) -> Dict[str, Any]:
    """
    Validate JWT token for WebSocket connections.
    
    This is a synchronous function suitable for WebSocket authentication
    before connection acceptance.
    
    Args:
        token: JWT token to validate
        supabase_client: Optional Supabase client for additional validation
        
    Returns:
        Dict containing user information
        
    Raises:
        AuthenticationError: If authentication fails
    """
    try:
        # Validate JWT token
        token_payload = validate_jwt_token(token, supabase_client)
        
        # Extract user information
        user_info = extract_user_info(token_payload)
        
        return user_info
        
    except AuthenticationError:
        # Re-raise authentication errors
        raise
    except Exception as e:
        raise AuthenticationError(f"WebSocket authentication failed: {str(e)}")


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    supabase_client: Client = Depends(get_supabase_client)
) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency to optionally get current user.
    
    This dependency does not raise an error if no authentication is provided,
    making it suitable for endpoints that can work with or without authentication.
    
    Args:
        credentials: HTTP Bearer token credentials (optional)
        supabase_client: Supabase client for validation
        
    Returns:
        Dict containing user information if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        # Validate JWT token
        token_payload = validate_jwt_token(credentials.credentials, supabase_client)
        
        # Extract user information
        user_info = extract_user_info(token_payload)
        
        return user_info
        
    except AuthenticationError:
        # Return None instead of raising error for optional auth
        return None
    except Exception:
        # Return None for any other errors in optional auth
        return None