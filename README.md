# Electronics_SupportAgent 🧠

A sophisticated RAG (Retrieval-Augmented Generation) knowledge base system for electronics support, built with LanceDB, Cognee, and n8n workflow automation.

## 🎯 Overview

Electronics_SupportAgent is an intelligent support system designed for companies like Samsung/LG, handling queries for TVs, Fridges, Washing Machines, Speakers, and other electronics. It combines multiple AI technologies to provide accurate, validated solutions with continuous learning capabilities.

## 🏗️ Architecture

### Core Components
- **LanceDB**: Vector database for efficient similarity search
- **Cognee**: AI memory engine with knowledge graphs
- **Kuzu**: Graph database for relationship mapping
- **OpenAI**: LLM for response generation and validation
- **Streamlit**: Web interface for chat and admin
- **FastAPI**: RESTful API services
- **n8n**: Workflow automation for production deployment

### Data Flow
```
User Query → Manual Knowledge (Priority) → Cognee AI Memory → OpenAI Generation → Validation → Response
```

## 🚀 Features

### 🤖 AI-Powered Support
- **Intelligent Query Processing**: Multi-source knowledge retrieval
- **Answer Validation**: AI-powered response quality assessment
- **Confidence Scoring**: Reliability indicators for responses
- **Graceful Degradation**: System resilience when APIs are unavailable

### 📚 Knowledge Management
- **Manual Knowledge Store**: Human-validated solutions with priority
- **Continuous Learning**: Feedback loop for system improvement
- **Multi-format Support**: PDF, DOCX, TXT, MD document processing
- **Brand-specific Filtering**: Samsung, LG, and other electronics brands

### 🔄 Learning & Feedback
- **Real-time Feedback**: User satisfaction tracking
- **Manual Learning**: Support agent solutions integration
- **Analytics Dashboard**: System performance monitoring
- **Admin Interface**: Raw data access and management

### 🎛️ Workflow Automation
- **n8n Integration**: Production-ready workflow orchestration
- **Webhook Support**: RESTful API endpoints
- **Service Monitoring**: Health checks and status monitoring
- **Error Handling**: Robust error recovery and logging

## 📋 Prerequisites

### System Requirements
- Python 3.8+
- Node.js 20.19+ (for n8n)
- 8GB+ RAM (for AI models)
- macOS/Linux/Windows

### API Keys Required
- OpenAI API Key (for LLM operations)
- Cognee API Key (optional, for advanced features)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/Electronics_SupportAgent.git
cd Electronics_SupportAgent
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install n8n (for workflow automation)
```bash
npm install -g n8n
```

### 4. Environment Setup
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### 5. Initialize the System
```bash
python main_cognee_enhanced.py --mode setup
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
COGNEE_API_KEY=your_cognee_api_key_here

# Database Paths
LANCEDB_PATH=./lancedb_data
MANUAL_KNOWLEDGE_PATH=./manual_knowledge_db
FEEDBACK_DATA_PATH=./feedback_data

# System Configuration
VECTOR_DIMENSION=384
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_TOKENS=2000
```

### Supported Brands & Products
- **Samsung**: TVs, Fridges, Washing Machines, Speakers
- **LG**: TVs, Fridges, Washing Machines, Speakers
- **Other Electronics**: Expandable via configuration

## 🚀 Quick Start

### 1. Start the Core System
```bash
# Start the main application
python main_cognee_enhanced.py --mode web

# Or start individual services
python -m uvicorn lance_code:app --host 0.0.0.0 --port 8000
python -m uvicorn cognee_code:app --host 0.0.0.0 --port 9000
```

### 2. Access the Web Interface
- **Chat Interface**: http://localhost:8505
- **Admin Panel**: http://localhost:8505 (Admin tab)
- **API Documentation**: http://localhost:8000/docs

### 3. Test the System
```bash
# Test the RAG system
python test_system.py

# Test n8n workflow
python n8n/test_workflow_activation.py
```

## 📊 Usage Examples

### Chat Interface
```python
# Query the system
query = "Samsung TV won't turn on after power outage"
response = rag_engine.intelligent_query(query)
print(response)
```

### API Usage
```bash
# Manual knowledge search
curl -X POST "http://localhost:8000/manual_search" \
  -H "Content-Type: application/json" \
  -d '{"question": "Samsung TV power issue"}'

# Cognee AI memory query
curl -X POST "http://localhost:9000/cognee_query" \
  -H "Content-Type: application/json" \
  -d '{"query": "LG fridge not cooling"}'
```

