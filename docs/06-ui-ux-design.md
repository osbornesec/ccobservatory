# 🎨 UI/UX Design Specifications - Claude Code Observatory

## 🎯 **Design Philosophy**

### **Core Design Principles**

#### **1. Clarity First**
- **Clean Information Hierarchy:** Clear visual distinction between different types of content
- **Uncluttered Interface:** Minimal UI elements with purposeful design
- **Intuitive Navigation:** Self-explanatory navigation patterns
- **Consistent Design Language:** Unified visual system across all components

#### **2. Real-Time Focus**
- **Live Updates:** Seamless real-time updates without disruptive refreshes
- **Visual Indicators:** Clear status indicators for active sessions and connections
- **Smooth Animations:** Subtle animations for state changes and new content
- **Instant Feedback:** Immediate visual response to user actions

#### **3. Developer-Centric**
- **Code-Friendly Typography:** Optimized fonts for code readability
- **Syntax Highlighting:** Consistent, accessible syntax highlighting
- **Dark/Light Themes:** Full theme support for developer preferences
- **Keyboard Shortcuts:** Comprehensive keyboard navigation for power users

#### **4. Data-Dense but Readable**
- **Efficient Space Usage:** Maximum information density without overwhelming
- **Progressive Disclosure:** Show details on demand, keep overview clean
- **Scannable Layouts:** Easy to scan for relevant information
- **Visual Grouping:** Clear grouping of related information

## 🎨 **Visual Design System**

### **Color Palette**

#### **Primary Colors**
```css
:root {
  /* Brand Colors */
  --claude-orange: #FF6B35;      /* Primary brand accent */
  --deep-blue: #2563EB;          /* Primary actions */
  --forest-green: #059669;       /* Success states */
  --warm-red: #DC2626;           /* Error states */
  
  /* Neutral Palette */
  --white: #FFFFFF;              /* Primary backgrounds */
  --gray-50: #F9FAFB;           /* Light backgrounds */
  --gray-100: #F3F4F6;          /* Secondary backgrounds */
  --gray-200: #E5E7EB;          /* Borders */
  --gray-300: #D1D5DB;          /* Disabled elements */
  --gray-400: #9CA3AF;          /* Placeholders */
  --gray-500: #6B7280;          /* Secondary text */
  --gray-600: #4B5563;          /* Primary text */
  --gray-700: #374151;          /* Headings */
  --gray-800: #1F2937;          /* High contrast text */
  --gray-900: #111827;          /* Maximum contrast */
  
  /* Semantic Colors */
  --info: #0EA5E9;              /* Information */
  --warning: #F59E0B;           /* Warnings */
  --success: #10B981;           /* Success feedback */
  --error: #EF4444;             /* Error feedback */
}
```

#### **Theme System**
```css
/* Light Theme (Default) */
.theme-light {
  --bg-primary: var(--white);
  --bg-secondary: var(--gray-50);
  --bg-tertiary: var(--gray-100);
  --bg-quaternary: var(--gray-200);
  
  --text-primary: var(--gray-800);
  --text-secondary: var(--gray-600);
  --text-tertiary: var(--gray-500);
  --text-quaternary: var(--gray-400);
  
  --border-primary: var(--gray-200);
  --border-secondary: var(--gray-300);
  
  --accent-primary: var(--deep-blue);
  --accent-secondary: var(--claude-orange);
}

/* Dark Theme */
.theme-dark {
  --bg-primary: var(--gray-900);
  --bg-secondary: var(--gray-800);
  --bg-tertiary: var(--gray-700);
  --bg-quaternary: var(--gray-600);
  
  --text-primary: var(--gray-100);
  --text-secondary: var(--gray-300);
  --text-tertiary: var(--gray-400);
  --text-quaternary: var(--gray-500);
  
  --border-primary: var(--gray-700);
  --border-secondary: var(--gray-600);
  
  --accent-primary: #3B82F6;
  --accent-secondary: #FB923C;
}
```

### **Typography System**

