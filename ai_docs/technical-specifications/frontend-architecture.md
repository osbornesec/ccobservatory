# 🎨 Frontend Architecture Technical Specification

## 🎯 **Executive Summary**

This specification defines the Vue 3 frontend architecture for Claude Code Observatory, implementing a modern, reactive, and scalable user interface. The system leverages the Composition API, TypeScript, and advanced state management patterns to deliver a responsive real-time dashboard experience with sub-200ms interaction times and comprehensive accessibility support.

---

## 📋 **Technical Requirements**

### **Performance Requirements**
- **Initial Load Time:** <3 seconds (95th percentile)
- **UI Interaction Response:** <200ms (95th percentile)
- **Real-time Update Latency:** <100ms from WebSocket message
- **Bundle Size:** <500KB initial, <2MB total
- **Memory Usage:** <100MB for typical sessions

### **User Experience Requirements**
- **WCAG 2.1 AA Compliance:** Full accessibility support
- **Responsive Design:** 320px to 4K viewport support
- **Offline Capability:** Basic functionality without network
- **Progressive Enhancement:** Graceful degradation
- **Keyboard Navigation:** Complete interface accessibility

### **Browser Compatibility**
- **Modern Browsers:** Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Mobile Support:** iOS Safari 14+, Chrome Mobile 90+
- **Feature Detection:** Polyfills for missing features
- **Error Boundaries:** Graceful failure handling

---

## 🏗️ **Architecture Overview**

### **System Components**

```
┌─────────────────────────────────────────────────────────────┐
│                    Vue 3 Application                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │    Router   │  │   Store     │  │    WebSocket        │  │
│  │   (Vue      │──│   (Pinia)   │──│     Client          │  │
│  │   Router)   │  │             │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│         │                 │                       │         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ View        │  │ Component   │  │    Service          │  │
│  │ Components  │  │ Library     │  │    Layer            │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│         │                 │                       │         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ UI          │  │ Utilities   │  │    API              │  │
│  │ Framework   │  │ & Helpers   │  │    Client           │  │
│  │ (Tailwind)  │  │             │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### **Project Structure**

```
src/
├── main.ts                    # Application entry point
├── App.vue                    # Root component
├── router/                    # Vue Router configuration
│   ├── index.ts
│   ├── routes.ts
│   └── guards.ts
├── stores/                    # Pinia state management
│   ├── index.ts
│   ├── conversations.ts
│   ├── projects.ts
│   ├── analytics.ts
│   └── websocket.ts
├── components/                # Reusable components
│   ├── common/               # Generic UI components
│   │   ├── Button.vue
│   │   ├── Modal.vue
│   │   ├── DataTable.vue
│   │   └── SearchInput.vue
│   ├── conversation/         # Conversation-specific components
│   │   ├── ConversationViewer.vue
│   │   ├── MessageDisplay.vue
│   │   ├── ToolUsageBlock.vue
│   │   └── ConversationList.vue
│   ├── analytics/            # Analytics components
│   │   ├── MetricsCard.vue
│   │   ├── TimeSeriesChart.vue
│   │   ├── ToolUsageChart.vue
│   │   └── AnalyticsDashboard.vue
│   └── layout/               # Layout components
│       ├── HeaderBar.vue
│       ├── Sidebar.vue
│       ├── NavigationMenu.vue
│       └── StatusBar.vue
├── views/                     # Page-level components
│   ├── Dashboard.vue
│   ├── Projects.vue
│   ├── Conversations.vue
│   ├── Analytics.vue
│   └── Settings.vue
├── composables/              # Composition API utilities
│   ├── useWebSocket.ts
│   ├── useConversations.ts
│   ├── useSearch.ts
│   ├── useAnalytics.ts
│   └── useNotifications.ts
├── services/                 # API and business logic
│   ├── api.ts
│   ├── websocket.ts
│   ├── storage.ts
│   └── analytics.ts
├── types/                    # TypeScript definitions
│   ├── api.ts
│   ├── websocket.ts
│   ├── conversation.ts
│   └── analytics.ts
├── utils/                    # Utility functions
│   ├── formatting.ts
│   ├── validation.ts
│   ├── date.ts
│   └── performance.ts
└── assets/                   # Static assets
    ├── styles/
    │   ├── main.css
    │   ├── components.css
    │   └── utilities.css
    ├── icons/
    └── images/
```

---

## 🔧 **Core Application Setup**

### **Main Application Bootstrap**

```typescript
// src/main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { router } from './router'
import { createVuestic } from 'vuestic-ui'
import App from './App.vue'

// Styles
import 'vuestic-ui/css'
import './assets/styles/main.css'

// Global error handler
import { setupErrorHandling } from './utils/error-handling'

// Performance monitoring
import { setupPerformanceMonitoring } from './utils/performance'

async function createApplication() {
  const app = createApp(App)
  
  // Store setup
  const pinia = createPinia()
  app.use(pinia)
  
  // Router setup
  app.use(router)
  
  // UI framework
  app.use(createVuestic({
    config: {
      colors: {
        variables: {
          primary: '#3B82F6',
          secondary: '#6B7280',
          success: '#10B981',
          warning: '#F59E0B',
          danger: '#EF4444'
        }
      },
      components: {
        all: {
          preset: 'floating'
        }
      }
    }
  }))
  
  // Global properties
  app.config.globalProperties.$filters = {
    formatDate: (date: Date) => new Intl.DateTimeFormat().format(date),
    formatDuration: (ms: number) => {
      const seconds = Math.floor(ms / 1000)
      const minutes = Math.floor(seconds / 60)
      const hours = Math.floor(minutes / 60)
      return hours > 0 ? `${hours}h ${minutes % 60}m` : `${minutes}m ${seconds % 60}s`
    }
  }
  
  // Error handling
  setupErrorHandling(app)
  
  // Performance monitoring
  setupPerformanceMonitoring(app)
  
  // Mount application
  app.mount('#app')
  
  return app
}

