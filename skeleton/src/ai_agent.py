"""AI Agent for analyzing failed message routing using LangChain."""

import json
import logging
from typing import Dict, Any, List
from langchain.agents import AgentType, initialize_agent
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory

from .config import settings
from .tools.backstage_catalog import create_backstage_catalog_tool
from .tools.backstage_notification_tool import create_backstage_notification_tool

logger = logging.getLogger(__name__)


class MessageAnalysisAgent:
    """AI Agent for analyzing failed message routing and sending notifications."""
    
    def __init__(self):
        """Initialize the AI agent with tools and memory."""
        self.llm = self._create_llm()
        self.tools = self._create_tools()
        self.memory = self._create_memory()
        self.agent = self._create_agent()
        
    def _create_llm(self) -> ChatOpenAI:
        """Create the OpenAI language model."""
        return ChatOpenAI(
            model_name=settings.ai_model,
            temperature=settings.ai_temperature,
            max_tokens=settings.ai_max_tokens,
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.inference_server_url
        )
    
    def _create_tools(self) -> List:
        """Create the tools available to the agent."""
        tools = []
        
        # Add Backstage Catalog tool for group lookups
        catalog_tool = create_backstage_catalog_tool()
        tools.append(catalog_tool)
        
        # Add Backstage Notification tool
        notification_tool = create_backstage_notification_tool()
        tools.append(notification_tool)
        
        return tools
    
    def _create_memory(self) -> ConversationBufferWindowMemory:
        """Create conversation memory for the agent."""
        return ConversationBufferWindowMemory(
            memory_key="chat_history",
            k=10,  # Keep last 10 interactions
            return_messages=True
        )
    
    def _create_agent(self):
        """Create the LangChain agent."""
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5  # Increased to allow for tool usage
        )
    
    def process_unknown_message(self, message_content: str, metadata: Dict[str, Any]) -> None:
        """Process a message from the unknown topic."""
        try:
            logger.info(f"Processing unknown message: {message_content[:100]}...")
            
            # Create a comprehensive prompt for the agent
            analysis_prompt = f"""
You are an expert system analyst reviewing a message that failed to be routed properly. A message has been sent to the 'unknown' topic, indicating a classification failure.

**Message Content:**
{message_content}

**Message Metadata:**
- Topic: {metadata.get('topic')}
- Partition: {metadata.get('partition')}
- Offset: {metadata.get('offset')}
- Timestamp: {metadata.get('timestamp')}
- Headers: {metadata.get('headers', {{}})}

**Your Task:**
1. Analyze this message to determine why it failed to be classified
2. Use the analysis prompt template: {settings.analysis_prompt_template.format(message=message_content)}
3. If helpful for your analysis, look up relevant teams or groups in the Backstage Catalog to understand organizational structure
4. Provide a detailed explanation of the likely cause and specific recommendations
5. **IMPORTANT: Send a notification to Backstage** with your analysis results using the notification tool

**Available Tools:**
- `backstage_catalog_groups`: Look up Groups in the Backstage Catalog to understand team structures and ownership
- `send_backstage_notification`: Send a notification to Backstage with your analysis findings (YOU MUST USE THIS)

Please complete your analysis and send a notification to the relevant group with your findings.
"""
            
            # Use the agent to analyze the message and send notification
            result = self.agent.run(analysis_prompt)
            
            logger.info(f"Agent completed analysis and notification: {result}")
            
        except Exception as e:
            logger.error(f"Error processing unknown message: {e}", exc_info=True)
            
            # Send a fallback notification directly if agent fails completely
            try:
                from .tools.backstage_notification import send_backstage_notification
                title = "AI Agent Error"
                description = f"""The AI agent encountered an error while analyzing a failed message:

**Error:** {str(e)}

**Original Message:** 
{message_content[:200]}{'...' if len(message_content) > 200 else ''}

**Metadata:**
- Topic: {metadata.get('topic')}
- Partition: {metadata.get('partition')}
- Offset: {metadata.get('offset')}
- Timestamp: {metadata.get('timestamp')}

Please investigate this message routing failure manually."""
                
                send_backstage_notification(title, description)
                logger.info("Sent fallback notification due to agent error")
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
            "memory_messages": len(self.memory.chat_memory.messages) if self.memory.chat_memory else 0,
            "service_name": settings.service_name,
            "available_tools": [tool.name for tool in self.tools]
        }