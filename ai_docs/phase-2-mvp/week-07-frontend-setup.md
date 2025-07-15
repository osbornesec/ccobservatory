# Week 7: Vue 3 Frontend Application Setup

## Overview
Establish the Vue 3 frontend application with Vite build tooling and Tailwind CSS styling framework. This week focuses on project structure, component architecture, routing, state management, and integration with the backend API and WebSocket services.

## Team Assignments
- **Frontend Lead**: Vue 3 architecture, component design, routing setup
- **Full-Stack Developer**: API integration, state management, authentication
- **UI/UX Developer**: Tailwind CSS configuration, design system, responsive layouts

## Daily Schedule

### Monday: Project Foundation & Build Setup
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Vite project initialization and configuration
- **10:30-12:00**: Vue 3 application structure and TypeScript setup

#### Afternoon (4 hours)
- **13:00-15:00**: Tailwind CSS integration and design system foundation
- **15:00-17:00**: Development environment configuration and tooling

### Tuesday: Routing & Layout Architecture
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Vue Router 4 setup and route configuration
- **10:30-12:00**: Layout components and navigation structure

#### Afternoon (4 hours)
- **13:00-15:00**: Protected routes and authentication guards
- **15:00-17:00**: Responsive layout implementation

### Wednesday: State Management & API Integration
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Pinia store setup and state architecture
- **10:30-12:00**: API service layer and HTTP client configuration

#### Afternoon (4 hours)
- **13:00-15:00**: Authentication store and JWT handling
- **15:00-17:00**: Error handling and loading states

### Thursday: Component Library & Design System
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Base component library creation
- **10:30-12:00**: Form components and validation setup

#### Afternoon (4 hours)
- **13:00-15:00**: Data display components (tables, cards, lists)
- **15:00-17:00**: Modal and notification systems

### Friday: WebSocket Integration & Testing
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: WebSocket service integration
- **10:30-12:00**: Real-time state updates and event handling

#### Afternoon (4 hours)
- **13:00-15:00**: Component testing setup (Vitest + Vue Test Utils)
- **15:00-17:00**: Integration testing and end-to-end testing foundation

## Technical Implementation Details

### Vue 3 + TypeScript Project Initialization

The Claude Code Observatory frontend is built with Vue 3, TypeScript, and Vite for optimal development experience and performance. This setup provides hot module replacement (HMR), excellent TypeScript support, and modern build tooling.

#### Project Creation and Setup

Use the official Vue scaffolding tool with TypeScript support:

```bash
# Create new Vue 3 project with TypeScript
npm create vue@latest claude-code-observatory-frontend

# Select the following options:
# ✅ TypeScript
# ✅ Router
# ✅ Pinia
# ✅ Vitest
# ✅ ESLint
# ✅ Prettier
# ✅ Playwright (E2E testing)

cd claude-code-observatory-frontend
npm install
```

#### Package.json Configuration

```json
{
  "name": "claude-code-observatory-frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "test:unit": "vitest",
    "test:e2e": "playwright test",
    "test:e2e:dev": "playwright test --ui",
    "test:coverage": "vitest run --coverage",
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix --ignore-path .gitignore",
    "format": "prettier --write src/",
    "type-check": "vue-tsc --noEmit -p tsconfig.vitest.json --composite false",
    "analyze": "npm run build && npx rollup-plugin-visualizer dist/stats.html --open"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "axios": "^1.6.2",
    "@headlessui/vue": "^1.7.16",
    "@heroicons/vue": "^2.0.18",
    "@vueuse/core": "^10.5.0",
    "@vee-validate/zod": "^4.12.4",
    "vee-validate": "^4.12.4",
    "zod": "^3.22.4",
    "date-fns": "^2.30.0",
    "lodash-es": "^4.17.21",
    "chart.js": "^4.4.0",
    "vue-chartjs": "^5.2.0",
    "socket.io-client": "^4.7.4"
  },
  "devDependencies": {
    "@types/node": "^20.9.0",
    "@types/lodash-es": "^4.17.12",
    "@typescript-eslint/eslint-plugin": "^6.12.0",
    "@typescript-eslint/parser": "^6.12.0",
    "@vitejs/plugin-vue": "^4.5.0",
    "@vue/eslint-config-prettier": "^8.0.0",
    "@vue/eslint-config-typescript": "^12.0.0",
    "@vue/test-utils": "^2.4.1",
    "@vue/tsconfig": "^0.4.0",
    "autoprefixer": "^10.4.16",
    "eslint": "^8.54.0",
    "eslint-plugin-vue": "^9.18.1",
    "jsdom": "^22.1.0",
    "npm-run-all": "^4.1.5",
    "playwright": "^1.40.0",
    "postcss": "^8.4.31",
    "prettier": "^3.1.0",
    "rollup-plugin-visualizer": "^5.9.2",
    "tailwindcss": "^3.3.5",
    "typescript": "~5.2.0",
    "vite": "^5.0.0",
    "vite-plugin-pwa": "^0.17.4",
    "vitest": "^0.34.6",
    "vue-tsc": "^1.8.22"
  }
}
```

