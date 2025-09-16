"""
Azure AI Search RAG System Implementation.
Implements secure RAG pipeline with Azure AI Search and Azure OpenAI.
"""

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Azure SDK imports
try:
    from azure.search.documents import SearchClient
    from azure.search.documents.models import VectorizedQuery
    from azure.core.exceptions import HttpResponseError
    from openai import AzureOpenAI
    AZURE_SDKS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Azure SDKs not available: {e}")
    AZURE_SDKS_AVAILABLE = False
    
    # Create dummy classes for type hints when SDKs are not available
    class SearchClient:
        pass
    class VectorizedQuery:
        pass
    class HttpResponseError(Exception):
        pass
    class AzureOpenAI:
        pass

# Local imports
from config import AzureConfig

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Represents a search result from Azure AI Search."""
    content: str
    score: float
    metadata: Dict[str, Any]

@dataclass
class RAGResponse:
    """Represents a complete RAG response."""
    query: str
    answer: str
    contexts: List[str]
    search_results: List[SearchResult]
    metadata: Dict[str, Any]

class AzureSearchRAGSystem:
    """
    Azure AI Search-based RAG system with security and performance optimizations.
    """
    
    def __init__(self, config: AzureConfig):
        """
        Initialize the RAG system with Azure configuration.
        
        Args:
            config: Azure configuration containing endpoints and credentials
        """
        if not AZURE_SDKS_AVAILABLE:
            raise ImportError(
                "Azure SDKs are required for RAG system. Install with: "
                "pip install azure-search-documents openai"
            )
        
        self.config = config
        self.credential = config.get_credential()
        
        # Initialize Azure AI Search client
        self.search_client = SearchClient(
            endpoint=config.search_endpoint,
            index_name=config.search_index_name,
            credential=self.credential
        )
        
        # Initialize Azure OpenAI client
        self.openai_client = AzureOpenAI(
            azure_endpoint=config.openai_endpoint,
            azure_deployment=config.openai_deployment_name,
            api_version=config.openai_api_version,
            azure_ad_token_provider=self._get_token_provider()
        )
        
        logger.info("Azure Search RAG System initialized successfully")
    
    def _get_token_provider(self):
        """Get Azure AD token provider for OpenAI authentication."""
        def get_token():
            token = self.credential.get_token("https://cognitiveservices.azure.com/.default")
            return token.token
        return get_token
    
    async def search_documents(
        self,
        query: str,
        top_k: int = 5,
        search_type: str = "hybrid",
        vector_query: Optional[List[float]] = None
    ) -> List[SearchResult]:
        """
        Search documents in Azure AI Search index.
        
        Args:
            query: Search query text
            top_k: Number of top results to return
            search_type: Type of search (semantic, vector, hybrid)
            vector_query: Optional vector query for semantic search
            
        Returns:
            List of search results
        """
        try:
            search_params = {
                "search_text": query,
                "top": top_k,
                "include_total_count": True,
                "highlight_fields": "content",
                "select": ["content", "title", "metadata", "id"]
            }
            
            # Add vector query if provided
            if vector_query and search_type in ["vector", "hybrid"]:
                vector_queries = [VectorizedQuery(
                    vector=vector_query,
                    k_nearest_neighbors=top_k,
                    fields="content_vector"
                )]
                search_params["vector_queries"] = vector_queries
            
            # Configure semantic search if available
            if search_type in ["semantic", "hybrid"]:
                search_params.update({
                    "query_type": "semantic",
                    "semantic_configuration_name": "default",
                    "query_caption": "extractive",
                    "query_answer": "extractive"
                })
            
            # Execute search
            results = self.search_client.search(**search_params)
            
            search_results = []
            for result in results:
                search_results.append(SearchResult(
                    content=result.get("content", ""),
                    score=result.get("@search.score", 0.0),
                    metadata={
                        "id": result.get("id"),
                        "title": result.get("title", ""),
                        "highlights": result.get("@search.highlights", {}),
                        **result.get("metadata", {})
                    }
                ))
            
            logger.info(f"Found {len(search_results)} results for query: {query[:100]}")
            return search_results
            
        except HttpResponseError as e:
            logger.error(f"Azure Search error: {e}")
            raise
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def generate_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings for text using Azure OpenAI.
        
        Args:
            text: Text to generate embeddings for
            
        Returns:
            List of embedding values
        """
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"  # Default embedding model
            )
            
            embeddings = response.data[0].embedding
            logger.debug(f"Generated embeddings for text: {text[:100]}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise
    
    def generate_answer(
        self,
        query: str,
        contexts: List[str],
        system_message: str = None,
        temperature: float = 0.0,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate answer using Azure OpenAI with retrieved contexts.
        
        Args:
            query: User query
            contexts: List of context strings from search
            system_message: Optional system message
            temperature: Generation temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated answer
        """
        try:
            # Default system message
            if system_message is None:
                system_message = (
                    "You are a helpful AI assistant that answers questions based on the provided context. "
                    "Use only the information from the context to answer questions. "
                    "If the context doesn't contain enough information, say so clearly."
                )
            
            # Prepare context
            context_text = "\n\n".join([f"Context {i+1}: {ctx}" for i, ctx in enumerate(contexts)])
            
            # Create messages
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {query}"}
            ]
            
            # Generate response
            response = self.openai_client.chat.completions.create(
                model=self.config.openai_deployment_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1.0,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            answer = response.choices[0].message.content
            logger.info(f"Generated answer for query: {query[:100]}")
            return answer
            
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            raise
    
    async def process_rag_query(
        self,
        query: str,
        top_k: int = 5,
        search_type: str = "hybrid",
        use_embeddings: bool = True,
        system_message: str = None,
        temperature: float = 0.0,
        max_tokens: int = 1000
    ) -> RAGResponse:
        """
        Process a complete RAG query with search and generation.
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
            search_type: Type of search to perform
            use_embeddings: Whether to use vector embeddings
            system_message: Optional system message for generation
            temperature: Generation temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Complete RAG response
        """
        try:
            # Generate embeddings if requested
            vector_query = None
            if use_embeddings:
                vector_query = self.generate_embeddings(query)
            
            # Search for relevant documents
            search_results = await self.search_documents(
                query=query,
                top_k=top_k,
                search_type=search_type,
                vector_query=vector_query
            )
            
            # Extract contexts
            contexts = [result.content for result in search_results if result.content]
            
            # Generate answer
            answer = self.generate_answer(
                query=query,
                contexts=contexts,
                system_message=system_message,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Create response
            rag_response = RAGResponse(
                query=query,
                answer=answer,
                contexts=contexts,
                search_results=search_results,
                metadata={
                    "search_type": search_type,
                    "top_k": top_k,
                    "use_embeddings": use_embeddings,
                    "num_contexts": len(contexts),
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            )
            
            logger.info(f"Successfully processed RAG query: {query[:100]}")
            return rag_response
            
        except Exception as e:
            logger.error(f"RAG query processing failed: {e}")
            raise
    
    async def batch_process_queries(
        self,
        queries: List[str],
        batch_size: int = 5,
        **kwargs
    ) -> List[RAGResponse]:
        """
        Process multiple RAG queries in batches for better performance.
        
        Args:
            queries: List of queries to process
            batch_size: Number of queries to process in parallel
            **kwargs: Additional arguments for process_rag_query
            
        Returns:
            List of RAG responses
        """
        results = []
        
        # Process queries in batches
        for i in range(0, len(queries), batch_size):
            batch = queries[i:i + batch_size]
            
            # Create tasks for parallel processing
            tasks = [
                self.process_rag_query(query, **kwargs)
                for query in batch
            ]
            
            # Execute batch
            try:
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Handle results and exceptions
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        logger.error(f"Failed to process query {i+j}: {batch[j][:100]} - {result}")
                        # Create error response
                        error_response = RAGResponse(
                            query=batch[j],
                            answer="Error occurred during processing",
                            contexts=[],
                            search_results=[],
                            metadata={"error": str(result)}
                        )
                        results.append(error_response)
                    else:
                        results.append(result)
                        
            except Exception as e:
                logger.error(f"Batch processing failed: {e}")
                raise
        
        logger.info(f"Processed {len(results)} queries in total")
        return results
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the RAG system components.
        
        Returns:
            Health status of system components
        """
        health_status = {
            "timestamp": None,
            "search_service": "unknown",
            "openai_service": "unknown",
            "overall": "unknown"
        }
        
        try:
            import datetime
            health_status["timestamp"] = datetime.datetime.utcnow().isoformat()
            
            # Test search service
            try:
                results = self.search_client.search("test", top=1)
                list(results)  # Force execution
                health_status["search_service"] = "healthy"
            except Exception as e:
                logger.warning(f"Search service health check failed: {e}")
                health_status["search_service"] = "unhealthy"
            
            # Test OpenAI service
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.config.openai_deployment_name,
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=1
                )
                health_status["openai_service"] = "healthy"
            except Exception as e:
                logger.warning(f"OpenAI service health check failed: {e}")
                health_status["openai_service"] = "unhealthy"
            
            # Overall health
            if (health_status["search_service"] == "healthy" and 
                health_status["openai_service"] == "healthy"):
                health_status["overall"] = "healthy"
            else:
                health_status["overall"] = "unhealthy"
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            health_status["overall"] = "error"
        
        return health_status