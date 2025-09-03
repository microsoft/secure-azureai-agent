# Development Guide

This guide provides detailed information for developers working on the Secure Azure AI Agent project.

## Project Structure

```
secure-azureai-agent/
├── azure.yaml                 # Azure Developer CLI configuration
├── README.md                  # Project overview and quick start
├── API.md                     # API documentation
├── CHANGELOG.md               # Version history
├── .env.sample               # Environment configuration template
├── backend/                  # FastAPI backend service
│   ├── requirements.txt      # Python dependencies
│   └── src/
│       ├── main.py          # FastAPI application entry point
│       ├── agents/          # Semantic Kernel agents
│       │   └── azure_troubleshoot_agent.py
│       └── telemetry/       # OpenTelemetry setup
│           └── setup.py
├── frontend/                 # Chainlit frontend
│   ├── app.py               # Chainlit application
│   ├── chainlit.md          # Frontend configuration
│   └── requirements.txt     # Frontend dependencies
└── eval/                    # Evaluation and testing
    ├── readteaming_test.ipynb
    └── requirements.txt
```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Azure subscription with OpenAI service
- Git
- VS Code (recommended)

### Environment Setup

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd secure-azureai-agent
   cp .env.sample .env
   ```

2. **Configure environment variables** in `.env`:
   - `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
   - `AZURE_OPENAI_API_KEY`: Your API key
   - `AZURE_OPENAI_DEPLOYMENT_NAME`: Your model deployment name

3. **Install dependencies**:
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd ../frontend
   pip install -r requirements.txt
   ```

### Running Locally

1. **Start the backend**:
   ```bash
   cd backend
   python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend** (in a new terminal):
   ```bash
   cd frontend
   chainlit run app.py --host 0.0.0.0 --port 8001
   ```

3. **Access the application**:
   - Frontend: http://localhost:8001
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Architecture Overview

### Backend Components

- **FastAPI Application** (`main.py`): REST API server with CORS support
- **Agent System** (`agents/`): Multi-agent architecture using Semantic Kernel
- **Telemetry** (`telemetry/`): OpenTelemetry integration for observability

### Frontend Components

- **Chainlit App** (`app.py`): Interactive chat interface
- **Backend Client**: HTTP client for API communication

### Agent Architecture

The system uses a multi-agent approach:

1. **Triage Agent**: Routes requests to appropriate specialists
2. **Technical Support Agent**: Handles general Azure troubleshooting
3. **Escalation Agent**: Manages complex or urgent issues
4. **Foundry Agent**: Specialized for Azure AI Foundry issues

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Include docstrings for classes and functions
- Keep functions focused and modular

### Error Handling

- Implement comprehensive error handling
- Use appropriate HTTP status codes
- Log errors with sufficient context
- Provide meaningful error messages to users

### Security Best Practices

- Never commit secrets or API keys
- Use environment variables for configuration
- Implement proper authentication and authorization
- Validate all user inputs
- Follow secure coding practices

### Testing

- Write unit tests for core functionality
- Test agent responses and routing
- Validate API endpoints
- Test error scenarios

### Logging and Monitoring

- Use structured logging
- Include correlation IDs for request tracking
- Monitor agent performance and accuracy
- Track user interaction patterns

## Deployment

### Azure Developer CLI (azd)

The project uses Azure Developer CLI for deployment:

```bash
# Login to Azure
azd auth login

# Initialize (first time only)
azd init

# Deploy to Azure
azd up
```

### Manual Deployment

1. **Create Azure Resources**:
   - App Service for backend
   - App Service for frontend
   - Application Insights for monitoring

2. **Configure Environment**:
   - Set environment variables in App Service configuration
   - Configure Azure AD authentication if needed

3. **Deploy Code**:
   - Use GitHub Actions or Azure DevOps
   - Deploy backend and frontend separately

## Troubleshooting

### Common Issues

1. **Agent not responding**:
   - Check Azure OpenAI endpoint configuration
   - Verify API key and deployment name
   - Check rate limits and quotas

2. **Frontend connection issues**:
   - Verify BACKEND_API_URL environment variable
   - Check CORS configuration in backend
   - Ensure both services are running

3. **Authentication errors**:
   - Verify Azure credentials
   - Check Azure AD configuration
   - Ensure proper permissions

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Monitoring

Monitor key metrics:
- Response times
- Agent success rates
- Error rates
- Resource utilization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Update documentation
6. Submit a pull request

Please follow the contributing guidelines and code of conduct.
