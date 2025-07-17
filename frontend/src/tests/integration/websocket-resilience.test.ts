import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { WebSocketClient } from '$lib/api/websocket';
import { dashboardService } from '$lib/api/dashboard';
import { connectionStatus, conversations, projects } from '$lib/stores/conversations';
import { get } from 'svelte/store';

// Mock WebSocket for testing
class MockWebSocket {
	static CONNECTING = 0;
	static OPEN = 1;
	static CLOSING = 2;
	static CLOSED = 3;

	public readyState: number = MockWebSocket.CLOSED;
	public onopen: ((event: Event) => void) | null = null;
	public onclose: ((event: CloseEvent) => void) | null = null;
	public onerror: ((event: Event) => void) | null = null;
	public onmessage: ((event: MessageEvent) => void) | null = null;

	constructor(public url: string) {
		// Simulate connection delay
		setTimeout(() => {
			this.readyState = MockWebSocket.OPEN;
			this.onopen?.(new Event('open'));
		}, 10);
	}

	send(data: string): void {
		if (this.readyState !== MockWebSocket.OPEN) {
			throw new Error('WebSocket is not open');
		}
		// Echo back for testing
		setTimeout(() => {
			this.onmessage?.(new MessageEvent('message', { data }));
		}, 5);
	}

	close(code?: number, reason?: string): void {
		this.readyState = MockWebSocket.CLOSED;
		this.onclose?.(new CloseEvent('close', { code: code || 1000, reason }));
	}

	simulateError(): void {
		this.onerror?.(new Event('error'));
	}

	simulateNetworkFailure(): void {
		this.readyState = MockWebSocket.CLOSED;
		this.onclose?.(new CloseEvent('close', { code: 1006, reason: 'Network error' }));
	}
}

// Mock browser environment
vi.mock('$app/environment', () => ({
	browser: true
}));

vi.mock('$app/navigation', () => ({
	beforeNavigate: vi.fn()
}));

vi.mock('$lib/config', () => ({
	config: {
		wsUrl: 'ws://localhost:3000/ws',
		reconnectInterval: 100,
		maxReconnectAttempts: 3,
		enableRealTime: true,
		apiBaseUrl: 'http://localhost:8000',
		requestTimeout: 5000
	},
	log: vi.fn(),
	logError: vi.fn(),
	logWarn: vi.fn()
}));

