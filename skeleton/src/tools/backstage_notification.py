"""Backstage notification utility for sending notifications."""

import json
import logging
from typing import Dict, Any, Optional
import requests

from ..config import settings

logger = logging.getLogger(__name__)


def send_backstage_notification(title: str, description: str) -> str:
    """Send a notification to Backstage Notification API.
    
    Args:
        title: The notification title
        description: The notification description/message
        
    Returns:
        str: Success or error message
    """
    try:
        # Use provided entity_ref or fall back to settings default
        recipient_entity = settings.notification_recipient_entity
        
        # Format according to Backstage Notifications API
        notification_payload = {
            "payload": {
                "title": title,
                "description": description
            },
            "recipients": {
                "type": "entity",
                "entityRef": recipient_entity
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.backstage_token}"
        }
        
        # Backstage Notification API endpoint
        url = f"{settings.backstage_api_url}/notifications"
        
        logger.info(f"Sending notification to Backstage: {title} -> {recipient_entity}")
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


 