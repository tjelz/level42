"""
Unit tests for tool registry and management system.
"""

import pytest
import tempfile
import os
from datetime import datetime
from unittest.mock import patch, Mock

from x402_agent.tools import Tool, ToolRegistry


class TestTool:
    """Test cases for Tool dataclass."""
    
    def test_tool_creation_valid(self):
        """Test creating a valid tool."""
        tool = Tool(
            name="test_api",
            endpoint="https://api.example.com",
            description="Test API",
            cost_per_call=0.01,
            payment_address="0x123"
        )
        
        assert tool.name == "test_api"
        assert tool.endpoint == "https://api.example.com"
        assert tool.description == "Test API"
        assert tool.cost_per_call == 0.01
        assert tool.payment_address == "0x123"
        assert isinstance(tool.parameters, dict)
        assert isinstance(tool.created_at, datetime)
    
    def test_tool_creation_with_parameters(self):
        """Test creating a tool with custom parameters."""
        parameters = {"api_key": {"required": True}, "format": {"required": False}}
        tool = Tool(
            name="test_api",
            endpoint="https://api.example.com",
            description="Test API",
            cost_per_call=0.01,
            payment_address="0x123",
            parameters=parameters
        )
        
        assert tool.parameters == parameters
    
    def test_tool_validation_empty_name(self):
        """Test tool validation fails with empty name."""
        with pytest.raises(ValueError, match="Tool name cannot be empty"):
            Tool(
                name="",
                endpoint="https://api.example.com",
                description="Test API",
                cost_per_call=0.01,
                payment_address="0x123"
            )
    
    def test_tool_validation_empty_endpoint(self):
        """Test tool validation fails with empty endpoint."""
        with pytest.raises(ValueError, match="Tool endpoint cannot be empty"):
            Tool(
                name="test_api",
                endpoint="",
                description="Test API",
                cost_per_call=0.01,
                payment_address="0x123"
            )
    
    def test_tool_validation_negative_cost(self):
        """Test tool validation fails with negative cost."""
        with pytest.raises(ValueError, match="Cost per call cannot be negative"):
            Tool(
                name="test_api",
                endpoint="https://api.example.com",
                description="Test API",
                cost_per_call=-0.01,
                payment_address="0x123"
            )
    
    def test_tool_validation_empty_payment_address(self):
        """Test tool validation fails with empty payment address."""
        with pytest.raises(ValueError, match="Payment address cannot be empty"):
            Tool(
                name="test_api",
                endpoint="https://api.example.com",
                description="Test API",
                cost_per_call=0.01,
                payment_address=""
            )


