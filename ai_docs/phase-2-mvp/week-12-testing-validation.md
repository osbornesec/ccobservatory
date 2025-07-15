# Week 12: Comprehensive Testing & User Validation

## Overview
Conduct comprehensive testing, user validation, and final quality assurance for the Claude Code Observatory MVP. This final week of Phase 2 focuses on validation across all quality dimensions, user acceptance testing, and preparation for production release.

## Team Assignments
- **QA Lead**: Test strategy execution, bug tracking, validation sign-off
- **Full-Stack Developer**: Test automation, performance validation, deployment testing
- **UI/UX Developer**: User experience testing, accessibility validation, design consistency
- **Product Manager**: User acceptance testing coordination, stakeholder validation

## Daily Schedule

### Monday: Comprehensive Test Execution
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Automated test suite execution and validation
- **10:30-12:00**: Manual testing for edge cases and user scenarios

#### Afternoon (4 hours)
- **13:00-15:00**: Security testing and vulnerability assessment
- **15:00-17:00**: Performance testing under realistic load conditions

### Tuesday: User Acceptance Testing
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Internal user acceptance testing setup
- **10:30-12:00**: Stakeholder testing sessions and feedback collection

#### Afternoon (4 hours)
- **13:00-15:00**: External beta user testing coordination
- **15:00-17:00**: User feedback analysis and prioritization

### Wednesday: Bug Resolution & Quality Assurance
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Critical bug fixes and regression testing
- **10:30-12:00**: Quality assurance validation and sign-off

#### Afternoon (4 hours)
- **13:00-15:00**: Final integration testing and system validation
- **15:00-17:00**: Documentation review and completion

### Thursday: Production Readiness Testing
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Production environment testing and validation
- **10:30-12:00**: Deployment process testing and rollback validation

#### Afternoon (4 hours)
- **13:00-15:00**: Monitoring and alerting system testing
- **15:00-17:00**: Backup and recovery process validation

### Friday: Final Validation & Release Preparation
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Final acceptance criteria validation
- **10:30-12:00**: Release candidate preparation and signing

#### Afternoon (4 hours)
- **13:00-15:00**: Phase 2 retrospective and lessons learned
- **15:00-17:00**: Phase 3 planning and handoff preparation

## Technical Implementation Details

### Testing Framework Selection & Setup

#### Jest vs Vitest Comparison

**Jest with TypeScript Setup**
```typescript
// jest.config.ts
import type { Config } from 'jest';

const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@shared/(.*)$': '<rootDir>/packages/shared/$1',
    '^@core/(.*)$': '<rootDir>/packages/core/$1'
  },
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    'packages/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.test.{ts,tsx}',
    '!src/**/*.stories.{ts,tsx}'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 85,
      lines: 85,
      statements: 85
    }
  },
  testMatch: [
    '<rootDir>/tests/**/*.test.{ts,tsx}',
    '<rootDir>/packages/**/tests/**/*.test.{ts,tsx}'
  ],
  transform: {
    '^.+\\.(ts|tsx)$': 'ts-jest'
  },
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],
  fakeTimers: {
    enableGlobally: true
  }
};

export default config;
```

**Vitest Configuration (Recommended)**
```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import vue from '@vitejs/plugin-vue';
import { resolve } from 'path';

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['tests/setup.ts'],
    include: ['tests/**/*.test.{ts,tsx}', 'packages/**/tests/**/*.test.{ts,tsx}'],
    coverage: {
      reporter: ['text', 'html', 'json'],
      include: ['src/**/*.{ts,tsx}', 'packages/**/*.{ts,tsx}'],
      exclude: ['src/**/*.d.ts', 'src/**/*.test.{ts,tsx}', 'src/**/*.stories.{ts,tsx}'],
      thresholds: {
        branches: 80,
        functions: 85,
        lines: 85,
        statements: 85
      }
    },
    pool: 'threads',
    poolOptions: {
      threads: {
        singleThread: false,
        isolate: true
      }
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@shared': resolve(__dirname, 'packages/shared'),
      '@core': resolve(__dirname, 'packages/core')
    }
  }
});
```

**Test Setup Configuration**
```typescript
// tests/setup.ts
import { expect, vi } from 'vitest';
import type { TestingLibraryMatchers } from '@testing-library/jest-dom/matchers';
import matchers from '@testing-library/jest-dom/matchers';

// Extend Vitest's expect with Jest DOM matchers
expect.extend(matchers);

// Global test setup
beforeEach(() => {
  // Clear all mocks before each test
  vi.clearAllMocks();
  
  // Reset fake timers
  vi.useRealTimers();
  
  // Clear localStorage
  localStorage.clear();
  
  // Reset any global state
  globalThis.resetBeforeEachTest = true;
});

// Mock WebSocket for testing
const mockWebSocket = vi.fn(() => ({
  send: vi.fn(),
  close: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  readyState: WebSocket.OPEN
}));

vi.stubGlobal('WebSocket', mockWebSocket);

// Mock fetch
const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn()
  }))
});

// Mock IntersectionObserver
const mockIntersectionObserver = vi.fn();
mockIntersectionObserver.mockReturnValue({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn()
});
vi.stubGlobal('IntersectionObserver', mockIntersectionObserver);

// Extend expect for custom matchers
declare module 'vitest' {
  interface Assertion<T = any> extends TestingLibraryMatchers<T, void> {}
  interface AsymmetricMatchersContaining extends TestingLibraryMatchers {}
}
```

### TypeScript Unit Testing Examples

#### Database Layer Testing
```typescript
// tests/unit/database/sqlite-manager.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { SQLiteManager } from '@/database/sqlite-manager';
import { ConversationRepository } from '@/database/repositories/conversation-repository';

describe('SQLiteManager', () => {
  let sqliteManager: SQLiteManager;
  let mockDatabase: any;

  beforeEach(() => {
    mockDatabase = {
      prepare: vi.fn(),
      exec: vi.fn(),
      close: vi.fn(),
      pragma: vi.fn().mockReturnValue([{ journal_mode: 'wal' }])
    };
    
    vi.doMock('better-sqlite3', () => {
      return {
        default: vi.fn(() => mockDatabase)
      };
    });
    
    sqliteManager = new SQLiteManager(':memory:');
  });

  describe('initialization', () => {
    it('should create database connection', () => {
      expect(sqliteManager.isConnected()).toBe(true);
    });

    it('should enable WAL mode', () => {
      expect(mockDatabase.pragma).toHaveBeenCalledWith('journal_mode = WAL');
    });

    it('should create required tables', () => {
      expect(mockDatabase.exec).toHaveBeenCalledWith(
        expect.stringContaining('CREATE TABLE IF NOT EXISTS conversations')
      );
    });
  });

  describe('transaction handling', () => {
    it('should execute transaction successfully', async () => {
      const mockTransaction = vi.fn();
      mockDatabase.transaction = vi.fn().mockReturnValue(mockTransaction);
      
      const callback = vi.fn().mockReturnValue('result');
      
      const result = await sqliteManager.executeTransaction(callback);
      
      expect(mockDatabase.transaction).toHaveBeenCalledWith(callback);
      expect(result).toBe('result');
    });

    it('should handle transaction errors', async () => {
      const mockTransaction = vi.fn().mockImplementation(() => {
        throw new Error('Transaction failed');
      });
      mockDatabase.transaction = vi.fn().mockReturnValue(mockTransaction);
      
      const callback = vi.fn();
      
      await expect(sqliteManager.executeTransaction(callback))
        .rejects.toThrow('Transaction failed');
    });
  });

  describe('prepared statements', () => {
    it('should prepare and cache statements', () => {
      const mockStatement = { run: vi.fn(), get: vi.fn(), all: vi.fn() };
      mockDatabase.prepare.mockReturnValue(mockStatement);
      
      const sql = 'SELECT * FROM conversations WHERE id = ?';
      const statement1 = sqliteManager.getStatement(sql);
      const statement2 = sqliteManager.getStatement(sql);
      
      expect(mockDatabase.prepare).toHaveBeenCalledOnce();
      expect(statement1).toBe(statement2);
    });
  });
});
```

#### API Layer Testing
```typescript
// tests/unit/api/conversation-handler.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ConversationHandler } from '@/api/handlers/conversation-handler';
import { ConversationService } from '@/services/conversation-service';
import { AuthService } from '@/services/auth-service';

// Mock dependencies
vi.mock('@/services/conversation-service');
vi.mock('@/services/auth-service');

describe('ConversationHandler', () => {
  let handler: ConversationHandler;
  let mockConversationService: any;
  let mockAuthService: any;
  let mockRequest: any;
  let mockResponse: any;

  beforeEach(() => {
    mockConversationService = {
      createConversation: vi.fn(),
      getConversation: vi.fn(),
      updateConversation: vi.fn(),
      deleteConversation: vi.fn(),
      listConversations: vi.fn()
    };
    
    mockAuthService = {
      verifyToken: vi.fn(),
      getCurrentUser: vi.fn()
    };
    
    mockRequest = {
      body: {},
      params: {},
      query: {},
      headers: {}
    };
    
    mockResponse = {
      status: vi.fn().mockReturnThis(),
      json: vi.fn().mockReturnThis(),
      send: vi.fn().mockReturnThis()
    };
    
    vi.mocked(ConversationService).mockImplementation(() => mockConversationService);
    vi.mocked(AuthService).mockImplementation(() => mockAuthService);
    
    handler = new ConversationHandler();
  });

  describe('createConversation', () => {
    it('should create conversation successfully', async () => {
      const mockUser = { id: 'user-123', email: 'test@example.com' };
      const mockConversation = { id: 'conv-123', title: 'Test Conversation' };
      
      mockAuthService.getCurrentUser.mockResolvedValue(mockUser);
      mockConversationService.createConversation.mockResolvedValue(mockConversation);
      
      mockRequest.body = { title: 'Test Conversation' };
      mockRequest.headers.authorization = 'Bearer valid-token';
      
      await handler.createConversation(mockRequest, mockResponse);
      
      expect(mockAuthService.getCurrentUser).toHaveBeenCalledWith('valid-token');
      expect(mockConversationService.createConversation).toHaveBeenCalledWith({
        title: 'Test Conversation',
        userId: 'user-123'
      });
      expect(mockResponse.status).toHaveBeenCalledWith(201);
      expect(mockResponse.json).toHaveBeenCalledWith(mockConversation);
    });

    it('should handle unauthorized requests', async () => {
      mockAuthService.getCurrentUser.mockRejectedValue(new Error('Unauthorized'));
      
      mockRequest.headers.authorization = 'Bearer invalid-token';
      
      await handler.createConversation(mockRequest, mockResponse);
      
      expect(mockResponse.status).toHaveBeenCalledWith(401);
      expect(mockResponse.json).toHaveBeenCalledWith({
        error: 'Unauthorized'
      });
    });

    it('should validate request body', async () => {
      const mockUser = { id: 'user-123', email: 'test@example.com' };
      mockAuthService.getCurrentUser.mockResolvedValue(mockUser);
      
      mockRequest.body = {}; // Missing title
      mockRequest.headers.authorization = 'Bearer valid-token';
      
      await handler.createConversation(mockRequest, mockResponse);
      
      expect(mockResponse.status).toHaveBeenCalledWith(400);
      expect(mockResponse.json).toHaveBeenCalledWith({
        error: 'Title is required'
      });
    });
  });

  describe('getConversation', () => {
    it('should retrieve conversation successfully', async () => {
      const mockUser = { id: 'user-123', email: 'test@example.com' };
      const mockConversation = { 
        id: 'conv-123', 
        title: 'Test Conversation',
        userId: 'user-123'
      };
      
      mockAuthService.getCurrentUser.mockResolvedValue(mockUser);
      mockConversationService.getConversation.mockResolvedValue(mockConversation);
      
      mockRequest.params.id = 'conv-123';
      mockRequest.headers.authorization = 'Bearer valid-token';
      
      await handler.getConversation(mockRequest, mockResponse);
      
      expect(mockConversationService.getConversation).toHaveBeenCalledWith('conv-123');
      expect(mockResponse.status).toHaveBeenCalledWith(200);
      expect(mockResponse.json).toHaveBeenCalledWith(mockConversation);
    });

    it('should handle conversation not found', async () => {
      const mockUser = { id: 'user-123', email: 'test@example.com' };
      
      mockAuthService.getCurrentUser.mockResolvedValue(mockUser);
      mockConversationService.getConversation.mockResolvedValue(null);
      
      mockRequest.params.id = 'non-existent';
      mockRequest.headers.authorization = 'Bearer valid-token';
      
      await handler.getConversation(mockRequest, mockResponse);
      
      expect(mockResponse.status).toHaveBeenCalledWith(404);
      expect(mockResponse.json).toHaveBeenCalledWith({
        error: 'Conversation not found'
      });
    });
  });
});
```

