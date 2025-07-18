-- Fix for conversation trigger that references wrong field name
-- The trigger is trying to reference NEW.updated_at but conversations table has last_updated

-- Drop the existing trigger
DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations;

-- Create a corrected trigger function for conversations
CREATE OR REPLACE FUNCTION update_conversations_last_updated()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create the corrected trigger
CREATE TRIGGER update_conversations_last_updated 
    BEFORE UPDATE ON conversations 
    FOR EACH ROW 
    EXECUTE FUNCTION update_conversations_last_updated();