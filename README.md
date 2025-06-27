# AI Agent

AI-powered Japanese business contract generator with web interface and CLI tools. Built with OpenAI GPT-4o and integrated Langfuse observability.

## Features

- **Contract Generation**: Japanese lease agreements and outsourcing contracts
- **Dual Interface**: Web UI and command-line tools
- **Observability**: Complete tracing with Langfuse
- **Docker Deployment**: Single-command setup

## Prerequisites

- Docker & Docker Compose
- OpenAI API Key
- Free ports 3000 and 8000 (or modify docker-compose.yml)

## Quick Start

```bash
git clone https://github.com/yourusername/AI_Agent_fin.git
cd AI_Agent_fin
chmod +x setup.sh
./setup.sh
```

The setup script will:
1. Create `.env` from template
2. Prompt for your OpenAI API key
3. Start all services

**Access:**
- Web Interface: http://localhost:8000
- Langfuse Dashboard: http://localhost:3000

## Configuration

Edit `.env` with your API keys:

```env
# Required
OPENAI_API_KEY=your_actual_openai_api_key_here
OPENAI_MODEL=gpt-4o

# Get from Langfuse dashboard after first run
LANGFUSE_PUBLIC_KEY=pk-lf-your-keys-here
LANGFUSE_SECRET_KEY=sk-lf-your-keys-here
```

**Getting Langfuse Keys:**
1. Open http://localhost:3000
2. Sign up → Create project → Settings → API Keys
3. Copy keys to `.env`
4. Restart: `docker compose restart ai-agent`

## Usage

### Web Interface
1. Open http://localhost:8000
2. Select contract type and parameters
3. Generate contract

### CLI
```bash
docker compose exec ai-agent ai_agent generate_contract \
  --contract_type lease_agreement \
  --number_of_words 1000 \
  --party_a "Company A" \
  --party_b "Company B"
```

**Contract Types:**
- `lease_agreement` - Japanese lease agreements
- `outsourcing_contract` - Business outsourcing contracts

## Troubleshooting

### Port Conflicts
If ports 3000/8000 are in use:
```bash
# Check what's using ports
lsof -i :3000
lsof -i :8000

# Modify docker-compose.yml ports section
langfuse-web:
  ports:
    - "3004:3000"  # Use different external port
```

### Common Issues
- **Services won't start**: `docker compose ps` to check status
- **OpenAI errors**: Verify API key and billing
- **Langfuse connection**: Ensure keys are correct in `.env`

## Development

```bash
# View logs
docker compose logs ai-agent

# Restart services
docker compose restart

# Stop everything
docker compose down
```

## Architecture

Docker Compose orchestrates AI Agent (FastAPI), Langfuse (observability), and supporting databases. The AI Agent connects to OpenAI's API for contract generation.