### Vue 3 Component Testing with Vue Test Utils

#### Basic Component Testing
```typescript
// tests/unit/components/ConversationList.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount, VueWrapper } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import ConversationList from '@/components/ConversationList.vue';
import { useConversationStore } from '@/stores/conversation-store';

// Mock the store
vi.mock('@/stores/conversation-store');

describe('ConversationList', () => {
  let wrapper: VueWrapper<any>;
  let mockConversationStore: any;

  beforeEach(() => {
    setActivePinia(createPinia());
    
    mockConversationStore = {
      conversations: [
        { id: '1', title: 'Conversation 1', createdAt: '2023-01-01' },
        { id: '2', title: 'Conversation 2', createdAt: '2023-01-02' }
      ],
      loading: false,
      error: null,
      fetchConversations: vi.fn(),
      deleteConversation: vi.fn()
    };
    
    vi.mocked(useConversationStore).mockReturnValue(mockConversationStore);
  });

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount();
    }
  });

  it('renders conversation list correctly', () => {
    wrapper = mount(ConversationList);
    
    expect(wrapper.findAll('[data-testid="conversation-item"]')).toHaveLength(2);
    expect(wrapper.text()).toContain('Conversation 1');
    expect(wrapper.text()).toContain('Conversation 2');
  });

  it('shows loading state', () => {
    mockConversationStore.loading = true;
    wrapper = mount(ConversationList);
    
    expect(wrapper.find('[data-testid="loading-spinner"]').exists()).toBe(true);
  });

  it('shows error state', () => {
    mockConversationStore.error = 'Failed to load conversations';
    wrapper = mount(ConversationList);
    
    expect(wrapper.find('[data-testid="error-message"]').exists()).toBe(true);
    expect(wrapper.text()).toContain('Failed to load conversations');
  });

  it('calls fetchConversations on mount', () => {
    wrapper = mount(ConversationList);
    
    expect(mockConversationStore.fetchConversations).toHaveBeenCalled();
  });

  it('handles conversation deletion', async () => {
    wrapper = mount(ConversationList);
    
    const deleteButton = wrapper.find('[data-testid="delete-button-1"]');
    await deleteButton.trigger('click');
    
    expect(mockConversationStore.deleteConversation).toHaveBeenCalledWith('1');
  });

  it('filters conversations based on search', async () => {
    wrapper = mount(ConversationList);
    
    const searchInput = wrapper.find('[data-testid="search-input"]');
    await searchInput.setValue('Conversation 1');
    
    expect(wrapper.findAll('[data-testid="conversation-item"]')).toHaveLength(1);
    expect(wrapper.text()).toContain('Conversation 1');
    expect(wrapper.text()).not.toContain('Conversation 2');
  });
});
```

#### Advanced Component Testing with Composition API
```typescript
// tests/unit/components/ConversationDetail.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount, VueWrapper } from '@vue/test-utils';
import { nextTick } from 'vue';
import { createPinia, setActivePinia } from 'pinia';
import ConversationDetail from '@/components/ConversationDetail.vue';
import { useConversationStore } from '@/stores/conversation-store';
import { useWebSocketStore } from '@/stores/websocket-store';

vi.mock('@/stores/conversation-store');
vi.mock('@/stores/websocket-store');

describe('ConversationDetail', () => {
  let wrapper: VueWrapper<any>;
  let mockConversationStore: any;
  let mockWebSocketStore: any;

  beforeEach(() => {
    setActivePinia(createPinia());
    
    mockConversationStore = {
      currentConversation: {
        id: '1',
        title: 'Test Conversation',
        messages: [
          { id: '1', content: 'Hello', timestamp: '2023-01-01T10:00:00Z' },
          { id: '2', content: 'Hi there', timestamp: '2023-01-01T10:01:00Z' }
        ]
      },
      sendMessage: vi.fn(),
      loading: false,
      error: null
    };
    
    mockWebSocketStore = {
      connected: true,
      connect: vi.fn(),
      disconnect: vi.fn(),
      sendMessage: vi.fn()
    };
    
    vi.mocked(useConversationStore).mockReturnValue(mockConversationStore);
    vi.mocked(useWebSocketStore).mockReturnValue(mockWebSocketStore);
  });

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount();
    }
  });

  it('renders conversation messages', () => {
    wrapper = mount(ConversationDetail);
    
    expect(wrapper.findAll('[data-testid="message-item"]')).toHaveLength(2);
    expect(wrapper.text()).toContain('Hello');
    expect(wrapper.text()).toContain('Hi there');
  });

  it('sends message when form is submitted', async () => {
    wrapper = mount(ConversationDetail);
    
    const messageInput = wrapper.find('[data-testid="message-input"]');
    const submitButton = wrapper.find('[data-testid="send-button"]');
    
    await messageInput.setValue('New message');
    await submitButton.trigger('click');
    
    expect(mockConversationStore.sendMessage).toHaveBeenCalledWith('New message');
  });

  it('handles WebSocket connection', () => {
    wrapper = mount(ConversationDetail);
    
    expect(mockWebSocketStore.connect).toHaveBeenCalled();
  });

  it('shows typing indicator', async () => {
    wrapper = mount(ConversationDetail);
    
    const messageInput = wrapper.find('[data-testid="message-input"]');
    await messageInput.setValue('Typing...');
    
    expect(wrapper.find('[data-testid="typing-indicator"]').exists()).toBe(true);
  });

  it('auto-scrolls to bottom when new message arrives', async () => {
    wrapper = mount(ConversationDetail);
    
    // Mock scroll behavior
    const scrollToBottom = vi.fn();
    wrapper.vm.scrollToBottom = scrollToBottom;
    
    // Add new message
    mockConversationStore.currentConversation.messages.push({
      id: '3',
      content: 'New message',
      timestamp: '2023-01-01T10:02:00Z'
    });
    
    await nextTick();
    
    expect(scrollToBottom).toHaveBeenCalled();
  });

  it('handles error states gracefully', async () => {
    mockConversationStore.error = 'Failed to send message';
    wrapper = mount(ConversationDetail);
    
    expect(wrapper.find('[data-testid="error-toast"]').exists()).toBe(true);
    expect(wrapper.text()).toContain('Failed to send message');
  });
});
```

## Technical Implementation Details

### API Testing and Mocking Patterns

#### HTTP Client Mocking
```typescript
// tests/unit/services/api-client.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ApiClient } from '@/services/api-client';
import { HttpError } from '@/types/errors';

// Mock fetch globally
const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

describe('ApiClient', () => {
  let apiClient: ApiClient;
  
  beforeEach(() => {
    apiClient = new ApiClient('http://localhost:3000');
    mockFetch.mockClear();
  });

  describe('GET requests', () => {
    it('should make successful GET request', async () => {
      const mockResponse = { data: 'test' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(mockResponse)
      });
      
      const result = await apiClient.get('/test');
      
      expect(mockFetch).toHaveBeenCalledWith('http://localhost:3000/test', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      expect(result).toEqual(mockResponse);
    });

    it('should handle 404 errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found'
      });
      
      await expect(apiClient.get('/nonexistent'))
        .rejects.toThrow(HttpError);
    });

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));
      
      await expect(apiClient.get('/test'))
        .rejects.toThrow('Network error');
    });
  });

  describe('POST requests', () => {
    it('should make POST request with data', async () => {
      const requestData = { name: 'Test' };
      const mockResponse = { id: 1, name: 'Test' };
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: vi.fn().mockResolvedValue(mockResponse)
      });
      
      const result = await apiClient.post('/test', requestData);
      
      expect(mockFetch).toHaveBeenCalledWith('http://localhost:3000/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      });
      expect(result).toEqual(mockResponse);
    });

    it('should handle validation errors', async () => {
      const requestData = { name: '' };
      const errorResponse = { 
        error: 'Validation failed',
        details: { name: 'Name is required' }
      };
      
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: vi.fn().mockResolvedValue(errorResponse)
      });
      
      await expect(apiClient.post('/test', requestData))
        .rejects.toThrow('Validation failed');
    });
  });

  describe('authentication', () => {
    it('should include auth token in requests', async () => {
      apiClient.setAuthToken('test-token');
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue({})
      });
      
      await apiClient.get('/protected');
      
      expect(mockFetch).toHaveBeenCalledWith('http://localhost:3000/protected', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test-token'
        }
      });
    });
  });
});
```

#### WebSocket Testing
```typescript
// tests/unit/services/websocket-service.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { WebSocketService } from '@/services/websocket-service';

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  readyState = MockWebSocket.CONNECTING;
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;

  send = vi.fn();
  close = vi.fn();
  addEventListener = vi.fn();
  removeEventListener = vi.fn();

  // Helper methods for testing
  simulateOpen() {
    this.readyState = MockWebSocket.OPEN;
    this.onopen?.(new Event('open'));
  }

  simulateMessage(data: any) {
    this.onmessage?.(new MessageEvent('message', { data: JSON.stringify(data) }));
  }

  simulateClose() {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.(new CloseEvent('close'));
  }

  simulateError() {
    this.onerror?.(new Event('error'));
  }
}

vi.stubGlobal('WebSocket', MockWebSocket);

describe('WebSocketService', () => {
  let service: WebSocketService;
  let mockWebSocket: MockWebSocket;

  beforeEach(() => {
    service = new WebSocketService('ws://localhost:3001');
    mockWebSocket = service['socket'] as MockWebSocket;
  });

  describe('connection', () => {
    it('should establish WebSocket connection', () => {
      service.connect();
      expect(mockWebSocket).toBeInstanceOf(MockWebSocket);
    });

    it('should handle connection open', () => {
      const onConnect = vi.fn();
      service.on('connect', onConnect);
      
      service.connect();
      mockWebSocket.simulateOpen();
      
      expect(onConnect).toHaveBeenCalled();
    });

    it('should handle connection close', () => {
      const onDisconnect = vi.fn();
      service.on('disconnect', onDisconnect);
      
      service.connect();
      mockWebSocket.simulateClose();
      
      expect(onDisconnect).toHaveBeenCalled();
    });

    it('should handle connection errors', () => {
      const onError = vi.fn();
      service.on('error', onError);
      
      service.connect();
      mockWebSocket.simulateError();
      
      expect(onError).toHaveBeenCalled();
    });
  });

  describe('messaging', () => {
    beforeEach(() => {
      service.connect();
      mockWebSocket.simulateOpen();
    });

    it('should send message when connected', () => {
      const message = { type: 'test', data: 'hello' };
      
      service.send(message);
      
      expect(mockWebSocket.send).toHaveBeenCalledWith(JSON.stringify(message));
    });

    it('should queue messages when not connected', () => {
      service.disconnect();
      
      const message = { type: 'test', data: 'hello' };
      service.send(message);
      
      expect(mockWebSocket.send).not.toHaveBeenCalled();
      
      // Reconnect and verify message is sent
      service.connect();
      mockWebSocket.simulateOpen();
      
      expect(mockWebSocket.send).toHaveBeenCalledWith(JSON.stringify(message));
    });

    it('should handle incoming messages', () => {
      const onMessage = vi.fn();
      service.on('message', onMessage);
      
      const message = { type: 'response', data: 'world' };
      mockWebSocket.simulateMessage(message);
      
      expect(onMessage).toHaveBeenCalledWith(message);
    });
  });

  describe('reconnection', () => {
    it('should attempt to reconnect on connection loss', () => {
      vi.useFakeTimers();
      
      service.connect();
      mockWebSocket.simulateOpen();
      mockWebSocket.simulateClose();
      
      // Fast-forward time to trigger reconnection
      vi.advanceTimersByTime(5000);
      
      expect(service.isConnected()).toBe(false);
      
      vi.useRealTimers();
    });
  });
});
```

