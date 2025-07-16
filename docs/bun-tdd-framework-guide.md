# Bun TDD Framework Guide for Claude Code Observatory

## Overview

This guide provides a comprehensive testing framework for the Claude Code Observatory project using Bun's built-in test runner. The framework supports the Red-Green-Refactor TDD cycle with structured testing patterns optimized for our monorepo architecture.

## 1. Bun Test Runner Capabilities

### Core Features
- **Native Speed**: 13-15x faster than Jest with parallel execution
- **Zero Configuration**: Works out-of-the-box with TypeScript
- **Jest Compatibility**: Familiar API for easy migration
- **Built-in Coverage**: No additional tools required
- **Watch Mode**: Real-time test execution during development
- **Snapshot Testing**: Built-in snapshot support
- **Mocking**: Complete mock and spy capabilities

### Key Commands
```bash
# Run all tests
bun test

# Watch mode for TDD
bun test --watch

# Coverage reporting
bun test --coverage

# Run specific test files
bun test src/**/*.test.ts

# Run tests with filter
bun test --filter "auth"

# Parallel execution
bun test --parallel

# Bail after failures
bun test --bail=5
```

## 2. Project Structure for Testing

### Monorepo Test Organization
```
claude-code-observatory/
├── packages/
│   ├── core/
│   │   ├── src/
│   │   │   ├── types.ts
│   │   │   └── types.test.ts          # Co-located unit tests
│   │   ├── tests/
│   │   │   ├── integration/           # Integration tests
│   │   │   ├── fixtures/              # Test data
│   │   │   └── setup.ts               # Test setup
│   │   └── bunfig.toml                # Package-specific config
│   ├── backend/
│   │   ├── src/
│   │   │   ├── api/
│   │   │   │   ├── conversations.ts
│   │   │   │   └── conversations.test.ts
│   │   │   ├── services/
│   │   │   │   ├── file-monitor.ts
│   │   │   │   └── file-monitor.test.ts
│   │   │   └── database/
│   │   │       ├── queries.ts
│   │   │       └── queries.test.ts
│   │   ├── tests/
│   │   │   ├── integration/
│   │   │   ├── e2e/
│   │   │   ├── fixtures/
│   │   │   └── setup.ts
│   │   └── bunfig.toml
│   └── frontend/
│       ├── src/
│       │   ├── lib/
│       │   │   ├── components/
│       │   │   │   ├── ConversationList.svelte
│       │   │   │   └── ConversationList.test.ts
│       │   │   └── stores/
│       │   │       ├── conversations.ts
│       │   │       └── conversations.test.ts
│       │   └── routes/
│       │       ├── +page.svelte
│       │       └── +page.test.ts
│       ├── tests/
│       │   ├── integration/
│       │   ├── e2e/
│       │   └── setup.ts
│       └── bunfig.toml
├── test-utils/                        # Shared test utilities
│   ├── src/
│   │   ├── factories/                 # Test data factories
│   │   ├── matchers/                  # Custom matchers
│   │   ├── mocks/                     # Mock implementations
│   │   └── helpers/                   # Test helpers
│   └── package.json
├── bunfig.toml                        # Root configuration
└── package.json                       # Workspace definition
```

### Test File Naming Conventions
- **Unit Tests**: `*.test.ts` (co-located with source)
- **Integration Tests**: `tests/integration/*.test.ts`
- **End-to-End Tests**: `tests/e2e/*.test.ts`
- **Test Utilities**: `test-utils/src/**/*.ts`

## 3. Configuration Setup

### Root `bunfig.toml`
```toml
[workspace]
packages = ["packages/*", "test-utils"]

[test]
# Global test configuration
coverage = true
coverageThreshold = { line = 0.8, function = 0.8, statement = 0.8 }
coverageReporter = ["text", "lcov", "html"]
coverageDirectory = "coverage"
smol = false  # Use full memory for faster tests
timeout = 30000  # 30 second timeout
bail = 10  # Stop after 10 failures

# Global preload scripts
preload = ["./test-utils/src/global-setup.ts"]

# Test file patterns
testNamePattern = ["**/*.test.{ts,js}", "**/*.spec.{ts,js}"]
```

### Package-Specific `bunfig.toml` (Backend Example)
```toml
[test]
# Package-specific preload
preload = [
  "../test-utils/src/global-setup.ts",
  "./tests/setup.ts"
]

# Environment variables for tests
env = {
  NODE_ENV = "test",
  DATABASE_URL = "postgresql://test:test@localhost:5433/ccobservatory_test",
  SUPABASE_URL = "http://localhost:54321",
  SUPABASE_ANON_KEY = "test_key"
}

# Test-specific root directory
root = "src"

# Coverage exclusions
coveragePathIgnorePatterns = [
  "tests/",
  "**/*.test.ts",
  "**/node_modules/"
]
```

