-- Initial schema for Claude Code Observatory
-- This migration creates the core tables for projects, conversations, messages, and tool calls

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  path TEXT NOT NULL UNIQUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  conversation_count INTEGER DEFAULT 0,
  total_messages INTEGER DEFAULT 0,
  total_tokens INTEGER DEFAULT 0
);

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  file_path TEXT NOT NULL UNIQUE,
  title TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
  message_count INTEGER DEFAULT 0,
  token_count INTEGER,
  model TEXT,
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'archived', 'error')),
  FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
  id TEXT PRIMARY KEY,
  conversation_id TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT,
  timestamp DATETIME NOT NULL,
  token_count INTEGER,
  model TEXT,
  sequence_number INTEGER NOT NULL,
  FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
);

-- Tool calls table
CREATE TABLE IF NOT EXISTS tool_calls (
  id TEXT PRIMARY KEY,
  message_id TEXT NOT NULL,
  tool_name TEXT NOT NULL,
  input_data TEXT, -- JSON
  output_data TEXT, -- JSON
  execution_time INTEGER,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'success', 'error')),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (message_id) REFERENCES messages (id) ON DELETE CASCADE
);

-- File watch events table for monitoring
CREATE TABLE IF NOT EXISTS file_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  file_path TEXT NOT NULL,
  event_type TEXT NOT NULL CHECK (event_type IN ('add', 'change', 'unlink')),
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  file_size INTEGER,
  processed BOOLEAN DEFAULT FALSE
);

-- System metrics table for performance monitoring
CREATE TABLE IF NOT EXISTS system_metrics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  memory_usage INTEGER,
  cpu_usage REAL,
  active_connections INTEGER,
  files_watched INTEGER,
  event_queue_size INTEGER
);

-- Processing stats table
CREATE TABLE IF NOT EXISTS processing_stats (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date DATE DEFAULT (DATE('now')),
  files_processed INTEGER DEFAULT 0,
  messages_extracted INTEGER DEFAULT 0,
  parsing_errors INTEGER DEFAULT 0,
  average_processing_time REAL DEFAULT 0,
  last_processed_at DATETIME
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_conversations_project_id ON conversations(project_id);
CREATE INDEX IF NOT EXISTS idx_conversations_file_path ON conversations(file_path);
CREATE INDEX IF NOT EXISTS idx_conversations_last_updated ON conversations(last_updated);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(role);
CREATE INDEX IF NOT EXISTS idx_messages_sequence ON messages(conversation_id, sequence_number);

CREATE INDEX IF NOT EXISTS idx_tool_calls_message_id ON tool_calls(message_id);
CREATE INDEX IF NOT EXISTS idx_tool_calls_tool_name ON tool_calls(tool_name);
CREATE INDEX IF NOT EXISTS idx_tool_calls_status ON tool_calls(status);

CREATE INDEX IF NOT EXISTS idx_file_events_timestamp ON file_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_file_events_processed ON file_events(processed);
CREATE INDEX IF NOT EXISTS idx_file_events_file_path ON file_events(file_path);

CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_processing_stats_date ON processing_stats(date);

-- Create triggers for automatic timestamp updates
CREATE TRIGGER IF NOT EXISTS update_project_timestamp
  AFTER UPDATE ON projects
BEGIN
  UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_conversation_timestamp
  AFTER UPDATE ON conversations
BEGIN
  UPDATE conversations SET last_updated = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Create trigger to update conversation message count
CREATE TRIGGER IF NOT EXISTS update_conversation_message_count
  AFTER INSERT ON messages
BEGIN
  UPDATE conversations 
  SET message_count = message_count + 1,
      last_updated = CURRENT_TIMESTAMP
  WHERE id = NEW.conversation_id;
END;

-- Create trigger to update project conversation count
CREATE TRIGGER IF NOT EXISTS update_project_conversation_count
  AFTER INSERT ON conversations
BEGIN
  UPDATE projects 
  SET conversation_count = conversation_count + 1,
      updated_at = CURRENT_TIMESTAMP
  WHERE id = NEW.project_id;
END;