### End-to-End Testing with Playwright

#### Playwright Configuration
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/results.xml' }]
  ],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure'
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] }
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] }
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] }
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] }
    }
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI
  }
});
```

#### Complete User Journey Testing
```typescript
// tests/e2e/user-journey.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Complete User Journey', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('new user onboarding flow', async ({ page }) => {
    // Step 1: Landing page
    await expect(page.getByRole('heading', { name: 'Claude Code Observatory' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Get Started' })).toBeVisible();
    
    // Step 2: Registration
    await page.getByRole('button', { name: 'Get Started' }).click();
    await page.getByLabel('Email').fill('test@example.com');
    await page.getByLabel('Password').fill('securepassword123');
    await page.getByLabel('Confirm Password').fill('securepassword123');
    await page.getByRole('button', { name: 'Create Account' }).click();
    
    // Step 3: Email verification (mock)
    await expect(page.getByText('Please check your email')).toBeVisible();
    
    // Simulate email verification
    await page.goto('/verify-email?token=mock-token');
    await expect(page.getByText('Email verified successfully')).toBeVisible();
    
    // Step 4: Onboarding tutorial
    await expect(page.getByText('Welcome to Claude Code Observatory')).toBeVisible();
    await page.getByRole('button', { name: 'Start Tutorial' }).click();
    
    // Navigate through tutorial steps
    for (let i = 0; i < 3; i++) {
      await page.getByRole('button', { name: 'Next' }).click();
    }
    
    await page.getByRole('button', { name: 'Finish Tutorial' }).click();
    
    // Step 5: Dashboard
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
    await expect(page.getByText('No conversations yet')).toBeVisible();
    
    // Step 6: Create first conversation
    await page.getByRole('button', { name: 'New Conversation' }).click();
    await page.getByLabel('Conversation Title').fill('My First Conversation');
    await page.getByRole('button', { name: 'Create' }).click();
    
    // Step 7: Send first message
    await expect(page.getByRole('heading', { name: 'My First Conversation' })).toBeVisible();
    await page.getByLabel('Message').fill('Hello, Claude!');
    await page.getByRole('button', { name: 'Send' }).click();
    
    // Verify message appears
    await expect(page.getByText('Hello, Claude!')).toBeVisible();
    
    // Step 8: Navigate back to dashboard
    await page.getByRole('link', { name: 'Dashboard' }).click();
    await expect(page.getByText('My First Conversation')).toBeVisible();
  });

  test('conversation management workflow', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.getByLabel('Email').fill('test@example.com');
    await page.getByLabel('Password').fill('securepassword123');
    await page.getByRole('button', { name: 'Sign In' }).click();
    
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
    
    // Create multiple conversations
    const conversations = [
      'Project Planning',
      'Code Review',
      'Architecture Discussion'
    ];
    
    for (const title of conversations) {
      await page.getByRole('button', { name: 'New Conversation' }).click();
      await page.getByLabel('Conversation Title').fill(title);
      await page.getByRole('button', { name: 'Create' }).click();
      
      // Add a message to each conversation
      await page.getByLabel('Message').fill(`Discussion about ${title}`);
      await page.getByRole('button', { name: 'Send' }).click();
      
      // Return to dashboard
      await page.getByRole('link', { name: 'Dashboard' }).click();
    }
    
    // Verify all conversations appear
    for (const title of conversations) {
      await expect(page.getByText(title)).toBeVisible();
    }
    
    // Test search functionality
    await page.getByLabel('Search conversations').fill('Code');
    await expect(page.getByText('Code Review')).toBeVisible();
    await expect(page.getByText('Project Planning')).not.toBeVisible();
    
    // Clear search
    await page.getByLabel('Search conversations').clear();
    
    // Test conversation sorting
    await page.getByRole('button', { name: 'Sort by Date' }).click();
    const conversationItems = page.locator('[data-testid="conversation-item"]');
    await expect(conversationItems).toHaveCount(3);
    
    // Test conversation deletion
    await page.getByRole('button', { name: 'Delete Project Planning' }).click();
    await page.getByRole('button', { name: 'Confirm Delete' }).click();
    
    await expect(page.getByText('Project Planning')).not.toBeVisible();
    await expect(conversationItems).toHaveCount(2);
  });

  test('real-time collaboration features', async ({ browser }) => {
    // Create two browser contexts for different users
    const context1 = await browser.newContext();
    const context2 = await browser.newContext();
    
    const page1 = await context1.newPage();
    const page2 = await context2.newPage();
    
    // User 1 login
    await page1.goto('/login');
    await page1.getByLabel('Email').fill('user1@example.com');
    await page1.getByLabel('Password').fill('password123');
    await page1.getByRole('button', { name: 'Sign In' }).click();
    
    // User 2 login
    await page2.goto('/login');
    await page2.getByLabel('Email').fill('user2@example.com');
    await page2.getByLabel('Password').fill('password123');
    await page2.getByRole('button', { name: 'Sign In' }).click();
    
    // User 1 creates a conversation
    await page1.getByRole('button', { name: 'New Conversation' }).click();
    await page1.getByLabel('Conversation Title').fill('Collaborative Discussion');
    await page1.getByRole('button', { name: 'Create' }).click();
    
    // Share conversation with User 2
    await page1.getByRole('button', { name: 'Share' }).click();
    await page1.getByLabel('Email').fill('user2@example.com');
    await page1.getByRole('button', { name: 'Send Invite' }).click();
    
    // User 2 accepts invitation (simulated)
    await page2.goto('/conversations/shared/mock-conversation-id');
    
    // Test real-time messaging
    await page1.getByLabel('Message').fill('Hello from User 1!');
    await page1.getByRole('button', { name: 'Send' }).click();
    
    // Verify message appears in both contexts
    await expect(page1.getByText('Hello from User 1!')).toBeVisible();
    await expect(page2.getByText('Hello from User 1!')).toBeVisible();
    
    // Test typing indicators
    await page2.getByLabel('Message').fill('Typing response...');
    await expect(page1.getByText('User 2 is typing...')).toBeVisible();
    
    // Send response
    await page2.getByRole('button', { name: 'Send' }).click();
    await expect(page1.getByText('Typing response...')).toBeVisible();
    
    // Clean up
    await context1.close();
    await context2.close();
  });

  test('mobile responsive experience', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Test mobile navigation
    await page.goto('/login');
    await page.getByLabel('Email').fill('test@example.com');
    await page.getByLabel('Password').fill('securepassword123');
    await page.getByRole('button', { name: 'Sign In' }).click();
    
    // Mobile menu should be visible
    await expect(page.getByRole('button', { name: 'Menu' })).toBeVisible();
    
    // Test mobile conversation view
    await page.getByRole('button', { name: 'New Conversation' }).click();
    await page.getByLabel('Conversation Title').fill('Mobile Test');
    await page.getByRole('button', { name: 'Create' }).click();
    
    // Test mobile message input
    await page.getByLabel('Message').fill('Testing mobile interface');
    await page.getByRole('button', { name: 'Send' }).click();
    
    await expect(page.getByText('Testing mobile interface')).toBeVisible();
    
    // Test mobile navigation back
    await page.getByRole('button', { name: 'Back' }).click();
    await expect(page.getByText('Mobile Test')).toBeVisible();
  });
});
```

### Performance Testing Configuration

#### Load Testing with Artillery
```yaml
# tests/performance/load-test.yml
config:
  target: 'http://localhost:3000'
  phases:
    - duration: 60
      arrivalRate: 5
      name: "Warm up"
    - duration: 120
      arrivalRate: 10
      name: "Ramp up load"
    - duration: 180
      arrivalRate: 20
      name: "Sustained load"
  payload:
    path: "./test-data.csv"
    fields:
      - "email"
      - "password"
  plugins:
    metrics-by-endpoint:
      useOnlyRequestNames: true

scenarios:
  - name: "User Authentication Flow"
    weight: 30
    flow:
      - post:
          url: "/api/auth/login"
          json:
            email: "{{ email }}"
            password: "{{ password }}"
          capture:
            - json: "$.token"
              as: "authToken"
      - get:
          url: "/api/conversations"
          headers:
            Authorization: "Bearer {{ authToken }}"
  
  - name: "Conversation Management"
    weight: 40
    flow:
      - post:
          url: "/api/auth/login"
          json:
            email: "{{ email }}"
            password: "{{ password }}"
          capture:
            - json: "$.token"
              as: "authToken"
      - post:
          url: "/api/conversations"
          json:
            title: "Load Test Conversation {{ $randomString() }}"
          headers:
            Authorization: "Bearer {{ authToken }}"
          capture:
            - json: "$.id"
              as: "conversationId"
      - post:
          url: "/api/conversations/{{ conversationId }}/messages"
          json:
            content: "Test message {{ $randomString() }}"
          headers:
            Authorization: "Bearer {{ authToken }}"
  
  - name: "Analytics Dashboard"
    weight: 20
    flow:
      - post:
          url: "/api/auth/login"
          json:
            email: "{{ email }}"
            password: "{{ password }}"
          capture:
            - json: "$.token"
              as: "authToken"
      - get:
          url: "/api/analytics/dashboard"
          headers:
            Authorization: "Bearer {{ authToken }}"
      - get:
          url: "/api/analytics/conversations/stats"
          headers:
            Authorization: "Bearer {{ authToken }}"
  
  - name: "WebSocket Connection"
    weight: 10
    engine: ws
    flow:
      - connect:
          url: "ws://localhost:3001"
      - send:
          payload: |
            {
              "type": "authenticate",
              "token": "{{ authToken }}"
            }
      - think: 5
      - send:
          payload: |
            {
              "type": "join_conversation",
              "conversationId": "{{ conversationId }}"
            }
      - think: 10
      - send:
          payload: |
            {
              "type": "message",
              "content": "WebSocket test message"
            }
```

#### Performance Testing with Vitest
```typescript
// tests/performance/api-performance.test.ts
import { describe, it, expect, vi } from 'vitest';
import { performance } from 'perf_hooks';
import { ApiClient } from '@/services/api-client';

