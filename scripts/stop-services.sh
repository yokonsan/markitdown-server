#!/bin/bash

# Stop services script
set -e

echo "🛑 Stopping Tools API services..."

# Stop all services
docker-compose down

echo "✅ Services stopped successfully!"

echo "🧹 Optional cleanup commands:"
echo "   Remove volumes: docker-compose down -v"
echo "   Remove images: docker-compose down --rmi all"
echo "   Remove orphans: docker-compose down --remove-orphans"