# Week 8: Core UI Components & Conversation Viewer

## Overview
Develop the core user interface components for the Claude Code Observatory, focusing on conversation viewing, message display, real-time interactions, and reusable UI elements. This week emphasizes creating a polished, accessible, and performant user experience.

## Team Assignments
- **Frontend Lead**: Core conversation components, message rendering, real-time UI
- **UI/UX Developer**: Design system implementation, responsive layouts, accessibility
- **Full-Stack Developer**: API integration, state management, performance optimization

## Daily Schedule

### Monday: Base Component Library
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Design system tokens and base components
- **10:30-12:00**: Button, input, and form component variants

#### Afternoon (4 hours)
- **13:00-15:00**: Layout components (containers, grids, cards)
- **15:00-17:00**: Navigation and menu components

### Tuesday: Conversation List & Navigation
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Conversation list component with virtual scrolling
- **10:30-12:00**: Search and filtering functionality

#### Afternoon (4 hours)
- **13:00-15:00**: Conversation metadata display and sorting
- **15:00-17:00**: Context menus and bulk actions

### Wednesday: Message Display & Rendering
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Message component with role-based styling
- **10:30-12:00**: Code syntax highlighting and formatting

#### Afternoon (4 hours)
- **13:00-15:00**: Message timestamps, metadata, and status indicators
- **15:00-17:00**: Message selection and copying functionality

### Thursday: Real-Time Features & Interactions
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Typing indicators and presence display
- **10:30-12:00**: Real-time message updates and animations

#### Afternoon (4 hours)
- **13:00-15:00**: Message reactions and interactions
- **15:00-17:00**: Collaborative features UI (shared cursors, live updates)

### Friday: Performance & Accessibility
**Hours: 8 hours**

#### Morning (4 hours)
- **9:00-10:30**: Virtual scrolling optimization for large conversations
- **10:30-12:00**: Lazy loading and code splitting

#### Afternoon (4 hours)
- **13:00-15:00**: Accessibility improvements (ARIA, keyboard navigation)
- **15:00-17:00**: Component testing and documentation

## Technical Implementation Details

### Design System Foundation
```typescript
// src/tokens/design-tokens.ts
export const designTokens = {
  colors: {
    primary: {
      50: '#f0f9ff',
      100: '#e0f2fe',
      500: '#0ea5e9',
      600: '#0284c7',
      700: '#0369a1',
      900: '#0c4a6e',
    },
    semantic: {
      success: '#22c55e',
      warning: '#f59e0b',
      error: '#ef4444',
      info: '#3b82f6',
    },
    neutral: {
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
    }
  },
  
  typography: {
    fontFamily: {
      sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
    },
    fontSize: {
      xs: ['0.75rem', { lineHeight: '1rem' }],
      sm: ['0.875rem', { lineHeight: '1.25rem' }],
      base: ['1rem', { lineHeight: '1.5rem' }],
      lg: ['1.125rem', { lineHeight: '1.75rem' }],
      xl: ['1.25rem', { lineHeight: '1.75rem' }],
      '2xl': ['1.5rem', { lineHeight: '2rem' }],
    }
  },
  
  spacing: {
    0: '0px',
    1: '0.25rem',
    2: '0.5rem',
    3: '0.75rem',
    4: '1rem',
    5: '1.25rem',
    6: '1.5rem',
    8: '2rem',
    10: '2.5rem',
    12: '3rem',
    16: '4rem',
  },
  
  borderRadius: {
    none: '0px',
    sm: '0.125rem',
    DEFAULT: '0.25rem',
    md: '0.375rem',
    lg: '0.5rem',
    xl: '0.75rem',
    full: '9999px',
  },
  
  shadows: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    DEFAULT: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  }
} as const
```

### Base Button Component
```vue
<!-- src/components/base/BaseButton.vue -->
<template>
  <component
    :is="tag"
    :type="tag === 'button' ? type : undefined"
    :disabled="disabled || loading"
    :class="buttonClasses"
    @click="handleClick"
  >
    <LoadingSpinner v-if="loading" :size="spinnerSize" class="mr-2" />
    <slot name="icon-left" />
    <span v-if="$slots.default" :class="{ 'sr-only': iconOnly }">
      <slot />
    </span>
    <slot name="icon-right" />
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import LoadingSpinner from './LoadingSpinner.vue'

type ButtonVariant = 'primary' | 'secondary' | 'tertiary' | 'danger' | 'ghost'
type ButtonSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl'
type ButtonType = 'button' | 'submit' | 'reset'

interface Props {
  variant?: ButtonVariant
  size?: ButtonSize
  type?: ButtonType
  tag?: 'button' | 'a' | 'router-link'
  disabled?: boolean
  loading?: boolean
  iconOnly?: boolean
  fullWidth?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  type: 'button',
  tag: 'button',
  disabled: false,
  loading: false,
  iconOnly: false,
  fullWidth: false
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const buttonClasses = computed(() => {
  const baseClasses = [
    'inline-flex items-center justify-center font-medium transition-all duration-200',
    'focus:outline-none focus:ring-2 focus:ring-offset-2',
    'disabled:opacity-50 disabled:cursor-not-allowed'
  ]
  
  // Size classes
  const sizeClasses = {
    xs: 'px-2 py-1 text-xs rounded-md',
    sm: 'px-3 py-1.5 text-sm rounded-md',
    md: 'px-4 py-2 text-sm rounded-lg',
    lg: 'px-6 py-3 text-base rounded-lg',
    xl: 'px-8 py-4 text-lg rounded-xl'
  }
  
  // Variant classes
  const variantClasses = {
    primary: [
      'bg-primary-600 text-white shadow-sm',
      'hover:bg-primary-700 focus:ring-primary-500',
      'active:bg-primary-800'
    ],
    secondary: [
      'bg-white text-gray-700 border border-gray-300 shadow-sm',
      'hover:bg-gray-50 focus:ring-primary-500',
      'active:bg-gray-100'
    ],
    tertiary: [
      'bg-gray-100 text-gray-700',
      'hover:bg-gray-200 focus:ring-primary-500',
      'active:bg-gray-300'
    ],
    danger: [
      'bg-red-600 text-white shadow-sm',
      'hover:bg-red-700 focus:ring-red-500',
      'active:bg-red-800'
    ],
    ghost: [
      'text-gray-700 hover:bg-gray-100',
      'focus:ring-primary-500 active:bg-gray-200'
    ]
  }
  
  const classes = [
    ...baseClasses,
    sizeClasses[props.size],
    ...variantClasses[props.variant]
  ]
  
  if (props.fullWidth) {
    classes.push('w-full')
  }
  
  if (props.iconOnly) {
    // Make button square for icon-only variant
    const iconOnlyClasses = {
      xs: 'w-6 h-6 p-1',
      sm: 'w-8 h-8 p-1.5',
      md: 'w-10 h-10 p-2',
      lg: 'w-12 h-12 p-3',
      xl: 'w-16 h-16 p-4'
    }
    classes.push(iconOnlyClasses[props.size])
  }
  
  return classes.join(' ')
})

const spinnerSize = computed(() => {
  const sizeMap = { xs: 'xs', sm: 'sm', md: 'sm', lg: 'md', xl: 'lg' }
  return sizeMap[props.size]
})

function handleClick(event: MouseEvent) {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>
```

### Conversation List Component
```vue
<!-- src/components/conversations/ConversationList.vue -->
<template>
  <div class="flex flex-col h-full">
    <!-- Header -->
    <div class="flex-shrink-0 p-4 border-b border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
          Conversations
        </h2>
        <BaseButton
          size="sm"
          @click="createNewConversation"
        >
          <PlusIcon class="w-4 h-4 mr-2" />
          New
        </BaseButton>
      </div>
      
      <!-- Search -->
      <div class="relative">
        <MagnifyingGlassIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search conversations..."
          class="w-full pl-10 pr-4 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
        />
      </div>
      
      <!-- Filters -->
      <div class="flex items-center gap-2 mt-3">
        <select
          v-model="sortBy"
          class="text-sm border border-gray-300 rounded-md px-3 py-1 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
        >
          <option value="updated_at">Recent</option>
          <option value="created_at">Created</option>
          <option value="title">Title</option>
          <option value="message_count">Messages</option>
        </select>
        
        <BaseButton
          variant="ghost"
          size="sm"
          :class="{ 'text-primary-600': sortOrder === 'desc' }"
          @click="toggleSortOrder"
        >
          <ArrowUpIcon v-if="sortOrder === 'asc'" class="w-4 h-4" />
          <ArrowDownIcon v-else class="w-4 h-4" />
        </BaseButton>
      </div>
    </div>
    
    <!-- Conversation List -->
    <div class="flex-1 overflow-hidden">
      <RecycleScroller
        v-if="filteredConversations.length > 0"
        class="h-full"
        :items="filteredConversations"
        :item-size="80"
        key-field="id"
        v-slot="{ item: conversation }"
      >
        <ConversationListItem
          :conversation="conversation"
          :is-active="activeConversationId === conversation.id"
          @click="selectConversation(conversation)"
          @delete="deleteConversation(conversation.id)"
        />
      </RecycleScroller>
      
      <!-- Empty State -->
      <div v-else class="flex flex-col items-center justify-center h-full p-6 text-center">
        <ChatBubbleLeftRightIcon class="w-12 h-12 text-gray-400 mb-4" />
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
          No conversations found
        </h3>
        <p class="text-gray-500 dark:text-gray-400 mb-4">
          {{ searchQuery ? 'Try adjusting your search criteria' : 'Start a new conversation to get started' }}
        </p>
        <BaseButton
          v-if="!searchQuery"
          @click="createNewConversation"
        >
          Create First Conversation
        </BaseButton>
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="isLoading" class="absolute inset-0 bg-white/50 dark:bg-gray-900/50 flex items-center justify-center">
      <LoadingSpinner size="lg" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { RecycleScroller } from 'vue-virtual-scroller'
import { 
  PlusIcon, 
  MagnifyingGlassIcon, 
  ArrowUpIcon, 
  ArrowDownIcon,
  ChatBubbleLeftRightIcon 
} from '@heroicons/vue/24/outline'
import { useConversationStore } from '@stores/conversations'
import { useWebSocketStore } from '@stores/websocket'
import ConversationListItem from './ConversationListItem.vue'
import BaseButton from '@components/base/BaseButton.vue'
import LoadingSpinner from '@components/base/LoadingSpinner.vue'
import type { Conversation } from '@types/conversation'

const router = useRouter()
const conversationStore = useConversationStore()
const webSocketStore = useWebSocketStore()

// Reactive state
const searchQuery = ref('')
const sortBy = ref<'updated_at' | 'created_at' | 'title' | 'message_count'>('updated_at')
const sortOrder = ref<'asc' | 'desc'>('desc')

// Computed properties
const filteredConversations = computed(() => {
  let conversations = [...conversationStore.conversations]
  
  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    conversations = conversations.filter(conv =>
      conv.title.toLowerCase().includes(query) ||
      conv.lastMessage?.content.toLowerCase().includes(query)
    )
  }
  
  // Sort conversations
  conversations.sort((a, b) => {
    let aValue: any, bValue: any
    
    switch (sortBy.value) {
      case 'title':
        aValue = a.title.toLowerCase()
        bValue = b.title.toLowerCase()
        break
      case 'message_count':
        aValue = a.messageCount || 0
        bValue = b.messageCount || 0
        break
      case 'created_at':
        aValue = new Date(a.createdAt)
        bValue = new Date(b.createdAt)
        break
      default:
        aValue = new Date(a.updatedAt)
        bValue = new Date(b.updatedAt)
    }
    
    if (sortOrder.value === 'asc') {
      return aValue < bValue ? -1 : aValue > bValue ? 1 : 0
    } else {
      return aValue > bValue ? -1 : aValue < bValue ? 1 : 0
    }
  })
  
  return conversations
})

const isLoading = computed(() => conversationStore.isLoading)
const activeConversationId = computed(() => conversationStore.activeConversationId)

// Methods
function selectConversation(conversation: Conversation) {
  router.push(`/conversations/${conversation.id}`)
}

function createNewConversation() {
  router.push('/conversations/new')
}

async function deleteConversation(id: string) {
  if (confirm('Are you sure you want to delete this conversation?')) {
    await conversationStore.deleteConversation(id)
  }
}

function toggleSortOrder() {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
}

// Lifecycle
onMounted(async () => {
  // Load conversations
  await conversationStore.fetchConversations()
  
  // Subscribe to real-time updates
  webSocketStore.on('conversation_updated', (data) => {
    conversationStore.updateConversation(data.conversation)
  })
  
  webSocketStore.on('new_conversation', (data) => {
    conversationStore.addConversation(data.conversation)
  })
})

// Watch for search changes and debounce
watch(searchQuery, async (newQuery) => {
  if (newQuery.length > 2) {
    await conversationStore.searchConversations(newQuery)
  }
}, { debounce: 300 })
</script>
```

