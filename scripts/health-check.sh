#!/bin/bash

# Health check script
set -e

echo "🔍 Checking service health..."

# Check if services are running
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Services are not running. Start with: ./scripts/start-services.sh"
    exit 1
fi

# Check API health
echo "📡 Checking API health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API is healthy"
else
    echo "❌ API health check failed"
fi

# Check Redis
echo "🔄 Checking Redis..."
if docker-compose exec redis redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis is healthy"
else
    echo "❌ Redis health check failed"
fi

# Check MinIO
echo "🪣 Checking MinIO..."
if curl -f http://localhost:9000/minio/health/live > /dev/null 2>&1; then
    echo "✅ MinIO is healthy"
else
    echo "❌ MinIO health check failed"
fi

# Check Celery workers
echo "⚙️  Checking Celery workers..."
if docker-compose exec celery-worker celery -A app.core.worker inspect ping > /dev/null 2>&1; then
    echo "✅ Celery workers are healthy"
else
    echo "❌ Celery workers health check failed"
fi

echo ""
echo "📊 Service Status:"
docker-compose ps