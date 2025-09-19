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

2. Set up environment variables:
   ```bash
   # Copy the environment template
   cp .env.template .env
   
   # Edit .env with your Azure service configurations
   ```
   
   **Required Environment Variables:**
   | Variable | Description | Example |
   |----------|-------------|---------|
   | `AZURE_OPENAI_ENDPOINT` | Azure OpenAI service endpoint URL | `https://your-openai.openai.azure.com` |
   | `AZURE_OPENAI_API_KEY` | API key for Azure OpenAI | `your-api-key-here` |
   | `AZURE_KEY_VAULT_URL` | Azure Key Vault URL (if using) | `https://your-keyvault.vault.azure.net/` |
   | `AZURE_CLIENT_ID` | Managed Identity Client ID (if using) | `00000000-0000-0000-0000-000000000000` |
   | `FRONTEND_URL` | Frontend application URL | `https://your-frontend.azurewebsites.net` |
   | `BACKEND_API_URL` | Backend API URL | `https://your-backend.azurewebsites.net` |
   | `APPLICATIONINSIGHTS_CONNECTION_STRING` | Application Insights connection string | `InstrumentationKey=...` |
   | `AZURE_SUBSCRIPTION_ID` | Azure subscription ID | `00000000-0000-0000-0000-000000000000` |
   | `AZURE_RESOURCE_GROUP` | Resource group name | `my-resource-group` |
   | `AZURE_LOCATION` | Azure region | `eastus` |
   
   **Environment Variable Setup Methods:**
   
   **Method 1: Using .env file (Local Development)**
   1. Copy `.env.template` to `.env`
   2. Edit `.env` file with your values:
      ```bash
      AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com
      AZURE_OPENAI_API_KEY=your-api-key-here
      AZURE_KEY_VAULT_URL=https://your-keyvault.vault.azure.net/
      # ... other variables
      ```
   
   **Method 2: Using Azure CLI (for local testing)**
   ```bash
   # Set environment variables for current session
   export AZURE_OPENAI_ENDPOINT="https://your-openai.openai.azure.com"
   export AZURE_OPENAI_API_KEY="your-api-key-here"
   export AZURE_KEY_VAULT_URL="https://your-keyvault.vault.azure.net/"
   # ... add other variables as needed
   ```
   
   **Method 3: Using Azure App Service Configuration (Production)**
   ```bash
   # Set app settings for your App Service
   az webapp config appsettings set --resource-group <resource-group> --name <app-name> \
     --settings AZURE_OPENAI_ENDPOINT="https://your-openai.openai.azure.com" \
                AZURE_OPENAI_API_KEY="your-api-key-here" \
                AZURE_KEY_VAULT_URL="https://your-keyvault.vault.azure.net/"
   ```
   
   **Finding Your Azure Service Values:**
   - **Azure OpenAI Endpoint & API Key**: Found in Azure Portal → AI Foundry → Your OpenAI resource
   - **Key Vault URL**: Azure Portal → Key Vault → Your vault → Properties → Vault URI
   - **Managed Identity Client ID**: Azure Portal → Managed Identity → Your identity → Properties → Client ID
   - **Application Insights Connection String**: Azure Portal → Application Insights → Your resource → Properties

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

## 🎓 ハンズオン形式で学ぶ
このプロジェクトはハンズオン形式で学習できるように設計されています。既存のAzureリソースを使用してCI/CDパイプラインを構築し、Pythonアプリケーションをデプロイする方法を学べます。

**👉 [ハンズオンガイドを始める](HANDS-ON-GUIDE.md)**

### 📖 詳細なドキュメント
- [DEPLOYMENT.md](DEPLOYMENT.md) - 詳細なデプロイメント手順
- [EXISTING-RESOURCES-CONFIG.md](EXISTING-RESOURCES-CONFIG.md) - 既存リソース使用時の設定
- [DEVELOPMENT.md](DEVELOPMENT.md) - 開発環境のセットアップ
- [TESTING.md](TESTING.md) - テスト実行方法

### 🚀 クイックスタート

#### 既存のAzureリソースがある場合:
1. [ハンズオンガイド](HANDS-ON-GUIDE.md)に従って設定を更新
2. CI/CDパイプラインを実行
3. アプリケーションの動作を確認

#### 新規でリソースを作成する場合:
Deploy to Azure using Azure Developer CLI:

```bash
azd auth login
azd init
azd up
```

## Configuration

### Main Application Configuration

Configure the application using environment variables in `.env`:

- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI service endpoint
- `AZURE_OPENAI_API_KEY`: API key for Azure OpenAI
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Deployment name for your model
- Additional configuration options available in `.env.template`

### Evaluation System Configuration

For the evaluation system (`eval/` directory), create a separate `.env` file:

```bash
# Navigate to eval directory
cd eval

# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
```

**Required variables for evaluation system:**
- `AZURE_SEARCH_ENDPOINT`: Azure AI Search service endpoint
- `AZURE_SEARCH_INDEX_NAME`: Search index name
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI endpoint (same as main app)
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Model deployment name
- `USE_MANAGED_IDENTITY`: Set to `true` for Azure-hosted deployment

**Security Best Practices:**
1. Never commit `.env` files to version control
2. Use Azure Key Vault for production secrets
3. Enable Managed Identity when deploying to Azure
4. Rotate API keys regularly
5. Use different configurations for development, staging, and production

**Troubleshooting Environment Variables:**
- Check if `.env` file exists in the correct directory
- Verify environment variable names match exactly (case-sensitive)
- Ensure no trailing spaces in variable values
- Use quotes for values containing special characters
- Check Azure resource permissions if using Managed Identity

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
