"""
Authentication module for Claude Code Observatory.

This module provides JWT authentication and authorization functionality
integrated with Supabase Auth for secure API and WebSocket access.
"""

from .middleware import AuthenticationError, validate_jwt_token
from .dependencies import get_current_user, require_auth

__all__ = [
    "AuthenticationError",
    "validate_jwt_token", 
    "get_current_user",
    "require_auth"
]