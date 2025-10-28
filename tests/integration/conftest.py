"""
Configuration and fixtures for integration tests.

Provides common fixtures and configuration for integration testing
including mock services, test data, and environment setup.
"""

import pytest
import os
import tempfile
import sqlite3
from unittest.mock import Mock, patch
from typing import Dict, Any, List
import json
import time

# Test configuration
TEST_CONFIG = {
    "networks": {
        "base": {
            "rpc_url": "https://goerli.base.org",  # Testnet
            "usdc_contract": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
            "chain_id": 84531
        },
        "solana": {
            "rpc_url": "https://api.devnet.solana.com",  # Devnet
            "usdc_mint": "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU",
            "cluster": "devnet"
        }
    },
    "test_wallets": {
        "base": "0x" + "1" * 64,
        "solana": "test_solana_key_base58"
    },
    "mock_apis": {
        "weather": {
            "endpoint": "https://api.weather.test/v1/current",
            "cost": 0.01,
            "response": {"temperature": 72, "condition": "sunny"}
        },
        "stocks": {
            "endpoint": "https://api.stocks.test/v1/price",
            "cost": 0.05,
            "response": {"symbol": "AAPL", "price": 150.25}
        },
        "news": {
            "endpoint": "https://api.news.test/v1/headlines",
            "cost": 0.02,
            "response": {"headlines": ["Test headline 1", "Test headline 2"]}
        }
    }
}


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration."""
    return TEST_CONFIG


@pytest.fixture(scope="session")
def temp_db():
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    # Initialize database schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables for testing
    cursor.execute("""
        CREATE TABLE agent_transactions (
            id INTEGER PRIMARY KEY,
            agent_id TEXT,
            tool_name TEXT,
            amount REAL,
            tx_hash TEXT,
            timestamp DATETIME,
            status TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE registered_tools (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            endpoint TEXT,
            description TEXT,
            cost_per_call REAL,
            payment_address TEXT,
            created_at DATETIME
        )
    """)
    
    cursor.execute("""
        CREATE TABLE deferred_payments (
            id INTEGER PRIMARY KEY,
            agent_id TEXT,
            amount REAL,
            recipient TEXT,
            tool_name TEXT,
            created_at DATETIME
        )
    """)
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    os.unlink(db_path)


@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    llm = Mock()
    llm.invoke.return_value = Mock(content="Test LLM response for integration testing")
    return llm


@pytest.fixture
def mock_web3_provider():
    """Mock Web3 provider for Base network testing."""
    with patch('x402_agent.wallet.Web3') as mock_web3_class:
        mock_web3_instance = Mock()
        
        # Mock account
        mock_account = Mock()
        mock_account.address = "0xtest_address"
        mock_web3_instance.eth.account.from_key.return_value = mock_account
        
        # Mock balance and transaction methods
        mock_web3_instance.eth.get_balance.return_value = 1000000000000000000  # 1 ETH
        mock_web3_instance.eth.get_transaction_count.return_value = 5
        mock_web3_instance.eth.gas_price = 1000000000  # 1 gwei
        mock_web3_instance.eth.estimate_gas.return_value = 21000
        mock_web3_instance.eth.send_raw_transaction.return_value = b"test_tx_hash"
        mock_web3_instance.to_hex.return_value = "0xtest_tx_hash"
        
        # Mock USDC contract
        mock_contract = Mock()
        mock_contract.functions.balanceOf.return_value.call.return_value = 10000000  # 10 USDC
        mock_contract.functions.transfer.return_value.build_transaction.return_value = {
            'to': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
            'value': 0,
            'gas': 21000,
            'gasPrice': 1000000000,
            'nonce': 5,
            'data': '0xtest_data'
        }
        mock_web3_instance.eth.contract.return_value = mock_contract
        
        mock_web3_class.return_value = mock_web3_instance
        yield mock_web3_instance


@pytest.fixture
def mock_solana_provider():
    """Mock Solana provider for Solana network testing."""
    try:
        with patch('x402_agent.solana_provider.Client') as mock_client_class:
            mock_client_instance = Mock()
            
            # Mock balance and transaction methods
            mock_balance_response = Mock()
            mock_balance_response.value = 1000000000  # 1 SOL in lamports
            mock_client_instance.get_balance.return_value = mock_balance_response
            
            mock_tx_response = Mock()
            mock_tx_response.value = "test_solana_signature"
            mock_client_instance.send_transaction.return_value = mock_tx_response
            
            # Mock token account balance
            mock_token_balance = Mock()
            mock_token_balance.value.ui_amount = 10.0  # 10 USDC
            mock_client_instance.get_token_account_balance.return_value = mock_token_balance
            
            mock_client_class.return_value = mock_client_instance
            yield mock_client_instance
    except ImportError:
        pytest.skip("Solana dependencies not available")


@pytest.fixture
def mock_http_402_server():
    """Mock HTTP server that returns 402 responses."""
    class MockHTTP402Server:
        def __init__(self):
            self.payments_received = []
            self.api_calls = []
        
        def handle_request(self, url: str, headers: Dict[str, str] = None, method: str = "GET"):
            """Handle API request with 402 payment flow."""
            self.api_calls.append({
                "url": url,
                "headers": headers or {},
                "method": method,
                "timestamp": time.time()
            })
            
            # Check for payment proof
            if headers and "X-Payment-Proof" in headers:
                # Payment provided, return success
                response = Mock()
                response.status_code = 200
                response.json.return_value = self._get_api_response(url)
                response.text = json.dumps(response.json.return_value)
                
                self.payments_received.append({
                    "url": url,
                    "proof": headers["X-Payment-Proof"],
                    "timestamp": time.time()
                })
                
                return response
            else:
                # No payment, return 402
                response = Mock()
                response.status_code = 402
                response.headers = {
                    "X-Payment-Amount": str(self._get_api_cost(url)),
                    "X-Payment-Address": "0x742d35Cc6634C0532925a3b8D4C9db96DfbBfC88",
                    "X-Payment-Currency": "USDC",
                    "X-Payment-Network": "base"
                }
                response.json.return_value = {
                    "error": "Payment required",
                    "message": f"Please pay {self._get_api_cost(url)} USDC"
                }
                response.text = json.dumps(response.json.return_value)
                
                return response
        
        def _get_api_cost(self, url: str) -> float:
            """Get cost for API based on URL."""
            for api_name, api_config in TEST_CONFIG["mock_apis"].items():
                if api_config["endpoint"] in url:
                    return api_config["cost"]
            return 0.01  # Default cost
        
        def _get_api_response(self, url: str) -> Dict[str, Any]:
            """Get mock response for API based on URL."""
            for api_name, api_config in TEST_CONFIG["mock_apis"].items():
                if api_config["endpoint"] in url:
                    return api_config["response"]
            return {"data": "default response"}
        
        def reset(self):
            """Reset server state."""
            self.payments_received.clear()
            self.api_calls.clear()
    
    return MockHTTP402Server()


@pytest.fixture
def test_agents(mock_llm, test_config):
    """Create multiple test agents for swarm testing."""
    agents = []
    
    for i in range(3):
        with patch('x402_agent.wallet.WalletManager') as mock_wallet_manager:
            mock_wallet_instance = Mock()
            mock_wallet_instance.get_balance.return_value = 10.0
            mock_wallet_instance.make_payment.return_value = f"0xtest_tx_hash_{i}"
            mock_wallet_instance.batch_payments.return_value = [f"0xbatch_tx_{i}"]
            mock_wallet_manager.return_value = mock_wallet_instance
            
            from x402_agent import X402Agent
            agent = X402Agent(
                llm=mock_llm,
                wallet_key=f"0x{'1' * 63}{i}",
                network="base"
            )
            agent.wallet_manager = mock_wallet_instance
            agents.append(agent)
    
    return agents


@pytest.fixture
def sample_tools():
    """Sample tools for testing."""
    from x402_agent.tools import Tool
    
    return [
        Tool(
            name="weather",
            endpoint="https://api.weather.test/v1/current",
            description="Get current weather",
            cost_per_call=0.01,
            payment_address="0x742d35Cc6634C0532925a3b8D4C9db96DfbBfC88"
        ),
        Tool(
            name="stocks",
            endpoint="https://api.stocks.test/v1/price",
            description="Get stock prices",
            cost_per_call=0.05,
            payment_address="0x742d35Cc6634C0532925a3b8D4C9db96DfbBfC88"
        ),
        Tool(
            name="news",
            endpoint="https://api.news.test/v1/headlines",
            description="Get news headlines",
            cost_per_call=0.02,
            payment_address="0x742d35Cc6634C0532925a3b8D4C9db96DfbBfC88"
        )
    ]


@pytest.fixture
def integration_test_environment(temp_db, mock_web3_provider, mock_http_402_server):
    """Set up complete integration test environment."""
    # Set environment variables for testing
    os.environ["X402_TEST_MODE"] = "true"
    os.environ["X402_DB_PATH"] = temp_db
    os.environ["X402_DEBUG"] = "true"
    
    yield {
        "db_path": temp_db,
        "web3_provider": mock_web3_provider,
        "http_server": mock_http_402_server
    }
    
    # Cleanup
    os.environ.pop("X402_TEST_MODE", None)
    os.environ.pop("X402_DB_PATH", None)
    os.environ.pop("X402_DEBUG", None)


# Pytest configuration
def pytest_configure(config):
    """Configure pytest for integration tests."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "network: mark test as requiring network access"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Mark all tests in integration directory as integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Mark network tests
        if "network" in item.name or "Network" in item.name:
            item.add_marker(pytest.mark.network)
        
        # Mark slow tests
        if "batch" in item.name or "concurrent" in item.name or "performance" in item.name:
            item.add_marker(pytest.mark.slow)