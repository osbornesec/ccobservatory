import { browser } from '$app/environment';
import { onDestroy } from 'svelte';
import { writable, type Writable } from 'svelte/store';
import { wsClient } from './websocket';
import { apiClient } from './client';
import { conversationsStore as conversations, projects, connectionStatus } from '$lib/stores/conversations';
import { config, log, logError, logWarn } from '$lib/config';
import type { 
	Analytics, 
	Project,
	Conversation,
	ConversationUpdateMessage, 
	ProjectUpdateMessage,
	ApiResponse
} from '$lib/types';

/**
 * Dashboard service with proper WebSocket lifecycle management.
 * Handles initialization, data loading, WebSocket setup, and cleanup.
 * 
 * Features:
 * - Automatic WebSocket connection management
 * - Proper cleanup on navigation and component destruction
 * - Memory leak prevention
 * - Error handling and recovery
 * - Centralized state management
 */
class DashboardService {
	private initialized = false;
	private cleanupFunctions: (() => void)[] = [];
	private isDestroyed = false;
	
	// State stores
	public readonly connectionState: Writable<{
		status: 'connecting' | 'connected' | 'disconnected' | 'error';
		attempts: number;
		lastError?: string;
	}> = writable({
		status: 'disconnected',
		attempts: 0
	});

	/**
	 * Initialize dashboard service with WebSocket and data loading
	 */
	public async initialize(): Promise<{ analytics: Analytics }> {
		if (this.initialized) {
			logWarn('Dashboard service already initialized');
			return this.loadInitialData();
		}

		if (!browser) {
			logWarn('Dashboard service initialization attempted outside browser environment');
			throw new Error('Dashboard service requires browser environment');
		}

		try {
			log('Initializing dashboard service...');
			
			// Test API connection first
			const isApiConnected = await this.testApiConnection();
			if (!isApiConnected) {
				throw new Error('Cannot connect to backend API');
			}

			// Setup WebSocket connection and handlers
			this.setupWebSocketHandlers();
			
			// Connect to WebSocket
			this.connectWebSocket();
			
			// Load initial data
			const analytics = await this.loadInitialData();
			
			// Setup cleanup on component destruction
			this.setupCleanup();
			
			this.initialized = true;
			log('Dashboard service initialized successfully');
			
			return { analytics };
			
		} catch (error) {
			logError('Failed to initialize dashboard service:', error);
			this.cleanup();
			throw error;
		}
	}

	/**
	 * Retry loading data after an error
	 */
	public async retryLoad(): Promise<Analytics> {
		try {
			log('Retrying dashboard data load...');
			
			// Test API connection
			const isConnected = await this.testApiConnection();
			if (!isConnected) {
				throw new Error('API connection failed');
			}

			// Reconnect WebSocket if needed
			if (!wsClient.isConnected) {
				this.connectWebSocket();
			}

			// Reload data
			const response = await apiClient.get<Analytics>('/analytics');
			log('Dashboard data reloaded successfully');
			
			return response.data;
			
		} catch (error) {
			logError('Failed to retry dashboard load:', error);
			throw error;
		}
	}

	/**
	 * Cleanup all resources and connections
	 */
	public cleanup(): void {
		if (this.isDestroyed) {
			return;
		}

		log('Cleaning up dashboard service...');
		
		// Disconnect WebSocket
		wsClient.disconnect();
		
		// Run all cleanup functions
		this.cleanupFunctions.forEach(cleanup => {
			try {
				cleanup();
			} catch (error) {
				logError('Error during cleanup:', error);
			}
		});
		
		this.cleanupFunctions = [];
		this.initialized = false;
		this.isDestroyed = true;
		
		log('Dashboard service cleanup completed');
	}

	/**
	 * Get current connection status
	 */
	public getConnectionStatus() {
		return wsClient.getConnectionStatus();
	}

	/**
	 * Force reconnect WebSocket
	 */
	public reconnectWebSocket(): void {
		log('Forcing WebSocket reconnection...');
		wsClient.disconnect();
		setTimeout(() => {
			if (!this.isDestroyed) {
				this.connectWebSocket();
			}
		}, 1000);
	}

	/**
	 * Test API connection
	 */
	private async testApiConnection(): Promise<boolean> {
		try {
			const response = await fetch(`${config.apiBaseUrl}/health`, {
				method: 'GET',
				headers: { 'Content-Type': 'application/json' },
				signal: AbortSignal.timeout(config.requestTimeout)
			});
			
			return response.ok;
		} catch (error) {
			logError('API connection test failed:', error);
			return false;
		}
	}

