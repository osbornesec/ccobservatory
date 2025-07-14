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

## Component Documentation
- Storybook setup for component documentation
- Props and events documentation
- Usage examples and best practices
- Design system token documentation
- Accessibility guidelines for each component

## Browser Performance Optimization
- Lazy loading for off-screen components
- Virtual scrolling for large lists
- Image optimization and lazy loading
- Code splitting and dynamic imports
- Service worker implementation for caching