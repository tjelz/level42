# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the x402-Agent Framework.

## Quick Diagnostics

### 1. Health Check Script

```python
# health_check.py
import os
import sys
from x402_agent import X402Agent
from x402_agent.wallet import WalletManager
from langchain_openai import ChatOpenAI

def run_health_check():
    """Comprehensive health check for x402-Agent setup."""
    
    print("🔍 x402-Agent Framework Health Check")
    print("=" * 50)
    
    issues = []
    
    # Check 1: Environment Variables
    print("\n1. Checking Environment Variables...")
    required_vars = ["WALLET_PRIVATE_KEY", "OPENAI_API_KEY"]
    
    for var in required_vars:
        if os.getenv(var):
            print(f"   ✅ {var}: Set")
        else:
            print(f"   ❌ {var}: Missing")
            issues.append(f"Missing environment variable: {var}")
    
    # Check 2: Private Key Format
    print("\n2. Validating Private Key...")
    private_key = os.getenv("WALLET_PRIVATE_KEY")
    
    if private_key:
        if len(private_key) == 66 and private_key.startswith("0x"):
            print("   ✅ Private key format: Valid")
        else:
            print("   ❌ Private key format: Invalid")
            issues.append("Private key must be 66 characters starting with 0x")
    
    # Check 3: Network Connectivity
    print("\n3. Testing Network Connectivity...")
    try:
        import requests
        response = requests.get("https://mainnet.base.org", timeout=10)
        if response.status_code == 200:
            print("   ✅ Base Network: Accessible")
        else:
            print(f"   ⚠️  Base Network: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Base Network: Connection failed ({e})")
        issues.append("Cannot connect to Base Network")
    
    # Check 4: Wallet Connection
    print("\n4. Testing Wallet Connection...")
    if private_key and len(private_key) == 66:
        try:
            wallet = WalletManager(private_key, "base")
            balance = wallet.get_balance()
            print(f"   ✅ Wallet Connection: Success")
            print(f"   💰 USDC Balance: ${balance:.2f}")
            
            if balance < 1.0:
                print("   ⚠️  Low balance warning")
                issues.append("Wallet balance is low (< $1.00 USDC)")
                
        except Exception as e:
            print(f"   ❌ Wallet Connection: Failed ({e})")
            issues.append(f"Wallet connection error: {e}")
    
    # Check 5: LLM Connection
    print("\n5. Testing LLM Connection...")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if openai_key:
        try:
            llm = ChatOpenAI(api_key=openai_key, model="gpt-3.5-turbo")
            response = llm.invoke("Hello")
            print("   ✅ OpenAI Connection: Success")
        except Exception as e:
            print(f"   ❌ OpenAI Connection: Failed ({e})")
            issues.append(f"OpenAI connection error: {e}")
    
    # Check 6: Agent Creation
    print("\n6. Testing Agent Creation...")
    if not issues:  # Only test if no critical issues
        try:
            agent = X402Agent(
                llm=ChatOpenAI(api_key=openai_key),
                wallet_key=private_key,
                network="base"
            )
            print("   ✅ Agent Creation: Success")
        except Exception as e:
            print(f"   ❌ Agent Creation: Failed ({e})")
            issues.append(f"Agent creation error: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    if issues:
        print("❌ Health Check Failed")
        print("\nIssues Found:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    else:
        print("✅ Health Check Passed - All systems operational!")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = run_health_check()
    sys.exit(0 if success else 1)
```

## Common Issues and Solutions

### 1. Installation Issues

#### Issue: `pip install x402-agent` fails

**Symptoms:**
```bash
ERROR: Could not find a version that satisfies the requirement x402-agent
```

**Solutions:**
```bash
# Update pip
pip install --upgrade pip

# Try with specific index
pip install --index-url https://pypi.org/simple/ x402-agent

# Install from source
git clone https://github.com/x402-agent/x402-agent-framework.git
cd x402-agent-framework
pip install -e .
```

