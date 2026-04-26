# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install curl for ECS health checks
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app.py .

# Environment variables (overridden at runtime)
ENV DB_HOST=localhost
ENV DB_USER=admin
ENV DB_PASSWORD=password
ENV DB_NAME=threetierdb
ENV APP_VERSION=1.0.0

# Expose port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]