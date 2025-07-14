/**
 * Default configuration constants for Claude Code Observatory
 */

export const DEFAULT_CONFIG = {
  // File monitoring
  DEBOUNCE_MS: 100,
  MAX_FILE_SIZE: 50 * 1024 * 1024, // 50MB
  WATCH_POLLING_INTERVAL: 1000,
  
  // Database
  DATABASE_NAME: 'claude_observatory.db',
  CONNECTION_POOL_SIZE: 10,
  QUERY_TIMEOUT: 30000,
  
  // Server
  DEFAULT_PORT: 3000,
  WS_PORT: 3001,
  MAX_CONNECTIONS: 1000,
  
  // Performance
  BATCH_SIZE: 100,
  PARSE_TIMEOUT: 5000,
  MEMORY_LIMIT: 512 * 1024 * 1024, // 512MB
  
  // UI
  PAGINATION_SIZE: 50,
  REFRESH_INTERVAL: 1000,
  
  // Claude Code specific
  CLAUDE_DIR: '~/.claude',
  PROJECTS_SUBDIR: 'projects',
  JSONL_EXTENSION: '.jsonl'
} as const;

export const FILE_PATTERNS = {
  JSONL: '**/*.jsonl',
  CONVERSATIONS: '**/conversations/*.jsonl',
  IGNORE: ['**/node_modules/**', '**/dist/**', '**/.git/**']
} as const;

export const ERROR_CODES = {
  PARSE_ERROR: 'PARSE_ERROR',
  FILE_NOT_FOUND: 'FILE_NOT_FOUND',
  PERMISSION_DENIED: 'PERMISSION_DENIED',
  DATABASE_ERROR: 'DATABASE_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR'
} as const;

export const LOG_LEVELS = {
  ERROR: 0,
  WARN: 1,
  INFO: 2,
  DEBUG: 3,
  TRACE: 4
} as const;