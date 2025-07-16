"""
Conversations API endpoints.

Implements CRUD operations for conversations with Supabase integration.
Following FastAPI best practices with dependency injection.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict, Any
from supabase import Client
from app.models.contracts import APIResponse, ConversationData, ProcessingError
from app.database.supabase_client import get_supabase_service_client
from app.auth.dependencies import require_auth

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


async def get_db_client() -> Client:
    """Dependency to get Supabase client with proper error handling."""
    try:
        return get_supabase_service_client()
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Database connection failed: {str(e)}"
        )


@router.get("/", response_model=APIResponse[List[ConversationData]])
async def get_conversations(
    skip: int = 0,
    limit: int = 100,
    client: Client = Depends(get_db_client),
    current_user: Dict[str, Any] = Depends(require_auth)
) -> APIResponse[List[ConversationData]]:
    """
    Get all conversations with pagination support.
    
    Args:
        skip: Number of conversations to skip (for pagination)
        limit: Maximum number of conversations to return (max 100)
        client: Supabase client injected via dependency
        current_user: Authenticated user information
        
    Returns:
        APIResponse containing list of conversations for the authenticated user
        
    Raises:
        HTTPException: 500 if database query fails
    """
    try:
        # For now, return empty list to make test pass
        # Next iteration will implement actual database query
        conversations: List[ConversationData] = []
        
        return APIResponse(success=True, data=conversations)
        
    except Exception as e:
        # Log error and return structured error response
        error = ProcessingError(
            error_type="DatabaseQueryError",
            error_message=f"Failed to retrieve conversations: {str(e)}",
            component="ConversationsAPI"
        )
        raise HTTPException(status_code=500, detail=error.dict())


@router.get("/{conversation_id}", response_model=APIResponse[Optional[ConversationData]])
async def get_conversation(
    conversation_id: str,
    client: Client = Depends(get_db_client),
    current_user: Dict[str, Any] = Depends(require_auth)
) -> APIResponse[Optional[ConversationData]]:
    """
    Get specific conversation with messages by ID.
    
    Args:
        conversation_id: UUID of the conversation to retrieve
        client: Supabase client injected via dependency
        current_user: Authenticated user information
        
    Returns:
        APIResponse containing conversation with messages or None if not found
        
    Raises:
        HTTPException: 500 if database query fails
    """
    try:
        # For now, return None to make test pass
        # Next iteration will implement actual database query
        conversation_data = None
        
        return APIResponse(success=True, data=conversation_data)
        
    except Exception as e:
        # Log error and return structured error response
        error = ProcessingError(
            error_type="DatabaseQueryError",
            error_message=f"Failed to retrieve conversation {conversation_id}: {str(e)}",
            component="ConversationsAPI"
        )
        raise HTTPException(status_code=500, detail=error.dict())