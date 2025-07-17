import { browser } from '$app/environment';
import { beforeNavigate } from '$app/navigation';
import { config, log, logError, logWarn } from '$lib/config';
import type { WebSocketMessage, WebSocketEventHandler, WebSocketConfig } from '$lib/types';

/**
 * WebSocket client with automatic reconnection, exponential backoff,
 * and proper memory management for SvelteKit navigation lifecycle.
 * 
 * Features:
 * - Automatic reconnection with exponential backoff
 * - Proper cleanup on navigation
 * - Memory leak prevention
 * - Error handling and recovery
 * - Connection state management
 */
export class WebSocketClient {
	private ws: WebSocket | null = null;
	private messageHandlers = new Map<string, Set<WebSocketEventHandler>>();
	private reconnectTimeoutId: number | null = null;
	private heartbeatIntervalId: number | null = null;
	private connectionAttempts = 0;
	private isConnecting = false;
	private isDestroyed = false;
	private currentReconnectDelay = 1000;
	
	// Configuration
	private readonly url: string;
	private readonly maxReconnectAttempts: number;
	private readonly baseReconnectDelay: number;
	private readonly maxReconnectDelay: number;
	private readonly heartbeatInterval: number;

	constructor(
		url?: string,
		reconnectInterval?: number,
		maxReconnectAttempts?: number
	) {
		this.url = url || config.wsUrl;
		this.baseReconnectDelay = reconnectInterval || config.reconnectInterval;
		this.maxReconnectAttempts = maxReconnectAttempts || config.maxReconnectAttempts;
		this.maxReconnectDelay = 30000; // Max 30 seconds
		this.heartbeatInterval = 30000; // 30 seconds heartbeat
		this.currentReconnectDelay = this.baseReconnectDelay;

		// Set up navigation cleanup
		this.setupNavigationCleanup();
	}

	/**
	 * Connect to WebSocket server with automatic reconnection
	 */
	public connect(): void {
		// Only connect in browser environment
		if (!browser) {
			logWarn('WebSocket connection attempted outside browser environment');
			return;
		}

		if (this.isDestroyed) {
			logError('Cannot connect - WebSocket client has been destroyed');
			return;
		}

		if (this.isConnecting || this.isConnected) {
			log('WebSocket already connecting or connected');
			return;
		}

		this.isConnecting = true;
		this.connectionAttempts++;

		try {
			log(`Attempting WebSocket connection to ${this.url} (attempt ${this.connectionAttempts})`);
			
			this.ws = new WebSocket(this.url);
			this.setupWebSocketEventHandlers();
			
		} catch (error) {
			logError('Failed to create WebSocket connection:', error);
			this.handleConnectionError();
		}
	}

	/**
	 * Disconnect WebSocket and clean up resources
	 */
	public disconnect(): void {
		log('Disconnecting WebSocket');
		
		this.clearTimeouts();
		this.clearHeartbeat();
		
		if (this.ws) {
			// Remove event listeners to prevent memory leaks
			this.ws.onopen = null;
			this.ws.onclose = null;
			this.ws.onerror = null;
			this.ws.onmessage = null;
			
			if (this.ws.readyState === WebSocket.OPEN) {
				this.ws.close(1000, 'Client disconnect');
			}
			
			this.ws = null;
		}
		
		this.isConnecting = false;
		this.connectionAttempts = 0;
		this.currentReconnectDelay = this.baseReconnectDelay;
	}

	/**
	 * Destroy WebSocket client and clean up all resources
	 * This should be called when the component/service is being destroyed
	 */
	public destroy(): void {
		log('Destroying WebSocket client');
		
		this.isDestroyed = true;
		this.disconnect();
		this.messageHandlers.clear();
	}

	/**
	 * Send message to WebSocket server
	 */
	public send<T = any>(type: string, data: T): void {
		if (!this.isConnected) {
			logWarn(`Cannot send message - WebSocket not connected. Message type: ${type}`);
			return;
		}

		const message: WebSocketMessage<T> = {
			type,
			data,
			timestamp: Date.now()
		};

		try {
			this.ws!.send(JSON.stringify(message));
			log(`Sent WebSocket message: ${type}`, data);
		} catch (error) {
			logError('Failed to send WebSocket message:', error);
		}
	}

	/**
	 * Register message handler for specific message type
	 * Returns unsubscribe function
	 */
	public on<T = any>(type: string, handler: WebSocketEventHandler<T>): () => void {
		if (!this.messageHandlers.has(type)) {
			this.messageHandlers.set(type, new Set());
		}
		
		this.messageHandlers.get(type)!.add(handler);

		// Return unsubscribe function
		return () => {
			const handlers = this.messageHandlers.get(type);
			if (handlers) {
				handlers.delete(handler);
				if (handlers.size === 0) {
					this.messageHandlers.delete(type);
				}
			}
		};
	}

	/**
	 * Check if WebSocket is connected
	 */
	public get isConnected(): boolean {
		return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
	}

	/**
	 * Get current WebSocket ready state
	 */
	public get readyState(): number {
		return this.ws?.readyState ?? WebSocket.CLOSED;
	}

	/**
	 * Get connection status information
	 */
	public getConnectionStatus(): {
		connected: boolean;
		connecting: boolean;
		attempts: number;
		readyState: number;
		nextRetryIn?: number;
	} {
		return {
			connected: this.isConnected,
			connecting: this.isConnecting,
			attempts: this.connectionAttempts,
			readyState: this.readyState,
			nextRetryIn: this.reconnectTimeoutId ? this.currentReconnectDelay : undefined
		};
	}