	/**
	 * Load initial data from API
	 */
	private async loadInitialData(): Promise<Analytics> {
		try {
			log('Loading initial dashboard data...');
			
			// Load all initial data in parallel
			const [analyticsResponse, projectsResponse, conversationsResponse] = await Promise.all([
				apiClient.get<Analytics>('/analytics'),
				apiClient.get<Project[]>('/projects'),
				apiClient.get<Conversation[]>('/conversations')
			]);
			
			// Update stores
			projects.set(projectsResponse.data as Project[]);
			conversations.set(conversationsResponse.data as Conversation[]);
			
			log('Initial dashboard data loaded successfully');
			return analyticsResponse.data;
			
		} catch (error) {
			logError('Failed to load initial data:', error);
			throw error;
		}
	}

	/**
	 * Setup WebSocket message handlers
	 */
	private setupWebSocketHandlers(): void {
		log('Setting up WebSocket handlers...');
		
		// Connection status handlers
		const unsubscribeConnected = wsClient.on('connection:connected', () => {
			log('WebSocket connected - updating connection status');
			connectionStatus.set('connected');
			this.connectionState.update(state => ({
				...state,
				status: 'connected',
				attempts: 0,
				lastError: undefined
			}));
		});

		const unsubscribeDisconnected = wsClient.on('connection:disconnected', () => {
			log('WebSocket disconnected - updating connection status');
			connectionStatus.set('disconnected');
			this.connectionState.update(state => ({
				...state,
				status: 'disconnected'
			}));
		});

		const unsubscribeError = wsClient.on('connection:error', (error: any) => {
			logError('WebSocket error:', error);
			connectionStatus.set('disconnected');
			this.connectionState.update(state => ({
				...state,
				status: 'error',
				lastError: error?.message || 'Connection error'
			}));
		});

		// Data update handlers
		const unsubscribeConversationUpdate = wsClient.on<ConversationUpdateMessage>(
			'conversation_update', 
			(data) => {
				log('Received conversation update:', data);
				conversations.updateConversation(data.id, data);
			}
		);

		const unsubscribeProjectUpdate = wsClient.on<ProjectUpdateMessage>(
			'project_update', 
			(data) => {
				log('Received project update:', data);
				projects.update(currentProjects =>
					currentProjects.map(p => (p.id === data.id ? { ...p, ...data } : p))
				);
			}
		);

		// Store cleanup functions
		this.cleanupFunctions.push(
			unsubscribeConnected,
			unsubscribeDisconnected,
			unsubscribeError,
			unsubscribeConversationUpdate,
			unsubscribeProjectUpdate
		);
	}

	/**
	 * Connect to WebSocket with retry logic
	 */
	private connectWebSocket(): void {
		if (!config.enableRealTime) {
			log('Real-time updates disabled - skipping WebSocket connection');
			return;
		}

		try {
			log('Connecting to WebSocket...');
			this.connectionState.update(state => ({
				...state,
				status: 'connecting'
			}));
			
			wsClient.connect();
			
		} catch (error) {
			logError('Failed to connect WebSocket:', error);
			this.connectionState.update(state => ({
				...state,
				status: 'error',
				lastError: error instanceof Error ? error.message : 'Connection failed'
			}));
		}
	}

	/**
	 * Setup cleanup hooks for component lifecycle
	 */
	private setupCleanup(): void {
		if (!browser) return;

		// Svelte onDestroy hook (when available)
		try {
			onDestroy(() => {
				log('Svelte onDestroy triggered - cleaning up dashboard service');
				this.cleanup();
			});
		} catch (error) {
			// onDestroy not available outside component context
			logWarn('onDestroy not available - manual cleanup required');
		}

		// Browser unload events as fallback
		const handleUnload = () => {
			this.cleanup();
		};

		window.addEventListener('beforeunload', handleUnload);
		window.addEventListener('pagehide', handleUnload);

		// Store cleanup function
		this.cleanupFunctions.push(() => {
			window.removeEventListener('beforeunload', handleUnload);
			window.removeEventListener('pagehide', handleUnload);
		});
	}
}

// Create and export singleton instance
export const dashboardService = new DashboardService();

// Export helper functions for component use
export function useDashboard() {
	return {
		initialize: () => dashboardService.initialize(),
		retryLoad: () => dashboardService.retryLoad(),
		cleanup: () => dashboardService.cleanup(),
		getConnectionStatus: () => dashboardService.getConnectionStatus(),
		reconnect: () => dashboardService.reconnectWebSocket(),
		connectionState: dashboardService.connectionState
	};
}

/**
 * SvelteKit-compatible dashboard service for component use
 * Automatically handles cleanup on component destruction
 */
export function createDashboardService() {
	const service = new DashboardService();
	
	// Automatic cleanup on component destroy
	if (browser) {
		try {
			onDestroy(() => {
				service.cleanup();
			});
		} catch (error) {
			// Not in component context
		}
	}
	
	return {
		initialize: () => service.initialize(),
		retryLoad: () => service.retryLoad(),
		connectionState: service.connectionState,
		getConnectionStatus: () => service.getConnectionStatus(),
		reconnect: () => service.reconnectWebSocket()
	};
}