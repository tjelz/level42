"""
Tool registry and management system.

This module provides tool registration, discovery, and validation
for external APIs and services.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import requests
import sqlite3
import os
from urllib.parse import urlparse


@dataclass
class Tool:
    """Represents an external API tool that can be used by agents."""
    name: str
    endpoint: str
    description: str
    cost_per_call: float
    payment_address: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate tool data after creation."""
        if not self.name or not self.name.strip():
            raise ValueError("Tool name cannot be empty")
        if not self.endpoint or not self.endpoint.strip():
            raise ValueError("Tool endpoint cannot be empty")
        if self.cost_per_call < 0:
            raise ValueError("Cost per call cannot be negative")
        if not self.payment_address or not self.payment_address.strip():
            raise ValueError("Payment address cannot be empty")


class ToolRegistry:
    """
    Manages registration and discovery of external API tools.
    
    Provides a centralized registry for tools that agents can use,
    with validation and query capabilities.
    """
    
    def __init__(self, db_path: str = "tools.db"):
        """
        Initialize tool registry with optional database persistence.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.tools: Dict[str, Tool] = {}
        self.db_path = db_path
        self._init_database()
        self._load_tools_from_db()
    
    def register_tool(self, tool: Tool) -> None:
        """
        Add tool to registry with validation and persistence.
        
        Args:
            tool: Tool instance to register
            
        Raises:
            ValueError: If tool name already exists or validation fails
        """
        if tool.name in self.tools:
            raise ValueError(f"Tool '{tool.name}' already registered")
        
        # Validate tool endpoint
        if not self._validate_endpoint(tool.endpoint):
            raise ValueError(f"Invalid endpoint: {tool.endpoint}")
        
        # Store in memory and database
        self.tools[tool.name] = tool
        self._save_tool_to_db(tool)
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """
        Retrieve tool by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool instance or None if not found
        """
        return self.tools.get(name)
    
    def discover_tools(self, query: str) -> List[Tool]:
        """
        Find tools matching query with enhanced search capabilities.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching tools sorted by relevance
        """
        if not query or not query.strip():
            return list(self.tools.values())
        
        query_lower = query.lower()
        matching_tools = []
        
        for tool in self.tools.values():
            score = 0
            
            # Exact name match gets highest score
            if query_lower == tool.name.lower():
                score += 100
            # Name contains query
            elif query_lower in tool.name.lower():
                score += 50
            # Description contains query
            elif query_lower in tool.description.lower():
                score += 25
            # Endpoint contains query
            elif query_lower in tool.endpoint.lower():
                score += 10
            
            if score > 0:
                matching_tools.append((tool, score))
        
        # Sort by score (descending) and return tools
        matching_tools.sort(key=lambda x: x[1], reverse=True)
        return [tool for tool, _ in matching_tools]
    
    def list_all_tools(self) -> List[Tool]:
        """
        Get all registered tools.
        
        Returns:
            List of all tools
        """
        return list(self.tools.values())
    
    def remove_tool(self, name: str) -> bool:
        """
        Remove tool from registry and database.
        
        Args:
            name: Tool name to remove
            
        Returns:
            True if tool was removed, False if not found
        """
        if name in self.tools:
            del self.tools[name]
            self._remove_tool_from_db(name)
            return True
        return False
    
    def _validate_endpoint(self, endpoint: str) -> bool:
        """
        Validate tool endpoint by checking URL format and connectivity.
        
        Args:
            endpoint: Endpoint URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Parse URL to check format
            parsed = urlparse(endpoint)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            if parsed.scheme not in ('http', 'https'):
                return False
            
            # Test connectivity with a HEAD request (timeout 5 seconds)
            response = requests.head(endpoint, timeout=5)
            # Accept any response that doesn't indicate server error
            return response.status_code < 500
            
        except (requests.RequestException, ValueError):
            return False
    
    def validate_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> bool:
        """
        Validate parameters for a specific tool.
        
        Args:
            tool_name: Name of the tool
            parameters: Parameters to validate
            
        Returns:
            True if parameters are valid, False otherwise
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return False
        
        # Check if all required parameters are provided
        if tool.parameters:
            for param_name, param_config in tool.parameters.items():
                if isinstance(param_config, dict) and param_config.get('required', False):
                    if param_name not in parameters:
                        return False
        
        return True
    
    def _init_database(self):
        """Initialize SQLite database for tool persistence."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS registered_tools (
                        id INTEGER PRIMARY KEY,
                        name TEXT UNIQUE,
                        endpoint TEXT,
                        description TEXT,
                        cost_per_call REAL,
                        payment_address TEXT,
                        parameters TEXT,
                        created_at DATETIME
                    )
                ''')
                conn.commit()
        except sqlite3.Error:
            # If database fails, continue without persistence
            pass
    
    def _save_tool_to_db(self, tool: Tool):
        """Save tool to database."""
        try:
            import json
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO registered_tools 
                    (name, endpoint, description, cost_per_call, payment_address, parameters, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    tool.name,
                    tool.endpoint,
                    tool.description,
                    tool.cost_per_call,
                    tool.payment_address,
                    json.dumps(tool.parameters),
                    tool.created_at.isoformat()
                ))
                conn.commit()
        except (sqlite3.Error, ImportError):
            # If database fails, continue without persistence
            pass
    
    def _load_tools_from_db(self):
        """Load tools from database on initialization."""
        try:
            import json
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT * FROM registered_tools')
                for row in cursor.fetchall():
                    _, name, endpoint, description, cost_per_call, payment_address, parameters_json, created_at = row
                    
                    parameters = json.loads(parameters_json) if parameters_json else {}
                    created_at_dt = datetime.fromisoformat(created_at) if created_at else datetime.now()
                    
                    tool = Tool(
                        name=name,
                        endpoint=endpoint,
                        description=description,
                        cost_per_call=cost_per_call,
                        payment_address=payment_address,
                        parameters=parameters,
                        created_at=created_at_dt
                    )
                    self.tools[name] = tool
        except (sqlite3.Error, ImportError, ValueError):
            # If database fails, start with empty registry
            pass
    
    def _remove_tool_from_db(self, name: str):
        """Remove tool from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM registered_tools WHERE name = ?', (name,))
                conn.commit()
        except sqlite3.Error:
            # If database fails, continue
            pass