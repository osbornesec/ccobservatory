import { writable } from 'svelte/store';
import { vi } from 'vitest';

// Mock theme store for testing
export function createMockThemeStore() {
	const { subscribe, set } = writable<string>('light');
	
	return {
		subscribe,
		set,
		init: vi.fn(() => {
			set('light');
		})
	};
}

// Mock API client for testing
export function createMockApiClient() {
	return {
		testConnection: vi.fn().mockResolvedValue(true),
		getProjects: vi.fn().mockResolvedValue([]),
		getConversations: vi.fn().mockResolvedValue({ data: [] }),
		getAnalytics: vi.fn().mockResolvedValue({
			total_conversations: 0,
			total_messages: 0,
			total_tool_calls: 0,
			avg_conversation_length: 0
		})
	};
}

// Mock WebSocket client for testing
export function createMockWsClient() {
	return {
		on: vi.fn(),
		off: vi.fn(),
		emit: vi.fn()
	};
}