#!/bin/bash

# Claude Code Observatory - Deployment Script
# Handles deployment to different environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCKER_REGISTRY=${DOCKER_REGISTRY:-"your-registry.com"}
IMAGE_TAG=${IMAGE_TAG:-"latest"}
ENVIRONMENT=${ENVIRONMENT:-"staging"}

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

# Show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] <environment>"
    echo ""
    echo "Arguments:"
    echo "  environment    Target environment (staging, production)"
    echo ""
    echo "Options:"
    echo "  -t, --tag TAG     Docker image tag (default: latest)"
    echo "  -r, --registry    Docker registry URL"
    echo "  -h, --help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 staging"
    echo "  $0 --tag v1.2.3 production"
    echo "  $0 --registry my-registry.com staging"
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--tag)
                IMAGE_TAG="$2"
                shift 2
                ;;
            -r|--registry)
                DOCKER_REGISTRY="$2"
                shift 2
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            -*)
                log_error "Unknown option $1"
                show_usage
                exit 1
                ;;
            *)
                ENVIRONMENT="$1"
                shift
                ;;
        esac
    done
}

# Validate environment
validate_environment() {
    case $ENVIRONMENT in
        staging|production)
            log_info "Deploying to $ENVIRONMENT environment"
            ;;
        *)
            log_error "Invalid environment: $ENVIRONMENT"
            log_info "Valid environments: staging, production"
            exit 1
            ;;
    esac
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is required but not installed"
        exit 1
    fi
    
    # Check if logged into Docker registry
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Run tests before deployment
run_tests() {
    log_info "Running tests before deployment..."
    
    # Run full test suite
    if make test; then
        log_success "All tests passed"
    else
        log_error "Tests failed - deployment aborted"
        exit 1
    fi
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    
    # Build backend image
    log_info "Building backend image..."
    docker build \
        -t "${DOCKER_REGISTRY}/cco-backend:${IMAGE_TAG}" \
        -t "${DOCKER_REGISTRY}/cco-backend:latest" \
        ./backend
    
    # Build frontend image
    log_info "Building frontend image..."
    docker build \
        -t "${DOCKER_REGISTRY}/cco-frontend:${IMAGE_TAG}" \
        -t "${DOCKER_REGISTRY}/cco-frontend:latest" \
        ./frontend
    
    log_success "Docker images built successfully"
}

# Push images to registry
push_images() {
    log_info "Pushing images to registry..."
    
    # Push backend image
    docker push "${DOCKER_REGISTRY}/cco-backend:${IMAGE_TAG}"
    docker push "${DOCKER_REGISTRY}/cco-backend:latest"
    
    # Push frontend image
    docker push "${DOCKER_REGISTRY}/cco-frontend:${IMAGE_TAG}"
    docker push "${DOCKER_REGISTRY}/cco-frontend:latest"
    
    log_success "Images pushed to registry"
}

# Deploy to Kubernetes (example)
deploy_to_kubernetes() {
    log_info "Deploying to Kubernetes..."
    
    # Update image tags in Kubernetes manifests
    if [ -f "k8s/${ENVIRONMENT}/deployment.yaml" ]; then
        # Replace image tags in deployment files
        sed -i.bak "s|image: .*/cco-backend:.*|image: ${DOCKER_REGISTRY}/cco-backend:${IMAGE_TAG}|g" \
            "k8s/${ENVIRONMENT}/deployment.yaml"
        sed -i.bak "s|image: .*/cco-frontend:.*|image: ${DOCKER_REGISTRY}/cco-frontend:${IMAGE_TAG}|g" \
            "k8s/${ENVIRONMENT}/deployment.yaml"
        
        # Apply Kubernetes manifests
        kubectl apply -f "k8s/${ENVIRONMENT}/"
        
        # Wait for rollout to complete
        kubectl rollout status deployment/cco-backend -n "cco-${ENVIRONMENT}"
        kubectl rollout status deployment/cco-frontend -n "cco-${ENVIRONMENT}"
        
        log_success "Kubernetes deployment completed"
    else
        log_warning "Kubernetes manifests not found for $ENVIRONMENT"
    fi
}