describe('API Performance Tests', () => {
  let apiClient: ApiClient;
  
  beforeEach(() => {
    apiClient = new ApiClient('http://localhost:3000');
  });

  it('should handle 100 concurrent requests', async () => {
    const startTime = performance.now();
    
    // Create 100 concurrent requests
    const promises = Array.from({ length: 100 }, (_, i) => 
      apiClient.get(`/api/conversations?page=${i}`)
    );
    
    const results = await Promise.allSettled(promises);
    const endTime = performance.now();
    
    const successCount = results.filter(r => r.status === 'fulfilled').length;
    const failureCount = results.filter(r => r.status === 'rejected').length;
    const duration = endTime - startTime;
    
    expect(successCount).toBeGreaterThan(95); // 95% success rate
    expect(duration).toBeLessThan(5000); // Under 5 seconds
    expect(failureCount).toBeLessThan(5); // Less than 5% failures
    
    console.log(`Performance Test Results:`);
    console.log(`Duration: ${duration.toFixed(2)}ms`);
    console.log(`Success Rate: ${(successCount / 100 * 100).toFixed(1)}%`);
    console.log(`Average Response Time: ${(duration / successCount).toFixed(2)}ms`);
  });

  it('should handle database query performance', async () => {
    const queries = [
      'SELECT * FROM conversations ORDER BY created_at DESC LIMIT 20',
      'SELECT COUNT(*) FROM messages WHERE conversation_id = ?',
      'SELECT * FROM users WHERE email = ?',
      'SELECT * FROM conversations WHERE user_id = ? AND archived = false'
    ];
    
    const results = [];
    
    for (const query of queries) {
      const startTime = performance.now();
      
      // Execute query (mocked for this example)
      await new Promise(resolve => setTimeout(resolve, Math.random() * 100));
      
      const endTime = performance.now();
      const duration = endTime - startTime;
      
      results.push({ query, duration });
      
      // Individual query should complete under 100ms
      expect(duration).toBeLessThan(100);
    }
    
    const averageDuration = results.reduce((sum, r) => sum + r.duration, 0) / results.length;
    expect(averageDuration).toBeLessThan(50); // Average under 50ms
  });

  it('should handle memory usage efficiently', async () => {
    const initialMemory = process.memoryUsage();
    
    // Simulate processing large dataset
    const largeArray = Array.from({ length: 10000 }, (_, i) => ({
      id: i,
      data: `Large data string ${i}`.repeat(100)
    }));
    
    // Process the data
    const processedData = largeArray.map(item => ({
      id: item.id,
      summary: item.data.substring(0, 100)
    }));
    
    const finalMemory = process.memoryUsage();
    const memoryIncrease = finalMemory.heapUsed - initialMemory.heapUsed;
    
    // Memory increase should be reasonable (less than 50MB)
    expect(memoryIncrease).toBeLessThan(50 * 1024 * 1024);
    
    // Clean up
    largeArray.length = 0;
    processedData.length = 0;
    
    // Force garbage collection if available
    if (global.gc) {
      global.gc();
    }
  });
});
```

### Continuous Integration Testing Workflows

#### GitHub Actions Configuration
```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18.x, 20.x]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run unit tests
        run: npm run test:unit -- --reporter=verbose --coverage
      
      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info
          flags: unittests
          name: codecov-umbrella
  
  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20.x'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run database migrations
        run: npm run db:migrate
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/testdb
      
      - name: Run integration tests
        run: npm run test:integration
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/testdb
  
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20.x'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Install Playwright
        run: npx playwright install --with-deps
      
      - name: Build application
        run: npm run build
      
      - name: Run E2E tests
        run: npm run test:e2e
      
      - name: Upload Playwright report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 30
  
  performance-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20.x'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build application
        run: npm run build
      
      - name: Start application
        run: npm run start &
      
      - name: Wait for application
        run: npx wait-on http://localhost:3000
      
      - name: Run performance tests
        run: npm run test:performance
      
      - name: Upload performance results
        uses: actions/upload-artifact@v4
        with:
          name: performance-results
          path: performance-results/
```

### Comprehensive Test Framework
```typescript
// tests/comprehensive/test-framework.ts
import { TestRunner } from './test-runner';
import { TestSuiteManager } from './test-suite-manager';
import { ReportGenerator } from './report-generator';

export class ComprehensiveTestFramework {
  private testRunner: TestRunner;
  private suiteManager: TestSuiteManager;
  private reportGenerator: ReportGenerator;

  constructor() {
    this.testRunner = new TestRunner();
    this.suiteManager = new TestSuiteManager();
    this.reportGenerator = new ReportGenerator();
  }

  async executeFullTestSuite(): Promise<TestExecutionReport> {
    const report: TestExecutionReport = {
      startTime: new Date(),
      testSuites: [],
      overallResults: {
        totalTests: 0,
        passed: 0,
        failed: 0,
        skipped: 0,
        duration: 0
      },
      coverage: {
        statements: 0,
        branches: 0,
        functions: 0,
        lines: 0
      },
      performance: {
        averageResponseTime: 0,
        p95ResponseTime: 0,
        throughput: 0,
        errorRate: 0
      },
      security: {
        vulnerabilities: [],
        passed: false
      },
      accessibility: {
        violations: [],
        passed: false
      }
    };

    try {
      // 1. Unit Tests
      const unitTestResults = await this.runUnitTests();
      report.testSuites.push(unitTestResults);

      // 2. Integration Tests
      const integrationTestResults = await this.runIntegrationTests();
      report.testSuites.push(integrationTestResults);

      // 3. End-to-End Tests
      const e2eTestResults = await this.runE2ETests();
      report.testSuites.push(e2eTestResults);

      // 4. Performance Tests
      const performanceResults = await this.runPerformanceTests();
      report.testSuites.push(performanceResults);
      report.performance = performanceResults.performance;

      // 5. Security Tests
      const securityResults = await this.runSecurityTests();
      report.testSuites.push(securityResults);
      report.security = securityResults.security;

      // 6. Accessibility Tests
      const accessibilityResults = await this.runAccessibilityTests();
      report.testSuites.push(accessibilityResults);
      report.accessibility = accessibilityResults.accessibility;

      // 7. Cross-Browser Tests
      const crossBrowserResults = await this.runCrossBrowserTests();
      report.testSuites.push(crossBrowserResults);

      // Calculate overall results
      report.overallResults = this.calculateOverallResults(report.testSuites);
      report.coverage = await this.generateCoverageReport();
      
      report.endTime = new Date();
      report.overallResults.duration = 
        report.endTime.getTime() - report.startTime.getTime();

      return report;

    } catch (error) {
      console.error('Test execution failed:', error);
      throw error;
    }
  }

  private async runUnitTests(): Promise<TestSuiteResult> {
    console.log('Running unit tests...');
    
    const suites = [
      'backend/database',
      'backend/api',
      'backend/analytics',
      'frontend/components',
      'frontend/stores',
      'frontend/utils',
      'shared/types',
      'shared/validation'
    ];

    const results: TestResult[] = [];
    
    for (const suite of suites) {
      const suiteResult = await this.testRunner.runTestSuite(`tests/unit/${suite}`);
      results.push(...suiteResult.tests);
    }

    return {
      name: 'Unit Tests',
      type: 'unit',
      results,
      summary: this.summarizeResults(results),
      duration: results.reduce((sum, test) => sum + test.duration, 0)
    };
  }

  private async runIntegrationTests(): Promise<TestSuiteResult> {
    console.log('Running integration tests...');
    
    const integrationTests = [
      'api-database-integration',
      'websocket-integration',
      'analytics-integration',
      'frontend-backend-integration',
      'real-time-features-integration'
    ];

    const results: TestResult[] = [];
    
    for (const testName of integrationTests) {
      const testResult = await this.testRunner.runTest(`tests/integration/${testName}`);
      results.push(testResult);
    }

    return {
      name: 'Integration Tests',
      type: 'integration',
      results,
      summary: this.summarizeResults(results),
      duration: results.reduce((sum, test) => sum + test.duration, 0)
    };
  }

  private async runE2ETests(): Promise<TestSuiteResult> {
    console.log('Running end-to-end tests...');
    
    const e2eScenarios = [
      'complete-user-journey',
      'conversation-management',
      'real-time-collaboration',
      'analytics-dashboard',
      'data-export',
      'error-handling',
      'mobile-experience'
    ];

    const results: TestResult[] = [];
    
    for (const scenario of e2eScenarios) {
      const testResult = await this.testRunner.runPlaywrightTest(`tests/e2e/${scenario}`);
      results.push(testResult);
    }

    return {
      name: 'End-to-End Tests',
      type: 'e2e',
      results,
      summary: this.summarizeResults(results),
      duration: results.reduce((sum, test) => sum + test.duration, 0)
    };
  }

  private async runPerformanceTests(): Promise<TestSuiteResult & { performance: PerformanceMetrics }> {
    console.log('Running performance tests...');
    
    const performanceTests = [
      'load-testing',
      'stress-testing',
      'spike-testing',
      'volume-testing',
      'endurance-testing'
    ];

    const results: TestResult[] = [];
    const performanceMetrics: PerformanceMetrics = {
      averageResponseTime: 0,
      p95ResponseTime: 0,
      throughput: 0,
      errorRate: 0
    };

    for (const testName of performanceTests) {
      const testResult = await this.testRunner.runPerformanceTest(`tests/performance/${testName}`);
      results.push(testResult);
      
      // Aggregate performance metrics
      if (testResult.metrics) {
        performanceMetrics.averageResponseTime += testResult.metrics.averageResponseTime;
        performanceMetrics.p95ResponseTime = Math.max(
          performanceMetrics.p95ResponseTime, 
          testResult.metrics.p95ResponseTime
        );
        performanceMetrics.throughput += testResult.metrics.throughput;
        performanceMetrics.errorRate = Math.max(
          performanceMetrics.errorRate, 
          testResult.metrics.errorRate
        );
      }
    }

    // Calculate averages
    performanceMetrics.averageResponseTime /= performanceTests.length;
    performanceMetrics.throughput /= performanceTests.length;

    return {
      name: 'Performance Tests',
      type: 'performance',
      results,
      summary: this.summarizeResults(results),
      duration: results.reduce((sum, test) => sum + test.duration, 0),
      performance: performanceMetrics
    };
  }

  private async runSecurityTests(): Promise<TestSuiteResult & { security: SecurityResults }> {
    console.log('Running security tests...');
    
    const securityTests = [
      'authentication-security',
      'authorization-testing',
      'input-validation',
      'sql-injection-protection',
      'xss-protection',
      'csrf-protection',
      'rate-limiting',
      'data-encryption'
    ];

    const results: TestResult[] = [];
    const vulnerabilities: SecurityVulnerability[] = [];

    for (const testName of securityTests) {
      const testResult = await this.testRunner.runSecurityTest(`tests/security/${testName}`);
      results.push(testResult);
      
      if (testResult.vulnerabilities) {
        vulnerabilities.push(...testResult.vulnerabilities);
      }
    }

    const criticalVulnerabilities = vulnerabilities.filter(v => v.severity === 'critical');
    const highVulnerabilities = vulnerabilities.filter(v => v.severity === 'high');

    return {
      name: 'Security Tests',
      type: 'security',
      results,
      summary: this.summarizeResults(results),
      duration: results.reduce((sum, test) => sum + test.duration, 0),
      security: {
        vulnerabilities,
        passed: criticalVulnerabilities.length === 0 && highVulnerabilities.length === 0
      }
    };
  }

  private async runAccessibilityTests(): Promise<TestSuiteResult & { accessibility: AccessibilityResults }> {
    console.log('Running accessibility tests...');
    
    const accessibilityTests = [
      'wcag-compliance',
      'keyboard-navigation',
      'screen-reader-compatibility',
      'color-contrast',
      'focus-management',
      'semantic-markup',
      'aria-labels'
    ];

    const results: TestResult[] = [];
    const violations: AccessibilityViolation[] = [];

    for (const testName of accessibilityTests) {
      const testResult = await this.testRunner.runAccessibilityTest(`tests/accessibility/${testName}`);
      results.push(testResult);
      
      if (testResult.violations) {
        violations.push(...testResult.violations);
      }
    }

    const criticalViolations = violations.filter(v => v.impact === 'critical');
    const seriousViolations = violations.filter(v => v.impact === 'serious');

    return {
      name: 'Accessibility Tests',
      type: 'accessibility',
      results,
      summary: this.summarizeResults(results),
      duration: results.reduce((sum, test) => sum + test.duration, 0),
      accessibility: {
        violations,
        passed: criticalViolations.length === 0 && seriousViolations.length === 0
      }
    };
  }

