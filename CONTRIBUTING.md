# Contributing to x402-Agent Framework

Thank you for your interest in contributing to the x402-Agent Framework! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Development Environment Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/x402-agent-framework.git
   cd x402-agent-framework
   ```

2. **Install Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Run Tests**
   ```bash
   make test
   ```

### Development Workflow

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code following our style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   make test
   make lint
   make type-check
   ```

4. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Open a PR against the `main` branch
   - Fill out the PR template
   - Wait for review and address feedback

## 📝 Code Style

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line Length**: 88 characters (Black default)
- **Imports**: Use absolute imports, group by standard/third-party/local
- **Type Hints**: Required for all public functions
- **Docstrings**: Google style for all public methods

### Code Formatting

We use automated formatting tools:

```bash
# Format code
make format

# Check formatting
make check-format
```

### Example Code Style

```python
from typing import List, Optional, Dict, Any
import logging

from x402_agent.base import BaseAgent
from x402_agent.types import Payment, Tool


class ExampleAgent(BaseAgent):
    """Example agent demonstrating code style.
    
    This class shows the preferred code style for the x402-Agent framework.
    
    Args:
        llm: The language model to use
        wallet_key: Private key for the wallet
        network: Blockchain network to use
        
    Attributes:
        tools: Registered tools for the agent
        payment_processor: Handles payment operations
    """
    
    def __init__(
        self, 
        llm: Any, 
        wallet_key: str, 
        network: str = "base"
    ) -> None:
        super().__init__(llm, wallet_key, network)
        self.logger = logging.getLogger(__name__)
        
    def register_tool(
        self, 
        name: str, 
        endpoint: str, 
        description: str = ""
    ) -> None:
        """Register a new tool for the agent.
        
        Args:
            name: Unique name for the tool
            endpoint: API endpoint URL
            description: Optional description of the tool
            
        Raises:
            ValueError: If tool name already exists
        """
        if name in self.tools:
            raise ValueError(f"Tool '{name}' already registered")
            
        tool = Tool(
            name=name,
            endpoint=endpoint,
            description=description
        )
        self.tools[name] = tool
        self.logger.info(f"Registered tool: {name}")
```

## 🧪 Testing

### Test Structure

```
tests/
├── __init__.py
├── test_agent.py          # Agent core functionality
├── test_wallet.py         # Wallet management
├── test_payments.py       # Payment processing
├── test_tools.py          # Tool registry
├── test_swarm.py          # Multi-agent coordination
├── test_monitoring.py     # Monitoring and logging
├── test_error_handling.py # Error handling
└── integration/           # Integration tests
    ├── test_e2e.py        # End-to-end scenarios
    └── test_networks.py   # Network integration
```

### Writing Tests

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete user workflows

### Test Guidelines

- Use descriptive test names: `test_agent_handles_insufficient_funds_gracefully`
- Mock external dependencies (APIs, blockchain calls)
- Test both success and failure scenarios
- Include edge cases and boundary conditions

### Example Test

```python
import pytest
from unittest.mock import Mock, patch

from x402_agent import X402Agent
from x402_agent.exceptions import InsufficientFundsError


class TestX402Agent:
    """Test cases for X402Agent class."""
    
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for testing."""
        llm = Mock()
        llm.invoke.return_value = "Test response"
        return llm
    
    @pytest.fixture
    def agent(self, mock_llm):
        """Create test agent."""
        return X402Agent(
            llm=mock_llm,
            wallet_key="0x" + "1" * 64,
            network="base"
        )
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.network == "base"
        assert len(agent.tools) == 0
        assert agent.wallet_manager is not None
    
    def test_register_tool_success(self, agent):
        """Test successful tool registration."""
        agent.register_tool("test_tool", "https://api.example.com")
        
        assert "test_tool" in agent.tools
        assert agent.tools["test_tool"].endpoint == "https://api.example.com"
    
    def test_register_duplicate_tool_raises_error(self, agent):
        """Test registering duplicate tool raises error."""
        agent.register_tool("test_tool", "https://api.example.com")
        
        with pytest.raises(ValueError, match="already registered"):
            agent.register_tool("test_tool", "https://api2.example.com")
    
    @patch('x402_agent.wallet.WalletManager.get_balance')
    def test_insufficient_funds_handling(self, mock_balance, agent):
        """Test agent handles insufficient funds gracefully."""
        mock_balance.return_value = 0.0
        
        with pytest.raises(InsufficientFundsError):
            agent.run("Make an expensive API call")
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
python -m pytest tests/test_agent.py -v

# Run with coverage
python -m pytest tests/ --cov=x402_agent --cov-report=html

# Run integration tests only
python -m pytest tests/integration/ -v
```

