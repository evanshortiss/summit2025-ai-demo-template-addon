"""AI Agent for analyzing failed message routing using LangChain."""

import json
import logging
from typing import Dict, Any, List
from langchain.agents import AgentType, initialize_agent
from langchain_openai import OpenAI

from .config import settings
from .tools.backstage_catalog import create_backstage_catalog_tool
from .tools.backstage_notification_tool import create_backstage_notification_tool

logger = logging.getLogger(__name__)


class MessageAnalysisAgent:
    """AI Agent for analyzing failed message routing and sending notifications."""
    
    def __init__(self):
        """Initialize the AI agent with tools."""
        self.llm = self._create_llm()
        self.tools = self._create_tools()
        self.agent = self._create_agent()
        
    def _create_llm(self) -> OpenAI:
        """Create the OpenAI language model."""
        return OpenAI(
            model_name=settings.ai_model,
            temperature=settings.ai_temperature,
            max_tokens=settings.ai_max_tokens,
            # This could be replaced if we wanted to use ExternalSecrets
            openai_api_key="placeholder-key-for-rhoai-without-auth",
            openai_api_base=settings.inference_server_url
        )
    
    def _create_tools(self) -> List:
        tools = []
        
        catalog_tool = create_backstage_catalog_tool()
        tools.append(catalog_tool)
        
        notification_tool = create_backstage_notification_tool()
        tools.append(notification_tool)
        
        return tools
    
    def _create_agent(self):
        # System message for the agent
        system_message = """You are an expert system analyst specializing in message routing failure analysis.

Your role is to:
1. Analyze messages that failed to be routed properly
2. Identify the likely cause of routing failures
3. Provide specific recommendations for resolution
4. Send a notification with your findings

When analyzing messages, consider these common failure causes:
- Ambiguous intent - message could fit multiple categories
- Missing context - insufficient information to classify
- Data format issues - malformed or unexpected structure
- New content type - content not covered by existing rules
- Schema validation failures - data doesn't match expected format

Always use the available tools to complete your analysis and send notifications."""

        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
            agent_kwargs={
                "system_message": system_message
            }
        )
    
    def process_unknown_message(self, message_content: str, metadata: Dict[str, Any]) -> None:
        try:
            logger.info(f"Processing unknown message: {message_content[:100]}...")
            
            # Create a simple, focused prompt for the agent
            headers_json = json.dumps(metadata.get('headers', {}), indent=2)
            
            # Simple prompt that focuses on the task
            input = f"""Analyze this failed message that failed to be routed properly, and generate a one sentence summary of the likely cause of the routing failure.

Message: {message_content}

Metadata: Topic={metadata.get('topic')}, Partition={metadata.get('partition')}, Offset={metadata.get('offset')}

Headers: {headers_json}

Always send a notification containing your analysis and summary of the likely cause of the routing failure."""

            logger.info(f"Input prompt: {input}")
            # Use the agent to analyze the message and send notification
            result = self.agent.run(input)
            
            logger.info(f"Agent completed analysis and notification: {result}")
            
        except Exception as e:
            logger.error(f"Error processing unknown message: {e}", exc_info=True)
            
            # Send a fallback notification directly if agent fails completely
            try:
                from .tools.backstage_notification import send_backstage_notification
                title = "AI Agent Error"
                description = f"""The AI agent encountered an error while analyzing a failed message:

**Error:** {str(e)}

**Metadata:**
- Topic: {metadata.get('topic')}
- Partition: {metadata.get('partition')}
- Offset: {metadata.get('offset')}
- Timestamp: {metadata.get('timestamp')}

Please investigate this message routing failure manually."""
                
                send_backstage_notification(title, description)
            except Exception as notification_error:
                logger.error(f"Failed to send fallback notification: {notification_error}")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get the current status of the agent."""
        return {
            "model": settings.ai_model,
            "inference_server_url": settings.inference_server_url,
            "temperature": settings.ai_temperature,
            "max_tokens": settings.ai_max_tokens,
            "tools_count": len(self.tools),
            "service_name": settings.service_name,
            "available_tools": [tool.name for tool in self.tools]
        }