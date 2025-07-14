import { DatabaseConnection } from './connection.ts';
import { readFileSync, readdirSync } from 'fs';
import { join, resolve } from 'path';

export interface Migration {
  id: string;
  filename: string;
  sql: string;
  appliedAt?: Date;
}

export class MigrationManager {
  private db: DatabaseConnection;
  private migrationsPath: string;

  constructor(db: DatabaseConnection, migrationsPath?: string) {
    this.db = db;
    this.migrationsPath = migrationsPath || join(__dirname, 'migrations');
    this.initializeMigrationsTable();
  }

  private initializeMigrationsTable(): void {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS schema_migrations (
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);
  }

  /**
   * Get all available migration files
   */
  private getAvailableMigrations(): Migration[] {
    try {
      const files = readdirSync(this.migrationsPath)
        .filter(file => file.endsWith('.sql'))
        .sort();

      return files.map(filename => {
        const filePath = join(this.migrationsPath, filename);
        const sql = readFileSync(filePath, 'utf-8');
        const id = filename.replace('.sql', '');

        return {
          id,
          filename,
          sql
        };
      });
    } catch (error) {
      console.warn(`Unable to read migrations from ${this.migrationsPath}:`, error);
      return [];
    }
  }

  /**
   * Get applied migrations from database
   */
  private getAppliedMigrations(): Set<string> {
    const applied = this.db.query<{ id: string }>(
      'SELECT id FROM schema_migrations ORDER BY applied_at'
    );
    return new Set(applied.map(m => m.id));
  }

  /**
   * Get pending migrations
   */
  getPendingMigrations(): Migration[] {
    const available = this.getAvailableMigrations();
    const applied = this.getAppliedMigrations();

    return available.filter(migration => !applied.has(migration.id));
  }

  /**
   * Apply a single migration
   */
  private applyMigration(migration: Migration): void {
    console.log(`Applying migration: ${migration.filename}`);

    this.db.transaction(() => {
      // Execute the migration SQL
      this.db.exec(migration.sql);

      // Record the migration as applied
      this.db.execute(
        'INSERT INTO schema_migrations (id, filename) VALUES (?, ?)',
        [migration.id, migration.filename]
      );
    });

    console.log(`Migration applied: ${migration.filename}`);
  }

  /**
   * Run all pending migrations
   */
  migrate(): void {
    const pending = this.getPendingMigrations();

    if (pending.length === 0) {
      console.log('No pending migrations');
      return;
    }

    console.log(`Applying ${pending.length} migration(s)...`);

    for (const migration of pending) {
      try {
        this.applyMigration(migration);
      } catch (error) {
        console.error(`Failed to apply migration ${migration.filename}:`, error);
        throw error;
      }
    }

    console.log('All migrations applied successfully');
  }

  /**
   * Get migration status
   */
  getStatus(): { applied: number; pending: number; total: number } {
    const available = this.getAvailableMigrations();
    const applied = this.getAppliedMigrations();
    const pending = this.getPendingMigrations();

    return {
      applied: applied.size,
      pending: pending.length,
      total: available.length
    };
  }

  /**
   * Reset database (drop all tables and reapply migrations)
   * WARNING: This will destroy all data!
   */
  reset(): void {
    console.warn('RESETTING DATABASE - ALL DATA WILL BE LOST!');

    // Get all tables
    const tables = this.db.query<{ name: string }>(
      "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    );

    // Drop all tables
    this.db.transaction(() => {
      for (const table of tables) {
        this.db.exec(`DROP TABLE IF EXISTS ${table.name}`);
      }
    });

    console.log('Database reset complete');

    // Reapply migrations
    this.initializeMigrationsTable();
    this.migrate();
  }
}