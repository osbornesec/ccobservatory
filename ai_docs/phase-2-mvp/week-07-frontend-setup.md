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

## Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari 14+, Chrome Mobile 90+)