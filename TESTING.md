# Testing Guide

This document outlines the testing strategy and procedures for the Secure Azure AI Agent project.

## Testing Overview

The project includes multiple types of testing to ensure reliability, security, and performance:

1. **Unit Tests**: Core functionality testing
2. **Integration Tests**: API and agent interaction testing
3. **Red Team Testing**: Security and safety evaluation
4. **Performance Tests**: Load and response time testing
5. **End-to-End Tests**: Full user workflow testing

## Test Structure

```
eval/
├── readteaming_test.ipynb    # Red team security testing
├── rag_evaluation.py         # RAG system evaluation
├── azure_rag.py             # RAG implementation testing
├── sample_data.py           # Sample data generation
├── ContosoTelecom社内資料.pdf # Sample test data
├── requirements.txt          # Testing dependencies
└── test_reports/            # Generated test reports
```

## Unit Testing

### Backend Tests

Test the core agent functionality:

```python
import pytest
from backend.src.agents.azure_troubleshoot_agent import AzureTroubleshootAgent

@pytest.mark.asyncio
async def test_agent_initialization():
    agent = AzureTroubleshootAgent()
    await agent.initialize()
    assert agent.ai_service is not None

@pytest.mark.asyncio
async def test_message_processing():
    agent = AzureTroubleshootAgent()
    await agent.initialize()
    
    response = await agent.process_message(
        "Help me with Azure App Service deployment issues",
        session_id="test-session"
    )
    
    assert response is not None
    assert len(response) > 0
```

### Frontend Tests

Test the Chainlit interface components:

```python
import pytest
from frontend.app import BackendAPIClient

@pytest.mark.asyncio
async def test_backend_api_client():
    client = BackendAPIClient()
    
    # Test health endpoint
    response = await client.health_check()
    assert response["status"] == "healthy"
```

## Red Team Testing

The project includes red team testing for AI safety and security evaluation using Azure AI Foundry's red teaming capabilities.

### Setup Red Team Testing

1. **Configure environment**:
   ```bash
   cd eval
   pip install -r requirements.txt
   ```

2. **Set up Azure AI project**:
   ```bash
   export PROJECT_ENDPOINT=https://your-account.services.ai.azure.com/api/projects/your-project
   ```

3. **Run red team tests**:
   ```bash
   jupyter notebook readteaming_test.ipynb
   ```

### Red Team Test Categories

The red team testing covers:

- **Harmful Content**: Attempts to generate inappropriate content
- **Bias and Fairness**: Testing for biased responses
- **Privacy**: Testing for data exposure
- **Security**: Testing for system vulnerabilities
- **Misinformation**: Testing for factual accuracy

### Example Red Team Test

```python
from azure.ai.evaluation.red_team import RedTeam, RiskCategory

# Initialize red team agent
red_team_agent = RedTeam(
    azure_ai_project=azure_ai_project,
    credential=DefaultAzureCredential()
)

# Define target application
async def target_application(query: str) -> str:
    # Your application logic here
    response = await agent.process_message(query)
    return response

# Run red team scan
red_team_result = await red_team_agent.scan(
    target=target_application,
    risk_categories=[RiskCategory.HARMFUL_CONTENT, RiskCategory.BIAS]
)
```

## RAG System Testing

### RAG Evaluation with Sample Data

The project includes comprehensive RAG testing using the `ContosoTelecom社内資料.pdf` sample document:

```python
import asyncio
from eval.config import AzureConfig, EvaluationConfig, setup_logging
from eval.azure_rag import AzureSearchRAGSystem
from eval.rag_evaluation import RAGEvaluationSystem

@pytest.mark.asyncio
async def test_rag_evaluation():
    # Setup
    setup_logging()
    azure_config = AzureConfig.from_environment()
    eval_config = EvaluationConfig.from_environment()
    
    # Initialize systems
    rag_system = AzureSearchRAGSystem(azure_config)
    evaluator = RAGEvaluationSystem(rag_system, eval_config)
    
    # Test queries based on sample data
    test_queries = [
        "ContosoTelecomのサービス内容について教えてください",
        "技術サポートの連絡方法は？",
        "製品の保証期間はどのくらいですか？"
    ]
    
    # Run evaluation
    results, summary = await evaluator.full_evaluation(
        queries=test_queries,
        output_file="test_rag_results.json"
    )
    
    # Assertions
    assert summary.total_queries == len(test_queries)
    assert summary.avg_faithfulness > 0.7  # Minimum faithfulness threshold
    assert summary.avg_answer_relevancy > 0.8  # Minimum relevancy threshold

# Run RAG performance test
async def test_rag_performance():
    rag_system = AzureSearchRAGSystem(AzureConfig.from_environment())
    
    start_time = time.time()
    response = await rag_system.process_rag_query(
        query="ContosoTelecomの製品について教えてください",
        top_k=5
    )
    end_time = time.time()
    
    # Performance assertions
    assert (end_time - start_time) < 5.0  # Response under 5 seconds
    assert len(response.contexts) > 0     # Retrieved contexts
    assert len(response.answer) > 50      # Substantial answer
```

