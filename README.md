# Secure Azure AI Agent

A secure, enterprise-ready AI agent system for Azure troubleshooting and support scenarios. This application provides intelligent assistance for Azure-related issues through a multi-agent architecture built with Microsoft Semantic Kernel.

## Features

- **Multi-Agent Architecture**: Specialized agents for different types of Azure troubleshooting scenarios
- **Secure by Design**: Enterprise security features with Azure AD integration and secure credential management
- **Real-time Chat Interface**: Interactive web-based chat powered by Chainlit
- **Azure Integration**: Deep integration with Azure services and APIs for comprehensive troubleshooting
- **Observability**: Built-in telemetry and monitoring with OpenTelemetry
- **Scalable Deployment**: Ready for Azure App Service deployment with infrastructure as code

## Architecture

- **Backend**: FastAPI-based REST API with Semantic Kernel agents
- **Frontend**: Chainlit web interface for user interactions
- **Infrastructure**: Azure App Service deployment with Bicep templates
- **AI Services**: Azure OpenAI integration for intelligent responses

## Quick Start

### Prerequisites

- Python 3.8+
- Azure subscription
- Azure OpenAI service endpoint

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/microsoft/secure-azureai-agent.git
   cd secure-azureai-agent
   ```

2. Copy the environment file and configure your settings:
   ```bash
   cp .env.sample .env
   # Edit .env with your Azure OpenAI and other service configurations
   ```

3. Install dependencies:
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd ../frontend
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   # Start backend (in one terminal)
   cd backend
   python -m uvicorn src.main:app --reload
   
   # Start frontend (in another terminal)
   cd frontend
   chainlit run app.py
   ```

### Azure Deployment

Deploy to Azure using Azure Developer CLI:

```bash
azd auth login
azd init
azd up
```

## Configuration

Configure the application using environment variables in `.env`:

- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI service endpoint
- `AZURE_OPENAI_API_KEY`: API key for Azure OpenAI
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Deployment name for your model
- Additional configuration options available in `.env.sample`

## Documentation

- **[Architecture Overview](./ARCHITECTURE.md)**: System design and technical architecture
- **[API Documentation](./API.md)**: Detailed API endpoint documentation
- **[Development Guide](./DEVELOPMENT.md)**: Comprehensive development setup and guidelines
- **[Deployment Guide](./DEPLOYMENT.md)**: Complete deployment instructions for various environments
- **[Testing Guide](./TESTING.md)**: Testing strategy, red team testing, and quality assurance
- **[Changelog](./CHANGELOG.md)**: Version history and release notes
- **[Support](./SUPPORT.md)**: How to get help and file issues
- **[Security](./SECURITY.md)**: Security reporting and guidelines

## Agent Capabilities

The system includes specialized agents for different scenarios:

- **Triage Agent**: Intelligent request routing and classification
- **Technical Support Agent**: General Azure troubleshooting and guidance
- **Escalation Agent**: Complex issue handling and expert consultation
- **Foundry Technical Support Agent**: Azure AI Foundry specific support

## Security Features

- Enterprise-grade security with Azure AD integration
- Secure credential management and environment configuration
- OpenTelemetry observability for monitoring and compliance
- Following Microsoft security best practices

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit [Contributor License Agreements](https://cla.opensource.microsoft.com).

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
