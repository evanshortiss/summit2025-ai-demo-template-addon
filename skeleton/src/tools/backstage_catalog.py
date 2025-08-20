"""Backstage Catalog API tool for LangChain agents."""

import json
import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import requests
from langchain.tools import BaseTool

from ..config import settings

logger = logging.getLogger(__name__)


class CatalogInput(BaseModel):
    """Input schema for the Backstage Catalog tool."""
    
    query: str = Field(
        default="",
        description="Not used - just list all groups (leave empty)"
    )


class BackstageCatalogTool(BaseTool):
    """Tool for querying the Backstage Catalog API to list Groups."""
    
    name: str = "backstage_catalog_groups"
    description: str = (
        "Look up and list all Groups from the Backstage Catalog API. "
        "This can help identify team structures and ownership for routing messages. "
        "Input is not used - just leave empty to get all groups."
    )
    args_schema: type[BaseModel] = CatalogInput
    
    def _run(self, query: str = "") -> str:
        """Query the Backstage Catalog API for Groups."""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.backstage_token}"
            }
            
            # Backstage Catalog API endpoint for entities
            url = f"{settings.backstage_api_url}/catalog/entities"
            
            # Parameters for filtering Groups
            params = {
                "filter": "kind=group"
            }
            
            logger.info("Querying Backstage Catalog for all Groups")
            
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                entities = response.json()
                groups = []
                
                for entity in entities:
                    if entity.get("kind") == "Group":
                        name = entity.get("metadata", {}).get("name", "")
                        namespace = entity.get("metadata", {}).get("namespace", "default")
                        display_name = entity.get("metadata", {}).get("title", "") or name
                        
                        # Create entity reference in the format: group:namespace/name
                        entity_ref = f"group:{namespace}/{name}"
                        
                        groups.append({
                            "entity_ref": entity_ref,
                            "display_name": display_name
                        })
                
                logger.info(f"Found {len(groups)} groups in Backstage Catalog")
                
                if not groups:
                    return "No groups found in the Backstage Catalog."
                
                # Format the response for the agent
                result = f"Found {len(groups)} group(s) in Backstage Catalog:\n\n"
                
                for group in groups:
                    result += f"- **{group['display_name']}** ({group['entity_ref']})\n"
                
                return result
                
            else:
                error_msg = f"Failed to query Backstage Catalog: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return f"Error: {error_msg}"
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error querying Backstage Catalog: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        except Exception as e:
            error_msg = f"Unexpected error querying Backstage Catalog: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
    
    async def _arun(self, query: str = "") -> str:
        """Async version of the catalog lookup tool."""
        # For now, we'll use the sync version
        # In production, consider using aiohttp for async requests
        return self._run(query)


def create_backstage_catalog_tool() -> BackstageCatalogTool:
    """Factory function to create the Backstage Catalog tool."""
    return BackstageCatalogTool()