### Message Component with Syntax Highlighting
```vue
<!-- src/components/messages/MessageItem.vue -->
<template>
  <div
    :class="messageClasses"
    :data-message-id="message.id"
  >
    <!-- Message Header -->
    <div class="flex items-start gap-3">
      <!-- Avatar -->
      <div class="flex-shrink-0">
        <div :class="avatarClasses">
          <UserIcon v-if="message.role === 'user'" class="w-4 h-4" />
          <CpuChipIcon v-else class="w-4 h-4" />
        </div>
      </div>
      
      <!-- Message Content -->
      <div class="flex-1 min-w-0">
        <!-- Role and Timestamp -->
        <div class="flex items-center gap-2 mb-2">
          <span :class="roleClasses">
            {{ roleDisplay }}
          </span>
          <span class="text-xs text-gray-500 dark:text-gray-400">
            {{ formatTimestamp(message.timestamp) }}
          </span>
          <MessageStatus :status="message.status" />
        </div>
        
        <!-- Message Content -->
        <div class="prose prose-sm dark:prose-invert max-w-none">
          <MessageContent
            :content="message.content"
            :type="message.contentType"
            @copy="handleCopy"
          />
        </div>
        
        <!-- Metadata -->
        <MessageMetadata
          v-if="showMetadata"
          :metadata="message.metadata"
          :token-count="message.tokenCount"
        />
      </div>
      
      <!-- Message Actions -->
      <MessageActions
        :message="message"
        @copy="handleCopy"
        @edit="handleEdit"
        @delete="handleDelete"
        @react="handleReact"
      />
    </div>
    
    <!-- Reactions -->
    <MessageReactions
      v-if="message.reactions && message.reactions.length > 0"
      :reactions="message.reactions"
      @add-reaction="handleReact"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { UserIcon, CpuChipIcon } from '@heroicons/vue/24/outline'
import MessageContent from './MessageContent.vue'
import MessageActions from './MessageActions.vue'
import MessageStatus from './MessageStatus.vue'
import MessageMetadata from './MessageMetadata.vue'
import MessageReactions from './MessageReactions.vue'
import { formatDistanceToNow } from 'date-fns'
import type { Message } from '@types/message'

interface Props {
  message: Message
  showMetadata?: boolean
  isSelectable?: boolean
  isSelected?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showMetadata: false,
  isSelectable: false,
  isSelected: false
})

const emit = defineEmits<{
  copy: [content: string]
  edit: [message: Message]
  delete: [messageId: string]
  react: [messageId: string, reaction: string]
  select: [messageId: string]
}>()

const messageClasses = computed(() => [
  'group relative p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors',
  {
    'bg-blue-50 dark:bg-blue-900/10': props.message.role === 'assistant',
    'border-l-4 border-blue-500': props.isSelected,
    'cursor-pointer': props.isSelectable
  }
])

const avatarClasses = computed(() => [
  'w-8 h-8 rounded-full flex items-center justify-center text-white font-medium text-sm',
  {
    'bg-blue-600': props.message.role === 'assistant',
    'bg-green-600': props.message.role === 'user',
    'bg-gray-600': props.message.role === 'system'
  }
])

const roleClasses = computed(() => [
  'text-sm font-medium',
  {
    'text-blue-600 dark:text-blue-400': props.message.role === 'assistant',
    'text-green-600 dark:text-green-400': props.message.role === 'user',
    'text-gray-600 dark:text-gray-400': props.message.role === 'system'
  }
])

const roleDisplay = computed(() => {
  const roles = {
    user: 'You',
    assistant: 'Claude',
    system: 'System'
  }
  return roles[props.message.role] || props.message.role
})

function formatTimestamp(timestamp: string): string {
  return formatDistanceToNow(new Date(timestamp), { addSuffix: true })
}

function handleCopy(content?: string) {
  emit('copy', content || props.message.content)
}

function handleEdit() {
  emit('edit', props.message)
}

function handleDelete() {
  emit('delete', props.message.id)
}

function handleReact(reaction: string) {
  emit('react', props.message.id, reaction)
}
</script>
```

### Message Content with Syntax Highlighting
```vue
<!-- src/components/messages/MessageContent.vue -->
<template>
  <div class="message-content">
    <!-- Code Blocks -->
    <template v-if="codeBlocks.length > 0">
      <template v-for="(block, index) in contentBlocks" :key="index">
        <div v-if="block.type === 'text'" class="prose-content" v-html="block.content" />
        <CodeBlock
          v-else
          :code="block.content"
          :language="block.language"
          :filename="block.filename"
          @copy="$emit('copy', block.content)"
        />
      </template>
    </template>
    
    <!-- Regular Text Content -->
    <div v-else class="prose-content" v-html="formattedContent" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import CodeBlock from './CodeBlock.vue'

interface Props {
  content: string
  type?: 'text' | 'markdown' | 'code'
}

const props = withDefaults(defineProps<Props>(), {
  type: 'markdown'
})

defineEmits<{
  copy: [content: string]
}>()

interface ContentBlock {
  type: 'text' | 'code'
  content: string
  language?: string
  filename?: string
}

const codeBlockRegex = /```(\w+)?\s*(?:\n(.+?)\n)?\n([\s\S]*?)```/g

const codeBlocks = computed(() => {
  const blocks: Array<{ content: string; language?: string; filename?: string }> = []
  let match
  
  while ((match = codeBlockRegex.exec(props.content)) !== null) {
    const [, language, filename, code] = match
    blocks.push({
      content: code.trim(),
      language: language || 'text',
      filename: filename?.trim()
    })
  }
  
  return blocks
})

const contentBlocks = computed((): ContentBlock[] => {
  if (codeBlocks.value.length === 0) {
    return []
  }
  
  const blocks: ContentBlock[] = []
  let lastIndex = 0
  let match
  
  // Reset regex
  codeBlockRegex.lastIndex = 0
  
  while ((match = codeBlockRegex.exec(props.content)) !== null) {
    // Add text before code block
    if (match.index > lastIndex) {
      const textContent = props.content.slice(lastIndex, match.index).trim()
      if (textContent) {
        blocks.push({
          type: 'text',
          content: processMarkdown(textContent)
        })
      }
    }
    
    // Add code block
    const [, language, filename, code] = match
    blocks.push({
      type: 'code',
      content: code.trim(),
      language: language || 'text',
      filename: filename?.trim()
    })
    
    lastIndex = match.index + match[0].length
  }
  
  // Add remaining text
  if (lastIndex < props.content.length) {
    const textContent = props.content.slice(lastIndex).trim()
    if (textContent) {
      blocks.push({
        type: 'text',
        content: processMarkdown(textContent)
      })
    }
  }
  
  return blocks
})

const formattedContent = computed(() => {
  if (props.type === 'code') {
    return `<pre><code>${escapeHtml(props.content)}</code></pre>`
  }
  
  return processMarkdown(props.content)
})

function processMarkdown(content: string): string {
  if (props.type !== 'markdown') {
    return escapeHtml(content)
  }
  
  // Configure marked for safe rendering
  marked.setOptions({
    breaks: true,
    gfm: true,
    headerIds: false,
    mangle: false
  })
  
  const html = marked.parse(content)
  return DOMPurify.sanitize(html)
}

function escapeHtml(text: string): string {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}
</script>

<style scoped>
.prose-content {
  @apply text-gray-900 dark:text-gray-100;
}

.prose-content :deep(p) {
  @apply mb-4 last:mb-0;
}

.prose-content :deep(h1),
.prose-content :deep(h2),
.prose-content :deep(h3),
.prose-content :deep(h4),
.prose-content :deep(h5),
.prose-content :deep(h6) {
  @apply font-semibold text-gray-900 dark:text-white mb-3 mt-6 first:mt-0;
}

.prose-content :deep(ul),
.prose-content :deep(ol) {
  @apply mb-4 pl-6;
}

.prose-content :deep(li) {
  @apply mb-1;
}

.prose-content :deep(blockquote) {
  @apply border-l-4 border-gray-300 dark:border-gray-600 pl-4 italic text-gray-700 dark:text-gray-300 my-4;
}

.prose-content :deep(a) {
  @apply text-blue-600 dark:text-blue-400 hover:underline;
}

.prose-content :deep(strong) {
  @apply font-semibold text-gray-900 dark:text-white;
}

.prose-content :deep(em) {
  @apply italic;
}

.prose-content :deep(code) {
  @apply bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 px-1.5 py-0.5 rounded text-sm font-mono;
}
</style>
```