### Root `package.json` Workspace Definition
```json
{
  "name": "claude-code-observatory",
  "workspaces": [
    "packages/*",
    "test-utils"
  ],
  "scripts": {
    "test": "bun test",
    "test:watch": "bun test --watch",
    "test:coverage": "bun test --coverage",
    "test:unit": "bun test --filter '**/src/**'",
    "test:integration": "bun test --filter '**/tests/integration/**'",
    "test:e2e": "bun test --filter '**/tests/e2e/**'",
    "test:backend": "bun test --filter 'packages/backend/**'",
    "test:frontend": "bun test --filter 'packages/frontend/**'",
    "test:clean": "rm -rf coverage && rm -rf packages/*/coverage"
  }
}
```

## 4. Test Utilities and Shared Code

### Global Setup (`test-utils/src/global-setup.ts`)
```typescript
import { beforeAll, afterAll, beforeEach, afterEach } from "bun:test";
import { TestDatabase } from "./database";
import { MockFileSystem } from "./mocks/file-system";

// Global test database
let testDb: TestDatabase;

beforeAll(async () => {
  // Initialize test database
  testDb = new TestDatabase();
  await testDb.setup();
  
  // Setup global mocks
  MockFileSystem.setup();
  
  // Set test environment
  process.env.NODE_ENV = "test";
});

afterAll(async () => {
  // Cleanup test database
  await testDb.teardown();
  
  // Cleanup mocks
  MockFileSystem.teardown();
});

beforeEach(async () => {
  // Reset database state
  await testDb.reset();
  
  // Reset mocks
  MockFileSystem.reset();
});

afterEach(() => {
  // Clear any test artifacts
  jest.clearAllMocks?.();
});

// Export utilities for tests
export { testDb };
```

### Test Data Factories (`test-utils/src/factories/index.ts`)
```typescript
import { faker } from "@faker-js/faker";

export interface ConversationFactory {
  id: string;
  sessionId: string;
  projectId: string;
  startTime: Date;
  endTime?: Date;
  messageCount: number;
}

export interface MessageFactory {
  id: string;
  conversationId: string;
  timestamp: Date;
  type: "user" | "assistant" | "system";
  content: string;
  toolUsage?: object;
  parentId?: string;
}

export interface ProjectFactory {
  id: string;
  name: string;
  path: string;
  isActive: boolean;
  createdAt: Date;
}

export class TestDataFactory {
  static createProject(overrides: Partial<ProjectFactory> = {}): ProjectFactory {
    return {
      id: faker.string.uuid(),
      name: faker.company.name(),
      path: faker.system.filePath(),
      isActive: true,
      createdAt: new Date(),
      ...overrides,
    };
  }

  static createConversation(overrides: Partial<ConversationFactory> = {}): ConversationFactory {
    return {
      id: faker.string.uuid(),
      sessionId: faker.string.alphanumeric(16),
      projectId: faker.string.uuid(),
      startTime: faker.date.recent(),
      messageCount: faker.number.int({ min: 1, max: 50 }),
      ...overrides,
    };
  }

  static createMessage(overrides: Partial<MessageFactory> = {}): MessageFactory {
    return {
      id: faker.string.uuid(),
      conversationId: faker.string.uuid(),
      timestamp: faker.date.recent(),
      type: faker.helpers.arrayElement(["user", "assistant", "system"]),
      content: faker.lorem.paragraph(),
      ...overrides,
    };
  }

  static createClaudeMessage(overrides: Partial<any> = {}) {
    return {
      uuid: faker.string.uuid(),
      sessionId: faker.string.alphanumeric(16),
      timestamp: new Date().toISOString(),
      type: "user",
      message: {
        role: "user",
        content: faker.lorem.sentence(),
      },
      cwd: faker.system.directoryPath(),
      ...overrides,
    };
  }

  // Batch creation methods
  static createProjects(count: number, overrides: Partial<ProjectFactory> = {}): ProjectFactory[] {
    return Array.from({ length: count }, () => this.createProject(overrides));
  }

  static createConversations(count: number, overrides: Partial<ConversationFactory> = {}): ConversationFactory[] {
    return Array.from({ length: count }, () => this.createConversation(overrides));
  }

  static createMessages(count: number, overrides: Partial<MessageFactory> = {}): MessageFactory[] {
    return Array.from({ length: count }, () => this.createMessage(overrides));
  }

  // Realistic conversation creation
  static createConversationWithMessages(messageCount: number = 10) {
    const conversation = this.createConversation({ messageCount });
    const messages = Array.from({ length: messageCount }, (_, index) => {
      const isUser = index % 2 === 0;
      return this.createMessage({
        conversationId: conversation.id,
        type: isUser ? "user" : "assistant",
        timestamp: new Date(conversation.startTime.getTime() + index * 60000), // 1 minute apart
        parentId: index > 0 ? `msg-${index - 1}` : undefined,
      });
    });

    return { conversation, messages };
  }
}
```

