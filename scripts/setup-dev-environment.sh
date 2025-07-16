#!/bin/bash

# Claude Code Observatory - Development Environment Setup Script
# This script sets up the complete development environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check system requirements
check_requirements() {
    log_info "Checking system requirements..."
    
    local requirements_met=true
    
    # Check Python
    if command_exists python3; then
        local python_version=$(python3 --version | cut -d' ' -f2)
        log_success "Python $python_version found"
    else
        log_error "Python 3.11+ is required but not found"
        requirements_met=false
    fi
    
    # Check Node.js
    if command_exists node; then
        local node_version=$(node --version)
        log_success "Node.js $node_version found"
    else
        log_error "Node.js 18+ is required but not found"
        requirements_met=false
    fi
    
    # Check npm
    if command_exists npm; then
        local npm_version=$(npm --version)
        log_success "npm $npm_version found"
    else
        log_error "npm is required but not found"
        requirements_met=false
    fi
    
    # Check Docker
    if command_exists docker; then
        local docker_version=$(docker --version | cut -d' ' -f3 | sed 's/,//')
        log_success "Docker $docker_version found"
    else
        log_warning "Docker not found - Docker setup will be skipped"
    fi
    
    # Check Git
    if command_exists git; then
        local git_version=$(git --version | cut -d' ' -f3)
        log_success "Git $git_version found"
    else
        log_error "Git is required but not found"
        requirements_met=false
    fi
    
    if [ "$requirements_met" = false ]; then
        log_error "Some requirements are not met. Please install the missing dependencies."
        exit 1
    fi
    
    log_success "All requirements met"
}

# Setup Python backend environment
setup_backend() {
    log_info "Setting up Python backend environment..."
    
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
        log_success "Virtual environment created"
    fi
    
    # Activate virtual environment and install dependencies
    log_info "Installing Python dependencies..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements-dev.txt
    
    log_success "Backend environment setup complete"
    cd ..
}

# Setup frontend environment
setup_frontend() {
    log_info "Setting up SvelteKit frontend environment..."
    
    cd frontend
    
    # Install Node.js dependencies
    log_info "Installing Node.js dependencies..."
    npm install
    
    # Run type checking to ensure everything is set up correctly
    log_info "Running initial type check..."
    npm run check
    
    log_success "Frontend environment setup complete"
    cd ..
}

# Setup Supabase
setup_supabase() {
    log_info "Setting up Supabase..."
    
    # Install Supabase CLI if not present
    if ! command_exists supabase; then
        log_info "Installing Supabase CLI..."
        npm install -g @supabase/cli@latest
        log_success "Supabase CLI installed"
    fi
    
    cd supabase
    
    # Initialize Supabase if not already done
    if [ ! -f "config.toml" ]; then
        log_info "Initializing Supabase..."
        supabase init
    fi
    
    # Start Supabase services
    log_info "Starting Supabase services..."
    if supabase start; then
        log_success "Supabase services started"
        log_info "Supabase Studio: http://localhost:54323"
    else
        log_warning "Failed to start Supabase services - you may need to start them manually"
    fi
    
    cd ..
}

# Setup Docker environment
setup_docker() {
    if command_exists docker; then
        log_info "Setting up Docker environment..."
        
        # Build Docker images
        log_info "Building Docker images..."
        make docker-build
        
        log_success "Docker environment setup complete"
    else
        log_warning "Docker not found - skipping Docker setup"
    fi
}

# Setup Git hooks
setup_git_hooks() {
    log_info "Setting up Git hooks..."
    
    # Create pre-commit hook
    mkdir -p .git/hooks
    
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

# Run linters before commit
echo "Running pre-commit checks..."

# Backend linting
cd backend
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Checking Python code..."
    black --check . || exit 1
    flake8 . || exit 1
    mypy . || exit 1
fi
cd ..

# Frontend linting
cd frontend
if [ -d "node_modules" ]; then
    echo "Checking TypeScript/Svelte code..."
    npm run lint || exit 1
    npm run check || exit 1
fi
cd ..

echo "Pre-commit checks passed!"
EOF
    
    chmod +x .git/hooks/pre-commit
    log_success "Git hooks setup complete"
}

# Create environment files
setup_environment_files() {
    log_info "Setting up environment files..."
    
    # Backend environment
    if [ ! -f "backend/.env" ]; then
        cp backend/env.template backend/.env
        log_info "Created backend/.env from template"
        log_warning "Please update backend/.env with your actual configuration"
    fi
    
    # Frontend environment
    if [ ! -f "frontend/.env" ]; then
        cat > frontend/.env << 'EOF'
# SvelteKit Frontend Environment Variables
PUBLIC_API_URL=http://localhost:8000
PUBLIC_WS_URL=ws://localhost:8000
PUBLIC_SUPABASE_URL=http://localhost:54321
PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
EOF
        log_info "Created frontend/.env"
        log_warning "Please update frontend/.env with your actual configuration"
    fi
    
    log_success "Environment files setup complete"
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    # Test backend
    log_info "Testing backend setup..."
    cd backend
    source venv/bin/activate
    python -c "import app; print('Backend import successful')"
    cd ..
    
    # Test frontend
    log_info "Testing frontend setup..."
    cd frontend
    npm run check
    cd ..
    
    log_success "Installation verification complete"
}

# Print helpful information
print_next_steps() {
    echo ""
    log_success "🎉 Development environment setup complete!"
    echo ""
    log_info "Next steps:"
    echo "  1. Update configuration files:"
    echo "     - backend/.env (database URLs, API keys)"
    echo "     - frontend/.env (API endpoints)"
    echo ""
    log_info "Start development:"
    echo "  • Full stack: make dev"
    echo "  • Backend only: make dev-backend"
    echo "  • Frontend only: make dev-frontend"
    echo "  • With Docker: make docker-dev"
    echo ""
    log_info "Run tests:"
    echo "  • All tests: make test"
    echo "  • Backend tests: make test-backend"
    echo "  • Frontend tests: make test-frontend"
    echo "  • E2E tests: make test-e2e"
    echo ""
    log_info "Useful commands:"
    echo "  • Code formatting: make format"
    echo "  • Linting: make lint"
    echo "  • Type checking: make typecheck"
    echo "  • Database reset: make db-reset"
    echo ""
    log_info "For more commands, run: make help"
}

# Main execution
main() {
    echo ""
    log_info "🚀 Claude Code Observatory - Development Environment Setup"
    echo ""
    
    check_requirements
    setup_backend
    setup_frontend
    setup_supabase
    setup_docker
    setup_git_hooks
    setup_environment_files
    verify_installation
    print_next_steps
}

# Run main function
main "$@"