class TestToolRegistry:
    """Test cases for ToolRegistry class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Use temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        self.registry = ToolRegistry(db_path=self.temp_db.name)
        
        # Create test tool
        self.test_tool = Tool(
            name="test_api",
            endpoint="https://httpbin.org/get",  # Real endpoint for testing
            description="Test API for unit tests",
            cost_per_call=0.01,
            payment_address="0x123"
        )
    
    def teardown_method(self):
        """Clean up test fixtures."""
        try:
            os.unlink(self.temp_db.name)
        except OSError:
            pass
    
    def test_registry_initialization(self):
        """Test registry initializes correctly."""
        assert isinstance(self.registry.tools, dict)
        assert len(self.registry.tools) == 0
    
    @patch('requests.head')
    def test_register_tool_success(self, mock_head):
        """Test successful tool registration."""
        mock_head.return_value = Mock(status_code=200)
        
        self.registry.register_tool(self.test_tool)
        
        assert "test_api" in self.registry.tools
        assert self.registry.tools["test_api"] == self.test_tool
        mock_head.assert_called_once()
    
    @patch('requests.head')
    def test_register_tool_duplicate_name(self, mock_head):
        """Test registration fails with duplicate name."""
        mock_head.return_value = Mock(status_code=200)
        
        self.registry.register_tool(self.test_tool)
        
        with pytest.raises(ValueError, match="Tool 'test_api' already registered"):
            self.registry.register_tool(self.test_tool)
    
    def test_register_tool_invalid_endpoint(self):
        """Test registration fails with invalid endpoint."""
        invalid_tool = Tool(
            name="invalid_api",
            endpoint="not-a-valid-url",
            description="Invalid API",
            cost_per_call=0.01,
            payment_address="0x123"
        )
        
        with pytest.raises(ValueError, match="Invalid endpoint"):
            self.registry.register_tool(invalid_tool)
    
    @patch('requests.head')
    def test_get_tool_exists(self, mock_head):
        """Test retrieving existing tool."""
        mock_head.return_value = Mock(status_code=200)
        
        self.registry.register_tool(self.test_tool)
        retrieved_tool = self.registry.get_tool("test_api")
        
        assert retrieved_tool == self.test_tool
    
    def test_get_tool_not_exists(self):
        """Test retrieving non-existent tool returns None."""
        retrieved_tool = self.registry.get_tool("nonexistent")
        assert retrieved_tool is None
    
    @patch('requests.head')
    def test_discover_tools_by_name(self, mock_head):
        """Test tool discovery by name."""
        mock_head.return_value = Mock(status_code=200)
        
        # Register multiple tools
        tool1 = Tool("weather_api", "https://httpbin.org/get", "Weather data", 0.01, "0x123")
        tool2 = Tool("stock_api", "https://httpbin.org/get", "Stock prices", 0.02, "0x456")
        tool3 = Tool("news_api", "https://httpbin.org/get", "Weather news", 0.03, "0x789")
        
        self.registry.register_tool(tool1)
        self.registry.register_tool(tool2)
        self.registry.register_tool(tool3)
        
        # Search for "weather"
        results = self.registry.discover_tools("weather")
        
        assert len(results) == 2  # weather_api and news_api (contains "weather" in description)
        assert results[0].name == "weather_api"  # Exact name match should be first
    
    @patch('requests.head')
    def test_discover_tools_by_description(self, mock_head):
        """Test tool discovery by description."""
        mock_head.return_value = Mock(status_code=200)
        
        self.registry.register_tool(self.test_tool)
        results = self.registry.discover_tools("unit tests")
        
        assert len(results) == 1
        assert results[0] == self.test_tool
    
    def test_discover_tools_empty_query(self):
        """Test discovery with empty query returns all tools."""
        results = self.registry.discover_tools("")
        assert len(results) == 0  # No tools registered
        
        results = self.registry.discover_tools("   ")
        assert len(results) == 0
    
    @patch('requests.head')
    def test_list_all_tools(self, mock_head):
        """Test listing all registered tools."""
        mock_head.return_value = Mock(status_code=200)
        
        tool1 = Tool("api1", "https://httpbin.org/get", "API 1", 0.01, "0x123")
        tool2 = Tool("api2", "https://httpbin.org/get", "API 2", 0.02, "0x456")
        
        self.registry.register_tool(tool1)
        self.registry.register_tool(tool2)
        
        all_tools = self.registry.list_all_tools()
        
        assert len(all_tools) == 2
        assert tool1 in all_tools
        assert tool2 in all_tools
    
    @patch('requests.head')
    def test_remove_tool_exists(self, mock_head):
        """Test removing existing tool."""
        mock_head.return_value = Mock(status_code=200)
        
        self.registry.register_tool(self.test_tool)
        assert "test_api" in self.registry.tools
        
        result = self.registry.remove_tool("test_api")
        
        assert result is True
        assert "test_api" not in self.registry.tools
    
    def test_remove_tool_not_exists(self):
        """Test removing non-existent tool."""
        result = self.registry.remove_tool("nonexistent")
        assert result is False
    
    def test_validate_parameters_tool_not_found(self):
        """Test parameter validation with non-existent tool."""
        result = self.registry.validate_parameters("nonexistent", {})
        assert result is False
    
    @patch('requests.head')
    def test_validate_parameters_no_requirements(self, mock_head):
        """Test parameter validation with tool that has no parameter requirements."""
        mock_head.return_value = Mock(status_code=200)
        
        self.registry.register_tool(self.test_tool)
        result = self.registry.validate_parameters("test_api", {"any": "param"})
        
        assert result is True
    
    @patch('requests.head')
    def test_validate_parameters_with_requirements(self, mock_head):
        """Test parameter validation with required parameters."""
        mock_head.return_value = Mock(status_code=200)
        
        tool_with_params = Tool(
            name="param_api",
            endpoint="https://httpbin.org/get",
            description="API with parameters",
            cost_per_call=0.01,
            payment_address="0x123",
            parameters={
                "api_key": {"required": True},
                "format": {"required": False}
            }
        )
        
        self.registry.register_tool(tool_with_params)
        
        # Test with missing required parameter
        result = self.registry.validate_parameters("param_api", {"format": "json"})
        assert result is False
        
        # Test with all required parameters
        result = self.registry.validate_parameters("param_api", {"api_key": "test", "format": "json"})
        assert result is True
        
        # Test with only required parameter
        result = self.registry.validate_parameters("param_api", {"api_key": "test"})
        assert result is True


class TestToolRegistryPersistence:
    """Test cases for database persistence functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        try:
            os.unlink(self.temp_db.name)
        except OSError:
            pass
    
    @patch('requests.head')
    def test_persistence_save_and_load(self, mock_head):
        """Test that tools are persisted and loaded correctly."""
        mock_head.return_value = Mock(status_code=200)
        
        # Create registry and add tool
        registry1 = ToolRegistry(db_path=self.temp_db.name)
        test_tool = Tool(
            name="persistent_api",
            endpoint="https://httpbin.org/get",
            description="Persistent API",
            cost_per_call=0.05,
            payment_address="0xabc"
        )
        registry1.register_tool(test_tool)
        
        # Create new registry instance (simulates restart)
        registry2 = ToolRegistry(db_path=self.temp_db.name)
        
        # Check that tool was loaded
        assert "persistent_api" in registry2.tools
        loaded_tool = registry2.get_tool("persistent_api")
        assert loaded_tool.name == test_tool.name
        assert loaded_tool.endpoint == test_tool.endpoint
        assert loaded_tool.description == test_tool.description
        assert loaded_tool.cost_per_call == test_tool.cost_per_call
        assert loaded_tool.payment_address == test_tool.payment_address
    
    @patch('requests.head')
    def test_persistence_remove_tool(self, mock_head):
        """Test that removed tools are deleted from database."""
        mock_head.return_value = Mock(status_code=200)
        
        # Create registry and add tool
        registry1 = ToolRegistry(db_path=self.temp_db.name)
        test_tool = Tool(
            name="temp_api",
            endpoint="https://httpbin.org/get",
            description="Temporary API",
            cost_per_call=0.01,
            payment_address="0x123"
        )
        registry1.register_tool(test_tool)
        registry1.remove_tool("temp_api")
        
        # Create new registry instance
        registry2 = ToolRegistry(db_path=self.temp_db.name)
        
        # Check that tool was not loaded
        assert "temp_api" not in registry2.tools