# 🗺️ API Documentation - Claude Code Observatory

## 🎯 **API Overview**

### **API Design Philosophy**

Claude Code Observatory provides a comprehensive RESTful API designed for:

- **Developer-First:** Intuitive, well-documented endpoints
- **Consistent Design:** Standardized request/response patterns
- **Extensible Architecture:** Easy integration with external tools
- **Real-Time Capabilities:** WebSocket support for live data
- **Security-First:** Authentication and authorization built-in

### **API Architecture**

```
🔗 REST API (HTTP/HTTPS)
├── /api/v1/conversations
├── /api/v1/projects
├── /api/v1/analytics
├── /api/v1/teams
└── /api/v1/admin

🔄 WebSocket (Real-time)
├── /ws/conversations
├── /ws/analytics
└── /ws/notifications

📏 GraphQL (Optional)
└── /graphql
```

## 🔑 **Authentication**

### **Authentication Methods**

#### **Bearer Token Authentication**

```typescript
// Request headers
interface AuthHeaders {
  'Authorization': 'Bearer <access_token>';
  'Content-Type': 'application/json';
  'X-API-Version': 'v1';
}

// Example request
fetch('/api/v1/conversations', {
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
    'Content-Type': 'application/json'
  }
});
```

#### **API Key Authentication (Server-to-Server)**

```typescript
// API key in header
interface APIKeyHeaders {
  'X-API-Key': '<api_key>';
  'Content-Type': 'application/json';
}

// Example server-to-server request
const response = await fetch('/api/v1/analytics/overview', {
  headers: {
    'X-API-Key': 'obs_sk_1234567890abcdef',
    'Content-Type': 'application/json'
  }
});
```

### **Token Management**

#### **OAuth 2.0 Token Flow**

```typescript
// Token endpoint
POST /api/auth/token

// Request body
{
  "grant_type": "authorization_code",
  "code": "authorization_code_from_callback",
  "redirect_uri": "https://your-app.com/callback",
  "client_id": "your_client_id",
  "code_verifier": "code_verifier_from_pkce"
}

// Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "refresh_token_here",
  "scope": "conversations:read analytics:read"
}
```

#### **Token Refresh**

```typescript
// Refresh token endpoint
POST /api/auth/refresh

// Request body
{
  "grant_type": "refresh_token",
  "refresh_token": "refresh_token_here"
}

// Response
{
  "access_token": "new_access_token",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

---

## 💬 **Conversations API**

### **List Conversations**

#### **Endpoint**
```
GET /api/v1/conversations
```

#### **Query Parameters**

```typescript
interface ConversationListParams {
  project_id?: number;           // Filter by project
  status?: 'active' | 'ended';   // Filter by status
  start_date?: string;           // ISO 8601 date
  end_date?: string;             // ISO 8601 date
  search?: string;               // Search query
  limit?: number;                // Page size (default: 50, max: 100)
  offset?: number;               // Pagination offset
  sort?: 'created_at' | 'updated_at' | 'message_count';
  order?: 'asc' | 'desc';        // Sort order (default: desc)
}
```

#### **Example Request**

```bash
curl -X GET "https://api.observatory.dev/api/v1/conversations?project_id=123&limit=20&search=authentication" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json"
```

#### **Response**

```typescript
interface ConversationListResponse {
  data: Conversation[];
  pagination: {
    limit: number;
    offset: number;
    total: number;
    has_more: boolean;
  };
  meta: {
    total_conversations: number;
    active_conversations: number;
    projects_count: number;
  };
}

