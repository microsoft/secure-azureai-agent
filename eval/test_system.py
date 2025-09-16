"""
Simple test runner for the RAG evaluation system.
Run basic tests to verify the system works correctly.
"""

import unittest
import asyncio
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from config import AzureConfig, EvaluationConfig
from sample_data import get_sample_dataset, create_test_scenarios

class TestRAGEvaluationSystem(unittest.TestCase):
    """Test cases for the RAG evaluation system."""
    
    def test_config_loading(self):
        """Test configuration loading."""
        # Test that config can be created (even if not all env vars are set)
        try:
            # This should work even with missing env vars
            required_vars = [
                "AZURE_SEARCH_ENDPOINT",
                "AZURE_SEARCH_INDEX_NAME",
                "AZURE_OPENAI_ENDPOINT", 
                "AZURE_OPENAI_DEPLOYMENT_NAME"
            ]
            
            # Set dummy values for testing
            for var in required_vars:
                if not os.getenv(var):
                    os.environ[var] = f"https://dummy-{var.lower()}.example.com"
            
            config = AzureConfig.from_environment()
            self.assertIsNotNone(config.search_endpoint)
            self.assertIsNotNone(config.openai_endpoint)
            
        except Exception as e:
            self.fail(f"Config loading failed: {e}")
    
    def test_evaluation_config(self):
        """Test evaluation configuration."""
        eval_config = EvaluationConfig.from_environment()
        
        self.assertTrue(eval_config.enable_faithfulness)
        self.assertTrue(eval_config.enable_answer_relevancy)
        self.assertGreater(eval_config.max_context_length, 0)
        self.assertGreater(eval_config.batch_size, 0)
    
    def test_sample_data_loading(self):
        """Test sample data generation."""
        # Test different domains
        domains = ["technology", "general", "business"]
        
        for domain in domains:
            queries, ground_truths, contexts = get_sample_dataset(domain=domain, size=3)
            
            self.assertEqual(len(queries), 3)
            self.assertEqual(len(ground_truths), 3)
            self.assertEqual(len(contexts), 3)
            
            # Check that queries are strings
            for query in queries:
                self.assertIsInstance(query, str)
                self.assertGreater(len(query), 0)
            
            # Check that contexts are lists
            for context_list in contexts:
                self.assertIsInstance(context_list, list)
                self.assertGreater(len(context_list), 0)
    
    def test_invalid_domain(self):
        """Test handling of invalid domain."""
        with self.assertRaises(ValueError):
            get_sample_dataset(domain="invalid_domain", size=5)
    
    def test_test_scenarios(self):
        """Test test scenario creation."""
        scenarios = create_test_scenarios()
        
        self.assertIsInstance(scenarios, dict)
        self.assertGreater(len(scenarios), 0)
        
        # Check that each scenario has required fields
        for name, scenario in scenarios.items():
            self.assertIn("description", scenario)
            self.assertIn("queries", scenario)
            self.assertIn("expected_metrics", scenario)
            
            self.assertIsInstance(scenario["queries"], list)
            self.assertGreater(len(scenario["queries"]), 0)
            
            self.assertIsInstance(scenario["expected_metrics"], dict)
    
    def test_environment_validation(self):
        """Test environment validation functionality."""
        from config import validate_environment
        
        # Save current environment
        original_env = {}
        required_vars = [
            "AZURE_SEARCH_ENDPOINT",
            "AZURE_SEARCH_INDEX_NAME",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_DEPLOYMENT_NAME"
        ]
        
        for var in required_vars:
            original_env[var] = os.environ.get(var)
            os.environ[var] = f"https://test-{var.lower()}.example.com"
        
        try:
            # Should pass with dummy values
            result = validate_environment()
            self.assertIsInstance(result, bool)
            
        finally:
            # Restore original environment
            for var, value in original_env.items():
                if value is None:
                    os.environ.pop(var, None)
                else:
                    os.environ[var] = value

class TestAsyncFunctions(unittest.IsolatedAsyncioTestCase):
    """Test async functions."""
    
    async def test_mock_rag_response(self):
        """Test that we can create mock RAG responses."""
        try:
            from azure_rag import RAGResponse, SearchResult
        except ImportError as e:
            self.skipTest(f"Azure SDK not available: {e}")
        
        # Create a mock response
        mock_response = RAGResponse(
            query="Test query",
            answer="Test answer", 
            contexts=["Context 1", "Context 2"],
            search_results=[
                SearchResult(
                    content="Test content",
                    score=0.8,
                    metadata={"id": "test1"}
                )
            ],
            metadata={"test": True}
        )
        
        self.assertEqual(mock_response.query, "Test query")
        self.assertEqual(mock_response.answer, "Test answer")
        self.assertEqual(len(mock_response.contexts), 2)
        self.assertEqual(len(mock_response.search_results), 1)

def run_tests():
    """Run all tests."""
    print("Running RAG Evaluation System Tests...")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestRAGEvaluationSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestAsyncFunctions))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
        return True
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback}")
        
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)