#### Issue: Dependency conflicts

**Symptoms:**
```bash
ERROR: pip's dependency resolver does not currently consider all the packages
```

**Solutions:**
```bash
# Create fresh virtual environment
python -m venv x402_env
source x402_env/bin/activate  # On Windows: x402_env\Scripts\activate

# Install with no dependencies first
pip install --no-deps x402-agent

# Install dependencies manually
pip install requests web3 langchain-core cryptography pydantic
```

### 2. Wallet and Network Issues

#### Issue: "Invalid private key" error

**Symptoms:**
```python
ValueError: Invalid private key format
```

**Diagnosis:**
```python
def diagnose_private_key(key):
    print(f"Key length: {len(key)}")
    print(f"Starts with 0x: {key.startswith('0x')}")
    print(f"Contains only hex: {all(c in '0123456789abcdefABCDEF' for c in key[2:])}")

# Test your key
diagnose_private_key(your_private_key)
```

**Solutions:**
```python
# Correct format
private_key = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"

# If you have key without 0x prefix
if not private_key.startswith("0x"):
    private_key = "0x" + private_key

# Validate length
if len(private_key) != 66:
    raise ValueError("Private key must be 64 hex characters plus 0x prefix")
```

#### Issue: "Insufficient funds" error

**Symptoms:**
```python
InsufficientFundsError: Wallet balance too low for transaction
```

**Diagnosis:**
```python
def diagnose_wallet_funds(agent):
    balance = agent.get_balance()
    native_balance = agent.wallet_manager.get_native_balance()
    
    print(f"USDC Balance: ${balance:.2f}")
    print(f"ETH Balance: {native_balance:.6f} ETH")
    
    if balance < 0.01:
        print("❌ Insufficient USDC for API payments")
    if native_balance < 0.001:
        print("❌ Insufficient ETH for gas fees")

diagnose_wallet_funds(agent)
```

**Solutions:**
```bash
# Fund your wallet with USDC on Base Network
# 1. Visit https://bridge.base.org
# 2. Bridge USDC from Ethereum mainnet to Base
# 3. Ensure you have some ETH for gas fees

# Or use a faucet for testnet
# Visit Base testnet faucet for test tokens
```

#### Issue: Network connection failures

**Symptoms:**
```python
NetworkError: Unable to connect to Base Network
```

**Diagnosis:**
```python
def diagnose_network_connection():
    import requests
    
    endpoints = {
        "Base Mainnet": "https://mainnet.base.org",
        "Base Testnet": "https://goerli.base.org",
        "Ethereum": "https://mainnet.infura.io"
    }
    
    for name, url in endpoints.items():
        try:
            response = requests.get(url, timeout=10)
            print(f"✅ {name}: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {e}")

diagnose_network_connection()
```

**Solutions:**
```python
# Use custom RPC endpoint
agent = X402Agent(
    llm=llm,
    wallet_key=private_key,
    network="base",
    rpc_url="https://your-custom-rpc.com"
)

# Check firewall/proxy settings
# Ensure ports 443 and 8545 are open
```

### 3. Payment Processing Issues

#### Issue: HTTP 402 parsing failures

**Symptoms:**
```python
InvalidPaymentRequestError: Missing required payment headers
```

**Diagnosis:**
```python
def diagnose_402_response(response):
    print(f"Status Code: {response.status_code}")
    print("Headers:")
    for header, value in response.headers.items():
        if header.lower().startswith('x-payment'):
            print(f"  {header}: {value}")
    
    # Check for required headers
    required_headers = [
        'X-Payment-Amount',
        'X-Payment-Address',
        'X-Payment-Currency'
    ]
    
    missing = [h for h in required_headers if h not in response.headers]
    if missing:
        print(f"❌ Missing headers: {missing}")

# Test with actual 402 response
diagnose_402_response(response)
```

