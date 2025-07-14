#!/usr/bin/env bun

/**
 * Database migration CLI script
 * Usage: bun run migrate.ts [command]
 * Commands:
 *   - migrate (default): Run pending migrations
 *   - status: Show migration status
 *   - reset: Reset database (WARNING: destroys all data)
 */

import { Database } from './index.ts';
import { resolve } from 'path';

const DEFAULT_DB_PATH = resolve(process.cwd(), 'data', 'claude_observatory.db');

function getDbPath(): string {
  return process.env.DATABASE_PATH || DEFAULT_DB_PATH;
}

async function main() {
  const command = process.argv[2] || 'migrate';
  const dbPath = getDbPath();

  console.log(`Using database: ${dbPath}`);

  const db = new Database(dbPath);

  try {
    switch (command) {
      case 'migrate':
        await runMigrations(db);
        break;
      
      case 'status':
        showStatus(db);
        break;
      
      case 'reset':
        await resetDatabase(db);
        break;
      
      case 'info':
        showInfo(db);
        break;
      
      default:
        console.error(`Unknown command: ${command}`);
        console.log('Available commands: migrate, status, reset, info');
        process.exit(1);
    }
  } catch (error) {
    console.error('Migration failed:', error);
    process.exit(1);
  } finally {
    db.close();
  }
}

async function runMigrations(db: Database) {
  console.log('Running database migrations...');
  await db.initialize();
  console.log('Migrations completed successfully');
}

function showStatus(db: Database) {
  const status = db.migrations.getStatus();
  console.log('Migration Status:');
  console.log(`  Applied: ${status.applied}`);
  console.log(`  Pending: ${status.pending}`);
  console.log(`  Total: ${status.total}`);

  if (status.pending > 0) {
    console.log('\nPending migrations:');
    const pending = db.migrations.getPendingMigrations();
    pending.forEach((migration: { filename: string }) => {
      console.log(`  - ${migration.filename}`);
    });
  }
}

async function resetDatabase(db: Database) {
  console.log('WARNING: This will destroy all data in the database!');
  
  // In a real application, you might want to add a confirmation prompt
  console.log('Resetting database...');
  db.migrations.reset();
  console.log('Database reset completed');
}

function showInfo(db: Database) {
  const info = db.getInfo();
  console.log('Database Information:');
  console.log(`  Size: ${(info.size / 1024 / 1024).toFixed(2)} MB`);
  console.log(`  Page Count: ${info.pageCount}`);
  console.log(`  Page Size: ${info.pageSize} bytes`);
  console.log(`  WAL Mode: ${info.walMode ? 'Enabled' : 'Disabled'}`);
  console.log(`  Foreign Keys: ${info.foreignKeys ? 'Enabled' : 'Disabled'}`);
}

// Run the script
if (import.meta.main) {
  main().catch(console.error);
}