#### **Font Families**
```css
:root {
  /* Primary Font - Interface */
  --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 
                  Roboto, 'Helvetica Neue', Arial, sans-serif;
  
  /* Monospace Font - Code */
  --font-mono: 'JetBrains Mono', 'SF Mono', Monaco, 'Cascadia Code', 
               'Roboto Mono', Consolas, 'Courier New', monospace;
  
  /* Display Font - Headings */
  --font-display: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 
                  Roboto, sans-serif;
}
```

#### **Typography Scale**
```css
:root {
  /* Font Sizes */
  --text-xs: 0.75rem;     /* 12px - Labels, metadata */
  --text-sm: 0.875rem;    /* 14px - Secondary text */
  --text-base: 1rem;      /* 16px - Body text */
  --text-lg: 1.125rem;    /* 18px - Large body text */
  --text-xl: 1.25rem;     /* 20px - Small headings */
  --text-2xl: 1.5rem;     /* 24px - Section headings */
  --text-3xl: 1.875rem;   /* 30px - Page headings */
  --text-4xl: 2.25rem;    /* 36px - Large headings */
  
  /* Line Heights */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
  
  /* Font Weights */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
}
```

### **Spacing System**

```css
:root {
  /* Spacing Scale (based on 0.25rem = 4px) */
  --space-0: 0;
  --space-1: 0.25rem;     /* 4px */
  --space-2: 0.5rem;      /* 8px */
  --space-3: 0.75rem;     /* 12px */
  --space-4: 1rem;        /* 16px */
  --space-5: 1.25rem;     /* 20px */
  --space-6: 1.5rem;      /* 24px */
  --space-8: 2rem;        /* 32px */
  --space-10: 2.5rem;     /* 40px */
  --space-12: 3rem;       /* 48px */
  --space-16: 4rem;       /* 64px */
  --space-20: 5rem;       /* 80px */
  --space-24: 6rem;       /* 96px */
  
  /* Component Spacing */
  --padding-component: var(--space-4);
  --margin-component: var(--space-6);
  --gap-component: var(--space-4);
}
```

## 🖼️ **Interface Components**

### **Main Application Layout**

```
┌─────────────────────────────────────────────────────────┐
│ Header (Navigation + Status + User Controls)           │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌───────────────────────────────────┐  │
│ │             │ │                                   │  │
│ │  Sidebar    │ │        Main Content Area          │  │
│ │             │ │                                   │  │
│ │ - Projects  │ │  ┌─ Dashboard View ─────────────┐ │  │
│ │ - Filters   │ │  │                             │ │  │
│ │ - Quick     │ │  │ - Live Conversations        │ │  │
│ │   Actions   │ │  │ - Analytics Charts          │ │  │
│ │ - Status    │ │  │ - Recent Activity           │ │  │
│ │             │ │  │                             │ │  │
│ │             │ │  └─────────────────────────────┘ │  │
│ │             │ │                                   │  │
│ └─────────────┘ └───────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│ Status Bar (Performance + Connection + Notifications)  │
└─────────────────────────────────────────────────────────┘
```

#### **Header Component**
```vue
<template>
  <header class="header">
    <div class="header-left">
      <div class="logo">
        <IconObservatory class="logo-icon" />
        <h1 class="logo-text">Claude Code Observatory</h1>
      </div>
      <nav class="main-nav">
        <NavItem to="/dashboard" icon="home">Dashboard</NavItem>
        <NavItem to="/conversations" icon="chat">Conversations</NavItem>
        <NavItem to="/projects" icon="folder">Projects</NavItem>
        <NavItem to="/analytics" icon="chart">Analytics</NavItem>
      </nav>
    </div>
    
    <div class="header-center">
      <SearchBar placeholder="Search conversations..." />
    </div>
    
    <div class="header-right">
      <ConnectionStatus />
      <NotificationCenter />
      <ThemeToggle />
      <UserMenu />
    </div>
  </header>
</template>

<style scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-6);
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-primary);
  height: 4rem;
}

.header-left, .header-right {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-weight: var(--font-bold);
  color: var(--text-primary);
}

.main-nav {
  display: flex;
  gap: var(--space-2);
  margin-left: var(--space-8);
}
</style>
```

### **Dashboard Views**

#### **1. Live Conversations Dashboard**