**Solutions:**
```python
# Ensure API returns proper 402 headers
# Example correct 402 response:
"""
HTTP/1.1 402 Payment Required
X-Payment-Amount: 0.01
X-Payment-Address: 0x1234567890abcdef...
X-Payment-Currency: USDC
X-Payment-Network: base
Content-Type: application/json

{
  "error": "Payment required",
  "payment": {
    "amount": 0.01,
    "currency": "USDC",
    "address": "0x1234567890abcdef..."
  }
}
"""
```

#### Issue: Payment transactions failing

**Symptoms:**
```python
PaymentError: Transaction failed with error: insufficient gas
```

**Diagnosis:**
```python
def diagnose_payment_failure(agent, amount, recipient):
    # Check balances
    usdc_balance = agent.get_balance()
    eth_balance = agent.wallet_manager.get_native_balance()
    
    print(f"USDC Balance: ${usdc_balance:.2f}")
    print(f"ETH Balance: {eth_balance:.6f}")
    
    # Estimate gas cost
    try:
        gas_cost = agent.wallet_manager.estimate_gas_cost(amount, recipient)
        print(f"Estimated gas cost: {gas_cost:.6f} ETH")
        
        if eth_balance < gas_cost:
            print("❌ Insufficient ETH for gas")
        if usdc_balance < amount:
            print("❌ Insufficient USDC for payment")
            
    except Exception as e:
        print(f"Gas estimation failed: {e}")

diagnose_payment_failure(agent, 0.01, "0xrecipient...")
```

**Solutions:**
```python
# Increase gas price for faster confirmation
agent.wallet_manager.set_gas_price(gwei=20)

# Use payment batching to reduce gas costs
processor = PaymentProcessor(agent.wallet_manager, deferred_threshold=10)

# Monitor gas prices and adjust accordingly
def adjust_gas_price():
    # Get current gas price from network
    current_gas = agent.wallet_manager.get_current_gas_price()
    # Set slightly higher for reliability
    agent.wallet_manager.set_gas_price(gwei=current_gas * 1.1)
```

### 4. Tool Registration Issues

#### Issue: Tool registration failures

**Symptoms:**
```python
ToolRegistrationError: Endpoint validation failed
```

**Diagnosis:**
```python
def diagnose_tool_endpoint(endpoint):
    import requests
    
    print(f"Testing endpoint: {endpoint}")
    
    try:
        # Test basic connectivity
        response = requests.head(endpoint, timeout=10)
        print(f"✅ Connectivity: {response.status_code}")
        
        # Check for CORS headers
        cors_headers = [h for h in response.headers if 'cors' in h.lower()]
        if cors_headers:
            print(f"CORS headers: {cors_headers}")
        
        # Test GET request
        response = requests.get(endpoint, timeout=10)
        print(f"GET response: {response.status_code}")
        
        # Check content type
        content_type = response.headers.get('content-type', '')
        print(f"Content-Type: {content_type}")
        
    except requests.exceptions.Timeout:
        print("❌ Timeout - endpoint too slow")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - endpoint unreachable")
    except Exception as e:
        print(f"❌ Error: {e}")

diagnose_tool_endpoint("https://api.example.com/data")
```

**Solutions:**
```python
# Register with custom configuration
agent.register_tool(
    name="api_tool",
    endpoint="https://api.example.com/data",
    description="API description",
    timeout=30,
    retry_attempts=3,
    headers={"User-Agent": "x402-agent/1.0"}
)

# Skip validation for internal APIs
agent.register_tool(
    name="internal_api",
    endpoint="http://internal.company.com/api",
    skip_validation=True
)
```

### 5. Performance Issues

#### Issue: Slow response times

**Symptoms:**
- Agent tasks taking too long
- Timeouts on API calls
- High memory usage