### Custom Matchers (`test-utils/src/matchers/index.ts`)
```typescript
import { expect } from "bun:test";

declare module "bun:test" {
  interface Matchers<T> {
    toBeValidUuid(): void;
    toBeWithinTimeRange(start: Date, end: Date): void;
    toHaveValidConversationStructure(): void;
    toHaveValidMessageStructure(): void;
    toBeClaudeMessage(): void;
    toMatchAnalyticsSchema(): void;
  }
}

expect.extend({
  toBeValidUuid(received: string) {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
    const pass = uuidRegex.test(received);
    
    return {
      pass,
      message: () => `Expected ${received} to be a valid UUID`,
    };
  },

  toBeWithinTimeRange(received: Date, start: Date, end: Date) {
    const pass = received >= start && received <= end;
    
    return {
      pass,
      message: () => `Expected ${received} to be between ${start} and ${end}`,
    };
  },

  toHaveValidConversationStructure(received: any) {
    const requiredFields = ["id", "sessionId", "projectId", "startTime", "messageCount"];
    const hasAllFields = requiredFields.every(field => field in received);
    const hasValidTypes = typeof received.id === "string" && 
                         typeof received.sessionId === "string" &&
                         typeof received.projectId === "string" &&
                         received.startTime instanceof Date &&
                         typeof received.messageCount === "number";
    
    const pass = hasAllFields && hasValidTypes;
    
    return {
      pass,
      message: () => `Expected object to have valid conversation structure`,
    };
  },

  toHaveValidMessageStructure(received: any) {
    const requiredFields = ["id", "conversationId", "timestamp", "type", "content"];
    const hasAllFields = requiredFields.every(field => field in received);
    const hasValidType = ["user", "assistant", "system"].includes(received.type);
    
    const pass = hasAllFields && hasValidType;
    
    return {
      pass,
      message: () => `Expected object to have valid message structure`,
    };
  },

  toBeClaudeMessage(received: any) {
    const requiredFields = ["uuid", "sessionId", "timestamp", "type", "message"];
    const hasAllFields = requiredFields.every(field => field in received);
    const hasValidStructure = typeof received.message === "object" && 
                             "role" in received.message && 
                             "content" in received.message;
    
    const pass = hasAllFields && hasValidStructure;
    
    return {
      pass,
      message: () => `Expected object to be a valid Claude message`,
    };
  },

  toMatchAnalyticsSchema(received: any) {
    const requiredFields = ["metric_name", "metric_value", "timestamp"];
    const hasAllFields = requiredFields.every(field => field in received);
    const hasValidTypes = typeof received.metric_name === "string" &&
                         typeof received.metric_value === "number" &&
                         received.timestamp instanceof Date;
    
    const pass = hasAllFields && hasValidTypes;
    
    return {
      pass,
      message: () => `Expected object to match analytics schema`,
    };
  },
});
```

### Database Test Helper (`test-utils/src/database.ts`)
```typescript
import { createClient } from "@supabase/supabase-js";

export class TestDatabase {
  private client: any;
  private originalTables: Map<string, any[]> = new Map();

  async setup() {
    this.client = createClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_ANON_KEY!
    );

    // Create test schema
    await this.createTestSchema();
  }

  async teardown() {
    // Drop test data
    await this.dropTestSchema();
  }

  async reset() {
    // Clear all test data but keep schema
    const tables = ["messages", "conversations", "projects", "analytics"];
    
    for (const table of tables) {
      await this.client.from(table).delete().neq("id", "");
    }
  }

  async createTestSchema() {
    // Create test tables if they don't exist
    // This would typically be handled by migrations
  }

  async dropTestSchema() {
    // Clean up test schema
  }

  // Helper methods for test data management
  async insertProject(project: any) {
    const { data, error } = await this.client
      .from("projects")
      .insert(project)
      .select()
      .single();
    
    if (error) throw error;
    return data;
  }

  async insertConversation(conversation: any) {
    const { data, error } = await this.client
      .from("conversations")
      .insert(conversation)
      .select()
      .single();
    
    if (error) throw error;
    return data;
  }

  async insertMessage(message: any) {
    const { data, error } = await this.client
      .from("messages")
      .insert(message)
      .select()
      .single();
    
    if (error) throw error;
    return data;
  }

  // Query helpers
  async getConversations(projectId?: string) {
    let query = this.client.from("conversations").select("*");
    
    if (projectId) {
      query = query.eq("project_id", projectId);
    }
    
    const { data, error } = await query;
    if (error) throw error;
    return data;
  }

  async getMessages(conversationId: string) {
    const { data, error } = await this.client
      .from("messages")
      .select("*")
      .eq("conversation_id", conversationId)
      .order("timestamp", { ascending: true });
    
    if (error) throw error;
    return data;
  }
}
```

