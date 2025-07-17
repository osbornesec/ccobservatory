import { browser } from '$app/environment';
import { config, log, logError } from '$lib/config';
import type { ApiResponse, PaginatedResponse, ApiError } from '$lib/types';

/**
 * HTTP client for API communication with proper error handling,
 * request timeout, and retry logic.
 */
class ApiClient {
	private readonly baseUrl: string;
	private readonly timeout: number;

	constructor(baseUrl?: string, timeout?: number) {
		this.baseUrl = baseUrl || config.apiBaseUrl;
		this.timeout = timeout || config.requestTimeout;
	}

	/**
	 * Test API connection
	 */
	public async testConnection(): Promise<boolean> {
		try {
			const response = await this.request('/health', {
				method: 'GET'
			});
			return response.status === 200;
		} catch (error) {
			logError('API connection test failed:', error);
			return false;
		}
	}

	/**
	 * GET request
	 */
	public async get<T>(endpoint: string, params?: Record<string, any>): Promise<ApiResponse<T>> {
		const url = new URL(endpoint, this.baseUrl);
		
		if (params) {
			Object.entries(params).forEach(([key, value]) => {
				if (value !== undefined && value !== null) {
					url.searchParams.append(key, String(value));
				}
			});
		}

		const response = await this.request(url.toString(), {
			method: 'GET'
		});

		return this.handleResponse<T>(response);
	}

	/**
	 * POST request
	 */
public async post<T>(endpoint: string, data?: Record<string, unknown>): Promise<ApiResponse<T>> {
		const response = await this.request(endpoint, {
			method: 'POST',
			body: data ? JSON.stringify(data) : undefined
		});

		return this.handleResponse<T>(response);
	}

	/**
	 * PUT request
	 */
	public async put<T>(endpoint: string, data?: Record<string, unknown>): Promise<ApiResponse<T>> {
		const response = await this.request(endpoint, {
			method: 'PUT',
			body: data ? JSON.stringify(data) : undefined
		});

		return this.handleResponse<T>(response);
	}

	/**
	 * DELETE request
	 */
	public async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
		const response = await this.request(endpoint, {
			method: 'DELETE'
		});

		return this.handleResponse<T>(response);
	}

	/**
	 * Make paginated GET request
	 */
	public async getPaginated<T>(
		endpoint: string, 
		params?: Record<string, any>
	): Promise<PaginatedResponse<T>> {
		const response = await this.get<T[]>(endpoint, params);
		
		// Assume the response includes pagination info
		return response as PaginatedResponse<T>;
	}

	/**
	 * Make raw HTTP request
	 */
	private async request(url: string, options: RequestInit = {}): Promise<Response> {
		if (!browser) {
			throw new Error('API requests can only be made in browser environment');
		}

		const fullUrl = url.startsWith('http') ? url : `${this.baseUrl}${url}`;
		
		const requestOptions: RequestInit = {
			...options,
			headers: {
				'Content-Type': 'application/json',
				...options.headers
			},
			signal: AbortSignal.timeout(this.timeout)
		};

		log(`API ${options.method || 'GET'}: ${fullUrl}`);

		try {
			const response = await fetch(fullUrl, requestOptions);
			
			if (!response.ok) {
				throw await this.createApiError(response);
			}

			return response;

		} catch (error) {
			if (error instanceof DOMException && error.name === 'TimeoutError') {
				throw new Error(`Request timeout after ${this.timeout}ms`);
			}
			
			if (error instanceof TypeError) {
				throw new Error('Network error - check your connection');
			}

			throw error;
		}
	}

	/**
	 * Handle API response and parse JSON
	 */
	private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
		try {
			const data = await response.json();
			
			log(`API Response (${response.status}):`, data);
			
			const apiResponse: any = {
				data: data.data || data,
				success: data.success !== false,
				message: data.message
			};

			if (data.pagination) {
				apiResponse.pagination = data.pagination;
			}

			return apiResponse;

		} catch (error) {
			logError('Failed to parse API response:', error);
			throw new Error('Invalid API response format');
		}
	}

	/**
	 * Create structured API error from response
	 */
	private async createApiError(response: Response): Promise<ApiError> {
		let errorData: any = {};
		
		try {
			errorData = await response.json();
		} catch {
			// Response doesn't contain JSON
		}

		const error: ApiError = new Error(
			errorData.message || 
			errorData.error || 
			`HTTP ${response.status}: ${response.statusText}`
		);
		
		error.name = 'ApiError';
		error.status = response.status;
		error.code = errorData.code;
		error.details = errorData.details;

		return error;
	}

	// Convenience methods for API endpoints
	public async health(): Promise<boolean> {
		return this.testConnection();
	}

	public async getProjects() {
		return this.get('/projects');
	}

	public async getProject(id: string) {
		return this.get(`/projects/${id}`);
	}

	public async createProject(data: Partial<import('$lib/types').Project>) {
		return this.post('/projects', data);
	}

	public async getConversations(page = 1, perPage = 20) {
		return this.getPaginated('/conversations', { page, per_page: perPage });
	}

	public async getConversation(id: string) {
		return this.get(`/conversations/${id}`);
	}

	public async search(query: string, filters?: any) {
		return this.post('/search', { query, filters });
	}

	public async getAnalytics(timeRange?: string) {
		return this.get('/analytics', timeRange ? { time_range: timeRange } : undefined);
	}
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export class for custom instances
export { ApiClient };

/**
 * Check if an error is an API error
 */
export function isApiError(error: any): error is ApiError {
	return error && error.name === 'ApiError' && typeof error.status === 'number';
}

/**
 * Get a user-friendly error message from any error
 */
export function getErrorMessage(error: any): string {
	if (isApiError(error)) {
		return error.message;
	}
	
	if (error instanceof Error) {
		return error.message;
	}
	
	if (typeof error === 'string') {
		return error;
	}
	
	return 'An unexpected error occurred';
}

// API methods using the singleton instance
export const api = {
	// Projects
	async getProjects() {
		return apiClient.get('/projects');
	},

	async getProject(id: string) {
		return apiClient.get(`/projects/${id}`);
	},

	// Conversations  
	async getConversations(page = 1, perPage = 20) {
		return apiClient.getPaginated('/conversations', { page, per_page: perPage });
	},

	async getConversation(id: string) {
		return apiClient.get(`/conversations/${id}`);
	},

	// Messages
	async getMessages(conversationId: string) {
		return apiClient.get(`/conversations/${conversationId}/messages`);
	},

	// Analytics
	async getAnalytics(timeRange?: string) {
		return apiClient.get('/analytics', timeRange ? { time_range: timeRange } : undefined);
	},

	// Search
	async search(query: string, filters?: import('$lib/types').SearchFilters) {
		return apiClient.post('/search', { query, filters });
	}
};