# Azure AI Search RAG Evaluation System

This module provides a comprehensive evaluation system for RAG (Retrieval Augmented Generation) systems built with Azure AI Search and Azure OpenAI, using the RAGAS evaluation framework.

## Sample Data

The project includes sample data for demonstrating and testing the RAG system:

- **ContosoTelecom社内資料.pdf**: A fictional Japanese corporate document containing:
  - Product and service information for Contoso Telecom
  - Technical support procedures and troubleshooting guides  
  - Internal policies and procedures
  - Sample content designed for RAG search and Q&A testing

This sample document is located at the project root and serves as test data for evaluating:
- Document indexing and chunking strategies
- Semantic search accuracy
- Japanese language processing capabilities
- Q&A generation and evaluation

## Features

- **Secure Authentication**: Uses Azure Managed Identity for credential management
- **Environment Configuration**: Uses .env files for secure configuration management
- **Comprehensive Evaluation**: Implements multiple RAGAS metrics (Faithfulness, Answer Relevancy, Context Precision, etc.)
- **Azure Integration**: Built specifically for Azure AI Search and Azure OpenAI services
- **Batch Processing**: Efficient evaluation of multiple queries
- **Results Export**: JSON and CSV export with comparison capabilities
- **OSS Security**: Environment variable-based configuration with no hardcoded secrets

## Architecture

### Core Components

1. **`config.py`**: Secure configuration management with environment variables
2. **`azure_rag.py`**: Azure AI Search RAG system implementation
3. **`rag_evaluation.py`**: RAGAS-based evaluation system

### Security Features

- Environment variable-based configuration via .env files
- Azure Managed Identity authentication
- No hardcoded credentials or API keys
- Comprehensive logging and error handling
- Secure credential management for OSS projects

## Setup

### Prerequisites

- Azure AI Search service with configured index
- Azure OpenAI service with deployed models  
- Python 3.8+ with pip
- Appropriate Azure RBAC permissions

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables using .env file:
```bash
cp .env.example .env
# Edit .env with your Azure service endpoints and configuration
```

### Required Environment Variables

```bash
# Azure Services
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_INDEX_NAME=your-index-name
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=your-gpt-deployment

# Optional
USE_MANAGED_IDENTITY=true
```

## Usage

### Basic RAG System Usage

```python
import asyncio
from config import AzureConfig, setup_logging
from azure_rag import AzureSearchRAGSystem

# Setup
setup_logging()
config = AzureConfig.from_environment()
rag_system = AzureSearchRAGSystem(config)

# Single query
async def example_query():
    response = await rag_system.process_rag_query(
        query="What is Azure AI Search?",
        top_k=5,
        search_type="hybrid"
    )
    print(f"Answer: {response.answer}")
    print(f"Contexts: {len(response.contexts)} documents")

asyncio.run(example_query())
```

### RAG Evaluation

```python
import asyncio
from config import AzureConfig, EvaluationConfig, setup_logging
from azure_rag import AzureSearchRAGSystem
from rag_evaluation import RAGEvaluationSystem

async def evaluate_rag():
    # Setup
    setup_logging()
    azure_config = AzureConfig.from_environment()
    eval_config = EvaluationConfig.from_environment()
    
    # Initialize systems
    rag_system = AzureSearchRAGSystem(azure_config)
    evaluator = RAGEvaluationSystem(rag_system, eval_config)
    
    # Evaluation queries
    queries = [
        "What is Azure AI Search?",
        "How does vector search work?",
        "What are the benefits of RAG systems?"
    ]
    
    # Optional ground truth answers
    ground_truths = [
        "Azure AI Search is a cloud search service...",
        "Vector search uses embeddings to find...",
        "RAG systems provide accurate, contextual..."
    ]
    
    # Run evaluation
    results, summary = await evaluator.full_evaluation(
        queries=queries,
        ground_truths=ground_truths,
        output_file="evaluation_results.json"
    )
    
    # Print summary
    print(f"Evaluation Summary:")
    print(f"Total queries: {summary.total_queries}")
    print(f"Avg Faithfulness: {summary.avg_faithfulness:.3f}")
    print(f"Avg Answer Relevancy: {summary.avg_answer_relevancy:.3f}")
    print(f"Avg Context Precision: {summary.avg_context_precision:.3f}")

asyncio.run(evaluate_rag())
```

### Using Sample Data for Evaluation

