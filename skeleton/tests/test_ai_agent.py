"""Tests for the AI agent module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.ai_agent import MessageAnalysisAgent
from src.config import settings


class TestMessageAnalysisAgent:
    """Test cases for MessageAnalysisAgent."""
    
    @patch('src.ai_agent.ChatOpenAI')
    @patch('src.ai_agent.create_backstage_catalog_tool')
    @patch('src.ai_agent.create_backstage_notification_tool')
    @patch('src.ai_agent.initialize_agent')
    def test_init(self, mock_initialize_agent, mock_notification_tool, mock_catalog_tool, mock_chat_openai):
        """Test agent initialization."""
        mock_catalog_tool.return_value = Mock()
        mock_notification_tool.return_value = Mock()
        mock_chat_openai.return_value = Mock()
        mock_initialize_agent.return_value = Mock()
        
        agent = MessageAnalysisAgent()
        
        assert agent.llm is not None
        assert agent.tools is not None
        assert agent.memory is not None
        assert agent.agent is not None
    
    @patch('src.ai_agent.ChatOpenAI')
    @patch('src.ai_agent.create_backstage_catalog_tool')
    @patch('src.ai_agent.create_backstage_notification_tool')
    @patch('src.ai_agent.initialize_agent')
    def test_process_unknown_message_success(self, mock_initialize_agent, mock_notification_tool,
                                           mock_catalog_tool, mock_chat_openai):
        """Test successful processing of unknown messages."""
        mock_catalog_tool.return_value = Mock()
        mock_notification_tool.return_value = Mock()
        mock_chat_openai.return_value = Mock()
        
        # Mock the agent to return analysis result indicating notification was sent
        mock_agent = Mock()
        mock_agent.run.return_value = "Analysis completed. Used send_backstage_notification to notify the team about the routing failure."
        mock_initialize_agent.return_value = mock_agent
        
        agent = MessageAnalysisAgent()
        
        metadata = {
            'topic': 'unknown',
            'partition': 0,
            'offset': 123,
            'timestamp': 1234567890,
            'headers': {}
        }
        
        # Should not raise any exceptions
        agent.process_unknown_message("Test message content", metadata)
        
        # Verify agent was called with proper prompt
        mock_agent.run.assert_called_once()
        call_args = mock_agent.run.call_args[0][0]
        assert "Test message content" in call_args
        assert "unknown" in call_args
        assert "send_backstage_notification" in call_args
        assert "YOU MUST USE THIS" in call_args
    
    @patch('src.ai_agent.send_backstage_notification')
    @patch('src.ai_agent.ChatOpenAI')
    @patch('src.ai_agent.create_backstage_catalog_tool')
    @patch('src.ai_agent.create_backstage_notification_tool')
    @patch('src.ai_agent.initialize_agent')
    def test_process_unknown_message_agent_error(self, mock_initialize_agent, mock_notification_tool,
                                                mock_catalog_tool, mock_chat_openai, mock_send_notification):
        """Test error handling when agent fails completely."""
        mock_catalog_tool.return_value = Mock()
        mock_notification_tool.return_value = Mock()
        mock_chat_openai.return_value = Mock()
        
        # Mock agent to raise an exception
        mock_agent = Mock()
        mock_agent.run.side_effect = Exception("AI model timeout")
        mock_initialize_agent.return_value = mock_agent
        
        # Mock successful fallback notification
        mock_send_notification.return_value = "Fallback notification sent"
        
        agent = MessageAnalysisAgent()
        
        metadata = {
            'topic': 'unknown',
            'partition': 0,
            'offset': 123,
            'timestamp': 1234567890
        }
        
        # Should not raise exception, but handle it gracefully
        agent.process_unknown_message("Test message", metadata)
        
        # Should send fallback notification
        mock_send_notification.assert_called_once()
        notification_call = mock_send_notification.call_args
        assert notification_call[0][0] == "AI Agent Error"
        assert "AI model timeout" in notification_call[0][1]
    
    @patch('src.ai_agent.ChatOpenAI')
    @patch('src.ai_agent.create_backstage_catalog_tool')
    @patch('src.ai_agent.create_backstage_notification_tool')
    @patch('src.ai_agent.initialize_agent')
    def test_get_agent_status(self, mock_initialize_agent, mock_notification_tool, mock_catalog_tool, mock_chat_openai):
        """Test getting agent status."""
        mock_catalog_tool.return_value = Mock(name="catalog_tool")
        mock_notification_tool.return_value = Mock(name="notification_tool")
        mock_chat_openai.return_value = Mock()
        mock_initialize_agent.return_value = Mock()
        
        # Mock memory
        mock_memory = Mock()
        mock_memory.chat_memory.messages = ["msg1", "msg2"]
        
        agent = MessageAnalysisAgent()
        agent.memory = mock_memory
        
        # Mock tools with names
        agent.tools = [Mock(name="backstage_catalog_groups"), Mock(name="send_backstage_notification")]
        
        status = agent.get_agent_status()
        
        assert 'model' in status
        assert 'inference_server_url' in status
        assert 'temperature' in status
        assert 'max_tokens' in status
        assert 'tools_count' in status
        assert 'memory_messages' in status
        assert 'service_name' in status
        assert 'available_tools' in status
        assert status['service_name'] == settings.service_name
        assert status['memory_messages'] == 2  # Two mock messages
        assert status['tools_count'] == 2  # Two tools
    
    @patch('src.ai_agent.ChatOpenAI')
    @patch('src.ai_agent.create_backstage_catalog_tool')
    @patch('src.ai_agent.create_backstage_notification_tool')
    @patch('src.ai_agent.initialize_agent')
    def test_tools_configuration(self, mock_initialize_agent, mock_notification_tool, mock_catalog_tool, mock_chat_openai):
        """Test that tools are properly configured."""
        mock_catalog_tool.return_value = Mock()
        mock_notification_tool.return_value = Mock()
        mock_chat_openai.return_value = Mock()
        mock_initialize_agent.return_value = Mock()
        
        agent = MessageAnalysisAgent()
        
        # Should have exactly two tools (Backstage Catalog and Notification)
        assert len(agent.tools) == 2
        
        # Verify both tools were created
        mock_catalog_tool.assert_called_once()
        mock_notification_tool.assert_called_once()
    
    @patch('src.ai_agent.ChatOpenAI')
    @patch('src.ai_agent.create_backstage_catalog_tool')
    @patch('src.ai_agent.create_backstage_notification_tool')
    @patch('src.ai_agent.initialize_agent')
    def test_llm_configuration(self, mock_initialize_agent, mock_notification_tool, mock_catalog_tool, mock_chat_openai):
        """Test that LLM is properly configured."""
        mock_catalog_tool.return_value = Mock()
        mock_notification_tool.return_value = Mock()
        mock_initialize_agent.return_value = Mock()
        
        agent = MessageAnalysisAgent()
        
        # Verify ChatOpenAI was called with correct parameters
        mock_chat_openai.assert_called_once_with(
            model_name=settings.ai_model,
            temperature=settings.ai_temperature,
            max_tokens=settings.ai_max_tokens,
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.inference_server_url
        )
    
    @patch('src.ai_agent.ChatOpenAI')
    @patch('src.ai_agent.create_backstage_catalog_tool')
    @patch('src.ai_agent.create_backstage_notification_tool')
    @patch('src.ai_agent.initialize_agent')
    def test_agent_configuration(self, mock_initialize_agent, mock_notification_tool, mock_catalog_tool, mock_chat_openai):
        """Test that agent is properly configured."""
        mock_catalog_tool.return_value = Mock()
        mock_notification_tool.return_value = Mock()
        mock_chat_openai.return_value = Mock()
        
        agent = MessageAnalysisAgent()
        
        # Verify initialize_agent was called with correct parameters
        mock_initialize_agent.assert_called_once()
        call_kwargs = mock_initialize_agent.call_args[1]
        
        assert call_kwargs['agent'] == AgentType.ZERO_SHOT_REACT_DESCRIPTION
        assert call_kwargs['verbose'] == True
        assert call_kwargs['handle_parsing_errors'] == True
        assert call_kwargs['max_iterations'] == 5  # Should be increased for tool usage
    
    @patch('src.ai_agent.ChatOpenAI')
    @patch('src.ai_agent.create_backstage_catalog_tool')
    @patch('src.ai_agent.create_backstage_notification_tool')
    @patch('src.ai_agent.initialize_agent')
    def test_prompt_contains_tool_instructions(self, mock_initialize_agent, mock_notification_tool,
                                             mock_catalog_tool, mock_chat_openai):
        """Test that the prompt includes instructions about available tools."""
        mock_catalog_tool.return_value = Mock()
        mock_notification_tool.return_value = Mock()
        mock_chat_openai.return_value = Mock()
        
        mock_agent = Mock()
        mock_agent.run.return_value = "Analysis complete"
        mock_initialize_agent.return_value = mock_agent
        
        agent = MessageAnalysisAgent()
        
        metadata = {'topic': 'unknown', 'partition': 0, 'offset': 123, 'timestamp': 1234567890}
        agent.process_unknown_message("Test message", metadata)
        
        # Verify the prompt includes tool instructions
        mock_agent.run.assert_called_once()
        prompt = mock_agent.run.call_args[0][0]
        
        assert "backstage_catalog_groups" in prompt
        assert "send_backstage_notification" in prompt
        assert "Available Tools:" in prompt
        assert "YOU MUST USE THIS" in prompt