"""Claude Code Observatory FastAPI Application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.conversations import router as conversations_router


def create_application() -> FastAPI:
    """Create and configure FastAPI application instance."""
    application = FastAPI(
        title="Claude Code Observatory API",
        description="Observability platform for Claude Code interactions",
        version="1.0.0",
    )

    # Configure CORS for SvelteKit frontend
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],  # SvelteKit dev server
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routers
    application.include_router(conversations_router)

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
