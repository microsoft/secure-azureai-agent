import chainlit as cl
import httpx
import os
import json
import asyncio
from typing import Optional, Dict, Any
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
    
    async def send_message_stream(self, message: str, session_id: Optional[str] = None, mode: str = "chat", enable_trace: bool = False):
        """Send message to backend API and stream response"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                payload = {
                    "message": message,
                    "session_id": session_id,
                    "mode": mode,  # Add mode parameter
                    "enable_trace": enable_trace  # Add trace parameter
                }
                
                logger.info(f"Sending request with mode: {mode}, trace: {enable_trace}")
                
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
    
    # Set up mode selection for the session
    settings = await cl.ChatSettings([
        cl.input_widget.Select(
            id="mode",
            label="🤖 実行モード",
            values=["chat", "agent"],
            initial_index=0,
            tooltip="チャットモード: シンプルな会話型AI\nエージェントモード: AI Foundryの高度なエージェント機能を使用"
        ),
        cl.input_widget.Switch(
            id="enable_trace",
            label="🔍 エージェント動作のトレース表示",
            initial=False,
            tooltip="エージェントモードでツール呼び出しや思考プロセスを表示"
        )
    ]).send()
    
    # Store initial mode in session
    cl.user_session.set("mode", "chat")
    cl.user_session.set("enable_trace", False)
    cl.user_session.set("session_history", [])  # Track conversation history across mode changes
    
    # Welcome message
    welcome_message = """🚀 **Azure AI エージェント** へようこそ！

**実行モード:**
- 📝 **チャットモード**: シンプルな会話型AIとしてご質問にお答えします
- 🤖 **エージェントモード**: AI Foundryの高度なエージェント機能を使用し、専門的なツールを活用してサポートします

**設定変更:**
右上の設定ボタン（⚙️）からモードを切り替えることができます。

⚠️ **注意**: エージェントモードを使用するには管理者による環境設定が必要です。設定が完了していない場合はチャットモードをご利用ください。

**得意分野:**
• **Azure技術サポート** - Azureサービスのトラブルシューティングとベストプラクティス
• **システム診断** - 技術的問題の特定とトラブルシューティング
• **最適化提案** - パフォーマンス改善とリソース最適化のアドバイス

ご質問をお聞かせください！"""
    
    await cl.Message(content=welcome_message).send()
    
    # Store session information
    cl.user_session.set("session_started", True)

@cl.on_settings_update
async def on_settings_update(settings: Dict[str, Any]):
    """Handle settings updates"""
    old_mode = cl.user_session.get("mode", "chat")
    new_mode = settings.get("mode", "chat")
    enable_trace = settings.get("enable_trace", False)
    
    # Update session with new settings
    cl.user_session.set("mode", new_mode)
    cl.user_session.set("enable_trace", enable_trace)
    
    logger.info(f"Settings updated - Old mode: {old_mode}, New mode: {new_mode}, Trace: {enable_trace}")
    
    # Send confirmation message
    mode_display = "🤖 エージェントモード" if new_mode == "agent" else "📝 チャットモード"
    trace_display = "有効" if enable_trace else "無効"
    
    # Check if mode changed
    mode_change_msg = ""
    if old_mode != new_mode:
        mode_change_msg = f"\n\n⚡ モードが変更されました: {old_mode} → {new_mode}\n会話履歴は継続されます。"
        
        # Add warning for agent mode
        if new_mode == "agent":
            mode_change_msg += f"""
            
⚠️ **エージェントモードについて:**
エージェントモードを使用するには、システム管理者による以下の設定が必要です：
- `USE_AZURE_AI_AGENT=true` 環境変数の設定
- AI Foundryプロジェクトの接続設定

