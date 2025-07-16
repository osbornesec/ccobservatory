# Multi-stage Docker build for SvelteKit frontend
FROM node:20-alpine AS builder

# Set work directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage with Nginx
FROM nginx:alpine AS runtime

# Install curl for health checks
RUN apk add --no-cache curl

# Copy built application from builder stage
COPY --from=builder /app/.svelte-kit/output/client /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create nginx user and set permissions
RUN addgroup -g 1001 -S cco && \
    adduser -S cco -u 1001 -G cco && \
    chown -R cco:cco /usr/share/nginx/html && \
    chown -R cco:cco /var/cache/nginx && \
    chown -R cco:cco /var/log/nginx && \
    chown -R cco:cco /etc/nginx/conf.d

# Switch to non-root user
USER cco

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]