	/**
	 * Setup WebSocket event handlers
	 */
	private setupWebSocketEventHandlers(): void {
		if (!this.ws) return;

		this.ws.onopen = (event) => {
			log('WebSocket connected successfully');
			this.isConnecting = false;
			this.connectionAttempts = 0;
			this.currentReconnectDelay = this.baseReconnectDelay;
			this.startHeartbeat();
			this.notifyConnectionHandlers('connected', event);
		};

		this.ws.onclose = (event) => {
			log('WebSocket connection closed', { code: event.code, reason: event.reason });
			this.isConnecting = false;
			this.clearHeartbeat();
			this.notifyConnectionHandlers('disconnected', event);
			
			// Attempt reconnection if not a clean close and not destroyed
			if (event.code !== 1000 && !this.isDestroyed) {
				this.scheduleReconnect();
			}
		};

		this.ws.onerror = (event) => {
			logError('WebSocket error occurred:', event);
			this.notifyConnectionHandlers('error', event);
			this.handleConnectionError();
		};

		this.ws.onmessage = (event) => {
			try {
				const message = JSON.parse(event.data);
				this.handleMessage(message);
			} catch (error) {
				logError('Failed to parse WebSocket message:', error, event.data);
			}
		};
	}

	/**
	 * Handle incoming WebSocket messages
	 */
	private handleMessage(message: WebSocketMessage): void {
		log('Received WebSocket message:', message.type, message.data);

		// Handle special system messages
		if (message.type === 'ping') {
			this.send('pong', { timestamp: Date.now() });
			return;
		}

		// Dispatch to registered handlers
		const handlers = this.messageHandlers.get(message.type);
		if (handlers) {
			handlers.forEach(handler => {
				try {
					handler(message.data);
				} catch (error) {
					logError(`Error in message handler for ${message.type}:`, error);
				}
			});
		} else {
			logWarn(`No handlers registered for message type: ${message.type}`);
		}
	}

	/**
	 * Handle connection errors and cleanup
	 */
	private handleConnectionError(): void {
		this.isConnecting = false;
		this.clearHeartbeat();

		if (!this.isDestroyed) {
			this.scheduleReconnect();
		}
	}

	/**
	 * Schedule reconnection with exponential backoff
	 */
	private scheduleReconnect(): void {
		if (this.connectionAttempts >= this.maxReconnectAttempts) {
			logError(`Max reconnection attempts (${this.maxReconnectAttempts}) reached. Giving up.`);
			this.notifyConnectionHandlers('error', new Error('Max reconnection attempts reached'));
			return;
		}

		if (this.reconnectTimeoutId) {
			clearTimeout(this.reconnectTimeoutId);
		}

		log(`Scheduling reconnection in ${this.currentReconnectDelay}ms`);
		
		this.reconnectTimeoutId = window.setTimeout(() => {
			this.reconnectTimeoutId = null;
			if (!this.isDestroyed) {
				this.connect();
			}
		}, this.currentReconnectDelay);

		// Exponential backoff with jitter
		this.currentReconnectDelay = Math.min(
			this.currentReconnectDelay * 2 + Math.random() * 1000,
			this.maxReconnectDelay
		);
	}

	/**
	 * Start heartbeat to keep connection alive
	 */
	private startHeartbeat(): void {
		this.clearHeartbeat();
		
		this.heartbeatIntervalId = window.setInterval(() => {
			if (this.isConnected) {
				this.send('ping', { timestamp: Date.now() });
			}
		}, this.heartbeatInterval);
	}

	/**
	 * Clear heartbeat interval
	 */
	private clearHeartbeat(): void {
		if (this.heartbeatIntervalId) {
			clearInterval(this.heartbeatIntervalId);
			this.heartbeatIntervalId = null;
		}
	}

	/**
	 * Clear all timeouts
	 */
	private clearTimeouts(): void {
		if (this.reconnectTimeoutId) {
			clearTimeout(this.reconnectTimeoutId);
			this.reconnectTimeoutId = null;
		}
	}

	/**
	 * Notify connection state handlers
	 */
	private notifyConnectionHandlers(status: 'connected' | 'disconnected' | 'error', event: any): void {
		const handlers = this.messageHandlers.get(`connection:${status}`);
		if (handlers) {
			handlers.forEach(handler => {
				try {
					handler(event);
				} catch (error) {
					logError(`Error in connection handler for ${status}:`, error);
				}
			});
		}
	}

	/**
	 * Setup navigation cleanup using SvelteKit lifecycle hooks
	 */
	private setupNavigationCleanup(): void {
		if (!browser) return;

		// Clean up before navigation
		beforeNavigate(() => {
			log('Navigation detected - cleaning up WebSocket resources');
			this.disconnect();
		});

		// Clean up on page unload
		if (typeof window !== 'undefined') {
			const handleUnload = () => {
				this.destroy();
			};

			window.addEventListener('beforeunload', handleUnload);
			window.addEventListener('pagehide', handleUnload);

			// Store cleanup function for potential manual cleanup
			(this as any).cleanupUnloadListeners = () => {
				window.removeEventListener('beforeunload', handleUnload);
				window.removeEventListener('pagehide', handleUnload);
			};
		}
	}
}

// Export singleton instance
export const wsClient = new WebSocketClient();

// Export connection status helpers
export function createConnectionStatusStore() {
	return {
		connecting: () => wsClient.on('connection:connecting', () => {}),
		connected: () => wsClient.on('connection:connected', () => {}),
		disconnected: () => wsClient.on('connection:disconnected', () => {}),
		error: (handler: (error: any) => void) => wsClient.on('connection:error', handler)
	};
}