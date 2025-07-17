// Core data types for Claude Code Observatory

export interface Project {
	id: string;
	name: string;
	path: string;
	created_at: string;
	updated_at: string;
	conversation_count: number;
	status: 'active' | 'inactive';
}

export interface Conversation {
	id: string;
	project_id: string;
	title: string;
	summary?: string;
	status: 'active' | 'completed' | 'error';
	created_at: string;
	updated_at: string;
	message_count: number;
	tool_usage_count: number;
	duration_seconds?: number;
	file_path: string;
}

export interface Message {
	id: string;
	conversation_id: string;
	role: 'user' | 'assistant';
	content: string;
	timestamp: string;
	token_count?: number;
	tool_calls?: ToolCall[];
	sequence_number: number;
}

export interface ToolCall {
	id: string;
	message_id: string;
	tool_name: string;
	tool_input: Record<string, any>;
	tool_output?: string;
	status: 'pending' | 'success' | 'error';
	execution_time_ms?: number;
	created_at: string;
}

export interface Analytics {
	total_conversations: number;
	total_messages: number;
	total_tool_calls: number;
	avg_conversation_length: number;
	most_used_tools: ToolUsageStats[];
	daily_activity: DailyActivity[];
	project_activity: ProjectActivity[];
}

export interface ToolUsageStats {
	tool_name: string;
	usage_count: number;
	success_rate: number;
	avg_execution_time_ms: number;
}

export interface DailyActivity {
	date: string;
	conversation_count: number;
	message_count: number;
	tool_call_count: number;
}

export interface ProjectActivity {
	project_id: string;
	project_name: string;
	conversation_count: number;
	last_activity: string;
}

// API response types
export interface ApiResponse<T> {
	data: T;
	success: boolean;
	message?: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
	pagination: {
		page: number;
		per_page: number;
		total: number;
		pages: number;
	};
}

// WebSocket message types
export interface WebSocketMessage<T = any> {
	type: string;
	data: T;
	timestamp: number;
}

export type WebSocketEventHandler<T = any> = (data: T) => void;

export interface WebSocketConfig {
	url: string;
	reconnectInterval: number;
	maxReconnectAttempts: number;
	heartbeatInterval?: number;
}

export interface ConversationUpdateMessage {
	id: string;
	title?: string;
	status?: 'active' | 'completed' | 'error';
	message_count?: number;
	tool_usage_count?: number;
	updated_at?: string;
}

export interface ProjectUpdateMessage {
	id: string;
	name?: string;
	conversation_count?: number;
	status?: 'active' | 'inactive';
	updated_at?: string;
}

// Search and filter types
export interface SearchFilters {
	project?: string;
	dateRange?: {
		start: Date;
		end: Date;
	};
	messageType?: 'user' | 'assistant';
	toolName?: string;
	status?: 'active' | 'completed' | 'error';
}

export interface SearchResult {
	conversations: Conversation[];
	messages: Message[];
	total: number;
}

// Chart data types
export interface ChartDataPoint {
	x: string | number | Date;
	y: number;
	label?: string;
}

export interface ChartSeries {
	name: string;
	data: ChartDataPoint[];
	color?: string;
}

// Component prop types
export interface ConversationListProps {
	conversations: Conversation[];
	selectedConversation?: Conversation;
	onSelect?: (conversation: Conversation) => void;
	showProject?: boolean;
}

export interface MessageListProps {
	messages: Message[];
	isLoading?: boolean;
	showTimestamps?: boolean;
}

export interface AnalyticsDashboardProps {
	analytics: Analytics;
	timeRange: 'day' | 'week' | 'month' | 'year';
	onTimeRangeChange?: (range: string) => void;
}

// Error types
export interface ApiError extends Error {
	status?: number;
	code?: string;
	details?: Record<string, any>;
}

// Theme types
export type Theme = 'light' | 'dark';

// Navigation types
export interface NavItem {
	href: string;
	label: string;
	icon?: string;
	badge?: string | number;
}
