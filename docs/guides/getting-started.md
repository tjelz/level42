# Getting Started with x402-Agent Framework

This guide will walk you through setting up and using the x402-Agent Framework for the first time.

## Prerequisites

Before you begin, ensure you have:

- Python 3.8 or higher
- A cryptocurrency wallet with USDC on Base Network
- Basic familiarity with Python and APIs
- An LLM provider (OpenAI, Anthropic, etc.)

## Installation

### 1. Install the Framework

```bash
# Basic installation
pip install x402-agent

# With optional dependencies
pip install x402-agent[solana,dev]
```

### 2. Verify Installation

```python
import x402_agent
print(f"x402-Agent version: {x402_agent.__version__}")
```

## Quick Setup

### 1. Prepare Your Wallet

You'll need a cryptocurrency wallet with USDC on Base Network:

```python
# Example wallet setup (use your own private key)
WALLET_PRIVATE_KEY = "0x1234567890abcdef..."  # Your actual private key
```

**Security Note**: Never hardcode private keys in production. Use environment variables or secure key management.

### 2. Set Up Environment Variables

```bash
# Create .env file
echo "WALLET_PRIVATE_KEY=your_private_key_here" > .env
echo "OPENAI_API_KEY=your_openai_key_here" >> .env
```

### 3. Fund Your Wallet

Ensure your wallet has:
- USDC for API payments (start with $10-20)
- ETH for gas fees on Base Network (0.001-0.01 ETH)

You can bridge funds to Base Network at: https://bridge.base.org

## Your First Agent

### 1. Create a Simple Agent

```python
import os
from x402_agent import X402Agent
from langchain_openai import ChatOpenAI

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4",
    api_key=os.getenv("OPENAI_API_KEY")
)

# Create agent
agent = X402Agent(
    llm=llm,
    wallet_key=os.getenv("WALLET_PRIVATE_KEY"),
    network="base",
    max_spend_per_hour=10.0
)

print(f"Agent created! Wallet address: {agent.wallet_manager.address}")
print(f"Current balance: ${agent.get_balance():.2f} USDC")
```

### 2. Register Your First Tool

```python
# Register a weather API tool
agent.register_tool(
    name="weather",
    endpoint="https://api.weather.com/v1/current",
    description="Get current weather data for any location"
)

print("Weather tool registered successfully!")
```

### 3. Run Your First Task

```python
# Execute a task that uses the weather tool
result = agent.run("What's the current weather in San Francisco?")
print(f"Agent response: {result}")

# Check balance after the API call
new_balance = agent.get_balance()
print(f"Balance after API call: ${new_balance:.2f} USDC")
```

## Understanding the Workflow

### 1. How Payments Work

When your agent encounters an HTTP 402 response:

1. **Detection**: Agent detects payment requirement
2. **Validation**: Payment details are validated
3. **Authorization**: Spending limits are checked
4. **Payment**: USDC is sent to the API provider
5. **Retry**: Original API call is retried with payment proof
6. **Response**: API returns the requested data

### 2. Payment Flow Example

```python
# This happens automatically when you run a task
response = agent.run("Get stock price for AAPL")

# Behind the scenes:
# 1. Agent calls stock API
# 2. API returns 402 Payment Required
# 3. Agent processes payment (e.g., $0.01 USDC)
# 4. Agent retries API call with payment proof
# 5. API returns stock data
# 6. Agent processes and returns result
```

## Configuration Options

### 1. Spending Limits

```python
# Set conservative spending limits
agent = X402Agent(
    llm=llm,
    wallet_key=private_key,
    max_spend_per_hour=5.0,  # $5 per hour limit
    max_spend_per_day=25.0   # $25 per day limit
)
```

### 2. Network Selection

```python
# Use different networks
base_agent = X402Agent(llm, private_key, network="base")
solana_agent = X402Agent(llm, private_key, network="solana")
```

### 3. Custom Configuration