  private async runCrossBrowserTests(): Promise<TestSuiteResult> {
    console.log('Running cross-browser tests...');
    
    const browsers = [
      { name: 'chrome', version: 'latest' },
      { name: 'firefox', version: 'latest' },
      { name: 'safari', version: 'latest' },
      { name: 'edge', version: 'latest' }
    ];

    const testScenarios = [
      'basic-functionality',
      'responsive-design',
      'interactive-features',
      'form-submission',
      'real-time-updates'
    ];

    const results: TestResult[] = [];

    for (const browser of browsers) {
      for (const scenario of testScenarios) {
        const testResult = await this.testRunner.runCrossBrowserTest(
          browser, 
          `tests/cross-browser/${scenario}`
        );
        results.push(testResult);
      }
    }

    return {
      name: 'Cross-Browser Tests',
      type: 'cross-browser',
      results,
      summary: this.summarizeResults(results),
      duration: results.reduce((sum, test) => sum + test.duration, 0)
    };
  }

  private summarizeResults(results: TestResult[]): TestSummary {
    return {
      total: results.length,
      passed: results.filter(r => r.status === 'passed').length,
      failed: results.filter(r => r.status === 'failed').length,
      skipped: results.filter(r => r.status === 'skipped').length
    };
  }

  private calculateOverallResults(testSuites: TestSuiteResult[]): TestSummary & { duration: number } {
    const allResults = testSuites.flatMap(suite => suite.results);
    
    return {
      ...this.summarizeResults(allResults),
      duration: testSuites.reduce((sum, suite) => sum + suite.duration, 0)
    };
  }

  private async generateCoverageReport(): Promise<CoverageReport> {
    // Integration with coverage tools (Istanbul, c8, etc.)
    return {
      statements: 85.5,
      branches: 78.2,
      functions: 92.1,
      lines: 87.3
    };
  }

  async generateDetailedReport(results: TestExecutionReport): Promise<string> {
    return this.reportGenerator.generateHTMLReport(results);
  }
}
```

### User Acceptance Testing Framework
```typescript
// tests/user-acceptance/uat-framework.ts
import { UserScenario } from './user-scenario';
import { FeedbackCollector } from './feedback-collector';
import { UsabilityMetrics } from './usability-metrics';

export class UserAcceptanceTestingFramework {
  private scenarios: UserScenario[] = [];
  private feedbackCollector: FeedbackCollector;
  private usabilityMetrics: UsabilityMetrics;

  constructor() {
    this.feedbackCollector = new FeedbackCollector();
    this.usabilityMetrics = new UsabilityMetrics();
    this.initializeScenarios();
  }

  private initializeScenarios(): void {
    this.scenarios = [
      {
        id: 'onboarding',
        title: 'User Onboarding Experience',
        description: 'New user registration and first-time experience',
        tasks: [
          'Create account and verify email',
          'Complete onboarding tutorial',
          'Create first conversation',
          'Send first message',
          'Navigate to dashboard'
        ],
        acceptanceCriteria: [
          'User completes onboarding within 5 minutes',
          'User successfully creates first conversation',
          'User understands core features',
          'No critical errors encountered'
        ],
        priority: 'critical'
      },
      {
        id: 'conversation-management',
        title: 'Conversation Management',
        description: 'Creating, managing, and organizing conversations',
        tasks: [
          'Create multiple conversations',
          'Organize conversations with tags/categories',
          'Search and filter conversations',
          'Share conversation with team member',
          'Archive completed conversations'
        ],
        acceptanceCriteria: [
          'All conversation operations work intuitively',
          'Search functionality returns relevant results',
          'Sharing mechanism works correctly',
          'Performance remains smooth with 50+ conversations'
        ],
        priority: 'high'
      },
      {
        id: 'real-time-collaboration',
        title: 'Real-Time Collaboration Features',
        description: 'Multiple users collaborating on conversations',
        tasks: [
          'Join shared conversation',
          'See typing indicators from other users',
          'Receive real-time message updates',
          'Use collaborative features (comments, reactions)',
          'Handle connection interruptions gracefully'
        ],
        acceptanceCriteria: [
          'Real-time updates appear within 2 seconds',
          'Typing indicators work correctly',
          'No message duplication or loss',
          'Graceful handling of network issues'
        ],
        priority: 'high'
      },
      {
        id: 'analytics-insights',
        title: 'Analytics and Insights',
        description: 'Viewing and understanding conversation analytics',
        tasks: [
          'Navigate to analytics dashboard',
          'Understand key metrics and visualizations',
          'Filter data by time range',
          'Export analytics data',
          'Generate custom reports'
        ],
        acceptanceCriteria: [
          'Charts and metrics are intuitive and accurate',
          'Filtering works smoothly',
          'Export functionality works correctly',
          'Data visualization is meaningful'
        ],
        priority: 'medium'
      },
      {
        id: 'mobile-experience',
        title: 'Mobile and Tablet Experience',
        description: 'Using the application on mobile devices',
        tasks: [
          'Access application on mobile browser',
          'Navigate using touch interface',
          'Create and send messages on mobile',
          'View analytics on tablet',
          'Use voice input for messages'
        ],
        acceptanceCriteria: [
          'Responsive design works on all device sizes',
          'Touch interactions are intuitive',
          'Performance is acceptable on mobile',
          'All core features accessible'
        ],
        priority: 'medium'
      }
    ];
  }

  async executeUserAcceptanceTests(): Promise<UATResults> {
    const results: UATResults = {
      startTime: new Date(),
      scenarios: [],
      userSatisfaction: {
        overallRating: 0,
        easeOfUse: 0,
        featureCompleteness: 0,
        performance: 0,
        reliability: 0
      },
      usabilityMetrics: {
        taskSuccessRate: 0,
        averageTaskTime: 0,
        errorRate: 0,
        learnabilityScore: 0
      },
      feedback: [],
      recommendations: []
    };

    try {
      // Execute each scenario with test users
      for (const scenario of this.scenarios) {
        const scenarioResult = await this.executeScenario(scenario);
        results.scenarios.push(scenarioResult);
      }

      // Collect overall feedback
      results.feedback = await this.feedbackCollector.collectFeedback();
      
      // Calculate usability metrics
      results.usabilityMetrics = await this.usabilityMetrics.calculate(results.scenarios);
      
      // Calculate user satisfaction
      results.userSatisfaction = this.calculateUserSatisfaction(results.feedback);
      
      // Generate recommendations
      results.recommendations = this.generateRecommendations(results);
      
      results.endTime = new Date();
      
      return results;

    } catch (error) {
      console.error('UAT execution failed:', error);
      throw error;
    }
  }

  private async executeScenario(scenario: UserScenario): Promise<ScenarioResult> {
    console.log(`Executing UAT scenario: ${scenario.title}`);
    
    const testUsers = await this.recruitTestUsers(scenario.priority);
    const userResults: UserTestResult[] = [];

    for (const user of testUsers) {
      const userResult = await this.runScenarioWithUser(scenario, user);
      userResults.push(userResult);
    }

    return {
      scenario,
      userResults,
      overallSuccess: this.calculateScenarioSuccess(userResults),
      averageTaskTime: this.calculateAverageTaskTime(userResults),
      commonIssues: this.identifyCommonIssues(userResults),
      recommendations: this.generateScenarioRecommendations(userResults)
    };
  }

  private async runScenarioWithUser(scenario: UserScenario, user: TestUser): Promise<UserTestResult> {
    const startTime = new Date();
    const taskResults: TaskResult[] = [];
    const userFeedback: string[] = [];
    const errors: UserError[] = [];

    try {
      // Brief user and start recording
      await this.briefUser(user, scenario);
      
      for (const task of scenario.tasks) {
        const taskStartTime = new Date();
        
        try {
          // User performs task while thinking aloud
          const taskSuccess = await this.observeTaskExecution(user, task);
          
          taskResults.push({
            task,
            success: taskSuccess,
            duration: new Date().getTime() - taskStartTime.getTime(),
            errors: [], // Collected during observation
            userComments: []
          });
          
        } catch (error) {
          errors.push({
            task,
            error: error.message,
            timestamp: new Date(),
            severity: 'high'
          });
          
          taskResults.push({
            task,
            success: false,
            duration: new Date().getTime() - taskStartTime.getTime(),
            errors: [error.message],
            userComments: []
          });
        }
      }

      // Post-scenario interview
      const postScenarioFeedback = await this.conductPostScenarioInterview(user, scenario);
      userFeedback.push(...postScenarioFeedback);

      return {
        user,
        taskResults,
        overallSuccess: taskResults.every(tr => tr.success),
        totalDuration: new Date().getTime() - startTime.getTime(),
        satisfactionRating: await this.collectSatisfactionRating(user),
        feedback: userFeedback,
        errors
      };

    } catch (error) {
      console.error(`UAT scenario failed for user ${user.id}:`, error);
      throw error;
    }
  }

  private async observeTaskExecution(user: TestUser, task: string): Promise<boolean> {
    // In real implementation, this would involve:
    // - Screen recording
    // - Keystroke logging
    // - Think-aloud protocol recording
    // - Eye tracking (if available)
    // - Time measurement
    
    console.log(`User ${user.id} attempting task: ${task}`);
    
    // Simulate task execution and success determination
    // In practice, this would be manual observation or automated testing
    const simulatedSuccess = Math.random() > 0.2; // 80% success rate simulation
    
    return simulatedSuccess;
  }

  private calculateUserSatisfaction(feedback: UserFeedback[]): UserSatisfactionMetrics {
    if (feedback.length === 0) {
      return {
        overallRating: 0,
        easeOfUse: 0,
        featureCompleteness: 0,
        performance: 0,
        reliability: 0
      };
    }

    return {
      overallRating: this.averageRating(feedback, 'overallRating'),
      easeOfUse: this.averageRating(feedback, 'easeOfUse'),
      featureCompleteness: this.averageRating(feedback, 'featureCompleteness'),
      performance: this.averageRating(feedback, 'performance'),
      reliability: this.averageRating(feedback, 'reliability')
    };
  }

  private averageRating(feedback: UserFeedback[], metric: keyof UserSatisfactionMetrics): number {
    const ratings = feedback.map(f => f.ratings[metric]).filter(r => r > 0);
    return ratings.length > 0 ? ratings.reduce((sum, r) => sum + r, 0) / ratings.length : 0;
  }

  private generateRecommendations(results: UATResults): string[] {
    const recommendations: string[] = [];

    // Analyze task success rates
    const lowSuccessScenarios = results.scenarios.filter(s => s.overallSuccess < 0.8);
    if (lowSuccessScenarios.length > 0) {
      recommendations.push(
        `Improve user experience for scenarios with low success rates: ${
          lowSuccessScenarios.map(s => s.scenario.title).join(', ')
        }`
      );
    }

    // Analyze satisfaction ratings
    if (results.userSatisfaction.overallRating < 4.0) {
      recommendations.push('Focus on improving overall user satisfaction');
    }

    if (results.userSatisfaction.easeOfUse < 4.0) {
      recommendations.push('Simplify user interface and improve usability');
    }

    if (results.userSatisfaction.performance < 4.0) {
      recommendations.push('Optimize application performance');
    }

    // Analyze common issues
    const commonIssues = this.identifyOverallCommonIssues(results.scenarios);
    if (commonIssues.length > 0) {
      recommendations.push(`Address common user issues: ${commonIssues.join(', ')}`);
    }

    return recommendations;
  }