interface Conversation {
  id: string;
  project_id: number;
  session_id: string;
  title?: string;
  status: 'active' | 'ended';
  message_count: number;
  tool_usage_count: number;
  start_time: string;            // ISO 8601
  end_time?: string;             // ISO 8601
  last_activity: string;         // ISO 8601
  preview: string;               // First message preview
  participants: string[];        // User types involved
  tags: string[];
  created_at: string;            // ISO 8601
  updated_at: string;            // ISO 8601
}
```

#### **Example Response**

```json
{
  "data": [
    {
      "id": "conv_1234567890abcdef",
      "project_id": 123,
      "session_id": "session_abc123",
      "title": "Debugging Authentication Issue",
      "status": "ended",
      "message_count": 15,
      "tool_usage_count": 8,
      "start_time": "2024-01-15T10:30:00Z",
      "end_time": "2024-01-15T11:45:00Z",
      "last_activity": "2024-01-15T11:45:00Z",
      "preview": "I'm having trouble with user authentication in my React app...",
      "participants": ["user", "assistant"],
      "tags": ["authentication", "react", "debugging"],
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T11:45:00Z"
    }
  ],
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total": 156,
    "has_more": true
  },
  "meta": {
    "total_conversations": 156,
    "active_conversations": 3,
    "projects_count": 8
  }
}
```

### **Get Conversation Details**

#### **Endpoint**
```
GET /api/v1/conversations/{conversation_id}
```

#### **Query Parameters**

```typescript
interface ConversationDetailParams {
  include_messages?: boolean;    // Include full message list (default: true)
  message_limit?: number;        // Limit messages returned (default: all)
  include_analytics?: boolean;   // Include conversation analytics (default: false)
}
```

#### **Response**

```typescript
interface ConversationDetailResponse {
  conversation: ConversationDetail;
  messages?: Message[];
  analytics?: ConversationAnalytics;
}

interface ConversationDetail extends Conversation {
  project: {
    id: number;
    name: string;
    path: string;
  };
  metrics: {
    duration_seconds: number;
    avg_response_time_ms: number;
    tool_success_rate: number;
    complexity_score: number;
  };
  sharing: {
    is_shared: boolean;
    share_link?: string;
    shared_with: string[];
  };
}

interface Message {
  id: string;
  conversation_id: string;
  timestamp: string;             // ISO 8601
  type: 'user' | 'assistant' | 'system';
  content: string;
  tool_usage?: ToolUsage[];
  parent_id?: string;
  thread_level: number;
  metadata: {
    request_id?: string;
    user_type?: string;
    model_version?: string;
    processing_time_ms?: number;
  };
}

interface ToolUsage {
  tool_id: string;
  tool_name: string;
  input: Record<string, any>;
  output?: string;
  execution_time_ms?: number;
  status: 'pending' | 'success' | 'error' | 'timeout';
  error_message?: string;
}
```

### **Create Conversation**

#### **Endpoint**
```
POST /api/v1/conversations
```

#### **Request Body**

```typescript
interface CreateConversationRequest {
  project_id: number;
  title?: string;
  initial_message?: {
    type: 'user' | 'system';
    content: string;
  };
  tags?: string[];
  metadata?: Record<string, any>;
}
```

#### **Example Request**

```bash
curl -X POST "https://api.observatory.dev/api/v1/conversations" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 123,
    "title": "New Feature Development",
    "initial_message": {
      "type": "user",
      "content": "I want to add a new search feature to my application"
    },
    "tags": ["feature", "search"]
  }'
```

### **Add Message to Conversation**

#### **Endpoint**
```
POST /api/v1/conversations/{conversation_id}/messages
```

#### **Request Body**

```typescript
interface AddMessageRequest {
  type: 'user' | 'assistant' | 'system';
  content: string;
  tool_usage?: ToolUsage[];
  parent_id?: string;
  metadata?: Record<string, any>;
}
```

### **Search Conversations**

#### **Endpoint**
```
POST /api/v1/conversations/search
```

#### **Request Body**

```typescript
interface ConversationSearchRequest {
  query: string;
  filters?: {
    project_ids?: number[];
    date_range?: {
      start: string;               // ISO 8601
      end: string;                 // ISO 8601
    };
    message_types?: Array<'user' | 'assistant' | 'system'>;
    tools_used?: string[];
    has_errors?: boolean;
    min_messages?: number;
    max_messages?: number;
  };
  sort?: {
    field: 'relevance' | 'created_at' | 'message_count';
    order: 'asc' | 'desc';
  };
  limit?: number;
  offset?: number;
}
```

#### **Response**

```typescript
interface ConversationSearchResponse {
  results: ConversationSearchResult[];
  pagination: PaginationInfo;
  aggregations: {
    total_matches: number;
    projects: Array<{ id: number; name: string; count: number }>;
    tools_used: Array<{ name: string; count: number }>;
    date_distribution: Array<{ date: string; count: number }>;
  };
}

