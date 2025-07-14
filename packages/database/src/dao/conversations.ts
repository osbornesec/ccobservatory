import { DatabaseConnection } from '../connection.ts';
import type { ConversationMetadata } from '@cco/core';
import { generateConversationId } from '@cco/core';

export interface CreateConversationData {
  projectId: string;
  filePath: string;
  title?: string;
  createdAt?: Date;
  lastUpdated?: Date;
  messageCount?: number;
  tokenCount?: number;
}

export interface UpdateConversationData {
  title?: string;
  messageCount?: number;
  tokenCount?: number;
  lastUpdated?: Date;
}

export class ConversationsDAO {
  constructor(private db: DatabaseConnection) {}

  /**
   * Create a new conversation
   */
  create(data: CreateConversationData): ConversationMetadata {
    const id = generateConversationId(data.filePath);
    const now = new Date();

    this.db.execute(
      `INSERT INTO conversations 
       (id, project_id, file_path, title, created_at, last_updated, message_count, token_count)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        id,
        data.projectId,
        data.filePath,
        data.title || 'Untitled Conversation',
        (data.createdAt || now).toISOString(),
        (data.lastUpdated || now).toISOString(),
        data.messageCount || 0,
        data.tokenCount || null
      ]
    );

    return {
      id,
      projectId: data.projectId,
      filePath: data.filePath,
      title: data.title || 'Untitled Conversation',
      createdAt: data.createdAt || now,
      lastUpdated: data.lastUpdated || now,
      messageCount: data.messageCount || 0,
      tokenCount: data.tokenCount
    };
  }

  /**
   * Find conversation by ID
   */
  findById(id: string): ConversationMetadata | null {
    const row = this.db.queryOne<any>(
      'SELECT * FROM conversations WHERE id = ?',
      [id]
    );

    return row ? this.mapRowToConversation(row) : null;
  }

  /**
   * Find conversation by file path
   */
  findByFilePath(filePath: string): ConversationMetadata | null {
    const row = this.db.queryOne<any>(
      'SELECT * FROM conversations WHERE file_path = ?',
      [filePath]
    );

    return row ? this.mapRowToConversation(row) : null;
  }

  /**
   * Get conversations for a project
   */
  findByProject(projectId: string, limit = 50, offset = 0): ConversationMetadata[] {
    const rows = this.db.query<any>(
      `SELECT * FROM conversations 
       WHERE project_id = ? 
       ORDER BY last_updated DESC 
       LIMIT ? OFFSET ?`,
      [projectId, limit, offset]
    );

    return rows.map(row => this.mapRowToConversation(row));
  }

  /**
   * Get all conversations with pagination
   */
  findAll(limit = 50, offset = 0): ConversationMetadata[] {
    const rows = this.db.query<any>(
      'SELECT * FROM conversations ORDER BY last_updated DESC LIMIT ? OFFSET ?',
      [limit, offset]
    );

    return rows.map(row => this.mapRowToConversation(row));
  }

  /**
   * Search conversations by title or content
   */
  search(query: string, projectId?: string, limit = 50): ConversationMetadata[] {
    const searchPattern = `%${query}%`;
    let sql = `
      SELECT DISTINCT c.* FROM conversations c
      LEFT JOIN messages m ON c.id = m.conversation_id
      WHERE (c.title LIKE ? OR m.content LIKE ?)
    `;
    const params: any[] = [searchPattern, searchPattern];

    if (projectId) {
      sql += ' AND c.project_id = ?';
      params.push(projectId);
    }

    sql += ' ORDER BY c.last_updated DESC LIMIT ?';
    params.push(limit);

    const rows = this.db.query<any>(sql, params);
    return rows.map(row => this.mapRowToConversation(row));
  }

  /**
   * Update conversation
   */
  update(id: string, data: UpdateConversationData): ConversationMetadata | null {
    const updates: string[] = [];
    const values: any[] = [];

    if (data.title !== undefined) {
      updates.push('title = ?');
      values.push(data.title);
    }

    if (data.messageCount !== undefined) {
      updates.push('message_count = ?');
      values.push(data.messageCount);
    }

    if (data.tokenCount !== undefined) {
      updates.push('token_count = ?');
      values.push(data.tokenCount);
    }

    if (data.lastUpdated !== undefined) {
      updates.push('last_updated = ?');
      values.push(data.lastUpdated.toISOString());
    }

    if (updates.length === 0) {
      return this.findById(id);
    }

    values.push(id);

    const result = this.db.execute(
      `UPDATE conversations SET ${updates.join(', ')} WHERE id = ?`,
      values
    );

    return result.changes > 0 ? this.findById(id) : null;
  }

  /**
   * Delete conversation and all related messages
   */
  delete(id: string): boolean {
    const result = this.db.execute('DELETE FROM conversations WHERE id = ?', [id]);
    return result.changes > 0;
  }

  /**
   * Get conversation count for a project
   */
  getCountByProject(projectId: string): number {
    const result = this.db.queryOne<{ count: number }>(
      'SELECT COUNT(*) as count FROM conversations WHERE project_id = ?',
      [projectId]
    );
    return result?.count || 0;
  }

  /**
   * Get recent conversations across all projects
   */
  getRecent(limit = 10): ConversationMetadata[] {
    const rows = this.db.query<any>(
      'SELECT * FROM conversations ORDER BY last_updated DESC LIMIT ?',
      [limit]
    );

    return rows.map(row => this.mapRowToConversation(row));
  }

  private mapRowToConversation(row: any): ConversationMetadata {
    return {
      id: row.id,
      projectId: row.project_id,
      filePath: row.file_path,
      title: row.title,
      createdAt: new Date(row.created_at),
      lastUpdated: new Date(row.last_updated),
      messageCount: row.message_count || 0,
      tokenCount: row.token_count || undefined
    };
  }
}