#### TypeScript Configuration

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "allowImportingTsExtensions": true,
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "paths": {
      "@/*": ["./src/*"],
      "@components/*": ["./src/components/*"],
      "@views/*": ["./src/views/*"],
      "@stores/*": ["./src/stores/*"],
      "@services/*": ["./src/services/*"],
      "@types/*": ["./src/types/*"],
      "@utils/*": ["./src/utils/*"],
      "@assets/*": ["./src/assets/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
  "exclude": ["node_modules", "dist"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

#### Environment Types Setup

```typescript
// src/vite-env.d.ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_WS_URL: string
  readonly VITE_APP_TITLE: string
  readonly VITE_APP_VERSION: string
  readonly VITE_ENVIRONMENT: 'development' | 'staging' | 'production'
  readonly VITE_ENABLE_ANALYTICS: boolean
  readonly VITE_SENTRY_DSN?: string
  readonly VITE_LOG_LEVEL: 'debug' | 'info' | 'warn' | 'error'
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

#### Environment Configuration Files

```bash
# .env
VITE_APP_TITLE=Claude Code Observatory
VITE_APP_VERSION=1.0.0
VITE_LOG_LEVEL=info
VITE_ENABLE_ANALYTICS=false
```

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:3001/api
VITE_WS_URL=ws://localhost:3002/ws
VITE_ENVIRONMENT=development
VITE_LOG_LEVEL=debug
```

```bash
# .env.production
VITE_API_BASE_URL=/api
VITE_WS_URL=wss://api.example.com/ws
VITE_ENVIRONMENT=production
VITE_LOG_LEVEL=error
```

### Vue 3 Composition API Patterns

#### Component Structure with TypeScript

```vue
<!-- src/components/ConversationCard.vue -->
<template>
  <div class="conversation-card" :class="cardClasses">
    <div class="conversation-header">
      <h3 class="conversation-title">{{ conversation.title }}</h3>
      <span class="conversation-status" :class="statusClasses">
        {{ conversation.status }}
      </span>
    </div>
    
    <div class="conversation-meta">
      <time :datetime="conversation.createdAt.toISOString()">
        {{ formatDate(conversation.createdAt) }}
      </time>
      <span class="message-count">
        {{ conversation.messageCount }} messages
      </span>
    </div>
    
    <div class="conversation-tools">
      <span v-for="tool in conversation.tools" 
            :key="tool.id" 
            class="tool-badge"
            :title="tool.description">
        {{ tool.name }}
      </span>
    </div>
    
    <div class="conversation-actions">
      <button 
        @click="handleView"
        class="btn btn-primary"
        :disabled="loading">
        View Details
      </button>
      <button 
        @click="handleExport"
        class="btn btn-secondary"
        :disabled="loading">
        Export
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useConversationStore } from '@/stores/conversation'
import { formatDate } from '@/utils/date'
import type { Conversation } from '@/types/conversation'

// Props with TypeScript validation
interface Props {
  conversation: Conversation
  variant?: 'default' | 'compact' | 'detailed'
  interactive?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  interactive: true
})

// Emits with TypeScript
const emit = defineEmits<{
  view: [conversation: Conversation]
  export: [conversation: Conversation]
  favorite: [conversation: Conversation]
}>()

// Reactive state
const loading = ref(false)
const router = useRouter()
const conversationStore = useConversationStore()

// Computed properties with type inference
const cardClasses = computed(() => ({
  'conversation-card--compact': props.variant === 'compact',
  'conversation-card--detailed': props.variant === 'detailed',
  'conversation-card--interactive': props.interactive,
  'conversation-card--loading': loading.value
}))

const statusClasses = computed(() => ({
  'status--active': props.conversation.status === 'active',
  'status--completed': props.conversation.status === 'completed',
  'status--error': props.conversation.status === 'error'
}))

// Methods with proper TypeScript signatures
async function handleView(): Promise<void> {
  if (loading.value) return
  
  loading.value = true
  try {
    await conversationStore.fetchConversationDetails(props.conversation.id)
    emit('view', props.conversation)
    
    if (props.interactive) {
      await router.push(`/conversations/${props.conversation.id}`)
    }
  } catch (error) {
    console.error('Failed to load conversation:', error)
  } finally {
    loading.value = false
  }
}

async function handleExport(): Promise<void> {
  if (loading.value) return
  
  loading.value = true
  try {
    await conversationStore.exportConversation(props.conversation.id)
    emit('export', props.conversation)
  } catch (error) {
    console.error('Failed to export conversation:', error)
  } finally {
    loading.value = false
  }
}

// Lifecycle hooks
onMounted(() => {
  console.log('ConversationCard mounted for:', props.conversation.id)
})

onUnmounted(() => {
  console.log('ConversationCard unmounted for:', props.conversation.id)
})
</script>

<style scoped>
.conversation-card {
  @apply bg-white rounded-lg shadow-md p-6 transition-all duration-200;
  @apply border border-gray-200 hover:shadow-lg;
}

.conversation-card--compact {
  @apply p-4;
}

.conversation-card--detailed {
  @apply p-8 max-w-2xl;
}

.conversation-card--interactive {
  @apply cursor-pointer hover:border-primary-300;
}

.conversation-card--loading {
  @apply opacity-50 pointer-events-none;
}

.conversation-header {
  @apply flex items-center justify-between mb-4;
}

.conversation-title {
  @apply text-lg font-semibold text-gray-900 truncate;
}

.conversation-status {
  @apply px-2 py-1 rounded-full text-xs font-medium;
}

.status--active {
  @apply bg-green-100 text-green-800;
}

.status--completed {
  @apply bg-blue-100 text-blue-800;
}

.status--error {
  @apply bg-red-100 text-red-800;
}

.conversation-meta {
  @apply flex items-center gap-4 text-sm text-gray-600 mb-3;
}

.conversation-tools {
  @apply flex flex-wrap gap-2 mb-4;
}

.tool-badge {
  @apply px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs;
}

.conversation-actions {
  @apply flex gap-2 justify-end;
}

.btn {
  @apply px-4 py-2 rounded-md font-medium transition-colors;
  @apply focus:outline-none focus:ring-2 focus:ring-offset-2;
}

.btn-primary {
  @apply bg-primary-600 text-white hover:bg-primary-700;
  @apply focus:ring-primary-500;
}

.btn-secondary {
  @apply bg-gray-200 text-gray-900 hover:bg-gray-300;
  @apply focus:ring-gray-500;
}

.btn:disabled {
  @apply opacity-50 cursor-not-allowed;
}
</style>
```

#### Advanced Composition API Patterns

```typescript
// src/composables/useConversationPolling.ts
import { ref, computed, onMounted, onUnmounted } from 'vue'
import type { Ref } from 'vue'

interface UseConversationPollingOptions {
  interval?: number
  immediate?: boolean
  maxRetries?: number
}

interface ConversationPollingState {
  isPolling: Ref<boolean>
  error: Ref<string | null>
  retryCount: Ref<number>
  start: () => void
  stop: () => void
  restart: () => void
}

export function useConversationPolling(
  fetchFn: () => Promise<void>,
  options: UseConversationPollingOptions = {}
): ConversationPollingState {
  const {
    interval = 5000,
    immediate = true,
    maxRetries = 3
  } = options
  
  const isPolling = ref(false)
  const error = ref<string | null>(null)
  const retryCount = ref(0)
  let pollingTimer: NodeJS.Timer | null = null
  
  const start = () => {
    if (isPolling.value) return
    
    isPolling.value = true
    error.value = null
    poll()
  }
  
  const stop = () => {
    if (pollingTimer) {
      clearTimeout(pollingTimer)
      pollingTimer = null
    }
    isPolling.value = false
  }
  
  const restart = () => {
    stop()
    retryCount.value = 0
    start()
  }
  
  const poll = async () => {
    try {
      await fetchFn()
      retryCount.value = 0
      error.value = null
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      retryCount.value++
      
      if (retryCount.value >= maxRetries) {
        console.error('Max retries reached, stopping polling')
        stop()
        return
      }
    }
    
    if (isPolling.value) {
      pollingTimer = setTimeout(poll, interval)
    }
  }
  
  onMounted(() => {
    if (immediate) {
      start()
    }
  })
  
  onUnmounted(() => {
    stop()
  })
  
  return {
    isPolling,
    error,
    retryCount,
    start,
    stop,
    restart
  }
}
```

### TypeScript Type Definitions

```typescript
// src/types/conversation.ts
export interface Conversation {
  id: string
  title: string
  status: ConversationStatus
  createdAt: Date
  updatedAt: Date
  messageCount: number
  tools: Tool[]
  metadata: ConversationMetadata
  participants: Participant[]
}

export type ConversationStatus = 'active' | 'completed' | 'error' | 'archived'

export interface Tool {
  id: string
  name: string
  description: string
  category: ToolCategory
  usage: ToolUsage
}

export type ToolCategory = 'file' | 'web' | 'system' | 'api' | 'database'

export interface ToolUsage {
  count: number
  lastUsed: Date
  averageExecutionTime: number
}

export interface ConversationMetadata {
  projectPath: string
  environment: string
  totalTokens: number
  cost: number
  tags: string[]
}

export interface Participant {
  id: string
  name: string
  role: 'user' | 'assistant' | 'system'
  avatar?: string
}

export interface Message {
  id: string
  conversationId: string
  content: string
  type: MessageType
  timestamp: Date
  participant: Participant
  metadata: MessageMetadata
}

export type MessageType = 'text' | 'code' | 'tool_call' | 'tool_response' | 'error'

export interface MessageMetadata {
  tokens: number
  processingTime: number
  toolCalls?: ToolCall[]
}

export interface ToolCall {
  id: string
  tool: string
  parameters: Record<string, any>
  result: any
  success: boolean
  executionTime: number
}

// API Response types
export interface ApiResponse<T> {
  data: T
  success: boolean
  message?: string
  pagination?: PaginationInfo
}

export interface PaginationInfo {
  page: number
  limit: number
  total: number
  totalPages: number
  hasNext: boolean
  hasPrev: boolean
}

// Store types
export interface ConversationFilters {
  status?: ConversationStatus[]
  dateRange?: {
    start: Date
    end: Date
  }
  tools?: string[]
  participants?: string[]
  tags?: string[]
  search?: string
}

export interface ConversationSortOptions {
  field: 'createdAt' | 'updatedAt' | 'messageCount' | 'title'
  direction: 'asc' | 'desc'
}
```

### Pinia Store Architecture with TypeScript

```typescript
// src/stores/conversation.ts
import { defineStore } from 'pinia'
import { ref, computed, reactive } from 'vue'
import { conversationService } from '@/services/conversation'
import type { 
  Conversation, 
  ConversationFilters,
  ConversationSortOptions,
  ApiResponse,
  PaginationInfo
} from '@/types/conversation'

export const useConversationStore = defineStore('conversation', () => {
  // State
  const conversations = ref<Conversation[]>([])
  const currentConversation = ref<Conversation | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const filters = reactive<ConversationFilters>({})
  const sortOptions = reactive<ConversationSortOptions>({
    field: 'createdAt',
    direction: 'desc'
  })
  const pagination = ref<PaginationInfo>({
    page: 1,
    limit: 20,
    total: 0,
    totalPages: 0,
    hasNext: false,
    hasPrev: false
  })

  // Getters
  const filteredConversations = computed(() => {
    let result = [...conversations.value]
    
    // Apply status filter
    if (filters.status?.length) {
      result = result.filter(conv => 
        filters.status!.includes(conv.status)
      )
    }
    
    // Apply search filter
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase()
      result = result.filter(conv =>
        conv.title.toLowerCase().includes(searchTerm) ||
        conv.tools.some(tool => 
          tool.name.toLowerCase().includes(searchTerm)
        )
      )
    }
    
    // Apply date range filter
    if (filters.dateRange) {
      result = result.filter(conv => {
        const convDate = new Date(conv.createdAt)
        return convDate >= filters.dateRange!.start && 
               convDate <= filters.dateRange!.end
      })
    }
    
    // Apply sorting
    result.sort((a, b) => {
      const field = sortOptions.field
      const direction = sortOptions.direction
      
      let aValue = a[field]
      let bValue = b[field]
      
      if (field === 'createdAt' || field === 'updatedAt') {
        aValue = new Date(aValue).getTime()
        bValue = new Date(bValue).getTime()
      }
      
      if (direction === 'asc') {
        return aValue > bValue ? 1 : -1
      } else {
        return aValue < bValue ? 1 : -1
      }
    })
    
    return result
  })

  const conversationStats = computed(() => {
    const stats = {
      total: conversations.value.length,
      active: 0,
      completed: 0,
      error: 0,
      archived: 0,
      totalMessages: 0,
      totalTokens: 0,
      averageTokens: 0
    }
    
    conversations.value.forEach(conv => {
      stats[conv.status]++
      stats.totalMessages += conv.messageCount
      stats.totalTokens += conv.metadata.totalTokens
    })
    
    stats.averageTokens = stats.total > 0 
      ? Math.round(stats.totalTokens / stats.total)
      : 0
    
    return stats
  })

  const isFiltered = computed(() => {
    return !!(
      filters.status?.length ||
      filters.search ||
      filters.dateRange ||
      filters.tools?.length ||
      filters.participants?.length ||
      filters.tags?.length
    )
  })

  // Actions
  async function fetchConversations(page: number = 1): Promise<void> {
    isLoading.value = true
    error.value = null
    
    try {
      const response: ApiResponse<Conversation[]> = await conversationService.getConversations({
        page,
        limit: pagination.value.limit,
        filters: filters,
        sort: sortOptions
      })
      
      if (response.success) {
        conversations.value = response.data
        if (response.pagination) {
          pagination.value = response.pagination
        }
      } else {
        throw new Error(response.message || 'Failed to fetch conversations')
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching conversations:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchConversationDetails(id: string): Promise<Conversation | null> {
    isLoading.value = true
    error.value = null
    
    try {
      const response: ApiResponse<Conversation> = await conversationService.getConversationById(id)
      
      if (response.success) {
        currentConversation.value = response.data
        
        // Update the conversation in the list if it exists
        const index = conversations.value.findIndex(conv => conv.id === id)
        if (index !== -1) {
          conversations.value[index] = response.data
        }
        
        return response.data
      } else {
        throw new Error(response.message || 'Failed to fetch conversation details')
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching conversation details:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  async function exportConversation(id: string, format: 'json' | 'csv' | 'markdown' = 'json'): Promise<void> {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await conversationService.exportConversation(id, format)
      
      if (response.success) {
        // Trigger download
        const blob = new Blob([response.data], { 
          type: format === 'json' ? 'application/json' : 'text/plain' 
        })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `conversation-${id}.${format}`
        a.click()
        URL.revokeObjectURL(url)
      } else {
        throw new Error(response.message || 'Failed to export conversation')
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error exporting conversation:', err)
    } finally {
      isLoading.value = false
    }
  }

  function updateFilters(newFilters: Partial<ConversationFilters>): void {
    Object.assign(filters, newFilters)
  }

  function updateSortOptions(newSort: Partial<ConversationSortOptions>): void {
    Object.assign(sortOptions, newSort)
  }

  function clearFilters(): void {
    Object.keys(filters).forEach(key => {
      delete filters[key as keyof ConversationFilters]
    })
  }

  function setCurrentConversation(conversation: Conversation | null): void {
    currentConversation.value = conversation
  }

  function clearError(): void {
    error.value = null
  }

  // Real-time updates
  function handleConversationUpdate(updatedConversation: Conversation): void {
    const index = conversations.value.findIndex(conv => conv.id === updatedConversation.id)
    
    if (index !== -1) {
      conversations.value[index] = updatedConversation
    } else {
      conversations.value.unshift(updatedConversation)
    }
    
    // Update current conversation if it's the same
    if (currentConversation.value?.id === updatedConversation.id) {
      currentConversation.value = updatedConversation
    }
  }

  function handleConversationDelete(conversationId: string): void {
    const index = conversations.value.findIndex(conv => conv.id === conversationId)
    
    if (index !== -1) {
      conversations.value.splice(index, 1)
    }
    
    // Clear current conversation if it's the deleted one
    if (currentConversation.value?.id === conversationId) {
      currentConversation.value = null
    }
  }

  return {
    // State
    conversations: readonly(conversations),
    currentConversation: readonly(currentConversation),
    isLoading: readonly(isLoading),
    error: readonly(error),
    filters: readonly(filters),
    sortOptions: readonly(sortOptions),
    pagination: readonly(pagination),
    
    // Getters
    filteredConversations,
    conversationStats,
    isFiltered,
    
    // Actions
    fetchConversations,
    fetchConversationDetails,
    exportConversation,
    updateFilters,
    updateSortOptions,
    clearFilters,
    setCurrentConversation,
    clearError,
    handleConversationUpdate,
    handleConversationDelete
  }
})
```

### Component Architecture and Organization

```
src/
├── components/
│   ├── base/               # Reusable UI components
│   │   ├── BaseButton.vue
│   │   ├── BaseInput.vue
│   │   ├── BaseModal.vue
│   │   ├── BaseTable.vue
│   │   └── index.ts
│   ├── forms/              # Form-specific components
│   │   ├── SearchForm.vue
│   │   ├── FilterForm.vue
│   │   └── ConversationForm.vue
│   ├── layout/             # Layout components
│   │   ├── AppHeader.vue
│   │   ├── AppSidebar.vue
│   │   ├── AppLayout.vue
│   │   └── PageHeader.vue
│   ├── conversation/       # Conversation-specific components
│   │   ├── ConversationCard.vue
│   │   ├── ConversationList.vue
│   │   ├── ConversationDetail.vue
│   │   ├── MessageBubble.vue
│   │   └── ToolUsageChart.vue
│   ├── analytics/          # Analytics components
│   │   ├── StatsCard.vue
│   │   ├── UsageChart.vue
│   │   └── PerformanceMetrics.vue
│   └── common/             # Common utility components
│       ├── LoadingSpinner.vue
│       ├── ErrorBoundary.vue
│       └── EmptyState.vue
```

### Vite Configuration
```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss()
  ],
  
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@views': resolve(__dirname, 'src/views'),
      '@stores': resolve(__dirname, 'src/stores'),
      '@services': resolve(__dirname, 'src/services'),
      '@types': resolve(__dirname, 'src/types'),
      '@assets': resolve(__dirname, 'src/assets')
    }
  },
  
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true
      },
      '/ws': {
        target: 'ws://localhost:3002',
        ws: true
      }
    }
  },
  
  build: {
    target: 'esnext',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'ui-vendor': ['@headlessui/vue', '@heroicons/vue']
        }
      }
    }
  },
  
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia']
  }
})
```

### Vue Application Setup
```typescript
// src/main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { router } from './router'
import { i18n } from './i18n'
import App from './App.vue'
import './assets/styles/main.css'

// Global components
import BaseButton from '@components/base/BaseButton.vue'
import BaseInput from '@components/base/BaseInput.vue'
import BaseModal from '@components/base/BaseModal.vue'
import LoadingSpinner from '@components/base/LoadingSpinner.vue'

const app = createApp(App)

// Install plugins
app.use(createPinia())
app.use(router)
app.use(i18n)

// Register global components
app.component('BaseButton', BaseButton)
app.component('BaseInput', BaseInput)
app.component('BaseModal', BaseModal)
app.component('LoadingSpinner', LoadingSpinner)

// Global error handler
app.config.errorHandler = (err, instance, info) => {
  console.error('Global error:', err, info)
  // Send to error tracking service
}

app.mount('#app')
```

### Router Configuration
```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@stores/auth'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@views/HomeView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@views/auth/LoginView.vue'),
    meta: { requiresAuth: false, hideForAuth: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@views/DashboardView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/conversations',
    name: 'Conversations',
    component: () => import('@views/conversations/ConversationListView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/conversations/:id',
    name: 'ConversationDetail',
    component: () => import('@views/conversations/ConversationDetailView.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: () => import('@views/analytics/AnalyticsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@views/SettingsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@views/NotFoundView.vue')
  }
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }
  
  // Hide auth pages for authenticated users
  if (to.meta.hideForAuth && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
    return
  }
  
  next()
})
```

### Pinia Store Architecture
```typescript
// src/stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@services/auth'
import type { User, LoginCredentials } from '@types/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  
  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userPermissions = computed(() => user.value?.permissions || [])
  
  // Actions
  async function login(credentials: LoginCredentials) {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await authService.login(credentials)
      
      token.value = response.token
      user.value = response.user
      
      localStorage.setItem('auth_token', response.token)
      
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Login failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  async function logout() {
    try {
      await authService.logout()
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('auth_token')
    }
  }
  
  async function refreshToken() {
    if (!token.value) return false
    
    try {
      const response = await authService.refreshToken()
      token.value = response.token
      localStorage.setItem('auth_token', response.token)
      return true
    } catch (err) {
      await logout()
      return false
    }
  }
  
  async function fetchUser() {
    if (!token.value) return
    
    try {
      user.value = await authService.getProfile()
    } catch (err) {
      console.error('Failed to fetch user:', err)
      await logout()
    }
  }
  
  function hasPermission(permission: string): boolean {
    return userPermissions.value.includes(permission)
  }
  
  return {
    // State
    user: readonly(user),
    token: readonly(token),
    isLoading: readonly(isLoading),
    error: readonly(error),
    
    // Getters
    isAuthenticated,
    userPermissions,
    
    // Actions
    login,
    logout,
    refreshToken,
    fetchUser,
    hasPermission
  }
})
```

### API Service Layer
```typescript
// src/services/api.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { useAuthStore } from '@stores/auth'
import { useNotificationStore } from '@stores/notifications'

class ApiService {
  private client: AxiosInstance
  
  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    this.setupInterceptors()
  }
  
  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const authStore = useAuthStore()
        
        if (authStore.token) {
          config.headers.Authorization = `Bearer ${authStore.token}`
        }
        
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )
    
    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const authStore = useAuthStore()
        const notificationStore = useNotificationStore()
        
        if (error.response?.status === 401) {
          // Try to refresh token
          const refreshed = await authStore.refreshToken()
          
          if (refreshed && error.config) {
            // Retry original request
            return this.client.request(error.config)
          } else {
            // Redirect to login
            await authStore.logout()
            window.location.href = '/login'
          }
        }
        
        // Handle other errors
        if (error.response?.status >= 500) {
          notificationStore.addNotification({
            type: 'error',
            title: 'Server Error',
            message: 'An unexpected error occurred. Please try again later.'
          })
        }
        
        return Promise.reject(error)
      }
    )
  }
  
  // Generic HTTP methods
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config)
    return response.data
  }
  
  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config)
    return response.data
  }
  
  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<T>(url, data, config)
    return response.data
  }
  
  async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.patch<T>(url, data, config)
    return response.data
  }
  
  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config)
    return response.data
  }
}

export const apiService = new ApiService()
```

### Tailwind CSS Configuration
```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          950: '#082f49',
        },
        secondary: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617',
        },
        success: {
          50: '#f0fdf4',
          500: '#22c55e',
          600: '#16a34a',
        },
        warning: {
          50: '#fffbeb',
          500: '#f59e0b',
          600: '#d97706',
        },
        error: {
          50: '#fef2f2',
          500: '#ef4444',
          600: '#dc2626',
        }
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
  darkMode: 'class',
}
```

### Main Layout Component
```vue
<!-- src/components/layout/AppLayout.vue -->
<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
    <!-- Navigation -->
    <AppNavigation 
      :is-sidebar-open="isSidebarOpen"
      @toggle-sidebar="toggleSidebar"
    />
    
    <!-- Main Content -->
    <div 
      class="transition-all duration-300"
      :class="isSidebarOpen ? 'lg:ml-64' : 'lg:ml-16'"
    >
      <!-- Top Bar -->
      <AppTopBar @toggle-sidebar="toggleSidebar" />
      
      <!-- Page Content -->
      <main class="p-6">
        <router-view v-slot="{ Component, route }">
          <transition name="page" mode="out-in">
            <component :is="Component" :key="route.path" />
          </transition>
        </router-view>
      </main>
    </div>
    
    <!-- Global Modals -->
    <AppModals />
    
    <!-- Notifications -->
    <AppNotifications />
    
    <!-- WebSocket Status -->
    <WebSocketStatus />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@stores/auth'
import { useWebSocketStore } from '@stores/websocket'
import AppNavigation from './AppNavigation.vue'
import AppTopBar from './AppTopBar.vue'
import AppModals from './AppModals.vue'
import AppNotifications from './AppNotifications.vue'
import WebSocketStatus from '@components/websocket/WebSocketStatus.vue'

const authStore = useAuthStore()
const webSocketStore = useWebSocketStore()

const isSidebarOpen = ref(true)

function toggleSidebar() {
  isSidebarOpen.value = !isSidebarOpen.value
}

onMounted(async () => {
  // Initialize user session
  if (authStore.token) {
    await authStore.fetchUser()
    
    // Connect WebSocket if authenticated
    if (authStore.isAuthenticated) {
      webSocketStore.connect()
    }
  }
})
</script>

<style scoped>
.page-enter-active,
.page-leave-active {
  transition: all 0.3s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateX(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}
</style>
```

### WebSocket Store Integration
```typescript
// src/stores/websocket.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { WebSocketClient } from '@services/websocket'
import { useAuthStore } from './auth'
import { useNotificationStore } from './notifications'

export const useWebSocketStore = defineStore('websocket', () => {
  const client = ref<WebSocketClient | null>(null)
  const isConnected = ref(false)
  const isConnecting = ref(false)
  const lastError = ref<string | null>(null)
  
  const connectionStatus = computed(() => {
    if (isConnecting.value) return 'connecting'
    if (isConnected.value) return 'connected'
    if (lastError.value) return 'error'
    return 'disconnected'
  })
  
  async function connect() {
    const authStore = useAuthStore()
    const notificationStore = useNotificationStore()
    
    if (!authStore.token || isConnecting.value) return
    
    isConnecting.value = true
    lastError.value = null
    
    try {
      const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:3002/ws'
      client.value = new WebSocketClient(wsUrl, authStore.token)
      
      // Setup event handlers
      client.value.on('connection_established', (data) => {
        isConnected.value = true
        isConnecting.value = false
        console.log('WebSocket connected:', data)
      })
      
      client.value.on('error', (error) => {
        lastError.value = error.message
        notificationStore.addNotification({
          type: 'error',
          title: 'Connection Error',
          message: 'Failed to connect to real-time services'
        })
      })
      
      client.value.on('disconnect', () => {
        isConnected.value = false
      })
      
      await client.value.connect()
    } catch (error) {
      isConnecting.value = false
      lastError.value = error instanceof Error ? error.message : 'Connection failed'
      console.error('WebSocket connection failed:', error)
    }
  }
  
  function disconnect() {
    if (client.value) {
      client.value.disconnect()
      client.value = null
    }
    isConnected.value = false
    isConnecting.value = false
  }
  
  function subscribe(channel: string) {
    if (client.value && isConnected.value) {
      client.value.subscribe(channel)
    }
  }
  
  function unsubscribe(channel: string) {
    if (client.value && isConnected.value) {
      client.value.unsubscribe(channel)
    }
  }
  
  function send(type: string, data: any) {
    if (client.value && isConnected.value) {
      client.value.send(type, data)
    }
  }
  
  function on(eventType: string, handler: Function) {
    if (client.value) {
      client.value.on(eventType, handler)
    }
  }
  
  function off(eventType: string, handler: Function) {
    if (client.value) {
      client.value.off(eventType, handler)
    }
  }
  
  return {
    // State
    isConnected: readonly(isConnected),
    isConnecting: readonly(isConnecting),
    lastError: readonly(lastError),
    connectionStatus,
    
    // Actions
    connect,
    disconnect,
    subscribe,
    unsubscribe,
    send,
    on,
    off
  }
})
```

## Performance Requirements
- **Initial Load Time**: First Contentful Paint within 1.5 seconds
- **Bundle Size**: Main bundle under 500KB gzipped
- **Runtime Performance**: 60fps scrolling and interactions
- **Memory Usage**: Client-side memory under 100MB
- **API Response**: UI updates within 100ms of API response

## Acceptance Criteria
- [ ] Vite development server running with HMR
- [ ] Vue 3 application with Composition API
- [ ] TypeScript configuration and type safety
- [ ] Tailwind CSS integrated with design system
- [ ] Vue Router with protected routes
- [ ] Pinia stores for state management
- [ ] API service layer with error handling
- [ ] WebSocket integration for real-time updates
- [ ] Responsive design across device sizes
- [ ] Component testing setup with Vitest
- [ ] Build optimization and code splitting

## Testing Procedures
1. **Component Testing**: Test individual Vue components
2. **Integration Testing**: Test store integrations and API calls
3. **E2E Testing**: Test complete user workflows
4. **Performance Testing**: Lighthouse audits and bundle analysis
5. **Accessibility Testing**: WCAG compliance verification

## Integration Points
- **Week 5-6**: Backend API and WebSocket consumption
- **Week 8**: UI component integration
- **Week 9-10**: Analytics and visualization components

## Development Tools
- **Vue DevTools**: Browser extension for debugging
- **Vite Plugin PWA**: Progressive Web App capabilities
- **ESLint + Prettier**: Code formatting and linting
- **Husky**: Git hooks for code quality
- **Commitizen**: Conventional commit messages

#### ESLint Configuration

```javascript
// .eslintrc.js
module.exports = {
  root: true,
  env: {
    node: true,
    es2022: true,
    browser: true,
  },
  extends: [
    'plugin:vue/vue3-essential',
    'eslint:recommended',
    '@vue/eslint-config-typescript',
    '@vue/eslint-config-prettier/skip-formatting',
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    parser: '@typescript-eslint/parser',
    sourceType: 'module',
  },
  plugins: ['vue', '@typescript-eslint'],
  rules: {
    'vue/multi-word-component-names': 'off',
    'vue/component-tags-order': [
      'error',
      {
        order: ['script', 'template', 'style'],
      },
    ],
    'vue/component-name-in-template-casing': ['error', 'PascalCase'],
    'vue/custom-event-name-casing': ['error', 'camelCase'],
    'vue/define-macros-order': ['error', {
      order: ['defineProps', 'defineEmits', 'defineExpose'],
    }],
    'vue/no-unused-vars': 'error',
    'vue/prefer-const-type-assertion': 'error',
    'vue/prefer-true-attribute-shorthand': 'error',
    '@typescript-eslint/no-unused-vars': 'error',
    '@typescript-eslint/prefer-const': 'error',
    '@typescript-eslint/no-explicit-any': 'warn',
    '@typescript-eslint/explicit-function-return-type': 'off',
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    'prefer-const': 'error',
    'no-var': 'error',
    'object-shorthand': 'error',
    'prefer-arrow-callback': 'error',
  },
  overrides: [
    {
      files: ['*.vue'],
      parser: 'vue-eslint-parser',
      parserOptions: {
        parser: '@typescript-eslint/parser',
      },
    },
  ],
}
```

#### Prettier Configuration

```json
// .prettierrc.json
{
  "semi": false,
  "tabWidth": 2,
  "singleQuote": true,
  "printWidth": 80,
  "trailingComma": "es5",
  "bracketSpacing": true,
  "arrowParens": "avoid",
  "endOfLine": "auto",
  "htmlWhitespaceSensitivity": "css",
  "insertPragma": false,
  "jsxBracketSameLine": false,
  "jsxSingleQuote": false,
  "proseWrap": "preserve",
  "quoteProps": "as-needed",
  "requirePragma": false,
  "useTabs": false,
  "vueIndentScriptAndStyle": false
}
```

#### Vitest Configuration

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.test.ts',
        '**/*.spec.ts',
      ],
    },
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@views': resolve(__dirname, 'src/views'),
      '@stores': resolve(__dirname, 'src/stores'),
      '@services': resolve(__dirname, 'src/services'),
      '@types': resolve(__dirname, 'src/types'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@assets': resolve(__dirname, 'src/assets'),
    },
  },
})
```

#### Test Setup File

```typescript
// src/test/setup.ts
import { vi } from 'vitest'
import { config } from '@vue/test-utils'

