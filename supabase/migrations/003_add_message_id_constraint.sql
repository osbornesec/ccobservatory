-- Migration: 003_add_message_id_constraint.sql
-- Description: Add message_id column and unique constraint for idempotency
-- Created: 2025-01-17
-- Dependencies: 002_performance_indexes.sql

-- =============================================================================
-- ADD message_id COLUMN TO MESSAGES TABLE
-- =============================================================================

-- Add message_id column to messages table for idempotency
ALTER TABLE messages 
ADD COLUMN IF NOT EXISTS message_id TEXT;

-- =============================================================================
-- CREATE UNIQUE CONSTRAINT FOR IDEMPOTENCY
-- =============================================================================

-- Create unique constraint on message_id to prevent duplicates
-- This ensures that retries won't create duplicate messages
ALTER TABLE messages 
ADD CONSTRAINT messages_message_id_unique UNIQUE (message_id);

-- =============================================================================
-- CREATE COMPOSITE UNIQUE CONSTRAINT FOR EXTRA SAFETY
-- =============================================================================

-- Create composite unique constraint on (conversation_id, message_id, timestamp)
-- This provides extra safety against duplicates and supports efficient queries
CREATE UNIQUE INDEX IF NOT EXISTS idx_messages_conversation_message_timestamp_unique
    ON messages(conversation_id, message_id, timestamp);

-- =============================================================================
-- UPDATE EXISTING RECORDS (if any exist)
-- =============================================================================

-- For any existing records without message_id, generate one based on timestamp and role
-- This is safe for existing data and provides backward compatibility
UPDATE messages 
SET message_id = role || '-' || EXTRACT(EPOCH FROM timestamp)::TEXT || '-' || 
    SUBSTRING(id::TEXT FROM 1 FOR 8) || '-' || 
    LPAD(EXTRACT(MICROSECONDS FROM timestamp)::TEXT, 6, '0')
WHERE message_id IS NULL;

-- =============================================================================
-- ADD NOT NULL CONSTRAINT AFTER BACKFILL
-- =============================================================================

-- Now that all records have message_id, make it NOT NULL
ALTER TABLE messages 
ALTER COLUMN message_id SET NOT NULL;

-- =============================================================================
-- COMMENTS FOR DOCUMENTATION
-- =============================================================================

COMMENT ON COLUMN messages.message_id IS 'Unique message identifier from source JSONL data for idempotency';
COMMENT ON CONSTRAINT messages_message_id_unique IS 'Prevents duplicate messages on retries';
COMMENT ON INDEX idx_messages_conversation_message_timestamp_unique IS 'Composite unique constraint for message deduplication and efficient queries';