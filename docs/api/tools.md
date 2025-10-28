# ToolRegistry API Reference

The `ToolRegistry` class manages registration, discovery, and execution of external APIs and tools for x402-Agent instances.

## Class Definition

```python
class ToolRegistry:
    """
    Manages external API tools and their registration for x402-Agent instances.
    
    Provides tool discovery, registration, validation, and execution capabilities
    with automatic payment handling for HTTP 402 responses.
    """
```

## Constructor

### `__init__(payment_processor=None)`

Initialize a new ToolRegistry instance.

**Parameters:**
- `payment_processor` (PaymentProcessor, optional): Payment processor for handling tool payments

**Example:**
```python
from x402_agent.tools import ToolRegistry
from x402_agent.payments import PaymentProcessor

registry = ToolRegistry(payment_processor=processor)
```

## Properties

### `tools`
Dictionary of registered tools, keyed by tool name.

**Type:** `Dict[str, Tool]`

### `payment_processor`
Payment processor instance for handling tool payments.

**Type:** `PaymentProcessor`

### `tool_categories`
Categories of registered tools for organization.

**Type:** `Dict[str, List[str]]`

## Methods

### `register_tool(name, endpoint, description="", category="general", **kwargs)`

Register a new external API tool.

**Parameters:**
- `name` (str): Unique identifier for the tool
- `endpoint` (str): API endpoint URL
- `description` (str, optional): Human-readable description of the tool
- `category` (str, optional): Tool category for organization. Defaults to "general"
- `**kwargs`: Additional tool configuration options

**Raises:**
- `ValueError`: If tool name already exists or endpoint is invalid
- `ToolRegistrationError`: If tool validation fails

**Example:**
```python
registry.register_tool(
    name="weather_api",
    endpoint="https://api.weather.com/v1/current",
    description="Get current weather data for any location",
    category="data",
    method="GET",
    headers={"User-Agent": "x402-agent/1.0"},
    timeout=30
)
```

### `unregister_tool(name)`

Remove a tool from the registry.

**Parameters:**
- `name` (str): Name of the tool to remove

**Raises:**
- `ValueError`: If tool doesn't exist

**Example:**
```python
registry.unregister_tool("weather_api")
```

### `get_tool(name)`

Retrieve a registered tool by name.

**Parameters:**
- `name` (str): Name of the tool to retrieve

**Returns:**
- `Tool`: The requested tool object

**Raises:**
- `ValueError`: If tool doesn't exist

**Example:**
```python
weather_tool = registry.get_tool("weather_api")
print(f"Tool endpoint: {weather_tool.endpoint}")
```

### `list_tools(category=None)`

List all registered tools, optionally filtered by category.

**Parameters:**
- `category` (str, optional): Filter by tool category

**Returns:**
- `List[Tool]`: List of matching tools

**Example:**
```python
# List all tools
all_tools = registry.list_tools()

# List only data tools
data_tools = registry.list_tools(category="data")
for tool in data_tools:
    print(f"{tool.name}: {tool.description}")
```

### `execute_tool(name, **kwargs)`

Execute a registered tool with automatic payment handling.

**Parameters:**
- `name` (str): Name of the tool to execute
- `**kwargs`: Parameters to pass to the tool

**Returns:**
- `ToolResult`: Result of the tool execution

**Raises:**
- `ToolExecutionError`: If tool execution fails
- `PaymentError`: If payment processing fails

**Example:**
```python
result = registry.execute_tool(
    name="weather_api",
    location="San Francisco",
    units="fahrenheit"
)

if result.success:
    print(f"Weather data: {result.data}")
else:
    print(f"Error: {result.error}")
```

### `discover_tools(endpoint_list)`

Automatically discover and register tools from a list of endpoints.

**Parameters:**
- `endpoint_list` (List[str]): List of API endpoints to check

**Returns:**
- `List[Tool]`: List of successfully discovered tools

**Example:**
```python
endpoints = [
    "https://api.weather.com/v1/current",
    "https://api.stocks.com/v1/price",
    "https://api.news.com/v1/headlines"
]

discovered = registry.discover_tools(endpoints)
print(f"Discovered {len(discovered)} tools")
```

### `validate_tool(tool)`

