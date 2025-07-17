import { apiClient } from './client';
import { wsClient } from './websocket';
import { projects, conversations, connectionStatus } from '$lib/stores/conversations';

// Service to handle data loading and WebSocket setup
export class DashboardService {
	async initialize(): Promise<{
		analytics: {
			total_conversations: number;
			total_messages: number;
			total_tool_calls: number;
			avg_conversation_length: number;
		};
	}> {
		// Test API connection
		const isConnected = await apiClient.testConnection();
		if (!isConnected) {
			throw new Error('Cannot connect to backend API');
		}

		// Load initial data
		const analytics = await this.loadData();

		// Set up WebSocket message handlers
		this.setupWebSocketHandlers();

		return { analytics };
	}

	private async loadData() {
		// Load projects
		const projectsData = await apiClient.getProjects();
		projects.set(projectsData);

		// Load recent conversations
		const conversationsData = await apiClient.getConversations(1, 10);
		conversations.set(conversationsData.data);

		// Load analytics
		const analyticsData = await apiClient.getAnalytics();
		return analyticsData;
	}

	private setupWebSocketHandlers() {
		wsClient.on('conversation_update', data => {
			conversations.updateConversation(data.id, data);
		});

		wsClient.on('project_update', data => {
			projects.update(currentProjects =>
				currentProjects.map(p => (p.id === data.id ? { ...p, ...data } : p))
			);
		});
	}

	async retryLoad() {
		return await this.loadData();
	}
}

export const dashboardService = new DashboardService();