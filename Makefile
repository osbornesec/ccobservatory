# Claude Code Observatory - Development Commands
# Unified command interface for Python FastAPI backend + SvelteKit frontend + Supabase

.PHONY: help install dev test lint format clean build docker-build docker-dev deploy

# Default target - show help
help:
	@echo "Claude Code Observatory - Development Commands"
	@echo ""
	@echo "Setup Commands:"
	@echo "  install          Install all dependencies (backend + frontend + tools)"
	@echo "  install-backend  Install Python backend dependencies"
	@echo "  install-frontend Install Node.js frontend dependencies"
	@echo "  install-tools    Install development tools (Supabase CLI, etc.)"
	@echo ""
	@echo "Development Commands:"
	@echo "  dev              Start all services in development mode"
	@echo "  dev-backend      Start Python FastAPI server only"
	@echo "  dev-frontend     Start SvelteKit dev server only"
	@echo "  dev-supabase     Start local Supabase instance"
	@echo "  dev-all          Start all services with hot reloading"
	@echo ""
	@echo "Testing Commands:"
	@echo "  test             Run all tests (backend + frontend + integration)"
	@echo "  test-backend     Run Python backend tests (pytest)"
	@echo "  test-frontend    Run SvelteKit frontend tests (Vitest)"
	@echo "  test-e2e         Run end-to-end tests (Playwright)"
	@echo "  test-integration Run integration tests"
	@echo "  test-watch       Run tests in watch mode"
	@echo "  test-coverage    Generate comprehensive coverage reports"
	@echo ""
	@echo "Code Quality Commands:"
	@echo "  lint             Run all linters (Python + TypeScript)"
	@echo "  lint-backend     Run Python linters (Black, Flake8, MyPy)"
	@echo "  lint-frontend    Run TypeScript/Svelte linters (ESLint)"
	@echo "  format           Auto-format all code"
	@echo "  format-backend   Auto-format Python code"
	@echo "  format-frontend  Auto-format TypeScript/Svelte code"
	@echo "  typecheck        Run type checking for all components"
	@echo ""
	@echo "Build Commands:"
	@echo "  build            Build all components for production"
	@echo "  build-backend    Build Python backend"
	@echo "  build-frontend   Build SvelteKit frontend"
	@echo "  build-docker     Build Docker images"
	@echo ""
	@echo "Database Commands:"
	@echo "  db-reset         Reset local Supabase database"
	@echo "  db-migrate       Run database migrations"
	@echo "  db-seed          Seed database with test data"
	@echo "  db-generate-types Generate TypeScript types from database"
	@echo ""
	@echo "Docker Commands:"
	@echo "  docker-build     Build all Docker images"
	@echo "  docker-dev       Start development environment with Docker Compose"
	@echo "  docker-test      Run tests in Docker containers"
	@echo "  docker-clean     Clean up Docker resources"
	@echo ""
	@echo "Utility Commands:"
	@echo "  clean            Clean all build artifacts and caches"
	@echo "  security-audit   Run security audits on dependencies"
	@echo "  deps-update      Update all dependencies"
	@echo "  health-check     Check system health and dependencies"

# Setup Commands
install: install-backend install-frontend install-tools
	@echo "✅ All dependencies installed successfully"

install-backend:
	@echo "📦 Installing Python backend dependencies..."
	cd backend && python -m venv venv
	cd backend && source venv/bin/activate && pip install --upgrade pip
	cd backend && source venv/bin/activate && pip install -r requirements-dev.txt
	@echo "✅ Backend dependencies installed"

install-frontend:
	@echo "📦 Installing Node.js frontend dependencies..."
	cd frontend && npm install
	@echo "✅ Frontend dependencies installed"

install-tools:
	@echo "🔧 Installing development tools..."
	@if ! command -v supabase >/dev/null 2>&1; then \
		echo "Installing Supabase CLI..."; \
		npm install -g @supabase/cli@latest; \
	fi
	@if ! command -v docker >/dev/null 2>&1; then \
		echo "⚠️  Docker not found. Please install Docker manually."; \
	fi
	@echo "✅ Development tools ready"

# Development Commands
dev: dev-supabase
	@echo "🚀 Starting all development services..."
	@make -j3 dev-backend dev-frontend dev-monitor

dev-backend:
	@echo "🐍 Starting FastAPI backend server..."
	cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "⚡ Starting SvelteKit frontend server..."
	cd frontend && npm run dev

dev-supabase:
	@echo "🗄️  Starting local Supabase instance..."
	@if [ ! -f supabase/.gitignore ]; then \
		cd supabase && supabase init; \
	fi
	cd supabase && supabase start

dev-monitor:
	@echo "📊 Development environment running:"
	@echo "  • Backend API: http://localhost:8000"
	@echo "  • Frontend: http://localhost:5173"
	@echo "  • Supabase Studio: http://localhost:54323"
	@echo "  • API Docs: http://localhost:8000/docs"

dev-all: dev

# Testing Commands
test: test-backend test-frontend test-integration
	@echo "✅ All tests completed successfully"

test-backend:
	@echo "🧪 Running Python backend tests..."
	cd backend && source venv/bin/activate && pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=85

test-frontend:
	@echo "🧪 Running SvelteKit frontend tests..."
	cd frontend && npm run test

test-e2e:
	@echo "🎭 Running end-to-end tests..."
	cd frontend && npm run test:e2e