## 📚 Documentation

### Documentation Structure

```
docs/
├── index.md              # Main documentation
├── quickstart.md         # Getting started guide
├── api/                  # API reference
│   ├── agent.md
│   ├── wallet.md
│   └── payments.md
├── examples/             # Usage examples
│   ├── basic_usage.md
│   ├── trading_bot.md
│   └── multi_agent.md
└── guides/               # How-to guides
    ├── configuration.md
    ├── troubleshooting.md
    └── deployment.md
```

### Writing Documentation

- Use clear, concise language
- Include code examples for all features
- Add screenshots for UI components
- Keep examples up-to-date with latest API

### Building Documentation

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Build documentation
make docs

# Serve locally
cd docs && python -m http.server 8000
```

## 🐛 Bug Reports

### Before Reporting

1. Check existing issues
2. Update to latest version
3. Test with minimal reproduction case

### Bug Report Template

```markdown
**Bug Description**
A clear description of the bug.

**To Reproduce**
Steps to reproduce the behavior:
1. Create agent with '...'
2. Call method '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Environment**
- OS: [e.g. macOS 12.0]
- Python: [e.g. 3.9.0]
- x402-agent: [e.g. 0.1.0]
- Network: [e.g. Base]

**Additional Context**
Any other context about the problem.
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Feature Description**
A clear description of the feature you'd like to see.

**Use Case**
Describe the problem this feature would solve.

**Proposed Solution**
How you envision this feature working.

**Alternatives Considered**
Other solutions you've considered.

**Additional Context**
Any other context or screenshots.
```

## 🏗️ Architecture Guidelines

### Project Structure

```
x402_agent/
├── __init__.py           # Package exports
├── agent.py              # Main agent class
├── wallet.py             # Wallet management
├── payments.py           # Payment processing
├── tools.py              # Tool registry
├── swarm.py              # Multi-agent coordination
├── monitoring.py         # Logging and analytics
├── utils.py              # Utility functions
├── exceptions.py         # Custom exceptions
├── types.py              # Type definitions
└── networks/             # Network providers
    ├── __init__.py
    ├── base.py
    └── solana.py
```

### Design Principles

1. **Modularity**: Each component has a single responsibility
2. **Extensibility**: Easy to add new networks and features
3. **Testability**: All components are easily testable
4. **Security**: Private keys never persisted, secure by default
5. **Performance**: Efficient payment batching and caching

### Adding New Features

1. **Network Support**: Implement `NetworkProvider` interface
2. **Payment Methods**: Extend `PaymentProcessor` class
3. **Tool Types**: Add new tool types to `ToolRegistry`
4. **Agent Behaviors**: Extend `X402Agent` class

## 🔒 Security Guidelines

### Security Best Practices

1. **Private Key Handling**
   - Never log private keys
   - Store in memory only
   - Use secure random generation

2. **Input Validation**
   - Validate all user inputs
   - Sanitize API responses
   - Check payment amounts

3. **Network Security**
   - Use HTTPS for all API calls
   - Verify SSL certificates
   - Implement request timeouts

### Security Review Process

1. All PRs undergo security review
2. Dependency updates checked for vulnerabilities
3. Regular security audits of codebase
4. Automated security scanning in CI

## 📋 Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. **Pre-release**
   - [ ] All tests passing
   - [ ] Documentation updated
   - [ ] CHANGELOG.md updated
   - [ ] Version bumped

2. **Release**
   - [ ] Create release tag
   - [ ] Build and upload to PyPI
   - [ ] Create GitHub release
   - [ ] Update documentation

3. **Post-release**
   - [ ] Announce on Discord/Twitter
   - [ ] Update examples
   - [ ] Monitor for issues

### Making a Release

```bash
# Bump version
make bump-minor  # or bump-patch, bump-major

# Create release
git tag v0.2.0
git push origin v0.2.0

# GitHub Actions will handle the rest
```

## 🤝 Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Discord**: Real-time chat and support
- **Twitter**: Announcements and updates

### Code of Conduct

We follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).

### Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- Annual contributor awards

## ❓ Questions?

If you have questions about contributing, please:

1. Check this guide and existing documentation
2. Search existing GitHub issues
3. Ask in GitHub Discussions
4. Join our Discord community

Thank you for contributing to x402-Agent Framework! 🚀