// Mock global objects
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Configure Vue Test Utils
config.global.plugins = []
```

#### Git Hooks with Husky

```bash
# Install husky
npm install --save-dev husky

# Initialize husky
npx husky install
npm set-script prepare "husky install"

# Add pre-commit hook
npx husky add .husky/pre-commit "npm run lint && npm run type-check"

# Add commit-msg hook
npx husky add .husky/commit-msg 'npx --no-install commitlint --edit "$1"'
```

#### Commitlint Configuration

```javascript
// commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',
        'fix',
        'docs',
        'style',
        'refactor',
        'perf',
        'test',
        'chore',
        'revert',
        'build',
        'ci',
      ],
    ],
    'scope-enum': [
      2,
      'always',
      [
        'core',
        'ui',
        'store',
        'router',
        'service',
        'component',
        'types',
        'utils',
        'config',
        'test',
        'build',
        'docs',
      ],
    ],
    'subject-max-length': [2, 'always', 100],
    'body-max-line-length': [2, 'always', 100],
  },
}
```

### Development Workflow and Best Practices

#### Component Testing with Vitest

```typescript
// src/components/__tests__/ConversationCard.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ConversationCard from '@/components/ConversationCard.vue'
import { useConversationStore } from '@/stores/conversation'
import type { Conversation } from '@/types/conversation'

