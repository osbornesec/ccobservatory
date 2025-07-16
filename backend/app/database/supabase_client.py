"""
Supabase client initialization and configuration.

This module provides a centralized way to initialize and configure the Supabase client
for the Claude Code Observatory project. Follows the patterns from the supabase-py documentation.
"""

import os
import logging
from typing import Optional
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class SupabaseConfig:
    """Configuration class for Supabase client settings."""

    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_KEY")
        self.service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    def validate(self) -> bool:
        """Validate that required configuration is present."""
        if not self.url:
            logger.error("SUPABASE_URL environment variable is required")
            return False

        if not self.key:
            logger.error("SUPABASE_KEY environment variable is required")
            return False

        return True


class SupabaseClientManager:
    """Manager class for Supabase client lifecycle."""

    def __init__(self):
        self._client: Optional[Client] = None
        self._service_client: Optional[Client] = None
        self.config = SupabaseConfig()

    def get_client(self) -> Client:
        """
        Get the standard Supabase client (anon key).

        Returns:
            Client: Initialized Supabase client

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.config.validate():
            raise ValueError("Invalid Supabase configuration")

        if self._client is None:
            logger.info("Initializing Supabase client")
            self._client = create_client(self.config.url, self.config.key)

        return self._client

    def get_service_client(self) -> Client:
        """
        Get the service role Supabase client (service role key).

        Use this for server-side operations that require elevated privileges.

        Returns:
            Client: Initialized Supabase client with service role

        Raises:
            ValueError: If service role key is not configured
        """
        if not self.config.service_role_key:
            raise ValueError(
                "SUPABASE_SERVICE_ROLE_KEY environment variable is required"
            )

        if self._service_client is None:
            logger.info("Initializing Supabase service client")
            self._service_client = create_client(
                self.config.url, self.config.service_role_key
            )

        return self._service_client

    def shutdown(self):
        """
        Properly shutdown Supabase clients.

        This ensures proper cleanup of resources.
        """
        if self._client:
            logger.info("Shutting down Supabase client")
            self._client.auth.sign_out()
            self._client = None

        if self._service_client:
            logger.info("Shutting down Supabase service client")
            self._service_client.auth.sign_out()
            self._service_client = None


# Global client manager instance
_client_manager = SupabaseClientManager()


def get_supabase_client() -> Client:
    """
    Get the default Supabase client.

    This is the main entry point for accessing Supabase throughout the application.

    Returns:
        Client: Initialized Supabase client
    """
    return _client_manager.get_client()


def get_supabase_service_client() -> Client:
    """
    Get the Supabase service client for elevated operations.

    Returns:
        Client: Initialized Supabase client with service role
    """
    return _client_manager.get_service_client()


def shutdown_supabase():
    """Shutdown all Supabase clients."""
    _client_manager.shutdown()


# Example usage patterns from the documentation
def example_basic_usage():
    """Example of basic Supabase usage patterns."""
    # Initialize client (following documented pattern)
    client = get_supabase_client()

    # Table operations (from documentation examples)
    # Select data
    data = client.table("countries").select("*").eq("country", "IL").execute()

    # Insert data
    data = client.table("countries").insert({"name": "Germany"}).execute()

    # Update data
    data = (
        client.table("countries")
        .update({"country": "Indonesia", "capital_city": "Jakarta"})
        .eq("id", 1)
        .execute()
    )

    # Upsert data
    country = {"country": "United Kingdom", "capital_city": "London"}
    data = client.table("countries").upsert(country).execute()

    # Delete data
    data = client.table("countries").delete().eq("id", 1).execute()


def example_auth_usage():
    """Example of authentication usage patterns."""
    client = get_supabase_client()

    # Sign up new user
    user = client.auth.sign_up({"email": "user@example.com", "password": "password123"})

    # Sign in existing user
    user = client.auth.sign_in_with_password(
        {"email": "user@example.com", "password": "password123"}
    )

    # Sign out (important for cleanup)
    client.auth.sign_out()


def example_storage_usage():
    """Example of storage usage patterns."""
    client = get_supabase_client()

    bucket_name = "photos"

    # Upload file
    # new_file = getUserFile()  # Your file data
    # data = client.storage.from_(bucket_name).upload("/user1/profile.png", new_file)

    # Download file
    data = client.storage.from_(bucket_name).download("photo1.png")

    # List files
    data = client.storage.from_(bucket_name).list()

    # Remove files
    data = client.storage.from_(bucket_name).remove(["old_photo.png", "image5.jpg"])

    # Move files
    old_path = "generic/graph1.png"
    new_path = "important/revenue.png"
    data = client.storage.from_(bucket_name).move(old_path, new_path)
