#!/bin/bash

# BasoKa PSN Bot Docker Deployment Script
# Usage: ./deploy.sh [production|development]

set -e

ENVIRONMENT=${1:-development}
PROJECT_NAME="basoka-psn-bot"

echo "🚀 Deploying BasoKa PSN Bot in $ENVIRONMENT mode..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Please copy .env.example to .env and configure it:"
    echo "   cp .env.example .env"
    exit 1
fi

# Validate environment variables
if ! grep -q "BOT_TOKEN=" .env || ! grep -q "AUTHORIZED_USER_IDS=" .env; then
    echo "⚠️  Please ensure BOT_TOKEN and AUTHORIZED_USER_IDS are set in .env"
    exit 1
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start containers
echo "🔨 Building and starting containers..."
if [ "$ENVIRONMENT" = "production" ]; then
    docker-compose up -d --build
else
    docker-compose up --build
fi

echo "✅ BasoKa PSN Bot deployed successfully!"
echo "📋 Container status:"
docker-compose ps

if [ "$ENVIRONMENT" = "production" ]; then
    echo ""
    echo "📊 To view logs: docker-compose logs -f"
    echo "🛑 To stop: docker-compose down"
    echo "🔄 To restart: docker-compose restart"
fi
