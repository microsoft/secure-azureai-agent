import semantic_kernel as sk
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread, AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.filters import FunctionInvocationContext
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ListSortOrder
from typing import Optional, Dict, Any, AsyncGenerator
import uuid
import logging
import os
import sys
import json
import datetime

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telemetry.setup import get_tracer

# Try to import Key Vault utilities, handle gracefully if not available
try:
    from utils.keyvault import get_secret_from_keyvault
    KEYVAULT_UTILS_AVAILABLE = True
except ImportError:
    logging.warning("Key Vault utilities not available")
    KEYVAULT_UTILS_AVAILABLE = False
    
    def get_secret_from_keyvault(secret_name: str) -> Optional[str]:
        return os.getenv(secret_name)

logger = logging.getLogger(__name__)

class TraceCollector:
    """Collects and formats trace information for agent operations"""
    
    def __init__(self):
        self.operations = []
        self.function_calls = []
        self.current_operation = None
        
    def start_operation(self, operation_name: str, context: Dict[str, Any] = None):
        """Start tracking an operation"""
        self.current_operation = {
            "name": operation_name,
            "start_time": datetime.datetime.now(),
            "context": context or {},
            "completed": False
        }
        
    def complete_operation(self, operation_name: str, result: Dict[str, Any] = None):
        """Complete an operation"""
        if self.current_operation and self.current_operation["name"] == operation_name:
            self.current_operation.update({
                "end_time": datetime.datetime.now(),
                "result": result or {},
                "completed": True
            })
            self.operations.append(self.current_operation.copy())
            self.current_operation = None
            
    def record_function_call(self, function_name: str, arguments: Dict[str, Any], result: Any = None):
        """Record a function call"""
        self.function_calls.append({
            "function": function_name,
            "arguments": arguments,
            "result": result,
            "timestamp": datetime.datetime.now()
        })
        
    def get_current_trace(self) -> Dict[str, Any]:
        """Get current trace information"""
        trace_info = {}
        
        if self.function_calls:
            trace_info["function_calls"] = self.function_calls[-5:]  # Last 5 calls
            
        if self.operations:
            completed_ops = [op for op in self.operations if op["completed"]]
            if completed_ops:
                trace_info["operations"] = completed_ops[-3:]  # Last 3 operations
                
        if self.current_operation:
            trace_info["current_operation"] = self.current_operation
            
        return trace_info if trace_info else None

