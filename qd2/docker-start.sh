#!/bin/bash

# Quick Start Script for Docker Deployment
# This script helps you get started with Docker deployment quickly

set -e  # Exit on error

echo "=========================================="
echo "Patient Health RAG System - Docker Setup"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed!"
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker is installed"
echo "✓ Docker Compose is installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    
    if [ -f .env.docker ]; then
        cp .env.docker .env
    elif [ -f env_template.txt ]; then
        cp env_template.txt .env
    else
        echo "❌ No template file found!"
        exit 1
    fi
    
    echo ""
    echo "⚠️  IMPORTANT: You need to add your OpenAI API key!"
    echo ""
    read -p "Do you have your OpenAI API key ready? (y/n) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        read -p "Enter your OpenAI API key: " api_key
        
        # Update .env file with API key
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/sk-your-openai-api-key-here/$api_key/" .env
        else
            # Linux
            sed -i "s/sk-your-openai-api-key-here/$api_key/" .env
        fi
        
        echo "✓ API key configured"
    else
        echo ""
        echo "Please edit .env file and add your OpenAI API key:"
        echo "  OPENAI_API_KEY=sk-your-key-here"
        echo ""
        read -p "Press Enter when ready to continue..."
    fi
else
    echo "✓ .env file already exists"
    
    # Check if API key is set
    if grep -q "sk-your-openai-api-key-here" .env 2>/dev/null; then
        echo "⚠️  WARNING: Default API key detected in .env"
        echo "Please update your OpenAI API key in .env file"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

echo ""
echo "🚀 Starting Docker deployment..."
echo ""

# Build the application image
echo "📦 Building application image..."
docker-compose build app

# Start all services
echo ""
echo "🎬 Starting all services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service health
echo ""
echo "🔍 Checking service health..."

services=("qdrant" "postgres" "mongodb" "app")
all_healthy=true

for service in "${services[@]}"; do
    container_name="qd2-${service}"
    
    if docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
        status=$(docker inspect --format='{{.State.Status}}' $container_name 2>/dev/null || echo "unknown")
        
        if [ "$status" = "running" ]; then
            echo "  ✓ $service is running"
        else
            echo "  ❌ $service is not running (status: $status)"
            all_healthy=false
        fi
    else
        echo "  ❌ $service container not found"
        all_healthy=false
    fi
done

echo ""

if [ "$all_healthy" = true ]; then
    echo "=========================================="
    echo "✅ SUCCESS! All services are running!"
    echo "=========================================="
    echo ""
    echo "📍 Access Points:"
    echo "  • Frontend UI:    http://localhost:1531"
    echo "  • API Docs:       http://localhost:1531/docs"
    echo "  • Qdrant UI:      http://localhost:6333/dashboard"
    echo "  • Health Check:   http://localhost:1531/health"
    echo ""
    echo "📚 Next Steps:"
    echo "  1. Open frontend: http://localhost:1531"
    echo "  2. Upload patient data using the tabs"
    echo "  3. Ask questions about patient health"
    echo ""
    echo "🔧 Useful Commands:"
    echo "  • View logs:      docker-compose logs -f app"
    echo "  • Stop services:  docker-compose down"
    echo "  • Restart:        docker-compose restart app"
    echo "  • Shell access:   docker-compose exec app bash"
    echo ""
    echo "📖 Documentation: See DOCKER_DEPLOYMENT.md"
    echo ""
else
    echo "=========================================="
    echo "⚠️  WARNING: Some services failed to start"
    echo "=========================================="
    echo ""
    echo "Check logs with:"
    echo "  docker-compose logs -f"
    echo ""
    echo "Try restarting:"
    echo "  docker-compose restart"
    echo ""
fi

# Offer to open browser
echo ""
read -p "Open frontend in browser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v open &> /dev/null; then
        open http://localhost:1531
    elif command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:1531
    else
        echo "Please open http://localhost:1531 in your browser"
    fi
fi

echo ""
echo "Happy querying! 🎉"
