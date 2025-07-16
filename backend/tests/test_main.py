"""Tests for FastAPI backend main application."""

from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_fastapi_application_instance_is_created_successfully() -> None:
    """FastAPI application instance should be created with correct configuration."""
    # Given: we import the main application
    from app.main import app

    # When: we check the application instance
    # Then: it should be a FastAPI instance
    assert isinstance(app, FastAPI)
    assert app.title == "Claude Code Observatory API"
    assert app.description == "Observability platform for Claude Code interactions"
    assert app.version == "1.0.0"


def test_application_can_be_imported_from_app_main_module() -> None:
    """Application should be importable from app.main module without errors."""
    # Given: we attempt to import the main application module
    # When: we import from app.main
    try:
        from app.main import app, create_application

        import_success = True
    except ImportError:
        import_success = False

    # Then: import should succeed and app should be accessible
    assert import_success is True
    assert app is not None
    assert callable(create_application)


def test_root_endpoint_returns_success_response() -> None:
    """Root endpoint ('/') should return success response with correct message."""
    # Given: a TestClient with the FastAPI app
    from app.main import app

    client = TestClient(app)

    # When: we make a GET request to the root endpoint
    response = client.get("/")

    # Then: response should be successful with correct content
    assert response.status_code == 200
    assert response.json() == {"message": "Claude Code Observatory API"}


def test_health_check_endpoint_returns_healthy_status() -> None:
    """Health check endpoint ('/health') should return healthy status."""
    # Given: a TestClient with the FastAPI app
    from app.main import app

    client = TestClient(app)

    # When: we make a GET request to the health endpoint
    response = client.get("/health")

    # Then: response should be successful with healthy status
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