## Integration Testing

### API Testing

Test the REST API endpoints:

```python
import httpx
import pytest

@pytest.mark.asyncio
async def test_chat_endpoint():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/chat",
            json={
                "message": "Test message",
                "session_id": "test-session"
            }
        )
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_health_endpoint():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
```

### Agent Integration Testing

Test agent routing and responses:

```python
@pytest.mark.asyncio
async def test_agent_routing():
    agent = AzureTroubleshootAgent()
    await agent.initialize()
    
    # Test different types of queries
    queries = [
        "Help with Azure App Service",
        "Database connection issues",
        "AI Foundry deployment problems"
    ]
    
    for query in queries:
        response = await agent.process_message(query)
        assert response is not None
        assert len(response) > 10  # Meaningful response
```

## Performance Testing

### Load Testing

Test system performance under load:

```python
import asyncio
import time

async def load_test(concurrent_requests=10, total_requests=100):
    """Simulate concurrent user requests"""
    
    async def single_request():
        async with httpx.AsyncClient() as client:
            start_time = time.time()
            response = await client.post(
                "http://localhost:8000/chat",
                json={"message": "Test load message"}
            )
            end_time = time.time()
            return {
                "status_code": response.status_code,
                "response_time": end_time - start_time
            }
    
    # Run concurrent requests
    tasks = []
    for _ in range(total_requests):
        task = single_request()
        tasks.append(task)
        
        if len(tasks) >= concurrent_requests:
            results = await asyncio.gather(*tasks)
            tasks = []
            
            # Analyze results
            avg_response_time = sum(r["response_time"] for r in results) / len(results)
            success_rate = sum(1 for r in results if r["status_code"] == 200) / len(results)
            
            print(f"Average response time: {avg_response_time:.2f}s")
            print(f"Success rate: {success_rate:.2%}")
```

## Running Tests

### Local Testing

1. **Install test dependencies**:
   ```bash
   pip install pytest pytest-asyncio httpx jupyter
   ```

2. **Run unit tests**:
   ```bash
   pytest tests/ -v
   ```

3. **Run integration tests**:
   ```bash
   # Start the application first
   python -m uvicorn backend.src.main:app --reload &
   
   # Run tests
   pytest tests/integration/ -v
   ```

### Continuous Integration

The project should include CI/CD pipeline testing:

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    
    - name: Install dependencies
      run: |
        pip install -r backend/requirements.txt
        pip install pytest pytest-asyncio
    
    - name: Run tests
      run: pytest tests/ -v
    
    - name: Run red team tests
      run: |
        cd eval
        pip install -r requirements.txt
        # Run red team testing
```

## Test Coverage

Aim for high test coverage across:

- **Agent Logic**: 90%+ coverage
- **API Endpoints**: 100% coverage
- **Error Handling**: 90%+ coverage
- **Security Functions**: 100% coverage

### Measuring Coverage

```bash
pip install pytest-cov
pytest --cov=backend/src tests/ --cov-report=html
```

## Test Data Management

### Mock Data

Use consistent test data:

```python
# test_data.py
SAMPLE_QUERIES = [
    "Help me deploy to Azure App Service",
    "My function app is not working",
    "Database connection timeout issues"
]

EXPECTED_RESPONSES = {
    "app_service": ["deployment", "configuration", "scaling"],
    "function_app": ["runtime", "triggers", "bindings"],
    "database": ["connection", "timeout", "performance"]
}
```

### Environment Setup

```bash
# Test environment variables
export AZURE_OPENAI_ENDPOINT=https://test-endpoint.openai.azure.com/
export AZURE_OPENAI_API_KEY=test-key
export AZURE_OPENAI_DEPLOYMENT_NAME=test-deployment
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Mock External Services**: Use mocks for Azure services in unit tests
3. **Test Both Success and Failure**: Cover error scenarios
4. **Performance Baselines**: Set acceptable response time thresholds
5. **Security Testing**: Regular red team evaluation
6. **Documentation**: Keep test documentation up to date

## Troubleshooting Tests

### Common Issues

1. **Authentication Failures**: Check Azure credentials and permissions
2. **Timeout Issues**: Increase timeout values for integration tests
3. **Rate Limiting**: Implement delays between test requests
4. **Resource Cleanup**: Ensure test sessions are properly cleaned up

### Debug Mode

Enable detailed test logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run tests with verbose output
pytest -v -s tests/
```