**Diagnosis:**
```python
import time
import psutil
import threading

def diagnose_performance(agent):
    """Comprehensive performance diagnosis."""
    
    # Memory usage
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Memory usage: {memory_mb:.1f} MB")
    
    # CPU usage
    cpu_percent = process.cpu_percent(interval=1)
    print(f"CPU usage: {cpu_percent:.1f}%")
    
    # Test response time
    start_time = time.time()
    try:
        balance = agent.get_balance()
        response_time = time.time() - start_time
        print(f"Balance check time: {response_time:.2f}s")
    except Exception as e:
        print(f"Balance check failed: {e}")
    
    # Check active connections
    connections = len([c for c in process.connections() if c.status == 'ESTABLISHED'])
    print(f"Active connections: {connections}")

diagnose_performance(agent)
```

**Solutions:**
```python
# Enable connection pooling
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry_strategy = Retry(total=3, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=20)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Use async processing for multiple tasks
import asyncio

async def process_tasks_async(agent, tasks):
    loop = asyncio.get_event_loop()
    
    # Process tasks concurrently
    futures = [
        loop.run_in_executor(None, agent.run, task)
        for task in tasks
    ]
    
    results = await asyncio.gather(*futures)
    return results

# Enable caching for frequent operations
agent.enable_balance_caching(ttl=60)  # Cache balance for 1 minute
```

### 6. Multi-Agent Swarm Issues

#### Issue: Agent communication failures

**Symptoms:**
```python
AgentCommunicationError: Message delivery failed
```

**Diagnosis:**
```python
def diagnose_swarm_communication(swarm):
    """Test inter-agent communication."""
    
    agents = list(swarm.agents.keys())
    
    for sender in agents:
        for receiver in agents:
            if sender != receiver:
                try:
                    swarm.send_message(sender, receiver, "test")
                    print(f"✅ {sender} → {receiver}: OK")
                except Exception as e:
                    print(f"❌ {sender} → {receiver}: {e}")

diagnose_swarm_communication(swarm)
```

**Solutions:**
```python
# Enable message queuing for reliability
swarm.enable_message_queuing(
    backend="redis",
    connection_string="redis://localhost:6379"
)

# Add retry logic for failed messages
swarm.configure_messaging({
    "retry_attempts": 3,
    "retry_delay": 1.0,
    "timeout": 30
})
```

#### Issue: Cost splitting errors

**Symptoms:**
```python
CostSplittingError: Allocation doesn't sum to total
```

**Diagnosis:**
```python
def diagnose_cost_splitting(swarm, test_amount=10.0):
    """Test cost splitting logic."""
    
    try:
        allocation = swarm.split_costs(test_amount)
        total_allocated = sum(allocation.values())
        
        print(f"Test amount: ${test_amount:.2f}")
        print(f"Total allocated: ${total_allocated:.2f}")
        print(f"Difference: ${abs(test_amount - total_allocated):.6f}")
        
        for agent_id, amount in allocation.items():
            print(f"  {agent_id}: ${amount:.2f}")
            
        if abs(test_amount - total_allocated) > 0.01:
            print("❌ Cost splitting error detected")
        else:
            print("✅ Cost splitting working correctly")
            
    except Exception as e:
        print(f"❌ Cost splitting failed: {e}")

diagnose_cost_splitting(swarm)
```

**Solutions:**
```python
# Use decimal for precise calculations
from decimal import Decimal, ROUND_HALF_UP

def precise_cost_split(total_cost, agent_count):
    """Precise cost splitting using Decimal."""
    total = Decimal(str(total_cost))
    per_agent = total / agent_count
    
    # Round to 6 decimal places
    per_agent = per_agent.quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
    
    return float(per_agent)

# Custom splitting function
def custom_split_function(total_cost, agents, usage_data):
    splits = {}
    remaining = Decimal(str(total_cost))
    
    # Calculate splits
    for agent_id in agents[:-1]:  # All but last
        split = precise_cost_split(total_cost, len(agents))
        splits[agent_id] = float(split)
        remaining -= Decimal(str(split))
    
    # Last agent gets remainder to ensure exact total
    splits[agents[-1]] = float(remaining)
    
    return splits

swarm.set_custom_split_function(custom_split_function)
```