Validate a tool's configuration and endpoint accessibility.

**Parameters:**
- `tool` (Tool): Tool object to validate

**Returns:**
- `bool`: True if tool is valid and accessible

**Raises:**
- `ToolValidationError`: If validation fails

**Example:**
```python
weather_tool = registry.get_tool("weather_api")
is_valid = registry.validate_tool(weather_tool)
print(f"Tool is valid: {is_valid}")
```

### `get_tool_usage_stats(name=None)`

Get usage statistics for tools.

**Parameters:**
- `name` (str, optional): Specific tool name. Returns stats for all tools if None

**Returns:**
- `dict`: Usage statistics

**Example:**
```python
# Get stats for specific tool
weather_stats = registry.get_tool_usage_stats("weather_api")
print(f"Total calls: {weather_stats['total_calls']}")
print(f"Success rate: {weather_stats['success_rate']:.2%}")

# Get stats for all tools
all_stats = registry.get_tool_usage_stats()
for tool_name, stats in all_stats.items():
    print(f"{tool_name}: {stats['total_calls']} calls")
```

## Tool Object

### Tool Class Definition

```python
@dataclass
class Tool:
    """Represents an external API tool."""
    name: str
    endpoint: str
    description: str = ""
    category: str = "general"
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    retry_attempts: int = 3
    cost_per_call: float = 0.0
    requires_auth: bool = False
    auth_type: str = "none"  # "none", "api_key", "bearer", "oauth"
    parameters: Dict[str, Any] = field(default_factory=dict)
    response_format: str = "json"
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    usage_count: int = 0
    success_count: int = 0
```

### Tool Configuration Options

```python
# Basic tool registration
registry.register_tool(
    name="simple_api",
    endpoint="https://api.example.com/data"
)

# Advanced tool registration
registry.register_tool(
    name="advanced_api",
    endpoint="https://api.example.com/v2/data",
    description="Advanced data API with authentication",
    category="data",
    method="POST",
    headers={
        "Content-Type": "application/json",
        "User-Agent": "x402-agent/1.0"
    },
    timeout=60,
    retry_attempts=5,
    requires_auth=True,
    auth_type="api_key",
    parameters={
        "format": "json",
        "version": "2.0"
    }
)
```

## Tool Categories

### Predefined Categories

- `"data"`: Data collection and retrieval APIs
- `"analysis"`: Data analysis and processing tools
- `"communication"`: Messaging and notification services
- `"finance"`: Financial data and trading APIs
- `"ai"`: AI and machine learning services
- `"utility"`: General utility and helper tools
- `"monitoring"`: System monitoring and alerting tools

### Custom Categories

```python
# Register tool with custom category
registry.register_tool(
    name="custom_tool",
    endpoint="https://api.custom.com/v1/data",
    category="custom_category"
)

# List tools by custom category
custom_tools = registry.list_tools(category="custom_category")
```

## Tool Discovery

### Automatic Discovery

```python
# Discover tools from endpoint list
endpoints = [
    "https://api.weather.com",
    "https://api.stocks.com",
    "https://api.news.com"
]

discovered_tools = registry.discover_tools(endpoints)
for tool in discovered_tools:
    print(f"Discovered: {tool.name} - {tool.description}")
```

### Discovery Configuration

```python
# Configure discovery settings
registry.configure_discovery({
    "timeout": 10,
    "follow_redirects": True,
    "check_payment_support": True,
    "validate_ssl": True
})
```

## Authentication Support

### API Key Authentication

```python
registry.register_tool(
    name="api_key_tool",
    endpoint="https://api.example.com/data",
    requires_auth=True,
    auth_type="api_key",
    auth_config={
        "header_name": "X-API-Key",
        "key": "your_api_key_here"
    }
)
```

### Bearer Token Authentication

```python
registry.register_tool(
    name="bearer_token_tool",
    endpoint="https://api.example.com/data",
    requires_auth=True,
    auth_type="bearer",
    auth_config={
        "token": "your_bearer_token_here"
    }
)
```

### OAuth Authentication

```python
registry.register_tool(
    name="oauth_tool",
    endpoint="https://api.example.com/data",
    requires_auth=True,
    auth_type="oauth",
    auth_config={
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
        "token_url": "https://api.example.com/oauth/token"
    }
)
```