```
┌─ Live Conversations ─────────────────────────────────────┐
│ 🔴 3 active conversations               [📊] [⚙️] [🔄] │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ ┌─ Project-A ── Session abc123... ── 2m ago ──────────┐ │
│ │ 👤 How can I fix this authentication error?        │ │
│ │                                                     │ │
│ │ 🤖 I'll help you debug the authentication issue.   │ │
│ │    Let me examine your auth configuration...       │ │
│ │                                                     │ │
│ │    🔧 [Read] src/auth/config.js                    │ │
│ │    ├─ Input: file_path: "src/auth/config.js"      │ │
│ │    └─ Output: [auth configuration content...]      │ │
│ │                                                     │ │
│ │ 🤖 I can see the issue. The JWT secret is...       │ │
│ │                                                     │ │
│ │ [💬 View Full] [📋 Copy] [🔗 Share] [🔖 Bookmark] │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ ┌─ Project-B ── Session def456... ── 5m ago ──────────┐ │
│ │ 👤 Create a new React component for...              │ │
│ │ 🤖 I'll help you create a React component...        │ │
│ │ [💬 View Full] [📋 Copy] [🔗 Share]                │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ [Load More...] [Export All] [🔍 Search All]            │
└──────────────────────────────────────────────────────────┘
```

#### **2. Analytics Dashboard**

```
┌─ Analytics & Insights ──────────────────────────────────┐
│ 📅 Last 30 days                           [Filter ▼]   │
├──────────────────────────────────────────────────────────┤
│ ┌─ Overview ─────────┐ ┌─ Tool Usage ─────────────────┐ │
│ │ 📊 342 conversations│ │ 🔧 Read        234 (45%)   │ │
│ │ ⏱️  4.2m avg length │ │ 📝 Write       119 (23%)   │ │
│ │ 🎯 89% success rate │ │ 🔍 Search       93 (18%)   │ │
│ │ 💰 $23.45 this month│ │ ⚡ Bash         72 (14%)   │ │
│ └────────────────────┘ └─────────────────────────────┘ │
│                                                          │
│ ┌─ Conversation Trends ──────────────────────────────┐  │
│ │     📈 Daily Conversations                         │  │
│ │    /  \                                            │  │
│ │   /    \        /\                                 │  │
│ │  /      \      /  \                                │  │
│ │ /        \____/    \___________________________    │  │
│ │ Mon  Tue  Wed  Thu  Fri  Sat  Sun               │  │
│ └────────────────────────────────────────────────────┘  │
│                                                          │
│ ┌─ AI Insights ──────────────────────────────────────┐  │
│ │ 💡 You're most productive between 9-11 AM         │  │
│ │ 🎯 Consider using more specific prompts for Read   │  │
│ │ 🚀 Your debugging sessions are 40% faster lately  │  │
│ │ 📚 Shared 3 conversations with team this week     │  │
│ └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### **Component Library**

#### **Message Bubble Component**
```vue
<template>
  <div :class="messageClasses">
    <div class="message-header">
      <div class="message-meta">
        <span :class="typeClasses">{{ message.type.toUpperCase() }}</span>
        <span class="timestamp">{{ formatTime(message.timestamp) }}</span>
        <span v-if="message.session_id" class="session-id">
          {{ message.session_id.slice(0, 8) }}
        </span>
      </div>
      <div class="message-actions">
        <button @click="copyMessage" class="action-btn" title="Copy">
          <IconCopy />
        </button>
        <button @click="shareMessage" class="action-btn" title="Share">
          <IconShare />
        </button>
      </div>
    </div>
    
    <div class="message-content">
      <div v-if="message.tool_usage" class="tool-usage">
        <ToolUsageDisplay :tool-usage="message.tool_usage" />
      </div>
      
      <div class="message-text">
        <MessageContent :content="message.content" />
      </div>
    </div>
    
    <div v-if="message.parent_id" class="message-thread">
      <IconArrowReply />
      <span>Reply to {{ message.parent_id.slice(0, 8) }}</span>
    </div>
  </div>
</template>

<style scoped>
.message {
  @apply rounded-lg border p-4 mb-4 transition-all duration-200;
  background: var(--bg-secondary);
  border-color: var(--border-primary);
}