describe('WebSocket Resilience Integration Tests', () => {
	let mockWebSocket: MockWebSocket;
	let originalWebSocket: typeof WebSocket;
	let wsClient: WebSocketClient;

	beforeEach(() => {
		// Store original WebSocket
		originalWebSocket = global.WebSocket;

		// Mock WebSocket constructor
		global.WebSocket = vi.fn().mockImplementation((url: string) => {
			mockWebSocket = new MockWebSocket(url);
			return mockWebSocket;
		}) as any;

		// Set WebSocket constants
		global.WebSocket.CONNECTING = MockWebSocket.CONNECTING;
		global.WebSocket.OPEN = MockWebSocket.OPEN;
		global.WebSocket.CLOSING = MockWebSocket.CLOSING;
		global.WebSocket.CLOSED = MockWebSocket.CLOSED;

		// Create fresh WebSocket client
		wsClient = new WebSocketClient();

		// Clear all stores
		connectionStatus.set('disconnected');
		conversations.clear();
		projects.clear();

		vi.clearAllMocks();
	});

	afterEach(() => {
		// Cleanup
		wsClient.destroy();
		global.WebSocket = originalWebSocket;
	});

	describe('Connection Resilience', () => {
		it('should establish WebSocket connection successfully', async () => {
			wsClient.connect();

			// Wait for connection
			await new Promise(resolve => setTimeout(resolve, 50));

			expect(wsClient.isConnected).toBe(true);
			expect(wsClient.readyState).toBe(WebSocket.OPEN);
		});

		it('should handle connection errors gracefully', async () => {
			const errorHandler = vi.fn();
			wsClient.on('connection:error', errorHandler);

			wsClient.connect();
			await new Promise(resolve => setTimeout(resolve, 20));

			// Simulate connection error
			mockWebSocket.simulateError();
			await new Promise(resolve => setTimeout(resolve, 20));

			expect(errorHandler).toHaveBeenCalled();
			expect(wsClient.isConnected).toBe(false);
		});

		it('should reconnect automatically after network failure', async () => {
			const connectedHandler = vi.fn();
			const disconnectedHandler = vi.fn();

			wsClient.on('connection:connected', connectedHandler);
			wsClient.on('connection:disconnected', disconnectedHandler);

			// Initial connection
			wsClient.connect();
			await new Promise(resolve => setTimeout(resolve, 50));
			expect(connectedHandler).toHaveBeenCalledTimes(1);

			// Simulate network failure
			mockWebSocket.simulateNetworkFailure();
			await new Promise(resolve => setTimeout(resolve, 20));
			expect(disconnectedHandler).toHaveBeenCalledTimes(1);

			// Wait for reconnection attempt
			await new Promise(resolve => setTimeout(resolve, 150));
			expect(connectedHandler).toHaveBeenCalledTimes(2);
		});

		it('should implement exponential backoff for reconnection', async () => {
			const attemptTimes: number[] = [];
			const originalConnect = wsClient.connect.bind(wsClient);
			
			vi.spyOn(wsClient, 'connect').mockImplementation(() => {
				attemptTimes.push(Date.now());
				// Fail first few attempts
				if (attemptTimes.length <= 2) {
					mockWebSocket.simulateNetworkFailure();
				} else {
					originalConnect();
				}
			});

			wsClient.connect();

			// Wait for multiple reconnection attempts
			await new Promise(resolve => setTimeout(resolve, 500));

			expect(attemptTimes.length).toBeGreaterThan(2);
			
			// Check that intervals increase (exponential backoff)
			if (attemptTimes.length >= 3) {
				const interval1 = attemptTimes[1] - attemptTimes[0];
				const interval2 = attemptTimes[2] - attemptTimes[1];
				expect(interval2).toBeGreaterThan(interval1);
			}
		});

		it('should stop reconnecting after max attempts', async () => {
			const errorHandler = vi.fn();
			wsClient.on('connection:error', errorHandler);

			// Mock connect to always fail
			vi.spyOn(wsClient, 'connect').mockImplementation(() => {
				mockWebSocket.simulateNetworkFailure();
			});

			wsClient.connect();

			// Wait for all reconnection attempts
			await new Promise(resolve => setTimeout(resolve, 800));

			// Should have called error handler for max attempts reached
			expect(errorHandler).toHaveBeenCalledWith(
				expect.objectContaining({
					message: expect.stringContaining('Max reconnection attempts')
				})
			);
		});
	});

	describe('Message Handling Resilience', () => {
		it('should handle malformed JSON messages gracefully', async () => {
			wsClient.connect();
			await new Promise(resolve => setTimeout(resolve, 50));

			const handler = vi.fn();
			wsClient.on('test_message', handler);

			// Send malformed JSON
			mockWebSocket.onmessage?.(new MessageEvent('message', { 
				data: 'invalid json {' 
			}));

			await new Promise(resolve => setTimeout(resolve, 20));

			// Handler should not be called for malformed messages
			expect(handler).not.toHaveBeenCalled();
		});

		it('should handle message handler errors without crashing', async () => {
			wsClient.connect();
			await new Promise(resolve => setTimeout(resolve, 50));

			// Handler that throws error
			const errorHandler = vi.fn(() => {
				throw new Error('Handler error');
			});
			wsClient.on('test_message', errorHandler);

			// Send valid message
			const message = JSON.stringify({
				type: 'test_message',
				data: { test: true },
				timestamp: Date.now()
			});

			mockWebSocket.onmessage?.(new MessageEvent('message', { data: message }));
			await new Promise(resolve => setTimeout(resolve, 20));

			expect(errorHandler).toHaveBeenCalled();
			// WebSocket should still be connected despite handler error
			expect(wsClient.isConnected).toBe(true);
		});

		it('should handle ping/pong heartbeat correctly', async () => {
			wsClient.connect();
			await new Promise(resolve => setTimeout(resolve, 50));

			const sentMessages: string[] = [];
			const originalSend = mockWebSocket.send.bind(mockWebSocket);
			mockWebSocket.send = vi.fn((data: string) => {
				sentMessages.push(data);
				originalSend(data);
			});

			// Send ping message
			const pingMessage = JSON.stringify({
				type: 'ping',
				data: { timestamp: Date.now() },
				timestamp: Date.now()
			});

			mockWebSocket.onmessage?.(new MessageEvent('message', { data: pingMessage }));
			await new Promise(resolve => setTimeout(resolve, 20));

			// Should have sent pong response
			expect(sentMessages).toHaveLength(1);
			const pongMessage = JSON.parse(sentMessages[0]);
			expect(pongMessage.type).toBe('pong');
			expect(pongMessage.data.timestamp).toBeDefined();
		});
	});

	describe('Dashboard Service Integration', () => {
		it('should initialize dashboard service with WebSocket integration', async () => {
			// Mock API client
			global.fetch = vi.fn()
				.mockResolvedValueOnce(new Response('OK', { status: 200 })) // Health check
				.mockResolvedValueOnce(new Response(JSON.stringify({ 
					data: { 
						total_conversations: 5,
						total_messages: 50,
						total_tool_calls: 25,
						avg_conversation_length: 10,
						most_used_tools: [],
						daily_activity: [],
						project_activity: []
					} 
				}), { status: 200 })) // Analytics
				.mockResolvedValueOnce(new Response(JSON.stringify({ data: [] }), { status: 200 })) // Projects
				.mockResolvedValueOnce(new Response(JSON.stringify({ data: [] }), { status: 200 })); // Conversations

			const result = await dashboardService.initialize();

			expect(result.analytics.total_conversations).toBe(5);
			expect(wsClient.isConnected).toBe(true);
		});

		it('should handle conversation updates via WebSocket', async () => {
			wsClient.connect();
			await new Promise(resolve => setTimeout(resolve, 50));

			// Set initial conversations
			conversations.set([
				{ 
					id: 'conv1', 
					title: 'Test Conversation',
					project_id: 'proj1',
					status: 'active',
					created_at: '2024-01-01',
					updated_at: '2024-01-01',
					message_count: 5,
					tool_usage_count: 2,
					file_path: '/test/path'
				}
			]);

			// Send conversation update message
			const updateMessage = JSON.stringify({
				type: 'conversation_update',
				data: {
					id: 'conv1',
					title: 'Updated Conversation',
					message_count: 10
				},
				timestamp: Date.now()
			});

			mockWebSocket.onmessage?.(new MessageEvent('message', { data: updateMessage }));
			await new Promise(resolve => setTimeout(resolve, 20));

			// Check that conversation was updated
			const currentConversations = get(conversations);
			expect(currentConversations[0].title).toBe('Updated Conversation');
			expect(currentConversations[0].message_count).toBe(10);
		});

		it('should handle project updates via WebSocket', async () => {
			wsClient.connect();
			await new Promise(resolve => setTimeout(resolve, 50));

			// Set initial projects
			projects.set([
				{
					id: 'proj1',
					name: 'Test Project',
					path: '/test/path',
					created_at: '2024-01-01',
					updated_at: '2024-01-01',
					conversation_count: 3,
					status: 'active'
				}
			]);

			// Send project update message
			const updateMessage = JSON.stringify({
				type: 'project_update',
				data: {
					id: 'proj1',
					name: 'Updated Project',
					conversation_count: 5
				},
				timestamp: Date.now()
			});

			mockWebSocket.onmessage?.(new MessageEvent('message', { data: updateMessage }));
			await new Promise(resolve => setTimeout(resolve, 20));

			// Check that project was updated
			const currentProjects = get(projects);
			expect(currentProjects[0].name).toBe('Updated Project');
			expect(currentProjects[0].conversation_count).toBe(5);
		});

		it('should update connection status store', async () => {
			wsClient.connect();
			await new Promise(resolve => setTimeout(resolve, 50));

			expect(get(connectionStatus)).toBe('connected');

			// Simulate disconnection
			mockWebSocket.simulateNetworkFailure();
			await new Promise(resolve => setTimeout(resolve, 20));

			expect(get(connectionStatus)).toBe('disconnected');
		});
	});

	describe('Memory Management', () => {
		it('should clean up event listeners on disconnect', () => {
			wsClient.connect();
			const handler = vi.fn();
			const unsubscribe = wsClient.on('test_message', handler);

			// Disconnect and verify cleanup
			wsClient.disconnect();

			expect(wsClient.isConnected).toBe(false);
			expect(mockWebSocket.onopen).toBeNull();
			expect(mockWebSocket.onclose).toBeNull();
			expect(mockWebSocket.onerror).toBeNull();
			expect(mockWebSocket.onmessage).toBeNull();
		});

		it('should clean up message handlers on unsubscribe', () => {
			const handler = vi.fn();
			const unsubscribe = wsClient.on('test_message', handler);

			// Unsubscribe
			unsubscribe();

			// Send message - handler should not be called
			wsClient.connect();
			const message = JSON.stringify({
				type: 'test_message',
				data: { test: true },
				timestamp: Date.now()
			});

			mockWebSocket.onmessage?.(new MessageEvent('message', { data: message }));
			expect(handler).not.toHaveBeenCalled();
		});

		it('should destroy WebSocket client completely', () => {
			wsClient.connect();
			const handler = vi.fn();
			wsClient.on('test_message', handler);

			// Destroy client
			wsClient.destroy();

			expect(wsClient.isConnected).toBe(false);
			
			// Should not be able to connect after destroy
			wsClient.connect();
			expect(wsClient.isConnected).toBe(false);
		});
	});

	describe('Stress Testing', () => {
		it('should handle rapid message bursts', async () => {
			wsClient.connect();
			await new Promise(resolve => setTimeout(resolve, 50));

			const receivedMessages: any[] = [];
			wsClient.on('burst_test', (data) => {
				receivedMessages.push(data);
			});

			// Send 100 messages rapidly
			for (let i = 0; i < 100; i++) {
				const message = JSON.stringify({
					type: 'burst_test',
					data: { id: i },
					timestamp: Date.now()
				});
				mockWebSocket.onmessage?.(new MessageEvent('message', { data: message }));
			}

			await new Promise(resolve => setTimeout(resolve, 100));

			expect(receivedMessages).toHaveLength(100);
			expect(receivedMessages[0].id).toBe(0);
			expect(receivedMessages[99].id).toBe(99);
		});

		it('should handle multiple concurrent connections', async () => {
			const clients = Array.from({ length: 10 }, () => new WebSocketClient());
			const connectedClients = [];

			// Connect all clients
			for (const client of clients) {
				client.connect();
				await new Promise(resolve => setTimeout(resolve, 20));
				if (client.isConnected) {
					connectedClients.push(client);
				}
			}

			expect(connectedClients.length).toBe(10);

			// Cleanup
			for (const client of clients) {
				client.destroy();
			}
		});

		it('should maintain connection stability under load', async () => {
			wsClient.connect();
			await new Promise(resolve => setTimeout(resolve, 50));

			let messageCount = 0;
			wsClient.on('load_test', () => {
				messageCount++;
			});

			// Send messages continuously for 1 second
			const interval = setInterval(() => {
				if (wsClient.isConnected) {
					const message = JSON.stringify({
						type: 'load_test',
						data: { timestamp: Date.now() },
						timestamp: Date.now()
					});
					try {
						mockWebSocket.onmessage?.(new MessageEvent('message', { data: message }));
					} catch (error) {
						// Connection might be lost during stress test
					}
				}
			}, 10);

			await new Promise(resolve => setTimeout(resolve, 1000));
			clearInterval(interval);

			// Should have processed many messages
			expect(messageCount).toBeGreaterThan(50);
			// Connection should still be stable
			expect(wsClient.isConnected).toBe(true);
		});
	});

	describe('Navigation Lifecycle', () => {
		it('should setup navigation cleanup hooks', () => {
			const client = new WebSocketClient();
			
			// Mock beforeNavigate was called during construction
			expect(vi.mocked(require('$app/navigation').beforeNavigate)).toHaveBeenCalled();
		});

		it('should handle browser unload events', () => {
			const addEventListener = vi.spyOn(window, 'addEventListener');
			
			const client = new WebSocketClient();
			
			expect(addEventListener).toHaveBeenCalledWith('beforeunload', expect.any(Function));
			expect(addEventListener).toHaveBeenCalledWith('pagehide', expect.any(Function));
			
			client.destroy();
		});
	});
});