interface ConversationSearchResult extends Conversation {
  relevance_score: number;
  matching_messages: Array<{
    id: string;
    content: string;
    highlight: string;             // HTML with highlighted terms
  }>;
}
```

---

## 📁 **Projects API**

### **List Projects**

#### **Endpoint**
```
GET /api/v1/projects
```

#### **Query Parameters**

```typescript
interface ProjectListParams {
  status?: 'active' | 'idle' | 'archived';
  search?: string;
  sort?: 'name' | 'created_at' | 'last_activity' | 'conversation_count';
  order?: 'asc' | 'desc';
  limit?: number;
  offset?: number;
}
```

#### **Response**

```typescript
interface ProjectListResponse {
  data: Project[];
  pagination: PaginationInfo;
}

interface Project {
  id: number;
  name: string;
  description?: string;
  path: string;
  status: 'active' | 'idle' | 'archived';
  conversation_count: number;
  message_count: number;
  last_activity: string;         // ISO 8601
  health_score: number;          // 0-100
  activity_trend: 'increasing' | 'stable' | 'decreasing';
  tags: string[];
  settings: {
    auto_discovery: boolean;
    file_patterns: string[];
    retention_days: number;
  };
  created_at: string;            // ISO 8601
  updated_at: string;            // ISO 8601
}
```

### **Get Project Details**

#### **Endpoint**
```
GET /api/v1/projects/{project_id}
```

#### **Response**

```typescript
interface ProjectDetailResponse {
  project: ProjectDetail;
  statistics: ProjectStatistics;
  recent_activity: RecentActivity[];
}

interface ProjectDetail extends Project {
  team: {
    owner: User;
    members: User[];
    permissions: ProjectPermissions;
  };
  integrations: {
    github?: {
      repository: string;
      branch: string;
    };
    slack?: {
      channel: string;
    };
  };
}

interface ProjectStatistics {
  time_periods: {
    last_24h: PeriodStats;
    last_7d: PeriodStats;
    last_30d: PeriodStats;
  };
  tools: {
    most_used: Array<{ name: string; count: number; success_rate: number }>;
    performance: Array<{ name: string; avg_time_ms: number }>;
  };
  patterns: {
    common_topics: string[];
    peak_hours: number[];
    success_indicators: string[];
  };
}

interface PeriodStats {
  conversations: number;
  messages: number;
  tools_used: number;
  avg_conversation_length: number;
  success_rate: number;
}
```

### **Create Project**

#### **Endpoint**
```
POST /api/v1/projects
```

#### **Request Body**

```typescript
interface CreateProjectRequest {
  name: string;
  description?: string;
  path?: string;                 // File system path to monitor
  settings?: {
    auto_discovery?: boolean;
    file_patterns?: string[];
    retention_days?: number;
  };
  tags?: string[];
}
```

### **Update Project**

#### **Endpoint**
```
PUT /api/v1/projects/{project_id}
```

#### **Request Body**

```typescript
interface UpdateProjectRequest {
  name?: string;
  description?: string;
  status?: 'active' | 'idle' | 'archived';
  settings?: ProjectSettings;
  tags?: string[];
}
```

---

## 📋 **Analytics API**

### **Get Analytics Overview**

#### **Endpoint**
```
GET /api/v1/analytics/overview
```

#### **Query Parameters**

```typescript
interface AnalyticsOverviewParams {
  time_range?: '24h' | '7d' | '30d' | '90d' | 'custom';
  start_date?: string;           // Required if time_range=custom
  end_date?: string;             // Required if time_range=custom
  project_ids?: number[];        // Filter by projects
  include_comparisons?: boolean; // Include period-over-period comparisons
}
```

#### **Response**

```typescript
interface AnalyticsOverviewResponse {
  summary: {
    total_conversations: number;
    total_messages: number;
    total_tools_used: number;
    avg_conversation_duration: number;
    success_rate: number;
  };
  
