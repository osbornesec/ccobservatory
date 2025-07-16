"""
Test Supabase configuration and dependency setup.

This module tests that Supabase dependencies are properly installed and configured
without instantiating actual clients to avoid network calls and version conflicts.
"""

import os
import pytest
from unittest.mock import patch, MagicMock


class TestSupabaseConfiguration:
    """Test cases for Supabase configuration and dependencies."""

    def test_supabase_imports_available(self):
        """Test that all Supabase modules can be imported."""
        # Test main supabase import
        try:
            import supabase

            assert supabase is not None
        except ImportError:
            pytest.fail("supabase package not available")

        # Test create_client function
        try:
            from supabase import create_client

            assert create_client is not None
        except ImportError:
            pytest.fail("create_client function not available")

        # Test Client class
        try:
            from supabase import Client

            assert Client is not None
        except ImportError:
            pytest.fail("Client class not available")

    def test_supabase_dependencies_available(self):
        """Test that required Supabase dependencies are available."""
        dependencies = ["gotrue", "postgrest", "realtime", "storage3", "supafunc"]

        for dep in dependencies:
            try:
                __import__(dep)
            except ImportError:
                pytest.fail(f"Required Supabase dependency '{dep}' not available")

    def test_environment_variable_handling(self):
        """Test environment variable configuration patterns."""
        # Test missing environment variables
        with patch.dict(os.environ, {}, clear=True):
            url = os.environ.get("SUPABASE_URL")
            key = os.environ.get("SUPABASE_KEY")

            assert url is None
            assert key is None

        # Test with mock environment variables
        test_env = {
            "SUPABASE_URL": "https://test-project.supabase.co",
            "SUPABASE_KEY": "test-key",
            "SUPABASE_SERVICE_ROLE_KEY": "test-service-key",
        }

        with patch.dict(os.environ, test_env):
            url = os.environ.get("SUPABASE_URL")
            key = os.environ.get("SUPABASE_KEY")
            service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

            assert url == test_env["SUPABASE_URL"]
            assert key == test_env["SUPABASE_KEY"]
            assert service_key == test_env["SUPABASE_SERVICE_ROLE_KEY"]

    def test_supabase_client_manager_import(self):
        """Test that our custom client manager can be imported."""
        try:
            from app.database.supabase_client import SupabaseClientManager

            assert SupabaseClientManager is not None
        except ImportError:
            pytest.fail("SupabaseClientManager not available")

    def test_supabase_config_class(self):
        """Test the SupabaseConfig class."""
        from app.database.supabase_client import SupabaseConfig

        # Test with empty environment
        with patch.dict(os.environ, {}, clear=True):
            config = SupabaseConfig()
            assert config.url is None
            assert config.key is None
            assert config.service_role_key is None
            assert not config.validate()

        # Test with valid environment
        test_env = {
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_KEY": "test-key",
        }

        with patch.dict(os.environ, test_env):
            config = SupabaseConfig()
            assert config.url == test_env["SUPABASE_URL"]
            assert config.key == test_env["SUPABASE_KEY"]
            assert config.validate()

    def test_helper_functions_available(self):
        """Test that helper functions are available."""
        try:
            from app.database.supabase_client import (
                get_supabase_client,
                get_supabase_service_client,
                shutdown_supabase,
            )

            assert get_supabase_client is not None
            assert get_supabase_service_client is not None
            assert shutdown_supabase is not None
        except ImportError:
            pytest.fail("Helper functions not available")

    @pytest.mark.asyncio
    async def test_pytest_asyncio_working(self):
        """Test that pytest-asyncio is working correctly."""
        import asyncio

        # Simple async test to verify pytest-asyncio setup
        await asyncio.sleep(0.001)
        assert True

    def test_additional_testing_dependencies(self):
        """Test that additional testing dependencies are available."""
        dependencies = ["aiofiles", "asyncpg", "psycopg2"]

        for dep in dependencies:
            try:
                __import__(dep)
            except ImportError:
                pytest.fail(f"Testing dependency '{dep}' not available")

    def test_environment_template_exists(self):
        """Test that environment template file exists."""
        import os

        template_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "env.template"
        )
        assert os.path.exists(template_path), "env.template file not found"

    def test_supabase_version_compatibility(self):
        """Test that installed Supabase version is compatible."""
        import supabase

        version = getattr(supabase, "__version__", None)

        # We expect at least version 2.3.0 or higher
        if version:
            major, minor = map(int, version.split(".")[:2])
            assert major >= 2 and minor >= 3, f"Supabase version {version} too old"

    def test_mock_client_creation_pattern(self):
        """Test the pattern for mocking Supabase client creation."""
        with patch("app.database.supabase_client.create_client") as mock_create:
            mock_client = MagicMock()
            mock_client.auth = MagicMock()
            mock_client.table = MagicMock()
            mock_create.return_value = mock_client

            # Test the import and mock pattern
            from app.database.supabase_client import SupabaseClientManager

            manager = SupabaseClientManager()
            manager.config.url = "https://test.supabase.co"
            manager.config.key = "test-key"

            # This should work with proper mocking
            client = manager.get_client()
            assert client is not None
            assert hasattr(client, "auth")
            assert hasattr(client, "table")
