# Level42 Framework

[![PyPI version](https://badge.fury.io/py/level42.svg)](https://badge.fury.io/py/level42)
[![Python Support](https://img.shields.io/pypi/pyversions/level42.svg)](https://pypi.org/project/level42/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/tjelz/level42/workflows/CI/badge.svg)](https://github.com/tjelz/level42/actions)
[![codecov](https://codecov.io/gh/tjelz/level42/branch/main/graph/badge.svg)](https://codecov.io/gh/tjelz/level42)

A lightweight Python framework for building autonomous AI agents that can pay for tools, APIs, and other agents in real-time using L42 micropayments.

## 🚀 Overview

The Level42 Framework eliminates API key management and subscription friction by enabling pay-per-use interactions through HTTP 402 status codes and USDC payments on blockchain networks. Build agents that can autonomously discover, pay for, and use external services without manual intervention.

## ✨ Features

- **🤖 Autonomous Micropayments**: Agents automatically pay for API access using USDC
- **💳 HTTP 402 Integration**: Seamless handling of payment-required responses
- **🔗 Multi-Agent Swarms**: Collaborative agents with cost-splitting capabilities
- **📦 Deferred Payment Batching**: Efficient transaction batching to minimize gas costs
- **🌐 Multi-Blockchain Support**: Base Network primary, extensible to Solana and Ethereum
- **⚡ Simple Setup**: One-line agent creation with minimal configuration
- **🔍 Tool Discovery**: Automatic registration and discovery of paid APIs
- **📊 Spending Analytics**: Built-in tracking and reporting of agent expenses
- **🛡️ Secure Wallet Management**: Non-persistent private key handling

## 📦 Installation

### Basic Installation

```bash
pip install level42
```

### With Optional Dependencies

```bash
# Include Solana support
pip install level42[solana]

# Include development tools
pip install level42[dev]

# Include documentation tools
pip install level42[docs]

# Install everything
pip install level42[solana,dev,docs]
```

### Development Installation

```bash
git clone https://github.com/tjelz/level42.git
cd level42
pip install -e ".[dev]"
```

## 🚀 Quick Start

### Basic Agent

```python
from level42 import Level42Agent
from langchain_openai import ChatOpenAI

# Initialize your LLM
llm = ChatOpenAI(model="gpt-4")

# Create an agent with your wallet
agent = Level42Agent(
    llm=llm, 
    wallet_key="your_base_network_private_key"
)

# Register a paid API tool
agent.register_tool(
    name="weather",
    endpoint="https://api.weather.com/v1/current",
    description="Get current weather data"
)

# Run a task - payments handled automatically
result = agent.run("Get the current weather in San Francisco")
print(result)
```

### Multi-Agent Swarm

```python
from level42 import Level42Agent, AgentSwarm
from langchain_openai import ChatOpenAI

# Create multiple agents
llm = ChatOpenAI(model="gpt-4")
agent1 = Level42Agent(llm=llm, wallet_key="key1")
agent2 = Level42Agent(llm=llm, wallet_key="key2")

# Create a swarm with shared wallet
swarm = AgentSwarm(shared_wallet=True)
swarm.add_agent(agent1)
swarm.add_agent(agent2)

# Collaborate on a task with automatic cost splitting
result = swarm.collaborate("Research the latest AI developments and summarize findings")
```

### Deferred Payment Batching

```python
from level42 import Level42Agent, PaymentProcessor

agent = Level42Agent(llm=llm, wallet_key="your_key")

# Configure deferred payments (batches after 10 calls)
processor = PaymentProcessor(agent.wallet_manager)

# Make multiple API calls - payments batched automatically
for i in range(15):
    result = agent.run(f"API call {i}")
    # Payments processed in batch after 10th call
```

## 📚 Documentation

### Complete Documentation Available

Visit our comprehensive documentation at **[docs.level42.dev](https://docs.level42.dev)** for:

- **[Getting Started Guide](docs/guides/getting-started.md)** - Complete setup and first steps
- **[API Reference](docs/api/)** - Detailed API documentation for all classes
- **[Multi-Agent Swarms](docs/guides/multi-agent-swarms.md)** - Collaborative agent systems
- **[Production Deployment](docs/guides/production-deployment.md)** - Enterprise deployment guide
- **[Troubleshooting](docs/guides/troubleshooting.md)** - Common issues and solutions
- **[Examples](docs/examples/)** - Practical usage examples and tutorials

### Quick API Reference

#### Level42Agent - Main Agent Class

```python
from level42 import Level42Agent

agent = Level42Agent(
    llm=your_llm,                    # LangChain-compatible LLM
    wallet_key="0x...",              # Private key for payments
    network="base",                  # Blockchain network
    max_spend_per_hour=10.0          # Spending limit in USDC
)

# Register API tools
agent.register_tool("weather", "https://api.weather.com/v1/current")

# Execute tasks with automatic payments
result = agent.run("What's the weather in San Francisco?")

# Check balance and transfer funds
balance = agent.get_balance()
agent.transfer_to_agent("other_agent", 5.0)
```

#### AgentSwarm - Multi-Agent Coordination

```python
from level42.swarm import AgentSwarm

swarm = AgentSwarm(shared_wallet=True, cost_splitting="equal")
swarm.add_agent(researcher, "researcher")
swarm.add_agent(analyst, "analyst")

# Collaborative task execution
result = swarm.collaborate(
    task="Research AI developments and create analysis",
    strategy="sequential"  # or "parallel", "divide_and_conquer"
)

# Automatic cost splitting and fund transfers
swarm.split_costs(total_cost)
swarm.transfer_funds("agent1", "agent2", 10.0)
```

#### WalletManager - Cryptocurrency Operations

```python
from level42.wallet import WalletManager

wallet = WalletManager("0xprivate_key...", network="base")

# Balance and payment operations
balance = wallet.get_balance()
native_balance = wallet.get_native_balance()

# Single and batch payments
tx_hash = wallet.make_payment(1.0, "0xrecipient...")
tx_hashes = wallet.batch_payments([payment1, payment2, payment3])

# Transaction monitoring
history = wallet.get_transaction_history()
```

For complete API documentation with all methods, parameters, and examples, visit the **[API Reference](docs/api/)** section.

## 🔧 Configuration

### Environment Variables

```bash
# Optional: Set default network
export LEVEL42_DEFAULT_NETWORK=base

# Optional: Set default spending limits
export LEVEL42_MAX_SPEND_PER_HOUR=10.0

# Optional: Enable debug logging
export LEVEL42_DEBUG=true
```

### Configuration File

Create `~/.level42/config.yaml`:

```yaml
default_network: base
max_spend_per_hour: 10.0
deferred_payment_threshold: 10
networks:
  base:
    rpc_url: "https://mainnet.base.org"
    usdc_contract: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
  solana:
    rpc_url: "https://api.mainnet-beta.solana.com"
    usdc_mint: "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
```

## 🌐 Supported Networks

### Base Network (Default)
- **Token**: USDC
- **RPC**: https://mainnet.base.org
- **Explorer**: https://basescan.org

### Solana (Optional)
- **Token**: USDC
- **RPC**: https://api.mainnet-beta.solana.com
- **Explorer**: https://solscan.io

### Ethereum (Coming Soon)
- **Token**: USDC
- **RPC**: https://mainnet.infura.io
- **Explorer**: https://etherscan.io

## 📖 Examples

### Simple Trading Bot

```python
from level42 import Level42Agent
from langchain_openai import ChatOpenAI

# Create trading agent
agent = Level42Agent(
    llm=ChatOpenAI(model="gpt-4"),
    wallet_key="your_key",
    max_spend_per_hour=50.0
)

# Register financial data APIs
agent.register_tool("stock_price", "https://api.stocks.com/v1/price")
agent.register_tool("crypto_price", "https://api.crypto.com/v1/price")

# Execute trading strategy
result = agent.run("""
Analyze AAPL stock price and BTC price.
If AAPL is down more than 2% and BTC is up more than 5%,
recommend a trading strategy.
""")
```

### Research Swarm

```python
from level42 import Level42Agent, AgentSwarm

# Create specialized research agents
researcher = Level42Agent(llm=llm, wallet_key="key1")
analyst = Level42Agent(llm=llm, wallet_key="key2")
writer = Level42Agent(llm=llm, wallet_key="key3")

# Register different tools for each agent
researcher.register_tool("arxiv", "https://api.arxiv.org/search")
analyst.register_tool("sentiment", "https://api.sentiment.com/analyze")
writer.register_tool("grammar", "https://api.grammar.com/check")

# Create collaborative swarm
swarm = AgentSwarm(shared_wallet=True)
swarm.add_agent(researcher)
swarm.add_agent(analyst)
swarm.add_agent(writer)

# Execute research project
report = swarm.collaborate("""
Research recent developments in quantum computing,
analyze market sentiment,
and write a comprehensive report.
""")
```

## 🛠️ Development

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
python -m pytest tests/ -v --cov=x402_agent --cov-report=html

# Run specific test file
python -m pytest tests/test_agent.py -v
```

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Type checking
make type-check

# Security audit
make security-check
```

### Building Documentation

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Build docs
make docs

# Serve docs locally
cd docs && python -m http.server 8000
```

## 🐛 Troubleshooting

### Common Issues

#### "Insufficient funds" Error
```python
# Check your wallet balance
balance = agent.get_balance()
print(f"Current balance: {balance} USDC")

# Fund your wallet with USDC on Base Network
# Visit https://bridge.base.org to bridge funds
```

#### "Invalid private key" Error
```python
# Ensure your private key is valid and has 0x prefix
wallet_key = "0x1234567890abcdef..."  # 64 hex characters

# Test wallet connection
from x402_agent import WalletManager
wallet = WalletManager(wallet_key, "base")
print(f"Wallet address: {wallet.address}")
```

#### "Network connection failed" Error
```python
# Check network configuration
agent = Level42Agent(
    llm=llm,
    wallet_key="your_key",
    network="base"  # or "solana"
)

# Verify RPC endpoint
import requests
response = requests.get("https://mainnet.base.org")
print(f"Network status: {response.status_code}")
```

#### "HTTP 402 parsing failed" Error
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check API response format
# Ensure the API returns proper x402 headers:
# X-Payment-Amount: 0.01
# X-Payment-Address: 0x1234...
# X-Payment-Currency: USDC
```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Create agent with debug mode
agent = Level42Agent(
    llm=llm,
    wallet_key="your_key",
    debug=True
)

# Monitor payment transactions
agent.payment_processor.enable_logging()
```

### Performance Optimization

```python
# Optimize for high-frequency trading
agent = Level42Agent(
    llm=llm,
    wallet_key="your_key",
    deferred_payment_threshold=50,  # Batch more payments
    max_spend_per_hour=1000.0       # Higher spending limit
)

# Use connection pooling for better performance
import requests
session = requests.Session()
agent.payment_processor.session = session
```

## 📊 Monitoring and Analytics

### Spending Analytics

```python
# Get spending summary
summary = agent.get_spending_summary()
print(f"Total spent today: ${summary['today']}")
print(f"Most expensive tool: {summary['top_tool']}")

# Export transaction history
transactions = agent.export_transactions()
import pandas as pd
df = pd.DataFrame(transactions)
df.to_csv("agent_transactions.csv")
```

### Real-time Monitoring

```python
# Set up spending alerts
def spending_alert(amount, tool_name):
    if amount > 1.0:  # Alert for payments over $1
        print(f"High payment alert: ${amount} for {tool_name}")

agent.payment_processor.add_callback(spending_alert)

# Monitor agent health
health = agent.get_health_status()
print(f"Agent status: {health['status']}")
print(f"Wallet balance: ${health['balance']}")
print(f"Active tools: {health['tools_count']}")
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/tjelz/level42.git
cd level42

# Install in development mode
pip install -e ".[dev]"

# Run tests
make test

# Submit a pull request
```

### Reporting Issues

Please report bugs and feature requests on our [GitHub Issues](https://github.com/tjelz/level42/issues) page.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on [LangChain](https://langchain.com) for LLM integration
- Uses [Web3.py](https://web3py.readthedocs.io) for blockchain interactions
- Inspired by the HTTP 402 Payment Required status code
- Thanks to the Base Network team for L2 infrastructure

## 🪙 Token Information

### CA (Contract Address) - Coming Soon! 🚀

The Level42 Framework will soon launch its native utility token to power the ecosystem:

- **Token Symbol**: L42
- **Network**: Base Network (Primary), Multi-chain expansion planned
- **Use Cases**: 
  - Governance and protocol upgrades
  - Staking rewards for API providers
  - Premium features and enterprise licensing
  - Agent marketplace transactions
  - Community incentives and grants

**Stay tuned for the official token launch announcement!** 

Join our community channels below to be the first to know about the CA release and token distribution details.

## 🔗 Links

- **Documentation**: https://docs.level42.dev
- **PyPI Package**: https://pypi.org/project/level42/
- **GitHub Repository**: https://github.com/tjelz/level42
- **Discord Community**: https://discord.gg/level42
- **Twitter**: https://x.com/xlevel42
- **Telegram**: https://t.me/xlevel42
- **Medium Blog**: https://medium.com/@xlevel42

## 🏆 Roadmap

### Q4 2024
- ✅ Core framework release (v0.1.0)
- ✅ Base Network integration
- ✅ Multi-agent swarm capabilities
- 🔄 Solana Network integration
- 🔄 Enhanced documentation and tutorials

### Q1 2025
- 🔮 Native L42 token launch
- 🔮 Agent marketplace beta
- 🔮 Ethereum Network support
- 🔮 Advanced analytics dashboard
- 🔮 Enterprise features and SLA tiers

### Q2 2025
- 🔮 Cross-chain agent interactions
- 🔮 AI model marketplace integration
- 🔮 Decentralized governance launch
- 🔮 Mobile SDK release
- 🔮 Partnership integrations

### Q3 2025
- 🔮 Layer 2 network expansions
- 🔮 Advanced security features
- 🔮 Agent-to-agent lending protocols
- 🔮 Real-time collaboration tools
- 🔮 Global hackathon series

---

**Built with ❤️ by the Level42 team**

*Empowering the future of autonomous AI through seamless micropayments*