// Mock the router
const mockRouter = {
  push: vi.fn()
}

vi.mock('vue-router', () => ({
  useRouter: () => mockRouter
}))

describe('ConversationCard', () => {
  let pinia: ReturnType<typeof createPinia>
  let conversationStore: ReturnType<typeof useConversationStore>
  
  const mockConversation: Conversation = {
    id: 'conv-123',
    title: 'Test Conversation',
    status: 'active',
    createdAt: new Date('2024-01-01'),
    updatedAt: new Date('2024-01-01'),
    messageCount: 5,
    tools: [{
      id: 'tool-1',
      name: 'File Reader',
      description: 'Reads files',
      category: 'file',
      usage: { count: 3, lastUsed: new Date(), averageExecutionTime: 100 }
    }],
    metadata: {
      projectPath: '/test/project',
      environment: 'development',
      totalTokens: 1000,
      cost: 0.05,
      tags: ['test']
    },
    participants: [{
      id: 'user-1',
      name: 'Test User',
      role: 'user'
    }]
  }

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    conversationStore = useConversationStore()
    
    vi.spyOn(conversationStore, 'fetchConversationDetails').mockResolvedValue(mockConversation)
  })

  it('renders conversation information correctly', () => {
    const wrapper = mount(ConversationCard, {
      props: { conversation: mockConversation },
      global: { plugins: [pinia] }
    })

    expect(wrapper.text()).toContain('Test Conversation')
    expect(wrapper.text()).toContain('active')
    expect(wrapper.text()).toContain('5 messages')
  })

  it('handles view action correctly', async () => {
    const wrapper = mount(ConversationCard, {
      props: { conversation: mockConversation },
      global: { plugins: [pinia] }
    })

    await wrapper.find('[data-testid="view-button"]').trigger('click')
    
    expect(conversationStore.fetchConversationDetails).toHaveBeenCalledWith('conv-123')
    expect(mockRouter.push).toHaveBeenCalledWith('/conversations/conv-123')
  })
})
```

#### Store Testing Patterns

```typescript
// src/stores/__tests__/conversation.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useConversationStore } from '@/stores/conversation'
import { conversationService } from '@/services/conversation'

