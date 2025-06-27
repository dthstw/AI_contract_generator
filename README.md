# 🤖 AI Agent LayerX

**AI-powered Japanese Business Contract Generator with Integrated Observability**

This project implements an intelligent AI agent that generates professional Japanese business contracts using OpenAI's GPT-4o model. The system provides both a modern web interface and command-line tools, with complete observability through integrated Langfuse tracing.

## 🎯 What This Project Does

An AI agent system that generates high-quality, legally-compliant Japanese business contracts with:

- **Professional Contract Generation**: Creates detailed Japanese lease agreements and outsourcing contracts
- **Dual Interface Options**: Modern web UI and powerful command-line interface
- **Complete Observability**: Integrated Langfuse tracing for monitoring and debugging
- **Docker-First Architecture**: Everything runs in containers for easy deployment
- **Japanese Legal Compliance**: Prompts designed for Japanese business law standards

## ✨ Features

- 🌐 **Modern Web Interface**: User-friendly contract generation with real-time feedback
- 💻 **Command Line Tools**: Terminal-based interface for automation and scripting
- 📊 **Integrated Observability**: Built-in Langfuse stack for complete tracing
- 🇯🇵 **Japanese Legal Focus**: Specialized prompts for Japanese business contracts
- 📝 **Multiple Contract Types**: Lease agreements, outsourcing contracts, and more
- 🔍 **Contract Search & Management**: Search and browse generated contracts
- 🐳 **Docker-Ready**: Complete stack deployment with single command

## 🔧 Prerequisites

- **Docker & Docker Compose**
- **OpenAI API Key**
- **Git**

That's it! No Python setup required - everything runs in containers.

## 🚀 Quick Start

### Automated Setup (Recommended)

```bash
# 1. Clone the project
git clone https://github.com/yourusername/AI_Agent_fin.git
cd AI_Agent_fin

# 2. Run the setup script
chmod +x setup.sh
./setup.sh
```

The setup script will:
- ✅ Check Docker installation
- ✅ Create configuration files
- ✅ Prompt for your OpenAI API key
- ✅ Build and start the complete stack
- ✅ Show you all the URLs to access

### Manual Setup

```bash
# 1. Clone and configure
git clone https://github.com/yourusername/AI_Agent_fin.git
cd AI_Agent_fin

# 2. Set up environment
cp env.template .env
# Edit .env and add your OpenAI API key

# 3. Start the stack
docker-compose up -d
```

## 🌐 Access Your Services

After setup, you'll have access to:

- **🤖 AI Agent Web Interface**: http://localhost:8000
- **📊 Langfuse Dashboard**: http://localhost:3000  
- **💾 MinIO Console**: http://localhost:9091

## 📋 Configuration

Edit your `.env` file with the required settings:

```env
# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY=your_actual_openai_api_key_here
OPENAI_TEMPERATURE=0.2

# Langfuse Configuration (Auto-configured)
LANGFUSE_PUBLIC_KEY=pk-lf-your-keys-from-langfuse-dashboard
LANGFUSE_SECRET_KEY=sk-lf-your-keys-from-langfuse-dashboard
LANGFUSE_HOST=http://langfuse-web:3000
```

**Getting Langfuse Keys:**
1. Open http://localhost:3000
2. Sign up and create a project
3. Go to Settings → API Keys
4. Copy your keys to `.env`
5. Restart: `docker-compose restart ai-agent`

## 🎯 Usage

### Web Interface (Recommended)

1. Open **http://localhost:8000**
2. Fill in the contract generation form
3. Click "Generate Contract"
4. View results and browse contract history

### Command Line Interface

Execute commands inside the Docker container:

