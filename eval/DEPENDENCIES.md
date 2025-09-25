# Dependencies Installation Guide

This guide explains how to install the required dependencies for the Azure AI Search RAG evaluation system.

## Core Requirements

The system requires several Azure SDKs and evaluation libraries. Install them step by step:

### 1. Basic Requirements

```bash
# Essential Python packages
pip install python-dotenv pandas numpy

# Azure Identity (always required)
pip install azure-identity
```

### 2. Azure AI Search

```bash
# Azure AI Search SDK
pip install azure-search-documents
```

### 3. Azure OpenAI

```bash
# OpenAI SDK with Azure support
pip install openai
```

### 4. RAG Evaluation with RAGAS

```bash
# RAGAS evaluation framework
pip install ragas

# Additional dependencies for RAGAS
pip install datasets
```

### 5. Optional Dependencies

```bash
# For async operations
pip install aiohttp asyncio-throttle

# For structured logging
pip install structlog

# For development and testing
pip install pytest pytest-asyncio pytest-cov

# For Jupyter notebooks
pip install jupyter ipywidgets matplotlib seaborn

# For code formatting (development)
pip install black isort mypy
```

## Installation Options

### Option 1: Install All at Once

```bash
pip install -r requirements.txt
```

### Option 2: Minimal Installation

If you only need basic functionality:

```bash
pip install python-dotenv azure-identity azure-search-documents openai ragas datasets pandas numpy
```

### Option 3: Development Installation

For development with all tools:

```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio black isort mypy
```

## Environment Setup

After installing dependencies:

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` with your Azure service details:
```bash
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_INDEX_NAME=your-index-name
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=your-gpt-deployment
```

## Testing Installation

Verify your installation:

```bash
python test_system.py
```

## Troubleshooting

### Common Issues

1. **Azure SDK Import Errors**
   ```
   ModuleNotFoundError: No module named 'azure.search'
   ```
   **Solution**: Install azure-search-documents
   ```bash
   pip install azure-search-documents
   ```

2. **RAGAS Import Errors**
   ```
   ModuleNotFoundError: No module named 'ragas'
   ```
   **Solution**: Install RAGAS and dependencies
   ```bash
   pip install ragas datasets
   ```

3. **OpenAI Import Errors**
   ```
   ModuleNotFoundError: No module named 'openai'
   ```
   **Solution**: Install OpenAI SDK
   ```bash
   pip install openai
   ```

### Version Compatibility

- Python 3.8+ required
- Azure SDKs require recent versions for best compatibility
- RAGAS requires datasets library

### Virtual Environment

Recommended to use a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Minimal Working Example

Test with minimal dependencies:

```python
# test_minimal.py
import os
os.environ['AZURE_SEARCH_ENDPOINT'] = 'https://dummy.search.windows.net'
os.environ['AZURE_SEARCH_INDEX_NAME'] = 'dummy'
os.environ['AZURE_OPENAI_ENDPOINT'] = 'https://dummy.openai.azure.com'
os.environ['AZURE_OPENAI_DEPLOYMENT_NAME'] = 'dummy'

from config import AzureConfig, EvaluationConfig

# This should work with basic dependencies
config = AzureConfig.from_environment()
eval_config = EvaluationConfig.from_environment()

print("✅ Configuration loading successful")
```

## Next Steps

After successful installation:

1. Configure your `.env` file with real Azure endpoints
2. Run the test suite: `python test_system.py`
3. Try the demo: `python demo.py`
4. Read the main README for usage examples