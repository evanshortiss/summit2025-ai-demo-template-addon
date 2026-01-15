"""Backstage notification tool for LangChain agents."""

import json
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain.tools import BaseTool

from .backstage_notification import send_backstage_notification

logger = logging.getLogger(__name__)


class NotificationInput(BaseModel):
    """Input schema for the Backstage notification tool."""
    
    notification_data: str = Field(
        description="JSON string containing notification data with fields: title (required) and description (required). Example: '{\"title\": \"Alert\", \"description\": \"Issue found\"}'"
    )


class BackstageNotificationTool(BaseTool):
    """Tool for sending notifications to Backstage Notification API."""
    
    name: str = "send_backstage_notification"
    description: str = (
        "Send a notification to Backstage when you have completed your analysis of a message routing failure. "
        "Input should be a JSON string with 'title' (required) and 'description' (required)"
        "Example: {{\"title\": \"Routing Issue Found\", \"description\": \"Details...\"}}"
    )
    args_schema: type[BaseModel] = NotificationInput
    
    def _run(self, notification_data: str) -> str:
        """Send a notification to Backstage."""
        try:
            logger.info(f"Notification tool invoked with input str: {notification_data}")

            # Parse the JSON input
            data = json.loads(notification_data)
            title = data.get('title', '')
            description = data.get('description', '')
            
            if not title:
                return "Error: title is required"
            if not description:
                return "Error: description is required"
            
            result = send_backstage_notification(title, description)
            logger.info(f"Notification sent successfully: {title}")
            return result
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse notification data JSON: {str(e)}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Failed to send notification: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    async def _arun(self, notification_data: str) -> str:
        """Async version of the notification tool."""
        return self._run(notification_data)


def create_backstage_notification_tool() -> BackstageNotificationTool:
    """Factory function to create the Backstage notification tool."""
    return BackstageNotificationTool()