  private identifyOverallCommonIssues(scenarios: ScenarioResult[]): string[] {
    const allIssues = scenarios.flatMap(s => s.commonIssues);
    const issueFrequency = new Map<string, number>();

    for (const issue of allIssues) {
      issueFrequency.set(issue, (issueFrequency.get(issue) || 0) + 1);
    }

    return Array.from(issueFrequency.entries())
      .filter(([_, count]) => count >= 2) // Issues appearing in 2+ scenarios
      .sort(([_, a], [__, b]) => b - a)
      .map(([issue, _]) => issue);
  }
}
```

### Final Validation Checklist
```typescript
// tests/validation/final-validation.ts
export class FinalValidationChecklist {
  private validationItems: ValidationItem[] = [
    // Functionality Validation
    {
      category: 'functionality',
      id: 'user-authentication',
      title: 'User Authentication System',
      description: 'Login, logout, session management work correctly',
      priority: 'critical',
      validationMethod: 'automated',
      acceptanceCriteria: [
        'Users can register with valid email',
        'Login with correct credentials succeeds',
        'Invalid credentials are rejected',
        'Session expires appropriately',
        'Password reset functionality works'
      ]
    },
    {
      category: 'functionality',
      id: 'conversation-management',
      title: 'Conversation Management',
      description: 'Complete conversation lifecycle management',
      priority: 'critical',
      validationMethod: 'automated',
      acceptanceCriteria: [
        'Users can create new conversations',
        'Messages can be sent and received',
        'Conversations can be searched and filtered',
        'Conversation metadata is accurate',
        'Conversation sharing works correctly'
      ]
    },
    {
      category: 'functionality',
      id: 'real-time-features',
      title: 'Real-Time Features',
      description: 'WebSocket-based real-time functionality',
      priority: 'high',
      validationMethod: 'automated',
      acceptanceCriteria: [
        'Real-time message updates work',
        'Typing indicators function correctly',
        'Presence status updates properly',
        'Connection recovery works',
        'Multi-user scenarios work'
      ]
    },

    // Performance Validation
    {
      category: 'performance',
      id: 'response-times',
      title: 'API Response Times',
      description: 'All API endpoints meet performance requirements',
      priority: 'high',
      validationMethod: 'automated',
      acceptanceCriteria: [
        'API responses < 500ms average',
        '95th percentile < 2 seconds',
        'Database queries < 100ms average',
        'File uploads complete reasonably',
        'Analytics queries perform well'
      ]
    },
    {
      category: 'performance',
      id: 'load-capacity',
      title: 'Load Handling Capacity',
      description: 'System handles expected concurrent load',
      priority: 'high',
      validationMethod: 'automated',
      acceptanceCriteria: [
        '100+ concurrent users supported',
        'Memory usage stays under limits',
        'CPU usage remains reasonable',
        'No memory leaks detected',
        'Graceful degradation under load'
      ]
    },

    // Security Validation
    {
      category: 'security',
      id: 'authentication-security',
      title: 'Authentication Security',
      description: 'Authentication mechanisms are secure',
      priority: 'critical',
      validationMethod: 'manual',
      acceptanceCriteria: [
        'Passwords are properly hashed',
        'JWT tokens have reasonable expiry',
        'Session management is secure',
        'No authentication bypass possible',
        'Rate limiting prevents brute force'
      ]
    },
    {
      category: 'security',
      id: 'data-protection',
      title: 'Data Protection',
      description: 'User data is properly protected',
      priority: 'critical',
      validationMethod: 'manual',
      acceptanceCriteria: [
        'Data transmission is encrypted',
        'Sensitive data is not logged',
        'Input validation prevents injection',
        'Authorization checks work properly',
        'Data access is properly controlled'
      ]
    },

    // Accessibility Validation
    {
      category: 'accessibility',
      id: 'wcag-compliance',
      title: 'WCAG 2.1 AA Compliance',
      description: 'Application meets accessibility standards',
      priority: 'high',
      validationMethod: 'manual',
      acceptanceCriteria: [
        'Keyboard navigation works completely',
        'Screen readers can access all content',
        'Color contrast meets requirements',
        'Focus indicators are visible',
        'ARIA labels are properly implemented'
      ]
    },

    // Compatibility Validation
    {
      category: 'compatibility',
      id: 'browser-compatibility',
      title: 'Cross-Browser Compatibility',
      description: 'Works across all supported browsers',
      priority: 'high',
      validationMethod: 'automated',
      acceptanceCriteria: [
        'Chrome latest version works',
        'Firefox latest version works',
        'Safari latest version works',
        'Edge latest version works',
        'Mobile browsers work correctly'
      ]
    },
    {
      category: 'compatibility',
      id: 'responsive-design',
      title: 'Responsive Design',
      description: 'Works across all device sizes',
      priority: 'high',
      validationMethod: 'automated',
      acceptanceCriteria: [
        'Desktop experience is optimal',
        'Tablet layout works correctly',
        'Mobile interface is usable',
        'Touch interactions work',
        'Text remains readable on all sizes'
      ]
    },

    // User Experience Validation
    {
      category: 'user-experience',
      id: 'usability',
      title: 'Overall Usability',
      description: 'Application is intuitive and easy to use',
      priority: 'high',
      validationMethod: 'manual',
      acceptanceCriteria: [
        'New users can complete onboarding',
        'Core features are discoverable',
        'Error messages are helpful',
        'Loading states are informative',
        'User flows are logical'
      ]
    }
  ];

  async executeValidation(): Promise<ValidationReport> {
    const report: ValidationReport = {
      startTime: new Date(),
      validationItems: [],
      overallStatus: 'pending',
      criticalIssues: [],
      recommendations: []
    };

    for (const item of this.validationItems) {
      const itemResult = await this.validateItem(item);
      report.validationItems.push(itemResult);
    }

    report.overallStatus = this.determineOverallStatus(report.validationItems);
    report.criticalIssues = this.identifyCriticalIssues(report.validationItems);
    report.recommendations = this.generateRecommendations(report.validationItems);
    report.endTime = new Date();

    return report;
  }

  private async validateItem(item: ValidationItem): Promise<ValidationItemResult> {
    const result: ValidationItemResult = {
      item,
      status: 'pending',
      validatedCriteria: [],
      issues: [],
      evidence: []
    };

    try {
      for (const criteria of item.acceptanceCriteria) {
        const criteriaResult = await this.validateCriteria(item, criteria);
        result.validatedCriteria.push(criteriaResult);
      }

      result.status = result.validatedCriteria.every(c => c.passed) ? 'passed' : 'failed';
      
      if (result.status === 'failed') {
        result.issues = result.validatedCriteria
          .filter(c => !c.passed)
          .map(c => c.issue!)
          .filter(Boolean);
      }

    } catch (error) {
      result.status = 'error';
      result.issues.push({
        severity: 'high',
        description: `Validation error: ${error.message}`,
        category: item.category
      });
    }

    return result;
  }

  private async validateCriteria(item: ValidationItem, criteria: string): Promise<CriteriaValidationResult> {
    // This would integrate with actual testing frameworks
    // For now, simulate validation based on item type
    
    if (item.validationMethod === 'automated') {
      return await this.runAutomatedValidation(item, criteria);
    } else {
      return await this.runManualValidation(item, criteria);
    }
  }

  private async runAutomatedValidation(item: ValidationItem, criteria: string): Promise<CriteriaValidationResult> {
    // Integrate with test runners, monitoring systems, etc.
    console.log(`Running automated validation for: ${criteria}`);
    
    // Simulate automated test execution
    const passed = Math.random() > 0.1; // 90% pass rate simulation
    
    return {
      criteria,
      passed,
      evidence: passed ? 'Automated test passed' : 'Automated test failed',
      issue: passed ? undefined : {
        severity: 'medium',
        description: `Automated validation failed for: ${criteria}`,
        category: item.category
      }
    };
  }

  private async runManualValidation(item: ValidationItem, criteria: string): Promise<CriteriaValidationResult> {
    // This would involve manual testing checklists, expert review, etc.
    console.log(`Manual validation required for: ${criteria}`);
    
    // In practice, this would pause for manual verification
    // For simulation, assume manual validation has higher pass rate
    const passed = Math.random() > 0.05; // 95% pass rate simulation
    
    return {
      criteria,
      passed,
      evidence: passed ? 'Manual verification completed' : 'Manual verification found issues',
      issue: passed ? undefined : {
        severity: 'medium',
        description: `Manual validation failed for: ${criteria}`,
        category: item.category
      }
    };
  }

  private determineOverallStatus(items: ValidationItemResult[]): ValidationStatus {
    const criticalFailed = items
      .filter(item => item.item.priority === 'critical')
      .some(item => item.status === 'failed');
    
    if (criticalFailed) {
      return 'failed';
    }

    const anyFailed = items.some(item => item.status === 'failed');
    if (anyFailed) {
      return 'warning';
    }

    const allPassed = items.every(item => item.status === 'passed');
    return allPassed ? 'passed' : 'pending';
  }

  private identifyCriticalIssues(items: ValidationItemResult[]): ValidationIssue[] {
    return items
      .flatMap(item => item.issues)
      .filter(issue => issue.severity === 'critical' || issue.severity === 'high')
      .sort((a, b) => {
        const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
        return severityOrder[a.severity] - severityOrder[b.severity];
      });
  }

  private generateRecommendations(items: ValidationItemResult[]): string[] {
    const recommendations: string[] = [];
    
    const failedCritical = items.filter(
      item => item.item.priority === 'critical' && item.status === 'failed'
    );
    
    if (failedCritical.length > 0) {
      recommendations.push(
        `URGENT: Address critical validation failures: ${
          failedCritical.map(item => item.item.title).join(', ')
        }`
      );
    }

    const failedHigh = items.filter(
      item => item.item.priority === 'high' && item.status === 'failed'
    );
    
    if (failedHigh.length > 0) {
      recommendations.push(
        `Address high-priority validation failures: ${
          failedHigh.map(item => item.item.title).join(', ')
        }`
      );
    }

    // Category-specific recommendations
    const categories = ['security', 'performance', 'accessibility', 'functionality'];
    for (const category of categories) {
      const categoryIssues = items
        .filter(item => item.item.category === category && item.status === 'failed')
        .length;
      
      if (categoryIssues > 0) {
        recommendations.push(`Review and fix ${category} issues (${categoryIssues} failures)`);
      }
    }

    return recommendations;
  }
}
```

## Performance Requirements
- **Test Execution Time**: Complete test suite runs within 2 hours
- **Test Coverage**: Achieve >90% code coverage across all components
- **Bug Resolution**: Critical bugs resolved within 24 hours
- **Performance Benchmarks**: All performance requirements validated
- **User Satisfaction**: Achieve >4.0/5.0 average satisfaction rating

## Acceptance Criteria
- [ ] All automated tests passing (>95% success rate)
- [ ] User acceptance testing completed with positive feedback
- [ ] Security audit passed with no critical vulnerabilities
- [ ] Performance benchmarks met under realistic load
- [ ] Cross-browser compatibility verified
- [ ] Accessibility compliance (WCAG 2.1 AA) achieved
- [ ] Mobile and tablet experience validated
- [ ] Production deployment tested successfully
- [ ] Documentation completed and reviewed
- [ ] Stakeholder sign-off obtained

## Testing Procedures
1. **Automated Test Execution**: Full test suite with comprehensive coverage
2. **Manual Testing**: Edge cases and complex user scenarios
3. **User Acceptance Testing**: Real users validating core workflows
4. **Security Testing**: Vulnerability assessment and penetration testing
5. **Performance Validation**: Load testing under realistic conditions
6. **Compatibility Testing**: Cross-browser and device validation
7. **Accessibility Testing**: WCAG compliance and assistive technology testing

## Integration Points
- **All Phase 2 Components**: Final integration validation
- **Production Environment**: Deployment and configuration testing
- **Monitoring Systems**: Alerting and monitoring validation
- **Backup Systems**: Data backup and recovery testing

## Quality Gates
- **Critical Bugs**: Zero critical bugs remaining
- **High Priority Bugs**: <3 high priority bugs remaining
- **Performance**: All benchmarks achieved
- **Security**: No critical or high security vulnerabilities
- **Accessibility**: WCAG 2.1 AA compliance verified
- **User Satisfaction**: >80% positive user feedback

## Risk Mitigation
- **Quality Issues**: Comprehensive testing at multiple levels
- **User Satisfaction**: Early user feedback integration
- **Performance Problems**: Realistic load testing and optimization
- **Security Vulnerabilities**: Multiple security validation layers
- **Deployment Issues**: Production environment validation

## Success Metrics
- **Test Coverage**: >90% code coverage achieved
- **Defect Density**: <2 defects per 1000 lines of code
- **User Satisfaction**: >4.0/5.0 average rating
- **Performance**: All SLA requirements met
- **Security**: Zero critical vulnerabilities
- **Accessibility**: 100% WCAG 2.1 AA compliance

## Deliverables
- Comprehensive test execution report
- User acceptance testing results
- Security audit report
- Performance validation report
- Cross-browser compatibility report
- Accessibility compliance report
- Bug tracking and resolution log
- Production readiness certification
- User feedback analysis
- Phase 2 completion documentation

## Testing Best Practices Summary

### Test Strategy Selection Guide

**Unit Tests (Vitest Recommended)**
- **Use for**: Pure functions, utility methods, individual components
- **Benefits**: Fast execution, isolated testing, excellent TypeScript support
- **Coverage Target**: 90%+ for critical business logic

**Integration Tests (Vitest + Test Containers)**
- **Use for**: API endpoints, database operations, service interactions
- **Benefits**: Real environment testing, catches integration issues
- **Coverage Target**: 80%+ for critical user flows

**End-to-End Tests (Playwright)**
- **Use for**: Complete user journeys, cross-browser compatibility
- **Benefits**: Real user experience validation, visual regression testing
- **Coverage Target**: 70%+ for critical user paths

**Performance Tests (Artillery + Custom Scripts)**
- **Use for**: Load testing, stress testing, memory leak detection
- **Benefits**: Validates SLA requirements, identifies bottlenecks
- **Coverage Target**: All critical performance scenarios

### Testing Pyramid Implementation

```
    /\
   /  \    E2E Tests (Few)
  /____\   - Critical user journeys
 /      \  - Cross-browser compatibility
