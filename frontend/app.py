import chainlit as cl
import httpx
import os
import json
import asyncio
from typing import Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Backend API configuration
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

class BackendAPIClient:
    """Client for communicating with the backend API"""
    
    def __init__(self):
        self.base_url = BACKEND_API_URL
    
    async def send_message_stream(self, message: str, session_id: Optional[str] = None):
        """Send message to backend API and stream response"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                payload = {
                    "message": message,
                    "session_id": session_id
                }
                
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/chat/stream",
                    json=payload,
                    headers={"Accept": "text/event-stream"}
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]  # Remove "data: " prefix
                            try:
                                yield json.loads(data)
                            except json.JSONDecodeError:
                                continue
                                
            except httpx.ConnectError as e:
                logger.error(f"🔒 Connection error to backend: {e}")
                yield {
                    "content": "🔒 接続エラー: バックエンドサービスに接続できません。これは閉域化設定やネットワーク制限が原因の可能性があります。システム管理者にネットワーク設定をご確認ください。",
                    "session_id": session_id or "error",
                    "is_done": True
                }
            except httpx.TimeoutException as e:
                logger.error(f"🔒 Timeout error: {e}")
                yield {
                    "content": "🔒 タイムアウトエラー: サービスからの応答がありません。これは閉域化設定やネットワーク制限が原因の可能性があります。システム管理者にネットワーク設定をご確認ください。",
                    "session_id": session_id or "error",
                    "is_done": True
                }
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP status error: {e}")
                if e.response.status_code == 500:
                    yield {
                        "content": "🔒 サービスエラー: Azure OpenAIサービスとの接続に問題があります。これは閉域化設定（Private Endpoint）によるネットワーク制限が原因の可能性があります。システム管理者にネットワーク設定をご確認ください。",
                        "session_id": session_id or "error",
                        "is_done": True
                    }
                else:
                    yield {
                        "content": f"❌ HTTPエラー: {e.response.status_code} - {e.response.text}",
                        "session_id": session_id or "error",
                        "is_done": True
                    }
            except httpx.HTTPError as e:
                logger.error(f"HTTP error in streaming: {e}")
                yield {
                    "content": f"🔒 通信エラー: {str(e)} - これは閉域化設定やネットワーク制限が原因の可能性があります。",
                    "session_id": session_id or "error",
                    "is_done": True
                }
            except Exception as e:
                logger.error(f"Error in streaming: {e}")
                yield {
                    "content": f"❌ 予期しないエラー: {str(e)}",
                    "session_id": session_id or "error",
                    "is_done": True
                }
    
    async def health_check(self):
        """Check if backend is healthy"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    health_data = response.json()
                    if health_data.get("status") == "degraded":
                        logger.warning(f"Backend service is degraded: {health_data.get('message', 'Unknown issue')}")
                    return True
                return False
            except httpx.ConnectError as e:
                logger.error(f"🔒 Connection error during health check: {e}")
                return False
            except httpx.TimeoutException as e:
                logger.error(f"🔒 Timeout during health check: {e}")
                return False
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return False

# Global API client
api_client = BackendAPIClient()

@cl.on_chat_start
async def on_chat_start():
    """Initialize chat session"""
    logger.info("Starting new chat session")
    
    # Welcome message
    welcome_message = """# 🤖 Technical Support Assistant

Welcome! I'm your technical support assistant. I can help you:

• **Technical problem solving** - Analyze and provide solutions for various technical issues
• **System diagnostics** - Help identify and troubleshoot system problems
• **Best practices guidance** - Recommend optimal approaches for technical implementations
• **Resource optimization** - Provide advice on improving performance and efficiency

To get started, describe the technical issue you're experiencing or ask me about any technical topic.

**Example questions:**
- "My application is running slowly, can you help identify the cause?"
- "What are the best practices for deploying a web application?"
- "How can I optimize my system's performance?"
"""
    
    await cl.Message(content=welcome_message).send()
    
    # Store session information
    cl.user_session.set("session_started", True)

@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages"""
    logger.info(f"Received message: {message.content[:100]}...")
    
    # Get session ID (use Chainlit's session ID)
    session_id = cl.user_session.get("id")
    
    # Create response message
    response_msg = cl.Message(content="")
    
    try:
        # Check if backend is available by making a simple request first
        if not await api_client.health_check():
            await cl.Message(
                content="🔒 バックエンドサービスが利用できません。これは閉域化設定やネットワーク制限が原因の可能性があります。システム管理者にネットワーク設定をご確認ください。"
            ).send()
            return
            
    except Exception as e:
        logger.error(f"Backend health check failed: {e}")
        await cl.Message(
            content="🔒 バックエンドサービスに接続できません。これは閉域化設定やネットワーク制限が原因の可能性があります。システム管理者にネットワーク設定をご確認ください。"
        ).send()
        return
    
    try:
        # Use streaming for better user experience
        async for chunk in api_client.send_message_stream(
            message=message.content,
            session_id=session_id
        ):
            if chunk.get("content"):
                await response_msg.stream_token(chunk["content"])
            
            if chunk.get("is_done", False):
                break
        
        # Send the final message
        await response_msg.send()
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        
        # Check if the error is network-related
        error_str = str(e).lower()
        if any(keyword in error_str for keyword in ['connection', 'network', 'timeout', 'unreachable', 'forbidden']):
            error_message = "🔒 接続エラー: サービスとの通信に問題があります。これは閉域化設定やネットワーク制限が原因の可能性があります。システム管理者にネットワーク設定をご確認ください。"
        else:
            error_message = f"❌ 申し訳ございませんが、リクエストの処理中にエラーが発生しました: {str(e)}"
            
        await cl.Message(content=error_message).send()

@cl.on_chat_end
async def on_chat_end():
    """Clean up when chat ends"""
    logger.info("Chat session ended")
    # Don't close the client here as it might be reused
    # await api_client.close()

if __name__ == "__main__":
    # For local development, you can run this directly
    port = int(os.getenv("PORT", 8501))
    
    # Run Chainlit app
    # Note: In production, use chainlit CLI commands instead
    logger.info(f"Starting Chainlit app on port {port}")
    
    # This is a placeholder - in practice, use: chainlit run app.py --port {port}
    print(f"To run this app, use: chainlit run app.py --port {port}")
