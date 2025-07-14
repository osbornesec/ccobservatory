# 🗃️ Database Architecture Technical Specification

## 🎯 **Executive Summary**

This specification defines the SQLite database architecture for Claude Code Observatory, optimized for high-performance real-time conversation storage, full-text search, and analytics. The design leverages WAL mode for concurrent access, implements sophisticated indexing strategies, and provides comprehensive data integrity guarantees.

---

## 📋 **Technical Requirements**

### **Performance Requirements**
- **Query Response Time:** <100ms (95th percentile)
- **Concurrent Connections:** 100+ simultaneous users
- **Write Throughput:** 10,000+ messages per second
- **Storage Capacity:** 10GB+ databases with 1M+ messages per project
- **Full-Text Search:** <500ms for complex queries

### **Data Integrity Requirements**
- **ACID Compliance:** Full transaction integrity
- **Backup Strategy:** Point-in-time recovery capability
- **Data Validation:** Comprehensive constraint enforcement
- **Concurrent Safety:** Reader-writer isolation in WAL mode

---

## 🏗️ **Database Schema Design**

### **Core Tables**

```sql
-- Enable WAL mode and optimize settings
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 10000;
PRAGMA temp_store = memory;
PRAGMA mmap_size = 268435456; -- 256MB

-- Projects table: Root entity for organizing conversations
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    path TEXT NOT NULL UNIQUE,
    description TEXT,
    settings JSON DEFAULT '{}',
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000),
    updated_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000),
    last_activity INTEGER,
    is_active BOOLEAN DEFAULT 1,
    metadata JSON DEFAULT '{}',
    
    -- Constraints
    CHECK (name != ''),
    CHECK (path != ''),
    CHECK (created_at > 0),
    CHECK (updated_at >= created_at)
);

-- Conversations table: Groups related messages in a session
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,  -- Derived from sessionId + project
    project_id INTEGER NOT NULL,
    session_id TEXT NOT NULL,
    start_time INTEGER NOT NULL,
    end_time INTEGER,
    message_count INTEGER DEFAULT 0,
    tool_usage_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'error')),
    context_window_size INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    metadata JSON DEFAULT '{}',
    
    -- Foreign key constraints
    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
    
    -- Data validation
    CHECK (start_time > 0),
    CHECK (end_time IS NULL OR end_time >= start_time),
    CHECK (message_count >= 0),
    CHECK (tool_usage_count >= 0),
    CHECK (context_window_size >= 0),
    CHECK (total_tokens >= 0)
);

-- Messages table: Individual conversation messages
CREATE TABLE messages (
    id TEXT PRIMARY KEY,  -- Claude message UUID
    conversation_id TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('user', 'assistant', 'system')),
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    token_count INTEGER DEFAULT 0,
    parent_id TEXT,
    depth INTEGER DEFAULT 0,
    tool_usage JSON,
    metadata JSON DEFAULT '{}',
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000),
    
    -- Foreign key constraints
    FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES messages (id) ON DELETE SET NULL,
    
    -- Data validation
    CHECK (timestamp > 0),
    CHECK (content != ''),
    CHECK (content_hash != ''),
    CHECK (token_count >= 0),
    CHECK (depth >= 0),
    CHECK (created_at > 0)
);

-- Tool executions table: Detailed tool usage tracking
CREATE TABLE tool_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT NOT NULL,
    tool_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    input JSON NOT NULL,
    output TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'success', 'error', 'timeout')),
    execution_time_ms INTEGER,
    error_message TEXT,
    started_at INTEGER NOT NULL,
    completed_at INTEGER,
    metadata JSON DEFAULT '{}',
    
    -- Foreign key constraints
    FOREIGN KEY (message_id) REFERENCES messages (id) ON DELETE CASCADE,
    
    -- Data validation
    CHECK (tool_id != ''),
    CHECK (tool_name != ''),
    CHECK (execution_time_ms IS NULL OR execution_time_ms >= 0),
    CHECK (started_at > 0),
    CHECK (completed_at IS NULL OR completed_at >= started_at)
);

-- Analytics table: Aggregated metrics and insights
CREATE TABLE analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    conversation_id TEXT,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    metric_unit TEXT,
    dimensions JSON DEFAULT '{}',
    aggregation_period TEXT, -- 'hour', 'day', 'week', 'month'
    period_start INTEGER NOT NULL,
    period_end INTEGER,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000),
    
    -- Foreign key constraints
    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE,
    
    -- Data validation
    CHECK (metric_name != ''),
    CHECK (period_start > 0),
    CHECK (period_end IS NULL OR period_end >= period_start),
    CHECK (created_at > 0)
);

-- Files table: Track source JSONL files
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    file_path TEXT NOT NULL UNIQUE,
    file_name TEXT NOT NULL,
    file_size INTEGER NOT NULL DEFAULT 0,
    last_modified INTEGER NOT NULL,
    checksum TEXT NOT NULL,
    read_position INTEGER NOT NULL DEFAULT 0,
    line_count INTEGER NOT NULL DEFAULT 0,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'error', 'archived')),
    error_message TEXT,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000),
    updated_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000),
    
    -- Foreign key constraints
    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
    
    -- Data validation
    CHECK (file_path != ''),
    CHECK (file_name != ''),
    CHECK (file_size >= 0),
    CHECK (last_modified > 0),
    CHECK (checksum != ''),
    CHECK (read_position >= 0),
    CHECK (line_count >= 0),
    CHECK (created_at > 0),
    CHECK (updated_at >= created_at)
);
```