```bash
# Generate a lease agreement
docker-compose exec ai-agent ai_agent generate_contract \
  --contract_type lease_agreement \
  --number_of_words 1000 \
  --party_a "LayerX Corp" \
  --party_b "Tenant Company"

# Generate an outsourcing contract
docker-compose exec ai-agent ai_agent generate_contract \
  --contract_type outsourcing_contract \
  --number_of_words 1500 \
  --party_a "Client Corp" \
  --party_b "Service Provider"

# Review a contract
docker-compose exec ai-agent ai_agent review_contract \
  --contract_file contracts/your_contract.txt \
  --review_type comprehensive
```

### Available Contract Types

- `lease_agreement` - Japanese lease agreements (賃貸借契約書)
- `outsourcing_contract` - Business outsourcing contracts (業務委託契約書)

## 📁 Generated Contracts

Contracts are automatically saved with descriptive filenames:

```
contracts/
├── lease_agreement_20240627_LayerX_Corp_Tenant_Company.txt
├── outsourcing_contract_20240627_Client_Corp_Service_Provider.txt
└── ...
```

## 🔍 Monitoring & Observability

The integrated Langfuse dashboard (http://localhost:3000) provides:

- **Complete Trace Visibility**: See every step of contract generation
- **Token Usage Tracking**: Monitor OpenAI API costs
- **Performance Metrics**: Response times and success rates
- **Error Debugging**: Detailed error traces and logs
- **Generation Analytics**: Track contract types and patterns

## ⚠️ Known Limitations

### Word Count Precision
- **Target**: Aims for ±5% of requested word count
- **Priority**: Focuses on legal completeness over exact word count
- **Quality**: Maintains professional legal language throughout

### Performance Notes
- Initial contract generation: 30-60 seconds
- Complex contracts take longer
- Web interface provides real-time progress feedback

## 🛠️ Development & Testing

### View Logs
```bash
# View all services
docker-compose logs

# View specific service
docker-compose logs ai-agent
docker-compose logs langfuse-web
```

### Restart Services
```bash
# Restart everything
docker-compose restart

# Restart specific service
docker-compose restart ai-agent
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## 🏗️ Architecture

### Technology Stack
- **AI Framework**: OpenAI Agents SDK with GPT-4o
- **Backend**: FastAPI with async support
- **Frontend**: Modern HTML/JavaScript interface
- **Observability**: Langfuse with complete tracing
- **Storage**: PostgreSQL, Redis, ClickHouse, MinIO
- **Deployment**: Docker Compose with health checks

### Service Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │───▶│   AI Agent      │───▶│   OpenAI API    │
│  localhost:8000 │    │  (FastAPI)      │    │   (GPT-4o)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Langfuse      │───▶│   Storage       │
                       │  (Observability)│    │ (Postgres/etc)  │
                       └─────────────────┘    └─────────────────┘
```

## 🔧 Troubleshooting

### Services Won't Start
```bash
# Check Docker is running
docker --version
docker-compose --version

# Check port conflicts
docker-compose ps
```

### OpenAI API Errors
- Verify your API key in `.env`
- Check API key permissions and billing
- Monitor usage in Langfuse dashboard

### Langfuse Connection Issues
- Ensure all services are healthy: `docker-compose ps`
- Check Langfuse keys are correctly set
- Restart the ai-agent service: `docker-compose restart ai-agent`

### Contract Generation Fails
- Check logs: `docker-compose logs ai-agent`
- Verify OpenAI API key and quota
- Check Langfuse traces for detailed error information

## 📄 Assignment Compliance

This project fulfills all requirements:

- ✅ **Core AI Agent Logic**: Implemented using OpenAI Agent SDK
- ✅ **Docker Compose Packaging**: Complete integrated stack
- ✅ **Error Handling & Tracing**: Comprehensive Langfuse integration
- ✅ **LLM Integration**: OpenAI GPT-4o with configurable parameters

**Model Choice**: Focused on OpenAI GPT-4o due to API key availability. The architecture supports multiple LLM providers through the ModelProvider interface.

## 📄 License

MIT License - See LICENSE file for details.

---

**Note**: This project generates Japanese business contracts and requires understanding of Japanese legal terminology. Generated contracts should be reviewed by legal professionals before production use.
