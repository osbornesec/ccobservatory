// Basic API client for data fetching
class ApiClient {
	async testConnection(): Promise<boolean> {
		// Stub implementation
		return true;
	}

	async getProjects(): Promise<any[]> {
		// Stub implementation
		return [];
	}

	async getConversations(page: number, limit: number): Promise<{ data: any[] }> {
		// Stub implementation  
		return { data: [] };
	}

	async getAnalytics(): Promise<{
		total_conversations: number;
		total_messages: number;
		total_tool_calls: number;
		avg_conversation_length: number;
	}> {
		// Stub implementation
		return {
			total_conversations: 0,
			total_messages: 0,
			total_tool_calls: 0,
			avg_conversation_length: 0
		};
	}
}

export const apiClient = new ApiClient();