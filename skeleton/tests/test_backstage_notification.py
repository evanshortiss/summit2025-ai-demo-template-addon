"""Tests for the Backstage notification utility."""

import pytest
from unittest.mock import Mock, patch
import requests
from src.tools.backstage_notification import send_backstage_notification


class TestBackstageNotification:
    """Test cases for Backstage notification functions."""
    
    @patch('src.tools.backstage_notification.requests.post')
    def test_successful_notification(self, mock_post):
        """Test successful notification sending."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = send_backstage_notification(
            title="Test Notification",
            description="Test message content"
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
        
        result = send_backstage_notification(
            title="Test Notification",
            description="Test message content"
        )
        
        assert "Error:" in result
        assert "400" in result
        mock_post.assert_called_once()
    
    @patch('src.tools.backstage_notification.requests.post')
    def test_network_error(self, mock_post):
        """Test network error handling."""
        # Mock network error
        mock_post.side_effect = requests.exceptions.ConnectionError("Network error")
        
        result = send_backstage_notification(
            title="Test Notification",
            description="Test message content"
        )
        
        assert "Error:" in result
        assert "Network error" in result
    
    @patch('src.tools.backstage_notification.requests.post')
    def test_notification_payload_structure(self, mock_post):
        """Test that notification payload has correct Backstage API structure."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        send_backstage_notification(
            title="Test Title",
            description="Test Description"
        )
        
        # Verify the payload structure matches Backstage API format
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        
        assert 'payload' in payload
        assert 'recipients' in payload
        assert payload['payload']['title'] == "Test Title"
        assert payload['payload']['description'] == "Test Description"
        assert payload['recipients']['type'] == "entity"
        assert 'entityRef' in payload['recipients']
    

    @patch('src.tools.backstage_notification.requests.post')
    def test_send_notification_with_entity_ref(self, mock_post):
        """Test sending notification to specific entity."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = send_backstage_notification(
            title="Test Notification",
            description="Test message content",
            entity_ref="group:default/platform-team"
        )
        
        assert "Notification sent successfully" in result
        
        # Verify the payload structure and entity reference
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert payload['recipients']['entityRef'] == "group:default/platform-team"
        assert payload['payload']['title'] == "Test Notification"
        assert payload['payload']['description'] == "Test message content"
    
    @patch('src.tools.backstage_notification.requests.post')
    def test_send_notification_without_entity_ref(self, mock_post):
        """Test sending notification without entity ref (uses default)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = send_backstage_notification(
            title="Default Notification",
            description="Uses default recipient"
        )
        
        assert "Notification sent successfully" in result
        
        # Verify it uses the settings default
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        # Should use settings.notification_recipient_entity (mocked via settings)
        assert 'entityRef' in payload['recipients']
    
    @patch('src.tools.backstage_notification.requests.post')
    def test_send_notification_error_handling_with_entity_ref(self, mock_post):
        """Test error handling in send_backstage_notification with entity_ref."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        result = send_backstage_notification(
            title="Error Test",
            description="This should fail",
            entity_ref="group:default/test-team"
        )
        
        assert "Error:" in result
        assert "400" in result
        assert "Bad Request" in result 