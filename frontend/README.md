# Claude Code Observatory - Frontend

The frontend dashboard for Claude Code Observatory, built with SvelteKit and TypeScript.

## Tech Stack

- **Framework**: SvelteKit 2.x with Svelte 5
- **Language**: TypeScript
- **Styling**: Tailwind CSS 3.x + DaisyUI
- **Icons**: Lucide Svelte
- **Charts**: Chart.js
- **API Client**: Custom TypeScript client
- **WebSocket**: Native WebSocket with reconnection logic
- **Build Tool**: Vite

## Development

### Prerequisites

- Node.js 18+ and npm
- Backend API running on http://localhost:8000

### Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:5173
```

### Available Scripts

```bash
npm run dev          # Start development server with hot reload
npm run build        # Build for production
npm run preview      # Preview production build
npm run check        # TypeScript type checking
npm run check:watch  # Watch mode for type checking
```

## Project Structure

```
src/
├── app.css                   # Global styles and Tailwind directives
├── app.html                  # HTML template
├── lib/
│   ├── api/                  # API client and WebSocket
│   │   ├── client.ts         # REST API client
│   │   └── websocket.ts      # WebSocket client with reconnection
│   ├── components/           # Reusable Svelte components
│   │   ├── Header.svelte     # Navigation header
│   │   ├── Sidebar.svelte    # Sidebar navigation
│   │   ├── LoadingSpinner.svelte
│   │   └── ErrorMessage.svelte
│   ├── stores/               # Svelte stores for state management
│   │   ├── theme.ts          # Theme (light/dark) state
│   │   └── conversations.ts  # Application data stores
│   ├── types.ts              # TypeScript type definitions
│   └── config.ts             # Configuration and environment variables
└── routes/
    ├── +layout.svelte        # Root layout with CSS imports
    └── +page.svelte          # Dashboard page
```

## Features

### Implemented

- ✅ SvelteKit setup with TypeScript
- ✅ Tailwind CSS + DaisyUI integration
- ✅ Responsive dashboard layout
- ✅ Dark/light theme support
- ✅ API client with error handling and logging
- ✅ WebSocket client with automatic reconnection
- ✅ Svelte stores for state management
- ✅ TypeScript type definitions
- ✅ Development and production builds

EOF < /dev/null