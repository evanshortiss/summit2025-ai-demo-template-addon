"""Tests for the Backstage notification tool."""

import pytest
from unittest.mock import Mock, patch
from src.tools.backstage_notification_tool import BackstageNotificationTool, create_backstage_notification_tool


class TestBackstageNotificationTool:
    """Test cases for BackstageNotificationTool."""
    
    def test_create_tool(self):
        """Test tool creation."""
        tool = create_backstage_notification_tool()
        
        assert isinstance(tool, BackstageNotificationTool)
        assert tool.name == "send_backstage_notification"
        assert "notification" in tool.description.lower()
        assert "backstage" in tool.description.lower()
    
    @patch('src.tools.backstage_notification_tool.send_backstage_notification')
    def test_successful_notification(self, mock_send_notification):
        """Test successful notification sending."""
        mock_send_notification.return_value = "Notification sent successfully to Backstage (status: 200)"
        
        tool = BackstageNotificationTool()
        result = tool._run(
            title="Test Notification",
            description="Test message content"
        )
        
        assert "successfully" in result
        mock_send_notification.assert_called_once_with("Test Notification", "Test message content", None)
    
    @patch('src.tools.backstage_notification_tool.send_backstage_notification')
    def test_failed_notification(self, mock_send_notification):
        """Test failed notification handling."""
        mock_send_notification.side_effect = Exception("API connection failed")
        
        tool = BackstageNotificationTool()
        result = tool._run(
            title="Test Notification",
            description="Test message content"
        )
        
        assert "Error:" in result
        assert "API connection failed" in result
        mock_send_notification.assert_called_once()
    
    @patch('src.tools.backstage_notification_tool.send_backstage_notification')
    def test_tool_input_validation(self, mock_send_notification):
        """Test that tool validates input correctly."""
        mock_send_notification.return_value = "Success"
        
        tool = BackstageNotificationTool()
        
        # Test with valid inputs
        result = tool._run(
            title="Valid Title",
            description="Valid description with details"
        )
        
        assert "Error:" not in result
        mock_send_notification.assert_called_once_with("Valid Title", "Valid description with details", None)
    
    def test_tool_schema(self):
        """Test that the tool has correct input schema."""
        tool = BackstageNotificationTool()
        
        # Check that args_schema is properly defined
        assert hasattr(tool, 'args_schema')
        
        # Check that schema has required fields
        schema_fields = tool.args_schema.__fields__
        assert 'title' in schema_fields
        assert 'description' in schema_fields
        
        # Check field descriptions
        assert 'title' in schema_fields['title'].field_info.description
        assert 'description' in schema_fields['description'].field_info.description
        assert 'entity_ref' in schema_fields
        assert schema_fields['entity_ref'].default is None  # Should be optional
    
    @patch('src.tools.backstage_notification_tool.send_backstage_notification')
    async def test_async_run(self, mock_send_notification):
        """Test async version of the tool."""
        mock_send_notification.return_value = "Async notification sent"
        
        tool = BackstageNotificationTool()
        result = await tool._arun(
            title="Async Test",
            description="Async test description"
        )
        
        assert "Async notification sent" in result
        mock_send_notification.assert_called_once_with("Async Test", "Async test description", None)
    
    @patch('src.tools.backstage_notification_tool.send_backstage_notification')
    def test_tool_logging(self, mock_send_notification):
        """Test that tool logs appropriately."""
        mock_send_notification.return_value = "Success"
        
        tool = BackstageNotificationTool()
        
        with patch('src.tools.backstage_notification_tool.logger') as mock_logger:
            tool._run(title="Log Test", description="Test logging")
            
            # Should log successful notification
            mock_logger.info.assert_called_once()
            log_call = mock_logger.info.call_args[0][0]
            assert "Log Test" in log_call
    
    @patch('src.tools.backstage_notification_tool.send_backstage_notification')
    def test_tool_error_logging(self, mock_send_notification):
        """Test that tool logs errors appropriately."""
        mock_send_notification.side_effect = Exception("Test error")
        
        tool = BackstageNotificationTool()
        
        with patch('src.tools.backstage_notification_tool.logger') as mock_logger:
            result = tool._run(title="Error Test", description="Test error handling")
            
            # Should log error
            mock_logger.error.assert_called_once()
            assert "Error:" in result
    
    @patch('src.tools.backstage_notification_tool.send_backstage_notification')
    def test_notification_with_entity_ref(self, mock_send_notification):
        """Test notification with specific entity reference."""
        mock_send_notification.return_value = "Notification sent to specific entity"
        
        tool = BackstageNotificationTool()
        result = tool._run(
            title="Specific Team Notification",
            description="This goes to a specific team",
            entity_ref="group:default/platform-team"
        )
        
        assert "Notification sent to specific entity" in result
        mock_send_notification.assert_called_once_with(
            "Specific Team Notification", 
            "This goes to a specific team",
            "group:default/platform-team"
        )
    
    @patch('src.tools.backstage_notification_tool.send_backstage_notification')
    def test_notification_without_entity_ref(self, mock_send_notification):
        """Test notification without entity reference (uses default)."""
        mock_send_notification.return_value = "Notification sent to default entity"
        
        tool = BackstageNotificationTool()
        result = tool._run(
            title="Default Notification",
            description="This goes to default recipient"
        )
        
        assert "Notification sent to default entity" in result
        mock_send_notification.assert_called_once_with(
            "Default Notification",
            "This goes to default recipient", 
            None
        )
