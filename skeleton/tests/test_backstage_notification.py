"""Tests for the Backstage notification tool."""

import pytest
from unittest.mock import Mock, patch
import requests
from src.tools.backstage_notification import BackstageNotificationTool, create_backstage_notification_tool


class TestBackstageNotificationTool:
    """Test cases for BackstageNotificationTool."""
    
    def test_create_tool(self):
        """Test tool creation."""
        tool = create_backstage_notification_tool()
        
        assert isinstance(tool, BackstageNotificationTool)
        assert tool.name == "backstage_notification"
        assert "Backstage" in tool.description
    
    @patch('src.tools.backstage_notification.requests.post')
    def test_successful_notification(self, mock_post):
        """Test successful notification sending."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        tool = BackstageNotificationTool()
        result = tool._run(
            title="Test Notification",
            message="Test message content",
            severity="normal"
        )
        
        assert "Notification sent successfully" in result
        mock_post.assert_called_once()
    
    @patch('src.tools.backstage_notification.requests.post')
    def test_failed_notification(self, mock_post):
        """Test failed notification sending."""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        tool = BackstageNotificationTool()
        result = tool._run(
            title="Test Notification",
            message="Test message content"
        )
        
        assert "Error:" in result
        assert "400" in result
        mock_post.assert_called_once()
    
    @patch('src.tools.backstage_notification.requests.post')
    def test_network_error(self, mock_post):
        """Test network error handling."""
        # Mock network error
        mock_post.side_effect = requests.exceptions.ConnectionError("Network error")
        
        tool = BackstageNotificationTool()
        result = tool._run(
            title="Test Notification",
            message="Test message content"
        )
        
        assert "Error:" in result
        assert "Network error" in result
    
    def test_notification_payload_structure(self):
        """Test that notification payload has correct structure."""
        tool = BackstageNotificationTool()
        
        with patch('src.tools.backstage_notification.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            metadata = {"key": "value"}
            tool._run(
                title="Test Title",
                message="Test Message",
                severity="high",
                topic="test-topic",
                metadata=metadata
            )
            
            # Verify the payload structure
            call_args = mock_post.call_args
            payload = call_args[1]['json']
            
            assert payload['title'] == "Test Title"
            assert payload['message'] == "Test Message"
            assert payload['severity'] == "high"
            assert payload['topic'] == "test-topic"
            assert payload['metadata'] == metadata
            assert 'timestamp' in payload 