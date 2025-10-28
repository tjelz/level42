# X402Agent API Reference

The `X402Agent` class is the main interface for creating autonomous AI agents with micropayment capabilities.

## Class Definition

```python
class X402Agent:
    """
    Autonomous AI agent with micropayment capabilities.
    
    The X402Agent can automatically pay for API access using cryptocurrency
    when encountering HTTP 402 Payment Required responses.
    """
```

## Constructor

### `__init__(llm, wallet_key, network="base", max_spend_per_hour=10.0)`

Initialize a new X402Agent instance.

**Parameters:**
- `llm` (Any): LangChain-compatible language model instance
- `wallet_key` (str): Private key for blockchain wallet (64 hex characters with 0x prefix)
- `network` (str, optional): Blockchain network to use. Defaults to "base"
- `max_spend_per_hour` (float, optional): Maximum spending limit in USDC per hour. Defaults to 10.0

**Raises:**
- `ValueError`: If wallet_key is invalid or network is unsupported
- `ConnectionError`: If unable to connect to blockchain network

**Example:**
```python
from x402_agent import X402Agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4")
agent = X402Agent(
    llm=llm,
    wallet_key="0x1234567890abcdef...",
    network="base",
    max_spend_per_hour=25.0
)
```

## Methods

### `register_tool(name, endpoint, description="")`

Register an external API as a tool that the agent can use.

**Parameters:**
- `name` (str): Unique identifier for the tool
- `endpoint` (str): API endpoint URL
- `description` (str, optional): Human-readable description of the tool

**Raises:**
- `ValueError`: If tool name already exists or endpoint is invalid
- `ConnectionError`: If endpoint is unreachable

**Example:**
```python
agent.register_tool(
    name="weather",
    endpoint="https://api.weather.com/v1/current",
    description="Get current weather data for any location"
)
```

### `run(prompt)`

Execute a task with automatic payment handling.

**Parameters:**
- `prompt` (str): Task description or question for the agent

**Returns:**
- `str`: Agent's response after completing the task

**Raises:**
- `InsufficientFundsError`: If wallet balance is too low
- `PaymentError`: If payment processing fails
- `NetworkError`: If blockchain network is unavailable

**Example:**
```python
result = agent.run("Get the current weather in San Francisco")
print(result)  # "The current weather in San Francisco is 72°F and sunny..."
```

### `get_balance()`

Get the current wallet balance in USDC.

**Returns:**
- `float`: Current balance in USDC

**Example:**
```python
balance = agent.get_balance()
print(f"Current balance: ${balance:.2f} USDC")
```

### `transfer_to_agent(agent_id, amount)`

Transfer funds to another agent in the same swarm.

**Parameters:**
- `agent_id` (str): Unique identifier of the recipient agent
- `amount` (float): Amount to transfer in USDC

**Returns:**
- `str`: Transaction hash of the transfer

**Raises:**
- `InsufficientFundsError`: If wallet balance is too low
- `ValueError`: If agent_id is invalid or amount is negative

**Example:**
```python
tx_hash = agent.transfer_to_agent("agent_2", 5.0)
print(f"Transfer completed: {tx_hash}")
```

### `get_spending_summary()`

Get a summary of agent spending and usage.

**Returns:**
- `dict`: Dictionary containing spending analytics

**Example:**
```python
summary = agent.get_spending_summary()
print(f"Total spent today: ${summary['today']:.2f}")
print(f"Most used tool: {summary['top_tool']}")
print(f"Average cost per call: ${summary['avg_cost']:.4f}")
```

### `export_transactions(start_date=None, end_date=None)`

Export transaction history for analysis.

**Parameters:**
- `start_date` (datetime, optional): Start date for export
- `end_date` (datetime, optional): End date for export

**Returns:**
- `List[dict]`: List of transaction records

**Example:**
```python
from datetime import datetime, timedelta

# Export last 7 days
start = datetime.now() - timedelta(days=7)
transactions = agent.export_transactions(start_date=start)

for tx in transactions:
    print(f"{tx['timestamp']}: ${tx['amount']} to {tx['tool_name']}")
```

## Properties

### `network`
Current blockchain network being used.

**Type:** `str`

### `tools`
Dictionary of registered tools.

**Type:** `Dict[str, Tool]`

### `wallet_manager`
Wallet manager instance for payment operations.

**Type:** `WalletManager`

### `payment_processor`
Payment processor for handling HTTP 402 responses.

**Type:** `PaymentProcessor`

## Events and Callbacks

### `add_payment_callback(callback)`

Add a callback function to be called on each payment.

**Parameters:**
- `callback` (Callable): Function to call with payment details

**Example:**
```python
def payment_alert(amount, tool_name, tx_hash):
    if amount > 1.0:
        print(f"High payment: ${amount} for {tool_name}")

agent.add_payment_callback(payment_alert)
```

### `add_error_callback(callback)`

Add a callback function to be called on payment errors.

**Parameters:**
- `callback` (Callable): Function to call with error details

**Example:**
```python
def error_handler(error, context):
    print(f"Payment error: {error} in {context}")
    # Send alert to monitoring system

agent.add_error_callback(error_handler)
```

## Configuration

### Environment Variables

The agent respects the following environment variables:

- `X402_DEFAULT_NETWORK`: Default blockchain network
- `X402_MAX_SPEND_PER_HOUR`: Default spending limit
- `X402_DEBUG`: Enable debug logging

### Configuration File

Agents can be configured using a YAML file at `~/.x402/config.yaml`:

```yaml
default_network: base
max_spend_per_hour: 10.0
deferred_payment_threshold: 10
networks:
  base:
    rpc_url: "https://mainnet.base.org"
    usdc_contract: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
```

## Error Handling

The X402Agent class raises specific exceptions for different error conditions:

### `InsufficientFundsError`
Raised when the wallet doesn't have enough balance for a payment.

### `PaymentError`
Raised when payment processing fails due to network or validation issues.

### `NetworkError`
Raised when unable to connect to the blockchain network.

### `ToolError`
Raised when tool registration or execution fails.

## Thread Safety

The X402Agent class is thread-safe for read operations but not for concurrent modifications. If you need to use an agent across multiple threads, consider using appropriate locking mechanisms.

## Performance Considerations

- **Payment Batching**: Use deferred payments for high-frequency API calls
- **Connection Pooling**: Reuse HTTP connections for better performance
- **Caching**: Tool metadata is cached to reduce lookup times
- **Async Support**: Consider using async variants for I/O intensive operations