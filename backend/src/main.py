from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
import os
import sys
from typing import List, Optional, AsyncGenerator
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class StreamChatResponse(BaseModel):
    content: str
    session_id: str
    is_done: bool = False

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
    """Stream chat response"""
    if not agent:
        error_msg = "🔒 サービスが初期化されていません。Azure OpenAIサービスへの接続に問題がある可能性があります。これは閉域化設定（Private Endpoint）によるネットワーク制限が原因の可能性があります。システム管理者にネットワーク設定をご確認ください。"
        logger.error("Agent not initialized - possibly due to connectivity issues")
        raise HTTPException(status_code=500, detail=error_msg)
    
    async def generate():
        try:
            async for chunk in agent.process_message_stream(
                message=request.message,
                session_id=request.session_id
            ):
                # Convert dict response to Pydantic model for proper serialization
                if isinstance(chunk, dict):
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
            else:
                error_content = f"エラー: {str(e)}"
            
            error_response = StreamChatResponse(
                content=error_content,
                session_id=request.session_id or "error",
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
