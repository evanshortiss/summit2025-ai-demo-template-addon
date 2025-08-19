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
    
    title: str = Field(
        description="The title of the notification"
    )
    description: str = Field(
        description="The detailed description/message content of the notification"
    )
    entity_ref: Optional[str] = Field(
        default=None,
        description="Optional entity reference to send the notification to (e.g. 'group:default/platform-team'). If not provided, uses the default configured recipient."
    )


class BackstageNotificationTool(BaseTool):
    """Tool for sending notifications to Backstage Notification API."""
    
    name: str = "send_backstage_notification"
    description: str = (
        "Send a notification to Backstage when you have completed your analysis of a message routing failure. "
        "Use this tool to notify the appropriate team about your findings and recommendations. "
        "Provide a clear title and detailed description of your analysis. "
        "Optionally specify an entity_ref (like 'group:default/team-name') to send to a specific team, or user"
        "otherwise it will use a default configured recipient."
    )
    args_schema: type[BaseModel] = NotificationInput
    
    def _run(self, title: str, description: str, entity_ref: Optional[str] = None) -> str:
        """Send a notification to Backstage."""
        return send_backstage_notification(title, description, entity_ref)
    
    async def _arun(self, title: str, description: str, entity_ref: Optional[str] = None) -> str:
        """Async version of the notification tool."""
        return self._run(title, description, entity_ref)


def create_backstage_notification_tool() -> BackstageNotificationTool:
    """Factory function to create the Backstage notification tool."""
    return BackstageNotificationTool()