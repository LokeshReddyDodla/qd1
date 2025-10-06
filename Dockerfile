FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy the qd2 directory contents to /app
COPY qd2/ /app/

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose port (Railway will set this dynamically via $PORT)
EXPOSE 8080

# Run the application (Railway provides $PORT environment variable)
# Using shell form to properly expand environment variables
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"
