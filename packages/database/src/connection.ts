import Database from 'bun:sqlite';
import { existsSync, mkdirSync } from 'fs';
import { dirname, resolve } from 'path';
import { DEFAULT_CONFIG } from '@cco/core';

export interface DatabaseConfig {
  path: string;
  enableWAL?: boolean;
  timeout?: number;
  cacheSize?: number;
}

export class DatabaseConnection {
  private db: Database;
  private isInitialized = false;

  constructor(config: DatabaseConfig) {
    // Ensure directory exists
    const dbDir = dirname(config.path);
    if (!existsSync(dbDir)) {
      mkdirSync(dbDir, { recursive: true });
    }

    this.db = new Database(config.path);
    this.initialize(config);
  }

  private initialize(config: DatabaseConfig): void {
    if (this.isInitialized) return;

    // Configure SQLite for optimal performance
    if (config.enableWAL !== false) {
      this.db.exec('PRAGMA journal_mode = WAL');
    }
    
    this.db.exec('PRAGMA synchronous = NORMAL');
    this.db.exec(`PRAGMA cache_size = ${config.cacheSize || DEFAULT_CONFIG.CONNECTION_POOL_SIZE * 1000}`);
    this.db.exec('PRAGMA foreign_keys = ON');
    this.db.exec(`PRAGMA busy_timeout = ${config.timeout || DEFAULT_CONFIG.QUERY_TIMEOUT}`);
    
    // Additional performance optimizations
    this.db.exec('PRAGMA temp_store = MEMORY');
    this.db.exec('PRAGMA mmap_size = 268435456'); // 256MB
    this.db.exec('PRAGMA optimize');

    this.isInitialized = true;
  }

  /**
   * Execute a query and return results
   */
  query<T = any>(sql: string, params: any[] = []): T[] {
    const stmt = this.db.prepare(sql);
    return stmt.all(...params) as T[];
  }

  /**
   * Execute a query and return the first result
   */
  queryOne<T = any>(sql: string, params: any[] = []): T | null {
    const stmt = this.db.prepare(sql);
    return (stmt.get(...params) as T) || null;
  }

  /**
   * Execute a statement (INSERT, UPDATE, DELETE)
   */
  execute(sql: string, params: any[] = []): { changes: number; lastInsertRowid: number } {
    const stmt = this.db.prepare(sql);
    const result = stmt.run(...params);
    return {
      changes: result.changes,
      lastInsertRowid: Number(result.lastInsertRowid)
    };
  }

  /**
   * Execute multiple statements in a transaction
   */
  transaction<T>(callback: (db: DatabaseConnection) => T): T {
    const transaction = this.db.transaction(() => {
      return callback(this);
    });
    return transaction();
  }

  /**
   * Execute raw SQL (for migrations and complex operations)
   */
  exec(sql: string): void {
    this.db.exec(sql);
  }

  /**
   * Check if a table exists
   */
  tableExists(tableName: string): boolean {
    const result = this.queryOne<{ count: number }>(
      "SELECT COUNT(*) as count FROM sqlite_master WHERE type='table' AND name=?",
      [tableName]
    );
    return (result?.count || 0) > 0;
  }

  /**
   * Get database info
   */
  getInfo(): { 
    size: number; 
    pageCount: number; 
    pageSize: number; 
    walMode: boolean;
    foreignKeys: boolean;
  } {
    const pageCount = this.queryOne<{ page_count: number }>('PRAGMA page_count')?.page_count || 0;
    const pageSize = this.queryOne<{ page_size: number }>('PRAGMA page_size')?.page_size || 0;
    const journalMode = this.queryOne<{ journal_mode: string }>('PRAGMA journal_mode')?.journal_mode || '';
    const foreignKeys = this.queryOne<{ foreign_keys: number }>('PRAGMA foreign_keys')?.foreign_keys || 0;

    return {
      size: pageCount * pageSize,
      pageCount,
      pageSize,
      walMode: journalMode.toLowerCase() === 'wal',
      foreignKeys: foreignKeys === 1
    };
  }

  /**
   * Optimize database (rebuild indexes, analyze, etc.)
   */
  optimize(): void {
    this.exec('PRAGMA optimize');
    this.exec('VACUUM');
    this.exec('ANALYZE');
  }

  /**
   * Close the database connection
   */
  close(): void {
    if (this.isInitialized) {
      this.db.close();
      this.isInitialized = false;
    }
  }

  /**
   * Get the underlying Bun SQLite database instance
   */
  getDatabase(): Database {
    return this.db;
  }
}

/**
 * Create a new database connection with default configuration
 */
export function createConnection(path?: string): DatabaseConnection {
  const dbPath = path || resolve(process.cwd(), 'data', DEFAULT_CONFIG.DATABASE_NAME);
  
  return new DatabaseConnection({
    path: dbPath,
    enableWAL: true,
    timeout: DEFAULT_CONFIG.QUERY_TIMEOUT,
    cacheSize: 10000
  });
}