import { DatabaseConnection } from '../connection.ts';
import type { Project } from '@cco/core';
import { generateId } from '@cco/core';

export interface CreateProjectData {
  name: string;
  path: string;
}

export interface UpdateProjectData {
  name?: string;
  path?: string;
}

export class ProjectsDAO {
  constructor(private db: DatabaseConnection) {}

  /**
   * Create a new project
   */
  create(data: CreateProjectData): Project {
    const id = generateId();
    const now = new Date();

    this.db.execute(
      `INSERT INTO projects (id, name, path, created_at, updated_at)
       VALUES (?, ?, ?, ?, ?)`,
      [id, data.name, data.path, now.toISOString(), now.toISOString()]
    );

    return {
      id,
      name: data.name,
      path: data.path,
      createdAt: now,
      updatedAt: now,
      conversationCount: 0
    };
  }

  /**
   * Find project by ID
   */
  findById(id: string): Project | null {
    const row = this.db.queryOne<any>(
      'SELECT * FROM projects WHERE id = ?',
      [id]
    );

    return row ? this.mapRowToProject(row) : null;
  }

  /**
   * Find project by path
   */
  findByPath(path: string): Project | null {
    const row = this.db.queryOne<any>(
      'SELECT * FROM projects WHERE path = ?',
      [path]
    );

    return row ? this.mapRowToProject(row) : null;
  }

  /**
   * Get all projects
   */
  findAll(): Project[] {
    const rows = this.db.query<any>('SELECT * FROM projects ORDER BY created_at DESC');
    return rows.map(row => this.mapRowToProject(row));
  }

  /**
   * Update project
   */
  update(id: string, data: UpdateProjectData): Project | null {
    const updates: string[] = [];
    const values: any[] = [];

    if (data.name !== undefined) {
      updates.push('name = ?');
      values.push(data.name);
    }

    if (data.path !== undefined) {
      updates.push('path = ?');
      values.push(data.path);
    }

    if (updates.length === 0) {
      return this.findById(id);
    }

    updates.push('updated_at = ?');
    values.push(new Date().toISOString());
    values.push(id);

    const result = this.db.execute(
      `UPDATE projects SET ${updates.join(', ')} WHERE id = ?`,
      values
    );

    return result.changes > 0 ? this.findById(id) : null;
  }

  /**
   * Delete project and all related data
   */
  delete(id: string): boolean {
    const result = this.db.execute('DELETE FROM projects WHERE id = ?', [id]);
    return result.changes > 0;
  }

  /**
   * Get project statistics
   */
  getStats(id: string): {
    conversationCount: number;
    messageCount: number;
    totalTokens: number;
    lastActivity: Date | null;
  } | null {
    const stats = this.db.queryOne<any>(
      `SELECT 
        COUNT(DISTINCT c.id) as conversation_count,
        COUNT(m.id) as message_count,
        COALESCE(SUM(m.token_count), 0) as total_tokens,
        MAX(c.last_updated) as last_activity
      FROM projects p
      LEFT JOIN conversations c ON p.id = c.project_id
      LEFT JOIN messages m ON c.id = m.conversation_id
      WHERE p.id = ?
      GROUP BY p.id`,
      [id]
    );

    if (!stats) return null;

    return {
      conversationCount: stats.conversation_count || 0,
      messageCount: stats.message_count || 0,
      totalTokens: stats.total_tokens || 0,
      lastActivity: stats.last_activity ? new Date(stats.last_activity) : null
    };
  }

  private mapRowToProject(row: any): Project {
    return {
      id: row.id,
      name: row.name,
      path: row.path,
      createdAt: new Date(row.created_at),
      updatedAt: new Date(row.updated_at),
      conversationCount: row.conversation_count || 0
    };
  }
}