  trends: {
    conversations_over_time: Array<{ date: string; count: number }>;
    tools_usage_over_time: Array<{ date: string; tools: Record<string, number> }>;
    performance_over_time: Array<{ date: string; avg_response_time: number }>;
  };
  
  top_metrics: {
    most_used_tools: Array<{ name: string; count: number; success_rate: number }>;
    most_active_projects: Array<{ id: number; name: string; activity_score: number }>;
    common_topics: Array<{ topic: string; frequency: number }>;
  };
  
  comparisons?: {
    previous_period: AnalyticsSummary;
    growth_rates: Record<string, number>;
  };
}
```

### **Get User Insights**

#### **Endpoint**
```
GET /api/v1/analytics/insights
```

#### **Response**

```typescript
interface UserInsightsResponse {
  productivity: {
    efficiency_score: number;      // 0-100
    improvement_trend: number;     // Percentage change
    time_saved_hours: number;
    problems_solved_reuse: number;
  };
  
  patterns: {
    most_productive_hours: number[];
    preferred_tools: string[];
    common_workflows: Array<{
      pattern: string;
      frequency: number;
      success_rate: number;
    }>;
  };
  
  recommendations: Array<{
    type: 'tool_usage' | 'workflow' | 'learning';
    title: string;
    description: string;
    potential_impact: 'low' | 'medium' | 'high';
    action_items: string[];
  }>;
  
  learning_progress: {
    skills_developed: string[];
    knowledge_areas: Array<{
      area: string;
      proficiency: number;         // 0-100
      growth_rate: number;
    }>;
  };
}
```

### **Export Analytics Data**

#### **Endpoint**
```
POST /api/v1/analytics/export
```

#### **Request Body**

```typescript
interface AnalyticsExportRequest {
  format: 'csv' | 'json' | 'xlsx';
  data_types: Array<'conversations' | 'messages' | 'tools' | 'analytics'>;
  filters: {
    time_range: {
      start: string;               // ISO 8601
      end: string;                 // ISO 8601
    };
    project_ids?: number[];
  };
  options?: {
    include_content?: boolean;     // Include message content
    anonymize_data?: boolean;      // Remove PII
    compression?: 'none' | 'gzip' | 'zip';
  };
}
```

#### **Response**

```typescript
interface AnalyticsExportResponse {
  export_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  download_url?: string;         // Available when status=completed
  estimated_completion?: string; // ISO 8601
  file_size_bytes?: number;
  expires_at: string;            // ISO 8601
}
```

---

## 👥 **Teams API**

### **List Teams**

#### **Endpoint**
```
GET /api/v1/teams
```

#### **Response**

```typescript
interface TeamsListResponse {
  teams: Team[];
}

interface Team {
  id: string;
  name: string;
  description?: string;
  member_count: number;
  role: 'owner' | 'admin' | 'member' | 'viewer';
  subscription: {
    plan: 'free' | 'team' | 'enterprise';
    status: 'active' | 'cancelled' | 'expired';
  };
  created_at: string;            // ISO 8601
}
```

### **Get Team Details**

#### **Endpoint**
```
GET /api/v1/teams/{team_id}
```

#### **Response**

```typescript
interface TeamDetailResponse {
  team: TeamDetail;
  members: TeamMember[];
  projects: TeamProject[];
  analytics: TeamAnalytics;
}

interface TeamDetail extends Team {
  settings: {
    sharing_enabled: boolean;
    analytics_retention_days: number;
    integrations: Record<string, any>;
  };
  billing: {
    plan: string;
    seats_used: number;
    seats_limit: number;
    next_billing_date: string;
  };
}

interface TeamMember {
  id: string;
  email: string;
  name: string;
  role: 'owner' | 'admin' | 'member' | 'viewer';
  status: 'active' | 'invited' | 'suspended';
  last_active: string;           // ISO 8601
  joined_at: string;             // ISO 8601
}

interface TeamProject {
  id: number;
  name: string;
  member_count: number;
  conversation_count: number;
  permissions: ProjectPermissions;
}
```

### **Team Analytics**

#### **Endpoint**
```
GET /api/v1/teams/{team_id}/analytics
```

#### **Response**

```typescript
interface TeamAnalyticsResponse {
  overview: {
    total_conversations: number;
    total_collaborations: number;
    knowledge_sharing_score: number;
    productivity_improvement: number;
  };
  
