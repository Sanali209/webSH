# Dockerfile for PC Center on Koyeb
# Multi-stage build for frontend and backend

# --- Stage 1: Frontend Build ---
FROM node:18-alpine AS frontend-builder
WORKDIR /app/web

# Copy package files and install dependencies
COPY web/package.json web/package-lock.json* ./
RUN npm ci

# Copy frontend source
COPY web/ ./
# Build the Svelte app (assumes output to /app/web/dist or similar)
RUN npm run build

# --- Stage 2: Backend Runtime ---
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies for LanceDB, Polars, and ZeroMQ
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libzmq3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Copy built frontend assets from Stage 1 to backend static folder
# Adjust destination path based on where FastAPI serves static files (e.g., /app/static)
COPY --from=frontend-builder /app/web/dist /app/static

# Expose port (Koyeb usually expects 8000 or defined via PORT env var)
ENV PORT=8000
EXPOSE 8000

# Run the application (using uvicorn)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
