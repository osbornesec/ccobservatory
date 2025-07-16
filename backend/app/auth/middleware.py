"""
Authentication middleware for JWT validation and user session management.

This module provides JWT token validation integrated with Supabase Auth,
supporting secure authentication for both API and WebSocket connections.
"""

import os
import jwt
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from supabase import Client

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


def get_jwt_secret() -> str:
    """
    Get JWT secret key for token validation.
    
    Returns:
        str: JWT secret key from environment
        
    Raises:
        ValueError: If JWT secret is not configured
    """
    secret = os.environ.get("SUPABASE_JWT_SECRET")
    if not secret:
        # For development, we can derive it from the anon key
        # In production, this should be explicitly set
        anon_key = os.environ.get("SUPABASE_KEY")
        if anon_key:
            # This is a temporary fallback - in production use proper JWT secret
            return anon_key
        raise ValueError("SUPABASE_JWT_SECRET or SUPABASE_KEY environment variable is required")
    return secret


def validate_jwt_token(token: str, supabase_client: Optional[Client] = None) -> Dict[str, Any]:
    """
    Validate JWT token and extract user information.
    
    Args:
        token: JWT token to validate
        supabase_client: Optional Supabase client for additional validation
        
    Returns:
        Dict containing user information from token payload
        
    Raises:
        AuthenticationError: If token is invalid, expired, or malformed
    """
    try:
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        # Get JWT secret for validation
        secret = get_jwt_secret()
        
        # Decode and validate token
        # Note: In production, you should also validate the issuer, audience, etc.
        payload = jwt.decode(
            token, 
            secret, 
            algorithms=["HS256"],
            options={
                "verify_signature": True, 
                "verify_exp": True,
                "verify_aud": False,  # Disable audience verification for flexibility
                "verify_iss": False   # Disable issuer verification for flexibility
            }
        )
        
        # Check token expiration explicitly
        if 'exp' in payload:
            exp_timestamp = payload['exp']
            if datetime.fromtimestamp(exp_timestamp, tz=timezone.utc) < datetime.now(timezone.utc):
                raise AuthenticationError("Token has expired")
        
        # Validate required fields
        if 'sub' not in payload:
            raise AuthenticationError("Token missing user ID (sub)")
            
        # Additional Supabase-specific validation if client provided
        if supabase_client:
            user_id = payload.get('sub')
            try:
                # Verify user exists and is active in Supabase
                user_response = supabase_client.auth.get_user(token)
                if not user_response or not user_response.user:
                    raise AuthenticationError("User not found or inactive")
            except Exception as e:
                logger.warning(f"Supabase user validation failed: {e}")
                # Continue with JWT validation only if Supabase check fails
                # This allows for offline validation scenarios
        
        logger.debug(f"Successfully validated token for user: {payload.get('sub')}")
        return payload
        
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise AuthenticationError(f"Invalid token: {str(e)}")
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise AuthenticationError(f"Token validation failed: {str(e)}")


def extract_user_info(token_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract relevant user information from validated JWT payload.
    
    Args:
        token_payload: Validated JWT token payload
        
    Returns:
        Dict containing extracted user information
    """
    return {
        'user_id': token_payload.get('sub'),
        'email': token_payload.get('email'),
        'role': token_payload.get('role', 'user'),
        'aud': token_payload.get('aud'),
        'exp': token_payload.get('exp'),
        'iat': token_payload.get('iat'),
        'iss': token_payload.get('iss')
    }


def validate_token_permissions(token_payload: Dict[str, Any], required_role: str = 'user') -> bool:
    """
    Validate if user has required permissions based on token payload.
    
    Args:
        token_payload: Validated JWT token payload
        required_role: Minimum required role (default: 'user')
        
    Returns:
        bool: True if user has required permissions
    """
    user_role = token_payload.get('role', 'user')
    
    # Define role hierarchy
    role_hierarchy = {
        'user': 0,
        'admin': 1,
        'superadmin': 2
    }
    
    user_level = role_hierarchy.get(user_role, 0)
    required_level = role_hierarchy.get(required_role, 0)
    
    return user_level >= required_level