class AzureTroubleshootAgent:
    """Azure troubleshooting multi-agent system using Semantic Kernel"""
    
    def __init__(self):
        self.ai_service = None
        self.technical_support_agent = None
        self.escalation_agent = None
        self.triage_agent = None
        self.simple_ai_assistant = None
        self.foundry_technical_support_agent = None
        self.sessions: Dict[str, ChatHistoryAgentThread] = {}
        self.tracer = get_tracer()
    
    # Define the auto function invocation filter that will be used by the kernel
    @staticmethod
    async def function_invocation_filter(context: FunctionInvocationContext, next):
        """A filter that will be called for each function call in the response."""
        # Get trace collector from session if available
        trace_collector = getattr(context, '_trace_collector', None)
        
        if "messages" not in context.arguments:
            await next(context)
            return
            
        function_name = context.function.name
        arguments = dict(context.arguments)
        
        print(f"    Agent [{function_name}] called with messages: {arguments.get('messages', 'N/A')}")
        
        # Record function call start
        if trace_collector:
            trace_collector.record_function_call(function_name, arguments)
        
        await next(context)
        
        result_preview = str(context.result.value)[:100] if context.result and context.result.value else "No result"
        print(f"    Response from agent [{function_name}]: {result_preview}")
        
        # Update function call with result
        if trace_collector and trace_collector.function_calls:
            trace_collector.function_calls[-1]["result"] = result_preview
    
    async def initialize(self):
        """Initialize the multi-agent system"""
        with self.tracer.start_as_current_span("agent_initialization"):
            try:
                # Setup Azure OpenAI service using secure credential retrieval
                api_key = get_secret_from_keyvault("AZURE_OPENAI_API_KEY")
                endpoint = get_secret_from_keyvault("AZURE_OPENAI_ENDPOINT") or os.getenv("AZURE_OPENAI_ENDPOINT")
                deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
                project_endpoint = os.getenv("PROJECT_ENDPOINT") or os.getenv("AGENT_API_URL")  # PROJECT_ENDPOINTを優先、フォールバックでAGENT_API_URL
                foundry_technical_support_agent_id = get_secret_from_keyvault("FOUNDARY_TECHNICAL_SUPPORT_AGENT_ID")
                
                # Check if agent mode is enabled (default: False for agentless mode)
                use_azure_ai_agent = os.getenv("USE_AZURE_AI_AGENT", "false").lower() in ("true", "1", "yes", "on")
                
                if not api_key or not endpoint:
                    raise ValueError("Azure OpenAI credentials not configured")
                
                kernel = Kernel()
                
                # Register the function invocation filter defined on this class
                kernel.add_filter("function_invocation", self.function_invocation_filter)
                
                try:
                    self.ai_service = AzureChatCompletion(
                        deployment_name=deployment_name,
                        endpoint=endpoint,
                        api_key=api_key
                    )
                    logger.info(f"✅ Azure OpenAI service initialized successfully - Endpoint: {endpoint}")
                except Exception as e:
                    error_msg = f"❌ Azure OpenAI initialization failed - This may be due to private endpoint restrictions or network connectivity issues. Endpoint: {endpoint}, Error: {str(e)}"
                    logger.error(error_msg)
                    raise ConnectionError(error_msg)
                
                # Initialize based on agent mode
                if use_azure_ai_agent:
                    logger.info("🤖 Azure AI Agent mode enabled - Initializing Azure AI Foundry agent")
                    try:
                        # Use AIProjectClient for proper Azure AI Agent integration
                        from azure.identity import DefaultAzureCredential as SyncDefaultAzureCredential
                        self.sync_creds = SyncDefaultAzureCredential()
                        self.project_client = AIProjectClient(
                            credential=self.sync_creds,
                            endpoint=project_endpoint
                        )
                        
                        # Get agent definition and initialize
                        self.foundry_agent_def = self.project_client.agents.get_agent(foundry_technical_support_agent_id)
                        logger.info(f"✅ Azure AI Foundry agent initialized successfully - Project Endpoint: {project_endpoint}")
                        
                        # Store agent ID for later use
                        self.foundry_agent_id = foundry_technical_support_agent_id
                        
                        # Mark that we have a valid AI Foundry setup
                        self.has_foundry_agent = True
                        logger.info("🎯 Using Azure AI Foundry agent directly via AIProjectClient")
                        
                    except Exception as e:
                        error_msg = f"❌ Azure AI Foundry initialization failed - This may be due to private endpoint restrictions or network connectivity issues. Project Endpoint: {project_endpoint}, Error: {str(e)}"
                        logger.error(error_msg)
                        # Fall back to agentless mode
                        use_azure_ai_agent = False
                        self.has_foundry_agent = False
                        logger.warning("⚠️ Falling back to agentless mode")
                
                if not use_azure_ai_agent:
                    logger.info("🚫 Azure AI Agent mode disabled - Running in agentless mode")
                    # Create simple AI assistant for agentless mode
                    self.simple_ai_assistant = ChatCompletionAgent(
                        service=self.ai_service,
                        name="AzureAssistant",
                        instructions="""
                        You are a helpful AI assistant specialized in Azure cloud services and general technical support.
                        
                        You can help users with:
                        - Azure services troubleshooting and configuration
                        - Best practices and recommendations
                        - Error message explanations and solutions
                        - General cloud computing questions
                        - Development and deployment guidance
                        
                        When responding:
                        - Provide clear, accurate, and helpful information
                        - Give step-by-step guidance when appropriate
                        - Suggest relevant Azure documentation when available
                        - Be honest about limitations and recommend escalation when needed
                        - Maintain a friendly and professional tone
                        
                        You are not part of a multi-agent system - respond directly to user queries as a single AI assistant.
                        """
                    )
                    # Set this as the main agent for processing
                    self.triage_agent = self.simple_ai_assistant
                    logger.info("🤖 Simple AI assistant initialized for agentless mode")
                
                mode = "with Azure AI Foundry agent (direct access)" if use_azure_ai_agent else "in agentless mode with simple AI assistant"
                logger.info(f"✅ Azure Multi-Agent System initialized successfully {mode}")
                
            except ConnectionError as e:
                # Network connectivity error (likely due to private endpoint restrictions)
                logger.error(f"🔒 Network connectivity error during initialization: {e}")
                raise
            except Exception as e:
                logger.error(f"❌ Failed to initialize multi-agent system: {e}")
                raise
    
    async def cleanup(self):
        """Cleanup resources"""
        # Clear sessions
        self.sessions.clear()
        
        # Close AI Project Client if exists
        if hasattr(self, "project_client") and self.project_client:
            # AIProjectClient doesn't have async close, but we can clear the reference
            self.project_client = None
            
        # Close old client if exists (backward compatibility)
        if hasattr(self, "client") and self.client:
            await self.client.close()
        if hasattr(self, "creds") and self.creds:
            await self.creds.close()
            
        logger.info("Multi-agent system cleaned up")
    
    async def _log_thread_details(self, thread: ChatHistoryAgentThread, session_id: str):
        """
        Log thread message details to logs and telemetry.
        
        NOTE: This process is relatively heavy, so it's not called during streaming
        to ensure responsiveness. It's executed after all responses are complete.
        
        Args:
            thread (ChatHistoryAgentThread): The thread to be logged
            session_id (str): The session ID
        """
        try:
            # Get thread message details
            thread_details = await self._extract_thread_details(thread)

            # Log to logger
            logger.info(f"Thread details for session {session_id}:")
            for detail in thread_details:
                logger.info(f"  {detail}")

            # Log to telemetry
            with self.tracer.start_as_current_span("thread_analysis") as span:
                span.set_attribute("session_id", session_id)
                span.set_attribute("message_count", len(thread_details))

                # Message type statistics
                message_types = {}
                for detail in thread_details:
                    msg_type = detail.get("type", "unknown")
                    message_types[msg_type] = message_types.get(msg_type, 0) + 1
                
                for msg_type, count in message_types.items():
                    span.set_attribute(f"message_type_{msg_type}_count", count)

                # Agent usage statistics
                agents_used = set()
                for detail in thread_details:
                    if detail.get("agent_name"):
                        agents_used.add(detail["agent_name"])
                
                span.set_attribute("agents_used", list(agents_used))
                span.set_attribute("unique_agent_count", len(agents_used))

                # Log entire conversation flow to telemetry (for debugging)
                span.add_event("thread_conversation", {
                    "conversation_flow": json.dumps(thread_details, ensure_ascii=False, indent=2)
                })
                
        except Exception as e:
            logger.error(f"Error logging thread details: {e}")
    
    async def _extract_thread_details(self, thread: ChatHistoryAgentThread) -> list:
        """
        Extract detailed information from the thread.
        
        Args:
            thread (ChatHistoryAgentThread): The thread to analyze
            
        Returns:
            list: List of message details
        """
        details = []
        message_index = 0
        
        try:
            async for message in thread.get_messages():
                message_index += 1
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                for item in message.items:
                    detail = {
                        "timestamp": timestamp,
                        "message_index": message_index,
                        "ai_model_id": getattr(message, 'ai_model_id', None),
                        "agent_name": getattr(message, 'name', None)
                    }
                    
                    # Function Call Content
                    if hasattr(item, 'name') and hasattr(item, 'arguments'):  # FunctionCallContent
                        detail.update({
                            "type": "function_call",
                            "function_name": item.name,
                            "arguments": str(item.arguments),
                            "description": f"[Function Calling] by {message.ai_model_id or 'unknown'}"
                        })
                    # Function Result Content
                    elif hasattr(item, 'result'):  # FunctionResultContent
                        result_str = str(item.result)
                        try:
                            # JSON形式の結果をパース試行
                            decoded_result = json.loads(result_str)
                            result_display = decoded_result
                        except json.JSONDecodeError:
                            result_display = result_str
                        
                        detail.update({
                            "type": "function_result",
                            "result": result_display,
                            "description": "[Function Result]"
                        })
                    
                    # Text Content
                    elif hasattr(item, 'text'):  # TextContent
                        if message.name:
                            msg_type = "agent_response"
                            description = f"[Agent Response] from {message.ai_model_id or 'unknown'}"
                        else:
                            msg_type = "user_message"
                            description = "[User Message]"
                        
                        detail.update({
                            "type": msg_type,
                            "content": item.text,
                            "description": description
                        })
                    
                    # Others
                    else:
                        detail.update({
                            "type": "unknown",
                            "raw_item": str(item),
                            "item_type": type(item).__name__,
                            "description": f"[Unknown Item Type] ({type(item).__name__})"
                        })
                    
                    details.append(detail)
        
        except Exception as e:
            logger.error(f"Error extracting thread details: {e}")
            details.append({
                "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "type": "error",
                "description": f"Error extracting message details: {str(e)}"
            })
        
        return details
    
    async def print_thread_details(self, session_id: str):
        """
        Output thread details for the specified session to the console (for debugging).
        
        Args:
            session_id (str): Session ID
        """
        thread = self.sessions.get(session_id)
        if not thread:
            print(f"Session {session_id} not found")
            return
        
        print(f"\n=== Thread Details for Session: {session_id} ===")
        
        try:
            async for message in thread.get_messages():
                print("-----")
                
                for item in message.items:
                    # Function Call Content
                    if hasattr(item, 'name') and hasattr(item, 'arguments'):
                        print(f"[Function Calling] by {message.ai_model_id or 'unknown'}")
                        print(f" - Function Name : {item.name}")
                        print(f" - Arguments     : {item.arguments}")
                    
                    # Function Result Content
                    elif hasattr(item, 'result'):
                        print(f"[Function Result]")
                        result_str = str(item.result)
                        try:
                            decoded = json.loads(result_str)
                            print(f" - Result        : {decoded}")
                        except json.JSONDecodeError:
                            print(f" - Result        : {result_str}")
                    
                    # Text Content
                    elif hasattr(item, 'text'):
                        if message.name:
                            print(f"[Agent Response] from {message.ai_model_id or 'unknown'}")
                        else:
                            print("[User Message]")
                        print(f" - Content       : {item.text}")
                    
                    # Others
                    else:
                        print(f"[Unknown Item Type] ({type(item).__name__})")
                        print(f" - Raw Item      : {item}")
            
            print("=== End of Thread Details ===\n")
            
        except Exception as e:
            print(f"Error printing thread details: {e}")
    
    async def get_thread_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get thread summary for the specified session.
        
        Args:
            session_id (str): Session ID
            
        Returns:
            Dict[str, Any]: Thread summary information
        """
        thread = self.sessions.get(session_id)
        if not thread:
            return {"error": f"Session {session_id} not found"}
        
        try:
            details = await self._extract_thread_details(thread)

            # Collect statistics
            message_types = {}
            agents_used = set()
            total_messages = len(details)
            
            for detail in details:
                msg_type = detail.get("type", "unknown")
                message_types[msg_type] = message_types.get(msg_type, 0) + 1
                
                if detail.get("agent_name"):
                    agents_used.add(detail["agent_name"])
            
            return {
                "session_id": session_id,
                "total_messages": total_messages,
                "message_types": message_types,
                "agents_used": list(agents_used),
                "conversation_details": details
            }
            
        except Exception as e:
            return {"error": f"Error getting thread summary: {str(e)}"}
    
    async def process_message_stream(self, message: str, session_id: Optional[str] = None, mode: str = "chat", enable_trace: bool = False) -> AsyncGenerator[Dict[str, Any], None]:
        """Process a message through the multi-agent system and stream the response
        
        Args:
            message: User message to process
            session_id: Optional session identifier
            mode: Execution mode - "chat" for simple chat, "agent" for full agent capabilities
            enable_trace: Whether to include trace information in the response (agent mode only)
        
        Log and telemetry recording is executed after streaming is complete.
        During streaming, responsiveness is prioritized and no log recording is performed.
        """
        if session_id is None:
            session_id = str(uuid.uuid4())

        with self.tracer.start_as_current_span("process_message_stream") as span:
            span.set_attribute("session_id", session_id)
            span.set_attribute("message_length", len(message))
            span.set_attribute("mode", mode)
            span.set_attribute("enable_trace", enable_trace)
            
            # Initialize trace collector for agent mode
            trace_collector = TraceCollector() if enable_trace and mode == "agent" else None
            
            try:
                # Get or create thread for this session
                thread = self.sessions.get(session_id)
                if thread is None:
                    thread = ChatHistoryAgentThread()
                
                # Route based on mode
                if mode == "agent":
                    # Full agent mode with multi-agent capabilities
                    
                    # Check if agent mode is enabled via environment variable
                    use_azure_ai_agent = os.getenv("USE_AZURE_AI_AGENT", "false").lower() in ("true", "1", "yes", "on")
                    if not use_azure_ai_agent:
                        error_msg = """🤖 **エージェントモードが無効です**

