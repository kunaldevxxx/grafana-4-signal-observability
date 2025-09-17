#!/bin/bash

# Grafana 4-Signal Observability Stack Startup Script

set -e

echo "🚀 Starting Grafana 4-Signal Observability Stack..."
echo ""

# Check if docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker compose is available
if ! command -v docker &> /dev/null || ! docker compose version >/dev/null 2>&1; then
    echo "❌ Docker Compose is not available. Please install Docker with Compose."
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Start the stack
echo "📦 Starting observability stack..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

services=(
    "grafana:3000"
    "sample-app:8080" 
    "prometheus:9090"
    "pyroscope:4040"
)

for service in "${services[@]}"; do
    name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    
    if curl -s -f http://localhost:$port >/dev/null 2>&1; then
        echo "✅ $name is running on port $port"
    else
        echo "⚠️  $name might still be starting on port $port"
    fi
done

echo ""
echo "🎉 Observability stack is running!"
echo ""
echo "📊 Access the services:"
echo "   Grafana:     http://localhost:3000 (admin/admin)"
echo "   Sample App:  http://localhost:8080"
echo "   Prometheus:  http://localhost:9090"
echo "   Pyroscope:   http://localhost:4040"
echo ""
echo "🔧 Generate test data:"
echo "   curl http://localhost:8080/generate-load"
echo "   curl http://localhost:8080/slow"
echo "   curl 'http://localhost:8080/error?type=500'"
echo ""
echo "📚 View logs with:"
echo "   docker compose logs -f [service-name]"
echo ""
echo "🛑 Stop the stack with:"
echo "   docker compose down"
echo ""