## Debugging Tools

### 1. Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Create agent with debug mode
agent = X402Agent(
    llm=llm,
    wallet_key=private_key,
    network="base",
    debug=True
)

# Enable payment processor debugging
agent.payment_processor.enable_debug_logging()
```

### 2. Transaction Monitoring

```python
def monitor_transactions(agent):
    """Monitor all transactions in real-time."""
    
    def transaction_callback(tx_hash, status, details):
        print(f"Transaction {tx_hash}: {status}")
        if details:
            print(f"  Amount: ${details.get('amount', 0):.2f}")
            print(f"  Recipient: {details.get('recipient', 'unknown')}")
            print(f"  Gas used: {details.get('gas_used', 0)}")
    
    agent.wallet_manager.add_transaction_callback(transaction_callback)

monitor_transactions(agent)
```

### 3. Performance Profiler

```python
import cProfile
import pstats
from io import StringIO

def profile_agent_task(agent, task):
    """Profile agent task execution."""
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    try:
        result = agent.run(task)
    finally:
        profiler.disable()
    
    # Print profiling results
    s = StringIO()
    ps = pstats.Stats(profiler, stream=s)
    ps.sort_stats('cumulative')
    ps.print_stats(20)  # Top 20 functions
    
    print(s.getvalue())
    return result

# Profile a task
result = profile_agent_task(agent, "Get weather data")
```

## Getting Help

### 1. Collect Diagnostic Information

```python
def collect_diagnostics(agent):
    """Collect comprehensive diagnostic information."""
    
    import platform
    import sys
    
    diagnostics = {
        "system": {
            "platform": platform.platform(),
            "python_version": sys.version,
            "x402_agent_version": x402_agent.__version__
        },
        "agent": {
            "agent_id": agent.agent_id,
            "network": agent.network,
            "wallet_address": agent.wallet_manager.address,
            "balance": agent.get_balance(),
            "tool_count": len(agent.tools)
        },
        "performance": agent.get_performance_metrics(),
        "recent_errors": agent.get_recent_errors()
    }
    
    return diagnostics

# Collect and save diagnostics
diagnostics = collect_diagnostics(agent)
with open("diagnostics.json", "w") as f:
    json.dump(diagnostics, f, indent=2)
```

### 2. Community Support

- **GitHub Issues**: https://github.com/x402-agent/x402-agent-framework/issues
- **Discord Community**: https://discord.gg/x402-agent
- **Documentation**: https://docs.x402-agent.dev
- **Stack Overflow**: Tag questions with `x402-agent`

### 3. Creating Bug Reports

When reporting bugs, include:

1. **Environment Information**:
   - Operating system
   - Python version
   - x402-agent version
   - Network (mainnet/testnet)

2. **Reproduction Steps**:
   - Minimal code example
   - Expected vs actual behavior
   - Error messages and stack traces

3. **Diagnostic Data**:
   - Output from health check script
   - Relevant log files
   - Network connectivity test results

### 4. Emergency Procedures

#### Wallet Compromise
```python
# If you suspect wallet compromise:
# 1. Immediately transfer funds to new wallet
emergency_wallet = WalletManager("0xnew_private_key...", "base")
current_balance = agent.get_balance()

if current_balance > 0:
    tx_hash = agent.wallet_manager.transfer_all_funds(emergency_wallet.address)
    print(f"Emergency transfer: {tx_hash}")

# 2. Rotate all API keys
# 3. Review transaction history
# 4. Update wallet key in all configurations
```

#### Service Outage
```python
# Implement circuit breaker pattern
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            
            raise e

# Use circuit breaker for critical operations
breaker = CircuitBreaker()
result = breaker.call(agent.run, "Critical task")
```

This troubleshooting guide should help you quickly identify and resolve most issues you might encounter with the x402-Agent Framework. Remember to always check the basics first (network connectivity, wallet balance, API keys) before diving into more complex diagnostics. 🔧