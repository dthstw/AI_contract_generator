# 🤖 AI Agent LayerX

**AI-powered Japanese Business Contract Generator with Web Interface**

This project implements an intelligent AI agent that generates professional Japanese business contracts using advanced language models. The system provides both a modern web interface and a command-line tool for contract generation, with full observability through Langfuse integration.

## 🎯 What This Project Does

I built this AI agent to solve the challenge of generating high-quality, legally-compliant Japanese business contracts automatically. The system:

- **Generates Professional Contracts**: Creates detailed Japanese lease agreements and outsourcing contracts
- **Maintains Legal Standards**: Uses carefully crafted prompts based on Japanese legal practices
- **Provides Dual Interfaces**: Both web UI and command-line access for different use cases
- **Ensures Observability**: Full tracing and monitoring through Langfuse integration
- **Handles Placeholders**: Automatically creates fillable contract templates

## ✨ Features

- 🌐 **Modern Web Interface**: User-friendly web application for contract generation
- 💻 **Command Line Tool**: Terminal-based interface for automation and scripting
- 📊 **Full Observability**: Langfuse integration for monitoring and debugging
- 🇯🇵 **Japanese Legal Compliance**: Prompts designed for Japanese business law
- 📝 **Multiple Contract Types**: Lease agreements, outsourcing contracts, and more
- 🔍 **Contract Search**: Search through generated contracts
- 📁 **File Management**: Automatic saving and organization of generated contracts

## 🔧 Prerequisites

- **Python 3.9+**
- **Docker & Docker Compose** (for Langfuse)
- **OpenAI API Key**
- **Git**

## 📦 Installation Guide

### Step 1: Clone the Project

```bash
git clone <your-repository-url>
cd ai-agent-layerx
```

### Step 2: Set Up Python Environment

#### Option 1: Using UV (Recommended)
```bash
# Install UV if you don't have it
brew install uv

# Create and activate virtual environment
uv venv .venv
source .venv/bin/activate

# Install the package with all dependencies
uv pip install -e .

# For development (includes testing tools)
uv pip install -e .[dev]
```

#### Option 2: Using pip
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows

# Install the package with all dependencies
pip install -e .

# For development (includes testing tools)
pip install -e .[dev]
```

### Step 3: Set Up Local Langfuse (Observability Platform)

#### Clone Langfuse Repository
```bash
# Navigate to parent directory
cd ..

# Clone Langfuse (if not already done)
git clone https://github.com/langfuse/langfuse.git
cd langfuse
```

#### Configure Langfuse
```bash
# Start Langfuse services
docker compose up -d
```

**Important**: The default configuration works for local development. You only need to generate a proper `NEXTAUTH_SECRET` if you encounter issues:

```bash
# Generate a secure NEXTAUTH_SECRET (if needed)
openssl rand -hex 32
```

#### Get Your API Keys
1. Open **http://localhost:3000** in your browser
2. **Sign up/Login** to create an account
3. **Create a new project** (or use existing)
4. **Go to Settings → API Keys**
5. **Copy your Public Key and Secret Key**

### Step 4: Configure Your AI Agent

Create a `.env` file in your AI Agent project directory:

```bash
cd ../ai-agent-layerx  # Back to your project
touch .env
```

Add the following configuration to your `.env` file:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_actual_openai_api_key_here
OPENAI_TEMPERATURE=0.2

# Langfuse Configuration (from your local instance)
LANGFUSE_PUBLIC_KEY=pk-lf-your-actual-public-key-here
LANGFUSE_SECRET_KEY=sk-lf-your-actual-secret-key-here
LANGFUSE_HOST=http://localhost:3000
```

**⚠️ Important**: Use the actual API keys from your local Langfuse instance, not placeholder values!

## 🚀 Usage Guide

### 🌐 Web Interface (Recommended)

Start the web server:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Then open **http://localhost:8000** in your browser.

**Web Interface Features:**
- 📝 **Contract Generation Form**: Easy-to-use interface for creating contracts
- 📋 **Contract History**: View all previously generated contracts
- 🔍 **Search Functionality**: Search through your contract database
- 📄 **Contract Preview**: View generated contracts directly in the browser

### 💻 Command Line Interface

The CLI provides powerful automation capabilities:

#### Basic Contract Generation