### Real-Time Typing Indicator
```vue
<!-- src/components/messages/TypingIndicator.vue -->
<template>
  <transition
    enter-active-class="transition-all duration-300 ease-out"
    enter-from-class="opacity-0 transform scale-95"
    enter-to-class="opacity-100 transform scale-100"
    leave-active-class="transition-all duration-200 ease-in"
    leave-from-class="opacity-100 transform scale-100"
    leave-to-class="opacity-0 transform scale-95"
  >
    <div v-if="typingUsers.length > 0" class="typing-indicator p-4 bg-gray-50 dark:bg-gray-800/50">
      <div class="flex items-start gap-3">
        <!-- Avatar Stack -->
        <div class="flex -space-x-2">
          <div
            v-for="user in displayUsers"
            :key="user.id"
            class="w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-medium border-2 border-white dark:border-gray-800"
            :title="user.name"
          >
            {{ user.name.charAt(0).toUpperCase() }}
          </div>
          <div
            v-if="extraCount > 0"
            class="w-6 h-6 rounded-full bg-gray-400 flex items-center justify-center text-white text-xs font-medium border-2 border-white dark:border-gray-800"
          >
            +{{ extraCount }}
          </div>
        </div>
        
        <!-- Typing Text and Animation -->
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-600 dark:text-gray-400">
            {{ typingText }}
          </span>
          
          <!-- Animated Dots -->
          <div class="flex gap-1">
            <div
              v-for="i in 3"
              :key="i"
              class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-pulse"
              :style="{ animationDelay: `${(i - 1) * 0.2}s` }"
            />
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { User } from '@types/user'

interface TypingUser extends User {
  id: string
  name: string
}

interface Props {
  typingUsers: TypingUser[]
  maxDisplayUsers?: number
}

const props = withDefaults(defineProps<Props>(), {
  maxDisplayUsers: 3
})

const displayUsers = computed(() => 
  props.typingUsers.slice(0, props.maxDisplayUsers)
)

const extraCount = computed(() => 
  Math.max(0, props.typingUsers.length - props.maxDisplayUsers)
)

const typingText = computed(() => {
  const count = props.typingUsers.length
  
  if (count === 0) return ''
  if (count === 1) return `${props.typingUsers[0].name} is typing...`
  if (count === 2) return `${props.typingUsers[0].name} and ${props.typingUsers[1].name} are typing...`
  if (count === 3) return `${props.typingUsers[0].name}, ${props.typingUsers[1].name}, and ${props.typingUsers[2].name} are typing...`
  
  return `${props.typingUsers.slice(0, 2).map(u => u.name).join(', ')} and ${count - 2} others are typing...`
})
</script>

<style scoped>
@keyframes pulse-dot {
  0%, 60%, 100% {
    opacity: 0.4;
    transform: scale(1);
  }
  30% {
    opacity: 1;
    transform: scale(1.2);
  }
}

.animate-pulse {
  animation: pulse-dot 1.5s infinite;
}
</style>
```

## Performance Requirements
- **Render Time**: Message components render within 16ms (60fps)
- **Virtual Scrolling**: Handle 10,000+ messages smoothly
- **Memory Usage**: Component memory usage under 50MB
- **Animation Performance**: 60fps animations with no jank
- **Bundle Size**: Component library under 200KB gzipped

## Accessibility Requirements
- **WCAG 2.1 AA Compliance**: All components meet accessibility standards
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader Support**: Proper ARIA labels and descriptions
- **Color Contrast**: Minimum 4.5:1 contrast ratio
- **Focus Management**: Clear focus indicators and logical tab order

## Acceptance Criteria
- [ ] Complete design system with consistent styling
- [ ] Conversation list with virtual scrolling and search
- [ ] Message components with syntax highlighting
- [ ] Real-time typing indicators and presence
- [ ] Responsive design across all device sizes
- [ ] Accessibility compliance (WCAG 2.1 AA)
- [ ] Component library documentation
- [ ] Performance benchmarks meeting requirements
- [ ] Cross-browser compatibility testing
- [ ] Unit tests for all components (>90% coverage)

## Testing Procedures
1. **Component Testing**: Individual component behavior and props
2. **Visual Regression**: Screenshot testing for UI consistency
3. **Accessibility Testing**: Automated and manual accessibility audits
4. **Performance Testing**: Rendering performance and memory usage
5. **Cross-Browser Testing**: Chrome, Firefox, Safari, Edge compatibility

## Integration Points
- **Week 6**: Real-time WebSocket event handling
- **Week 9**: Analytics data visualization components
- **Week 10**: Chart and dashboard integrations

## Advanced Vue 3 Component Patterns

### Composition API with TypeScript Best Practices

#### 1. Component Setup and Props Definition
```vue
<!-- src/components/conversation/ConversationHeader.vue -->
<template>
  <header class="sticky top-0 z-10 bg-white/80 backdrop-blur-md border-b border-gray-200 dark:bg-gray-900/80 dark:border-gray-700">
    <div class="flex items-center justify-between px-4 py-3">
      <!-- Title Section -->
      <div class="flex items-center gap-3 min-w-0">
        <button
          v-if="showBackButton"
          @click="$emit('back')"
          class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          aria-label="Go back"
        >
          <ArrowLeftIcon class="w-5 h-5" />
        </button>
        
        <div class="min-w-0 flex-1">
          <h1 
            class="text-lg font-semibold text-gray-900 dark:text-white truncate"
            :title="conversation.title"
          >
            {{ conversation.title }}
          </h1>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            {{ messageCount }} messages • {{ formatLastActivity(conversation.updatedAt) }}
          </p>
        </div>
      </div>
      
      <!-- Actions -->
      <div class="flex items-center gap-2">
        <ConversationActions
          :conversation="conversation"
          :is-loading="isLoading"
          @export="$emit('export', $event)"
          @delete="$emit('delete')"
          @share="$emit('share')"
        />
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArrowLeftIcon } from '@heroicons/vue/24/outline'
import { formatDistanceToNow } from 'date-fns'
import ConversationActions from './ConversationActions.vue'
import type { Conversation } from '@/types/conversation'

// Props with comprehensive TypeScript definitions
interface Props {
  conversation: Conversation
  messageCount: number
  isLoading?: boolean
  showBackButton?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
  showBackButton: false
})

// Events with type-safe emit definitions
interface Emits {
  back: []
  export: [format: 'json' | 'markdown' | 'pdf']
  delete: []
  share: []
}

const emit = defineEmits<Emits>()

// Computed properties with proper typing
const formatLastActivity = (date: string): string => {
  return formatDistanceToNow(new Date(date), { addSuffix: true })
}
</script>
```

#### 2. Reusable Input Components with v-model
```vue
<!-- src/components/base/BaseInput.vue -->
<template>
  <div class="relative">
    <!-- Label -->
    <label 
      v-if="label"
      :for="inputId"
      class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
    >
      {{ label }}
      <span v-if="required" class="text-red-500 ml-1">*</span>
    </label>
    
    <!-- Input wrapper -->
    <div class="relative">
      <!-- Leading icon -->
      <div 
        v-if="$slots.leading"
        class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"
      >
        <slot name="leading" />
      </div>
      
      <!-- Input element -->
      <input
        :id="inputId"
        ref="inputRef"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :autocomplete="autocomplete"
        :class="inputClasses"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
        @keydown="handleKeydown"
      />
      
      <!-- Trailing content -->
      <div 
        v-if="$slots.trailing || showClearButton"
        class="absolute inset-y-0 right-0 pr-3 flex items-center"
      >
        <button
          v-if="showClearButton"
          @click="clearInput"
          class="p-1 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          aria-label="Clear input"
        >
          <XMarkIcon class="w-4 h-4 text-gray-400" />
        </button>
        <slot name="trailing" />
      </div>
    </div>
    
    <!-- Helper text or error message -->
    <div v-if="helperText || errorMessage" class="mt-1 text-sm">
      <p 
        v-if="errorMessage"
        class="text-red-600 dark:text-red-400"
        role="alert"
      >
        {{ errorMessage }}
      </p>
      <p 
        v-else-if="helperText"
        class="text-gray-500 dark:text-gray-400"
      >
        {{ helperText }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, nextTick, useId } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'

// Props interface with comprehensive options
interface Props {
  modelValue: string
  type?: 'text' | 'email' | 'password' | 'search' | 'url' | 'tel'
  label?: string
  placeholder?: string
  helperText?: string
  errorMessage?: string
  disabled?: boolean
  readonly?: boolean
  required?: boolean
  autocomplete?: string
  size?: 'sm' | 'md' | 'lg'
  variant?: 'default' | 'filled' | 'outlined'
  clearable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  size: 'md',
  variant: 'default',
  disabled: false,
  readonly: false,
  required: false,
  clearable: false
})

// Events
interface Emits {
  'update:modelValue': [value: string]
  blur: [event: FocusEvent]
  focus: [event: FocusEvent]
  keydown: [event: KeyboardEvent]
  clear: []
}

const emit = defineEmits<Emits>()

// Template refs
const inputRef = ref<HTMLInputElement>()

// Unique ID for accessibility
const inputId = useId()

// Computed properties
const inputClasses = computed(() => {
  const baseClasses = [
    'block w-full rounded-md border-0 py-1.5 shadow-sm ring-1 ring-inset',
    'placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600',
    'disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500',
    'transition-all duration-200'
  ]
  
  // Size variants
  const sizeClasses = {
    sm: 'text-sm px-2.5 py-1.5',
    md: 'text-sm px-3 py-2',
    lg: 'text-base px-4 py-3'
  }
  
  // Variant styles
  const variantClasses = {
    default: [
      'bg-white dark:bg-gray-900',
      'text-gray-900 dark:text-white',
      'ring-gray-300 dark:ring-gray-600',
      'focus:ring-primary-600 dark:focus:ring-primary-500'
    ],
    filled: [
      'bg-gray-50 dark:bg-gray-800',
      'text-gray-900 dark:text-white',
      'ring-transparent',
      'focus:ring-primary-600 dark:focus:ring-primary-500'
    ],
    outlined: [
      'bg-transparent',
      'text-gray-900 dark:text-white',
      'ring-gray-300 dark:ring-gray-600',
      'focus:ring-primary-600 dark:focus:ring-primary-500'
    ]
  }
  
  // Error state
  const errorClasses = props.errorMessage ? [
    'ring-red-300 dark:ring-red-600',
    'focus:ring-red-500 dark:focus:ring-red-400'
  ] : []
  
  // Padding adjustments for icons
  const iconPaddingClasses = []
  if (props.$$slots?.leading) iconPaddingClasses.push('pl-10')
  if (props.$$slots?.trailing || showClearButton.value) iconPaddingClasses.push('pr-10')
  
  return [
    ...baseClasses,
    sizeClasses[props.size],
    ...variantClasses[props.variant],
    ...errorClasses,
    ...iconPaddingClasses
  ].join(' ')
})

const showClearButton = computed(() => 
  props.clearable && props.modelValue.length > 0 && !props.disabled && !props.readonly
)

// Methods
const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}

const handleBlur = (event: FocusEvent) => {
  emit('blur', event)
}

const handleFocus = (event: FocusEvent) => {
  emit('focus', event)
}

const handleKeydown = (event: KeyboardEvent) => {
  emit('keydown', event)
}

const clearInput = () => {
  emit('update:modelValue', '')
  emit('clear')
  nextTick(() => {
    inputRef.value?.focus()
  })
}

// Expose methods for parent components
defineExpose({
  focus: () => inputRef.value?.focus(),
  blur: () => inputRef.value?.blur(),
  select: () => inputRef.value?.select()
})
</script>
```

