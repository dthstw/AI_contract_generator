#!/bin/bash

# AI Agent LayerX Setup Script
# This script helps you set up the complete AI Agent stack with Langfuse

set -e

echo "🤖 AI Agent LayerX - Setup Script"
echo "=================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.template .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit the .env file and add your OpenAI API key:"
    echo "   OPENAI_API_KEY=your_actual_api_key_here"
    echo ""
    read -p "Press Enter after you've added your OpenAI API key to .env file..."
else
    echo "✅ .env file already exists"
fi

# Check if OpenAI API key is set
if grep -q "your_openai_api_key_here" .env; then
    echo "⚠️  Warning: Please update your OpenAI API key in .env file"
    echo "   Current value appears to be the placeholder"
    echo ""
fi

# Create contracts directory
echo "📁 Creating contracts directory..."
mkdir -p contracts
echo "✅ Contracts directory created"
echo ""

# Build and start the services
echo "🚀 Building and starting AI Agent LayerX stack..."
echo "   This may take a few minutes on first run..."
echo ""

if docker compose version &> /dev/null; then
    docker compose up -d --build
else
    docker-compose up -d --build
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Your AI Agent LayerX stack is now running:"
echo ""
echo "🌐 Web Interface:     http://localhost:8000"
echo "📊 Langfuse Dashboard: http://localhost:3000"
echo "💾 MinIO Console:     http://localhost:9091"
echo ""
echo "📋 Next Steps:"
echo "1. Open http://localhost:3000 to set up Langfuse"
echo "2. Create a project and get your API keys"
echo "3. Update .env file with your Langfuse keys"
echo "4. Restart the stack: docker compose restart ai-agent"
echo "5. Open http://localhost:8000 to use the AI Agent"
echo ""
echo "🔧 CLI Usage:"
echo "   Generate contract: docker compose exec ai-agent ai_agent generate_contract --help"
echo "   Review contract:   docker compose exec ai-agent ai_agent review_contract --help"
echo ""
echo "📖 For more information, check the README.md file"
echo "" 