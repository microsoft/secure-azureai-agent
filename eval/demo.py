#!/usr/bin/env python3
"""
Example script demonstrating Azure AI Search RAG evaluation.
Run this script to see the evaluation system in action.
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from config import AzureConfig, EvaluationConfig, setup_logging, validate_environment
from azure_rag import AzureSearchRAGSystem
from rag_evaluation import RAGEvaluationSystem
from sample_data import get_sample_dataset, create_test_scenarios, validate_test_results

async def demo_basic_rag():
    """Demonstrate basic RAG functionality."""
    print("\n=== Basic RAG Demo ===")
    
    try:
        # Initialize system
        config = AzureConfig.from_environment()
        rag_system = AzureSearchRAGSystem(config)
        
        # Health check
        health = rag_system.health_check()
        print(f"System Health: {health['overall']}")
        
        if health['overall'] != 'healthy':
            print("⚠️  System health check failed. Some features may not work properly.")
            return
        
        # Demo single query
        query = "What is Azure AI Search?"
        print(f"\nQuery: {query}")
        
        response = await rag_system.process_rag_query(
            query=query,
            top_k=3,
            search_type="hybrid"
        )
        
        print(f"\nAnswer: {response.answer}")
        print(f"Number of contexts: {len(response.contexts)}")
        print(f"Search results: {len(response.search_results)}")
        
        # Show first context
        if response.contexts:
            print(f"\nFirst context: {response.contexts[0][:200]}...")
        
        return response
        
    except Exception as e:
        print(f"❌ Basic RAG demo failed: {e}")
        return None

async def demo_evaluation():
    """Demonstrate RAG evaluation with RAGAS."""
    print("\n=== RAG Evaluation Demo ===")
    
    try:
        # Initialize systems
        azure_config = AzureConfig.from_environment()
        eval_config = EvaluationConfig.from_environment()
        
        rag_system = AzureSearchRAGSystem(azure_config)
        evaluator = RAGEvaluationSystem(rag_system, eval_config)
        
        # Get sample data
        queries, ground_truths, _ = get_sample_dataset(domain="technology", size=3)
        
        print(f"Evaluating {len(queries)} sample queries...")
        print("Queries:")
        for i, query in enumerate(queries, 1):
            print(f"  {i}. {query}")
        
        # Run evaluation
        results, summary = await evaluator.full_evaluation(
            queries=queries,
            ground_truths=[gt for gt in ground_truths if gt is not None],
            output_file=f"demo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            top_k=5,
            search_type="hybrid"
        )
        
        # Display results
        print(f"\n📊 Evaluation Results:")
        print(f"Total queries evaluated: {summary.total_queries}")
        
        if summary.avg_faithfulness:
            print(f"Average Faithfulness: {summary.avg_faithfulness:.3f}")
        if summary.avg_answer_relevancy:
            print(f"Average Answer Relevancy: {summary.avg_answer_relevancy:.3f}")
        if summary.avg_context_precision:
            print(f"Average Context Precision: {summary.avg_context_precision:.3f}")
        if summary.avg_context_recall:
            print(f"Average Context Recall: {summary.avg_context_recall:.3f}")
        
        # Show individual results
        print(f"\n📝 Individual Results:")
        for i, result in enumerate(results[:2], 1):  # Show first 2 results
            print(f"\nQuery {i}: {result.query[:60]}...")
            print(f"Answer: {result.answer[:100]}...")
            if result.faithfulness_score:
                print(f"Faithfulness: {result.faithfulness_score:.3f}")
            if result.answer_relevancy_score:
                print(f"Answer Relevancy: {result.answer_relevancy_score:.3f}")
        
        return results, summary
        
    except Exception as e:
        print(f"❌ Evaluation demo failed: {e}")
        return None, None

async def demo_test_scenarios():
    """Demonstrate different test scenarios."""
    print("\n=== Test Scenarios Demo ===")
    
    try:
        # Initialize systems
        azure_config = AzureConfig.from_environment()
        eval_config = EvaluationConfig.from_environment()
        
        rag_system = AzureSearchRAGSystem(azure_config)
        evaluator = RAGEvaluationSystem(rag_system, eval_config)
        
        # Get test scenarios
        scenarios = create_test_scenarios()
        
        # Run a simple scenario
        scenario_name = "basic_accuracy"
        scenario = scenarios[scenario_name]
        
        print(f"Running scenario: {scenario_name}")
        print(f"Description: {scenario['description']}")
        print(f"Queries: {len(scenario['queries'])}")
        
        # Run evaluation for this scenario
        results, summary = await evaluator.full_evaluation(
            queries=scenario['queries'],
            output_file=f"scenario_{scenario_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        # Validate results
        validation = validate_test_results(
            results=summary,
            scenario_name=scenario_name,
            expected_metrics=scenario['expected_metrics']
        )
        
        print(f"\n✅ Scenario Validation:")
        print(f"Scenario: {validation['scenario']}")
        print(f"Overall passed: {validation['passed']}")
        
        if validation['failures']:
            print(f"Failures:")
            for failure in validation['failures']:
                print(f"  ❌ {failure}")
        
        if validation['summary']:
            print(f"Metric summary:")
            for metric, details in validation['summary'].items():
                status = "✅" if details['passed'] else "❌"
                print(f"  {status} {metric}: {details['actual']:.3f} (expected >= {details['expected']})")
        
        return validation
        
    except Exception as e:
        print(f"❌ Test scenarios demo failed: {e}")
        return None

async def demo_batch_processing():
    """Demonstrate batch processing capabilities."""
    print("\n=== Batch Processing Demo ===")
    
    try:
        # Initialize system
        config = AzureConfig.from_environment()
        rag_system = AzureSearchRAGSystem(config)
        
        # Get multiple queries
        queries, _, _ = get_sample_dataset(domain="general", size=5)
        
        print(f"Processing {len(queries)} queries in batch...")
        
        # Process in batch
        responses = await rag_system.batch_process_queries(
            queries=queries,
            batch_size=3,
            top_k=3
        )
        
        print(f"✅ Successfully processed {len(responses)} queries")
        
        # Show summary
        successful = sum(1 for r in responses if "error" not in r.metadata)
        failed = len(responses) - successful
        
        print(f"Successful: {successful}, Failed: {failed}")
        
        if successful > 0:
            avg_contexts = sum(len(r.contexts) for r in responses if "error" not in r.metadata) / successful
            print(f"Average contexts per response: {avg_contexts:.1f}")
        
        return responses
        
    except Exception as e:
        print(f"❌ Batch processing demo failed: {e}")
        return None

def print_environment_info():
    """Print information about the environment setup."""
    print("=== Environment Information ===")
    
    # Check if environment is configured
    env_status = validate_environment()
    print(f"Environment configured: {'✅ Yes' if env_status else '❌ No'}")
    
    # Check required environment variables
    required_vars = [
        "AZURE_SEARCH_ENDPOINT",
        "AZURE_SEARCH_INDEX_NAME",
        "AZURE_OPENAI_ENDPOINT", 
        "AZURE_OPENAI_DEPLOYMENT_NAME"
    ]
    
    print("\nEnvironment Variables:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive information
            if "endpoint" in var.lower():
                masked_value = value[:30] + "..." if len(value) > 30 else value
                print(f"  ✅ {var}: {masked_value}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: Not set")
    
    # Check optional variables
    optional_vars = ["USE_MANAGED_IDENTITY"]
    print("\nOptional Variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {value}")
        else:
            print(f"  ⚪ {var}: Not set (using default)")

async def main():
    """Main demo function."""
    print("🚀 Azure AI Search RAG Evaluation Demo")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    
    # Print environment info
    print_environment_info()
    
    # Check if environment is properly configured
    if not validate_environment():
        print("\n❌ Environment not properly configured.")
        print("Please check the README and set up your environment variables.")
        print("Copy .env.example to .env and fill in your Azure service details.")
        return
    
    try:
        # Run demos
        print("\n" + "="*50)
        await demo_basic_rag()
        
        print("\n" + "="*50) 
        await demo_batch_processing()
        
        print("\n" + "="*50)
        await demo_evaluation()
        
        print("\n" + "="*50)
        await demo_test_scenarios()
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"Check the generated files for detailed results.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())