"""
Sample data and test cases for Azure AI Search RAG evaluation.
"""

# Sample evaluation queries for different domains
SAMPLE_QUERIES = {
    "technology": [
        "What is Azure AI Search and how does it work?",
        "How do I implement semantic search in Azure AI Search?", 
        "What are the benefits of using vector embeddings in search?",
        "How does hybrid search combine keyword and semantic search?",
        "What are the pricing tiers for Azure AI Search?",
        "How do I configure indexers in Azure AI Search?",
        "What is the difference between simple and full Lucene query syntax?",
        "How does Azure AI Search handle multi-language content?",
        "What security features are available in Azure AI Search?",
        "How do I optimize search performance in Azure AI Search?"
    ],
    
    "general": [
        "What is artificial intelligence?",
        "How does machine learning work?",
        "What are the applications of natural language processing?",
        "What is the difference between AI and ML?",
        "How do neural networks function?",
        "What are large language models?",
        "How does deep learning differ from traditional ML?",
        "What is computer vision used for?",
        "How does reinforcement learning work?",
        "What are the ethical considerations in AI?"
    ],
    
    "business": [
        "How can AI improve business operations?",
        "What are the ROI benefits of implementing AI?",
        "How do companies use AI for customer service?",
        "What are AI-powered analytics tools?",
        "How does AI help in decision making?",
        "What are the challenges of AI adoption in enterprises?",
        "How can small businesses leverage AI?",
        "What is AI governance in organizations?",
        "How does AI impact workforce productivity?",
        "What are the best practices for AI implementation?"
    ]
}

# Sample ground truth answers (simplified examples)
SAMPLE_GROUND_TRUTHS = {
    "What is Azure AI Search and how does it work?": 
        "Azure AI Search is a cloud-based search-as-a-service solution that provides rich search capabilities over user content. It works by indexing content from various data sources, creating searchable indexes that support full-text search, semantic search, and vector search capabilities.",
    
    "How do I implement semantic search in Azure AI Search?":
        "To implement semantic search in Azure AI Search, you need to: 1) Enable semantic search in your search service, 2) Configure semantic configurations in your index schema, 3) Use semantic query types in your search requests, and 4) Define semantic fields for title, content, and keywords.",
    
    "What are the benefits of using vector embeddings in search?":
        "Vector embeddings in search provide benefits including: better semantic understanding, improved relevance for complex queries, multilingual search capabilities, and the ability to find conceptually similar content even when exact keywords don't match.",
        
    "What is artificial intelligence?":
        "Artificial Intelligence (AI) is a branch of computer science that aims to create machines capable of performing tasks that typically require human intelligence, such as learning, reasoning, problem-solving, perception, and language understanding.",
        
    "How can AI improve business operations?":
        "AI can improve business operations through automation of repetitive tasks, enhanced decision-making with data analytics, improved customer experiences through personalization, predictive maintenance, supply chain optimization, and fraud detection."
}

# Sample contexts for evaluation (would typically come from your indexed data)
SAMPLE_CONTEXTS = {
    "azure_search": [
        "Azure AI Search (formerly Azure Cognitive Search) is a cloud search service that gives developers infrastructure, APIs, and tools for building a rich search experience over private, heterogeneous content in web, mobile, and enterprise applications.",
        "Azure AI Search provides powerful search capabilities including full-text search, faceted navigation, geo-search, and AI-powered semantic search using natural language understanding.",
        "The service supports various data sources including Azure SQL Database, Azure Cosmos DB, Azure Blob Storage, and more through built-in indexers.",
        "Semantic search in Azure AI Search uses machine learning models to understand the meaning and context of search queries, providing more relevant results."
    ],
    
    "ai_concepts": [
        "Artificial Intelligence encompasses machine learning, deep learning, natural language processing, computer vision, and robotics to create systems that can perform human-like cognitive tasks.",
        "Machine learning is a subset of AI that enables systems to automatically learn and improve from experience without being explicitly programmed.",
        "Deep learning uses neural networks with multiple layers to model and understand complex patterns in data.",
        "Natural Language Processing (NLP) combines computational linguistics with machine learning to help computers understand human language."
    ],
    
    "business_ai": [
        "AI in business operations includes process automation, predictive analytics, customer relationship management, and supply chain optimization.",
        "Return on investment for AI initiatives typically comes from cost reduction, revenue growth, and improved operational efficiency.",
        "AI-powered customer service uses chatbots, sentiment analysis, and automated response systems to improve customer satisfaction.",
        "Business intelligence and analytics tools powered by AI can identify patterns, predict trends, and support data-driven decision making."
    ]
}

