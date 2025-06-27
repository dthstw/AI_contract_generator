#!/bin/bash

# AI Agent Setup Script
# This script helps you set up the complete AI Agent stack with Langfuse

set -e

echo "🤖 AI Agent - Setup Script"
echo "=========================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check Docker Compose installation and determine which command to use
DOCKER_COMPOSE_CMD=""

# Try modern Docker Compose (docker compose) first
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
    echo "✅ Docker and Docker Compose (v2) are installed"
# Try legacy Docker Compose (docker-compose) as fallback
elif command -v docker-compose &> /dev/null && docker-compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
    echo "✅ Docker and Docker Compose (v1) are installed"
else
    echo "❌ Docker Compose is not properly installed or working."
    echo ""
    echo "🔧 Try these solutions:"
    echo "1. Install Docker Compose v2 (recommended):"
    echo "   sudo apt-get update && sudo apt-get install docker-compose-plugin"
    echo ""
    echo "2. Or install Docker Compose v1:"
    echo "   sudo curl -L \"https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose"
    echo "   sudo chmod +x /usr/local/bin/docker-compose"
    echo ""
    echo "3. Or use Docker Compose from pip:"
    echo "   pip install docker-compose"
    exit 1
fi
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
echo "🚀 Building and starting AI Agent stack..."
echo "   This may take a few minutes on first run..."
echo ""

# Check for problematic folder names that could cause Docker image naming issues
FOLDER_NAME=$(basename "$PWD")
if [[ "$FOLDER_NAME" =~ [^a-zA-Z0-9._-] ]] || [[ "$FOLDER_NAME" =~ ^[._-] ]] || [[ "$FOLDER_NAME" =~ [._-]$ ]]; then
    echo "⚠️  Warning: Folder name '$FOLDER_NAME' may cause Docker image naming issues."
    echo "   Consider renaming to use only letters, numbers, dots, dashes, and underscores."
    echo "   And avoid starting/ending with special characters."
    echo ""
fi

# Use the detected Docker Compose command
$DOCKER_COMPOSE_CMD up -d --build

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Your AI Agent stack is now running:"
echo ""
echo "🌐 Web Interface:     http://localhost:8000"
echo "📊 Langfuse Dashboard: http://localhost:3000"
echo "💾 MinIO Console:     http://localhost:9091"
echo ""
echo "📋 Next Steps:"
echo "1. Open http://localhost:3000 to set up Langfuse"
echo "2. Create a project and get your API keys"
echo "3. Update .env file with your Langfuse keys"
echo "4. Restart the stack: $DOCKER_COMPOSE_CMD restart ai-agent"
echo "5. Open http://localhost:8000 to use the AI Agent"
echo ""
echo "🔧 CLI Usage:"
echo "   Generate contract: $DOCKER_COMPOSE_CMD exec ai-agent ai_agent generate_contract --help"
echo "   Review contract:   $DOCKER_COMPOSE_CMD exec ai-agent ai_agent review_contract --help"
echo ""
echo "📖 For more information, check the README.md file"
echo "" 