# Deploy with Docker Compose (alternative)
deploy_with_compose() {
    log_info "Deploying with Docker Compose..."
    
    # Create environment-specific compose file
    export DOCKER_REGISTRY
    export IMAGE_TAG
    export ENVIRONMENT
    
    # Start services
    docker-compose -f docker-compose.${ENVIRONMENT}.yml up -d
    
    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 30
    
    # Health check
    if curl -f "http://localhost:8000/health" > /dev/null 2>&1; then
        log_success "Backend health check passed"
    else
        log_error "Backend health check failed"
        exit 1
    fi
    
    if curl -f "http://localhost:8080/health" > /dev/null 2>&1; then
        log_success "Frontend health check passed"
    else
        log_error "Frontend health check failed"
        exit 1
    fi
    
    log_success "Docker Compose deployment completed"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    # Run Supabase migrations
    cd supabase
    if [ "$ENVIRONMENT" = "production" ]; then
        # Use production database URL
        supabase db push --db-url "$PRODUCTION_DATABASE_URL"
    else
        # Use staging database URL
        supabase db push --db-url "$STAGING_DATABASE_URL"
    fi
    cd ..
    
    log_success "Database migrations completed"
}

# Post-deployment verification
verify_deployment() {
    log_info "Verifying deployment..."
    
    local api_url backend_url frontend_url
    
    case $ENVIRONMENT in
        staging)
            backend_url="https://api.staging.cco.example.com"
            frontend_url="https://staging.cco.example.com"
            ;;
        production)
            backend_url="https://api.cco.example.com"
            frontend_url="https://cco.example.com"
            ;;
    esac
    
    # Test backend health
    if curl -f "${backend_url}/health" > /dev/null 2>&1; then
        log_success "Backend is responding at ${backend_url}"
    else
        log_error "Backend health check failed at ${backend_url}"
        exit 1
    fi
    
    # Test frontend
    if curl -f "${frontend_url}" > /dev/null 2>&1; then
        log_success "Frontend is accessible at ${frontend_url}"
    else
        log_error "Frontend is not accessible at ${frontend_url}"
        exit 1
    fi
    
    log_success "Deployment verification completed"
}

# Send deployment notification
send_notification() {
    log_info "Sending deployment notification..."
    
    local message="🚀 Claude Code Observatory deployed to ${ENVIRONMENT} (${IMAGE_TAG})"
    
    # Slack notification (if webhook URL is set)
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"$message\"}" \
            "$SLACK_WEBHOOK_URL"
    fi
    
    # Discord notification (if webhook URL is set)
    if [ -n "$DISCORD_WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"content\":\"$message\"}" \
            "$DISCORD_WEBHOOK_URL"
    fi
    
    log_success "Deployment notification sent"
}

# Rollback deployment
rollback_deployment() {
    log_error "Deployment failed - initiating rollback..."
    
    # Rollback Kubernetes deployment
    if command -v kubectl &> /dev/null; then
        kubectl rollout undo deployment/cco-backend -n "cco-${ENVIRONMENT}"
        kubectl rollout undo deployment/cco-frontend -n "cco-${ENVIRONMENT}"
    fi
    
    # Rollback Docker Compose deployment
    if [ -f "docker-compose.${ENVIRONMENT}.yml" ]; then
        docker-compose -f "docker-compose.${ENVIRONMENT}.yml" down
        # Start previous version (this would need additional logic to track previous versions)
    fi
    
    log_info "Rollback completed"
}

# Main deployment function
main() {
    echo ""
    log_info "🚀 Claude Code Observatory - Deployment Script"
    echo ""
    
    parse_args "$@"
    validate_environment
    check_prerequisites
    
    # Set up error handling for rollback
    trap rollback_deployment ERR
    
    run_tests
    build_images
    push_images
    run_migrations
    
    # Choose deployment method based on environment
    if [ -f "k8s/${ENVIRONMENT}/deployment.yaml" ]; then
        deploy_to_kubernetes
    else
        deploy_with_compose
    fi
    
    verify_deployment
    send_notification
    
    log_success "🎉 Deployment to ${ENVIRONMENT} completed successfully!"
    echo ""
    log_info "Deployment details:"
    echo "  • Environment: ${ENVIRONMENT}"
    echo "  • Image tag: ${IMAGE_TAG}"
    echo "  • Registry: ${DOCKER_REGISTRY}"
    echo ""
}

# Run main function
main "$@"