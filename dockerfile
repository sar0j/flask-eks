# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install curl for health checks
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip==26.0 wheel==0.46.2 jaraco.context==6.1.0 && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --upgrade wheel==0.46.2 jaraco.context==6.1.0 && \
    find /usr/local/lib -path "*/setuptools/_vendor/jaraco*" -delete && \
    find /usr/local/lib -path "*/setuptools/_vendor/wheel*" -delete

# Copy app code
COPY app.py .

# Environment variables
ENV DB_HOST=localhost
ENV DB_USER=admin
ENV DB_NAME=threetierdb
ENV APP_VERSION=1.0.0

# Expose port
EXPOSE 5000

# Run app
CMD ["python", "app.py"]