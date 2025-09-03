# Deployment Guide

This guide provides comprehensive instructions for deploying the Secure Azure AI Agent to various environments.

## Deployment Options

1. **Azure Developer CLI (Recommended)**: One-command deployment
2. **Azure Portal**: Manual resource creation and deployment
3. **GitHub Actions**: Automated CI/CD pipeline
4. **Docker Containers**: Containerized deployment

## Prerequisites

### Azure Resources Required

- Azure subscription with appropriate permissions
- Azure OpenAI service with GPT-4 or GPT-3.5-turbo deployment
- (Optional) Azure AI Foundry project for advanced agent capabilities
- (Optional) Application Insights for monitoring

### Tools Required

- [Azure Developer CLI (azd)](https://docs.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- Git
- Python 3.8+

## Option 1: Azure Developer CLI (azd) Deployment

This is the recommended deployment method for its simplicity and best practices.

### 1. Initial Setup

```bash
# Install Azure Developer CLI
# Windows
winget install microsoft.azd

# macOS
brew tap azure/azd && brew install azd

# Linux
curl -fsSL https://aka.ms/install-azd.sh | bash
```

### 2. Authentication

```bash
# Login to Azure
azd auth login

# Verify login
azd auth logout && azd auth login
```

### 3. Project Initialization

```bash
# Clone the repository
git clone https://github.com/microsoft/secure-azureai-agent.git
cd secure-azureai-agent

# Initialize azd project (first time only)
azd init

# Follow prompts to:
# - Choose environment name (e.g., "prod", "dev", "staging")
# - Select Azure subscription
# - Choose Azure region
```

### 4. Environment Configuration

```bash
# Set required environment variables
azd env set AZURE_OPENAI_ENDPOINT "https://your-openai-resource.openai.azure.com/"
azd env set AZURE_OPENAI_API_KEY "your-openai-api-key"
azd env set AZURE_OPENAI_DEPLOYMENT_NAME "gpt-4"

# Optional: Azure AI Foundry configuration
azd env set USE_AZURE_AI_AGENT "true"
azd env set PROJECT_ENDPOINT "https://your-project.services.ai.azure.com/api/projects/firstProject"
azd env set FOUNDARY_TECHNICAL_SUPPORT_AGENT_ID "your-agent-id"
```

### 5. Deploy

```bash
# Deploy infrastructure and application
azd up

# This will:
# - Create Azure resources (App Services, Application Insights, etc.)
# - Deploy backend and frontend applications
# - Configure networking and security
# - Set up monitoring and logging
```

### 6. Post-Deployment

```bash
# Get deployment information
azd show

# View application URLs
azd env get-values

# Monitor deployment
azd monitor
```

## Option 2: Manual Azure Portal Deployment

### 1. Create Azure Resources

#### Resource Group
```bash
az group create --name rg-secure-azureai-agent --location eastus
```

#### App Service Plan
```bash
az appservice plan create \
  --name plan-secure-azureai-agent \
  --resource-group rg-secure-azureai-agent \
  --sku B1 \
  --is-linux
```

#### Backend App Service
```bash
az webapp create \
  --resource-group rg-secure-azureai-agent \
  --plan plan-secure-azureai-agent \
  --name app-secure-azureai-backend \
  --runtime "PYTHON|3.9"
```

#### Frontend App Service
```bash
az webapp create \
  --resource-group rg-secure-azureai-agent \
  --plan plan-secure-azureai-agent \
  --name app-secure-azureai-frontend \
  --runtime "PYTHON|3.9"
```

#### Application Insights
```bash
az monitor app-insights component create \
  --app insights-secure-azureai-agent \
  --location eastus \
  --resource-group rg-secure-azureai-agent
```

### 2. Configure App Settings

#### Backend Configuration
```bash
az webapp config appsettings set \
  --resource-group rg-secure-azureai-agent \
  --name app-secure-azureai-backend \
  --settings \
    AZURE_OPENAI_ENDPOINT="https://your-openai-resource.openai.azure.com/" \
    AZURE_OPENAI_API_KEY="your-openai-api-key" \
    AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4" \
    APPLICATIONINSIGHTS_CONNECTION_STRING="your-app-insights-connection-string"
```

#### Frontend Configuration
```bash
az webapp config appsettings set \
  --resource-group rg-secure-azureai-agent \
  --name app-secure-azureai-frontend \
  --settings \
    BACKEND_API_URL="https://app-secure-azureai-backend.azurewebsites.net"
```

### 3. Deploy Code

#### Using Azure CLI
```bash
# Deploy backend
cd backend
zip -r backend.zip .
az webapp deployment source config-zip \
  --resource-group rg-secure-azureai-agent \
  --name app-secure-azureai-backend \
  --src backend.zip

# Deploy frontend
cd ../frontend
zip -r frontend.zip .
az webapp deployment source config-zip \
  --resource-group rg-secure-azureai-agent \
  --name app-secure-azureai-frontend \
  --src frontend.zip
```

## Option 3: GitHub Actions CI/CD

### 1. Setup GitHub Secrets

Add the following secrets to your GitHub repository:

- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_DEPLOYMENT_NAME`

### 2. GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Azure

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  AZURE_WEBAPP_BACKEND_NAME: app-secure-azureai-backend
  AZURE_WEBAPP_FRONTEND_NAME: app-secure-azureai-frontend
  PYTHON_VERSION: '3.9'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Azure Login
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Build and deploy backend
      run: |
        cd backend
        pip install -r requirements.txt
        zip -r backend.zip .
        az webapp deployment source config-zip \
          --resource-group rg-secure-azureai-agent \
          --name ${{ env.AZURE_WEBAPP_BACKEND_NAME }} \
          --src backend.zip
    
    - name: Build and deploy frontend
      run: |
        cd frontend
        pip install -r requirements.txt
        zip -r frontend.zip .
        az webapp deployment source config-zip \
          --resource-group rg-secure-azureai-agent \
          --name ${{ env.AZURE_WEBAPP_FRONTEND_NAME }} \
          --src frontend.zip
    
    - name: Configure app settings
      run: |
        az webapp config appsettings set \
          --resource-group rg-secure-azureai-agent \
          --name ${{ env.AZURE_WEBAPP_BACKEND_NAME }} \
          --settings \
            AZURE_OPENAI_ENDPOINT="${{ secrets.AZURE_OPENAI_ENDPOINT }}" \
            AZURE_OPENAI_API_KEY="${{ secrets.AZURE_OPENAI_API_KEY }}" \
            AZURE_OPENAI_DEPLOYMENT_NAME="${{ secrets.AZURE_OPENAI_DEPLOYMENT_NAME }}"
```

## Option 4: Docker Deployment

### 1. Build Docker Images

#### Backend Dockerfile
```dockerfile
# backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile
```dockerfile
# frontend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8001"]
```

### 2. Build and Push Images

```bash
# Build images
docker build -t secure-azureai-backend ./backend
docker build -t secure-azureai-frontend ./frontend

# Tag for Azure Container Registry
docker tag secure-azureai-backend myregistry.azurecr.io/secure-azureai-backend:latest
docker tag secure-azureai-frontend myregistry.azurecr.io/secure-azureai-frontend:latest

# Push to registry
docker push myregistry.azurecr.io/secure-azureai-backend:latest
docker push myregistry.azurecr.io/secure-azureai-frontend:latest
```

### 3. Deploy to Azure Container Instances

```bash
az container create \
  --resource-group rg-secure-azureai-agent \
  --name aci-secure-azureai-backend \
  --image myregistry.azurecr.io/secure-azureai-backend:latest \
  --cpu 1 \
  --memory 2 \
  --ports 8000 \
  --environment-variables \
    AZURE_OPENAI_ENDPOINT="https://your-openai-resource.openai.azure.com/" \
    AZURE_OPENAI_API_KEY="your-openai-api-key" \
    AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4"
```

## Environment-Specific Configurations

### Development Environment

```bash
# .env.development
AZURE_OPENAI_ENDPOINT=https://dev-openai-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo
USE_AZURE_AI_AGENT=false
LOG_LEVEL=DEBUG
```

### Staging Environment

```bash
# .env.staging
AZURE_OPENAI_ENDPOINT=https://staging-openai-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
USE_AZURE_AI_AGENT=true
LOG_LEVEL=INFO
```

### Production Environment

```bash
# .env.production
AZURE_OPENAI_ENDPOINT=https://prod-openai-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
USE_AZURE_AI_AGENT=true
LOG_LEVEL=WARNING
ENABLE_RATE_LIMITING=true
```

## Post-Deployment Verification

### 1. Health Checks

```bash
# Check backend health
curl https://your-backend-url.azurewebsites.net/health

# Check frontend accessibility
curl https://your-frontend-url.azurewebsites.net/
```

### 2. Functional Testing

```bash
# Test chat endpoint
curl -X POST https://your-backend-url.azurewebsites.net/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, can you help me with Azure?"}'
```

### 3. Monitoring Setup

```bash
# View application logs
az webapp log tail --resource-group rg-secure-azureai-agent --name app-secure-azureai-backend

# Check Application Insights metrics
az monitor metrics list --resource app-secure-azureai-backend --metric-names Requests
```

## Troubleshooting Deployment Issues

### Common Problems

1. **Authentication Errors**
   - Verify Azure credentials and permissions
   - Check service principal roles

2. **Resource Creation Failures**
   - Verify subscription quotas and limits
   - Check resource naming conventions

3. **Application Startup Issues**
   - Review application logs
   - Verify environment variable configuration

4. **Network Connectivity**
   - Check firewall and network security group rules
   - Verify DNS resolution

### Debug Commands

```bash
# Check deployment status
azd show

# View detailed logs
azd logs

# Check resource status
az resource list --resource-group rg-secure-azureai-agent

# Test connectivity
az webapp browse --resource-group rg-secure-azureai-agent --name app-secure-azureai-backend
```

## Security Considerations

### 1. Network Security

- Configure virtual networks for isolation
- Use private endpoints for sensitive resources
- Implement web application firewall (WAF)

### 2. Identity and Access Management

- Use managed identities for service-to-service authentication
- Implement role-based access control (RBAC)
- Regular security audits and reviews

### 3. Data Protection

- Enable encryption at rest and in transit
- Configure Key Vault for secret management
- Implement data loss prevention policies

## Maintenance and Updates

### 1. Regular Updates

```bash
# Update application
azd deploy

# Update environment variables
azd env set VARIABLE_NAME "new-value"
azd deploy
```

### 2. Monitoring and Alerts

- Set up Application Insights alerts
- Monitor resource utilization
- Track application performance metrics

### 3. Backup and Recovery

- Regular backup of configuration
- Document recovery procedures
- Test disaster recovery scenarios