.message:hover {
  background: var(--bg-tertiary);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.message-user {
  border-left: 4px solid var(--accent-primary);
}

.message-assistant {
  border-left: 4px solid var(--success);
}

.message-system {
  border-left: 4px solid var(--warning);
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}

.message-meta {
  display: flex;
  gap: var(--space-3);
  align-items: center;
}

.type-badge {
  @apply px-2 py-1 rounded text-xs font-bold uppercase;
}

.type-user {
  background: var(--accent-primary);
  color: white;
}

.type-assistant {
  background: var(--success);
  color: white;
}

.type-system {
  background: var(--warning);
  color: var(--gray-900);
}

.timestamp {
  color: var(--text-tertiary);
  font-size: var(--text-sm);
  font-family: var(--font-mono);
}

.session-id {
  color: var(--text-secondary);
  font-size: var(--text-xs);
  font-family: var(--font-mono);
  background: var(--bg-quaternary);
  padding: var(--space-1) var(--space-2);
  border-radius: 0.25rem;
}

.message-actions {
  display: flex;
  gap: var(--space-2);
  opacity: 0;
  transition: opacity 0.2s;
}

.message:hover .message-actions {
  opacity: 1;
}

.action-btn {
  @apply p-2 rounded hover:bg-gray-100 transition-colors;
  color: var(--text-secondary);
}

.action-btn:hover {
  color: var(--text-primary);
  background: var(--bg-quaternary);
}
</style>
```

#### **Tool Usage Display Component**
```vue
<template>
  <div class="tool-usage">
    <div class="tool-header">
      <div class="tool-info">
        <IconTool class="tool-icon" />
        <span class="tool-name">{{ toolUsage.tool_name }}</span>
        <span v-if="toolUsage.execution_time_ms" class="execution-time">
          {{ toolUsage.execution_time_ms }}ms
        </span>
        <span :class="statusClasses">{{ toolUsage.status }}</span>
      </div>
      <button @click="toggleExpanded" class="expand-btn">
        <IconChevronDown :class="{ 'rotate-180': isExpanded }" />
      </button>
    </div>
    
    <div v-if="isExpanded" class="tool-details">
      <div v-if="toolUsage.input" class="tool-section">
        <h4 class="section-title">Input</h4>
        <CodeBlock :code="formatInput(toolUsage.input)" language="json" />
      </div>
      
      <div v-if="toolUsage.output" class="tool-section">
        <h4 class="section-title">Output</h4>
        <CodeBlock 
          :code="toolUsage.output" 
          :language="detectLanguage(toolUsage.output)"
          :max-height="400"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.tool-usage {
  @apply border rounded-md mb-3;
  background: var(--bg-tertiary);
  border-color: var(--border-secondary);
}

.tool-header {
  @apply flex items-center justify-between p-3 cursor-pointer;
}

.tool-header:hover {
  background: var(--bg-quaternary);
}

.tool-info {
  @apply flex items-center gap-2;
}

.tool-icon {
  @apply w-4 h-4;
  color: var(--accent-primary);
}

.tool-name {
  @apply font-medium;
  color: var(--text-primary);
}

.execution-time {
  @apply text-xs font-mono;
  color: var(--text-secondary);
  background: var(--bg-quaternary);
  padding: var(--space-1) var(--space-2);
  border-radius: 0.25rem;
}

.status-success {
  @apply text-xs px-2 py-1 rounded;
  background: var(--success);
  color: white;
}

.status-error {
  @apply text-xs px-2 py-1 rounded;
  background: var(--error);
  color: white;
}

.status-pending {
  @apply text-xs px-2 py-1 rounded;
  background: var(--warning);
  color: var(--gray-900);
}

.expand-btn {
  @apply p-1 rounded transition-transform duration-200;
  color: var(--text-secondary);
}

.expand-btn:hover {
  background: var(--bg-quaternary);
}

.tool-details {
  @apply border-t px-3 pb-3;
  border-color: var(--border-secondary);
}

.tool-section {
  @apply mt-3;
}

.section-title {
  @apply text-sm font-medium mb-2;
  color: var(--text-primary);
}
</style>
```

### **Mobile-Responsive Design**

#### **Breakpoint System**
```css
:root {
  /* Responsive Breakpoints */
  --breakpoint-sm: 640px;   /* Small tablets */
  --breakpoint-md: 768px;   /* Large tablets */
  --breakpoint-lg: 1024px;  /* Small desktops */
  --breakpoint-xl: 1280px;  /* Large desktops */
  --breakpoint-2xl: 1536px; /* Extra large desktops */
}

/* Mobile-first responsive utilities */
.mobile\:hidden { display: none; }
.mobile\:block { display: block; }
.mobile\:flex { display: flex; }

@media (min-width: 640px) {
  .sm\:hidden { display: none; }
  .sm\:block { display: block; }
  .sm\:flex { display: flex; }
}

@media (min-width: 768px) {
  .md\:hidden { display: none; }
  .md\:block { display: block; }
  .md\:flex { display: flex; }
}
```

#### **Mobile Layout Adaptations**
```vue
<template>
  <div class="app-layout">
    <!-- Mobile Header -->
    <header class="mobile-header md:hidden">
      <button @click="toggleSidebar" class="sidebar-toggle">
        <IconMenu />
      </button>
      <div class="header-title">Observatory</div>
      <div class="header-actions">
        <button class="action-btn">
          <IconSearch />
        </button>
        <button class="action-btn">
          <IconNotification />
        </button>
      </div>
    </header>
    
    <!-- Desktop Header -->
    <header class="desktop-header hidden md:flex">
      <!-- Full desktop header content -->
    </header>
    
    <!-- Mobile Sidebar Overlay -->
    <div 
      v-if="sidebarOpen" 
      class="sidebar-overlay md:hidden"
      @click="closeSidebar"
    >
      <aside class="mobile-sidebar">
        <!-- Sidebar content -->
      </aside>
    </div>
    
    <!-- Desktop Sidebar -->
    <aside class="desktop-sidebar hidden md:block">
      <!-- Sidebar content -->
    </aside>
    
    <!-- Main Content -->
    <main class="main-content">
      <!-- Responsive content -->
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  @apply min-h-screen;
  display: grid;
  grid-template-areas: 
    "header"
    "main";
  grid-template-rows: auto 1fr;
}