  collaboration: {
    shared_conversations: number;
    comments_added: number;
    knowledge_reuse_rate: number;
    cross_project_learning: number;
  };
  
  member_insights: Array<{
    member_id: string;
    productivity_score: number;
    collaboration_score: number;
    learning_velocity: number;
    mentoring_impact: number;
  }>;
  
  best_practices: Array<{
    pattern: string;
    adoption_rate: number;
    impact_score: number;
    examples: string[];
  }>;
}
```

---

## 🔄 **WebSocket API**

### **Connection & Authentication**

#### **WebSocket Connection**

```typescript
// Connect to WebSocket
const ws = new WebSocket('wss://api.observatory.dev/ws/conversations', {
  headers: {
    'Authorization': 'Bearer <access_token>'
  }
});

// Handle connection events
ws.on('open', () => {
  console.log('Connected to Observatory WebSocket');
  
  // Subscribe to specific events
  ws.send(JSON.stringify({
    type: 'subscribe',
    payload: {
      events: ['conversation_started', 'message_added', 'conversation_ended'],
      filters: {
        project_ids: [123, 456],
        user_id: 'user_789'
      }
    }
  }));
});

ws.on('message', (data) => {
  const event = JSON.parse(data.toString());
  handleRealtimeEvent(event);
});
```

### **Real-Time Events**

#### **Event Types**

```typescript
interface WebSocketEvent {
  type: string;
  payload: any;
  timestamp: string;             // ISO 8601
  event_id: string;
}

// Conversation Events
interface ConversationStartedEvent extends WebSocketEvent {
  type: 'conversation_started';
  payload: {
    conversation_id: string;
    project_id: number;
    session_id: string;
    initial_message?: Message;
  };
}

interface MessageAddedEvent extends WebSocketEvent {
  type: 'message_added';
  payload: {
    conversation_id: string;
    message: Message;
    project: {
      id: number;
      name: string;
    };
  };
}

interface ConversationEndedEvent extends WebSocketEvent {
  type: 'conversation_ended';
  payload: {
    conversation_id: string;
    duration_seconds: number;
    message_count: number;
    summary?: string;
  };
}

// System Events
interface SystemHealthEvent extends WebSocketEvent {
  type: 'system_health';
  payload: {
    status: 'healthy' | 'degraded' | 'down';
    metrics: {
      cpu_usage: number;
      memory_usage: number;
      active_connections: number;
    };
  };
}
```

#### **Event Subscription Management**

```typescript
// Subscribe to events
interface SubscribeMessage {
  type: 'subscribe';
  payload: {
    events: string[];              // Event types to subscribe to
    filters?: {
      project_ids?: number[];
      user_id?: string;
      conversation_ids?: string[];
    };
  };
}

// Unsubscribe from events
interface UnsubscribeMessage {
  type: 'unsubscribe';
  payload: {
    events: string[];
    filters?: Record<string, any>;
  };
}

// Get subscription status
interface GetSubscriptionsMessage {
  type: 'get_subscriptions';
}

interface SubscriptionStatusResponse {
  type: 'subscription_status';
  payload: {
    active_subscriptions: Array<{
      events: string[];
      filters: Record<string, any>;
      created_at: string;
    }>;
  };
}
```

---

## 🛠️ **Admin API**

### **System Health**

#### **Endpoint**
```
GET /api/v1/admin/health
```

#### **Response**

```typescript
interface SystemHealthResponse {
  status: 'healthy' | 'degraded' | 'down';
  timestamp: string;             // ISO 8601
  version: string;
  
  services: {
    database: ServiceHealth;
    file_monitor: ServiceHealth;
    websocket: ServiceHealth;
    authentication: ServiceHealth;
  };
  
  metrics: {
    uptime_seconds: number;
    cpu_usage_percent: number;
    memory_usage_percent: number;
    disk_usage_percent: number;
    active_connections: number;
    requests_per_minute: number;
  };
  
