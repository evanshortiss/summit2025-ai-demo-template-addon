"""Backstage notification tool for LangChain agents."""

import json
import logging
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import requests
from langchain.tools import BaseTool

from ..config import settings

logger = logging.getLogger(__name__)


class NotificationInput(BaseModel):
    """Input schema for the Backstage notification tool."""
    
    notification_data: str = Field(
        description="JSON string containing title, message, severity, and optional metadata"
    )


class BackstageNotificationTool(BaseTool):
    """Tool for sending notifications to Backstage Notification API."""
    
    name: str = "backstage_notification"
    description: str = (
        "Send notifications to Backstage when message routing failures are detected. "
        "Input should be a JSON string with keys: title, message, severity (optional), "
        "topic (optional), and metadata (optional). Example: "
        '{"title": "Alert", "message": "Issue found", "severity": "high"}'
    )
    args_schema: type[BaseModel] = NotificationInput
    
    def _run(self, notification_data: str) -> str:
        """Send a notification to Backstage."""
        try:
            # Parse the JSON input
            try:
                data = json.loads(notification_data)
            except json.JSONDecodeError:
                return f"Error: Invalid JSON format in notification_data: {notification_data}"
            
            # Extract required fields with defaults
            title = data.get("title", "AI Agent Notification")
            message = data.get("message", "")
            severity = data.get("severity", "normal")
            topic = data.get("topic", "ai-agent-alerts")
            metadata = data.get("metadata", {})
            
            notification_payload = {
                "title": title,
                "message": message,
                "severity": severity,
                "topic": topic,
                "source": settings.service_name,
                "timestamp": None,  # Will be set by the API
                "metadata": metadata
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.backstage_token}"
            }
            
            # Backstage Notification API endpoint
            url = f"{settings.backstage_api_url}/notifications"
            
            logger.info(f"Sending notification to Backstage: {title}")
            logger.debug(f"Notification payload: {notification_payload}")
            
            response = requests.post(
                url,
                headers=headers,
                json=notification_payload,
                timeout=30
            )
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Notification sent successfully: {response.status_code}")
                return f"Notification sent successfully to Backstage (status: {response.status_code})"
            else:
                error_msg = f"Failed to send notification: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return f"Error: {error_msg}"
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error sending notification: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        except Exception as e:
            error_msg = f"Unexpected error sending notification: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
    
    async def _arun(self, notification_data: str) -> str:
        """Async version of the notification tool."""
        # For now, we'll use the sync version
        # In production, consider using aiohttp for async requests
        return self._run(notification_data)


def create_backstage_notification_tool() -> BackstageNotificationTool:
    """Factory function to create the Backstage notification tool."""
    return BackstageNotificationTool() 