```python
# Advanced configuration
agent = X402Agent(
    llm=llm,
    wallet_key=private_key,
    network="base",
    config={
        "payment_timeout": 30,
        "retry_attempts": 3,
        "enable_batching": True,
        "batch_threshold": 10
    }
)
```

## Common Use Cases

### 1. Data Collection Agent

```python
# Create a data collection agent
data_agent = X402Agent(llm, private_key, network="base")

# Register multiple data sources
data_sources = [
    ("weather", "https://api.weather.com/v1/current", "Weather data"),
    ("stocks", "https://api.stocks.com/v1/price", "Stock prices"),
    ("news", "https://api.news.com/v1/headlines", "News headlines")
]

for name, endpoint, description in data_sources:
    data_agent.register_tool(name, endpoint, description)

# Collect data from multiple sources
result = data_agent.run("""
Collect the following data:
1. Current weather in New York
2. Stock price for AAPL
3. Latest tech news headlines
""")
```

### 2. Research Assistant

```python
# Create a research assistant
research_agent = X402Agent(llm, private_key, network="base")

# Register research tools
research_agent.register_tool("arxiv", "https://api.arxiv.org/search", "Academic papers")
research_agent.register_tool("patents", "https://api.patents.com/search", "Patent database")
research_agent.register_tool("market", "https://api.market.com/research", "Market research")

# Conduct research
result = research_agent.run("""
Research the latest developments in quantum computing:
1. Find recent academic papers
2. Check for new patents
3. Analyze market trends
""")
```

### 3. Trading Assistant

```python
# Create a trading assistant with higher spending limits
trading_agent = X402Agent(
    llm=llm,
    wallet_key=private_key,
    network="base",
    max_spend_per_hour=50.0  # Higher limit for trading
)

# Register financial data tools
trading_agent.register_tool("prices", "https://api.finance.com/prices", "Real-time prices")
trading_agent.register_tool("analysis", "https://api.finance.com/analysis", "Technical analysis")
trading_agent.register_tool("news", "https://api.finance.com/news", "Financial news")

# Analyze market conditions
result = trading_agent.run("""
Analyze current market conditions for Bitcoin:
1. Get current price and volume
2. Perform technical analysis
3. Check recent news sentiment
4. Provide trading recommendation
""")
```

## Monitoring and Analytics

### 1. Basic Monitoring

```python
# Check spending and usage
balance = agent.get_balance()
summary = agent.get_spending_summary()

print(f"Current balance: ${balance:.2f}")
print(f"Spent today: ${summary['today']:.2f}")
print(f"Most used tool: {summary['top_tool']}")
```

### 2. Advanced Monitoring

```python
from x402_agent.monitoring import AgentMonitor

# Set up monitoring
monitor = AgentMonitor(agent_id="my_agent")

# Configure alerts
monitor.set_alert_threshold("hourly_spending", 10.0)
monitor.add_alert_callback(lambda alert: print(f"Alert: {alert}"))

# Get detailed analytics
analytics = monitor.get_spending_analytics(period="7d")
performance = monitor.get_performance_metrics()

print(f"7-day spending: ${analytics['total_amount']:.2f}")
print(f"Success rate: {performance['success_rate']:.2%}")
```

## Error Handling

### 1. Common Errors and Solutions

```python
from x402_agent.exceptions import InsufficientFundsError, PaymentError

try:
    result = agent.run("Expensive API call")
except InsufficientFundsError:
    print("Need to add more USDC to wallet")
    print(f"Current balance: ${agent.get_balance():.2f}")
except PaymentError as e:
    print(f"Payment failed: {e}")
    # Check network connectivity, gas fees, etc.
```

### 2. Graceful Error Handling

```python
def safe_agent_run(agent, task, max_retries=3):
    """Safely run agent task with retries."""
    for attempt in range(max_retries):
        try:
            return agent.run(task)
        except InsufficientFundsError:
            print(f"Insufficient funds. Current balance: ${agent.get_balance():.2f}")
            return None
        except PaymentError as e:
            print(f"Payment error (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                return None
            time.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    return None

# Use the safe wrapper
result = safe_agent_run(agent, "Get weather data")
if result:
    print(f"Success: {result}")
else:
    print("Task failed after retries")
```