  recent_errors: Array<{
    timestamp: string;
    level: 'warning' | 'error' | 'critical';
    message: string;
    count: number;
  }>;
}

interface ServiceHealth {
  status: 'healthy' | 'degraded' | 'down';
  response_time_ms: number;
  last_check: string;            // ISO 8601
  error_rate: number;
}
```

### **Usage Statistics**

#### **Endpoint**
```
GET /api/v1/admin/usage
```

#### **Response**

```typescript
interface UsageStatisticsResponse {
  users: {
    total_users: number;
    active_users_24h: number;
    active_users_7d: number;
    active_users_30d: number;
    new_users_7d: number;
  };
  
  conversations: {
    total_conversations: number;
    conversations_24h: number;
    avg_messages_per_conversation: number;
    avg_conversation_duration_minutes: number;
  };
  
  performance: {
    avg_response_time_ms: number;
    error_rate_percent: number;
    file_processing_rate: number;
    websocket_connections: number;
  };
  
  storage: {
    database_size_mb: number;
    file_storage_mb: number;
    backup_size_mb: number;
    growth_rate_mb_per_day: number;
  };
}
```

---

## 📚 **Rate Limiting**

### **Rate Limit Rules**

```typescript
interface RateLimits {
  authenticated: {
    requests_per_minute: 1000;
    requests_per_hour: 10000;
    requests_per_day: 100000;
  };
  
  unauthenticated: {
    requests_per_minute: 60;
    requests_per_hour: 1000;
    requests_per_day: 5000;
  };
  
  websocket: {
    connections_per_user: 10;
    messages_per_minute: 1000;
  };
  
  upload: {
    files_per_hour: 100;
    max_file_size_mb: 50;
  };
}
```

### **Rate Limit Headers**

```typescript
// Response headers for rate limiting
interface RateLimitHeaders {
  'X-RateLimit-Limit': string;          // Request limit per window
  'X-RateLimit-Remaining': string;      // Requests remaining in window
  'X-RateLimit-Reset': string;          // Unix timestamp when limit resets
  'X-RateLimit-Window': string;         // Window duration in seconds
}

// Example response headers
{
  'X-RateLimit-Limit': '1000',
  'X-RateLimit-Remaining': '987',
  'X-RateLimit-Reset': '1640995200',
  'X-RateLimit-Window': '60'
}
```

### **Rate Limit Exceeded Response**

```typescript
// HTTP 429 Too Many Requests
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 60 seconds.",
    "retry_after": 60,
    "limit": 1000,
    "window": "1 minute"
  }
}
```

---

## ⚠️ **Error Handling**

### **Error Response Format**

```typescript
interface ErrorResponse {
  error: {
    code: string;                  // Machine-readable error code
    message: string;               // Human-readable error message
    details?: any;                 // Additional error details
    request_id: string;            // Unique request identifier
    timestamp: string;             // ISO 8601
  };
}
```

### **HTTP Status Codes**

```typescript
interface HTTPStatusCodes {
  200: 'OK - Request successful';
  201: 'Created - Resource created successfully';
  204: 'No Content - Request successful, no content returned';
  
  400: 'Bad Request - Invalid request format or parameters';
  401: 'Unauthorized - Authentication required or invalid';
  403: 'Forbidden - Access denied for this resource';
  404: 'Not Found - Resource not found';
  409: 'Conflict - Resource conflict (e.g., duplicate)';
  422: 'Unprocessable Entity - Valid format but invalid data';
  429: 'Too Many Requests - Rate limit exceeded';
  
  500: 'Internal Server Error - Server error occurred';
  502: 'Bad Gateway - Upstream service error';
  503: 'Service Unavailable - Service temporarily unavailable';
  504: 'Gateway Timeout - Upstream service timeout';
}
```

### **Common Error Codes**

```typescript
interface CommonErrorCodes {
  // Authentication errors
  'AUTH_TOKEN_INVALID': 'Invalid or expired authentication token';
  'AUTH_TOKEN_MISSING': 'Authentication token required';
  'AUTH_INSUFFICIENT_PERMISSIONS': 'Insufficient permissions for this operation';
  
