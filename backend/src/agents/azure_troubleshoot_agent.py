import semantic_kernel as sk
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread, AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.filters import FunctionInvocationContext
from azure.identity.aio import DefaultAzureCredential
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

logger = logging.getLogger(__name__)

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
        if "messages" not in context.arguments:
            await next(context)
            return
        print(f"    Agent [{context.function.name}] called with messages: {context.arguments['messages']}")
        await next(context)
        print(f"    Response from agent [{context.function.name}]: {context.result.value}")
    
    async def initialize(self):
        """Initialize the multi-agent system"""
        with self.tracer.start_as_current_span("agent_initialization"):
            try:
                # Setup Azure OpenAI service
                api_key = os.getenv("AZURE_OPENAI_API_KEY")
                endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
                deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
                project_endpoint = os.getenv("PROJECT_ENDPOINT")
                foundry_technical_support_agent_id = os.getenv("FOUNDARY_TECHNICAL_SUPPORT_AGENT_ID")
                
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
                        self.creds = DefaultAzureCredential()
                        self.client = AzureAIAgent.create_client(credential=self.creds, endpoint=project_endpoint)
                        foundry_technical_support_agent_definition = await self.client.agents.get_agent(agent_id=foundry_technical_support_agent_id)
                        self.foundry_technical_support_agent = AzureAIAgent(client=self.client, definition=foundry_technical_support_agent_definition)
                        logger.info(f"✅ Azure AI Foundry agent initialized successfully - Project Endpoint: {project_endpoint}")
                        
                        # Create Escalation Agent for agent mode
                        self.escalation_agent = ChatCompletionAgent(
                            service=self.ai_service,
                            name="EscalationAgent", 
                            instructions="""
                            You are an agent specializing in escalation to human operators.
                            
                            Handle the following cases:
                            - Complex issues that cannot be resolved by technical support
                            - Billing and account-related issues
                            - Cases requiring enterprise support
                            - High-priority urgent issues
                            - Cases requiring custom development or consulting
                            
                            Please provide users with the following information:
                            1. Problem overview and background
                            2. Appropriate support channels (Azure Portal, Microsoft Support, sales representatives, etc.)
                            3. Information required for escalation
                            4. Expected response time
                            
                            Maintain a kind and understanding approach, and guide users to receive appropriate support.
                            """
                        )
                        
                        # Create plugin list for agent mode
                        plugins = [self.foundry_technical_support_agent, self.escalation_agent]
                        logger.info("🔌 Added Azure AI Foundry agent and Escalation agent to plugins")
                        
                        # Create Triage Agent (Orchestrator) for agent mode
                        self.triage_agent = ChatCompletionAgent(
                            service=self.ai_service,
                            kernel=kernel,
                            name="TriageAgent",
                            instructions="""
                            You are an orchestrator that evaluates user requests and routes them to the appropriate 
                            specialized agent (Azure AI Foundry agent or EscalationAgent) to provide proper support.
                            
                            Analyze user requests and route them according to the following criteria:
                            
                            Route to Azure AI Foundry agent for:
                            - Technical issues with Azure services
                            - Configuration and setup questions
                            - Error message resolution
                            - Best practices consultation
                            - Performance issue diagnosis
                            
                            Route to EscalationAgent for:
                            - Billing and account-related issues
                            - Highly complex technical issues requiring specialized expertise
                            - SLA violations or emergency situations
                            - Cases requiring enterprise-level support
                            - Custom development consultations
                            
                            Provide complete and clear responses to users, including information from the appropriate agents.
                            Ensure that the original user request has been fully processed.
                            """,
                            plugins=plugins,
                        )
                        
                    except Exception as e:
                        error_msg = f"❌ Azure AI Foundry initialization failed - This may be due to private endpoint restrictions or network connectivity issues. Project Endpoint: {project_endpoint}, Error: {str(e)}"
                        logger.error(error_msg)
                        # Fall back to agentless mode
                        use_azure_ai_agent = False
                        self.foundry_technical_support_agent = None
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
                
                mode = "with Azure AI Foundry agent" if use_azure_ai_agent else "in agentless mode with simple AI assistant"
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
    
    async def process_message_stream(self, message: str, session_id: Optional[str] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """Process a message through the multi-agent system and stream the response
        
        Log and telemetry recording is executed after streaming is complete.
        During streaming, responsiveness is prioritized and no log recording is performed.
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        with self.tracer.start_as_current_span("process_message_stream") as span:
            span.set_attribute("session_id", session_id)
            span.set_attribute("message_length", len(message))
            
            try:
                # Get or create thread for this session
                thread = self.sessions.get(session_id)
                if thread is None:
                    thread = ChatHistoryAgentThread()
                
                # Stream the response through triage agent
                # NOTE: During streaming, no log recording is performed to prioritize responsiveness
                async for response in self.triage_agent.invoke_stream(messages=message, thread=thread):
                    if response.content:
                        # During streaming, return only content without log recording
                        yield {
                            "content": str(response.content),
                            "session_id": session_id,
                            "is_done": False
                        }
                    
                    # Update thread state for final logging
                    thread = response.thread
                
                # Post-streaming processing: session storage and log recording
                # Store the final thread state
                self.sessions[session_id] = thread
                
                # Log thread details for debugging and telemetry (executed after streaming completion)
                await self._log_thread_details(thread, session_id)
                
                # Send completion signal
                yield {
                    "content": "",
                    "session_id": session_id,
                    "is_done": True
                }
                
            except ConnectionError as e:
                # Network connectivity error (likely due to private endpoint restrictions)
                error_msg = f"🔒 接続エラー: Azure OpenAIサービスへの接続に失敗しました。これは閉域化設定（Private Endpoint）によるネットワーク制限が原因の可能性があります。システム管理者にネットワーク設定をご確認ください。詳細: {str(e)}"
                logger.error(f"🔒 Network connectivity error in message stream: {e}")
                span.record_exception(e)
                yield {
                    "content": error_msg,
                    "session_id": session_id,
                    "is_done": True
                }
            except Exception as e:
                # Check if the error is related to Azure OpenAI connectivity
                error_str = str(e).lower()
                if any(keyword in error_str for keyword in ['connection', 'network', 'timeout', 'unreachable', 'forbidden', '403', '404', 'dns']):
                    error_msg = f"🔒 接続エラー: Azure OpenAIサービスへの接続に問題があります。これは閉域化設定やネットワーク制限が原因の可能性があります。システム管理者にネットワーク設定をご確認ください。詳細: {str(e)}"
                    logger.error(f"🔒 Potential network connectivity error in message stream: {e}")
                else:
                    error_msg = f"エラー: {str(e)}"
                    logger.error(f"❌ Error in message stream: {e}")
                
                span.record_exception(e)
                yield {
                    "content": error_msg,
                    "session_id": session_id,
                    "is_done": True
                }