## Best Practices

### 1. Security

```python
# ✅ Good: Use environment variables
private_key = os.getenv("WALLET_PRIVATE_KEY")

# ❌ Bad: Hardcode private keys
private_key = "0x1234..."  # Never do this!

# ✅ Good: Validate private key format
if not private_key or len(private_key) != 66:
    raise ValueError("Invalid private key format")
```

### 2. Cost Management

```python
# Set appropriate spending limits
agent = X402Agent(
    llm=llm,
    wallet_key=private_key,
    max_spend_per_hour=10.0,    # Conservative limit
    max_spend_per_day=50.0      # Daily budget
)

# Monitor spending regularly
def check_spending():
    summary = agent.get_spending_summary()
    if summary['today'] > 20.0:  # Alert threshold
        print(f"High spending alert: ${summary['today']:.2f} today")

# Check before expensive operations
if agent.get_balance() < 5.0:
    print("Low balance warning")
```

### 3. Tool Management

```python
# Organize tools by category
categories = {
    "data": [
        ("weather", "https://api.weather.com/v1/current"),
        ("stocks", "https://api.stocks.com/v1/price")
    ],
    "analysis": [
        ("sentiment", "https://api.sentiment.com/analyze"),
        ("trends", "https://api.trends.com/analyze")
    ]
}

for category, tools in categories.items():
    for name, endpoint in tools:
        agent.register_tool(name, endpoint, category=category)
```

## Troubleshooting

### 1. Connection Issues

```python
# Test network connectivity
try:
    balance = agent.get_balance()
    print(f"Network OK. Balance: ${balance:.2f}")
except Exception as e:
    print(f"Network issue: {e}")
    # Check RPC endpoints, internet connection
```

### 2. Payment Issues

```python
# Debug payment problems
def debug_payment_issue(agent):
    print(f"Wallet address: {agent.wallet_manager.address}")
    print(f"Network: {agent.network}")
    print(f"Balance: ${agent.get_balance():.2f} USDC")
    
    # Check native token for gas
    native_balance = agent.wallet_manager.get_native_balance()
    print(f"Native balance: {native_balance:.6f} ETH")
    
    if native_balance < 0.001:
        print("Warning: Low ETH balance for gas fees")

debug_payment_issue(agent)
```

### 3. Tool Registration Issues

```python
# Validate tool endpoints
def validate_tool_endpoint(endpoint):
    import requests
    try:
        response = requests.head(endpoint, timeout=10)
        return response.status_code < 400
    except:
        return False

# Test before registration
endpoint = "https://api.example.com/data"
if validate_tool_endpoint(endpoint):
    agent.register_tool("example", endpoint)
else:
    print(f"Endpoint not accessible: {endpoint}")
```

## Next Steps

Now that you have a basic agent running:

1. **Explore Multi-Agent Swarms**: Learn about collaborative agents
2. **Advanced Payment Features**: Implement deferred payment batching
3. **Custom Tool Development**: Create your own API tools
4. **Production Deployment**: Set up monitoring and alerts
5. **Integration**: Connect with existing systems and workflows

### Recommended Reading

- [Multi-Agent Swarms Guide](./multi-agent-swarms.md)
- [Payment Optimization Guide](./payment-optimization.md)
- [Production Deployment Guide](./production-deployment.md)
- [API Reference](../api/agent.md)

### Community Resources

- [GitHub Repository](https://github.com/x402-agent/x402-agent-framework)
- [Discord Community](https://discord.gg/x402-agent)
- [Example Projects](../examples/)

## Support

If you encounter issues:

1. Check the [Troubleshooting Guide](./troubleshooting.md)
2. Search [GitHub Issues](https://github.com/x402-agent/x402-agent-framework/issues)
3. Ask in [Discord](https://discord.gg/x402-agent)
4. Create a new issue with detailed information

Welcome to the x402-Agent Framework community! 🚀