vi.mock('@/services/conversation')

describe('useConversationStore', () => {
  let store: ReturnType<typeof useConversationStore>

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useConversationStore()
    vi.clearAllMocks()
  })

  it('fetches conversations successfully', async () => {
    const mockData = [{ id: '1', title: 'Test', status: 'active' }]
    vi.mocked(conversationService.getConversations).mockResolvedValue({
      success: true,
      data: mockData,
      pagination: { page: 1, limit: 20, total: 1, totalPages: 1, hasNext: false, hasPrev: false }
    })

    await store.fetchConversations()

    expect(store.conversations).toEqual(mockData)
    expect(store.isLoading).toBe(false)
    expect(store.error).toBe(null)
  })

  it('handles fetch errors', async () => {
    vi.mocked(conversationService.getConversations).mockRejectedValue(new Error('Network error'))

    await store.fetchConversations()

    expect(store.error).toBe('Network error')
    expect(store.isLoading).toBe(false)
  })
})
```

#### Performance Optimization Patterns

```typescript
// src/composables/useVirtualScroll.ts
import { ref, computed, onMounted, onUnmounted } from 'vue'

export function useVirtualScroll<T>(
  items: T[],
  containerHeight: number,
  itemHeight: number,
  options: {
    overscan?: number
    bufferSize?: number
  } = {}
) {
  const { overscan = 5, bufferSize = 10 } = options
  
  const scrollTop = ref(0)
  const containerRef = ref<HTMLElement>()
  
  const visibleRange = computed(() => {
    const start = Math.floor(scrollTop.value / itemHeight)
    const end = Math.min(
      start + Math.ceil(containerHeight / itemHeight) + overscan,
      items.length
    )
    
    return {
      start: Math.max(0, start - overscan),
      end
    }
  })
  
  const visibleItems = computed(() => {
    const { start, end } = visibleRange.value
    return items.slice(start, end).map((item, index) => ({
      item,
      index: start + index
    }))
  })
  
  const totalHeight = computed(() => items.length * itemHeight)
  
  const offsetY = computed(() => visibleRange.value.start * itemHeight)
  
  const handleScroll = (event: Event) => {
    scrollTop.value = (event.target as HTMLElement).scrollTop
  }
  
  onMounted(() => {
    containerRef.value?.addEventListener('scroll', handleScroll)
  })
  
  onUnmounted(() => {
    containerRef.value?.removeEventListener('scroll', handleScroll)
  })
  
  return {
    containerRef,
    visibleItems,
    totalHeight,
    offsetY,
    scrollTop
  }
}
```

#### Error Handling Patterns

```typescript
// src/composables/useErrorHandler.ts
import { ref } from 'vue'
import { useNotificationStore } from '@/stores/notifications'