// Additional utility test for WebSocket status monitoring
describe('WebSocket Status Monitoring', () => {
	let wsClient: WebSocketClient;

	beforeEach(() => {
		global.WebSocket = vi.fn().mockImplementation((url: string) => {
			const mock = new MockWebSocket(url);
			return mock;
		}) as any;

		wsClient = new WebSocketClient();
	});

	afterEach(() => {
		wsClient.destroy();
	});

	it('should provide accurate connection status', async () => {
		const status1 = wsClient.getConnectionStatus();
		expect(status1.connected).toBe(false);
		expect(status1.connecting).toBe(false);

		wsClient.connect();
		
		const status2 = wsClient.getConnectionStatus();
		expect(status2.connecting).toBe(true);

		await new Promise(resolve => setTimeout(resolve, 50));

		const status3 = wsClient.getConnectionStatus();
		expect(status3.connected).toBe(true);
		expect(status3.connecting).toBe(false);
		expect(status3.attempts).toBe(1);
	});

	it('should track connection attempts', async () => {
		// Mock connection to fail initially
		vi.spyOn(wsClient, 'connect').mockImplementation(() => {
			const mockWs = global.WebSocket as any;
			const instance = new mockWs.mock.instances[0];
			instance.simulateNetworkFailure();
		});

		wsClient.connect();
		await new Promise(resolve => setTimeout(resolve, 200));

		const status = wsClient.getConnectionStatus();
		expect(status.attempts).toBeGreaterThan(1);
	});
});