### Mock File System (`test-utils/src/mocks/file-system.ts`)
```typescript
import { jest } from "bun:test";
import * as fs from "fs";
import * as path from "path";

export class MockFileSystem {
  private static originalFs: any;
  private static mockFiles: Map<string, string> = new Map();
  private static watchers: Set<any> = new Set();

  static setup() {
    this.originalFs = { ...fs };
    this.mockFiles.clear();
    this.watchers.clear();

    // Mock fs methods
    jest.spyOn(fs, "readFileSync").mockImplementation((filePath: string) => {
      const content = this.mockFiles.get(filePath);
      if (content === undefined) {
        throw new Error(`ENOENT: no such file or directory, open '${filePath}'`);
      }
      return content;
    });

    jest.spyOn(fs, "writeFileSync").mockImplementation((filePath: string, content: string) => {
      this.mockFiles.set(filePath, content);
    });

    jest.spyOn(fs, "existsSync").mockImplementation((filePath: string) => {
      return this.mockFiles.has(filePath);
    });

    jest.spyOn(fs, "watchFile").mockImplementation((filename: string, listener: any) => {
      const watcher = { filename, listener };
      this.watchers.add(watcher);
      return watcher;
    });
  }

  static teardown() {
    jest.restoreAllMocks();
    this.mockFiles.clear();
    this.watchers.clear();
  }

  static reset() {
    this.mockFiles.clear();
    this.watchers.clear();
  }

  // Helper methods for tests
  static createFile(filePath: string, content: string) {
    this.mockFiles.set(filePath, content);
  }

  static createClaudeProject(projectPath: string, sessions: string[] = ["session1"]) {
    // Create project directory structure
    const projectDir = path.join(projectPath, ".claude", "projects", "test-project");
    
    sessions.forEach(sessionId => {
      const sessionFile = path.join(projectDir, `${sessionId}.jsonl`);
      this.createFile(sessionFile, "");
    });

    return projectDir;
  }

  static appendToFile(filePath: string, content: string) {
    const existing = this.mockFiles.get(filePath) || "";
    this.mockFiles.set(filePath, existing + content);
    
    // Trigger file watchers
    this.triggerWatchers(filePath);
  }

  static triggerWatchers(filePath: string) {
    this.watchers.forEach(watcher => {
      if (watcher.filename === filePath) {
        watcher.listener();
      }
    });
  }

  static getFileContent(filePath: string): string | undefined {
    return this.mockFiles.get(filePath);
  }

  static getWatchedFiles(): string[] {
    return Array.from(this.watchers).map(w => w.filename);
  }
}
```

## 5. TDD Testing Patterns

### Red-Green-Refactor Examples

#### Example 1: File Monitor Service (TDD)

```typescript
// packages/backend/src/services/file-monitor.test.ts

import { describe, it, expect, beforeEach, jest } from "bun:test";
import { FileMonitor } from "./file-monitor";
import { MockFileSystem } from "../../../test-utils/src/mocks/file-system";
import { TestDataFactory } from "../../../test-utils/src/factories";

describe("FileMonitor", () => {
  let fileMonitor: FileMonitor;
  let mockCallback: jest.Mock;

  beforeEach(() => {
    MockFileSystem.reset();
    mockCallback = jest.fn();
    fileMonitor = new FileMonitor();
  });

  describe("when watching a directory", () => {
    it("should detect new JSONL files", async () => {
      // RED: Write test first (will fail)
      const projectPath = "/test/project";
      const sessionFile = `${projectPath}/.claude/projects/test/session1.jsonl`;
      
      fileMonitor.watch(projectPath, mockCallback);
      
      // Simulate file creation
      MockFileSystem.createFile(sessionFile, "");
      MockFileSystem.triggerWatchers(sessionFile);
      
      expect(mockCallback).toHaveBeenCalledWith({
        type: "file_created",
        path: sessionFile,
        projectPath,
      });
    });

    it("should process new messages in existing files", async () => {
      // RED: Test for incremental file reading
      const projectPath = "/test/project";
      const sessionFile = `${projectPath}/.claude/projects/test/session1.jsonl`;
      const message = TestDataFactory.createClaudeMessage();
      
      MockFileSystem.createFile(sessionFile, "");
      fileMonitor.watch(projectPath, mockCallback);
      
      // Simulate new message
      MockFileSystem.appendToFile(sessionFile, JSON.stringify(message) + "\n");
      
      expect(mockCallback).toHaveBeenCalledWith({
        type: "message_added",
        path: sessionFile,
        message,
      });
    });

    it("should handle multiple concurrent file changes", async () => {
      // RED: Test for concurrent processing
      const projectPath = "/test/project";
      const files = [
        `${projectPath}/.claude/projects/test/session1.jsonl`,
        `${projectPath}/.claude/projects/test/session2.jsonl`,
      ];
      
      files.forEach(file => MockFileSystem.createFile(file, ""));
      fileMonitor.watch(projectPath, mockCallback);
      
      // Simulate concurrent changes
      const messages = files.map(() => TestDataFactory.createClaudeMessage());
      files.forEach((file, index) => {
        MockFileSystem.appendToFile(file, JSON.stringify(messages[index]) + "\n");
      });
      
      expect(mockCallback).toHaveBeenCalledTimes(2);
    });
  });

  describe("error handling", () => {
    it("should recover from file system errors", async () => {
      // RED: Test error recovery
      const projectPath = "/test/project";
      
      // Mock fs error
      jest.spyOn(fs, "readFileSync").mockImplementationOnce(() => {
        throw new Error("EACCES: permission denied");
      });
      
      fileMonitor.watch(projectPath, mockCallback);
      
      // Should not crash and should retry
      expect(fileMonitor.isWatching()).toBe(true);
    });
  });
});
```

