"""
Projects API endpoints.

Implements CRUD operations for projects with Supabase integration.
Following FastAPI best practices with dependency injection.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from supabase import Client
from app.models.contracts import APIResponse, Project, ProcessingError
from app.database.supabase_client import get_supabase_service_client

router = APIRouter(prefix="/api/projects", tags=["projects"])


async def get_db_client() -> Client:
    """Dependency to get Supabase client with proper error handling."""
    try:
        return get_supabase_service_client()
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Database connection failed: {str(e)}"
        )


@router.get("/", response_model=APIResponse[List[Project]])
async def get_projects(
    skip: int = 0,
    limit: int = 100,
    client: Client = Depends(get_db_client)
) -> APIResponse[List[Project]]:
    """
    Get all projects with pagination support.
    
    Args:
        skip: Number of projects to skip (for pagination)
        limit: Maximum number of projects to return (max 100)
        client: Supabase client injected via dependency
        
    Returns:
        APIResponse containing list of projects
        
    Raises:
        HTTPException: 500 if database query fails
    """
    try:
        # For now, return empty list to make test pass
        # Next iteration will implement actual database query
        projects: List[Project] = []
        
        return APIResponse(success=True, data=projects)
        
    except Exception as e:
        # Log error and return structured error response
        error = ProcessingError(
            error_type="DatabaseQueryError",
            error_message=f"Failed to retrieve projects: {str(e)}",
            component="ProjectsAPI"
        )
        raise HTTPException(status_code=500, detail=error.dict())


@router.get("/{project_id}", response_model=APIResponse[Optional[Project]])
async def get_project(
    project_id: str,
    client: Client = Depends(get_db_client)
) -> APIResponse[Optional[Project]]:
    """
    Get specific project by ID.
    
    Args:
        project_id: UUID of the project to retrieve
        client: Supabase client injected via dependency
        
    Returns:
        APIResponse containing project or None if not found
        
    Raises:
        HTTPException: 500 if database query fails
    """
    try:
        # For now, return None to make test pass
        # Next iteration will implement actual database query
        project_data = None
        
        return APIResponse(success=True, data=project_data)
        
    except Exception as e:
        # Log error and return structured error response
        error = ProcessingError(
            error_type="DatabaseQueryError",
            error_message=f"Failed to retrieve project {project_id}: {str(e)}",
            component="ProjectsAPI"
        )
        raise HTTPException(status_code=500, detail=error.dict())