# Environment Configuration Template

This file should be copied to `.env.example` in the project root. The sensitive file guardian hook prevents direct creation, so please manually create the file with this content:

```bash
# Claude Code Observatory - Environment Configuration Template
# Copy this file to .env and fill in your actual values
# Required for both development and production environments

# =============================================================================
# SUPABASE CONFIGURATION (REQUIRED)
# =============================================================================
# Get these values from your Supabase project dashboard at https://app.supabase.com/

# Supabase URL - Your project's unique URL
SUPABASE_URL=https://your-project-id.supabase.co

# Supabase Anon Key - Public API key for client-side operations
SUPABASE_KEY=your-anon-public-key-here

# Supabase Service Role Key - Secret key for server-side operations
# WARNING: Keep this secret! Only use server-side, never expose to clients
# CRITICAL: This key is required for backend tests to pass (16 tests currently failing without it)
SUPABASE_SERVICE_ROLE_KEY=your-service-role-secret-key-here

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
# Direct PostgreSQL connection (automatically available in Supabase projects)
DATABASE_URL=postgresql://postgres:[password]@db.[project-id].supabase.co:5432/postgres

# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================
# Environment: development, staging, production
ENVIRONMENT=development

# Application metadata
APP_NAME=Claude Code Observatory
APP_VERSION=1.0.0
DEBUG=true

# Security
SECRET_KEY=your-secret-key-for-jwt-signing-generate-strong-random-key

# =============================================================================
# FILE MONITORING CONFIGURATION
# =============================================================================
# Path to Claude Code projects directory (where JSONL files are located)
CLAUDE_PROJECTS_PATH=~/.claude/projects

# File monitoring settings
MONITORING_INTERVAL=1.0
MAX_FILE_SIZE_MB=10
MAX_CONCURRENT_FILES=1000
FILE_DETECTION_TIMEOUT_MS=100

# =============================================================================
# API & WEBSOCKET CONFIGURATION
# =============================================================================
# Backend API server settings
API_HOST=localhost
API_PORT=8000
API_RELOAD=true

# WebSocket server settings
WEBSOCKET_HOST=localhost
WEBSOCKET_PORT=8001

# =============================================================================
# FRONTEND CONFIGURATION (SvelteKit)
# =============================================================================
# Frontend development server (SvelteKit)
FRONTEND_PORT=5173
FRONTEND_HOST=localhost

# Frontend environment variables (must be prefixed with PUBLIC_)
# These are available in the browser and should be added to frontend/.env.local
PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
PUBLIC_SUPABASE_ANON_KEY=your-anon-public-key-here
PUBLIC_API_BASE_URL=http://localhost:8000
PUBLIC_WS_URL=ws://localhost:8000/ws
PUBLIC_DEV_MODE=true
PUBLIC_ENABLE_DEBUG_LOGS=true
PUBLIC_ENABLE_ANALYTICS=true
PUBLIC_ENABLE_REAL_TIME=true
PUBLIC_ENABLE_SEARCH=true
PUBLIC_REQUEST_TIMEOUT=10000
PUBLIC_RECONNECT_INTERVAL=5000
PUBLIC_MAX_RECONNECT_ATTEMPTS=10

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
LOG_LEVEL=INFO
LOG_FORMAT=json

# =============================================================================
# DEVELOPMENT TOOLS
# =============================================================================
# Python virtual environment path (optional, defaults to ./backend/venv)
PYTHON_VENV_PATH=./backend/venv

# Node.js package manager preference
PACKAGE_MANAGER=npm

# =============================================================================
# TESTING CONFIGURATION
# =============================================================================
# Test database settings (for pytest)
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:54322/postgres
TEST_SUPABASE_URL=http://localhost:54321
TEST_SUPABASE_KEY=test-anon-key

# =============================================================================
# QUICK SETUP INSTRUCTIONS
# =============================================================================
# 1. Copy this file: cp .env.example .env
# 2. Create Supabase project at https://app.supabase.com/
# 3. Copy your project URL and keys from the Supabase dashboard
# 4. Generate a strong SECRET_KEY: python -c "import secrets; print(secrets.token_urlsafe(32))"
# 5. Run: make install && make dev
# 6. Verify setup: make test (should pass all 97 tests)
#
# For detailed setup instructions, see:
# - docs/Week-1-Completion-Report.md
# - backend/SUPABASE_SETUP.md
# - README.md

# =============================================================================
# SECURITY NOTES
# =============================================================================
# - Never commit .env files to version control
# - SUPABASE_SERVICE_ROLE_KEY has admin privileges - keep secure
# - Use different keys for development, staging, and production
# - Rotate keys regularly in production environments
# - Consider using environment-specific .env files (.env.development, .env.production)

# =============================================================================
# TROUBLESHOOTING
# =============================================================================
# If tests are failing:
# 1. Verify SUPABASE_SERVICE_ROLE_KEY is set correctly
# 2. Check Supabase project is active and accessible
# 3. Ensure database migrations have been applied
# 4. Run: make db-reset && make db-migrate && make test
#
# If file monitoring isn't working:
# 1. Verify CLAUDE_PROJECTS_PATH exists and is readable
# 2. Check file permissions on the monitoring directory
# 3. Ensure no other processes are locking the files
#
# For additional help, see docs/Week-1-Completion-Report.md
```

## Manual Setup Required

1. Copy the above content to `.env.example` in the project root
2. Copy `.env.example` to `.env` and fill in your actual Supabase values
3. The sensitive file guardian hook protects these files for security reasons