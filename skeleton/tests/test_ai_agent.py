"""Tests for the AI agent module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.ai_agent import MessageAnalysisAgent
from src.config import settings


class TestMessageAnalysisAgent:
    """Test cases for MessageAnalysisAgent."""
    
    @patch('src.ai_agent.ChatOpenAI')
    @patch('src.ai_agent.create_backstage_notification_tool')
    def test_init(self, mock_notification_tool, mock_chat_openai):
        """Test agent initialization."""
        mock_notification_tool.return_value = Mock()
        mock_chat_openai.return_value = Mock()
        
        agent = MessageAnalysisAgent()
        
        assert agent.llm is not None
        assert agent.tools is not None
        assert agent.memory is not None
        assert agent.agent is not None
    
    @patch('src.ai_agent.ChatOpenAI')
    @patch('src.ai_agent.create_backstage_notification_tool')
    def test_analyze_message_content(self, mock_notification_tool, mock_chat_openai):
        """Test message content analysis."""
        mock_notification_tool.return_value = Mock()
        
        # Mock the LLM response
        mock_response = Mock()
        mock_response.content = "This message failed because it lacks clear intent."
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm
        
        agent = MessageAnalysisAgent()
        result = agent._analyze_message_content("Hello, I need help")
        
        assert "failed because it lacks clear intent" in result
        mock_llm.invoke.assert_called_once()
    
    @patch('src.ai_agent.ChatOpenAI')
    @patch('src.ai_agent.create_backstage_notification_tool')
    def test_process_unknown_message(self, mock_notification_tool, mock_chat_openai):
        """Test processing of unknown messages."""
        mock_notification_tool.return_value = Mock()
        mock_chat_openai.return_value = Mock()
        
        # Mock the agent
        mock_agent = Mock()
        mock_agent.run.return_value = "Analysis completed successfully"
        
        agent = MessageAnalysisAgent()
        agent.agent = mock_agent
        
        metadata = {
            'topic': 'unknown',
            'partition': 0,
            'offset': 123,
            'timestamp': 1234567890,
            'headers': {}
        }
        
        # Should not raise any exceptions
        agent.process_unknown_message("Test message", metadata)
        
        mock_agent.run.assert_called_once()
    
    @patch('src.ai_agent.ChatOpenAI')
    @patch('src.ai_agent.create_backstage_notification_tool')
    def test_get_agent_status(self, mock_notification_tool, mock_chat_openai):
        """Test getting agent status."""
        mock_notification_tool.return_value = Mock()
        mock_chat_openai.return_value = Mock()
        
        agent = MessageAnalysisAgent()
        status = agent.get_agent_status()
        
        assert 'model' in status
        assert 'temperature' in status
        assert 'max_tokens' in status
        assert 'tools_count' in status
        assert 'service_name' in status
        assert status['service_name'] == settings.service_name 