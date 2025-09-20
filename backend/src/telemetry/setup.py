import os
import logging

from opentelemetry import trace
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from azure.ai.agents.telemetry import AIAgentsInstrumentor

APP_LOGGER_NAME = "myapp"

logger = logging.getLogger(APP_LOGGER_NAME)

def setup_telemetry():
    """Set up OpenTelemetry with Azure Monitor (configure_azure_monitor only)"""
    # Include generative AI input/output in trace attributes (remove if not needed)
    # os.environ['AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED'] = 'true'
    # os.environ['SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE'] = 'true'
    
    logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)

    # Get Application Insights connection string from AI Project (recommended)
    connection_string = None
    AIAgentsInstrumentor().instrument()
    
    # Check for PROJECT_ENDPOINT first
    project_endpoint = os.environ.get("PROJECT_ENDPOINT")
    if project_endpoint:
        try:
            project_client = AIProjectClient(
                credential=DefaultAzureCredential(),
                endpoint=project_endpoint,
            )
            connection_string = project_client.telemetry.get_application_insights_connection_string()
            logger.info("Successfully retrieved connection string from AI Project")
        except Exception as e:
            logger.warning(f"Failed to get connection string from AIProjectClient: {e}. Falling back to environment variables.")
    else:
        logger.info("PROJECT_ENDPOINT is not set. Looking for connection string in environment variables.")

    # Fallback: read from environment variables
    if not connection_string:
        connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

    if not connection_string:
        logger.info("Application Insights connection string not found. Telemetry is disabled for this session.")
        return

    try:
        # This automatically configures providers and exporters for traces, metrics, and logs
        configure_azure_monitor(
            connection_string=connection_string,
            logger_name=APP_LOGGER_NAME,
            # instrumentation_options={
			# 	"azure_sdk": {"enabled": False}
			# }
        )
        logger.info("OpenTelemetry configured for Azure Monitor.")
    except Exception as e:
        logger.error(f"Failed to initialize telemetry: {e}")

def get_tracer():
    """Get the tracer configured by configure_azure_monitor"""
    return trace.get_tracer(__name__)