/        \ 
\        /  Integration Tests (Some)
 \______/   - API endpoints
  \    /    - Database operations
   \  /     - Service interactions
    \/      
   ____     Unit Tests (Many)
  /____\    - Pure functions
 /______\   - Component logic
/__________\ - Utility methods
```

### Code Quality Metrics

**Minimum Thresholds:**
- Line Coverage: 85%
- Branch Coverage: 80%
- Function Coverage: 90%
- Statement Coverage: 85%

**Quality Gates:**
- Zero critical bugs
- <3 high priority issues
- All tests passing
- Performance benchmarks met
- Security vulnerabilities resolved

### Accessibility Testing Checklist

**WCAG 2.1 AA Compliance:**
- [ ] Keyboard navigation support
- [ ] Screen reader compatibility
- [ ] Color contrast ratios (4.5:1 minimum)
- [ ] Focus indicators visible
- [ ] ARIA labels implemented
- [ ] Semantic HTML structure
- [ ] Alternative text for images
- [ ] Form validation messages

**Tools:**
- axe-core for automated testing
- NVDA/JAWS for screen reader testing
- Color contrast analyzers
- Keyboard-only navigation testing

### Security Testing Framework

**Automated Security Tests:**
```typescript
// Example security test
describe('Security Tests', () => {
  it('should prevent SQL injection', async () => {
    const maliciousInput = "'; DROP TABLE users; --";
    const response = await request(app)
      .post('/api/search')
      .send({ query: maliciousInput });
    
    expect(response.status).toBe(400);
    expect(response.body.error).toContain('Invalid input');
  });

  it('should validate JWT tokens', async () => {
    const invalidToken = 'invalid.jwt.token';
    const response = await request(app)
      .get('/api/protected')
      .set('Authorization', `Bearer ${invalidToken}`);
    
    expect(response.status).toBe(401);
  });
});
```

**Manual Security Checklist:**
- [ ] Input validation and sanitization
- [ ] Authentication bypass attempts
- [ ] Authorization boundary testing
- [ ] Session management validation
- [ ] Cross-site scripting (XSS) prevention
- [ ] Cross-site request forgery (CSRF) protection
- [ ] Data encryption verification
- [ ] Rate limiting effectiveness

### Performance Testing Strategies

**Load Testing Scenarios:**
1. **Normal Load**: Expected concurrent users (100-200)
2. **Peak Load**: Maximum expected users (500-1000)
3. **Stress Testing**: Beyond maximum capacity (1000+)
4. **Spike Testing**: Sudden load increases
5. **Endurance Testing**: Extended periods (24+ hours)

**Key Performance Metrics:**
- Response time: <500ms average, <2s 95th percentile
- Throughput: >1000 requests/second
- Error rate: <1% under normal load
- Resource utilization: <80% CPU, <85% memory

### Continuous Testing Pipeline

**Pre-commit Hooks:**
```json
{
  "husky": {
    "hooks": {
      "pre-commit": "lint-staged",
      "pre-push": "npm run test:unit"
    }
  },
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix",
      "prettier --write",
      "vitest related --run"
    ]
  }
}
```

**CI/CD Integration:**
1. **Pull Request**: Unit + Integration tests
2. **Staging Deploy**: Full test suite + E2E
3. **Production Deploy**: Smoke tests + monitoring
4. **Post-Deploy**: Performance validation

### Testing Environment Management

**Test Data Management:**
```typescript
// Test data factory
export class TestDataFactory {
  static createUser(overrides = {}) {
    return {
      id: faker.string.uuid(),
      email: faker.internet.email(),
      name: faker.person.fullName(),
      createdAt: faker.date.recent(),
      ...overrides
    };
  }

  static createConversation(userId: string, overrides = {}) {
    return {
      id: faker.string.uuid(),
      title: faker.lorem.sentence(),
      userId,
      createdAt: faker.date.recent(),
      ...overrides
    };
  }
}
```

**Environment Configuration:**
```typescript
// Test environment config
export const testConfig = {
  database: {
    url: process.env.TEST_DATABASE_URL || 'sqlite::memory:',
    logging: false
  },
  redis: {
    url: process.env.TEST_REDIS_URL || 'redis://localhost:6379/1'
  },
  external: {
    mockApis: true,
    timeouts: 1000
  }
};
```

### Mock Strategy Guidelines

**When to Mock:**
- External API calls
- Database operations (in unit tests)
- File system operations
- Network requests
- Time-dependent operations

**When NOT to Mock:**
- Pure functions
- Simple data transformations
- Configuration objects
- Constants and enums

**Mock Best Practices:**
```typescript
// Good: Specific, realistic mock
const mockUserService = {
  getUser: vi.fn().mockResolvedValue({
    id: '123',
    email: 'test@example.com',
    name: 'Test User'
  }),
  updateUser: vi.fn().mockResolvedValue(true)
};

// Bad: Generic, unrealistic mock
const mockUserService = {
  getUser: vi.fn().mockResolvedValue({}),
  updateUser: vi.fn().mockResolvedValue(true)
};
```

### Test Reporting and Monitoring

**Coverage Reports:**
- HTML reports for local development
- JSON reports for CI/CD integration
- Trend analysis for coverage changes
- Quality gate enforcement

**Test Execution Monitoring:**
- Test duration trends
- Flaky test identification
- Success rate tracking
- Resource usage monitoring

**Alerting:**
- Test failure notifications
- Coverage threshold violations
- Performance regression alerts
- Security vulnerability findings

## Advanced Testing Patterns and Best Practices (2024)

### Modern Testing Architecture Patterns

#### Feature Object Pattern for E2E Tests
```typescript
// tests/e2e/features/conversation-feature.ts
import { Page } from '@playwright/test';

export class ConversationFeature {
  constructor(private page: Page) {}

  async createNewConversation(title: string) {
    await this.page.getByRole('button', { name: 'New Conversation' }).click();
    await this.page.getByPlaceholder('Enter conversation title').fill(title);
    await this.page.getByRole('button', { name: 'Create' }).click();
  }

  async sendMessage(content: string) {
    await this.page.getByTestId('message-input').fill(content);
    await this.page.getByRole('button', { name: 'Send' }).click();
  }

  async expectMessageToBeVisible(content: string) {
    await this.page.getByText(content).waitFor({ state: 'visible' });
  }

  async expectConversationTitle(title: string) {
    await this.page.getByRole('heading', { name: title }).waitFor({ state: 'visible' });
  }
}
```

#### Component Testing with Composition API Patterns
```typescript
// tests/unit/composables/useConversationManager.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ref, nextTick } from 'vue';
import { useConversationManager } from '@/composables/useConversationManager';
import { createWrapper } from '@vue/test-utils';

describe('useConversationManager', () => {
  let mockApi: any;

  beforeEach(() => {
    mockApi = {
      getConversations: vi.fn(),
      createConversation: vi.fn(),
      updateConversation: vi.fn(),
      deleteConversation: vi.fn()
    };
  });

  it('should manage conversation state correctly', async () => {
    const mockConversations = [
      { id: '1', title: 'Test 1', createdAt: '2024-01-01' },
      { id: '2', title: 'Test 2', createdAt: '2024-01-02' }
    ];

    mockApi.getConversations.mockResolvedValue(mockConversations);

    const { conversations, loading, error, loadConversations } = useConversationManager(mockApi);

    expect(loading.value).toBe(false);
    expect(conversations.value).toEqual([]);

    await loadConversations();

    expect(loading.value).toBe(false);
    expect(conversations.value).toEqual(mockConversations);
    expect(error.value).toBeNull();
  });

  it('should handle API errors gracefully', async () => {
    const errorMessage = 'Failed to load conversations';
    mockApi.getConversations.mockRejectedValue(new Error(errorMessage));

    const { conversations, loading, error, loadConversations } = useConversationManager(mockApi);

    await loadConversations();

    expect(loading.value).toBe(false);
    expect(conversations.value).toEqual([]);
    expect(error.value).toBe(errorMessage);
  });
});
```

#### Modern API Testing with MSW (Mock Service Worker)
```typescript
// tests/mocks/handlers.ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/conversations', () => {
    return HttpResponse.json([
      { id: '1', title: 'Test Conversation', createdAt: '2024-01-01' },
      { id: '2', title: 'Another Test', createdAt: '2024-01-02' }
    ]);
  }),

  http.post('/api/conversations', async ({ request }) => {
    const newConversation = await request.json();
    return HttpResponse.json(
      { id: '3', ...newConversation, createdAt: new Date().toISOString() },
      { status: 201 }
    );
  }),

  http.get('/api/conversations/:id', ({ params }) => {
    const { id } = params;
    return HttpResponse.json({
      id,
      title: `Conversation ${id}`,
      messages: [
        { id: '1', content: 'Hello', timestamp: '2024-01-01T10:00:00Z' },
        { id: '2', content: 'Hi there', timestamp: '2024-01-01T10:01:00Z' }
      ]
    });
  }),

  http.delete('/api/conversations/:id', ({ params }) => {
    return HttpResponse.json({ success: true });
  })
];

// tests/mocks/server.ts
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);
```

### Advanced Performance Testing Strategies

#### Memory Leak Detection
```typescript
// tests/performance/memory-leak.test.ts
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { mount } from '@vue/test-utils';
import ConversationList from '@/components/ConversationList.vue';