createApplication().catch(console.error)
```

### **Root App Component**

```vue
<!-- src/App.vue -->
<template>
  <div id="app" class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Global loading overlay -->
    <Teleport to="body">
      <div
        v-if="isLoading"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
        role="dialog"
        aria-labelledby="loading-title"
        aria-describedby="loading-description"
      >
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-xl">
          <div class="flex items-center space-x-3">
            <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            <span id="loading-title" class="text-lg font-medium">{{ loadingMessage }}</span>
          </div>
          <p id="loading-description" class="sr-only">Application is loading, please wait</p>
        </div>
      </div>
    </Teleport>

    <!-- Main application layout -->
    <div v-if="!isLoading" class="flex h-screen">
      <!-- Sidebar -->
      <Sidebar
        v-if="showSidebar"
        :collapsed="sidebarCollapsed"
        @toggle="toggleSidebar"
        class="flex-shrink-0"
      />

      <!-- Main content area -->
      <div class="flex-1 flex flex-col overflow-hidden">
        <!-- Header -->
        <HeaderBar
          :show-menu-button="!showSidebar"
          @menu-click="toggleSidebar"
          class="flex-shrink-0"
        />

        <!-- Router view with transitions -->
        <main class="flex-1 overflow-auto">
          <router-view v-slot="{ Component, route }">
            <transition
              :name="route.meta.transition || 'fade'"
              mode="out-in"
              appear
            >
              <component
                :is="Component"
                :key="route.fullPath"
                class="p-6"
              />
            </transition>
          </router-view>
        </main>

        <!-- Status bar -->
        <StatusBar class="flex-shrink-0" />
      </div>
    </div>

    <!-- Global notifications -->
    <NotificationContainer />

    <!-- Global modals -->
    <ModalContainer />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'

import HeaderBar from './components/layout/HeaderBar.vue'
import Sidebar from './components/layout/Sidebar.vue'
import StatusBar from './components/layout/StatusBar.vue'
import NotificationContainer from './components/common/NotificationContainer.vue'
import ModalContainer from './components/common/ModalContainer.vue'

import { useAppStore } from './stores/app'
import { useWebSocketStore } from './stores/websocket'
import { useTheme } from './composables/useTheme'
import { useBreakpoints } from './composables/useBreakpoints'

// Stores
const appStore = useAppStore()
const websocketStore = useWebSocketStore()

// Composables
const route = useRoute()
const router = useRouter()
const { isDark, toggleTheme } = useTheme()
const { isMobile, isTablet } = useBreakpoints()

// Reactive state
const sidebarCollapsed = ref(false)
const { isLoading, loadingMessage } = storeToRefs(appStore)

// Computed properties
const showSidebar = computed(() => !isMobile.value)

// Methods
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// Lifecycle
onMounted(async () => {
  try {
    // Initialize application
    await appStore.initialize()
    
    // Connect WebSocket
    await websocketStore.connect()
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts()
    
  } catch (error) {
    console.error('Failed to initialize application:', error)
    // Show error notification
  }
})

onUnmounted(() => {
  // Cleanup WebSocket connection
  websocketStore.disconnect()
})

// Keyboard shortcuts
const setupKeyboardShortcuts = () => {
  const handleKeydown = (event: KeyboardEvent) => {
    // Ctrl/Cmd + K: Open search
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
      event.preventDefault()
      // Open search modal
    }
    
    // Ctrl/Cmd + /: Toggle sidebar
    if ((event.ctrlKey || event.metaKey) && event.key === '/') {
      event.preventDefault()
      toggleSidebar()
    }
    
    // Escape: Close modals
    if (event.key === 'Escape') {
      // Close any open modals
    }
  }
  
  document.addEventListener('keydown', handleKeydown)
  
  return () => {
    document.removeEventListener('keydown', handleKeydown)
  }
}
</script>

