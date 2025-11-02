# AI-Powered Database Query Agent

An intelligent database query assistant built with LangChain, LangGraph, and LangSmith that allows users to interact with databases using natural language.

## 🚀 Features

- **Natural Language to SQL**: Convert plain English questions into optimized SQL queries
- **Multi-Database Support**: Connect to PostgreSQL, MySQL, SQLite, MongoDB, and more
- **Intelligent Query Optimization**: Automatic query performance analysis and suggestions
- **Safety First**: Built-in query validation and read-only access controls
- **Conversational Context**: Maintains context across multiple queries in a session
- **Query Explanation**: Human-readable explanations of generated SQL queries
- **Schema Understanding**: Automatic database schema analysis and relationship mapping

## 🏗️ Architecture

This project uses a multi-agent architecture powered by:

- **LangChain**: Database connectors and SQL toolkits
- **LangGraph**: Multi-agent workflow orchestration
- **LangSmith**: Query monitoring, tracking, and continuous improvement

### Agent Roles

1. **Schema Analyzer**: Understands database structure and relationships
2. **Query Generator**: Converts natural language to SQL
3. **Safety Validator**: Ensures query safety and permissions
4. **Query Optimizer**: Suggests performance improvements
5. **Result Explainer**: Provides human-readable query explanations

## 🛠️ Installation

```bash
# Clone the repository
git clone <repository-url>
cd ai-database-query-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database connections and API keys
```

## ⚙️ Configuration

### LLM Provider Setup

This project supports multiple LLM providers. Choose the one that best fits your needs:

#### Option 1: Ollama (Recommended for Local Development)
**Advantages**: Free, runs locally, no API costs, privacy-focused

1. Install Ollama:
   ```bash
   # macOS
   brew install ollama
   
   # Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Windows: Download from https://ollama.ai
   ```

2. Start Ollama server:
   ```bash
   ollama serve
   ```

3. Download a recommended model:
   ```bash
   # Best for SQL generation
   ollama pull codellama:7b
   
   # Alternative options
   ollama pull llama2:7b
   ollama pull mistral:7b
   ```

4. Update your `.env` file:
   ```env
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=codellama:7b
   ```

#### Option 2: OpenAI API
**Advantages**: Highest quality results, no local setup required

1. Get an API key from [OpenAI](https://platform.openai.com/)
2. Update your `.env` file:
   ```env
   LLM_PROVIDER=openai
   OPENAI_API_KEY=your_api_key_here
   DEFAULT_LLM_MODEL=gpt-4
   ```

#### Option 3: Anthropic Claude
**Advantages**: Strong reasoning capabilities, good for complex queries

1. Get an API key from [Anthropic](https://console.anthropic.com/)
2. Update your `.env` file:
   ```env
   LLM_PROVIDER=anthropic
   ANTHROPIC_API_KEY=your_api_key_here
   ```

### Database Configuration

1. Copy `.env.example` to `.env`
2. Configure your database connections
3. Set up LangSmith project (optional but recommended for monitoring)

## 🚦 Quick Start

### Option 1: Using Ollama (Local LLM)

```bash
# 1. Install and set up Ollama
python scripts/setup_ollama.py

# 2. Test the integration
python scripts/test_ollama.py

# 3. Use the agent
from src.main import DatabaseQueryAgent

agent = DatabaseQueryAgent()
await agent.connect_database("sqlite:///example.db")
response = await agent.query("Show me the top 10 customers by revenue")
```

### Option 2: Using OpenAI API

```python
import os
from src.main import DatabaseQueryAgent
from src.utils.config import Settings

# Configure for OpenAI
settings = Settings(
    llm_provider="openai",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

agent = DatabaseQueryAgent(settings)
await agent.connect_database("postgresql://user:pass@localhost/mydb")
response = await agent.query("Show me the top 10 customers by revenue this year")
```

## 📁 Project Structure

```
├── src/
│   ├── agents/              # LangGraph agents
│   ├── database/           # Database connectors and utilities
│   ├── models/             # Data models and schemas
│   ├── utils/              # Utility functions
│   └── main.py             # Main application entry point
├── tests/                  # Test files
├── docs/                   # Documentation
├── examples/               # Usage examples
├── config/                 # Configuration files
└── scripts/                # Utility scripts
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
```

## 📊 Monitoring

This project integrates with LangSmith for:
- Query performance monitoring
- Agent conversation tracking
- Continuous improvement through usage analytics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/your-username/ai-database-query-agent/issues)
- Discussions: [GitHub Discussions](https://github.com/your-username/ai-database-query-agent/discussions)

## 🗺️ Roadmap

- [ ] Multi-database connection management
- [ ] Advanced query optimization
- [ ] Data visualization integration
- [ ] Real-time collaboration features
- [ ] Enterprise SSO integration
- [ ] Custom agent training capabilities