## Error Handling

### Tool Errors

#### `ToolRegistrationError`
Raised when tool registration fails.

```python
try:
    registry.register_tool("invalid_tool", "not_a_url")
except ToolRegistrationError as e:
    print(f"Registration failed: {e}")
```

#### `ToolExecutionError`
Raised when tool execution fails.

```python
try:
    result = registry.execute_tool("weather_api", location="Invalid")
except ToolExecutionError as e:
    print(f"Execution failed: {e}")
```

#### `ToolValidationError`
Raised when tool validation fails.

```python
try:
    registry.validate_tool(invalid_tool)
except ToolValidationError as e:
    print(f"Validation failed: {e}")
```

## Monitoring and Analytics

### Tool Performance Monitoring

```python
def tool_monitor(tool_name, execution_time, success):
    print(f"Tool {tool_name}: {execution_time:.2f}s, Success: {success}")

registry.add_execution_callback(tool_monitor)
```

### Usage Analytics

```python
analytics = registry.get_analytics()
print(f"Total tool executions: {analytics['total_executions']}")
print(f"Average execution time: {analytics['avg_execution_time']:.2f}s")
print(f"Most used tool: {analytics['most_used_tool']}")
print(f"Success rate: {analytics['success_rate']:.2%}")
```

### Cost Tracking

```python
cost_summary = registry.get_cost_summary()
print(f"Total tool costs: ${cost_summary['total_cost']:.2f}")
print(f"Most expensive tool: {cost_summary['most_expensive']}")
print(f"Average cost per execution: ${cost_summary['avg_cost']:.4f}")
```

## Configuration

### Registry Configuration

```python
registry.configure({
    "default_timeout": 30,
    "default_retry_attempts": 3,
    "enable_caching": True,
    "cache_ttl": 300,  # 5 minutes
    "enable_analytics": True,
    "max_concurrent_executions": 10
})
```

### Tool Caching

```python
# Enable response caching for specific tools
registry.enable_caching("weather_api", ttl=600)  # 10 minutes

# Disable caching
registry.disable_caching("weather_api")

# Clear cache
registry.clear_cache("weather_api")
```

## Best Practices

1. **Tool Organization**: Use categories to organize tools logically
2. **Error Handling**: Always handle tool execution errors gracefully
3. **Authentication**: Secure API keys and tokens properly
4. **Monitoring**: Track tool usage and performance
5. **Validation**: Validate tools before registration
6. **Caching**: Use caching for frequently accessed data

## Examples

### Basic Tool Registration and Usage

```python
from x402_agent.tools import ToolRegistry

# Create registry
registry = ToolRegistry()

# Register a simple tool
registry.register_tool(
    name="weather",
    endpoint="https://api.weather.com/v1/current",
    description="Get current weather data"
)

# Execute the tool
result = registry.execute_tool("weather", location="New York")
if result.success:
    print(f"Weather: {result.data}")
```

### Advanced Tool Management

```python
# Register multiple tools with different configurations
tools_config = [
    {
        "name": "stock_price",
        "endpoint": "https://api.stocks.com/v1/price",
        "category": "finance",
        "method": "GET",
        "timeout": 15
    },
    {
        "name": "news_headlines",
        "endpoint": "https://api.news.com/v1/headlines",
        "category": "data",
        "method": "GET",
        "requires_auth": True,
        "auth_type": "api_key"
    }
]

for config in tools_config:
    registry.register_tool(**config)

# Get usage statistics
stats = registry.get_tool_usage_stats()
for tool_name, tool_stats in stats.items():
    print(f"{tool_name}: {tool_stats['usage_count']} uses")
```

### Tool Discovery and Validation

```python
# Discover tools from multiple endpoints
endpoints = [
    "https://api.weather.com",
    "https://api.finance.com",
    "https://api.news.com"
]

discovered = registry.discover_tools(endpoints)
print(f"Discovered {len(discovered)} tools")

# Validate all registered tools
for tool_name in registry.tools:
    tool = registry.get_tool(tool_name)
    is_valid = registry.validate_tool(tool)
    print(f"{tool_name}: {'Valid' if is_valid else 'Invalid'}")
```