#!/bin/bash

# FortiDesk Docker Startup Script

echo "🏉 Starting FortiDesk Application..."

# Check if .env file exists, if not copy from .env.docker
if [ ! -f .env ]; then
    echo "Creating .env file from .env.docker template..."
    cp .env.docker .env
    echo "⚠️  Please review and update .env file with your production settings!"
fi

# Build and start containers
echo "Building Docker images..."
docker-compose build

echo "Starting services..."
docker-compose up -d

echo "Waiting for services to be ready..."
sleep 10

# Check service health
echo "Checking service status..."
docker-compose ps

echo ""
echo "✅ FortiDesk is starting up!"
echo "🌐 Application will be available at: http://localhost"
echo "🗄️  MySQL database is available at: localhost:3306"
echo ""
echo "📋 Default admin credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "To monitor logs: docker-compose logs -f"
echo "To stop services: docker-compose down"