#### 3. Advanced Slot and Event Patterns
```vue
<!-- src/components/base/BaseModal.vue -->
<template>
  <Teleport to="body">
    <Transition
      name="modal"
      @enter="onEnter"
      @leave="onLeave"
    >
      <div 
        v-if="isOpen"
        class="fixed inset-0 z-50 flex items-center justify-center"
        @click="handleBackdropClick"
      >
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" />
        
        <!-- Modal container -->
        <div 
          ref="modalRef"
          :class="modalClasses"
          @click.stop
          role="dialog"
          :aria-labelledby="titleId"
          :aria-describedby="descriptionId"
          aria-modal="true"
        >
          <!-- Header -->
          <header 
            v-if="$slots.header || title"
            class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700"
          >
            <div class="flex-1 min-w-0">
              <slot name="header">
                <h2 
                  :id="titleId"
                  class="text-xl font-semibold text-gray-900 dark:text-white"
                >
                  {{ title }}
                </h2>
              </slot>
            </div>
            
            <button
              v-if="showCloseButton"
              @click="closeModal"
              class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              aria-label="Close modal"
            >
              <XMarkIcon class="w-5 h-5" />
            </button>
          </header>
          
          <!-- Body -->
          <div class="flex-1 p-6 overflow-y-auto">
            <slot :close="closeModal" />
          </div>
          
          <!-- Footer -->
          <footer 
            v-if="$slots.footer"
            class="flex items-center justify-end gap-3 p-6 border-t border-gray-200 dark:border-gray-700"
          >
            <slot name="footer" :close="closeModal" />
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref, watch, nextTick, useId, onMounted, onUnmounted } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'

// Props
interface Props {
  isOpen: boolean
  title?: string
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  showCloseButton?: boolean
  closeOnBackdrop?: boolean
  closeOnEscape?: boolean
  persistent?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  showCloseButton: true,
  closeOnBackdrop: true,
  closeOnEscape: true,
  persistent: false
})

// Events
interface Emits {
  'update:isOpen': [value: boolean]
  open: []
  close: []
  escape: []
}

const emit = defineEmits<Emits>()

// Template refs
const modalRef = ref<HTMLElement>()

// Unique IDs for accessibility
const titleId = useId()
const descriptionId = useId()

// Computed properties
const modalClasses = computed(() => {
  const baseClasses = [
    'relative bg-white dark:bg-gray-900 rounded-lg shadow-xl',
    'max-h-[90vh] flex flex-col',
    'mx-4 my-8'
  ]
  
  const sizeClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    full: 'max-w-full mx-4'
  }
  
  return [
    ...baseClasses,
    sizeClasses[props.size]
  ].join(' ')
})

// Methods
const closeModal = () => {
  if (!props.persistent) {
    emit('update:isOpen', false)
    emit('close')
  }
}

const handleBackdropClick = () => {
  if (props.closeOnBackdrop) {
    closeModal()
  }
}

const handleEscapeKey = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && props.closeOnEscape) {
    emit('escape')
    closeModal()
  }
}

// Focus management
const trapFocus = (event: KeyboardEvent) => {
  if (event.key !== 'Tab') return
  
  const modal = modalRef.value
  if (!modal) return
  
  const focusableElements = modal.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  )
  
  const firstElement = focusableElements[0] as HTMLElement
  const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement
  
  if (event.shiftKey) {
    if (document.activeElement === firstElement) {
      lastElement.focus()
      event.preventDefault()
    }
  } else {
    if (document.activeElement === lastElement) {
      firstElement.focus()
      event.preventDefault()
    }
  }
}

// Lifecycle hooks
onMounted(() => {
  document.addEventListener('keydown', handleEscapeKey)
  document.addEventListener('keydown', trapFocus)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscapeKey)
  document.removeEventListener('keydown', trapFocus)
})

// Watchers
watch(() => props.isOpen, (newValue) => {
  if (newValue) {
    emit('open')
    nextTick(() => {
      const modal = modalRef.value
      if (modal) {
        const firstFocusable = modal.querySelector(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        ) as HTMLElement
        firstFocusable?.focus()
      }
    })
  }
})

// Transition handlers
const onEnter = () => {
  document.body.style.overflow = 'hidden'
}

const onLeave = () => {
  document.body.style.overflow = ''
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
</style>
```

### Tailwind CSS Design System Integration

#### 1. Component Design Tokens
```typescript
// src/design-system/tokens.ts
export const designTokens = {
  // Color system with semantic naming
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
      950: '#082f49'
    },
    
    // Semantic colors
    semantic: {
      success: {
        light: '#22c55e',
        DEFAULT: '#16a34a',
        dark: '#15803d'
      },
      warning: {
        light: '#f59e0b',
        DEFAULT: '#d97706',
        dark: '#b45309'
      },
      error: {
        light: '#ef4444',
        DEFAULT: '#dc2626',
        dark: '#b91c1c'
      },
      info: {
        light: '#3b82f6',
        DEFAULT: '#2563eb',
        dark: '#1d4ed8'
      }
    },
    
    // Neutral grays
    gray: {
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
      950: '#020617'
    }
  },

  // Typography scale
  typography: {
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif'],
      mono: ['JetBrains Mono', 'ui-monospace', 'monospace']
    },
    fontSize: {
      xs: ['0.75rem', { lineHeight: '1rem' }],
      sm: ['0.875rem', { lineHeight: '1.25rem' }],
      base: ['1rem', { lineHeight: '1.5rem' }],
      lg: ['1.125rem', { lineHeight: '1.75rem' }],
      xl: ['1.25rem', { lineHeight: '1.75rem' }],
      '2xl': ['1.5rem', { lineHeight: '2rem' }],
      '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
      '4xl': ['2.25rem', { lineHeight: '2.5rem' }]
    },
    fontWeight: {
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700'
    }
  },

  // Spacing system
  spacing: {
    px: '1px',
    0: '0px',
    0.5: '0.125rem',
    1: '0.25rem',
    1.5: '0.375rem',
    2: '0.5rem',
    2.5: '0.625rem',
    3: '0.75rem',
    3.5: '0.875rem',
    4: '1rem',
    5: '1.25rem',
    6: '1.5rem',
    7: '1.75rem',
    8: '2rem',
    9: '2.25rem',
    10: '2.5rem',
    11: '2.75rem',
    12: '3rem',
    14: '3.5rem',
    16: '4rem',
    20: '5rem',
    24: '6rem',
    28: '7rem',
    32: '8rem',
    36: '9rem',
    40: '10rem',
    44: '11rem',
    48: '12rem',
    52: '13rem',
    56: '14rem',
    60: '15rem',
    64: '16rem',
    72: '18rem',
    80: '20rem',
    96: '24rem'
  },

  // Border radius
  borderRadius: {
    none: '0px',
    sm: '0.125rem',
    DEFAULT: '0.25rem',
    md: '0.375rem',
    lg: '0.5rem',
    xl: '0.75rem',
    '2xl': '1rem',
    '3xl': '1.5rem',
    full: '9999px'
  },

  // Shadows
  boxShadow: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    DEFAULT: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
    '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
    inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
    none: 'none'
  },

  // Z-index scale
  zIndex: {
    0: '0',
    10: '10',
    20: '20',
    30: '30',
    40: '40',
    50: '50',
    auto: 'auto'
  },

  // Transitions
  transitionDuration: {
    75: '75ms',
    100: '100ms',
    150: '150ms',
    200: '200ms',
    300: '300ms',
    500: '500ms',
    700: '700ms',
    1000: '1000ms'
  },

  transitionTimingFunction: {
    linear: 'linear',
    in: 'cubic-bezier(0.4, 0, 1, 1)',
    out: 'cubic-bezier(0, 0, 0.2, 1)',
    'in-out': 'cubic-bezier(0.4, 0, 0.2, 1)'
  }
} as const

// Type definitions for design tokens
export type ColorScale = typeof designTokens.colors.primary
export type SemanticColor = keyof typeof designTokens.colors.semantic
export type FontSize = keyof typeof designTokens.typography.fontSize
export type SpacingScale = keyof typeof designTokens.spacing
```

#### 2. Responsive Component Patterns
```vue
<!-- src/components/layout/ResponsiveGrid.vue -->
<template>
  <div :class="gridClasses">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  cols?: {
    default: number
    sm?: number
    md?: number
    lg?: number
    xl?: number
    '2xl'?: number
  }
  gap?: {
    default: number
    sm?: number
    md?: number
    lg?: number
    xl?: number
    '2xl'?: number
  }
  autoRows?: 'auto' | 'min' | 'max' | 'fr'
}

const props = withDefaults(defineProps<Props>(), {
  cols: () => ({ default: 1 }),
  gap: () => ({ default: 4 }),
  autoRows: 'auto'
})

const gridClasses = computed(() => {
  const classes = ['grid']
  
  // Grid columns
  const colsMap = {
    1: 'grid-cols-1',
    2: 'grid-cols-2',
    3: 'grid-cols-3',
    4: 'grid-cols-4',
    5: 'grid-cols-5',
    6: 'grid-cols-6',
    12: 'grid-cols-12'
  }
  
  // Default columns
  classes.push(colsMap[props.cols.default] || 'grid-cols-1')
  
  // Responsive columns
  if (props.cols.sm) classes.push(`sm:${colsMap[props.cols.sm]}`)
  if (props.cols.md) classes.push(`md:${colsMap[props.cols.md]}`)
  if (props.cols.lg) classes.push(`lg:${colsMap[props.cols.lg]}`)
  if (props.cols.xl) classes.push(`xl:${colsMap[props.cols.xl]}`)
  if (props.cols['2xl']) classes.push(`2xl:${colsMap[props.cols['2xl']]}`)
  
  // Gap
  const gapMap = {
    0: 'gap-0',
    1: 'gap-1',
    2: 'gap-2',
    3: 'gap-3',
    4: 'gap-4',
    5: 'gap-5',
    6: 'gap-6',
    8: 'gap-8'
  }
  
  // Default gap
  classes.push(gapMap[props.gap.default] || 'gap-4')
  
  // Responsive gap
  if (props.gap.sm) classes.push(`sm:${gapMap[props.gap.sm]}`)
  if (props.gap.md) classes.push(`md:${gapMap[props.gap.md]}`)
  if (props.gap.lg) classes.push(`lg:${gapMap[props.gap.lg]}`)
  if (props.gap.xl) classes.push(`xl:${gapMap[props.gap.xl]}`)
  if (props.gap['2xl']) classes.push(`2xl:${gapMap[props.gap['2xl']]}`)
  
  // Auto rows
  const autoRowsMap = {
    auto: 'auto-rows-auto',
    min: 'auto-rows-min',
    max: 'auto-rows-max',
    fr: 'auto-rows-fr'
  }
  
  classes.push(autoRowsMap[props.autoRows])
  
  return classes.join(' ')
})
</script>
```