```bash
ai_agent generate_contract \
  --contract_type lease_agreement \
  --number_of_words 1000 \
  --party_a "LayerX Corp" \
  --party_b "Tenant Company"
```

#### Available Contract Types

- `lease_agreement` - Japanese lease agreements (賃貸借契約書)
- `outsourcing_contract` - Business outsourcing contracts (業務委託契約書)

#### Advanced Examples

```bash
# Generate a detailed lease agreement
ai_agent generate_contract \
  --contract_type lease_agreement \
  --number_of_words 2000 \
  --party_a "Real Estate Company Ltd" \
  --party_b "Business Tenant Corp" \
  --folder_to_save "contracts/2024"

# Generate an outsourcing contract
ai_agent generate_contract \
  --contract_type outsourcing_contract \
  --number_of_words 1500 \
  --party_a "Client Corporation" \
  --party_b "Service Provider Inc"
```

#### CLI Parameters

- `--contract_type`: Type of contract to generate (required)
- `--number_of_words`: Target word count (minimum 500, required)
- `--party_a`: Name of the first party (required)
- `--party_b`: Name of the second party (required)
- `--folder_to_save`: Output directory (default: "contracts")

## 📁 Generated Contracts

Contracts are automatically saved with descriptive filenames:
```
contracts/
├── lease_agreement_20250627_LayerX_Corp_Tenant_Company.txt
├── outsourcing_contract_20250627_Client_Corp_Service_Provider.txt
└── ...
```

## ⚠️ Known Limitations & Notes

### Word Count Precision
While I implemented sophisticated prompt engineering to control document length, **achieving exact word counts remains challenging**. The system:

- ✅ **Quality Over Quantity**: Prioritizes legal completeness and accuracy
- ⚠️ **Approximate Targeting**: Aims for ±5% of requested word count
- 🎯 **Smart Adjustment**: Uses content depth rather than filler text

### Document Quality
Despite word count challenges, the **contract quality is excellent**:
- ✅ **Legal Compliance**: Follows Japanese legal standards
- ✅ **Professional Language**: Uses appropriate legal terminology
- ✅ **Complete Structure**: Includes all necessary clauses
- ✅ **Proper Formatting**: Professional contract layout

### Performance Notes
- Initial contract generation may take 30-60 seconds
- Complex contracts (higher word counts) take longer
- Web interface provides real-time feedback

## 🔍 Troubleshooting

### Langfuse Authentication Errors

If you see OpenTelemetry authentication errors:

```
ERROR:opentelemetry.exporter.otlp.proto.http.trace_exporter:Failed to export batch code: 401
```

**Solution:**
1. Ensure Langfuse is running: `docker compose up -d` in langfuse directory
2. Verify your API keys are correct in `.env`
3. Check that `LANGFUSE_HOST=http://localhost:3000`

### Import Errors

If you get import errors, ensure the package is installed correctly:

```bash
pip install -e . --force-reinstall
```

### Web Interface Not Loading

1. Check that the server is running on the correct port
2. Ensure `index.html` exists in the project root
3. Verify all dependencies are installed

## 🛠️ Development

### Running Tests

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=src
```

### Project Structure

```
ai-agent-layerx/
├── src/                     # Source code
│   ├── cli.py              # Command line interface
│   ├── main.py             # Main application entry
│   ├── core/               # Core agent logic
│   ├── custom_agents/      # Agent implementations
│   ├── prompts/            # Contract generation prompts
│   └── tools/              # Utility tools
├── tests/                  # Test suite
├── contracts/              # Generated contracts (created automatically)
├── api.py                  # FastAPI web server
├── index.html              # Web interface
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

### Technology Stack

- **Backend**: FastAPI, Python 3.9+
- **AI Framework**: OpenAI Agents, OpenAI GPT models
- **Observability**: Langfuse
- **Frontend**: HTML/JavaScript (simple interface)
- **Packaging**: Modern Python packaging with pyproject.toml

## 🤝 Contributing

This project demonstrates advanced AI agent architecture with professional contract generation. The modular design allows for easy extension to new contract types and customization of generation parameters.

## 📄 License

MIT License - See LICENSE file for details.

---

**Note**: This project is designed for Japanese business contracts and requires understanding of Japanese legal terminology. Generated contracts should be reviewed by legal professionals before use in production environments.