### **Indexes for Performance Optimization**

```sql
-- Primary performance indexes
CREATE INDEX idx_conversations_project_time ON conversations(project_id, start_time DESC);
CREATE INDEX idx_conversations_session ON conversations(session_id, project_id);
CREATE INDEX idx_conversations_status ON conversations(status, project_id);

CREATE INDEX idx_messages_conversation_time ON messages(conversation_id, timestamp ASC);
CREATE INDEX idx_messages_timestamp ON messages(timestamp DESC);
CREATE INDEX idx_messages_type ON messages(type, conversation_id);
CREATE INDEX idx_messages_parent ON messages(parent_id);
CREATE INDEX idx_messages_content_hash ON messages(content_hash);

CREATE INDEX idx_tool_executions_message ON tool_executions(message_id);
CREATE INDEX idx_tool_executions_tool_name ON tool_executions(tool_name, status);
CREATE INDEX idx_tool_executions_status ON tool_executions(status, started_at);

CREATE INDEX idx_analytics_project_metric ON analytics(project_id, metric_name, period_start);
CREATE INDEX idx_analytics_conversation ON analytics(conversation_id, metric_name);
CREATE INDEX idx_analytics_period ON analytics(aggregation_period, period_start);

CREATE INDEX idx_files_project ON files(project_id, status);
CREATE INDEX idx_files_path ON files(file_path);
CREATE INDEX idx_files_modified ON files(last_modified DESC);

CREATE INDEX idx_projects_active ON projects(is_active, last_activity DESC);
CREATE INDEX idx_projects_name ON projects(name);
```

### **Full-Text Search Implementation**

```sql
-- Full-text search virtual table
CREATE VIRTUAL TABLE messages_fts USING fts5(
    content,
    tool_usage,
    metadata,
    content=messages,
    content_rowid=id,
    tokenize='porter unicode61'
);

-- Populate FTS table
INSERT INTO messages_fts(rowid, content, tool_usage, metadata)
SELECT rowid, content, 
       COALESCE(json_extract(tool_usage, '$'), ''),
       COALESCE(json_extract(metadata, '$'), '')
FROM messages;

-- FTS triggers for automatic maintenance
CREATE TRIGGER messages_fts_insert AFTER INSERT ON messages BEGIN
    INSERT INTO messages_fts(rowid, content, tool_usage, metadata) 
    VALUES (
        new.rowid, 
        new.content,
        COALESCE(json_extract(new.tool_usage, '$'), ''),
        COALESCE(json_extract(new.metadata, '$'), '')
    );
END;

CREATE TRIGGER messages_fts_update AFTER UPDATE ON messages BEGIN
    UPDATE messages_fts SET 
        content = new.content,
        tool_usage = COALESCE(json_extract(new.tool_usage, '$'), ''),
        metadata = COALESCE(json_extract(new.metadata, '$'), '')
    WHERE rowid = new.rowid;
END;

CREATE TRIGGER messages_fts_delete AFTER DELETE ON messages BEGIN
    DELETE FROM messages_fts WHERE rowid = old.rowid;
END;
```

