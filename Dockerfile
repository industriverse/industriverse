# Multi-stage Dockerfile for Capsule Pins PWA
# Week 16: Production-Ready DAC Factory

# Stage 1: Build frontend
FROM node:22-alpine AS frontend-builder

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install pnpm
RUN npm install -g pnpm@10.4.1

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY client ./client
COPY shared ./shared
COPY tsconfig.json ./
COPY vite.config.ts ./

# Build frontend
RUN pnpm run build:client

# Stage 2: Build backend
FROM node:22-alpine AS backend-builder

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install pnpm
RUN npm install -g pnpm@10.4.1

# Install dependencies (including devDependencies for TypeScript)
RUN pnpm install --frozen-lockfile

# Copy source code
COPY server ./server
COPY shared ./shared
COPY tsconfig.json ./

# Build backend
RUN pnpm run build:server

# Stage 3: Production image
FROM node:22-alpine AS production

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create app user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install pnpm
RUN npm install -g pnpm@10.4.1

# Install production dependencies only
RUN pnpm install --prod --frozen-lockfile

# Copy built frontend from frontend-builder
COPY --from=frontend-builder --chown=nodejs:nodejs /app/dist ./dist

# Copy built backend from backend-builder
COPY --from=backend-builder --chown=nodejs:nodejs /app/server-dist ./server-dist

# Copy shared types
COPY --chown=nodejs:nodejs shared ./shared

# Create directories for uploads and logs
RUN mkdir -p /app/uploads /app/logs && \
    chown -R nodejs:nodejs /app/uploads /app/logs

# Switch to non-root user
USER nodejs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Start application
CMD ["node", "server-dist/index.js"]