#### 3. Dark Mode Implementation
```vue
<!-- src/components/theme/ThemeProvider.vue -->
<template>
  <div>
    <slot />
  </div>
</template>

<script setup lang="ts">
import { provide, ref, computed, watch, onMounted } from 'vue'

// Theme types
type Theme = 'light' | 'dark' | 'system'

// Theme state
const theme = ref<Theme>('system')
const systemPrefersDark = ref(false)

// Computed resolved theme
const resolvedTheme = computed(() => {
  if (theme.value === 'system') {
    return systemPrefersDark.value ? 'dark' : 'light'
  }
  return theme.value
})

// Theme functions
const setTheme = (newTheme: Theme) => {
  theme.value = newTheme
  localStorage.setItem('theme', newTheme)
  applyTheme()
}

const applyTheme = () => {
  const html = document.documentElement
  const isDark = resolvedTheme.value === 'dark'
  
  html.classList.toggle('dark', isDark)
  
  // Update meta theme-color for mobile browsers
  const metaThemeColor = document.querySelector('meta[name="theme-color"]')
  if (metaThemeColor) {
    metaThemeColor.setAttribute('content', isDark ? '#0f172a' : '#ffffff')
  }
}

// Watch system preference
const watchSystemPreference = () => {
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  systemPrefersDark.value = mediaQuery.matches
  
  const handleChange = (event: MediaQueryListEvent) => {
    systemPrefersDark.value = event.matches
    if (theme.value === 'system') {
      applyTheme()
    }
  }
  
  mediaQuery.addEventListener('change', handleChange)
  
  return () => mediaQuery.removeEventListener('change', handleChange)
}

// Initialize theme
onMounted(() => {
  // Get saved theme or default to system
  const savedTheme = localStorage.getItem('theme') as Theme
  if (savedTheme && ['light', 'dark', 'system'].includes(savedTheme)) {
    theme.value = savedTheme
  }
  
  // Watch system preference
  const cleanup = watchSystemPreference()
  
  // Apply initial theme
  applyTheme()
  
  // Cleanup on unmount
  return cleanup
})

// Watch theme changes
watch(resolvedTheme, applyTheme)

// Provide theme context
provide('theme', {
  theme: computed(() => theme.value),
  resolvedTheme,
  setTheme,
  isDark: computed(() => resolvedTheme.value === 'dark')
})
</script>
```

#### 4. Animation and Transition Patterns
```vue
<!-- src/components/transitions/SlideOver.vue -->
<template>
  <Teleport to="body">
    <Transition
      name="slide-over"
      @enter="onEnter"
      @leave="onLeave"
    >
      <div 
        v-if="isOpen"
        class="fixed inset-0 z-50 overflow-hidden"
        @click="handleBackdropClick"
      >
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" />
        
        <!-- Slide over panel -->
        <div class="fixed inset-y-0 right-0 flex max-w-full pl-10">
          <div 
            ref="panelRef"
            class="pointer-events-auto w-screen max-w-md"
            @click.stop
          >
            <div class="flex h-full flex-col bg-white dark:bg-gray-900 shadow-xl">
              <!-- Header -->
              <div class="px-4 py-6 sm:px-6">
                <div class="flex items-center justify-between">
                  <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
                    {{ title }}
                  </h2>
                  <button
                    @click="closePanel"
                    class="rounded-md p-2 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                  >
                    <XMarkIcon class="h-6 w-6" />
                  </button>
                </div>
              </div>
              
              <!-- Content -->
              <div class="flex-1 overflow-y-auto px-4 py-6 sm:px-6">
                <slot />
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'

interface Props {
  isOpen: boolean
  title: string
}

const props = defineProps<Props>()

interface Emits {
  'update:isOpen': [value: boolean]
  close: []
}

const emit = defineEmits<Emits>()

const panelRef = ref<HTMLElement>()

const closePanel = () => {
  emit('update:isOpen', false)
  emit('close')
}

const handleBackdropClick = () => {
  closePanel()
}

const onEnter = () => {
  document.body.style.overflow = 'hidden'
}

const onLeave = () => {
  document.body.style.overflow = ''
}
</script>

<style scoped>
.slide-over-enter-active {
  transition: all 0.3s ease-out;
}

.slide-over-leave-active {
  transition: all 0.3s ease-in;
}

.slide-over-enter-from .absolute {
  opacity: 0;
}

.slide-over-leave-to .absolute {
  opacity: 0;
}

.slide-over-enter-from .pointer-events-auto {
  transform: translateX(100%);
}

.slide-over-leave-to .pointer-events-auto {
  transform: translateX(100%);
}
</style>
```

### Component Testing Strategies

#### 1. Unit Testing with Vitest
```typescript
// src/components/base/__tests__/BaseButton.test.ts
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseButton from '../BaseButton.vue'

describe('BaseButton', () => {
  it('renders correctly with default props', () => {
    const wrapper = mount(BaseButton, {
      slots: { default: 'Click me' }
    })
    
    expect(wrapper.text()).toContain('Click me')
    expect(wrapper.classes()).toContain('bg-primary-600')
  })

  it('applies correct variant classes', () => {
    const wrapper = mount(BaseButton, {
      props: { variant: 'secondary' },
      slots: { default: 'Button' }
    })
    
    expect(wrapper.classes()).toContain('bg-white')
    expect(wrapper.classes()).toContain('border-gray-300')
  })

  it('shows loading state correctly', () => {
    const wrapper = mount(BaseButton, {
      props: { loading: true },
      slots: { default: 'Loading...' }
    })
    
    expect(wrapper.find('.animate-spin').exists()).toBe(true)
    expect(wrapper.find('button').attributes('disabled')).toBe('')
  })

  it('emits click event when clicked', async () => {
    const wrapper = mount(BaseButton, {
      slots: { default: 'Click me' }
    })
    
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('click')).toHaveLength(1)
  })

  it('does not emit click when disabled', async () => {
    const wrapper = mount(BaseButton, {
      props: { disabled: true },
      slots: { default: 'Disabled' }
    })
    
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('click')).toBeUndefined()
  })

  it('handles icon-only variant correctly', () => {
    const wrapper = mount(BaseButton, {
      props: { iconOnly: true, size: 'md' },
      slots: { default: 'A' }
    })
    
    expect(wrapper.classes()).toContain('w-10')
    expect(wrapper.classes()).toContain('h-10')
  })
})
```

#### 2. Component Testing with Cypress
```typescript
// cypress/components/BaseModal.cy.ts
import BaseModal from '@/components/base/BaseModal.vue'

describe('BaseModal', () => {
  it('opens and closes correctly', () => {
    cy.mount(BaseModal, {
      props: {
        isOpen: true,
        title: 'Test Modal'
      },
      slots: {
        default: '<p>Modal content</p>'
      }
    })

    cy.get('[role="dialog"]').should('be.visible')
    cy.get('h2').should('contain', 'Test Modal')
    cy.get('p').should('contain', 'Modal content')
    
    // Test close button
    cy.get('[aria-label="Close modal"]').click()
    cy.get('[role="dialog"]').should('not.exist')
  })

  it('closes on backdrop click', () => {
    cy.mount(BaseModal, {
      props: {
        isOpen: true,
        title: 'Test Modal',
        closeOnBackdrop: true
      },
      slots: {
        default: '<p>Modal content</p>'
      }
    })

    cy.get('.fixed.inset-0').click({ force: true })
    cy.get('[role="dialog"]').should('not.exist')
  })

  it('traps focus correctly', () => {
    cy.mount(BaseModal, {
      props: {
        isOpen: true,
        title: 'Test Modal'
      },
      slots: {
        default: `
          <input data-testid="first-input" />
          <input data-testid="second-input" />
        `
      }
    })

    cy.get('[data-testid="first-input"]').should('be.focused')
    cy.get('[data-testid="first-input"]').tab()
    cy.get('[data-testid="second-input"]').should('be.focused')
  })
})
```

### Performance Optimization Patterns

#### 1. Virtual Scrolling Implementation
```vue
<!-- src/components/virtualized/VirtualList.vue -->
<template>
  <div 
    ref="containerRef"
    class="relative overflow-auto"
    :style="{ height: `${height}px` }"
    @scroll="handleScroll"
  >
    <!-- Virtual spacer for scrollbar -->
    <div :style="{ height: `${totalHeight}px` }" />
    
    <!-- Visible items -->
    <div
      class="absolute top-0 left-0 right-0"
      :style="{ transform: `translateY(${offsetY}px)` }"
    >
      <div
        v-for="item in visibleItems"
        :key="item.index"
        :style="{ height: `${itemHeight}px` }"
        class="flex items-center px-4 border-b border-gray-200 dark:border-gray-700"
      >
        <slot :item="item.data" :index="item.index" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface Props {
  items: any[]
  itemHeight: number
  height: number
  overscan?: number
}

const props = withDefaults(defineProps<Props>(), {
  overscan: 5
})

const containerRef = ref<HTMLElement>()
const scrollTop = ref(0)

const totalHeight = computed(() => props.items.length * props.itemHeight)

const visibleRange = computed(() => {
  const containerHeight = props.height
  const start = Math.floor(scrollTop.value / props.itemHeight)
  const end = Math.min(
    start + Math.ceil(containerHeight / props.itemHeight),
    props.items.length
  )

  return {
    start: Math.max(0, start - props.overscan),
    end: Math.min(props.items.length, end + props.overscan)
  }
})

const visibleItems = computed(() => {
  const { start, end } = visibleRange.value
  const items = []
  
  for (let i = start; i < end; i++) {
    items.push({
      index: i,
      data: props.items[i]
    })
  }
  
  return items
})

const offsetY = computed(() => visibleRange.value.start * props.itemHeight)

const handleScroll = (event: Event) => {
  const target = event.target as HTMLElement
  scrollTop.value = target.scrollTop
}

// Scroll to item
const scrollToItem = (index: number) => {
  if (containerRef.value) {
    const scrollTop = index * props.itemHeight
    containerRef.value.scrollTop = scrollTop
  }
}

defineExpose({
  scrollToItem
})
</script>
```

