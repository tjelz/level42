# Level42 Framework Examples

This directory contains example implementations demonstrating the key features of the Level42 Framework.

## Prerequisites

1. Install the level42 framework:
   ```bash
   pip install -e .
   ```

2. Set up your wallet private key as an environment variable:
   ```bash
   export WALLET_PRIVATE_KEY="your_private_key_here"
   ```

## Examples

### 1. Simple Agent (`simple_agent.py`)

**Demonstrates:** Basic agent creation and tool registration

**Features:**
- One-line agent creation with LLM and wallet
- Tool registration for external APIs
- Automatic payment handling for API calls
- Basic balance checking

**Usage:**
```bash
python examples/simple_agent.py
```

**Requirements Covered:** 5.3, 5.4

### 2. Trading Bot (`trading_bot.py`)

**Demonstrates:** Advanced payment batching and portfolio management

**Features:**
- Deferred payment batching with multiple API calls
- Portfolio management and spending tracking
- Stock/crypto API integration
- Comprehensive spending analytics
- Multiple API calls per analysis session

**Usage:**
```bash
python examples/trading_bot.py
```

**Key Features:**
- Batches up to 10+ API calls before processing payments
- Tracks spending per trading session
- Demonstrates cost optimization through batching
- Portfolio tracking and management

**Requirements Covered:** 3.1, 3.2, 7.3

### 3. Multi-Agent Research Swarm (`research_swarm.py`)

**Demonstrates:** Collaborative multi-agent coordination

**Features:**
- Multiple specialized research agents
- Collaborative task execution with different strategies
- Cost-splitting for shared research tasks
- Agent-to-agent fund transfers
- Swarm-level coordination and communication
- Comprehensive analytics and reporting

**Usage:**
```bash
python examples/research_swarm.py
```

**Key Features:**
- 4 specialized research agents (data analysis, literature review, market research, technical research)
- Three collaboration strategies: parallel, sequential, and divided
- Automatic cost-splitting among agents
- Fund transfer demonstrations
- Detailed spending analytics per agent and tool

**Requirements Covered:** 4.1, 4.3, 4.4

## Example Output

### Simple Agent
```
🤖 Simple Level42 Agent created successfully!
💰 Current balance: $10.00 USDC
🔧 Weather API tool registered
🌤️  Agent response: Mock response to: What's the weather like in San Francisco?
💰 Balance after API call: $9.99 USDC
```

### Trading Bot
```
🚀 Starting trading bot session...
💰 Initial balance: $10.00 USDC
📊 Market Analysis Session 1
🔍 Analyzing AAPL...
💰 Analysis cost: $0.0040 USDC
📈 Processed 12 API calls
📋 Trading Session Summary:
💰 Final balance: $9.98 USDC
💸 Total spent: $0.0200 USDC
📞 Total API calls: 36
```

### Research Swarm
```
🚀 Starting Multi-Agent Research Session
🔬 Created data_analyst agent: Specializes in data analysis and statistics
🔬 Created literature_reviewer agent: Focuses on academic literature and sources
🔬 Created market_researcher agent: Analyzes market trends and consumer behavior
🔬 Created tech_researcher agent: Investigates technical implementations
🔍 Starting collaborative research on: Artificial Intelligence in Healthcare
💰 Total research cost: $0.0160 USDC
✅ Successful research projects: 3/3
💸 Total session cost: $0.0480 USDC
```

## Configuration

### Environment Variables

- `WALLET_PRIVATE_KEY`: Your blockchain wallet private key (required)

### Network Configuration

All examples default to the Base network. You can modify the network by changing the `network` parameter:

```python
agent = Level42Agent(llm, private_key, network="base")  # or "ethereum", "solana"
```

### Mock vs Real APIs

These examples use mock LLM providers for demonstration. In production:

1. Replace mock providers with real LLM providers (OpenAI, Anthropic, etc.)
2. Register real API endpoints that support HTTP 402 payments
3. Ensure sufficient wallet balance for actual payments

## Security Notes

- Never commit private keys to version control
- Use environment variables or secure key management
- Test with small amounts on testnets first
- Monitor spending and set appropriate limits

## Troubleshooting

### Common Issues

1. **"Please set WALLET_PRIVATE_KEY environment variable"**
   - Set the environment variable with your private key

2. **"Insufficient funds" errors**
   - Ensure your wallet has sufficient USDC balance
   - Check network connectivity

3. **Import errors**
   - Install the framework: `pip install -e .`
   - Ensure you're in the correct directory

### Getting Help

- Check the main README.md for installation instructions
- Review the requirements.md and design.md in `.kiro/specs/level42-framework/`
- Ensure all dependencies are installed from requirements.txt