設定が完了していない場合は、エラーメッセージが表示されます。
その場合はチャットモードでの基本機能をご利用ください。"""
    
    await cl.Message(
        content=f"⚙️ 設定が更新されました:\n- 実行モード: {mode_display}\n- トレース表示: {trace_display}{mode_change_msg}"
    ).send()

@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages"""
    logger.info(f"Received message: {message.content[:100]}...")
    
    # Get current mode and trace settings from session
    current_mode = cl.user_session.get("mode", "chat")
    enable_trace = cl.user_session.get("enable_trace", False)
    
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
    
    # Show mode indicator
    mode_indicator = "🤖 エージェントモード" if current_mode == "agent" else "📝 チャットモード"
    status_msg = await cl.Message(content=f"{mode_indicator} で処理中...").send()
    
    # Initialize trace messages list for agent mode
    trace_messages = []
    
    try:
        # Use streaming for better user experience with current mode
        async for chunk in api_client.send_message_stream(
            message=message.content,
            session_id=session_id,
            mode=current_mode,
            enable_trace=enable_trace
        ):
            if chunk.get("content"):
                await response_msg.stream_token(chunk["content"])
            
            # Handle trace information if available and enabled
            if enable_trace and current_mode == "agent" and chunk.get("trace"):
                trace_data = chunk["trace"]
                trace_content = await format_trace_data(trace_data)
                if trace_content:
                    trace_messages.append(trace_content)
            
            if chunk.get("is_done", False):
                break
        
        # Remove status message after processing is complete
        await status_msg.remove()
        
        # Send the final message
        await response_msg.send()
        
        # Send trace information as separate expandable messages if enabled
        if enable_trace and current_mode == "agent" and trace_messages:
            for trace_msg in trace_messages:
                await cl.Message(
                    content=trace_msg,
                    elements=[cl.Text(name="trace", content=trace_msg, display="side")]
                ).send()
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        
        # Remove status message in case of error
        try:
            await status_msg.remove()
        except:
            pass  # Ignore if message already removed
        
        # Check if the error is network-related
        error_str = str(e).lower()
        if any(keyword in error_str for keyword in ['connection', 'network', 'timeout', 'unreachable', 'forbidden']):
            error_message = "🔒 接続エラー: サービスとの通信に問題があります。これは閉域化設定やネットワーク制限が原因の可能性があります。システム管理者にネットワーク設定をご確認ください。"
        elif current_mode == "agent" and any(keyword in error_str for keyword in ['agent', 'foundry', 'project']):
            error_message = f"🤖 エージェントモードエラー: AI Foundryエージェントとの接続に問題があります。\n\n**対処方法:**\n1. チャットモードに切り替えて基本的な機能をご利用ください\n2. AI Foundryプロジェクトの設定を確認してください\n3. エージェント接続情報が正しく設定されているか確認してください\n\n詳細: {str(e)}"
        elif current_mode == "agent" and "trace" in error_str:
            error_message = f"🔍 トレース機能エラー: エージェントのトレース表示でエラーが発生しました。基本的なエージェント機能は動作する可能性があります。\n\n詳細: {str(e)}"
        else:
            error_message = f"❌ メッセージ処理中にエラーが発生しました: {str(e)}"
        
        await cl.Message(content=error_message).send()

async def format_trace_data(trace_data: Dict[str, Any]) -> Optional[str]:
    """Format trace data for display"""
    if not trace_data:
        return None
    
    trace_lines = ["🔍 **エージェント動作トレース:**"]
    
    if trace_data.get("function_calls"):
        trace_lines.append("\n📞 **ツール呼び出し:**")
        for call in trace_data["function_calls"]:
            function_name = call.get("function", "Unknown")
            arguments = call.get("arguments", {})
            result = call.get("result", "No result")
            
            trace_lines.append(f"- **{function_name}**")
            if arguments:
                trace_lines.append(f"  - 引数: `{json.dumps(arguments, ensure_ascii=False, indent=2)}`")
            if result:
                trace_lines.append(f"  - 結果: `{str(result)[:200]}{'...' if len(str(result)) > 200 else ''}`")
    
    if trace_data.get("thought_process"):
        trace_lines.append("\n🧠 **思考プロセス:**")
        for step in trace_data["thought_process"]:
            trace_lines.append(f"- {step}")
    
    if trace_data.get("decision_making"):
        trace_lines.append("\n⚖️ **意思決定:**")
        for decision in trace_data["decision_making"]:
            trace_lines.append(f"- {decision}")
    
    return "\n".join(trace_lines) if len(trace_lines) > 1 else None

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