#### Example 2: Conversation Parser (TDD)

```typescript
// packages/backend/src/services/conversation-parser.test.ts

import { describe, it, expect } from "bun:test";
import { ConversationParser } from "./conversation-parser";
import { TestDataFactory } from "../../../test-utils/src/factories";

describe("ConversationParser", () => {
  let parser: ConversationParser;

  beforeEach(() => {
    parser = new ConversationParser();
  });

  describe("parseMessage", () => {
    it("should parse user messages correctly", () => {
      // RED: Write test first
      const claudeMessage = TestDataFactory.createClaudeMessage({
        type: "user",
        message: {
          role: "user",
          content: "Hello, world!",
        },
      });

      const result = parser.parseMessage(JSON.stringify(claudeMessage));

      expect(result).toHaveValidMessageStructure();
      expect(result.type).toBe("user");
      expect(result.content).toBe("Hello, world!");
    });

    it("should extract tool usage from assistant messages", () => {
      // RED: Test tool usage extraction
      const claudeMessage = TestDataFactory.createClaudeMessage({
        type: "assistant",
        message: {
          role: "assistant",
          content: "I'll help you with that.",
          tool_use: {
            name: "read_file",
            input: { path: "/test/file.ts" },
            id: "tool_123",
          },
        },
      });

      const result = parser.parseMessage(JSON.stringify(claudeMessage));

      expect(result.toolUsage).toEqual({
        toolName: "read_file",
        input: { path: "/test/file.ts" },
        toolId: "tool_123",
      });
    });

    it("should handle threading with parent relationships", () => {
      // RED: Test message threading
      const parentMessage = TestDataFactory.createClaudeMessage();
      const childMessage = TestDataFactory.createClaudeMessage({
        parentUuid: parentMessage.uuid,
      });

      const parsedChild = parser.parseMessage(JSON.stringify(childMessage));

      expect(parsedChild.parentId).toBe(parentMessage.uuid);
    });
  });

  describe("parseConversation", () => {
    it("should parse entire conversation from JSONL", () => {
      // RED: Test full conversation parsing
      const messages = [
        TestDataFactory.createClaudeMessage({ type: "user" }),
        TestDataFactory.createClaudeMessage({ type: "assistant" }),
        TestDataFactory.createClaudeMessage({ type: "user" }),
      ];

      const jsonl = messages.map(msg => JSON.stringify(msg)).join("\n");
      const result = parser.parseConversation(jsonl);

      expect(result.messages).toHaveLength(3);
      expect(result.sessionId).toBe(messages[0].sessionId);
      expect(result.startTime).toBeInstanceOf(Date);
    });

    it("should calculate conversation metrics", () => {
      // RED: Test metrics calculation
      const startTime = new Date("2024-01-01T10:00:00Z");
      const endTime = new Date("2024-01-01T10:30:00Z");
      
      const messages = [
        TestDataFactory.createClaudeMessage({ 
          timestamp: startTime.toISOString(),
          type: "user" 
        }),
        TestDataFactory.createClaudeMessage({ 
          timestamp: endTime.toISOString(),
          type: "assistant",
          message: {
            role: "assistant",
            content: "Response",
            tool_use: { name: "test_tool" }
          }
        }),
      ];

      const jsonl = messages.map(msg => JSON.stringify(msg)).join("\n");
      const result = parser.parseConversation(jsonl);

      expect(result.duration).toBe(30 * 60 * 1000); // 30 minutes in ms
      expect(result.messageCount).toBe(2);
      expect(result.toolUsageCount).toBe(1);
    });
  });
});
```

#### Example 3: Frontend Component Testing (TDD)

