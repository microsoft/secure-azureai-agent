"""
Configuration module for Azure AI Search RAG evaluation system.
Implements secure configuration management following OSS security best practices.
"""

import os
import logging
from typing import Optional
from dataclasses import dataclass
from pathlib import Path
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env file from current directory or parent directories
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Try to find .env in parent directories
        load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    logging.warning("python-dotenv not available. Environment variables must be set manually.")

logger = logging.getLogger(__name__)

@dataclass
class AzureConfig:
    """Azure service configuration using secure credential management."""
    
    # Azure AI Search configuration
    search_endpoint: str
    search_index_name: str
    
    # Azure OpenAI configuration
    openai_endpoint: str
    openai_deployment_name: str
    openai_api_version: str = "2024-02-15-preview"
    
    # Azure Key Vault configuration (optional)
    keyvault_url: Optional[str] = None
    
    # Authentication
    use_managed_identity: bool = True
    
    @classmethod
    def from_environment(cls) -> "AzureConfig":
        """
        Initialize configuration from environment variables.
        
        Required Environment Variables:
        - AZURE_SEARCH_ENDPOINT: Azure AI Search service endpoint
        - AZURE_SEARCH_INDEX_NAME: Name of the search index
        - AZURE_OPENAI_ENDPOINT: Azure OpenAI service endpoint
        - AZURE_OPENAI_DEPLOYMENT_NAME: Name of the deployment
        
        Optional Environment Variables:
        - AZURE_OPENAI_API_VERSION: API version (default: 2024-02-15-preview)
        - USE_MANAGED_IDENTITY: Use managed identity (default: True)
        
        Note: This implementation uses .env files instead of Azure Key Vault.
        Create a .env file in the same directory with your configuration.
        """
        
        # Validate required environment variables
        required_vars = [
            "AZURE_SEARCH_ENDPOINT",
            "AZURE_SEARCH_INDEX_NAME", 
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_DEPLOYMENT_NAME"
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
        
        return cls(
            search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            search_index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
            openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            openai_deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            keyvault_url=None,  # Not used in this implementation
            use_managed_identity=os.getenv("USE_MANAGED_IDENTITY", "true").lower() == "true"
        )
    
    def get_credential(self):
        """
        Get appropriate Azure credential based on configuration.
        
        Returns:
            Azure credential object for authentication
        """
        try:
            if self.use_managed_identity:
                # Try managed identity first (for Azure-hosted environments)
                credential = ManagedIdentityCredential()
                logger.info("Using Managed Identity for authentication")
            else:
                # Fall back to default credential chain
                credential = DefaultAzureCredential()
                logger.info("Using Default Azure Credential for authentication")
            
            return credential
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure credentials: {e}")
            raise
    
    def get_secret_from_keyvault(self, secret_name: str) -> Optional[str]:
        """
        Retrieve secret from Azure Key Vault if configured.
        Note: Key Vault is not used in this implementation. Use .env file instead.
        
        Args:
            secret_name: Name of the secret to retrieve
            
        Returns:
            None - Key Vault not supported in this configuration
        """
        logger.warning("Key Vault is not configured. Use .env file for configuration instead.")
        return None

@dataclass 
class EvaluationConfig:
    """Configuration for RAG evaluation parameters."""
    
    # RAGAS evaluation metrics
    enable_faithfulness: bool = True
    enable_answer_relevancy: bool = True
    enable_context_precision: bool = True
    enable_context_recall: bool = True
    enable_context_relevancy: bool = True
    
    # Evaluation parameters
    max_context_length: int = 4000
    max_answer_length: int = 1000
    batch_size: int = 10
    
    # LLM configuration for evaluation
    evaluation_model: str = "gpt-4"
    temperature: float = 0.0
    
    @classmethod
    def from_environment(cls) -> "EvaluationConfig":
        """Initialize evaluation configuration from environment variables."""
        return cls(
            enable_faithfulness=os.getenv("ENABLE_FAITHFULNESS", "true").lower() == "true",
            enable_answer_relevancy=os.getenv("ENABLE_ANSWER_RELEVANCY", "true").lower() == "true", 
            enable_context_precision=os.getenv("ENABLE_CONTEXT_PRECISION", "true").lower() == "true",
            enable_context_recall=os.getenv("ENABLE_CONTEXT_RECALL", "true").lower() == "true",
            enable_context_relevancy=os.getenv("ENABLE_CONTEXT_RELEVANCY", "true").lower() == "true",
            max_context_length=int(os.getenv("MAX_CONTEXT_LENGTH", "4000")),
            max_answer_length=int(os.getenv("MAX_ANSWER_LENGTH", "1000")),
            batch_size=int(os.getenv("EVALUATION_BATCH_SIZE", "10")),
            evaluation_model=os.getenv("EVALUATION_MODEL", "gpt-4"),
            temperature=float(os.getenv("EVALUATION_TEMPERATURE", "0.0"))
        )

def setup_logging(level: str = "INFO") -> None:
    """
    Configure logging for the evaluation system.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('rag_evaluation.log')
        ]
    )
    
    # Set Azure SDK logging to WARNING to reduce noise
    logging.getLogger('azure').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

def validate_environment() -> bool:
    """
    Validate that all required environment variables are set.
    
    Returns:
        True if environment is properly configured, False otherwise
    """
    try:
        azure_config = AzureConfig.from_environment()
        eval_config = EvaluationConfig.from_environment()
        
        logger.info("Environment configuration validated successfully")
        logger.info(f"Search endpoint: {azure_config.search_endpoint}")
        logger.info(f"OpenAI endpoint: {azure_config.openai_endpoint}")
        logger.info(f"Using managed identity: {azure_config.use_managed_identity}")
        
        return True
        
    except Exception as e:
        logger.error(f"Environment validation failed: {e}")
        return False