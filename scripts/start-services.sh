#!/bin/bash

# Start services script
set -e

echo "🚀 Starting Tools API services..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp env.example .env
    echo "📝 Please edit .env file with your configurations"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs uploads temp

# Create MinIO bucket if it doesn't exist
echo "🪣 Setting up MinIO bucket..."
docker-compose up -d minio
sleep 5

# Create bucket
docker-compose exec minio mc alias set local http://localhost:9000 admin admin123456 || true
docker-compose exec minio mc mb local/tools-storage || true
docker-compose exec minio mc policy set public local/tools-storage || true

# Start all services
echo "🔄 Starting all services..."
docker-compose up -d

echo "✅ Services started successfully!"
echo ""
echo "📋 Service URLs:"
echo "   API: http://localhost:8000"
echo "   MinIO Console: http://localhost:9001 (admin/admin123456)"
echo "   MinIO API: http://localhost:9000"
echo "   Redis: localhost:6379"
echo ""
echo "📝 Check service status: docker-compose ps"
echo "📊 View logs: docker-compose logs -f [service-name]"