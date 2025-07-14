export interface ConversationMetadata {
  id: string;
  projectId: string;
  filePath: string;
  title: string;
  createdAt: Date;
  lastUpdated: Date;
  messageCount: number;
  tokenCount?: number;
}

export interface Message {
  id: string;
  conversationId: string;
  role: 'user' | 'assistant';
  content: string;
  toolCalls?: ToolCall[];
  timestamp: Date;
  tokenCount?: number;
  model?: string;
}

export interface ToolCall {
  id: string;
  name: string;
  input: Record<string, any>;
  output?: Record<string, any>;
  executionTime?: number;
  status: 'pending' | 'success' | 'error';
}

export interface Project {
  id: string;
  name: string;
  path: string;
  createdAt: Date;
  updatedAt: Date;
  conversationCount: number;
}

// Actual Claude Code JSONL message format
export interface ClaudeCodeMessage {
  // Core fields present in all messages
  type: 'user' | 'assistant' | 'system' | 'summary';
  uuid: string;
  timestamp: string;
  sessionId: string;
  version: string;
  cwd: string;
  userType: string;
  isSidechain: boolean;
  parentUuid: string | null;

  // User message fields
  message?: {
    role: 'user' | 'assistant';
    content: string | Array<any>;
    id?: string;
    type?: string;
    model?: string;
    usage?: {
      input_tokens: number;
      cache_creation_input_tokens?: number;
      cache_read_input_tokens?: number;
      output_tokens: number;
      service_tier?: string;
    };
  };

  // System message fields
  content?: string;
  level?: string;
  toolUseID?: string;
  isMeta?: boolean;

  // Tool result fields
  toolUseResult?: {
    stdout?: string;
    stderr?: string;
    interrupted: boolean;
    isImage: boolean;
  };

  // Summary fields
  summary?: string;
  leafUuid?: string;

  // Request tracking
  requestId?: string;
}

// Legacy interface for backward compatibility
export interface ClaudeMessage {
  type: 'user' | 'assistant' | 'tool_call' | 'tool_result';
  content?: string;
  tool_calls?: Array<{
    name: string;
    input: Record<string, any>;
    output?: Record<string, any>;
  }>;
  timestamp: string;
  model?: string;
  usage?: {
    input_tokens: number;
    output_tokens: number;
  };
}