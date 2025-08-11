"""AI Agent for analyzing failed message routing using LangChain."""

import json
import logging
from typing import Dict, Any, List
from langchain.agents import AgentType, initialize_agent
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import HumanMessage, SystemMessage
from langchain.tools import Tool

from .config import settings
from .tools.backstage_notification import create_backstage_notification_tool

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
            openai_api_key=settings.openai_api_key
        )
    
    def _create_tools(self) -> List[Tool]:
        """Create the tools available to the agent."""
        tools = [
            create_backstage_notification_tool(),
        ]
        
        # Add a custom analysis tool
        analysis_tool = Tool(
            name="message_analysis",
            description="Analyze a failed message to determine the cause of routing failure",
            func=self._analyze_message_content
        )
        tools.append(analysis_tool)
        
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
            max_iterations=3
        )
    
    def _analyze_message_content(self, message: str) -> str:
        """Analyze message content to determine routing failure cause."""
        try:
            # Use the configured prompt template
            analysis_prompt = settings.analysis_prompt_template.format(message=message)
            
            response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error analyzing message: {e}")
            return f"Analysis failed: {str(e)}"
    
    def process_unknown_message(self, message_content: str, metadata: Dict[str, Any]) -> None:
        """Process a message from the unknown topic."""
        try:
            logger.info(f"Processing unknown message: {message_content[:100]}...")
            
            # Create a comprehensive prompt for the agent
            prompt = f"""
            A message has been routed to the 'unknown' topic, indicating a classification failure.
            
            Message Content: {message_content}
            
            Metadata:
            - Topic: {metadata.get('topic')}
            - Partition: {metadata.get('partition')}
            - Offset: {metadata.get('offset')}
            - Timestamp: {metadata.get('timestamp')}
            - Headers: {json.dumps(metadata.get('headers', {}), indent=2)}
            
            Please:
            1. Analyze this message to determine why it failed to be classified
            2. Provide a detailed explanation of the likely cause
            3. Send a notification to Backstage with your findings and recommendations
            
            Use the available tools to complete this analysis and notification.
            """
            
            # Run the agent
            result = self.agent.run(prompt)
            
            logger.info(f"Agent analysis completed: {result}")
            
        except Exception as e:
            logger.error(f"Error processing unknown message: {e}", exc_info=True)
            
            # Send a fallback notification
            try:
                notification_tool = create_backstage_notification_tool()
                notification_data = json.dumps({
                    "title": "AI Agent Error",
                    "message": f"Failed to analyze unknown message: {str(e)}\n\nMessage: {message_content[:200]}...",
                    "severity": "high",
                    "metadata": metadata
                })
                notification_tool.run(notification_data)
            except Exception as notification_error:
                logger.error(f"Failed to send fallback notification: {notification_error}")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get the current status of the agent."""
        return {
            "model": settings.ai_model,
            "temperature": settings.ai_temperature,
            "max_tokens": settings.ai_max_tokens,
            "tools_count": len(self.tools),
            "memory_messages": len(self.memory.chat_memory.messages),
            "service_name": settings.service_name
        } 