#### 2. Lazy Loading Component
```vue
<!-- src/components/optimization/LazyComponent.vue -->
<template>
  <div ref="containerRef">
    <div
      v-if="!isIntersecting"
      :style="{ height: `${placeholder.height}px` }"
      class="flex items-center justify-center bg-gray-50 dark:bg-gray-800"
    >
      <div class="text-center">
        <div class="animate-pulse">
          <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24 mx-auto mb-2" />
          <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-16 mx-auto" />
        </div>
      </div>
    </div>
    
    <component
      v-else
      :is="loadedComponent"
      v-bind="$attrs"
    >
      <slot />
    </component>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, type Component } from 'vue'

interface Props {
  component: () => Promise<Component>
  placeholder?: {
    height: number
  }
  rootMargin?: string
  threshold?: number
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: () => ({ height: 200 }),
  rootMargin: '50px',
  threshold: 0.1
})

const containerRef = ref<HTMLElement>()
const isIntersecting = ref(false)
const loadedComponent = ref<Component | null>(null)

let observer: IntersectionObserver | null = null

const handleIntersection = async (entries: IntersectionObserverEntry[]) => {
  const entry = entries[0]
  
  if (entry.isIntersecting && !loadedComponent.value) {
    try {
      const component = await props.component()
      loadedComponent.value = component
      isIntersecting.value = true
      
      // Clean up observer after loading
      if (observer) {
        observer.disconnect()
        observer = null
      }
    } catch (error) {
      console.error('Failed to load component:', error)
    }
  }
}

onMounted(() => {
  if (containerRef.value) {
    observer = new IntersectionObserver(handleIntersection, {
      rootMargin: props.rootMargin,
      threshold: props.threshold
    })
    
    observer.observe(containerRef.value)
  }
})

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
})
</script>
```

### Accessibility Best Practices

#### 1. Accessible Form Components
```vue
<!-- src/components/forms/AccessibleForm.vue -->
<template>
  <form
    @submit.prevent="handleSubmit"
    novalidate
    class="space-y-6"
  >
    <fieldset class="space-y-4">
      <legend class="text-lg font-semibold text-gray-900 dark:text-white">
        {{ title }}
      </legend>
      
      <div class="space-y-4">
        <BaseInput
          v-model="formData.email"
          type="email"
          label="Email Address"
          :error-message="errors.email"
          required
          autocomplete="email"
          :aria-describedby="errors.email ? 'email-error' : undefined"
        />
        
        <BaseInput
          v-model="formData.password"
          type="password"
          label="Password"
          :error-message="errors.password"
          required
          autocomplete="current-password"
          :aria-describedby="errors.password ? 'password-error' : 'password-help'"
        />
        
        <div id="password-help" class="text-sm text-gray-500">
          Password must be at least 8 characters long
        </div>
      </div>
    </fieldset>
    
    <div class="flex items-center justify-between">
      <button
        type="submit"
        :disabled="isSubmitting"
        class="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        :aria-describedby="isSubmitting ? 'submit-status' : undefined"
      >
        {{ isSubmitting ? 'Submitting...' : 'Submit' }}
      </button>
      
      <div
        v-if="isSubmitting"
        id="submit-status"
        class="text-sm text-gray-500"
        role="status"
        aria-live="polite"
      >
        Please wait while we process your request
      </div>
    </div>
    
    <!-- Form-level errors -->
    <div
      v-if="formError"
      class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4"
      role="alert"
    >
      <div class="flex">
        <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800 dark:text-red-200">
            There was an error with your submission
          </h3>
          <p class="mt-1 text-sm text-red-700 dark:text-red-300">
            {{ formError }}
          </p>
        </div>
      </div>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import BaseInput from '@/components/base/BaseInput.vue'

interface Props {
  title: string
}

const props = defineProps<Props>()

interface Emits {
  submit: [data: { email: string; password: string }]
}

const emit = defineEmits<Emits>()

const formData = reactive({
  email: '',
  password: ''
})

const errors = reactive({
  email: '',
  password: ''
})

const isSubmitting = ref(false)
const formError = ref('')

const validateForm = () => {
  errors.email = ''
  errors.password = ''
  
  if (!formData.email) {
    errors.email = 'Email is required'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
    errors.email = 'Please enter a valid email address'
  }
  
  if (!formData.password) {
    errors.password = 'Password is required'
  } else if (formData.password.length < 8) {
    errors.password = 'Password must be at least 8 characters long'
  }
  
  return !errors.email && !errors.password
}

const handleSubmit = async () => {
  if (!validateForm()) return
  
  isSubmitting.value = true
  formError.value = ''
  
  try {
    emit('submit', { ...formData })
  } catch (error) {
    formError.value = 'An unexpected error occurred. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}
</script>
```

## Advanced Component Patterns

### 1. Composable Hook Pattern
```typescript
// src/composables/useConversationList.ts
import { ref, computed, watch } from 'vue'
import { useWebSocketStore } from '@/stores/websocket'
import { useConversationStore } from '@/stores/conversations'
import type { Conversation } from '@/types/conversation'

export function useConversationList() {
  const conversationStore = useConversationStore()
  const webSocketStore = useWebSocketStore()
  
  // Reactive state
  const searchQuery = ref('')
  const sortBy = ref<'updated_at' | 'created_at' | 'title'>('updated_at')
  const sortOrder = ref<'asc' | 'desc'>('desc')
  const selectedConversations = ref<Set<string>>(new Set())
  
  // Computed properties
  const filteredConversations = computed(() => {
    let conversations = [...conversationStore.conversations]
    
    // Apply search filter
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      conversations = conversations.filter(conv =>
        conv.title.toLowerCase().includes(query) ||
        conv.lastMessage?.content.toLowerCase().includes(query)
      )
    }
    
    // Apply sorting
    conversations.sort((a, b) => {
      const aValue = a[sortBy.value]
      const bValue = b[sortBy.value]
      
      if (sortOrder.value === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0
      }
    })
    
    return conversations
  })
  
  // Methods
  const toggleSelection = (conversationId: string) => {
    if (selectedConversations.value.has(conversationId)) {
      selectedConversations.value.delete(conversationId)
    } else {
      selectedConversations.value.add(conversationId)
    }
  }
  
  const selectAll = () => {
    filteredConversations.value.forEach(conv => {
      selectedConversations.value.add(conv.id)
    })
  }
  
  const clearSelection = () => {
    selectedConversations.value.clear()
  }
  
  const deleteSelected = async () => {
    const ids = Array.from(selectedConversations.value)
    await conversationStore.deleteConversations(ids)
    clearSelection()
  }
  
  // Real-time updates
  watch(() => webSocketStore.isConnected, (connected) => {
    if (connected) {
      webSocketStore.on('conversation_updated', (data) => {
        conversationStore.updateConversation(data.conversation)
      })
    }
  })
  
  return {
    // State
    searchQuery,
    sortBy,
    sortOrder,
    selectedConversations,
    
    // Computed
    filteredConversations,
    hasSelection: computed(() => selectedConversations.value.size > 0),
    isAllSelected: computed(() => 
      filteredConversations.value.length > 0 && 
      selectedConversations.value.size === filteredConversations.value.length
    ),
    
    // Methods
    toggleSelection,
    selectAll,
    clearSelection,
    deleteSelected
  }
}
```

### 2. Compound Component Pattern
```vue
<!-- src/components/compound/DataTable.vue -->
<template>
  <div class="bg-white dark:bg-gray-900 shadow-sm rounded-lg overflow-hidden">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { provide, ref, computed } from 'vue'
import type { TableColumn, TableRow } from '@/types/table'

interface Props {
  data: TableRow[]
  columns: TableColumn[]
  sortable?: boolean
  selectable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  sortable: true,
  selectable: false
})

interface Emits {
  sort: [column: string, direction: 'asc' | 'desc']
  select: [rows: TableRow[]]
}

const emit = defineEmits<Emits>()

// Table state
const sortColumn = ref<string>('')
const sortDirection = ref<'asc' | 'desc'>('asc')
const selectedRows = ref<Set<string>>(new Set())

// Methods
const handleSort = (column: string) => {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value = column
    sortDirection.value = 'asc'
  }
  emit('sort', column, sortDirection.value)
}

const toggleRowSelection = (rowId: string) => {
  if (selectedRows.value.has(rowId)) {
    selectedRows.value.delete(rowId)
  } else {
    selectedRows.value.add(rowId)
  }
  
  const selected = props.data.filter(row => selectedRows.value.has(row.id))
  emit('select', selected)
}

// Provide context to child components
provide('table-context', {
  columns: computed(() => props.columns),
  data: computed(() => props.data),
  sortColumn,
  sortDirection,
  selectedRows,
  sortable: computed(() => props.sortable),
  selectable: computed(() => props.selectable),
  handleSort,
  toggleRowSelection
})
</script>
```

```vue
<!-- src/components/compound/DataTableHeader.vue -->
<template>
  <thead class="bg-gray-50 dark:bg-gray-800">
    <tr>
      <th
        v-if="selectable"
        class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
      >
        <input
          type="checkbox"
          :checked="isAllSelected"
          :indeterminate="isIndeterminate"
          @change="toggleAllSelection"
          class="rounded border-gray-300 dark:border-gray-600 focus:ring-primary-500"
        />
      </th>
      
      <th
        v-for="column in columns"
        :key="column.key"
        :class="headerCellClasses(column)"
        @click="column.sortable !== false && sortable ? handleSort(column.key) : null"
      >
        <div class="flex items-center gap-2">
          <span>{{ column.title }}</span>
          
          <div
            v-if="column.sortable !== false && sortable"
            class="flex flex-col"
          >
            <ChevronUpIcon
              :class="[
                'w-3 h-3 transition-colors',
                sortColumn === column.key && sortDirection === 'asc'
                  ? 'text-primary-600'
                  : 'text-gray-400'
              ]"
            />
            <ChevronDownIcon
              :class="[
                'w-3 h-3 transition-colors',
                sortColumn === column.key && sortDirection === 'desc'
                  ? 'text-primary-600'
                  : 'text-gray-400'
              ]"
            />
          </div>
        </div>
      </th>
    </tr>
  </thead>
</template>

<script setup lang="ts">
import { inject, computed } from 'vue'
import { ChevronUpIcon, ChevronDownIcon } from '@heroicons/vue/24/outline'

const tableContext = inject('table-context')

if (!tableContext) {
  throw new Error('DataTableHeader must be used within DataTable')
}

const {
  columns,
  data,
  sortColumn,
  sortDirection,
  selectedRows,
  sortable,
  selectable,
  handleSort,
  toggleRowSelection
} = tableContext

const isAllSelected = computed(() => 
  data.value.length > 0 && selectedRows.value.size === data.value.length
)

const isIndeterminate = computed(() => 
  selectedRows.value.size > 0 && selectedRows.value.size < data.value.length
)

const headerCellClasses = (column: any) => [
  'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
  {
    'cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700': 
      column.sortable !== false && sortable.value
  }
]

const toggleAllSelection = () => {
  if (isAllSelected.value) {
    selectedRows.value.clear()
  } else {
    data.value.forEach(row => selectedRows.value.add(row.id))
  }
}
</script>
```

