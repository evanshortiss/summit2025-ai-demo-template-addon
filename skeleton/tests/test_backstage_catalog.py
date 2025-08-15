"""Tests for the Backstage Catalog API tool."""

import pytest
from unittest.mock import Mock, patch
import requests
from src.tools.backstage_catalog import BackstageCatalogTool, create_backstage_catalog_tool


class TestBackstageCatalogTool:
    """Test cases for BackstageCatalogTool."""
    
    def test_create_tool(self):
        """Test tool creation."""
        tool = create_backstage_catalog_tool()
        
        assert isinstance(tool, BackstageCatalogTool)
        assert tool.name == "backstage_catalog_groups"
        assert "Backstage Catalog" in tool.description
    
    @patch('src.tools.backstage_catalog.requests.get')
    def test_successful_groups_lookup(self, mock_get):
        """Test successful groups lookup."""
        # Mock successful response with sample groups
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "kind": "Group",
                "metadata": {
                    "name": "platform-team",
                    "namespace": "default",
                    "title": "Platform Team",
                    "description": "Platform engineering team"
                },
                "spec": {
                    "type": "team",
                    "parent": "engineering",
                    "children": [],
                    "members": ["user:alice", "user:bob"]
                }
            },
            {
                "kind": "Group",
                "metadata": {
                    "name": "frontend-team",
                    "namespace": "default",
                    "title": "Frontend Team"
                },
                "spec": {
                    "type": "team",
                    "members": ["user:charlie"]
                }
            }
        ]
        mock_get.return_value = mock_response
        
        tool = BackstageCatalogTool()
        result = tool._run()
        
        assert "Found 2 group(s)" in result
        assert "Platform Team" in result
        assert "Frontend Team" in result
        assert "group:default/platform-team" in result
        assert "group:default/frontend-team" in result
        mock_get.assert_called_once()
    
    @patch('src.tools.backstage_catalog.requests.get')
    def test_groups_lookup_with_query(self, mock_get):
        """Test groups lookup with query filter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "kind": "Group",
                "metadata": {
                    "name": "platform-team",
                    "namespace": "default",
                    "title": "Platform Team"
                },
                "spec": {
                    "type": "team"
                }
            }
        ]
        mock_get.return_value = mock_response
        
        tool = BackstageCatalogTool()
        result = tool._run(query="platform")
        
        assert "Found 1 group(s)" in result
        assert "Platform Team" in result
        assert "group:default/platform-team" in result
        
        # Verify the API call included the query filter
        call_args = mock_get.call_args
        assert "metadata.name=platform" in call_args[1]['params']['filter']
    
    @patch('src.tools.backstage_catalog.requests.get')
    def test_no_groups_found(self, mock_get):
        """Test when no groups are found."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        tool = BackstageCatalogTool()
        result = tool._run()
        
        assert "No groups found" in result
        mock_get.assert_called_once()
    
    @patch('src.tools.backstage_catalog.requests.get')
    def test_api_error_response(self, mock_get):
        """Test API error response handling."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response
        
        tool = BackstageCatalogTool()
        result = tool._run()
        
        assert "Error:" in result
        assert "401" in result
        assert "Unauthorized" in result
        mock_get.assert_called_once()
    
    @patch('src.tools.backstage_catalog.requests.get')
    def test_network_error(self, mock_get):
        """Test network error handling."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")
        
        tool = BackstageCatalogTool()
        result = tool._run()
        
        assert "Error:" in result
        assert "Network error" in result
    
    @patch('src.tools.backstage_catalog.requests.get')
    def test_api_request_structure(self, mock_get):
        """Test that API request has correct structure."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        tool = BackstageCatalogTool()
        tool._run()
        
        # Verify the API call structure
        call_args = mock_get.call_args
        
        # Check URL
        assert "/catalog/entities" in call_args[0][0]
        
        # Check headers
        headers = call_args[1]['headers']
        assert 'Authorization' in headers
        assert headers['Authorization'].startswith('Bearer ')
        assert headers['Content-Type'] == 'application/json'
        
        # Check parameters
        params = call_args[1]['params']
        assert 'filter' in params
        assert 'kind=group' in params['filter']
    
    @patch('src.tools.backstage_catalog.requests.get')
    def test_group_data_parsing(self, mock_get):
        """Test that group data is parsed correctly."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "kind": "Group",
                "metadata": {
                    "name": "test-group",
                    "namespace": "custom",
                    "title": "Test Group",
                    "description": "A test group"
                },
                "spec": {
                    "type": "team",
                    "parent": "parent-group",
                    "children": ["child1", "child2"],
                    "members": ["user1", "user2", "user3"]
                }
            }
        ]
        mock_get.return_value = mock_response
        
        tool = BackstageCatalogTool()
        result = tool._run()
        
        # Check that simplified group information is included
        assert "Test Group" in result
        assert "group:custom/test-group" in result  # entity reference with custom namespace
