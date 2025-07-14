// Database connection and configuration
export {
  DatabaseConnection,
  createConnection,
  type DatabaseConfig
} from './connection.ts';

// Migration system
export {
  MigrationManager,
  type Migration
} from './migrations.ts';

// Data Access Objects
export {
  ProjectsDAO,
  type CreateProjectData,
  type UpdateProjectData
} from './dao/projects.ts';

export {
  ConversationsDAO,
  type CreateConversationData,
  type UpdateConversationData
} from './dao/conversations.ts';

// Re-export for easier importing
import { DatabaseConnection, createConnection } from './connection.ts';
import { MigrationManager } from './migrations.ts';
import { ProjectsDAO } from './dao/projects.ts';
import { ConversationsDAO } from './dao/conversations.ts';

// Database factory for easy setup
export class Database {
  public connection: DatabaseConnection;
  public projects: ProjectsDAO;
  public conversations: ConversationsDAO;
  public migrations: MigrationManager;

  constructor(dbPath?: string) {
    this.connection = createConnection(dbPath);
    this.projects = new ProjectsDAO(this.connection);
    this.conversations = new ConversationsDAO(this.connection);
    this.migrations = new MigrationManager(this.connection);
  }

  /**
   * Initialize database with migrations
   */
  async initialize(): Promise<void> {
    console.log('Initializing database...');
    this.migrations.migrate();
    console.log('Database initialized successfully');
  }

  /**
   * Get database information
   */
  getInfo() {
    return this.connection.getInfo();
  }

  /**
   * Optimize database performance
   */
  optimize(): void {
    this.connection.optimize();
  }

  /**
   * Close database connection
   */
  close(): void {
    this.connection.close();
  }
}