# Stage 1: Build Svelte frontend
FROM node:20-alpine AS builder

# Set working directory for build
WORKDIR /app/shell

# Copy package files first to leverage cache
COPY shell/package.json shell/pnpm-lock.yaml ./

# Install dependencies
RUN npm install -g pnpm && pnpm install --frozen-lockfile

# Copy the rest of the frontend source code
COPY shell/ ./

# Build the frontend
RUN pnpm build
# Artifacts are now in /app/shell/dist

# Stage 2: Runtime environment
FROM python:3.11-slim AS runtime

WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY core/ ./core
COPY plugins/ ./plugins

# Copy main.py to core/main.py to align with CMD
COPY main.py ./core/main.py

# Copy frontend build artifacts from builder stage
COPY --from=builder /app/shell/dist ./dist

# Create persistence directory
RUN mkdir data

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=7860

# Expose port
EXPOSE 7860

# Switch to non-root user
USER appuser

# Run the application
CMD ["uvicorn", "core.main:app", "--host", "0.0.0.0", "--port", "7860"]