  // Validation errors
  'VALIDATION_FAILED': 'Request validation failed';
  'INVALID_PARAMETER': 'Invalid parameter value';
  'MISSING_REQUIRED_FIELD': 'Required field missing';
  
  // Resource errors
  'RESOURCE_NOT_FOUND': 'Requested resource not found';
  'RESOURCE_ALREADY_EXISTS': 'Resource already exists';
  'RESOURCE_LIMIT_EXCEEDED': 'Resource limit exceeded';
  
  // System errors
  'INTERNAL_ERROR': 'Internal system error';
  'SERVICE_UNAVAILABLE': 'Service temporarily unavailable';
  'RATE_LIMIT_EXCEEDED': 'Rate limit exceeded';
}
```

### **Example Error Responses**

```json
// 400 Bad Request
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Request validation failed",
    "details": {
      "field_errors": {
        "project_id": "Invalid project ID format",
        "limit": "Must be between 1 and 100"
      }
    },
    "request_id": "req_1234567890abcdef",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}

// 404 Not Found
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Conversation not found",
    "details": {
      "resource_type": "conversation",
      "resource_id": "conv_nonexistent"
    },
    "request_id": "req_abcdef1234567890",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

---

## 📜 **SDK Examples**

### **JavaScript/TypeScript SDK**

```typescript
// Installation
// npm install @claude-observatory/sdk

import { ObservatoryClient } from '@claude-observatory/sdk';

// Initialize client
const client = new ObservatoryClient({
  apiKey: 'your_api_key',
  baseUrl: 'https://api.observatory.dev'
});

// List conversations
const conversations = await client.conversations.list({
  project_id: 123,
  limit: 20
});

// Get conversation details
const conversation = await client.conversations.get('conv_123');

// Search conversations
const searchResults = await client.conversations.search({
  query: 'authentication error',
  filters: {
    project_ids: [123, 456],
    date_range: {
      start: '2024-01-01T00:00:00Z',
      end: '2024-01-31T23:59:59Z'
    }
  }
});

// Real-time subscriptions
const subscription = client.realtime.subscribe({
  events: ['message_added', 'conversation_ended'],
  filters: { project_ids: [123] }
});

subscription.on('message_added', (event) => {
  console.log('New message:', event.payload.message);
});
```

### **Python SDK**

```python
# Installation
# pip install claude-observatory-sdk

from claude_observatory import ObservatoryClient

# Initialize client
client = ObservatoryClient(
    api_key='your_api_key',
    base_url='https://api.observatory.dev'
)

# List conversations
conversations = client.conversations.list(
    project_id=123,
    limit=20
)

# Get analytics
analytics = client.analytics.overview(
    time_range='30d',
    project_ids=[123, 456]
)

# Export data
export_job = client.analytics.export(
    format='csv',
    data_types=['conversations', 'analytics'],
    filters={
        'time_range': {
            'start': '2024-01-01T00:00:00Z',
            'end': '2024-01-31T23:59:59Z'
        }
    }
)

# Check export status
while export_job.status != 'completed':
    time.sleep(10)
    export_job.refresh()

# Download export
export_job.download('analytics_export.csv')
```

### **cURL Examples**

```bash
# Set your API key
API_KEY="your_api_key_here"
BASE_URL="https://api.observatory.dev/api/v1"

# List conversations
curl -X GET "$BASE_URL/conversations?limit=10" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json"

# Search conversations
curl -X POST "$BASE_URL/conversations/search" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "authentication",
    "filters": {
      "project_ids": [123],
      "date_range": {
        "start": "2024-01-01T00:00:00Z",
        "end": "2024-01-31T23:59:59Z"
      }
    },
    "limit": 20
  }'

# Get analytics overview
curl -X GET "$BASE_URL/analytics/overview?time_range=7d" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json"

# Create a new project
curl -X POST "$BASE_URL/projects" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My New Project",
    "description": "Project for testing new features",
    "settings": {
      "auto_discovery": true,
      "retention_days": 90
    }
  }'
```

---

*This comprehensive API documentation provides everything needed to integrate with Claude Code Observatory, from basic CRUD operations to advanced analytics and real-time features.*