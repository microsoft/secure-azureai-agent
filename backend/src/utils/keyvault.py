"""
Azure Key Vault integration utilities for secure credential management
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import Azure Key Vault SDK, handle gracefully if not available
try:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential
    KEYVAULT_AVAILABLE = True
except ImportError:
    logger.warning("Azure Key Vault SDK not available. Using environment variables only.")
    KEYVAULT_AVAILABLE = False


def get_secret_from_keyvault(secret_name: str, key_vault_url: Optional[str] = None) -> Optional[str]:
    """
    Get secret from Azure Key Vault if available, otherwise fallback to environment variable
    
    Args:
        secret_name: Name of the secret to retrieve
        key_vault_url: Key Vault URL, defaults to KEY_VAULT_URL environment variable
    
    Returns:
        Secret value or None if not found
    """
    # In production, try Key Vault first
    if os.getenv("ENVIRONMENT") == "production" and KEYVAULT_AVAILABLE:
        try:
            vault_url = key_vault_url or os.getenv("KEY_VAULT_URL")
            if vault_url:
                credential = DefaultAzureCredential()
                client = SecretClient(vault_url=vault_url, credential=credential)
                secret = client.get_secret(secret_name)
                logger.info(f"Retrieved secret '{secret_name}' from Key Vault")
                return secret.value
        except Exception as e:
            logger.warning(f"Failed to retrieve secret '{secret_name}' from Key Vault: {e}")
            logger.info("Falling back to environment variable")
    
    # Fallback to environment variable
    value = os.getenv(secret_name)
    if value:
        # Check if it's a Key Vault reference (Azure App Service syntax)
        if value.startswith("@Microsoft.KeyVault("):
            logger.info(f"Secret '{secret_name}' is configured as Key Vault reference in App Service")
            # Azure App Service will resolve this automatically
            return value
        else:
            logger.info(f"Retrieved secret '{secret_name}' from environment variable")
            return value
    
    logger.warning("A required secret was not found in Key Vault or environment variables")
    return None


def get_secure_config() -> dict:
    """
    Get secure configuration using Key Vault when available
    
    Returns:
        Dictionary of configuration values
    """
    config = {}
    
    # Required secrets
    secrets_to_retrieve = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT", 
        "APPLICATIONINSIGHTS_CONNECTION_STRING",
        "FOUNDARY_TECHNICAL_SUPPORT_AGENT_ID"
    ]
    
    for secret_name in secrets_to_retrieve:
        value = get_secret_from_keyvault(secret_name)
        if value:
            config[secret_name] = value
    
    # Non-secret configuration from environment
    non_secret_config = [
        "AZURE_OPENAI_DEPLOYMENT_NAME",
        "PROJECT_ENDPOINT", 
        "USE_AZURE_AI_AGENT",
        "AZURE_ENV_NAME",
        "AZURE_LOCATION",
        "PORT",
        "FRONTEND_URL",
        "ALLOWED_HOST",
        "ENVIRONMENT"
    ]
    
    for config_name in non_secret_config:
        value = os.getenv(config_name)
        if value:
            config[config_name] = value
    
    return config