```typescript
// packages/frontend/src/lib/components/ConversationList.test.ts

import { describe, it, expect, beforeEach } from "bun:test";
import { render, screen, fireEvent } from "@testing-library/svelte";
import { vi } from "vitest";
import ConversationList from "./ConversationList.svelte";
import { TestDataFactory } from "../../../../test-utils/src/factories";
import { conversationStore } from "../stores/conversations";

describe("ConversationList", () => {
  beforeEach(() => {
    conversationStore.set([]);
  });

  describe("rendering", () => {
    it("should display empty state when no conversations", () => {
      // RED: Test empty state
      render(ConversationList);
      
      expect(screen.getByText("No conversations found")).toBeInTheDocument();
    });

    it("should display conversation list", () => {
      // RED: Test conversation rendering
      const conversations = TestDataFactory.createConversations(3);
      conversationStore.set(conversations);

      render(ConversationList);

      conversations.forEach(conv => {
        expect(screen.getByText(conv.sessionId)).toBeInTheDocument();
      });
    });

    it("should show conversation metadata", () => {
      // RED: Test metadata display
      const conversation = TestDataFactory.createConversation({
        messageCount: 15,
        startTime: new Date("2024-01-01T10:00:00Z"),
      });
      
      conversationStore.set([conversation]);
      render(ConversationList);

      expect(screen.getByText("15 messages")).toBeInTheDocument();
      expect(screen.getByText(/Jan 1, 2024/)).toBeInTheDocument();
    });
  });

  describe("interactions", () => {
    it("should emit select event when conversation clicked", async () => {
      // RED: Test selection interaction
      const conversation = TestDataFactory.createConversation();
      conversationStore.set([conversation]);

      const { component } = render(ConversationList);
      const selectSpy = vi.fn();
      component.$on("select", selectSpy);

      const conversationElement = screen.getByText(conversation.sessionId);
      await fireEvent.click(conversationElement);

      expect(selectSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          detail: conversation.id
        })
      );
    });

    it("should filter conversations by search term", async () => {
      // RED: Test search functionality
      const conversations = [
        TestDataFactory.createConversation({ sessionId: "abc123" }),
        TestDataFactory.createConversation({ sessionId: "def456" }),
        TestDataFactory.createConversation({ sessionId: "abc789" }),
      ];
      
      conversationStore.set(conversations);
      render(ConversationList);

      const searchInput = screen.getByPlaceholderText("Search conversations...");
      await fireEvent.input(searchInput, { target: { value: "abc" } });

      expect(screen.getByText("abc123")).toBeInTheDocument();
      expect(screen.queryByText("def456")).not.toBeInTheDocument();
      expect(screen.getByText("abc789")).toBeInTheDocument();
    });
  });

  describe("real-time updates", () => {
    it("should update when new conversations are added", () => {
      // RED: Test real-time updates
      render(ConversationList);
      
      const newConversation = TestDataFactory.createConversation();
      conversationStore.set([newConversation]);

      expect(screen.getByText(newConversation.sessionId)).toBeInTheDocument();
    });
  });
});
```

## 6. Advanced Testing Patterns

### Integration Testing with Database

```typescript
// packages/backend/tests/integration/conversation-api.test.ts

import { describe, it, expect, beforeEach } from "bun:test";
import { testDb } from "../../../../test-utils/src/global-setup";
import { TestDataFactory } from "../../../../test-utils/src/factories";
import { ConversationService } from "../../src/services/conversation-service";

describe("ConversationService Integration", () => {
  let service: ConversationService;

  beforeEach(async () => {
    service = new ConversationService();
  });

  describe("createConversation", () => {
    it("should create conversation and return with ID", async () => {
      const project = TestDataFactory.createProject();
      await testDb.insertProject(project);

      const conversationData = TestDataFactory.createConversation({
        projectId: project.id,
      });

      const result = await service.createConversation(conversationData);

      expect(result).toHaveValidConversationStructure();
      expect(result.id).toBeValidUuid();
      expect(result.projectId).toBe(project.id);
    });

    it("should handle concurrent conversation creation", async () => {
      const project = TestDataFactory.createProject();
      await testDb.insertProject(project);

      const conversations = Array.from({ length: 5 }, () => 
        TestDataFactory.createConversation({ projectId: project.id })
      );

      const promises = conversations.map(conv => 
        service.createConversation(conv)
      );

      const results = await Promise.all(promises);

      expect(results).toHaveLength(5);
      results.forEach(result => {
        expect(result.id).toBeValidUuid();
      });
    });
  });

  describe("getConversationsByProject", () => {
    it("should return conversations for specific project", async () => {
      const project = TestDataFactory.createProject();
      await testDb.insertProject(project);

      const conversations = TestDataFactory.createConversations(3, {
        projectId: project.id,
      });

      for (const conv of conversations) {
        await testDb.insertConversation(conv);
      }

      const result = await service.getConversationsByProject(project.id);

      expect(result).toHaveLength(3);
      result.forEach(conv => {
        expect(conv.projectId).toBe(project.id);
      });
    });

    it("should paginate results correctly", async () => {
      const project = TestDataFactory.createProject();
      await testDb.insertProject(project);

      const conversations = TestDataFactory.createConversations(15, {
        projectId: project.id,
      });

      for (const conv of conversations) {
        await testDb.insertConversation(conv);
      }

      const firstPage = await service.getConversationsByProject(
        project.id, 
        { page: 1, limit: 10 }
      );
      
      const secondPage = await service.getConversationsByProject(
        project.id, 
        { page: 2, limit: 10 }
      );

      expect(firstPage.data).toHaveLength(10);
      expect(secondPage.data).toHaveLength(5);
      expect(firstPage.total).toBe(15);
    });
  });
});
```