### 3. Render Props Pattern
```vue
<!-- src/components/patterns/InfiniteScroll.vue -->
<template>
  <div class="space-y-4">
    <!-- Render items -->
    <slot
      v-for="item in items"
      :key="item.id"
      :item="item"
      :index="items.indexOf(item)"
    />
    
    <!-- Loading more indicator -->
    <div
      v-if="isLoading"
      class="flex justify-center py-8"
    >
      <LoadingSpinner size="md" />
    </div>
    
    <!-- Load more trigger -->
    <div
      ref="loadMoreRef"
      class="h-4"
      :class="{ 'opacity-0': !hasMore }"
    />
    
    <!-- Error state -->
    <div
      v-if="error"
      class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4"
    >
      <p class="text-red-600 dark:text-red-400">
        {{ error }}
      </p>
      <button
        @click="retry"
        class="mt-2 text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200"
      >
        Try again
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import LoadingSpinner from '@/components/base/LoadingSpinner.vue'

interface Props {
  items: any[]
  hasMore: boolean
  isLoading: boolean
  error?: string
  threshold?: number
}

const props = withDefaults(defineProps<Props>(), {
  threshold: 200
})

interface Emits {
  loadMore: []
  retry: []
}

const emit = defineEmits<Emits>()

const loadMoreRef = ref<HTMLElement>()
let observer: IntersectionObserver | null = null

const setupIntersectionObserver = () => {
  if (!loadMoreRef.value) return
  
  observer = new IntersectionObserver(
    (entries) => {
      const entry = entries[0]
      if (entry.isIntersecting && props.hasMore && !props.isLoading) {
        emit('loadMore')
      }
    },
    {
      rootMargin: `${props.threshold}px`
    }
  )
  
  observer.observe(loadMoreRef.value)
}

const cleanup = () => {
  if (observer) {
    observer.disconnect()
    observer = null
  }
}

const retry = () => {
  emit('retry')
}

onMounted(() => {
  setupIntersectionObserver()
})

onUnmounted(() => {
  cleanup()
})

watch(() => props.hasMore, (hasMore) => {
  if (!hasMore) {
    cleanup()
  } else {
    setupIntersectionObserver()
  }
})
</script>
```

### 4. Provider Pattern for State Management
```vue
<!-- src/components/providers/NotificationProvider.vue -->
<template>
  <div>
    <slot />
    
    <!-- Notification container -->
    <Teleport to="body">
      <div
        class="fixed top-4 right-4 z-50 space-y-2"
        role="region"
        aria-label="Notifications"
      >
        <TransitionGroup
          name="notification"
          tag="div"
          class="space-y-2"
        >
          <NotificationItem
            v-for="notification in notifications"
            :key="notification.id"
            :notification="notification"
            @dismiss="removeNotification"
          />
        </TransitionGroup>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { provide, ref } from 'vue'
import { nanoid } from 'nanoid'
import NotificationItem from './NotificationItem.vue'

interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
  duration?: number
  persistent?: boolean
}

const notifications = ref<Notification[]>([])

const addNotification = (notification: Omit<Notification, 'id'>) => {
  const id = nanoid()
  const newNotification: Notification = {
    ...notification,
    id,
    duration: notification.duration ?? 5000
  }
  
  notifications.value.push(newNotification)
  
  // Auto-dismiss after duration
  if (!notification.persistent) {
    setTimeout(() => {
      removeNotification(id)
    }, newNotification.duration)
  }
  
  return id
}

const removeNotification = (id: string) => {
  const index = notifications.value.findIndex(n => n.id === id)
  if (index > -1) {
    notifications.value.splice(index, 1)
  }
}

const clearAll = () => {
  notifications.value = []
}

// Provide notification methods
provide('notifications', {
  addNotification,
  removeNotification,
  clearAll,
  notifications
})
</script>

<style scoped>
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.notification-move {
  transition: transform 0.3s ease;
}
</style>
```

### 5. Advanced Tailwind CSS Utilities
```vue
<!-- src/components/advanced/ConversationCard.vue -->
<template>
  <article 
    :class="cardClasses"
    @click="$emit('click', conversation)"
    @keydown.enter="$emit('click', conversation)"
    @keydown.space.prevent="$emit('click', conversation)"
    tabindex="0"
    role="button"
    :aria-label="`Open conversation: ${conversation.title}`"
  >
    <!-- Header -->
    <header class="p-4 border-b border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3 min-w-0">
          <div class="flex-shrink-0">
            <div 
              :class="statusIndicatorClasses"
              :title="statusText"
            />
          </div>
          
          <div class="min-w-0 flex-1">
            <h3 class="font-medium text-gray-900 dark:text-white truncate">
              {{ conversation.title }}
            </h3>
            <p class="text-sm text-gray-500 dark:text-gray-400 truncate">
              {{ conversation.lastMessage?.preview || 'No messages' }}
            </p>
          </div>
        </div>
        
        <div class="flex items-center gap-2">
          <span class="text-xs text-gray-500 dark:text-gray-400">
            {{ formatRelativeTime(conversation.updatedAt) }}
          </span>
          
          <div
            v-if="conversation.messageCount > 0"
            class="bg-primary-100 dark:bg-primary-900 text-primary-800 dark:text-primary-200 text-xs px-2 py-1 rounded-full"
          >
            {{ conversation.messageCount }}
          </div>
        </div>
      </div>
    </header>
    
    <!-- Content -->
    <div class="p-4">
      <div class="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
        <div class="flex items-center gap-4">
          <span>{{ conversation.participants.length }} participants</span>
          <span>{{ formatFileSize(conversation.totalSize) }}</span>
        </div>
        
        <div class="flex items-center gap-2">
          <span 
            v-if="conversation.hasAttachments"
            class="inline-flex items-center gap-1"
          >
            <PaperClipIcon class="w-4 h-4" />
            {{ conversation.attachmentCount }}
          </span>
          
          <span
            v-if="conversation.isStarred"
            class="text-yellow-500"
          >
            <StarIcon class="w-4 h-4 fill-current" />
          </span>
        </div>
      </div>
    </div>
    
    <!-- Actions -->
    <footer class="px-4 py-3 bg-gray-50 dark:bg-gray-800/50 border-t border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <TagList 
            :tags="conversation.tags" 
            size="sm"
            max-visible="3"
          />
        </div>
        
        <div class="flex items-center gap-1">
          <button
            @click.stop="$emit('star', conversation)"
            class="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            :aria-label="conversation.isStarred ? 'Unstar conversation' : 'Star conversation'"
          >
            <StarIcon
              :class="[
                'w-4 h-4',
                conversation.isStarred 
                  ? 'text-yellow-500 fill-current' 
                  : 'text-gray-400 hover:text-yellow-500'
              ]"
            />
          </button>
          
          <button
            @click.stop="$emit('archive', conversation)"
            class="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            :aria-label="conversation.isArchived ? 'Unarchive conversation' : 'Archive conversation'"
          >
            <ArchiveBoxIcon class="w-4 h-4 text-gray-400 hover:text-gray-600" />
          </button>
          
          <button
            @click.stop="$emit('delete', conversation)"
            class="p-1 rounded hover:bg-red-100 dark:hover:bg-red-900/20 transition-colors"
            aria-label="Delete conversation"
          >
            <TrashIcon class="w-4 h-4 text-gray-400 hover:text-red-500" />
          </button>
        </div>
      </div>
    </footer>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { 
  PaperClipIcon, 
  StarIcon, 
  ArchiveBoxIcon, 
  TrashIcon 
} from '@heroicons/vue/24/outline'
import { formatDistanceToNow } from 'date-fns'
import TagList from '@/components/base/TagList.vue'
import type { Conversation } from '@/types/conversation'

interface Props {
  conversation: Conversation
  isActive?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isActive: false
})

interface Emits {
  click: [conversation: Conversation]
  star: [conversation: Conversation]
  archive: [conversation: Conversation]
  delete: [conversation: Conversation]
}

const emit = defineEmits<Emits>()

const cardClasses = computed(() => [
  // Base styles
  'block w-full text-left bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm',
  
  // Interactive states
  'hover:shadow-md hover:border-gray-300 dark:hover:border-gray-600',
  'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
  'active:scale-[0.98]',
  
  // Transitions
  'transition-all duration-200',
  
  // Active state
  {
    'ring-2 ring-primary-500 border-primary-500': props.isActive,
    'bg-primary-50 dark:bg-primary-900/20': props.isActive
  }
])

const statusIndicatorClasses = computed(() => [
  'w-2 h-2 rounded-full',
  {
    'bg-green-500': props.conversation.status === 'active',
    'bg-yellow-500': props.conversation.status === 'pending',
    'bg-red-500': props.conversation.status === 'error',
    'bg-gray-400': props.conversation.status === 'archived'
  }
])

const statusText = computed(() => {
  const statusMap = {
    active: 'Active conversation',
    pending: 'Pending response',
    error: 'Error occurred',
    archived: 'Archived conversation'
  }
  return statusMap[props.conversation.status] || 'Unknown status'
})

const formatRelativeTime = (date: string) => {
  return formatDistanceToNow(new Date(date), { addSuffix: true })
}

const formatFileSize = (bytes: number) => {
  const sizes = ['B', 'KB', 'MB', 'GB']
  if (bytes === 0) return '0 B'
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}
</script>
```

## Component Testing and Quality Assurance

### 1. Advanced Testing Patterns
```typescript
// src/components/base/__tests__/BaseModal.test.ts
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { nextTick } from 'vue'
import BaseModal from '../BaseModal.vue'

describe('BaseModal', () => {
  let wrapper: VueWrapper<any>
  
  beforeEach(() => {
    // Mock portal target
    const portalTarget = document.createElement('div')
    portalTarget.id = 'modal-portal'
    document.body.appendChild(portalTarget)
  })
  
  afterEach(() => {
    wrapper?.unmount()
    document.body.innerHTML = ''
  })

  describe('Accessibility', () => {
    it('has proper ARIA attributes', () => {
      wrapper = mount(BaseModal, {
        props: {
          isOpen: true,
          title: 'Test Modal'
        }
      })
      
      const modal = wrapper.find('[role="dialog"]')
      expect(modal.attributes('aria-modal')).toBe('true')
      expect(modal.attributes('aria-labelledby')).toBeTruthy()
    })
    
    it('traps focus within modal', async () => {
      wrapper = mount(BaseModal, {
        props: {
          isOpen: true,
          title: 'Test Modal'
        },
        slots: {
          default: `
            <input data-testid="first-input" />
            <input data-testid="second-input" />
            <button data-testid="submit-button">Submit</button>
          `
        }
      })
      
      await nextTick()
      
      const firstInput = wrapper.find('[data-testid="first-input"]')
      const submitButton = wrapper.find('[data-testid="submit-button"]')
      
      // Focus should be trapped within modal
      expect(document.activeElement).toBe(firstInput.element)
      
      // Tab to last element
      await submitButton.trigger('keydown', { key: 'Tab' })
      expect(document.activeElement).toBe(firstInput.element)
    })
    
    it('returns focus to trigger element on close', async () => {
      const triggerButton = document.createElement('button')
      document.body.appendChild(triggerButton)
      triggerButton.focus()
      
      wrapper = mount(BaseModal, {
        props: {
          isOpen: true,
          title: 'Test Modal'
        }
      })
      
      await wrapper.setProps({ isOpen: false })
      await nextTick()
      
      expect(document.activeElement).toBe(triggerButton)
    })
  })
  
  describe('Keyboard Navigation', () => {
    it('closes on Escape key', async () => {
      wrapper = mount(BaseModal, {
        props: {
          isOpen: true,
          title: 'Test Modal',
          closeOnEscape: true
        }
      })
      
      await wrapper.trigger('keydown', { key: 'Escape' })
      expect(wrapper.emitted('close')).toHaveLength(1)
    })
    
    it('does not close on Escape when closeOnEscape is false', async () => {
      wrapper = mount(BaseModal, {
        props: {
          isOpen: true,
          title: 'Test Modal',
          closeOnEscape: false
        }
      })
      
      await wrapper.trigger('keydown', { key: 'Escape' })
      expect(wrapper.emitted('close')).toBeUndefined()
    })
  })
  
  describe('Animation and Transitions', () => {
    it('applies correct transition classes', async () => {
      wrapper = mount(BaseModal, {
        props: {
          isOpen: false,
          title: 'Test Modal'
        }
      })
      
      await wrapper.setProps({ isOpen: true })
      await nextTick()
      
      const modal = wrapper.find('[role="dialog"]')
      expect(modal.classes()).toContain('modal-enter-active')
    })
  })
})
```

