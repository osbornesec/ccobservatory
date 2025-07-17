"""
DatabaseWriter implementation for storing conversation data in Supabase.

This module handles writing ConversationData and ParsedMessage objects to the
Supabase database with proper relationship management and performance tracking.
"""

import logging
import time
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from postgrest import APIError
from supabase import Client

from app.database.supabase_client import get_supabase_service_client
from app.models.contracts import ConversationData, ParsedMessage, ProcessingError

logger = logging.getLogger(__name__)


class DatabaseWriterError(Exception):
    """Exception raised by DatabaseWriter for database operation errors."""
    def __init__(self, processing_error: ProcessingError):
        self.processing_error = processing_error
        super().__init__(processing_error.error_message)

# Configuration constants
CONVERSATIONS_TABLE = "conversations"
MESSAGES_TABLE = "messages"
MAX_RETRIES = 3
INITIAL_RETRY_DELAY_S = 0.1  # Start with 100ms


class DatabaseWriter:
    """
    Handles writing conversation and message data to the Supabase database.

    Provides high-level interface for persisting parsed conversation data with
    batch operations, error handling, retry logic, and performance metrics.

    Uses a read-then-write pattern for conversations to ensure proper updates,
    and upsert for messages to handle idempotent batch insertion.
    """

    def __init__(self, client: Optional[Client] = None):
        """
        Initialize the DatabaseWriter.

        Args:
            client: Optional Supabase client instance. If not provided,
                   a service client is initialized automatically.
        """
        self._client: Client = client or get_supabase_service_client()
        self.stats = {
            "conversations_written": 0,
            "conversations_updated": 0,
            "messages_written": 0,
            "write_errors": 0,
        }

        logger.info("DatabaseWriter initialized")

    def write_conversation(
        self, conversation_data: ConversationData
    ) -> Tuple[bool, UUID, Dict[str, float]]:
        """
        Write a full conversation and its messages to the database.

        Performs the following operations:
        1. Check for existing conversation (read)
        2. Update existing or insert new conversation record
        3. Batch upsert all associated messages

        Args:
            conversation_data: ConversationData object to persist

        Returns:
            Tuple of (success: bool, conversation_id: UUID, metrics: Dict[str, float])

        Raises:
            ProcessingError: If database operation fails after all retries
        """
        start_time = time.perf_counter()
        metrics = {}

        logger.debug(
            f"Starting to write conversation for session_id: {conversation_data.session_id}"
        )

        try:
            # Step 1: Handle conversation record (read-then-write pattern)
            conv_start = time.perf_counter()
            conversation_id = self._write_conversation_record(conversation_data)
            conv_end = time.perf_counter()
            metrics["conversation_write_ms"] = (conv_end - conv_start) * 1000

            # Step 2: Batch upsert messages if any exist
            if conversation_data.messages:
                msg_start = time.perf_counter()
                self._batch_upsert_messages(conversation_id, conversation_data.messages)
                msg_end = time.perf_counter()
                metrics["messages_write_ms"] = (msg_end - msg_start) * 1000
                self.stats["messages_written"] += len(conversation_data.messages)
            else:
                logger.debug(
                    f"No messages to write for conversation_id: {conversation_id}"
                )
                metrics["messages_write_ms"] = 0.0

            # Calculate total operation time
            total_end = time.perf_counter()
            metrics["total_write_ms"] = (total_end - start_time) * 1000

            logger.info(
                f"Successfully wrote conversation {conversation_id} "
                f"for session {conversation_data.session_id} "
                f"({len(conversation_data.messages)} messages) "
                f"in {metrics['total_write_ms']:.2f}ms"
            )

            return True, conversation_id, metrics

        except DatabaseWriterError:
            self.stats["write_errors"] += 1
            raise
        except Exception as e:
            self.stats["write_errors"] += 1
            error = ProcessingError(
                error_type="UnexpectedDatabaseError",
                error_message=f"Unexpected error writing conversation: {str(e)}",
                component="DatabaseWriter",
                original_event={"session_id": conversation_data.session_id},
            )
            logger.error(f"Unexpected database error: {error}")
            raise DatabaseWriterError(error)

    def _write_conversation_record(self, conversation_data: ConversationData) -> UUID:
        """
        Write conversation record using read-then-write pattern for proper updates.

        Args:
            conversation_data: Conversation data to write

        Returns:
            UUID of the conversation record
        """
        # Prepare payload excluding relational and DB-managed fields
        conversation_payload = conversation_data.model_dump(
            exclude={"messages", "id", "created_at", "updated_at"},
            exclude_none=True,
            by_alias=True,
        )
        
        # Ensure UUIDs are stringified for JSON payload
        if "project_id" in conversation_payload:
            conversation_payload["project_id"] = str(conversation_payload["project_id"])

        for attempt in range(MAX_RETRIES):
            try:
                # Step 1: Check for existing conversation
                existing_response = (
                    self._client.table(CONVERSATIONS_TABLE)
                    .select("id")
                    .eq("project_id", str(conversation_data.project_id))
                    .eq("session_id", conversation_data.session_id)
                    .limit(1)
                    .execute()
                )

                existing_record = (
                    existing_response.data[0] if existing_response.data else None
                )

                if existing_record:
                    # Step 2a: Update existing record
                    update_response = (
                        self._client.table(CONVERSATIONS_TABLE)
                        .update(conversation_payload)
                        .eq("id", existing_record["id"])
                        .execute()
                    )

                    if not update_response.data:
                        raise APIError("Update operation returned no data")

                    conversation_id = UUID(existing_record["id"])
                    self.stats["conversations_updated"] += 1
                    logger.debug(f"Updated existing conversation: {conversation_id}")

                else:
                    # Step 2b: Insert new record
                    insert_response = (
                        self._client.table(CONVERSATIONS_TABLE)
                        .insert(conversation_payload)
                        .execute()
                    )

                    if not insert_response.data:
                        raise APIError("Insert operation returned no data")

                    conversation_id = UUID(insert_response.data[0]["id"])
                    self.stats["conversations_written"] += 1
                    logger.debug(f"Created new conversation: {conversation_id}")

                return conversation_id

            except APIError as e:
                logger.warning(
                    f"Attempt {attempt + 1}/{MAX_RETRIES} to write conversation failed: {e}"
                )
                if attempt + 1 >= MAX_RETRIES:
                    logger.error(
                        f"Failed to write conversation for session_id: {conversation_data.session_id} "
                        f"after {MAX_RETRIES} attempts"
                    )
                    error = ProcessingError(
                        error_type="DatabaseError",
                        error_message=f"Failed to write conversation: {str(e)}",
                        component="DatabaseWriter",
                        original_event={"session_id": conversation_data.session_id},
                    )
                    raise DatabaseWriterError(error) from e

                time.sleep(INITIAL_RETRY_DELAY_S * (2**attempt))  # Exponential backoff

        raise RuntimeError("Exited retry loop unexpectedly during conversation write")

    def _batch_upsert_messages(
        self, conversation_id: UUID, messages: List[ParsedMessage]
    ) -> None:
        """
        Batch upsert messages using ON CONFLICT DO NOTHING for idempotent insertion.

        Args:
            conversation_id: UUID of the parent conversation
            messages: List of ParsedMessage objects to upsert
        """
        if not messages:
            return

        # Prepare message payloads with correct foreign key
        messages_payload = []
        for msg in messages:
            msg.conversation_id = conversation_id  # Set correct foreign key
            payload = msg.model_dump(exclude={"id", "message_id"}, exclude_none=True, by_alias=True)
            # Ensure UUIDs are stringified for JSON payload
            payload["conversation_id"] = str(payload["conversation_id"])
            # Ensure datetime objects are stringified for JSON payload
            if "timestamp" in payload:
                payload["timestamp"] = payload["timestamp"].isoformat()
            messages_payload.append(payload)

        for attempt in range(MAX_RETRIES):
            try:
                # Use regular insert for now (messages have UUID primary keys)
                response = (
                    self._client.table(MESSAGES_TABLE)
                    .insert(messages_payload)
                    .execute()
                )

                logger.debug(
                    f"Batch upserted {len(messages_payload)} messages "
                    f"for conversation_id: {conversation_id}"
                )
                return

            except APIError as e:
                logger.warning(
                    f"Attempt {attempt + 1}/{MAX_RETRIES} to batch upsert messages failed: {e}"
                )
                if attempt + 1 >= MAX_RETRIES:
                    logger.error(
                        f"Failed to upsert messages for conversation_id: {conversation_id} "
                        f"after {MAX_RETRIES} attempts"
                    )
                    error = ProcessingError(
                        error_type="DatabaseError",
                        error_message=f"Failed to batch upsert messages: {str(e)}",
                        component="DatabaseWriter",
                        original_event={"conversation_id": str(conversation_id)},
                    )
                    raise DatabaseWriterError(error) from e

                time.sleep(INITIAL_RETRY_DELAY_S * (2**attempt))

        raise RuntimeError("Exited retry loop unexpectedly during message upsert")

    def get_stats(self) -> Dict[str, int]:
        """
        Get database writing statistics.

        Returns:
            Dictionary of database operation statistics
        """
        return self.stats.copy()

    def reset_stats(self) -> None:
        """Reset database writing statistics."""
        self.stats = {
            "conversations_written": 0,
            "conversations_updated": 0,
            "messages_written": 0,
            "write_errors": 0,
        }
