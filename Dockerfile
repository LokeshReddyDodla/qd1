FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy the qd2 directory contents to /app
COPY qd2/ /app/

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose port (Railway will set this dynamically via $PORT)
EXPOSE $PORT

# Health check (using PORT environment variable)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os, requests; requests.get(f'http://localhost:{os.getenv(\"PORT\", \"8080\")}/health', timeout=5)" || exit 1

# Run the application (Railway provides $PORT environment variable)
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
