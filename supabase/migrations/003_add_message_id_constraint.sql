-- Migration: 003_add_message_id_constraint.sql
-- Description: Add message_id column and unique constraint for idempotency
-- Created: 2025-01-17
-- Dependencies: 002_performance_indexes.sql

-- =============================================================================
-- TRANSACTION WRAPPER FOR ATOMICITY
-- =============================================================================
-- All DDL and DML operations are wrapped in a transaction to ensure atomicity.
-- If any step fails, the entire migration is rolled back to maintain consistency.

BEGIN;

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

-- =============================================================================
-- COMMIT TRANSACTION
-- =============================================================================
-- If we reach this point, all operations succeeded and changes are committed.
-- PostgreSQL will automatically rollback on any error before this point.

COMMIT;