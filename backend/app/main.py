"""Claude Code Observatory FastAPI Application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from app.api.conversations import router as conversations_router
from app.websocket.endpoints import router as websocket_router
from app.api.projects import router as projects_router


def create_application() -> FastAPI:
    """Create and configure FastAPI application instance."""
    application = FastAPI(
        title="Claude Code Observatory API",
        description="Observability platform for Claude Code interactions",
        version="1.0.0",
    )

    # Add trusted host middleware for security
    application.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["localhost", "127.0.0.1", "*.localhost", "testserver"]
    )

    # Configure CORS for SvelteKit frontend with enhanced security
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # SvelteKit dev server
            "http://127.0.0.1:5173", 
            "http://localhost:3000",  # Alternative dev port
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=[
            "Authorization", 
            "Content-Type", 
            "Accept", 
            "Origin", 
            "X-Requested-With"
        ],
        expose_headers=["X-RateLimit-Remaining", "X-RateLimit-Reset"],
        max_age=3600,  # Cache preflight requests for 1 hour
    )

    # Add security headers middleware
    @application.middleware("http")
    async def add_security_headers(request, call_next):
        """Add security headers to all HTTP responses."""
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # HSTS header for HTTPS (will be ignored on HTTP)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self' ws: wss:; "
            "frame-ancestors 'none';"
        )
        
        return response

    # Include API routers
    application.include_router(conversations_router)
    
    # Include WebSocket router
    application.include_router(websocket_router)
    application.include_router(projects_router)

    return application


# Create application instance
app = create_application()


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint returning API information."""
    return {"message": "Claude Code Observatory API"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}