エージェントモードを使用するには、以下の設定が必要です：

**環境変数の設定:**
- `USE_AZURE_AI_AGENT=true` を設定してください
- `PROJECT_ENDPOINT` - AI Foundryプロジェクトのエンドポイント
- `FOUNDARY_TECHNICAL_SUPPORT_AGENT_ID` - FoundryエージェントID

**現在の状況:**
- エージェントモードフラグ: 無効 ❌
- 基本のチャット機能は利用可能です 💬

**対処方法:**
1. システム管理者に環境変数の設定を依頼してください
2. 設定後、アプリケーションを再起動してください
3. または、チャットモードで基本的なAI機能をご利用ください

詳細は管理者向けドキュメントをご確認ください。"""
                        logger.warning(f"Agent mode requested but USE_AZURE_AI_AGENT flag is disabled for session {session_id}")
                        yield {
                            "content": error_msg,
                            "session_id": session_id,
                            "is_done": True,
                            "mode": mode
                        }
                        return
                    
                    # Check if we have a properly initialized AI Foundry agent
                    if not hasattr(self, 'has_foundry_agent') or not self.has_foundry_agent:
                        error_msg = """🔒 **エージェントが初期化されていません**

エージェント機能の初期化に問題があります。以下の可能性があります：

**考えられる原因:**
- AI Foundryプロジェクトとの接続エラー
- エージェント設定の不備
- ネットワーク接続の問題