export function useErrorHandler() {
  const error = ref<string | null>(null)
  const notificationStore = useNotificationStore()
  
  const handleError = (err: unknown, context?: string) => {
    let message = 'An unexpected error occurred'
    
    if (err instanceof Error) {
      message = err.message
    } else if (typeof err === 'string') {
      message = err
    }
    
    error.value = message
    
    // Log to console in development
    if (import.meta.env.DEV) {
      console.error(`Error in ${context || 'unknown context'}:`, err)
    }
    
    // Send to external error reporting service
    if (import.meta.env.VITE_SENTRY_DSN) {
      // Sentry.captureException(err)
    }
    
    // Show user notification
    notificationStore.addNotification({
      type: 'error',
      title: 'Error',
      message,
      duration: 5000
    })
  }
  
  const clearError = () => {
    error.value = null
  }
  
  return {
    error,
    handleError,
    clearError
  }
}
```

#### Form Validation with VeeValidate

```typescript
// src/composables/useFormValidation.ts
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'

export function useConversationFormValidation() {
  const schema = toTypedSchema(z.object({
    title: z.string().min(1, 'Title is required').max(100, 'Title too long'),
    description: z.string().max(500, 'Description too long').optional(),
    tags: z.array(z.string()).max(10, 'Too many tags'),
    isPrivate: z.boolean().default(false),
    participants: z.array(z.object({
      id: z.string(),
      role: z.enum(['user', 'assistant'])
    })).min(1, 'At least one participant required')
  }))
  
  const { handleSubmit, errors, values, setFieldValue } = useForm({
    validationSchema: schema,
    initialValues: {
      title: '',
      description: '',
      tags: [],
      isPrivate: false,
      participants: []
    }
  })
  
  const onSubmit = handleSubmit(async (values) => {
    // Handle form submission
    console.log('Form submitted:', values)
  })
  
  return {
    errors,
    values,
    setFieldValue,
    onSubmit
  }
}
```

### Build Optimization and Deployment

#### Bundle Analysis Configuration

```typescript
// vite.config.ts - Production optimizations
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { visualizer } from 'rollup-plugin-visualizer'