### n8n Workflow
```bash
# Test the n8n webhook
curl -X POST "http://localhost:5678/webhook/test_lancedb" \
  -H "Content-Type: application/json" \
  -d '{"query": "Samsung TV won'\''t turn on"}'
```

## 🧪 Testing

### System Tests
```bash
# Run comprehensive tests
python test_system.py
python test_enhanced_features.py
python test_cognee_system.py

# Test specific components
python test_manual_knowledge_fix.py
python test_cognee_population.py
```

### n8n Tests
```bash
# Test n8n workflow activation
python n8n/test_workflow_activation.py

# Test multiple queries
python n8n/test_multiple_queries.py
```

## 📈 Monitoring & Analytics

### System Status
```bash
# Check system health
python admin_cli.py status

# View raw data
python admin_cli.py raw-data
```

### Performance Metrics
- Query response time
- Manual knowledge hit rate
- Cognee memory utilization
- Validation accuracy scores
- User satisfaction ratings

## 🔧 Administration

### Admin CLI
```bash
# System overview
python admin_cli.py overview

# Database inspection
python admin_cli.py lancedb
python admin_cli.py cognee
python admin_cli.py kuzu

# Cross-database search
python admin_cli.py search "Samsung TV"
```

### Web Admin Panel
- Raw data viewer
- System analytics
- Memory insights
- Database management

## 🎨 Visualization

### Knowledge Graph Visualization
```bash
# Generate Kuzu graph visualization
python visualize_kuzu_graph.py

# View interactive graph
open mock_kuzu_graph.html
```

## 🔄 Continuous Learning

### Feedback Integration
1. User submits query
2. System provides response
3. User rates satisfaction
4. If dissatisfied, support agent provides solution
5. Solution is logged to manual knowledge store
6. Future queries prioritize manual knowledge

### Manual Knowledge Management
- High-satisfaction solutions automatically added
- Brand and product-specific filtering
- Confidence scoring based on success rate
- Regular cleanup of outdated entries

## 🚨 Troubleshooting

### Common Issues

#### OpenAI API Errors
```bash
# Check API key configuration
echo $OPENAI_API_KEY

# Test API connection
python -c "import openai; openai.api_key='your_key'; print('API working')"
```

#### LanceDB Schema Issues
```bash
# Reset LanceDB tables
rm -rf lancedb_data/
python main_cognee_enhanced.py --mode setup
```

#### n8n Connection Issues
```bash
# Check n8n status
n8n status

# Restart n8n
n8n start --tunnel
```

#### Cognee Memory Issues
```bash
# Check Cognee configuration
python -c "import cognee; print(cognee.__version__)"

# Reset Cognee memory
rm -rf ~/.cognee_system/
```

### Debug Mode
```bash
# Enable debug logging
export DEBUG=1
python main_cognee_enhanced.py --mode debug
```

## 📚 API Documentation

### Core Endpoints

#### Manual Knowledge Search
```http
POST /manual_search
Content-Type: application/json

{
  "question": "Samsung TV won't turn on"
}
```

#### Cognee AI Memory Query
```http
POST /cognee_query
Content-Type: application/json

{
  "query": "LG fridge not cooling"
}
```

#### Answer Validation
```http
POST /validate_answer
Content-Type: application/json

{
  "answer": "Try unplugging the TV...",
  "question": "Samsung TV power issue"
}
```

#### Feedback Logging
```http
POST /log_interaction
Content-Type: application/json

{
  "query": "Samsung TV issue",
  "response": "Try this solution...",
  "satisfaction": 4,
  "manual_solution": "Support agent solution..."
}
```

## 🤝 Contributing

### Development Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest tests/
```

### Code Style
- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add docstrings for all functions
- Include tests for new features

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LanceDB**: For efficient vector database capabilities
- **Cognee**: For AI memory engine and knowledge graphs
- **OpenAI**: For LLM capabilities
- **n8n**: For workflow automation
- **Streamlit**: For web interface framework

## 📞 Support

### Getting Help
- **Documentation**: Check the `docs/` directory
- **Issues**: Use GitHub Issues for bug reports
- **Discussions**: Use GitHub Discussions for questions
- **Wiki**: Check the project wiki for detailed guides

### Community
- **Discord**: Join our community server
- **Slack**: Connect with other developers
- **Email**: support@electronics-support-agent.com

---

**Made with ❤️ for intelligent electronics support** 