**対処方法:**
1. チャットモードに切り替えて基本機能をご利用ください
2. システム管理者にエージェント設定の確認を依頼してください
3. しばらく時間をおいてから再度お試しください"""
                        logger.error(error_msg)
                        yield {
                            "content": error_msg,
                            "session_id": session_id,
                            "is_done": True,
                            "mode": mode
                        }
                        return
                    
                    # Use AI Project Client for agent communication
                    logger.info(f"Processing in agent mode for session {session_id}")
                    
                    try:
                        # Create a thread for this conversation
                        ai_thread = self.project_client.agents.threads.create()
                        logger.debug(f"Created AI thread: {ai_thread.id}")
                        
                        # Add user message to thread
                        self.project_client.agents.messages.create(
                            thread_id=ai_thread.id,
                            role="user",
                            content=message
                        )
                        
                        # Run the agent
                        run = self.project_client.agents.runs.create_and_process(
                            thread_id=ai_thread.id,
                            agent_id=self.foundry_agent_id
                        )
                        
                        if run.status == "failed":
                            error_msg = f"🤖 エージェント実行エラー: {run.last_error}"
                            logger.error(error_msg)
                            yield {
                                "content": error_msg,
                                "session_id": session_id,
                                "is_done": True,
                                "mode": mode
                            }
                            return
                        
                        # Get messages from thread
                        messages = self.project_client.agents.messages.list(
                            thread_id=ai_thread.id, 
                            order=ListSortOrder.ASCENDING
                        )
                        
                        # Stream agent response
                        for msg in messages:
                            if msg.role == "assistant" and msg.text_messages:
                                content = msg.text_messages[-1].text.value
                                yield {
                                    "content": content,
                                    "session_id": session_id,
                                    "is_done": False,
                                    "mode": mode
                                }
                                
                    except Exception as agent_e:
                        error_msg = f"🤖 エージェント通信エラー: {str(agent_e)}"
                        logger.error(f"Agent communication error: {agent_e}")
                        yield {
                            "content": error_msg,
                            "session_id": session_id,
                            "is_done": True,
                            "mode": mode
                        }
                        return
                        
                elif mode == "chat":
                    # Simple chat mode using direct AI service
                    logger.info(f"Processing in chat mode for session {session_id}")
                    
                    if not self.simple_ai_assistant:
                        # Create a simple assistant if not available
                        if not self.ai_service:
                            error_msg = "🔒 Chat service not initialized"
                            logger.error(error_msg)
                            yield {
                                "content": error_msg,
                                "session_id": session_id,
                                "is_done": True,
                                "mode": mode
                            }
                            return
                        
                        self.simple_ai_assistant = ChatCompletionAgent(
                            service=self.ai_service,
                            name="SimpleAssistant",
                            instructions="""
                            You are a helpful AI assistant specializing in Azure and technical support.
                            Provide clear, concise, and helpful responses to user questions.
                            Focus on practical solutions and best practices.
                            If you don't know something, acknowledge it honestly and suggest where to find more information.
                            """
                        )
                    
                    try:
                        async for response in self.simple_ai_assistant.invoke_stream(thread=thread, messages=message):
                            if hasattr(response, 'content') and response.content:
                                content = str(response.content)
                                yield {
                                    "content": content,
                                    "session_id": session_id,
                                    "is_done": False,
                                    "mode": mode
                                }
                            
                            if hasattr(response, 'thread'):
                                thread = response.thread
                                
                    except Exception as chat_e:
                        logger.error(f"Error in chat mode: {chat_e}")
                        yield {
                            "content": f"チャットモードでエラーが発生しました: {str(chat_e)}",
                            "session_id": session_id,
                            "is_done": True,
                            "mode": mode
                        }
                        return
                
                else:
                    # Invalid mode
                    error_msg = f"無効なモード: {mode}. 'chat' または 'agent' を使用してください。"
                    logger.error(error_msg)
                    yield {
                        "content": error_msg,
                        "session_id": session_id,
                        "is_done": True,
                        "mode": mode
                    }
                    return
                
                # Post-streaming processing: session storage and log recording
                # Store the final thread state
                self.sessions[session_id] = thread
                
                # Log thread details for debugging and telemetry (executed after streaming completion)
                await self._log_thread_details(thread, session_id)
                
                # Send completion signal with trace information if available
                completion_data = {
                    "content": "",
                    "session_id": session_id,
                    "is_done": True,
                    "mode": mode
                }
                
                # Add final trace information if enabled
                if trace_collector:
                    final_trace = trace_collector.get_current_trace()
                    if final_trace:
                        completion_data["trace"] = final_trace
                
                yield completion_data
                
            except ConnectionError as e:
                # Network connectivity error (likely due to private endpoint restrictions)
                error_msg = f"🔒 接続エラー: Azure OpenAIサービスへの接続に失敗しました。これは閉域化設定（Private Endpoint）によるネットワーク制限が原因の可能性があります。システム管理者にネットワーク設定をご確認ください。詳細: {str(e)}"
                logger.error(f"🔒 Network connectivity error in message stream: {e}")
                span.record_exception(e)
                yield {
                    "content": error_msg,
                    "session_id": session_id,
                    "is_done": True,
                    "mode": mode
                }
            except Exception as e:
                # Check if the error is related to Azure OpenAI connectivity
                error_str = str(e).lower()
                if any(keyword in error_str for keyword in ['connection', 'network', 'timeout', 'unreachable', 'forbidden', '403', '404', 'dns']):
                    error_msg = f"🔒 接続エラー: Azure OpenAIサービスへの接続に問題があります。これは閉域化設定やネットワーク制限が原因の可能性があります。システム管理者にネットワーク設定をご確認ください。詳細: {str(e)}"
                    logger.error(f"🔒 Potential network connectivity error in message stream: {e}")
                elif mode == "agent" and any(keyword in error_str for keyword in ['agent', 'foundry', 'project']):
                    error_msg = f"🤖 エージェントモードエラー: AI Foundryエージェントとの接続に問題があります。エージェント設定を確認してください。詳細: {str(e)}"
                    logger.error(f"🤖 Agent mode error in message stream: {e}")
                else:
                    error_msg = f"エラー: {str(e)}"
                    logger.error(f"❌ Error in message stream: {e}")
                
                span.record_exception(e)
                yield {
                    "content": error_msg,
                    "session_id": session_id,
                    "is_done": True,
                    "mode": mode
                }