### 2. Performance Testing
```typescript
// src/components/virtualized/__tests__/VirtualList.performance.test.ts
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import VirtualList from '../VirtualList.vue'

describe('VirtualList Performance', () => {
  it('renders large datasets efficiently', async () => {
    const largeDataset = Array.from({ length: 10000 }, (_, i) => ({
      id: i,
      name: `Item ${i}`,
      description: `Description for item ${i}`
    }))
    
    const startTime = performance.now()
    
    const wrapper = mount(VirtualList, {
      props: {
        items: largeDataset,
        itemHeight: 60,
        height: 400
      },
      slots: {
        default: `
          <template #default="{ item }">
            <div class="p-4 border-b">
              <h3>{{ item.name }}</h3>
              <p>{{ item.description }}</p>
            </div>
          </template>
        `
      }
    })
    
    const renderTime = performance.now() - startTime
    
    // Should render in under 100ms
    expect(renderTime).toBeLessThan(100)
    
    // Should only render visible items
    const renderedItems = wrapper.findAll('[data-testid="virtual-item"]')
    expect(renderedItems.length).toBeLessThan(20) // Only visible items
  })
  
  it('maintains smooth scrolling performance', async () => {
    const wrapper = mount(VirtualList, {
      props: {
        items: Array.from({ length: 1000 }, (_, i) => ({ id: i, name: `Item ${i}` })),
        itemHeight: 50,
        height: 300
      }
    })
    
    const container = wrapper.find('[data-testid="virtual-container"]')
    const scrollSpy = vi.fn()
    
    container.element.addEventListener('scroll', scrollSpy)
    
    // Simulate rapid scrolling
    for (let i = 0; i < 100; i++) {
      await container.trigger('scroll', { target: { scrollTop: i * 10 } })
    }
    
    expect(scrollSpy).toHaveBeenCalledTimes(100)
  })
})
```

### 3. Visual Regression Testing
```typescript
// src/components/__tests__/visual-regression.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { toMatchImageSnapshot } from 'jest-image-snapshot'
import BaseButton from '@/components/base/BaseButton.vue'

expect.extend({ toMatchImageSnapshot })

describe('Visual Regression Tests', () => {
  it('BaseButton renders correctly in all variants', async () => {
    const variants = ['primary', 'secondary', 'tertiary', 'danger', 'ghost']
    
    for (const variant of variants) {
      const wrapper = mount(BaseButton, {
        props: { variant },
        slots: { default: `${variant} Button` }
      })
      
      // Create screenshot
      const screenshot = await wrapper.element.toMatchImageSnapshot({
        testName: `button-${variant}`,
        threshold: 0.1
      })
      
      expect(screenshot).toMatchImageSnapshot()
    }
  })
  
  it('Modal renders correctly in different states', async () => {
    const states = [
      { isOpen: true, title: 'Basic Modal' },
      { isOpen: true, title: 'Modal with Footer', hasFooter: true },
      { isOpen: true, title: 'Large Modal', size: 'lg' }
    ]
    
    for (const state of states) {
      const wrapper = mount(BaseModal, {
        props: state,
        slots: {
          default: '<p>Modal content</p>',
          footer: state.hasFooter ? '<button>Save</button>' : undefined
        }
      })
      
      const screenshot = await wrapper.element.toMatchImageSnapshot({
        testName: `modal-${state.title.toLowerCase().replace(' ', '-')}`,
        threshold: 0.1
      })
      
      expect(screenshot).toMatchImageSnapshot()
    }
  })
})
```

## Component Documentation and Storybook

### 1. Storybook Configuration
```typescript
// .storybook/main.ts
import type { StorybookConfig } from '@storybook/vue3-vite'
import { mergeConfig } from 'vite'
import { resolve } from 'path'

const config: StorybookConfig = {
  stories: ['../src/**/*.stories.@(js|jsx|ts|tsx|mdx)'],
  addons: [
    '@storybook/addon-links',
    '@storybook/addon-essentials',
    '@storybook/addon-interactions',
    '@storybook/addon-a11y',
    '@storybook/addon-viewport',
    '@storybook/addon-docs'
  ],
  framework: {
    name: '@storybook/vue3-vite',
    options: {}
  },
  typescript: {
    check: false,
    reactDocgen: 'react-docgen-typescript',
    reactDocgenTypescriptOptions: {
      shouldExtractLiteralValuesFromEnum: true,
      propFilter: (prop) => (prop.parent ? !/node_modules/.test(prop.parent.fileName) : true)
    }
  },
  viteFinal: async (config) => {
    return mergeConfig(config, {
      resolve: {
        alias: {
          '@': resolve(__dirname, '../src')
        }
      }
    })
  }
}

export default config
```

### 2. Component Stories
```typescript
// src/components/base/BaseButton.stories.ts
import type { Meta, StoryObj } from '@storybook/vue3'
import { userEvent, within } from '@storybook/testing-library'
import { expect } from '@storybook/jest'
import BaseButton from './BaseButton.vue'

const meta: Meta<typeof BaseButton> = {
  title: 'Base/Button',
  component: BaseButton,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'A versatile button component with multiple variants, sizes, and states.'
      }
    }
  },
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['primary', 'secondary', 'tertiary', 'danger', 'ghost']
    },
    size: {
      control: { type: 'select' },
      options: ['xs', 'sm', 'md', 'lg', 'xl']
    },
    disabled: { control: 'boolean' },
    loading: { control: 'boolean' },
    fullWidth: { control: 'boolean' }
  },
  args: {
    variant: 'primary',
    size: 'md',
    disabled: false,
    loading: false,
    fullWidth: false
  }
}

export default meta
type Story = StoryObj<typeof BaseButton>

export const Primary: Story = {
  args: {
    variant: 'primary'
  },
  render: (args) => ({
    components: { BaseButton },
    setup() {
      return { args }
    },
    template: '<BaseButton v-bind="args">Primary Button</BaseButton>'
  })
}

export const AllVariants: Story = {
  render: () => ({
    components: { BaseButton },
    template: `
      <div class="space-y-4">
        <div class="flex gap-4">
          <BaseButton variant="primary">Primary</BaseButton>
          <BaseButton variant="secondary">Secondary</BaseButton>
          <BaseButton variant="tertiary">Tertiary</BaseButton>
          <BaseButton variant="danger">Danger</BaseButton>
          <BaseButton variant="ghost">Ghost</BaseButton>
        </div>
        
        <div class="flex gap-4">
          <BaseButton variant="primary" loading>Loading</BaseButton>
          <BaseButton variant="secondary" disabled>Disabled</BaseButton>
          <BaseButton variant="tertiary" iconOnly>A</BaseButton>
        </div>
        
        <div class="space-y-2">
          <BaseButton variant="primary" fullWidth>Full Width</BaseButton>
          <BaseButton variant="secondary" fullWidth>Full Width Secondary</BaseButton>
        </div>
      </div>
    `
  })
}

export const WithIcons: Story = {
  render: () => ({
    components: { BaseButton },
    template: `
      <div class="flex gap-4">
        <BaseButton variant="primary">
          <template #icon-left>
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 2L3 7v11h4v-6h6v6h4V7l-7-5z"/>
            </svg>
          </template>
          Home
        </BaseButton>
        
        <BaseButton variant="secondary">
          Save
          <template #icon-right>
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/>
            </svg>
          </template>
        </BaseButton>
      </div>
    `
  })
}

export const InteractionTest: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const button = canvas.getByRole('button')
    
    await userEvent.click(button)
    await expect(button).toHaveAttribute('aria-pressed', 'true')
  }
}
```

### 3. Component Documentation
```typescript
// src/components/base/BaseInput.stories.ts
import type { Meta, StoryObj } from '@storybook/vue3'
import BaseInput from './BaseInput.vue'

const meta: Meta<typeof BaseInput> = {
  title: 'Base/Input',
  component: BaseInput,
  parameters: {
    docs: {
      description: {
        component: `
# BaseInput Component

A flexible input component with comprehensive features:

## Features
- Multiple variants (default, filled, outlined)
- Size options (sm, md, lg)
- Built-in validation states
- Icon support (leading and trailing)
- Clearable functionality
- Accessibility compliant (WCAG 2.1 AA)

## Usage

\`\`\`vue
<BaseInput
  v-model="value"
  label="Email"
  type="email"
  placeholder="Enter your email"
  :error-message="error"
  required
/>
\`\`\`

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| modelValue | string | '' | The input value |
| type | string | 'text' | Input type |
| label | string | - | Input label |
| placeholder | string | - | Placeholder text |
| disabled | boolean | false | Disabled state |
| required | boolean | false | Required field |
| errorMessage | string | - | Error message to display |

## Events

| Event | Payload | Description |
|-------|---------|-------------|
| update:modelValue | string | Emitted when value changes |
| blur | FocusEvent | Emitted on blur |
| focus | FocusEvent | Emitted on focus |
        `
      }
    }
  }
}

export default meta
```

## Component Documentation
- **Storybook Integration**: Interactive component showcase with live examples and controls
- **TypeScript Documentation**: Comprehensive interfaces and type definitions for all props and events
- **Usage Examples**: Real-world implementation patterns with code snippets
- **Design System Integration**: Seamless integration with Tailwind CSS design tokens and utilities
- **Accessibility Guidelines**: WCAG 2.1 AA compliance documentation with testing procedures
- **Performance Guidelines**: Optimization patterns for large-scale applications with benchmarks
- **Testing Documentation**: Unit, integration, and visual regression testing strategies

## Browser Performance Optimization
- **Lazy Loading**: Intersection Observer-based lazy loading for off-screen components
- **Virtual Scrolling**: Efficient rendering of large lists with minimal DOM nodes
- **Code Splitting**: Dynamic imports and route-based code splitting strategies
- **Image Optimization**: Responsive images with lazy loading and modern format support
- **Memory Management**: Proper cleanup of event listeners and observers
- **Bundle Analysis**: Webpack Bundle Analyzer integration for optimization insights