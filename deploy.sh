#!/bin/bash

# Business Card Scanner Deployment Script
set -e

echo "🚀 Deploying Business Card Scanner..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker compose is available
if ! docker compose version &> /dev/null; then
    echo "❌ docker compose not found. Please install Docker Compose."
    exit 1
fi

# Create logs directory
mkdir -p logs

# Stop existing container if running
echo "🛑 Stopping existing containers..."
docker compose down --remove-orphans 2>/dev/null || true

# Build and start the service
echo "🔨 Building Docker image..."
docker compose build --no-cache

echo "🚀 Starting Business Card Scanner service..."
docker compose up -d

# Wait for service to be healthy
echo "⏳ Waiting for service to be ready..."
timeout=60
counter=0
while [ $counter -lt $timeout ]; do
    if docker compose ps | grep -q "healthy"; then
        echo "✅ Business Card Scanner is running and healthy!"
        echo "🌐 Access the application at: http://localhost:7860"
        break
    fi
    sleep 2
    counter=$((counter + 2))
    echo "Waiting... ($counter/$timeout seconds)"
done

if [ $counter -ge $timeout ]; then
    echo "❌ Service failed to become healthy within $timeout seconds"
    echo "📋 Checking logs..."
    docker compose logs business-card-scanner
    exit 1
fi

echo "📊 Service status:"
docker compose ps

echo ""
echo "✅ Deployment completed successfully!"
echo "🌐 Application URL: http://localhost:7860"
echo "📋 View logs: docker compose logs -f business-card-scanner"
echo "🛑 Stop service: docker compose down" 