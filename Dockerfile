# Stage 1: Build Svelte frontend
FROM node:20-alpine AS ui-builder

# Set working directory for build
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package files first to leverage cache
COPY shell/package.json shell/package-lock.json ./shell/

# Install dependencies
WORKDIR /app/shell
RUN pnpm install

# Copy the rest of the frontend source code
COPY shell/ .

# Build the frontend
RUN pnpm build
# Artifacts are now in /app/shell/dist

# Stage 2: Runtime environment
FROM python:3.11-slim AS runtime

# Create a non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend build artifacts from builder stage
COPY --from=ui-builder --chown=appuser:appuser /app/shell/dist ./dist

# Copy backend source code
COPY --chown=appuser:appuser core ./core
COPY --chown=appuser:appuser plugins ./plugins
COPY --chown=appuser:appuser main.py .

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=7860

# Expose port
EXPOSE 7860

# Switch to non-root user
USER appuser

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