describe('Memory Leak Detection', () => {
  let initialMemory: number;
  let wrapper: any;

  beforeEach(() => {
    if (global.gc) {
      global.gc();
    }
    initialMemory = process.memoryUsage().heapUsed;
  });

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount();
    }
  });

  it('should not have memory leaks after mounting/unmounting components', () => {
    const iterations = 1000;
    
    for (let i = 0; i < iterations; i++) {
      wrapper = mount(ConversationList);
      wrapper.unmount();
    }

    if (global.gc) {
      global.gc();
    }

    const finalMemory = process.memoryUsage().heapUsed;
    const memoryIncrease = finalMemory - initialMemory;
    
    // Allow for some memory variance but flag significant increases
    expect(memoryIncrease).toBeLessThan(50 * 1024 * 1024); // 50MB threshold
  });
});
```

#### Load Testing with Artillery (TypeScript)
```typescript
// tests/performance/load-test.ts
import { Config, Scenario } from 'artillery';

export const config: Config = {
  target: 'http://localhost:3000',
  phases: [
    { duration: 60, arrivalRate: 10 },
    { duration: 120, arrivalRate: 20 },
    { duration: 60, arrivalRate: 30 }
  ],
  defaults: {
    headers: {
      'Content-Type': 'application/json'
    }
  }
};

export const scenarios: Scenario[] = [
  {
    name: 'API Load Test',
    weight: 70,
    flow: [
      { get: { url: '/api/conversations' } },
      { think: 2 },
      { post: { url: '/api/conversations', json: { title: 'Test {{ $randomString() }}' } } },
      { think: 1 },
      { get: { url: '/api/conversations/{{ id }}' } }
    ]
  },
  {
    name: 'WebSocket Load Test',
    weight: 30,
    flow: [
      { ws: { url: 'ws://localhost:3000/ws' } },
      { send: { message: 'Hello from Artillery' } },
      { think: 5 },
      { send: { message: 'Test message {{ $randomString() }}' } }
    ]
  }
];
```

### Visual Regression Testing

#### Playwright Visual Testing
```typescript
// tests/visual/visual-regression.test.ts
import { test, expect } from '@playwright/test';

test.describe('Visual Regression Tests', () => {
  test('conversation list should match visual baseline', async ({ page }) => {
    await page.goto('/conversations');
    
    // Wait for content to load
    await page.waitForLoadState('networkidle');
    
    // Take screenshot and compare
    await expect(page).toHaveScreenshot('conversation-list.png');
  });

  test('conversation detail should match visual baseline', async ({ page }) => {
    await page.goto('/conversations/1');
    
    // Wait for messages to load
    await page.waitForSelector('[data-testid="message-item"]');
    
    // Take screenshot of specific component
    await expect(page.locator('[data-testid="conversation-detail"]')).toHaveScreenshot('conversation-detail.png');
  });

  test('responsive design should work correctly', async ({ page }) => {
    await page.goto('/conversations');
    
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page).toHaveScreenshot('conversation-list-mobile.png');
    
    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page).toHaveScreenshot('conversation-list-tablet.png');
    
    // Test desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
    await expect(page).toHaveScreenshot('conversation-list-desktop.png');
  });
});
```

### Security Testing Enhancements

#### SQL Injection Prevention Testing
```typescript
// tests/security/sql-injection.test.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { ConversationRepository } from '@/database/repositories/conversation-repository';
import { SQLiteManager } from '@/database/sqlite-manager';

describe('SQL Injection Prevention', () => {
  let repository: ConversationRepository;
  let sqliteManager: SQLiteManager;

  beforeEach(async () => {
    sqliteManager = new SQLiteManager(':memory:');
    await sqliteManager.initialize();
    repository = new ConversationRepository(sqliteManager);
  });

  it('should prevent SQL injection in search queries', async () => {
    const maliciousInput = "'; DROP TABLE conversations; --";
    
    // This should not crash or delete data
    const result = await repository.searchConversations(maliciousInput);
    
    // Verify the table still exists and is functional
    expect(result).toBeDefined();
    expect(Array.isArray(result)).toBe(true);
    
    // Verify we can still insert data
    const newConversation = await repository.createConversation({
      title: 'Test after injection attempt',
      projectId: 'test-project'
    });
    
    expect(newConversation).toBeDefined();
    expect(newConversation.id).toBeDefined();
  });

  it('should sanitize user input in conversation titles', async () => {
    const maliciousTitle = "<script>alert('XSS')</script>";
    
    const conversation = await repository.createConversation({
      title: maliciousTitle,
      projectId: 'test-project'
    });
    
    expect(conversation.title).not.toContain('<script>');
    expect(conversation.title).toBe("alert('XSS')"); // Should be sanitized
  });
});
```

#### JWT Token Security Testing
```typescript
// tests/security/jwt-validation.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { JWTManager } from '@/auth/jwt-manager';
import jwt from 'jsonwebtoken';

describe('JWT Security', () => {
  let jwtManager: JWTManager;
  const validSecret = 'test-secret-key';

  beforeEach(() => {
    jwtManager = new JWTManager(validSecret);
  });

  it('should reject tokens with invalid signatures', () => {
    const token = jwt.sign({ userId: '123' }, 'wrong-secret');
    
    expect(() => jwtManager.validateToken(token)).toThrow('Invalid token signature');
  });

  it('should reject expired tokens', () => {
    const token = jwt.sign({ userId: '123' }, validSecret, { expiresIn: '1ms' });
    
    // Wait for token to expire
    setTimeout(() => {
      expect(() => jwtManager.validateToken(token)).toThrow('Token expired');
    }, 10);
  });

  it('should reject tokens with tampered payload', () => {
    const token = jwt.sign({ userId: '123' }, validSecret);
    const tamperedToken = token.slice(0, -10) + 'tampered123';
    
    expect(() => jwtManager.validateToken(tamperedToken)).toThrow('Invalid token');
  });

  it('should validate legitimate tokens', () => {
    const payload = { userId: '123', role: 'user' };
    const token = jwt.sign(payload, validSecret);
    
    const decoded = jwtManager.validateToken(token);
    expect(decoded.userId).toBe('123');
    expect(decoded.role).toBe('user');
  });
});
```

### AI-Powered Testing Enhancements

#### Conversation Context Testing
```typescript
// tests/ai/conversation-context.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ConversationContextAnalyzer } from '@/ai/conversation-context-analyzer';
import { ConversationRepository } from '@/database/repositories/conversation-repository';

describe('Conversation Context Analysis', () => {
  let analyzer: ConversationContextAnalyzer;
  let mockRepository: ConversationRepository;

  beforeEach(() => {
    mockRepository = {
      getConversationMessages: vi.fn(),
      getConversationMetadata: vi.fn()
    } as any;
    
    analyzer = new ConversationContextAnalyzer(mockRepository);
  });

  it('should analyze conversation complexity correctly', async () => {
    const mockMessages = [
      { id: '1', content: 'Simple question', toolCalls: [] },
      { id: '2', content: 'Complex analysis with multiple steps', toolCalls: ['read', 'analyze', 'write'] },
      { id: '3', content: 'Another complex task', toolCalls: ['search', 'process', 'generate'] }
    ];

    mockRepository.getConversationMessages.mockResolvedValue(mockMessages);

    const analysis = await analyzer.analyzeComplexity('conversation-1');

    expect(analysis.complexity).toBe('high');
    expect(analysis.toolUsageCount).toBe(6);
    expect(analysis.averageToolsPerMessage).toBe(2);
  });

  it('should detect conversation patterns', async () => {
    const mockMessages = [
      { id: '1', content: 'Debug this error', toolCalls: ['read', 'analyze'] },
      { id: '2', content: 'Fix the bug', toolCalls: ['edit', 'test'] },
      { id: '3', content: 'Test the solution', toolCalls: ['run', 'validate'] }
    ];

    mockRepository.getConversationMessages.mockResolvedValue(mockMessages);

    const patterns = await analyzer.detectPatterns('conversation-1');

    expect(patterns).toContain('debugging');
    expect(patterns).toContain('problem-solving');
    expect(patterns).toContain('iterative-development');
  });
});
```

### Test Data Management

#### Test Data Factories
```typescript
// tests/factories/conversation-factory.ts
import { faker } from '@faker-js/faker';

export class ConversationFactory {
  static create(overrides: Partial<Conversation> = {}): Conversation {
    return {
      id: faker.string.uuid(),
      title: faker.lorem.sentence(),
      projectId: faker.string.uuid(),
      createdAt: faker.date.past().toISOString(),
      updatedAt: faker.date.recent().toISOString(),
      messageCount: faker.number.int({ min: 1, max: 100 }),
      ...overrides
    };
  }

  static createMany(count: number, overrides: Partial<Conversation> = {}): Conversation[] {
    return Array.from({ length: count }, () => this.create(overrides));
  }

  static withMessages(messageCount: number): Conversation {
    return this.create({
      messageCount,
      messages: MessageFactory.createMany(messageCount)
    });
  }
}

export class MessageFactory {
  static create(overrides: Partial<Message> = {}): Message {
    return {
      id: faker.string.uuid(),
      conversationId: faker.string.uuid(),
      content: faker.lorem.paragraph(),
      timestamp: faker.date.recent().toISOString(),
      toolCalls: faker.helpers.arrayElements(['read', 'write', 'analyze', 'search'], { min: 0, max: 3 }),
      ...overrides
    };
  }

  static createMany(count: number, overrides: Partial<Message> = {}): Message[] {
    return Array.from({ length: count }, () => this.create(overrides));
  }
}
```

### Continuous Integration Enhancements

#### GitHub Actions with Matrix Testing
```yaml
# .github/workflows/comprehensive-testing.yml
name: Comprehensive Testing Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18.x, 20.x, 22.x]
        package: [core, frontend, backend, file-monitor]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run unit tests for ${{ matrix.package }}
      run: npm run test:unit:${{ matrix.package }}
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        flags: unit-tests-${{ matrix.package }}

  integration-tests:
    runs-on: ubuntu-latest
    services:
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20.x'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run integration tests
      run: npm run test:integration
      env:
        REDIS_URL: redis://localhost:6379

  e2e-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        browser: [chromium, firefox, webkit]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20.x'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Install Playwright browsers
      run: npx playwright install --with-deps ${{ matrix.browser }}
    
    - name: Start application
      run: npm run dev &
    
    - name: Wait for application to be ready
      run: npx wait-on http://localhost:3000
    
    - name: Run E2E tests
      run: npx playwright test --project=${{ matrix.browser }}
    
    - name: Upload test results
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: playwright-report-${{ matrix.browser }}
        path: playwright-report/

  performance-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20.x'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Start application
      run: npm run dev &
    
    - name: Wait for application to be ready
      run: npx wait-on http://localhost:3000
    
    - name: Run performance tests
      run: npm run test:performance
    
    - name: Upload performance results
      uses: actions/upload-artifact@v4
      with:
        name: performance-results
        path: performance-results/

  security-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20.x'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run security audit
      run: npm audit --audit-level=high
    
    - name: Run SAST scan
      run: npm run test:security
    
    - name: Run dependency check
      uses: dependency-check/Dependency-Check_Action@main
      with:
        project: 'ccobservatory'
        path: '.'
        format: 'JSON'
```

## Phase 2 Completion Criteria
- [ ] MVP functionality completely implemented
- [ ] All acceptance criteria validated
- [ ] Quality gates successfully passed
- [ ] User acceptance testing completed
- [ ] Production deployment validated
- [ ] Documentation finalized
- [ ] Team knowledge transfer completed
- [ ] Phase 3 planning initiated
- [ ] Modern testing patterns implemented
- [ ] Security testing comprehensive
- [ ] Performance benchmarks established
- [ ] Visual regression testing operational
- [ ] AI-powered testing capabilities validated