export default defineConfig({
  plugins: [
    vue(),
    // Bundle analyzer
    visualizer({
      filename: 'dist/stats.html',
      open: true,
      gzipSize: true,
      brotliSize: true,
    }),
  ],
  
  build: {
    target: 'es2020',
    sourcemap: false,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks
          'vue-vendor': ['vue', 'vue-router'],
          'pinia-vendor': ['pinia'],
          'ui-vendor': ['@headlessui/vue', '@heroicons/vue'],
          'chart-vendor': ['chart.js', 'vue-chartjs'],
          'utils-vendor': ['lodash-es', 'date-fns', 'fuse.js'],
          
          // Feature chunks
          'conversation-feature': [
            './src/views/conversations/',
            './src/components/conversation/',
            './src/stores/conversation.ts'
          ],
          'analytics-feature': [
            './src/views/analytics/',
            './src/components/analytics/',
            './src/stores/analytics.ts'
          ]
        },
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId
          if (facadeModuleId) {
            return `js/[name]-[hash].js`
          }
          return `js/[name]-[hash].js`
        },
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name!.split('.')
          const ext = info[info.length - 1]
          
          if (/\.(png|jpe?g|svg|gif|tiff|bmp|ico)$/i.test(assetInfo.name!)) {
            return `images/[name]-[hash][extname]`
          }
          if (/\.(woff2?|eot|ttf|otf)$/i.test(assetInfo.name!)) {
            return `fonts/[name]-[hash][extname]`
          }
          if (ext === 'css') {
            return `css/[name]-[hash][extname]`
          }
          return `assets/[name]-[hash][extname]`
        }
      }
    },
    chunkSizeWarningLimit: 1000
  },
  
  optimizeDeps: {
    include: [
      'vue',
      'vue-router',
      'pinia',
      'axios',
      '@vueuse/core',
      'date-fns',
      'lodash-es',
      'chart.js',
      'vue-chartjs'
    ]
  }
})
```

#### PWA Configuration

```typescript
// vite.config.ts - PWA setup
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\.example\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 10,
                maxAgeSeconds: 60 * 60 * 24 * 365 // 1 year
              },
              cacheKeyWillBeUsed: async ({ request }) => {
                return `${request.url}?version=1`
              }
            }
          }
        ]
      },
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
      manifest: {
        name: 'Claude Code Observatory',
        short_name: 'CCO',
        description: 'Observability platform for Claude Code interactions',
        theme_color: '#3b82f6',
        background_color: '#ffffff',
        display: 'standalone',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable'
          }
        ]
      }
    })
  ]
})
```

#### Docker Configuration

```dockerfile
# Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;

    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' wss: https:;" always;

        # Handle SPA routing
        location / {
            try_files $uri $uri/ /index.html;
        }

        # API proxy
        location /api {
            proxy_pass http://backend:3001;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket proxy
        location /ws {
            proxy_pass http://backend:3002;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Static assets caching
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

## Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari 14+, Chrome Mobile 90+)

## Key Features Implemented

### 1. Type-Safe Development
- Complete TypeScript integration with Vue 3
- Comprehensive type definitions for all data structures
- Type-safe API calls and store operations
- Proper component prop and emit typing

### 2. Modern State Management
- Pinia stores with Composition API syntax
- Reactive state with computed properties
- Async actions with proper error handling
- Real-time updates through WebSocket integration

### 3. Performance Optimization
- Code splitting and lazy loading
- Virtual scrolling for large lists
- Optimized bundle chunks
- Progressive Web App capabilities

### 4. Developer Experience
- Hot Module Replacement (HMR)
- Comprehensive testing setup
- Code formatting and linting
- Error tracking and debugging tools

### 5. Production Ready
- Docker containerization
- Nginx reverse proxy configuration
- Security headers and CSP
- Performance monitoring and analytics

## Implementation Checklist

### Week 7 Day 1: Project Foundation
- [ ] Initialize Vue 3 project with TypeScript
- [ ] Configure Vite build system
- [ ] Set up Tailwind CSS with design tokens
- [ ] Configure development environment
- [ ] Set up Git hooks and commit conventions

### Week 7 Day 2: Routing & Architecture
- [ ] Configure Vue Router with TypeScript
- [ ] Create layout components (AppLayout, AppNavigation)
- [ ] Set up protected routes and guards
- [ ] Implement responsive navigation
- [ ] Create route-based code splitting

### Week 7 Day 3: State Management
- [ ] Set up Pinia with TypeScript
- [ ] Create conversation store with full CRUD
- [ ] Implement authentication store
- [ ] Set up API service layer with interceptors
- [ ] Add error handling and loading states

### Week 7 Day 4: Component Library
- [ ] Create base component library
- [ ] Implement form components with validation
- [ ] Build data display components
- [ ] Create modal and notification systems
- [ ] Set up component testing framework

### Week 7 Day 5: WebSocket & Testing
- [ ] Integrate WebSocket for real-time updates
- [ ] Set up comprehensive testing suite
- [ ] Write unit tests for key components
- [ ] Create integration test scenarios
- [ ] Performance optimization and PWA setup

## Success Metrics

### Technical Metrics
- **Build Time**: < 30 seconds for development builds
- **Bundle Size**: < 500KB gzipped for initial load
- **Test Coverage**: > 80% for critical components
- **TypeScript Coverage**: 100% strict mode compliance
- **Performance**: Lighthouse score > 90

### Development Metrics
- **Developer Experience**: Hot reload < 500ms
- **Code Quality**: Zero ESLint/TypeScript errors
- **Commit Convention**: 100% conventional commits
- **Documentation**: All components documented
- **Testing**: All critical paths covered

## Post-Week 7 Roadmap

### Week 8: Advanced Features
- Enhanced component library with accessibility
- Advanced state management patterns
- Performance monitoring integration
- Advanced testing strategies

### Week 9: Integration & Polish
- Backend API integration completion
- WebSocket real-time features
- Advanced analytics dashboard
- Performance optimization

### Week 10: Production Readiness
- Security hardening
- Performance optimization
- Monitoring and observability
- Documentation completion

## Additional Resources

### Documentation Links
- [Vue 3 Official Documentation](https://v3.vuejs.org/)
- [Pinia State Management](https://pinia.vuejs.org/)
- [TypeScript Vue Guide](https://vuejs.org/guide/typescript/overview.html)
- [Vite Build Tool](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)

### Community Resources
- Vue.js Discord Community
- Vue.js GitHub Discussions
- Stack Overflow Vue.js Tag
- Vue.js YouTube Channel
- Vue Mastery Learning Platform

### Tools and Extensions
- Vue DevTools Browser Extension
- Volar VS Code Extension
- Vue 3 Snippets Extension
- ESLint Vue Plugin
- Prettier Vue Plugin

This comprehensive frontend setup provides a robust foundation for the Claude Code Observatory's user interface, ensuring type safety, performance, and developer productivity throughout the development process.