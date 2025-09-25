from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import uvicorn
import os
import sys
from typing import List, Optional, AsyncGenerator, Dict
import logging
from dotenv import load_dotenv

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.azure_troubleshoot_agent import AzureTroubleshootAgent
from telemetry.setup import setup_telemetry

# Load environment variables from .env file for local development
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup OpenTelemetry
setup_telemetry()

app = FastAPI(
    title="Azure Troubleshoot Agent API",
    description="Semantic Kernel based agent for Azure troubleshooting",
    version="1.0.0"
)

# CORS middleware for frontend communication
# Get allowed origins from environment variable
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8501")
ALLOWED_ORIGINS = [FRONTEND_URL] if FRONTEND_URL else ["http://localhost:8501"]

# Add additional localhost origins for development
if os.getenv("ENVIRONMENT", "development") == "development":
    ALLOWED_ORIGINS.extend(["http://localhost:8501", "http://127.0.0.1:8501"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Restrict to necessary methods
    allow_headers=["Accept", "Content-Type", "Authorization"],
)

# Add security middleware for production
if os.getenv("ENVIRONMENT") == "production":
    # Trust only specified hosts
    allowed_hosts = [os.getenv("ALLOWED_HOST", "localhost")]
    if FRONTEND_URL:
        from urllib.parse import urlparse
        parsed = urlparse(FRONTEND_URL)
        if parsed.hostname:
            allowed_hosts.append(parsed.hostname)
    
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    if os.getenv("ENVIRONMENT") == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    mode: str = "chat"  # "chat" or "agent"
    enable_trace: bool = False  # For agent mode tracing

class StreamChatResponse(BaseModel):
    content: str
    session_id: str
    is_done: bool = False
    mode: str = "chat"
    trace: Optional[Dict] = None  # For agent trace information

# Global agent instance
agent = None

@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup"""
    global agent
    try:
        logger.info("Starting Azure Troubleshoot Agent API...")
        
        # Check required environment variables
        required_vars = ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            logger.error("Please check your .env file or environment configuration.")
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Security validation for production
        if os.getenv("ENVIRONMENT") == "production":
            # Ensure sensitive tracing is disabled in production
            if os.getenv("SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE", "false").lower() == "true":
                logger.warning("⚠️  Sensitive tracing is enabled in production. Consider disabling for security.")
            
            # Ensure content recording is controlled
            if os.getenv("AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED", "false").lower() == "true":
                logger.warning("⚠️  Content recording is enabled in production. Consider disabling for privacy.")
        
        logger.info("Initializing Azure Troubleshoot Agent...")
        agent = AzureTroubleshootAgent()
        await agent.initialize()
        logger.info("✅ Azure Troubleshoot Agent initialized successfully")
    except ConnectionError as e:
        # Network connectivity error (likely due to private endpoint restrictions)
        logger.error(f"🔒 Network connectivity error during startup: {e}")
        logger.error("This may be due to private endpoint restrictions. Please check network configuration.")
        # Don't raise here to allow the API to start for health checks
    except Exception as e:
        logger.error(f"❌ Failed to initialize agent: {e}")
        logger.error("Please check your Azure OpenAI configuration and try again.")
        # Don't raise here to allow the API to start for health checks

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "service": "Azure Troubleshoot Agent API",
        "agent_initialized": agent is not None
    }
    
    if not agent:
        status["status"] = "degraded"
        status["message"] = "Agent not initialized - this may be due to Azure OpenAI connectivity issues or private endpoint restrictions"
        logger.warning("Health check: Agent not initialized")
    
    return status

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Stream chat response with mode selection"""
    if not agent:
        error_msg = "🔒 サービスが初期化されていません。Azure OpenAIサービスへの接続に問題がある可能性があります。これは閉域化設定（Private Endpoint）によるネットワーク制限が原因の可能性があります。システム管理者にネットワーク設定をご確認ください。"
        logger.error("Agent not initialized - possibly due to connectivity issues")
        raise HTTPException(status_code=500, detail=error_msg)
    
    logger.info(f"Processing request with mode: {request.mode}, trace: {request.enable_trace}")
    
    async def generate():
        try:
            # Pass mode and trace settings to the agent
            async for chunk in agent.process_message_stream(
                message=request.message,
                session_id=request.session_id,
                mode=request.mode,
                enable_trace=request.enable_trace
            ):
                # Convert dict response to Pydantic model for proper serialization
                if isinstance(chunk, dict):
                    # Ensure the chunk has the correct structure
                    chunk["mode"] = request.mode
                    chunk_model = StreamChatResponse(**chunk)
                    yield f"data: {chunk_model.model_dump_json()}\n\n"
                else:
                    yield f"data: {chunk.model_dump_json()}\n\n"
        except Exception as e:
            logger.error(f"Error in streaming chat: {e}")
            
            # Check if the error is related to Azure OpenAI connectivity
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ['connection', 'network', 'timeout', 'unreachable', 'forbidden', '403', '404', 'dns']):
                error_content = f"🔒 接続エラー: Azure OpenAIサービスへの接続に問題があります。これは閉域化設定やネットワーク制限が原因の可能性があります。システム管理者にネットワーク設定をご確認ください。詳細: {str(e)}"
            elif request.mode == "agent" and any(keyword in error_str for keyword in ['agent', 'foundry', 'project']):
                error_content = f"🤖 エージェントモードエラー: AI Foundryエージェントとの接続に問題があります。エージェント設定を確認してください。詳細: {str(e)}"
            else:
                error_content = f"エラー: {str(e)}"
            
            error_response = StreamChatResponse(
                content=error_content,
                session_id=request.session_id or "error",
                mode=request.mode,
                is_done=True
            )
            yield f"data: {error_response.model_dump_json()}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

# Note: Azure App Service uses gunicorn
# This uvicorn run is only for local development when running main.py directly
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