### E2E Testing with WebSocket

```typescript
// packages/backend/tests/e2e/websocket-realtime.test.ts

import { describe, it, expect, beforeEach, afterEach } from "bun:test";
import { WebSocket } from "ws";
import { TestDataFactory } from "../../../../test-utils/src/factories";
import { startTestServer, stopTestServer } from "../helpers/test-server";

describe("WebSocket Real-time Updates E2E", () => {
  let serverUrl: string;
  let ws: WebSocket;

  beforeEach(async () => {
    serverUrl = await startTestServer();
  });

  afterEach(async () => {
    if (ws) {
      ws.close();
    }
    await stopTestServer();
  });

  describe("conversation updates", () => {
    it("should broadcast new message events", async () => {
      // Establish WebSocket connection
      ws = new WebSocket(`${serverUrl.replace('http', 'ws')}/ws`);
      
      const messagePromise = new Promise((resolve) => {
        ws.on("message", (data) => {
          const event = JSON.parse(data.toString());
          resolve(event);
        });
      });

      await new Promise(resolve => ws.on("open", resolve));

      // Simulate file system event that should trigger broadcast
      const message = TestDataFactory.createClaudeMessage();
      const response = await fetch(`${serverUrl}/api/conversations/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(message),
      });

      expect(response.ok).toBe(true);

      const receivedEvent = await messagePromise;
      expect(receivedEvent).toEqual({
        type: "new_message",
        data: expect.objectContaining({
          id: expect.any(String),
          content: message.message.content,
        }),
      });
    });

    it("should handle multiple client connections", async () => {
      // Create multiple WebSocket connections
      const clients = Array.from({ length: 3 }, () => 
        new WebSocket(`${serverUrl.replace('http', 'ws')}/ws`)
      );

      const messagePromises = clients.map(client => 
        new Promise(resolve => {
          client.on("message", (data) => {
            resolve(JSON.parse(data.toString()));
          });
        })
      );

      // Wait for all connections to be established
      await Promise.all(clients.map(client => 
        new Promise(resolve => client.on("open", resolve))
      ));

      // Trigger broadcast event
      const message = TestDataFactory.createClaudeMessage();
      await fetch(`${serverUrl}/api/conversations/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(message),
      });

      const receivedEvents = await Promise.all(messagePromises);

      // All clients should receive the same event
      receivedEvents.forEach(event => {
        expect(event.type).toBe("new_message");
        expect(event.data.content).toBe(message.message.content);
      });

      clients.forEach(client => client.close());
    });
  });
});
```

## 7. Performance Testing

```typescript
// packages/backend/tests/performance/file-processing.test.ts

import { describe, it, expect } from "bun:test";
import { performance } from "perf_hooks";
import { FileMonitor } from "../../src/services/file-monitor";
import { TestDataFactory } from "../../../../test-utils/src/factories";
import { MockFileSystem } from "../../../../test-utils/src/mocks/file-system";

describe("File Processing Performance", () => {
  describe("large file handling", () => {
    it("should process 1000 messages within 100ms", async () => {
      const fileMonitor = new FileMonitor();
      const messages = Array.from({ length: 1000 }, () => 
        TestDataFactory.createClaudeMessage()
      );
      
      const jsonl = messages.map(msg => JSON.stringify(msg)).join("\n");
      const projectPath = "/test/project";
      const sessionFile = `${projectPath}/.claude/projects/test/session1.jsonl`;
      
      MockFileSystem.createFile(sessionFile, jsonl);

      let processedCount = 0;
      const startTime = performance.now();

      fileMonitor.watch(projectPath, () => {
        processedCount++;
      });

      MockFileSystem.triggerWatchers(sessionFile);

      // Wait for processing to complete
      await new Promise(resolve => setTimeout(resolve, 50));

      const endTime = performance.now();
      const duration = endTime - startTime;

      expect(processedCount).toBeGreaterThan(0);
      expect(duration).toBeLessThan(100);
    });

    it("should handle concurrent file processing", async () => {
      const fileMonitor = new FileMonitor();
      const fileCount = 10;
      const messagesPerFile = 100;
      
      const files = Array.from({ length: fileCount }, (_, index) => {
        const messages = Array.from({ length: messagesPerFile }, () => 
          TestDataFactory.createClaudeMessage()
        );
        const jsonl = messages.map(msg => JSON.stringify(msg)).join("\n");
        const filePath = `/test/project/.claude/projects/test/session${index}.jsonl`;
        
        MockFileSystem.createFile(filePath, jsonl);
        return filePath;
      });

      let processedFiles = 0;
      const startTime = performance.now();

      fileMonitor.watch("/test/project", () => {
        processedFiles++;
      });

      // Trigger all files simultaneously
      files.forEach(file => MockFileSystem.triggerWatchers(file));

      // Wait for all processing to complete
      await new Promise(resolve => {
        const checkComplete = () => {
          if (processedFiles >= fileCount) {
            resolve(undefined);
          } else {
            setTimeout(checkComplete, 10);
          }
        };
        checkComplete();
      });

      const endTime = performance.now();
      const duration = endTime - startTime;

      expect(processedFiles).toBe(fileCount);
      expect(duration).toBeLessThan(500); // 500ms for 10 files with 100 messages each
    });
  });
});
```

## 8. Coverage and Reporting

### Coverage Configuration

```toml
# Root bunfig.toml - Coverage settings
[test]
coverage = true
coverageDirectory = "coverage"
coverageReporter = ["text", "lcov", "html", "json"]

# Coverage thresholds
coverageThreshold = {
  global = { line = 0.8, function = 0.8, statement = 0.8, branch = 0.7 },
  "packages/core/" = { line = 0.9, function = 0.9 },
  "packages/backend/" = { line = 0.85, function = 0.85 },
  "packages/frontend/" = { line = 0.75, function = 0.75 }
}

# Exclude patterns
coveragePathIgnorePatterns = [
  "node_modules/",
  "**/*.test.ts",
  "**/*.spec.ts",
  "**/tests/",
  "**/__mocks__/",
  "**/coverage/",
  "**/*.d.ts"
]
```

### Custom Test Scripts

```json
{
  "scripts": {
    "test": "bun test",
    "test:watch": "bun test --watch",
    "test:coverage": "bun test --coverage",
    "test:coverage:open": "bun test --coverage && open coverage/lcov-report/index.html",
    
    "test:unit": "bun test --filter '**/src/**/*.test.ts'",
    "test:integration": "bun test --filter '**/tests/integration/**'",
    "test:e2e": "bun test --filter '**/tests/e2e/**'",
    "test:performance": "bun test --filter '**/tests/performance/**'",
    
    "test:backend": "bun test --filter 'packages/backend/**'",
    "test:frontend": "bun test --filter 'packages/frontend/**'",
    "test:core": "bun test --filter 'packages/core/**'",
    
    "test:ci": "bun test --coverage --bail=5",
    "test:debug": "bun test --inspect",
    
    "tdd": "bun test --watch --filter",
    "tdd:backend": "bun test --watch --filter 'packages/backend/**'",
    "tdd:frontend": "bun test --watch --filter 'packages/frontend/**'"
  }
}
```

## 9. CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: ccobservatory_test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5433:5432

    steps:
      - uses: actions/checkout@v4
      
      - uses: oven-sh/setup-bun@v1
        with:
          bun-version: latest
          
      - name: Install dependencies
        run: bun install --frozen-lockfile
        
      - name: Run unit tests
        run: bun test:unit
        
      - name: Run integration tests
        run: bun test:integration
        env:
          DATABASE_URL: postgresql://test:test@localhost:5433/ccobservatory_test
          
      - name: Run E2E tests
        run: bun test:e2e
        
      - name: Generate coverage report
        run: bun test:coverage
        
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info
          fail_ci_if_error: true
```

## 10. Best Practices Summary

### TDD Workflow
1. **Red**: Write failing test first
2. **Green**: Write minimal code to pass
3. **Refactor**: Improve code while keeping tests green
4. **Repeat**: Continue cycle for each feature

### Test Organization
- **Co-locate unit tests** with source files
- **Separate integration tests** in dedicated directories
- **Use descriptive test names** that explain behavior
- **Group related tests** with describe blocks
- **Set up proper test isolation** with beforeEach/afterEach

### Performance Considerations
- **Use Bun's speed advantage** for rapid feedback
- **Parallelize test execution** where possible
- **Mock external dependencies** to avoid slow I/O
- **Use test factories** for consistent data generation
- **Monitor test execution time** and optimize slow tests

### Maintenance
- **Keep tests simple** and focused
- **Update tests when refactoring** code
- **Maintain high coverage** but focus on critical paths
- **Review test failures** regularly and fix promptly
- **Document complex test scenarios** for team understanding

This comprehensive TDD framework provides the foundation for building robust, well-tested code in the Claude Code Observatory project using Bun's powerful testing capabilities.