test-integration:
	@echo "🔗 Running integration tests..."
	cd backend && source venv/bin/activate && pytest tests/test_*integration* -v

test-watch:
	@echo "👀 Running tests in watch mode..."
	@make -j2 test-backend-watch test-frontend-watch

test-backend-watch:
	cd backend && source venv/bin/activate && pytest-watch -- tests/ -v

test-frontend-watch:
	cd frontend && npm run test:watch

test-coverage:
	@echo "📊 Generating comprehensive coverage reports..."
	cd backend && source venv/bin/activate && pytest tests/ --cov=app --cov-report=html --cov-report=xml --cov-fail-under=85
	cd frontend && npm run test:coverage
	@echo "📊 Coverage reports generated:"
	@echo "  • Backend: backend/htmlcov/index.html"
	@echo "  • Frontend: frontend/coverage/index.html"

# Code Quality Commands
lint: lint-backend lint-frontend
	@echo "✅ All linting completed"

lint-backend:
	@echo "🔍 Linting Python backend..."
	cd backend && source venv/bin/activate && black --check .
	cd backend && source venv/bin/activate && flake8 .
	cd backend && source venv/bin/activate && mypy .

lint-frontend:
	@echo "🔍 Linting TypeScript frontend..."
	cd frontend && npm run lint
	cd frontend && npm run check

format: format-backend format-frontend
	@echo "✨ All code formatted"

format-backend:
	@echo "✨ Formatting Python backend..."
	cd backend && source venv/bin/activate && black .
	cd backend && source venv/bin/activate && isort .

format-frontend:
	@echo "✨ Formatting TypeScript frontend..."
	cd frontend && npm run format

typecheck:
	@echo "🔎 Running type checking..."
	cd backend && source venv/bin/activate && mypy .
	cd frontend && npm run check

# Build Commands
build: build-backend build-frontend
	@echo "✅ All components built successfully"

build-backend:
	@echo "🏗️  Building Python backend..."
	cd backend && source venv/bin/activate && python -m build

build-frontend:
	@echo "🏗️  Building SvelteKit frontend..."
	cd frontend && npm run build

build-docker:
	@echo "🐳 Building Docker images..."
	docker build -t cco-backend ./backend
	docker build -t cco-frontend ./frontend

# Database Commands
db-reset:
	@echo "🗄️  Resetting local Supabase database..."
	cd supabase && supabase db reset

db-migrate:
	@echo "🗄️  Running database migrations..."
	cd supabase && supabase db push

db-seed:
	@echo "🌱 Seeding database with test data..."
	cd supabase && supabase db seed

db-generate-types:
	@echo "📝 Generating TypeScript types from database..."
	cd supabase && supabase gen types typescript --local > ../frontend/src/lib/database.types.ts
	@echo "✅ Database types generated: frontend/src/lib/database.types.ts"

# Docker Commands
docker-build:
	@echo "🐳 Building Docker images..."
	docker-compose build

docker-dev:
	@echo "🐳 Starting development environment with Docker Compose..."
	docker-compose up -d
	@echo "🐳 Services started:"
	@echo "  • Backend: http://localhost:8000"
	@echo "  • Frontend: http://localhost:5173"
	@echo "  • Database: localhost:5432"

docker-test:
	@echo "🐳 Running tests in Docker containers..."
	docker-compose -f docker-compose.test.yml up --abort-on-container-exit

docker-clean:
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose down -v
	docker system prune -f

# Utility Commands
clean:
	@echo "🧹 Cleaning build artifacts and caches..."
	rm -rf backend/.pytest_cache backend/.coverage backend/htmlcov backend/dist backend/build
	rm -rf frontend/.svelte-kit frontend/build frontend/node_modules/.cache
	rm -rf frontend/coverage frontend/.nyc_output
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✅ Cleanup completed"

security-audit:
	@echo "🔒 Running security audits..."
	cd backend && source venv/bin/activate && safety check
	cd frontend && npm audit
	@echo "✅ Security audit completed"

deps-update:
	@echo "⬆️  Updating dependencies..."
	cd backend && source venv/bin/activate && pip-review --auto
	cd frontend && npm update
	@echo "✅ Dependencies updated"

health-check:
	@echo "🏥 Checking system health..."
	@echo "Python version: $$(python --version)"
	@echo "Node.js version: $$(node --version)"
	@echo "Docker version: $$(docker --version 2>/dev/null || echo 'Not installed')"
	@echo "Supabase CLI: $$(supabase --version 2>/dev/null || echo 'Not installed')"
	@echo ""
	@echo "Backend dependencies:"
	@cd backend && source venv/bin/activate && pip check
	@echo ""
	@echo "Frontend dependencies:"
	@cd frontend && npm ls --depth=0 2>/dev/null || true
	@echo "✅ Health check completed"

# TDD Workflow Commands
tdd:
	@echo "🔄 Starting TDD workflow..."
	@echo "Running continuous testing with coverage..."
	@make -j2 test-backend-watch test-frontend-watch

ci-local:
	@echo "🤖 Running local CI simulation..."
	@make lint test build
	@echo "✅ Local CI pipeline completed successfully"

# Performance Commands
perf-test:
	@echo "⚡ Running performance tests..."
	cd backend && source venv/bin/activate && pytest tests/test_performance_benchmarks.py -v

benchmark:
	@echo "📊 Running benchmarks..."
	@make perf-test
	@echo "📊 Benchmark results saved to backend/benchmark_results.json"