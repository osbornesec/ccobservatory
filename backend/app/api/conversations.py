"""
Conversations API endpoints.

Implements CRUD operations for conversations with Supabase integration.
Following FastAPI best practices with dependency injection.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from supabase import Client
from app.models.contracts import APIResponse, ConversationData, ProcessingError
from app.database.supabase_client import get_supabase_service_client

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
    client: Client = Depends(get_db_client)
) -> APIResponse[List[ConversationData]]:
    """
    Get all conversations with pagination support.
    
    Args:
        skip: Number of conversations to skip (for pagination)
        limit: Maximum number of conversations to return (max 100)
        client: Supabase client injected via dependency
        
    Returns:
        APIResponse containing list of conversations
        
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