def get_sample_dataset(domain: str = "technology", size: int = 10):
    """
    Get a sample dataset for evaluation.
    
    Args:
        domain: Domain of queries ("technology", "general", "business")
        size: Number of samples to return
        
    Returns:
        Tuple of (queries, ground_truths, contexts)
    """
    if domain not in SAMPLE_QUERIES:
        raise ValueError(f"Domain {domain} not available. Choose from: {list(SAMPLE_QUERIES.keys())}")
    
    queries = SAMPLE_QUERIES[domain][:size]
    
    # Get ground truths where available
    ground_truths = []
    for query in queries:
        if query in SAMPLE_GROUND_TRUTHS:
            ground_truths.append(SAMPLE_GROUND_TRUTHS[query])
        else:
            ground_truths.append(None)  # No ground truth available
    
    # Get relevant contexts based on domain
    if domain == "technology":
        context_pool = SAMPLE_CONTEXTS["azure_search"]
    elif domain == "general":
        context_pool = SAMPLE_CONTEXTS["ai_concepts"] 
    else:  # business
        context_pool = SAMPLE_CONTEXTS["business_ai"]
    
    # For each query, provide relevant contexts (simplified - would normally come from search)
    contexts = [context_pool[:3] for _ in queries]  # Top 3 contexts per query
    
    return queries, ground_truths, contexts

def create_test_scenarios():
    """
    Create different test scenarios for comprehensive evaluation.
    
    Returns:
        Dictionary of test scenarios
    """
    scenarios = {
        "basic_accuracy": {
            "description": "Test basic RAG accuracy with clear questions",
            "queries": [
                "What is Azure AI Search?",
                "How does semantic search work?",
                "What are vector embeddings?"
            ],
            "expected_metrics": {
                "min_faithfulness": 0.7,
                "min_answer_relevancy": 0.8
            }
        },
        
        "complex_queries": {
            "description": "Test performance on complex, multi-part questions", 
            "queries": [
                "How do I implement a hybrid search system using Azure AI Search with both keyword and semantic capabilities?",
                "What are the cost implications and performance trade-offs between different Azure AI Search pricing tiers?",
                "How can I integrate Azure AI Search with my existing data pipeline for real-time document indexing?"
            ],
            "expected_metrics": {
                "min_faithfulness": 0.6,
                "min_answer_relevancy": 0.7,
                "min_context_precision": 0.6
            }
        },
        
        "edge_cases": {
            "description": "Test handling of ambiguous or unclear queries",
            "queries": [
                "What is the best search solution?",
                "How much does it cost?",
                "Is it better than other options?"
            ],
            "expected_metrics": {
                "min_faithfulness": 0.5,
                "min_answer_relevancy": 0.5
            }
        },
        
        "domain_specific": {
            "description": "Test domain-specific knowledge",
            "queries": SAMPLE_QUERIES["technology"][:5],
            "expected_metrics": {
                "min_faithfulness": 0.8,
                "min_answer_relevancy": 0.8,
                "min_context_precision": 0.7
            }
        }
    }
    
    return scenarios

def validate_test_results(results, scenario_name, expected_metrics):
    """
    Validate test results against expected metrics.
    
    Args:
        results: Evaluation results
        scenario_name: Name of the test scenario
        expected_metrics: Expected minimum metric values
        
    Returns:
        Dictionary with validation results
    """
    validation = {
        "scenario": scenario_name,
        "passed": True,
        "failures": [],
        "summary": {}
    }
    
    # Check each expected metric
    for metric, min_value in expected_metrics.items():
        if metric.startswith("min_"):
            actual_metric = metric.replace("min_", "avg_")
            
            if hasattr(results, actual_metric):
                actual_value = getattr(results, actual_metric)
                
                if actual_value is not None:
                    validation["summary"][metric] = {
                        "expected": min_value,
                        "actual": actual_value,
                        "passed": actual_value >= min_value
                    }
                    
                    if actual_value < min_value:
                        validation["passed"] = False
                        validation["failures"].append(
                            f"{metric}: expected >= {min_value}, got {actual_value:.3f}"
                        )
    
    return validation