```python
import asyncio
from config import AzureConfig, EvaluationConfig, setup_logging
from azure_rag import AzureSearchRAGSystem
from rag_evaluation import RAGEvaluationSystem

async def evaluate_contoso_data():
    # Setup
    setup_logging()
    azure_config = AzureConfig.from_environment()
    eval_config = EvaluationConfig.from_environment()
    
    # Initialize systems
    rag_system = AzureSearchRAGSystem(azure_config)
    evaluator = RAGEvaluationSystem(rag_system, eval_config)
    
    # Sample queries based on ContosoTelecom sample data
    queries = [
        "ContosoTelecomのサポート体制について教えてください",
        "技術的な問題が発生した場合の対処手順は？",
        "製品保証ポリシーの詳細を教えてください",
        "新規顧客向けのサービス紹介をお願いします"
    ]
    
    # Run evaluation with Japanese sample data
    results, summary = await evaluator.full_evaluation(
        queries=queries,
        output_file="contoso_evaluation_results.json",
        top_k=5,
        search_type="hybrid"
    )
    
    # Print results
    print(f"ContosoTelecom Data Evaluation Summary:")
    print(f"Total queries: {summary.total_queries}")
    print(f"Avg Faithfulness: {summary.avg_faithfulness:.3f}")
    print(f"Avg Answer Relevancy: {summary.avg_answer_relevancy:.3f}")

asyncio.run(evaluate_contoso_data())
```

### Batch Evaluation

```python
# Load queries from file
with open('evaluation_queries.txt', 'r') as f:
    queries = [line.strip() for line in f]

# Run batch evaluation with custom parameters
results, summary = await evaluator.full_evaluation(
    queries=queries,
    output_file=f"evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
    top_k=10,
    search_type="semantic",
    temperature=0.0
)
```

## Evaluation Metrics

The system supports the following RAGAS metrics:

### Faithfulness
Measures how factually accurate the generated answer is based on the given context. Scores range from 0 to 1, where 1 indicates perfect faithfulness.

### Answer Relevancy  
Evaluates how relevant the generated answer is to the given question. Higher scores indicate better relevance.

### Context Precision
Measures whether all the retrieved contexts are relevant to the query. Higher precision means fewer irrelevant contexts.

### Context Recall
Evaluates whether the retrieved context contains all the necessary information to answer the query.

### Context Relevancy
Assesses the relevance of the retrieved context to the query.

## Configuration Options

### Azure Configuration
- `search_endpoint`: Azure AI Search service endpoint
- `search_index_name`: Name of the search index
- `openai_endpoint`: Azure OpenAI service endpoint  
- `openai_deployment_name`: Name of the GPT deployment
- `use_managed_identity`: Use managed identity authentication

### Evaluation Configuration
- `enable_*`: Enable/disable specific metrics
- `max_context_length`: Maximum context length for evaluation
- `batch_size`: Number of queries to process in parallel
- `evaluation_model`: Model to use for evaluation

## Output Format

Results are saved in both JSON and CSV formats:

### JSON Structure
```json
{
  "summary": {
    "total_queries": 100,
    "avg_faithfulness": 0.85,
    "avg_answer_relevancy": 0.92,
    "evaluation_timestamp": "2024-01-15T10:30:00"
  },
  "detailed_results": [
    {
      "query": "What is Azure AI Search?",
      "answer": "Azure AI Search is a cloud service...",
      "contexts": ["...", "..."],
      "faithfulness_score": 0.88,
      "answer_relevancy_score": 0.95
    }
  ]
}
```

## Security Considerations

- **No Hardcoded Secrets**: All credentials are managed through .env files and Azure services
- **Managed Identity**: Preferred authentication method for Azure-hosted applications
- **Environment Files**: Secure configuration using .env files (excluded from git)
- **Least Privilege**: Configure minimal required permissions for Azure services
- **Logging**: Comprehensive logging without exposing sensitive information

## Performance Optimization

- **Batch Processing**: Concurrent evaluation of multiple queries
- **Connection Pooling**: Efficient Azure service client management
- **Async Operations**: Non-blocking I/O operations
- **Error Handling**: Robust retry logic with exponential backoff

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Ensure Azure credentials are properly configured
   - Check Azure RBAC permissions
   - Verify managed identity is enabled if used

2. **Search Service Issues**
   - Confirm search endpoint and index name
   - Verify search index has required fields
   - Check search service availability

3. **OpenAI Service Issues**
   - Confirm deployment name and endpoint
   - Check model deployment status
   - Verify API version compatibility

4. **RAGAS Import Errors**
   - Install RAGAS: `pip install ragas`
   - Check Python version compatibility
   - Verify all dependencies are installed

### Logging

Enable detailed logging by setting `LOG_LEVEL=DEBUG` in your environment:

```python
from config import setup_logging
setup_logging(level="DEBUG")
```

## Contributing

This evaluation system follows Azure security best practices and is designed for OSS projects. When contributing:

- Never commit secrets or credentials
- Use environment variables for configuration
- Follow Azure SDK best practices
- Include comprehensive error handling
- Add appropriate logging

## License

This project is licensed under the MIT License - see the LICENSE file for details.