@media (min-width: 768px) {
  .app-layout {
    grid-template-areas: 
      "header header"
      "sidebar main";
    grid-template-columns: 16rem 1fr;
    grid-template-rows: auto 1fr;
  }
}

.mobile-header {
  @apply flex items-center justify-between p-4 border-b;
  grid-area: header;
  background: var(--bg-primary);
  border-color: var(--border-primary);
}

.desktop-header {
  @apply items-center justify-between p-4 border-b;
  grid-area: header;
  background: var(--bg-primary);
  border-color: var(--border-primary);
}

.sidebar-overlay {
  @apply fixed inset-0 z-50;
  background: rgba(0, 0, 0, 0.5);
}

.mobile-sidebar {
  @apply w-80 h-full bg-white shadow-xl;
  background: var(--bg-primary);
  transform: translateX(-100%);
  animation: slideIn 0.3s ease-out forwards;
}

@keyframes slideIn {
  to {
    transform: translateX(0);
  }
}

.desktop-sidebar {
  @apply border-r;
  grid-area: sidebar;
  background: var(--bg-secondary);
  border-color: var(--border-primary);
}

.main-content {
  @apply overflow-auto;
  grid-area: main;
  background: var(--bg-primary);
}
```

## 📱 **Interaction Design**

### **User Flow Patterns**

#### **Primary User Flows**
1. **Quick Conversation View:** Home → See live conversation → Click to expand
2. **Search Flow:** Header search → Results → Select conversation → View details
3. **Project Navigation:** Sidebar projects → Select project → View conversations
4. **Analytics Review:** Analytics tab → Select time range → Review insights

#### **Interaction States**
```css
/* Interactive Element States */
.interactive {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.interactive:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.interactive:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.interactive:focus {
  outline: 2px solid var(--accent-primary);
  outline-offset: 2px;
}

/* Loading States */
.loading {
  position: relative;
  overflow: hidden;
}

.loading::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, 
    transparent, 
    rgba(255, 255, 255, 0.4), 
    transparent
  );
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { left: -100%; }
  100% { left: 100%; }
}
```

### **Animation System**

#### **Micro-Interactions**
```css
/* Button Interactions */
.btn {
  @apply px-4 py-2 rounded-md font-medium transition-all duration-200;
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.12);
}

.btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12);
}

/* Message Animations */
.message-enter-active {
  transition: all 0.3s ease;
}

.message-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.message-enter-to {
  opacity: 1;
  transform: translateY(0);
}

/* Notification Animations */
.notification-enter-active {
  transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.notification-enter-to {
  opacity: 1;
  transform: translateX(0);
}
```

### **Accessibility Features**

#### **WCAG 2.1 AA Compliance**
```css
/* Focus Management */
.focus-visible {
  outline: 2px solid var(--accent-primary);
  outline-offset: 2px;
}

/* High Contrast Support */
@media (prefers-contrast: high) {
  :root {
    --text-primary: #000000;
    --bg-primary: #ffffff;
    --border-primary: #000000;
  }
}

/* Reduced Motion Support */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Screen Reader Only Content */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

## 🎛️ **Component States & Feedback**

### **Status Indicators**

#### **Connection Status**
```vue
<template>
  <div :class="connectionClasses">
    <div class="status-dot" />
    <span class="status-text">{{ statusText }}</span>
  </div>
</template>

<script setup>
const connectionClasses = computed(() => [
  'connection-status',
  `status-${connectionState.value}`
]);

const statusText = computed(() => {
  switch (connectionState.value) {
    case 'connected': return 'Connected';
    case 'connecting': return 'Connecting...';
    case 'disconnected': return 'Disconnected';
    case 'error': return 'Connection Error';
    default: return 'Unknown';
  }
});
</script>

<style scoped>
.connection-status {
  @apply flex items-center gap-2 px-3 py-1 rounded-full text-sm;
}

.status-connected {
  @apply bg-green-100 text-green-800;
}

.status-connected .status-dot {
  @apply w-2 h-2 bg-green-500 rounded-full;
  animation: pulse 2s infinite;
}

.status-connecting {
  @apply bg-yellow-100 text-yellow-800;
}

.status-connecting .status-dot {
  @apply w-2 h-2 bg-yellow-500 rounded-full;
  animation: spin 1s linear infinite;
}

.status-disconnected {
  @apply bg-red-100 text-red-800;
}

.status-disconnected .status-dot {
  @apply w-2 h-2 bg-red-500 rounded-full;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
```

### **Loading States**

#### **Skeleton Loaders**
```vue
<template>
  <div class="conversation-skeleton">
    <div class="skeleton-header">
      <div class="skeleton-badge" />
      <div class="skeleton-timestamp" />
    </div>
    <div class="skeleton-content">
      <div class="skeleton-line long" />
      <div class="skeleton-line medium" />
      <div class="skeleton-line short" />
    </div>
  </div>
</template>

<style scoped>
.conversation-skeleton {
  @apply p-4 border rounded-lg;
  background: var(--bg-secondary);
  border-color: var(--border-primary);
}

.skeleton-header {
  @apply flex items-center justify-between mb-3;
}

.skeleton-badge {
  @apply w-16 h-6 rounded;
  background: var(--bg-tertiary);
  animation: skeleton-pulse 1.5s ease-in-out infinite alternate;
}

.skeleton-timestamp {
  @apply w-20 h-4 rounded;
  background: var(--bg-tertiary);
  animation: skeleton-pulse 1.5s ease-in-out infinite alternate;
}

.skeleton-line {
  @apply h-4 rounded mb-2;
  background: var(--bg-tertiary);
  animation: skeleton-pulse 1.5s ease-in-out infinite alternate;
}

.skeleton-line.long { width: 100%; }
.skeleton-line.medium { width: 75%; }
.skeleton-line.short { width: 50%; }

@keyframes skeleton-pulse {
  0% { opacity: 1; }
  100% { opacity: 0.6; }
}
</style>
```

---

*This UI/UX design specification provides comprehensive guidance for creating a modern, accessible, and user-friendly interface for Claude Code Observatory that serves both individual developers and teams effectively.*