// Basic WebSocket client for real-time communication
class WebSocketClient {
	private handlers: Record<string, ((data: any) => void)[]> = {};

	on(event: string, handler: (data: any) => void): void {
		if (!this.handlers[event]) {
			this.handlers[event] = [];
		}
		this.handlers[event].push(handler);
	}

	off(event: string, handler: (data: any) => void): void {
		if (this.handlers[event]) {
			this.handlers[event] = this.handlers[event].filter(h => h !== handler);
		}
	}

	emit(event: string, data: any): void {
		if (this.handlers[event]) {
			this.handlers[event].forEach(handler => handler(data));
		}
	}
}

export const wsClient = new WebSocketClient();