<style>
/* Global transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from {
  transform: translateX(-100%);
}

.slide-leave-to {
  transform: translateX(100%);
}
</style>
```

---

## 📊 **State Management with Pinia**

### **Application Store**

```typescript
// src/stores/app.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { AppConfig, UserPreferences, SystemInfo } from '@/types/app'

export const useAppStore = defineStore('app', () => {
  // State
  const isLoading = ref(false)
  const loadingMessage = ref('')
  const config = ref<AppConfig | null>(null)
  const userPreferences = ref<UserPreferences>({
    theme: 'system',
    sidebarCollapsed: false,
    notifications: true,
    autoRefresh: true,
    refreshInterval: 30000
  })
  const systemInfo = ref<SystemInfo | null>(null)
  const errors = ref<AppError[]>([])

  // Getters
  const isDarkMode = computed(() => {
    if (userPreferences.value.theme === 'system') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    return userPreferences.value.theme === 'dark'
  })

  const hasErrors = computed(() => errors.value.length > 0)

  // Actions
  const initialize = async () => {
    setLoading(true, 'Initializing application...')
    
    try {
      // Load configuration
      config.value = await loadConfig()
      
      // Load user preferences
      await loadUserPreferences()
      
      // Get system information
      systemInfo.value = await getSystemInfo()
      
      // Apply theme
      applyTheme()
      
    } catch (error) {
      addError({
        id: Date.now().toString(),
        type: 'initialization',
        message: 'Failed to initialize application',
        details: error,
        timestamp: Date.now()
      })
      throw error
    } finally {
      setLoading(false)
    }
  }

  const setLoading = (loading: boolean, message = '') => {
    isLoading.value = loading
    loadingMessage.value = message
  }

  const updatePreferences = async (newPreferences: Partial<UserPreferences>) => {
    userPreferences.value = { ...userPreferences.value, ...newPreferences }
    await saveUserPreferences(userPreferences.value)
    
    // Apply changes
    if ('theme' in newPreferences) {
      applyTheme()
    }
  }

  const addError = (error: AppError) => {
    errors.value.push(error)
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      removeError(error.id)
    }, 5000)
  }

  const removeError = (errorId: string) => {
    const index = errors.value.findIndex(error => error.id === errorId)
    if (index > -1) {
      errors.value.splice(index, 1)
    }
  }

  const clearErrors = () => {
    errors.value = []
  }

  const applyTheme = () => {
    const isDark = isDarkMode.value
    document.documentElement.classList.toggle('dark', isDark)
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light')
  }

  // Helper functions
  const loadConfig = async (): Promise<AppConfig> => {
    // Load from API or environment
    return {
      apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000',
      wsUrl: import.meta.env.VITE_WS_URL || 'ws://localhost:8080',
      version: import.meta.env.VITE_APP_VERSION || '1.0.0',
      environment: import.meta.env.MODE
    }
  }

  const loadUserPreferences = async (): Promise<void> => {
    const stored = localStorage.getItem('userPreferences')
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        userPreferences.value = { ...userPreferences.value, ...parsed }
      } catch (error) {
        console.warn('Failed to parse stored preferences:', error)
      }
    }
  }

  const saveUserPreferences = async (preferences: UserPreferences): Promise<void> => {
    localStorage.setItem('userPreferences', JSON.stringify(preferences))
  }

  const getSystemInfo = async (): Promise<SystemInfo> => {
    return {
      userAgent: navigator.userAgent,
      platform: navigator.platform,
      language: navigator.language,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight
      }
    }
  }

  return {
    // State
    isLoading,
    loadingMessage,
    config,
    userPreferences,
    systemInfo,
    errors,
    
    // Getters
    isDarkMode,
    hasErrors,
    
    // Actions
    initialize,
    setLoading,
    updatePreferences,
    addError,
    removeError,
    clearErrors
  }
})
```

### **Conversations Store**

```typescript
// src/stores/conversations.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Conversation, Message, ConversationFilter } from '@/types/conversation'
import { conversationApi } from '@/services/api'

export const useConversationsStore = defineStore('conversations', () => {
  // State
  const conversations = ref<Map<string, Conversation>>(new Map())
  const messages = ref<Map<string, Message[]>>(new Map())
  const currentConversationId = ref<string | null>(null)
  const searchQuery = ref('')
  const filter = ref<ConversationFilter>({
    projectId: null,
    status: null,
    dateRange: null,
    messageType: null
  })
  const isLoading = ref(false)
  const pagination = ref({
    page: 1,
    limit: 50,
    total: 0
  })

  // Getters
  const currentConversation = computed(() => {
    return currentConversationId.value ? 
      conversations.value.get(currentConversationId.value) : null
  })

  const currentMessages = computed(() => {
    return currentConversationId.value ? 
      messages.value.get(currentConversationId.value) || [] : []
  })

  const filteredConversations = computed(() => {
    let result = Array.from(conversations.value.values())

    // Apply search filter
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      result = result.filter(conv => 
        conv.sessionId.toLowerCase().includes(query) ||
        conv.projectName?.toLowerCase().includes(query)
      )
    }

    // Apply status filter
    if (filter.value.status) {
      result = result.filter(conv => conv.status === filter.value.status)
    }

    // Apply project filter
    if (filter.value.projectId) {
      result = result.filter(conv => conv.projectId === filter.value.projectId)
    }

    // Apply date range filter
    if (filter.value.dateRange) {
      const { start, end } = filter.value.dateRange
      result = result.filter(conv => 
        conv.startTime >= start && conv.startTime <= end
      )
    }

    // Sort by start time (newest first)
    return result.sort((a, b) => b.startTime - a.startTime)
  })

  const conversationStats = computed(() => {
    const all = Array.from(conversations.value.values())
    return {
      total: all.length,
      active: all.filter(c => c.status === 'active').length,
      completed: all.filter(c => c.status === 'completed').length,
      error: all.filter(c => c.status === 'error').length
    }
  })

  // Actions
  const loadConversations = async (projectId?: number) => {
    isLoading.value = true
    
    try {
      const response = await conversationApi.getConversations({
        projectId,
        page: pagination.value.page,
        limit: pagination.value.limit
      })

      response.conversations.forEach(conv => {
        conversations.value.set(conv.id, conv)
      })

      pagination.value.total = response.total
      
    } catch (error) {
      console.error('Failed to load conversations:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const loadMessages = async (conversationId: string) => {
    if (messages.value.has(conversationId)) {
      return messages.value.get(conversationId)!
    }

    isLoading.value = true
    
    try {
      const response = await conversationApi.getMessages(conversationId)
      messages.value.set(conversationId, response.messages)
      return response.messages
      
    } catch (error) {
      console.error('Failed to load messages:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const setCurrentConversation = async (conversationId: string | null) => {
    currentConversationId.value = conversationId
    
    if (conversationId && !messages.value.has(conversationId)) {
      await loadMessages(conversationId)
    }
  }

  const addMessage = (conversationId: string, message: Message) => {
    const conversation = conversations.value.get(conversationId)
    if (conversation) {
      // Update conversation stats
      conversation.messageCount++
      conversation.lastActivity = message.timestamp
      
      // Add message to list
      const conversationMessages = messages.value.get(conversationId) || []
      conversationMessages.push(message)
      messages.value.set(conversationId, conversationMessages)
      
      // Update conversation in map
      conversations.value.set(conversationId, conversation)
    }
  }

  const updateConversation = (conversation: Conversation) => {
    conversations.value.set(conversation.id, conversation)
  }

  const addConversation = (conversation: Conversation) => {
    conversations.value.set(conversation.id, conversation)
    messages.value.set(conversation.id, [])
  }

  const setSearchQuery = (query: string) => {
    searchQuery.value = query
  }

  const setFilter = (newFilter: Partial<ConversationFilter>) => {
    filter.value = { ...filter.value, ...newFilter }
  }

  const clearFilter = () => {
    filter.value = {
      projectId: null,
      status: null,
      dateRange: null,
      messageType: null
    }
    searchQuery.value = ''
  }

  const searchMessages = async (query: string) => {
    try {
      const response = await conversationApi.searchMessages(query)
      return response.results
    } catch (error) {
      console.error('Failed to search messages:', error)
      throw error
    }
  }

  return {
    // State
    conversations,
    messages,
    currentConversationId,
    searchQuery,
    filter,
    isLoading,
    pagination,
    
    // Getters
    currentConversation,
    currentMessages,
    filteredConversations,
    conversationStats,
    
    // Actions
    loadConversations,
    loadMessages,
    setCurrentConversation,
    addMessage,
    updateConversation,
    addConversation,
    setSearchQuery,
    setFilter,
    clearFilter,
    searchMessages
  }
})
```

---

## 🔌 **WebSocket Integration**

### **WebSocket Composable**

```typescript
// src/composables/useWebSocket.ts
import { ref, onMounted, onUnmounted } from 'vue'
import { useWebSocketStore } from '@/stores/websocket'
import { useConversationsStore } from '@/stores/conversations'
import { useProjectsStore } from '@/stores/projects'
import { useNotifications } from '@/composables/useNotifications'
import type { WebSocketEvent, SubscriptionFilters } from '@/types/websocket'

export function useWebSocket() {
  const websocketStore = useWebSocketStore()
  const conversationsStore = useConversationsStore()
  const projectsStore = useProjectsStore()
  const notifications = useNotifications()

  const isConnected = ref(false)
  const reconnectAttempts = ref(0)
  const lastError = ref<string | null>(null)

  // Event handlers
  const handleConnectionEstablished = (data: any) => {
    isConnected.value = true
    reconnectAttempts.value = 0
    lastError.value = null
    
    notifications.success('Connected to Claude Code Observatory')
    
    // Subscribe to relevant events
    setupSubscriptions()
  }

  const handleDisconnected = (data: any) => {
    isConnected.value = false
    notifications.warning('Connection lost. Attempting to reconnect...')
  }

  const handleReconnecting = (data: any) => {
    reconnectAttempts.value = data.attempt
    notifications.info(`Reconnecting... (attempt ${data.attempt})`)
  }

  const handleMessageAdded = (data: any) => {
    const { conversationId, message, projectInfo } = data
    
    // Add message to store
    conversationsStore.addMessage(conversationId, message)
    
    // Show notification for new user messages
    if (message.type === 'user') {
      notifications.info(`New message in ${projectInfo.name}`, {
        action: () => navigateToConversation(conversationId)
      })
    }
  }

  const handleConversationStarted = (data: any) => {
    const { conversationId, sessionId, projectId, projectName, startTime } = data
    
    // Add conversation to store
    conversationsStore.addConversation({
      id: conversationId,
      sessionId,
      projectId,
      projectName,
      startTime,
      status: 'active',
      messageCount: 0,
      toolUsageCount: 0
    })
    
    notifications.success(`New conversation started in ${projectName}`)
  }

  const handleConversationEnded = (data: any) => {
    const { conversationId, duration, messageCount } = data
    
    // Update conversation status
    const conversation = conversationsStore.conversations.get(conversationId)
    if (conversation) {
      conversation.status = 'completed'
      conversation.endTime = Date.now()
      conversation.messageCount = messageCount
      conversationsStore.updateConversation(conversation)
    }
  }

  const handleProjectDiscovered = (data: any) => {
    const { project, conversationCount, lastActivity } = data
    
    // Add project to store
    projectsStore.addProject({
      ...project,
      conversationCount,
      lastActivity
    })
    
    notifications.info(`New project discovered: ${project.name}`)
  }

  const handleAnalyticsUpdate = (data: any) => {
    // Update analytics data
    // This could trigger chart updates, etc.
  }

  const handleError = (data: any) => {
    lastError.value = data.message
    notifications.error(`WebSocket error: ${data.message}`)
  }

  // Setup event listeners
  const setupEventListeners = () => {
    websocketStore.client?.on('connection_established', handleConnectionEstablished)
    websocketStore.client?.on('disconnected', handleDisconnected)
    websocketStore.client?.on('reconnecting', handleReconnecting)
    websocketStore.client?.on('message_added', handleMessageAdded)
    websocketStore.client?.on('conversation_started', handleConversationStarted)
    websocketStore.client?.on('conversation_ended', handleConversationEnded)
    websocketStore.client?.on('project_discovered', handleProjectDiscovered)
    websocketStore.client?.on('analytics_update', handleAnalyticsUpdate)
    websocketStore.client?.on('error', handleError)
  }

  // Setup subscriptions based on current context
  const setupSubscriptions = () => {
    const filters: SubscriptionFilters = {
      eventTypes: [
        'message_added',
        'conversation_started',
        'conversation_ended',
        'project_discovered',
        'project_updated',
        'analytics_update'
      ]
    }

    // Add project filter if specific project is selected
    const currentProjectId = projectsStore.currentProjectId
    if (currentProjectId) {
      filters.projectIds = [currentProjectId]
    }

    websocketStore.subscribe(filters)
  }

  // Subscribe to specific events
  const subscribe = (filters: SubscriptionFilters) => {
    websocketStore.subscribe(filters)
  }

  const unsubscribe = (filters?: SubscriptionFilters) => {
    websocketStore.unsubscribe(filters)
  }

  // Navigation helper
  const navigateToConversation = (conversationId: string) => {
    // This would use router to navigate
    // router.push(`/conversations/${conversationId}`)
  }

  // Lifecycle
  onMounted(() => {
    setupEventListeners()
  })

  onUnmounted(() => {
    // Cleanup listeners if needed
  })

  return {
    isConnected,
    reconnectAttempts,
    lastError,
    subscribe,
    unsubscribe,
    setupSubscriptions
  }
}
```

---

## 🎨 **Component Library**

### **Conversation Viewer Component**

```vue
<!-- src/components/conversation/ConversationViewer.vue -->
<template>
  <div class="conversation-viewer h-full flex flex-col">
    <!-- Header -->
    <div class="flex-shrink-0 border-b border-gray-200 dark:border-gray-700 p-4">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
            {{ conversation?.sessionId || 'Loading...' }}
          </h2>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            {{ conversation?.projectName }} • 
            {{ formatDate(conversation?.startTime) }} •
            {{ conversation?.messageCount }} messages
          </p>
        </div>
        
        <div class="flex items-center space-x-2">
          <!-- Export button -->
          <button
            @click="exportConversation"
            class="btn btn-secondary btn-sm"
            :disabled="!conversation"
            title="Export conversation"
          >
            <IconDownload class="w-4 h-4" />
          </button>
          
          <!-- Share button -->
          <button
            @click="shareConversation"
            class="btn btn-secondary btn-sm"
            :disabled="!conversation"
            title="Share conversation"
          >
            <IconShare class="w-4 h-4" />
          </button>
          
          <!-- Settings -->
          <button
            @click="showSettings = true"
            class="btn btn-secondary btn-sm"
            title="View settings"
          >
            <IconSettings class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Messages container -->
    <div
      ref="messagesContainer"
      class="flex-1 overflow-y-auto p-4 space-y-4"
      @scroll="handleScroll"
    >
      <!-- Loading skeleton -->
      <div v-if="isLoading" class="space-y-4">
        <MessageSkeleton v-for="i in 5" :key="i" />
      </div>

      <!-- Messages -->
      <div v-else-if="messages.length > 0" class="space-y-4">
        <MessageDisplay
          v-for="message in messages"
          :key="message.id"
          :message="message"
          :show-timestamp="showTimestamps"
          :compact="compactMode"
          @copy="copyMessage"
          @expand="expandMessage"
        />
      </div>

      <!-- Empty state -->
      <div v-else class="flex flex-col items-center justify-center h-full text-gray-500">
        <IconMessageCircle class="w-16 h-16 mb-4" />
        <h3 class="text-lg font-medium mb-2">No messages yet</h3>
        <p class="text-sm">This conversation hasn't started yet.</p>
      </div>
    </div>

    <!-- Live indicator -->
    <div
      v-if="isLive"
      class="flex-shrink-0 bg-green-50 dark:bg-green-900/20 border-t border-green-200 dark:border-green-800 p-3"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span class="text-sm text-green-700 dark:text-green-400 font-medium">
            Live conversation
          </span>
        </div>
        
        <button
          @click="scrollToBottom"
          class="text-sm text-green-600 dark:text-green-400 hover:underline"
        >
          Stay at bottom
        </button>
      </div>
    </div>

    <!-- Settings modal -->
    <Modal v-model="showSettings" title="Conversation Settings">
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <label class="text-sm font-medium">Show timestamps</label>
          <Toggle v-model="showTimestamps" />
        </div>
        
        <div class="flex items-center justify-between">
          <label class="text-sm font-medium">Compact mode</label>
          <Toggle v-model="compactMode" />
        </div>
        
        <div class="flex items-center justify-between">
          <label class="text-sm font-medium">Auto-scroll</label>
          <Toggle v-model="autoScroll" />
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useConversationsStore } from '@/stores/conversations'
import { useWebSocket } from '@/composables/useWebSocket'
import { useClipboard } from '@/composables/useClipboard'
import { useNotifications } from '@/composables/useNotifications'

// Components
import MessageDisplay from './MessageDisplay.vue'
import MessageSkeleton from './MessageSkeleton.vue'
import Modal from '@/components/common/Modal.vue'
import Toggle from '@/components/common/Toggle.vue'

// Icons
import IconDownload from '@/components/icons/IconDownload.vue'
import IconShare from '@/components/icons/IconShare.vue'
import IconSettings from '@/components/icons/IconSettings.vue'
import IconMessageCircle from '@/components/icons/IconMessageCircle.vue'

interface Props {
  conversationId: string
}

const props = defineProps<Props>()

// Stores and composables
const conversationsStore = useConversationsStore()
const { subscribe, unsubscribe } = useWebSocket()
const { copy } = useClipboard()
const notifications = useNotifications()

// Reactive refs
const messagesContainer = ref<HTMLElement>()
const showSettings = ref(false)
const showTimestamps = ref(true)
const compactMode = ref(false)
const autoScroll = ref(true)
const isAtBottom = ref(true)

// Store state
const { isLoading } = storeToRefs(conversationsStore)

// Computed properties
const conversation = computed(() => 
  conversationsStore.conversations.get(props.conversationId)
)

const messages = computed(() => 
  conversationsStore.messages.get(props.conversationId) || []
)

const isLive = computed(() => 
  conversation.value?.status === 'active'
)

// Methods
const handleScroll = () => {
  if (!messagesContainer.value) return
  
  const { scrollTop, scrollHeight, clientHeight } = messagesContainer.value
  isAtBottom.value = scrollTop + clientHeight >= scrollHeight - 10
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const copyMessage = (message: any) => {
  copy(message.content)
  notifications.success('Message copied to clipboard')
}

const expandMessage = (message: any) => {
  // Implement message expansion logic
}

const exportConversation = () => {
  if (!conversation.value) return
  
  const data = {
    conversation: conversation.value,
    messages: messages.value
  }
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { 
    type: 'application/json' 
  })
  
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `conversation-${conversation.value.sessionId}.json`
  a.click()
  
  URL.revokeObjectURL(url)
}

const shareConversation = async () => {
  if (!conversation.value) return
  
  try {
    const url = `${window.location.origin}/conversations/${conversation.value.id}`
    
    if (navigator.share) {
      await navigator.share({
        title: `Conversation ${conversation.value.sessionId}`,
        url
      })
    } else {
      await copy(url)
      notifications.success('Conversation link copied to clipboard')
    }
  } catch (error) {
    console.error('Failed to share conversation:', error)
  }
}

const formatDate = (timestamp?: number) => {
  if (!timestamp) return ''
  return new Date(timestamp).toLocaleString()
}

// Watchers
watch(() => props.conversationId, async (newId) => {
  if (newId) {
    await conversationsStore.setCurrentConversation(newId)
  }
}, { immediate: true })

watch(messages, async () => {
  if (autoScroll.value && isAtBottom.value) {
    await scrollToBottom()
  }
}, { flush: 'post' })

// Lifecycle
onMounted(() => {
  // Subscribe to live updates for this conversation
  subscribe({
    eventTypes: ['message_added'],
    sessionIds: [conversation.value?.sessionId].filter(Boolean)
  })
})

onUnmounted(() => {
  // Cleanup subscription
  unsubscribe()
})
</script>

<style scoped>
.conversation-viewer {
  @apply bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700;
}

.btn {
  @apply inline-flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors;
}

.btn-secondary {
  @apply text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600;
}

.btn-sm {
  @apply px-2 py-1 text-xs;
}

.btn:disabled {
  @apply opacity-50 cursor-not-allowed;
}
</style>
```

---

## 📊 **Performance Optimization**

### **Virtual Scrolling for Large Lists**

```typescript
// src/composables/useVirtualScrolling.ts
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface VirtualScrollOptions {
  itemHeight: number
  containerHeight: number
  overscan: number
}

export function useVirtualScrolling<T>(
  items: Ref<T[]>,
  options: VirtualScrollOptions
) {
  const scrollTop = ref(0)
  const containerRef = ref<HTMLElement>()
  
  const { itemHeight, containerHeight, overscan } = options
  
  // Calculate visible range
  const visibleRange = computed(() => {
    const start = Math.floor(scrollTop.value / itemHeight)
    const end = Math.min(
      start + Math.ceil(containerHeight / itemHeight),
      items.value.length
    )
    
    return {
      start: Math.max(0, start - overscan),
      end: Math.min(items.value.length, end + overscan)
    }
  })
  
  // Get visible items
  const visibleItems = computed(() => {
    const { start, end } = visibleRange.value
    return items.value.slice(start, end).map((item, index) => ({
      item,
      index: start + index
    }))
  })
  
  // Calculate total height and offset
  const totalHeight = computed(() => items.value.length * itemHeight)
  const offsetY = computed(() => visibleRange.value.start * itemHeight)
  
  const handleScroll = (event: Event) => {
    const target = event.target as HTMLElement
    scrollTop.value = target.scrollTop
  }
  
  onMounted(() => {
    containerRef.value?.addEventListener('scroll', handleScroll, { passive: true })
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

### **Performance Monitoring**

```typescript
// src/utils/performance.ts
interface PerformanceMetrics {
  renderTime: number
  componentCount: number
  memoryUsage: number
  bundleSize: number
}

class PerformanceMonitor {
  private metrics: PerformanceMetrics = {
    renderTime: 0,
    componentCount: 0,
    memoryUsage: 0,
    bundleSize: 0
  }

  startRenderMeasurement(name: string): void {
    performance.mark(`${name}-start`)
  }

  endRenderMeasurement(name: string): number {
    performance.mark(`${name}-end`)
    performance.measure(name, `${name}-start`, `${name}-end`)
    
    const entries = performance.getEntriesByName(name)
    const duration = entries[entries.length - 1]?.duration || 0
    
    this.metrics.renderTime = duration
    return duration
  }

  measureMemoryUsage(): number {
    if ('memory' in performance) {
      const memory = (performance as any).memory
      this.metrics.memoryUsage = memory.usedJSHeapSize / 1024 / 1024 // MB
      return this.metrics.memoryUsage
    }
    return 0
  }

  reportWebVitals(): void {
    // Core Web Vitals
    new PerformanceObserver((entryList) => {
      for (const entry of entryList.getEntries()) {
        if (entry.entryType === 'largest-contentful-paint') {
          console.log('LCP:', entry.startTime)
        }
        if (entry.entryType === 'first-input') {
          console.log('FID:', entry.processingStart - entry.startTime)
        }
        if (entry.entryType === 'layout-shift') {
          console.log('CLS:', entry.value)
        }
      }
    }).observe({ entryTypes: ['largest-contentful-paint', 'first-input', 'layout-shift'] })
  }

  getMetrics(): PerformanceMetrics {
    return { ...this.metrics }
  }
}

export const performanceMonitor = new PerformanceMonitor()

export function setupPerformanceMonitoring(app: any): void {
  // Component performance tracking
  app.config.performance = true
  
  // Measure app initialization
  performanceMonitor.startRenderMeasurement('app-init')
  
  app.mixin({
    beforeCreate() {
      performanceMonitor.startRenderMeasurement(`component-${this.$options.name || 'anonymous'}`)
    },
    mounted() {
      const componentName = this.$options.name || 'anonymous'
      const duration = performanceMonitor.endRenderMeasurement(`component-${componentName}`)
      
      if (duration > 100) {
        console.warn(`Slow component render: ${componentName} took ${duration.toFixed(2)}ms`)
      }
    }
  })
  
  // Report web vitals
  performanceMonitor.reportWebVitals()
  
  // Memory monitoring
  setInterval(() => {
    const memoryUsage = performanceMonitor.measureMemoryUsage()
    if (memoryUsage > 100) { // 100MB threshold
      console.warn(`High memory usage: ${memoryUsage.toFixed(2)}MB`)
    }
  }, 30000) // Every 30 seconds
}
```

---

## 🧪 **Testing Strategy**

### **Component Testing with Vue Test Utils**

```typescript
// src/components/conversation/__tests__/ConversationViewer.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ConversationViewer from '../ConversationViewer.vue'
import { useConversationsStore } from '@/stores/conversations'

// Mock WebSocket composable
vi.mock('@/composables/useWebSocket', () => ({
  useWebSocket: () => ({
    subscribe: vi.fn(),
    unsubscribe: vi.fn()
  })
}))

describe('ConversationViewer', () => {
  let wrapper: any
  let conversationsStore: any

  beforeEach(() => {
    setActivePinia(createPinia())
    conversationsStore = useConversationsStore()
    
    // Mock conversation data
    const mockConversation = {
      id: 'conv-1',
      sessionId: 'session-123',
      projectId: 1,
      projectName: 'Test Project',
      startTime: Date.now(),
      status: 'active',
      messageCount: 3
    }
    
    const mockMessages = [
      {
        id: 'msg-1',
        type: 'user',
        content: 'Hello',
        timestamp: Date.now() - 1000
      },
      {
        id: 'msg-2',
        type: 'assistant',
        content: 'Hi there!',
        timestamp: Date.now() - 500
      },
      {
        id: 'msg-3',
        type: 'user',
        content: 'How are you?',
        timestamp: Date.now()
      }
    ]
    
    conversationsStore.conversations.set('conv-1', mockConversation)
    conversationsStore.messages.set('conv-1', mockMessages)
  })

  it('renders conversation header correctly', () => {
    wrapper = mount(ConversationViewer, {
      props: { conversationId: 'conv-1' }
    })
    
    expect(wrapper.find('h2').text()).toBe('session-123')
    expect(wrapper.text()).toContain('Test Project')
    expect(wrapper.text()).toContain('3 messages')
  })

  it('displays messages in correct order', () => {
    wrapper = mount(ConversationViewer, {
      props: { conversationId: 'conv-1' }
    })
    
    const messageComponents = wrapper.findAllComponents({ name: 'MessageDisplay' })
    expect(messageComponents).toHaveLength(3)
  })

  it('shows live indicator for active conversations', () => {
    wrapper = mount(ConversationViewer, {
      props: { conversationId: 'conv-1' }
    })
    
    expect(wrapper.find('.animate-pulse').exists()).toBe(true)
    expect(wrapper.text()).toContain('Live conversation')
  })

  it('handles message copying', async () => {
    const mockCopy = vi.fn()
    vi.mock('@/composables/useClipboard', () => ({
      useClipboard: () => ({ copy: mockCopy })
    }))
    
    wrapper = mount(ConversationViewer, {
      props: { conversationId: 'conv-1' }
    })
    
    const messageComponent = wrapper.findComponent({ name: 'MessageDisplay' })
    await messageComponent.vm.$emit('copy', { content: 'Hello' })
    
    expect(mockCopy).toHaveBeenCalledWith('Hello')
  })

  it('exports conversation data', async () => {
    // Mock URL.createObjectURL
    const mockCreateObjectURL = vi.fn(() => 'blob:url')
    global.URL.createObjectURL = mockCreateObjectURL
    global.URL.revokeObjectURL = vi.fn()
    
    // Mock createElement and click
    const mockClick = vi.fn()
    const mockElement = { href: '', download: '', click: mockClick }
    document.createElement = vi.fn(() => mockElement as any)
    
    wrapper = mount(ConversationViewer, {
      props: { conversationId: 'conv-1' }
    })
    
    const exportButton = wrapper.find('[title="Export conversation"]')
    await exportButton.trigger('click')
    
    expect(mockCreateObjectURL).toHaveBeenCalled()
    expect(mockClick).toHaveBeenCalled()
    expect(mockElement.download).toBe('conversation-session-123.json')
  })

  it('handles empty state correctly', () => {
    // Clear messages
    conversationsStore.messages.set('conv-1', [])
    
    wrapper = mount(ConversationViewer, {
      props: { conversationId: 'conv-1' }
    })
    
    expect(wrapper.text()).toContain('No messages yet')
  })

  it('handles loading state', () => {
    conversationsStore.isLoading = true
    
    wrapper = mount(ConversationViewer, {
      props: { conversationId: 'conv-1' }
    })
    
    expect(wrapper.findAllComponents({ name: 'MessageSkeleton' })).toHaveLength(5)
  })
})
```

### **E2E Testing with Playwright**

```typescript
// tests/e2e/conversation-viewer.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Conversation Viewer', () => {
  test.beforeEach(async ({ page }) => {
    // Setup test data
    await page.goto('/test-setup')
    await page.click('[data-testid="create-test-data"]')
    await page.waitForSelector('[data-testid="test-data-ready"]')
    
    // Navigate to conversation
    await page.goto('/conversations/test-conversation-1')
  })

  test('displays conversation messages correctly', async ({ page }) => {
    await expect(page.locator('[data-testid="conversation-header"]')).toBeVisible()
    await expect(page.locator('[data-testid="message"]')).toHaveCount(3)
    
    // Check message order
    const messages = page.locator('[data-testid="message"]')
    await expect(messages.first()).toContainText('Hello')
    await expect(messages.nth(1)).toContainText('Hi there!')
    await expect(messages.last()).toContainText('How are you?')
  })

  test('handles real-time message updates', async ({ page }) => {
    // Simulate WebSocket message
    await page.evaluate(() => {
      window.mockWebSocket.emit('message_added', {
        conversationId: 'test-conversation-1',
        message: {
          id: 'msg-4',
          type: 'assistant',
          content: 'I am fine, thank you!',
          timestamp: Date.now()
        }
      })
    })
    
    // Wait for new message to appear
    await expect(page.locator('[data-testid="message"]')).toHaveCount(4)
    await expect(page.locator('[data-testid="message"]').last()).toContainText('I am fine, thank you!')
  })

  test('exports conversation successfully', async ({ page }) => {
    // Start download
    const downloadPromise = page.waitForEvent('download')
    await page.click('[data-testid="export-button"]')
    const download = await downloadPromise
    
    // Verify download
    expect(download.suggestedFilename()).toMatch(/conversation-.*\.json/)
    
    // Save and verify content
    const path = await download.path()
    const fs = require('fs')
    const content = JSON.parse(fs.readFileSync(path, 'utf8'))
    
    expect(content.conversation).toBeDefined()
    expect(content.messages).toBeDefined()
    expect(content.messages).toHaveLength(3)
  })

  test('handles keyboard navigation', async ({ page }) => {
    // Focus conversation viewer
    await page.click('[data-testid="conversation-viewer"]')
    
    // Test keyboard shortcuts
    await page.keyboard.press('ArrowDown')
    await expect(page.locator('[data-testid="message"].focused')).toBeVisible()
    
    await page.keyboard.press('ArrowUp')
    await page.keyboard.press('Enter')
    // Should expand message or show details
  })

  test('maintains performance under load', async ({ page }) => {
    // Create large conversation
    await page.goto('/test-setup')
    await page.click('[data-testid="create-large-conversation"]')
    await page.waitForSelector('[data-testid="large-conversation-ready"]')
    
    await page.goto('/conversations/large-conversation')
    
    // Measure load time
    const startTime = Date.now()
    await page.waitForSelector('[data-testid="conversation-viewer"]')
    const loadTime = Date.now() - startTime
    
    expect(loadTime).toBeLessThan(3000) // 3 second max
    
    // Test scroll performance
    const metrics = await page.evaluate(() => {
      const start = performance.now()
      document.querySelector('[data-testid="messages-container"]')?.scrollTo(0, 10000)
      return performance.now() - start
    })
    
    expect(metrics).toBeLessThan(100) // 100ms max for scroll
  })
})
```

---

## 🚀 **Build and Deployment**

### **Vite Configuration**

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { visualizer } from 'rollup-plugin-visualizer'

export default defineConfig({
  plugins: [
    vue(),
    visualizer({
      filename: 'dist/bundle-analysis.html',
      open: false,
      gzipSize: true
    })
  ],
  
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  
  build: {
    target: 'es2020',
    outDir: 'dist',
    sourcemap: process.env.NODE_ENV === 'development',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: process.env.NODE_ENV === 'production',
        drop_debugger: true
      }
    },
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
          ui: ['vuestic-ui'],
          charts: ['chart.js', 'vue-chartjs']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  },
  
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', 'chart.js']
  },
  
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/ws': {
        target: 'ws://localhost:8080',
        ws: true
      }
    }
  },
  
  define: {
    __VUE_OPTIONS_API__: false,
    __VUE_PROD_DEVTOOLS__: false
  }
})
```

### **Deployment Configuration**

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

# Expose port
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

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
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
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Referrer-Policy strict-origin-when-cross-origin;

        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # API proxy
        location /api/ {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # WebSocket proxy
        location /ws {
            proxy_pass http://websocket:8080;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }

        # Fallback to index.html for SPA routing
        location / {
            try_files $uri $uri/ /index.html;
        }
    }
}
```

This comprehensive frontend architecture specification provides a solid foundation for building a modern, performant, and maintainable Vue 3 application for the Claude Code Observatory project.