---

## 🔧 **Data Access Layer**

### **Core Database Manager**

```typescript
class DatabaseManager {
    private db: Database;
    private readonly dbPath: string;
    private readonly config: DatabaseConfig;

    constructor(dbPath: string, config: DatabaseConfig = {}) {
        this.dbPath = dbPath;
        this.config = {
            walMode: true,
            busyTimeout: 5000,
            cacheSize: 10000,
            mmapSize: 268435456, // 256MB
            synchronous: 'NORMAL',
            tempStore: 'memory',
            ...config
        };
    }

    async initialize(): Promise<void> {
        this.db = new Database(this.dbPath);
        
        // Configure SQLite for optimal performance
        await this.configure();
        
        // Run migrations
        await this.runMigrations();
        
        // Setup connection pool
        await this.setupConnectionPool();
        
        // Initialize analytics
        await this.initializeAnalytics();
    }

    private async configure(): Promise<void> {
        const pragmas = [
            `PRAGMA journal_mode = ${this.config.walMode ? 'WAL' : 'DELETE'}`,
            `PRAGMA synchronous = ${this.config.synchronous}`,
            `PRAGMA cache_size = ${this.config.cacheSize}`,
            `PRAGMA temp_store = ${this.config.tempStore}`,
            `PRAGMA mmap_size = ${this.config.mmapSize}`,
            `PRAGMA busy_timeout = ${this.config.busyTimeout}`,
            'PRAGMA foreign_keys = ON',
            'PRAGMA optimize'
        ];

        for (const pragma of pragmas) {
            this.db.exec(pragma);
        }
    }

    async createProject(projectData: CreateProjectData): Promise<Project> {
        const stmt = this.db.prepare(`
            INSERT INTO projects (name, path, description, settings, metadata)
            VALUES (?, ?, ?, ?, ?)
        `);

        const result = stmt.run(
            projectData.name,
            projectData.path,
            projectData.description || null,
            JSON.stringify(projectData.settings || {}),
            JSON.stringify(projectData.metadata || {})
        );

        return this.getProjectById(result.lastInsertRowid as number);
    }

    async createConversation(conversationData: CreateConversationData): Promise<Conversation> {
        return this.db.transaction(() => {
            const stmt = this.db.prepare(`
                INSERT INTO conversations (
                    id, project_id, session_id, start_time, metadata
                ) VALUES (?, ?, ?, ?, ?)
            `);

            stmt.run(
                conversationData.id,
                conversationData.projectId,
                conversationData.sessionId,
                conversationData.startTime,
                JSON.stringify(conversationData.metadata || {})
            );

            // Update project activity
            this.updateProjectActivity(conversationData.projectId);

            return this.getConversationById(conversationData.id);
        })();
    }

    async insertMessage(messageData: CreateMessageData): Promise<Message> {
        return this.db.transaction(() => {
            const contentHash = this.generateContentHash(messageData.content);
            
            const stmt = this.db.prepare(`
                INSERT INTO messages (
                    id, conversation_id, timestamp, type, role, content, 
                    content_hash, token_count, parent_id, depth, tool_usage, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            `);

            stmt.run(
                messageData.id,
                messageData.conversationId,
                messageData.timestamp,
                messageData.type,
                messageData.role,
                messageData.content,
                contentHash,
                messageData.tokenCount || 0,
                messageData.parentId || null,
                messageData.depth || 0,
                JSON.stringify(messageData.toolUsage || null),
                JSON.stringify(messageData.metadata || {})
            );

            // Update conversation statistics
            this.updateConversationStats(messageData.conversationId);

            // Insert tool executions if present
            if (messageData.toolUsage && messageData.toolUsage.length > 0) {
                this.insertToolExecutions(messageData.id, messageData.toolUsage);
            }

            return this.getMessageById(messageData.id);
        })();
    }

    async searchMessages(query: SearchQuery): Promise<SearchResult> {
        const { text, projectId, conversationId, messageType, limit = 50, offset = 0 } = query;
        
        let sql = `
            SELECT m.*, c.project_id, p.name as project_name,
                   snippet(messages_fts, 0, '<mark>', '</mark>', '...', 32) as highlight
            FROM messages_fts 
            JOIN messages m ON messages_fts.rowid = m.rowid
            JOIN conversations c ON m.conversation_id = c.id
            JOIN projects p ON c.project_id = p.id
            WHERE messages_fts MATCH ?
        `;
        
        const params: any[] = [text];
        
        if (projectId) {
            sql += ' AND c.project_id = ?';
            params.push(projectId);
        }
        
        if (conversationId) {
            sql += ' AND m.conversation_id = ?';
            params.push(conversationId);
        }
        
        if (messageType) {
            sql += ' AND m.type = ?';
            params.push(messageType);
        }
        
        sql += ' ORDER BY rank LIMIT ? OFFSET ?';
        params.push(limit, offset);
        
        const stmt = this.db.prepare(sql);
        const results = stmt.all(...params);
        
        return {
            results: results.map(row => this.mapRowToMessage(row)),
            total: this.getSearchResultCount(text, projectId, conversationId, messageType),
            query,
            executionTimeMs: 0 // TODO: Implement timing
        };
    }
}
```

### **Performance Optimization Utilities**

```typescript
class DatabaseOptimizer {
    private db: Database;
    private analyzeThreshold = 1000; // Analyze after 1000 operations
    private operationCount = 0;

    constructor(db: Database) {
        this.db = db;
    }

    async optimizeDatabase(): Promise<OptimizationResult> {
        const startTime = Date.now();
        const initialSize = await this.getDatabaseSize();
        
        // Run ANALYZE to update query planner statistics
        this.db.exec('ANALYZE');
        
        // Optimize indexes
        this.db.exec('PRAGMA optimize');
        
        // Vacuum if needed (careful with large databases)
        if (await this.shouldVacuum()) {
            this.db.exec('VACUUM');
        }
        
        // WAL checkpoint
        this.db.exec('PRAGMA wal_checkpoint(FULL)');
        
        const finalSize = await this.getDatabaseSize();
        const duration = Date.now() - startTime;
        
        return {
            duration,
            initialSize,
            finalSize,
            spaceReclaimed: initialSize - finalSize,
            optimizationsApplied: ['analyze', 'optimize', 'checkpoint']
        };
    }

    async getPerformanceMetrics(): Promise<PerformanceMetrics> {
        const stats = this.db.prepare(`
            SELECT 
                (SELECT COUNT(*) FROM projects) as project_count,
                (SELECT COUNT(*) FROM conversations) as conversation_count,
                (SELECT COUNT(*) FROM messages) as message_count,
                (SELECT COUNT(*) FROM tool_executions) as tool_execution_count,
                (SELECT AVG(message_count) FROM conversations) as avg_messages_per_conversation,
                (SELECT AVG(LENGTH(content)) FROM messages) as avg_message_length
        `).get();

        const cacheStats = this.db.prepare('PRAGMA cache_size').get();
        const pageSize = this.db.prepare('PRAGMA page_size').get();
        const pageCount = this.db.prepare('PRAGMA page_count').get();
        
        return {
            ...stats,
            cache_size: cacheStats['cache_size'],
            page_size: pageSize['page_size'],
            page_count: pageCount['page_count'],
            database_size_mb: (pageSize['page_size'] * pageCount['page_count']) / (1024 * 1024)
        };
    }

    trackOperation(): void {
        this.operationCount++;
        
        if (this.operationCount >= this.analyzeThreshold) {
            // Run optimization asynchronously
            setImmediate(() => {
                this.db.exec('PRAGMA optimize');
                this.operationCount = 0;
            });
        }
    }
}
```

---

## 🔒 **Security and Data Integrity**

### **Data Validation Layer**

```typescript
class DataValidator {
    static validateProject(data: any): ValidationResult {
        const errors: string[] = [];
        
        if (!data.name || typeof data.name !== 'string' || data.name.trim().length === 0) {
            errors.push('Project name is required and must be non-empty string');
        }
        
        if (!data.path || typeof data.path !== 'string' || data.path.trim().length === 0) {
            errors.push('Project path is required and must be non-empty string');
        }
        
        if (data.name && data.name.length > 255) {
            errors.push('Project name must not exceed 255 characters');
        }
        
        if (data.description && data.description.length > 2000) {
            errors.push('Project description must not exceed 2000 characters');
        }
        
        return {
            isValid: errors.length === 0,
            errors
        };
    }

    static validateMessage(data: any): ValidationResult {
        const errors: string[] = [];
        
        if (!data.id || typeof data.id !== 'string') {
            errors.push('Message ID is required and must be string');
        }
        
        if (!data.conversationId || typeof data.conversationId !== 'string') {
            errors.push('Conversation ID is required and must be string');
        }
        
        if (!data.timestamp || typeof data.timestamp !== 'number' || data.timestamp <= 0) {
            errors.push('Timestamp is required and must be positive number');
        }
        
        if (!['user', 'assistant', 'system'].includes(data.type)) {
            errors.push('Message type must be one of: user, assistant, system');
        }
        
        if (!data.content || typeof data.content !== 'string' || data.content.trim().length === 0) {
            errors.push('Message content is required and must be non-empty string');
        }
        
        if (data.content && data.content.length > 1000000) { // 1MB
            errors.push('Message content must not exceed 1MB');
        }
        
        if (data.tokenCount && (typeof data.tokenCount !== 'number' || data.tokenCount < 0)) {
            errors.push('Token count must be non-negative number');
        }
        
        return {
            isValid: errors.length === 0,
            errors
        };
    }
}
```

### **Backup and Recovery**

```typescript
class BackupManager {
    private db: Database;
    private backupConfig: BackupConfig;

    constructor(db: Database, config: BackupConfig) {
        this.db = db;
        this.backupConfig = config;
    }

    async createBackup(type: 'full' | 'incremental' = 'full'): Promise<BackupResult> {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const backupPath = path.join(this.backupConfig.backupDir, `backup-${timestamp}.db`);
        
        if (type === 'full') {
            return this.createFullBackup(backupPath);
        } else {
            return this.createIncrementalBackup(backupPath);
        }
    }

    private async createFullBackup(backupPath: string): Promise<BackupResult> {
        const startTime = Date.now();
        
        // Use SQLite's backup API for hot backup
        await this.db.backup(backupPath);
        
        // Verify backup integrity
        const isValid = await this.verifyBackup(backupPath);
        
        if (!isValid) {
            throw new Error('Backup verification failed');
        }
        
        const stats = await fs.stat(backupPath);
        
        return {
            type: 'full',
            path: backupPath,
            size: stats.size,
            duration: Date.now() - startTime,
            verified: true,
            timestamp: new Date()
        };
    }

    async restoreFromBackup(backupPath: string): Promise<void> {
        // Verify backup before restoration
        const isValid = await this.verifyBackup(backupPath);
        if (!isValid) {
            throw new Error('Cannot restore from invalid backup');
        }

        // Close current database
        this.db.close();
        
        // Replace database file
        await fs.copyFile(backupPath, this.db.name);
        
        // Reopen database
        this.db = new Database(this.db.name);
        
        // Verify restoration
        await this.verifyDatabaseIntegrity();
    }

    private async verifyBackup(backupPath: string): Promise<boolean> {
        try {
            const testDb = new Database(backupPath, { readonly: true });
            
            // Run integrity check
            const result = testDb.prepare('PRAGMA integrity_check').get();
            testDb.close();
            
            return result['integrity_check'] === 'ok';
        } catch {
            return false;
        }
    }

    async scheduleAutoBackup(): Promise<void> {
        const interval = this.backupConfig.autoBackupInterval || 24 * 60 * 60 * 1000; // 24 hours
        
        setInterval(async () => {
            try {
                await this.createBackup('incremental');
                await this.cleanOldBackups();
            } catch (error) {
                console.error('Auto backup failed:', error);
            }
        }, interval);
    }
}
```

---

## 📊 **Analytics and Reporting**

### **Metrics Aggregation**

```typescript
class AnalyticsEngine {
    private db: Database;

    constructor(db: Database) {
        this.db = db;
    }

    async generateProjectMetrics(projectId: number, timeRange: TimeRange): Promise<ProjectMetrics> {
        const conversationMetrics = this.db.prepare(`
            SELECT 
                COUNT(*) as total_conversations,
                AVG(message_count) as avg_messages_per_conversation,
                AVG(julianday(datetime(end_time/1000, 'unixepoch')) - 
                    julianday(datetime(start_time/1000, 'unixepoch'))) * 24 * 60 as avg_duration_minutes,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_conversations,
                COUNT(CASE WHEN status = 'error' THEN 1 END) as error_conversations
            FROM conversations 
            WHERE project_id = ? 
                AND start_time BETWEEN ? AND ?
        `).get(projectId, timeRange.start, timeRange.end);

        const messageMetrics = this.db.prepare(`
            SELECT 
                COUNT(*) as total_messages,
                COUNT(CASE WHEN type = 'user' THEN 1 END) as user_messages,
                COUNT(CASE WHEN type = 'assistant' THEN 1 END) as assistant_messages,
                COUNT(CASE WHEN type = 'system' THEN 1 END) as system_messages,
                AVG(LENGTH(content)) as avg_message_length,
                SUM(token_count) as total_tokens
            FROM messages m
            JOIN conversations c ON m.conversation_id = c.id
            WHERE c.project_id = ? 
                AND m.timestamp BETWEEN ? AND ?
        `).get(projectId, timeRange.start, timeRange.end);

        const toolMetrics = this.db.prepare(`
            SELECT 
                COUNT(*) as total_tool_executions,
                COUNT(CASE WHEN status = 'success' THEN 1 END) as successful_executions,
                COUNT(CASE WHEN status = 'error' THEN 1 END) as failed_executions,
                AVG(execution_time_ms) as avg_execution_time,
                COUNT(DISTINCT tool_name) as unique_tools_used
            FROM tool_executions te
            JOIN messages m ON te.message_id = m.id
            JOIN conversations c ON m.conversation_id = c.id
            WHERE c.project_id = ? 
                AND te.started_at BETWEEN ? AND ?
        `).get(projectId, timeRange.start, timeRange.end);

        return {
            projectId,
            timeRange,
            conversations: conversationMetrics,
            messages: messageMetrics,
            tools: toolMetrics,
            generatedAt: Date.now()
        };
    }

    async getTopTools(projectId?: number, limit = 10): Promise<ToolUsageStats[]> {
        let sql = `
            SELECT 
                tool_name,
                COUNT(*) as usage_count,
                COUNT(CASE WHEN status = 'success' THEN 1 END) as success_count,
                COUNT(CASE WHEN status = 'error' THEN 1 END) as error_count,
                AVG(execution_time_ms) as avg_execution_time,
                MIN(execution_time_ms) as min_execution_time,
                MAX(execution_time_ms) as max_execution_time
            FROM tool_executions te
        `;

        const params: any[] = [];

        if (projectId) {
            sql += `
                JOIN messages m ON te.message_id = m.id
                JOIN conversations c ON m.conversation_id = c.id
                WHERE c.project_id = ?
            `;
            params.push(projectId);
        }

        sql += `
            GROUP BY tool_name 
            ORDER BY usage_count DESC 
            LIMIT ?
        `;
        params.push(limit);

        return this.db.prepare(sql).all(...params);
    }

    async createAnalyticsView(): Promise<void> {
        // Create materialized view for common analytics queries
        this.db.exec(`
            CREATE VIEW IF NOT EXISTS conversation_analytics AS
            SELECT 
                c.id as conversation_id,
                c.project_id,
                c.session_id,
                c.start_time,
                c.end_time,
                c.message_count,
                c.tool_usage_count,
                COUNT(m.id) as actual_message_count,
                COUNT(CASE WHEN m.type = 'user' THEN 1 END) as user_message_count,
                COUNT(CASE WHEN m.type = 'assistant' THEN 1 END) as assistant_message_count,
                AVG(LENGTH(m.content)) as avg_message_length,
                SUM(m.token_count) as total_tokens,
                MIN(m.timestamp) as first_message_time,
                MAX(m.timestamp) as last_message_time,
                (MAX(m.timestamp) - MIN(m.timestamp)) / 1000.0 / 60.0 as duration_minutes
            FROM conversations c
            LEFT JOIN messages m ON c.id = m.conversation_id
            GROUP BY c.id
        `);
    }
}
```

---

## 🧪 **Testing Strategy**

### **Database Testing Framework**

```typescript
describe('Database Performance Tests', () => {
    let db: DatabaseManager;
    let testData: TestDataGenerator;

    beforeAll(async () => {
        db = new DatabaseManager(':memory:', { walMode: false }); // In-memory for tests
        await db.initialize();
        testData = new TestDataGenerator();
    });

    describe('Write Performance', () => {
        it('should handle high-volume message insertion', async () => {
            const projectId = await testData.createTestProject(db);
            const conversationId = await testData.createTestConversation(db, projectId);
            
            const messageCount = 10000;
            const messages = testData.generateMessages(messageCount, conversationId);
            
            const startTime = Date.now();
            
            // Batch insert messages
            await db.transaction(() => {
                messages.forEach(message => {
                    db.insertMessage(message);
                });
            });
            
            const duration = Date.now() - startTime;
            const messagesPerSecond = messageCount / (duration / 1000);
            
            expect(messagesPerSecond).toBeGreaterThan(1000);
            expect(duration).toBeLessThan(10000); // 10 seconds max
        });

        it('should maintain performance under concurrent writes', async () => {
            const concurrentWriters = 10;
            const messagesPerWriter = 1000;
            
            const promises = Array.from({ length: concurrentWriters }, async (_, i) => {
                const projectId = await testData.createTestProject(db, `project-${i}`);
                const conversationId = await testData.createTestConversation(db, projectId);
                const messages = testData.generateMessages(messagesPerWriter, conversationId);
                
                const startTime = Date.now();
                
                for (const message of messages) {
                    await db.insertMessage(message);
                }
                
                return Date.now() - startTime;
            });
            
            const durations = await Promise.all(promises);
            const maxDuration = Math.max(...durations);
            
            expect(maxDuration).toBeLessThan(30000); // 30 seconds max per writer
        });
    });

    describe('Read Performance', () => {
        it('should perform fast message queries', async () => {
            // Setup large dataset
            await testData.createLargeDataset(db, {
                projects: 10,
                conversationsPerProject: 100,
                messagesPerConversation: 100
            });
            
            const startTime = Date.now();
            
            const results = await db.searchMessages({
                text: 'test query',
                limit: 50
            });
            
            const duration = Date.now() - startTime;
            
            expect(duration).toBeLessThan(500); // 500ms max
            expect(results.results.length).toBeLessThanOrEqual(50);
        });

        it('should handle complex analytics queries efficiently', async () => {
            const projectId = await testData.createLargeProject(db);
            
            const startTime = Date.now();
            
            const analytics = new AnalyticsEngine(db);
            const metrics = await analytics.generateProjectMetrics(projectId, {
                start: Date.now() - 30 * 24 * 60 * 60 * 1000, // 30 days ago
                end: Date.now()
            });
            
            const duration = Date.now() - startTime;
            
            expect(duration).toBeLessThan(1000); // 1 second max
            expect(metrics.conversations.total_conversations).toBeGreaterThan(0);
        });
    });

    describe('Full-Text Search Performance', () => {
        it('should perform fast text searches on large datasets', async () => {
            await testData.createSearchableDataset(db, 100000); // 100k messages
            
            const queries = [
                'simple query',
                'complex AND query OR test',
                '"exact phrase match"',
                'tool* usage',
                'NEAR(word1, word2, 5)'
            ];
            
            for (const query of queries) {
                const startTime = Date.now();
                
                const results = await db.searchMessages({
                    text: query,
                    limit: 20
                });
                
                const duration = Date.now() - startTime;
                
                expect(duration).toBeLessThan(500); // 500ms max per query
            }
        });
    });
});
```

---

## 🚀 **Deployment and Monitoring**

### **Production Configuration**

```typescript
const productionDbConfig: DatabaseConfig = {
    walMode: true,
    synchronous: 'NORMAL',
    cacheSize: 20000, // 20MB cache
    mmapSize: 1073741824, // 1GB memory mapped
    tempStore: 'memory',
    busyTimeout: 10000, // 10 seconds
    connectionPoolSize: 20,
    enableWalAutoCheckpoint: true,
    walAutocheckpointPages: 1000,
    enableOptimize: true,
    optimizeInterval: 3600000, // 1 hour
    backup: {
        enabled: true,
        backupDir: '/var/backups/ccobservatory',
        autoBackupInterval: 21600000, // 6 hours
        retentionDays: 30,
        compressionEnabled: true
    },
    monitoring: {
        enabled: true,
        metricsInterval: 60000, // 1 minute
        slowQueryThreshold: 1000, // 1 second
        enableQueryLogging: false // Only in debug mode
    }
};
```

### **Health Monitoring**

```typescript
class DatabaseHealthMonitor {
    private db: Database;
    private metrics: DatabaseMetrics = {
        queryCount: 0,
        errorCount: 0,
        slowQueryCount: 0,
        avgQueryTime: 0,
        lastOptimization: 0
    };

    constructor(db: Database) {
        this.db = db;
        this.startMonitoring();
    }

    private startMonitoring(): void {
        setInterval(() => {
            this.collectMetrics();
            this.checkHealth();
        }, 60000); // Every minute
    }

    private async collectMetrics(): Promise<void> {
        try {
            // Check database size
            const stats = this.db.prepare('PRAGMA page_count, page_size').all();
            const databaseSize = stats[0].page_count * stats[0].page_size;
            
            // Check WAL file size
            const walInfo = this.db.prepare('PRAGMA wal_checkpoint(PASSIVE)').get();
            
            // Check cache hit ratio
            const cacheStats = this.db.prepare('PRAGMA cache_size').get();
            
            this.metrics.databaseSize = databaseSize;
            this.metrics.walSize = walInfo.log * stats[0].page_size;
            this.metrics.cacheHitRatio = this.calculateCacheHitRatio();
            
        } catch (error) {
            console.error('Failed to collect database metrics:', error);
            this.metrics.errorCount++;
        }
    }

    private checkHealth(): DatabaseHealth {
        const health: DatabaseHealth = {
            status: 'healthy',
            issues: [],
            metrics: this.metrics,
            timestamp: Date.now()
        };

        // Check for issues
        if (this.metrics.errorCount > 10) {
            health.status = 'unhealthy';
            health.issues.push('High error rate detected');
        }

        if (this.metrics.slowQueryCount > 100) {
            health.status = 'degraded';
            health.issues.push('High number of slow queries');
        }

        if (this.metrics.walSize > 100 * 1024 * 1024) { // 100MB
            health.status = 'warning';
            health.issues.push('WAL file is large, checkpoint recommended');
        }

        return health;
    }
}
```

This comprehensive database architecture specification provides the foundation for a high-performance, scalable, and reliable data storage system for the Claude Code Observatory project.