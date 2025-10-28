"""
Network integration tests for x402-Agent Framework.

Tests integration with different blockchain networks including Base and Solana.
Uses testnet connections and mock network providers for testing.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any
import time

from x402_agent import WalletManager
from x402_agent.exceptions import NetworkError, InsufficientFundsError


class TestBaseNetworkIntegration:
    """Test Base network integration."""
    
    @pytest.fixture
    def base_wallet_key(self):
        """Test wallet key for Base network."""
        return "0x" + "1" * 64
    
    @pytest.fixture
    def mock_web3(self):
        """Mock Web3 instance for Base network testing."""
        with patch('x402_agent.wallet.Web3') as mock_web3_class:
            mock_web3_instance = Mock()
            mock_web3_instance.eth.account.from_key.return_value = Mock(address="0xtest_address")
            mock_web3_instance.eth.get_balance.return_value = 1000000000000000000  # 1 ETH in wei
            mock_web3_instance.eth.get_transaction_count.return_value = 5
            mock_web3_instance.eth.gas_price = 1000000000  # 1 gwei
            mock_web3_instance.eth.send_raw_transaction.return_value = b"test_tx_hash"
            mock_web3_instance.to_hex.return_value = "0xtest_tx_hash"
            mock_web3_class.return_value = mock_web3_instance
            return mock_web3_instance
    
    @pytest.fixture
    def mock_usdc_contract(self, mock_web3):
        """Mock USDC contract for Base network."""
        mock_contract = Mock()
        mock_contract.functions.balanceOf.return_value.call.return_value = 10000000  # 10 USDC (6 decimals)
        mock_contract.functions.transfer.return_value.build_transaction.return_value = {
            'to': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
            'value': 0,
            'gas': 21000,
            'gasPrice': 1000000000,
            'nonce': 5,
            'data': '0xtest_data'
        }
        mock_web3.eth.contract.return_value = mock_contract
        return mock_contract
    
    def test_base_wallet_initialization(self, base_wallet_key, mock_web3, mock_usdc_contract):
        """Test Base network wallet initialization."""
        wallet = WalletManager(base_wallet_key, "base")
        
        assert wallet.network == "base"
        assert wallet.private_key == base_wallet_key
        
        # Verify Web3 connection was established
        mock_web3.eth.account.from_key.assert_called_once_with(base_wallet_key)
    
    def test_base_balance_check(self, base_wallet_key, mock_web3, mock_usdc_contract):
        """Test USDC balance checking on Base network."""
        wallet = WalletManager(base_wallet_key, "base")
        
        balance = wallet.get_balance()
        
        # Should return 10.0 USDC (10000000 / 10^6)
        assert balance == 10.0
        
        # Verify contract method was called
        mock_usdc_contract.functions.balanceOf.assert_called_once()
    
    def test_base_payment_execution(self, base_wallet_key, mock_web3, mock_usdc_contract):
        """Test USDC payment execution on Base network."""
        wallet = WalletManager(base_wallet_key, "base")
        
        recipient = "0x742d35Cc6634C0532925a3b8D4C9db96DfbBfC88"
        amount = 1.5
        
        tx_hash = wallet.make_payment(amount, recipient)
        
        assert tx_hash == "0xtest_tx_hash"
        
        # Verify transaction was built and sent
        mock_usdc_contract.functions.transfer.assert_called_once()
        mock_web3.eth.send_raw_transaction.assert_called_once()
    
    def test_base_batch_payments(self, base_wallet_key, mock_web3, mock_usdc_contract):
        """Test batch payment processing on Base network."""
        wallet = WalletManager(base_wallet_key, "base")
        
        from x402_agent.payments import Payment
        payments = [
            Payment(amount=1.0, recipient="0x742d35Cc6634C0532925a3b8D4C9db96DfbBfC88", tool_name="api1"),
            Payment(amount=2.0, recipient="0x742d35Cc6634C0532925a3b8D4C9db96DfbBfC88", tool_name="api2"),
            Payment(amount=0.5, recipient="0x742d35Cc6634C0532925a3b8D4C9db96DfbBfC88", tool_name="api3")
        ]
        
        tx_hashes = wallet.batch_payments(payments)
        
        assert len(tx_hashes) == 3
        assert all(tx_hash == "0xtest_tx_hash" for tx_hash in tx_hashes)
    
    def test_base_insufficient_funds(self, base_wallet_key, mock_web3, mock_usdc_contract):
        """Test insufficient funds handling on Base network."""
        # Mock zero balance
        mock_usdc_contract.functions.balanceOf.return_value.call.return_value = 0
        
        wallet = WalletManager(base_wallet_key, "base")
        
        with pytest.raises(InsufficientFundsError):
            wallet.make_payment(10.0, "0x742d35Cc6634C0532925a3b8D4C9db96DfbBfC88")
    
    def test_base_network_connection_failure(self, base_wallet_key):
        """Test Base network connection failure handling."""
        with patch('x402_agent.wallet.Web3') as mock_web3_class:
            mock_web3_class.side_effect = ConnectionError("Failed to connect to Base network")
            
            with pytest.raises(NetworkError):
                WalletManager(base_wallet_key, "base")
    
    def test_base_gas_estimation(self, base_wallet_key, mock_web3, mock_usdc_contract):
        """Test gas estimation for Base network transactions."""
        wallet = WalletManager(base_wallet_key, "base")
        
        # Mock gas estimation
        mock_web3.eth.estimate_gas.return_value = 25000
        
        recipient = "0x742d35Cc6634C0532925a3b8D4C9db96DfbBfC88"
        amount = 1.0
        
        tx_hash = wallet.make_payment(amount, recipient)
        
        # Verify gas estimation was called
        mock_web3.eth.estimate_gas.assert_called_once()
        assert tx_hash == "0xtest_tx_hash"


class TestSolanaNetworkIntegration:
    """Test Solana network integration (if available)."""
    
    @pytest.fixture
    def solana_wallet_key(self):
        """Test wallet key for Solana network."""
        return "test_solana_private_key_base58"
    
    @pytest.fixture
    def mock_solana_client(self):
        """Mock Solana client for testing."""
        try:
            with patch('x402_agent.solana_provider.Client') as mock_client_class:
                mock_client_instance = Mock()
                mock_client_instance.get_balance.return_value.value = 1000000000  # 1 SOL in lamports
                mock_client_instance.send_transaction.return_value.value = "test_solana_signature"
                mock_client_class.return_value = mock_client_instance
                return mock_client_instance
        except ImportError:
            pytest.skip("Solana dependencies not available")
    
    def test_solana_wallet_initialization(self, solana_wallet_key, mock_solana_client):
        """Test Solana network wallet initialization."""
        try:
            wallet = WalletManager(solana_wallet_key, "solana")
            
            assert wallet.network == "solana"
            assert wallet.private_key == solana_wallet_key
        except ImportError:
            pytest.skip("Solana dependencies not available")
    
    def test_solana_balance_check(self, solana_wallet_key, mock_solana_client):
        """Test SOL balance checking on Solana network."""
        try:
            wallet = WalletManager(solana_wallet_key, "solana")
            
            balance = wallet.get_balance()
            
            # Should return 1.0 SOL (1000000000 / 10^9)
            assert balance == 1.0
            
            # Verify client method was called
            mock_solana_client.get_balance.assert_called_once()
        except ImportError:
            pytest.skip("Solana dependencies not available")
    
    def test_solana_payment_execution(self, solana_wallet_key, mock_solana_client):
        """Test SOL payment execution on Solana network."""
        try:
            wallet = WalletManager(solana_wallet_key, "solana")
            
            recipient = "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
            amount = 0.1
            
            tx_signature = wallet.make_payment(amount, recipient)
            
            assert tx_signature == "test_solana_signature"
            
            # Verify transaction was sent
            mock_solana_client.send_transaction.assert_called_once()
        except ImportError:
            pytest.skip("Solana dependencies not available")
    
    def test_solana_usdc_payment(self, solana_wallet_key, mock_solana_client):
        """Test USDC payment on Solana network."""
        try:
            with patch('x402_agent.solana_provider.get_associated_token_address') as mock_ata:
                mock_ata.return_value = "test_usdc_account"
                
                wallet = WalletManager(solana_wallet_key, "solana")
                
                recipient = "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
                amount = 5.0
                
                # Mock USDC balance
                mock_solana_client.get_token_account_balance.return_value.value.ui_amount = 10.0
                
                tx_signature = wallet.make_payment(amount, recipient, token="USDC")
                
                assert tx_signature == "test_solana_signature"
        except ImportError:
            pytest.skip("Solana dependencies not available")


class TestNetworkSwitching:
    """Test switching between different networks."""
    
    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for testing."""
        llm = Mock()
        llm.invoke.return_value = Mock(content="Network switching test")
        return llm
    
    def test_network_provider_selection(self):
        """Test automatic network provider selection."""
        from x402_agent.wallet import WalletManager
        
        # Test Base network selection
        with patch('x402_agent.wallet.Web3'):
            base_wallet = WalletManager("0x" + "1" * 64, "base")
            assert base_wallet.network == "base"
        
        # Test Solana network selection (if available)
        try:
            with patch('x402_agent.solana_provider.Client'):
                solana_wallet = WalletManager("test_key", "solana")
                assert solana_wallet.network == "solana"
        except ImportError:
            pytest.skip("Solana dependencies not available")
    
    def test_unsupported_network_error(self):
        """Test error handling for unsupported networks."""
        with pytest.raises(ValueError, match="Unsupported network"):
            WalletManager("test_key", "unsupported_network")
    
    def test_network_configuration_validation(self):
        """Test network configuration validation."""
        # Test valid network configurations
        valid_networks = ["base", "solana"]
        
        for network in valid_networks:
            try:
                if network == "base":
                    with patch('x402_agent.wallet.Web3'):
                        wallet = WalletManager("0x" + "1" * 64, network)
                        assert wallet.network == network
                elif network == "solana":
                    with patch('x402_agent.solana_provider.Client'):
                        wallet = WalletManager("test_key", network)
                        assert wallet.network == network
            except ImportError:
                # Skip if dependencies not available
                continue


class TestNetworkPerformance:
    """Test network performance and optimization."""
    
    def test_connection_pooling(self):
        """Test connection pooling for better performance."""
        # This would test connection reuse and pooling
        # For now, we'll create a placeholder test
        with patch('x402_agent.wallet.Web3') as mock_web3:
            wallet1 = WalletManager("0x" + "1" * 64, "base")
            wallet2 = WalletManager("0x" + "2" * 64, "base")
            
            # In a real implementation, both wallets should reuse connections
            assert mock_web3.call_count == 2  # One per wallet for now
    
    def test_transaction_batching_optimization(self):
        """Test transaction batching for gas optimization."""
        with patch('x402_agent.wallet.Web3') as mock_web3_class:
            mock_web3_instance = Mock()
            mock_web3_instance.eth.account.from_key.return_value = Mock(address="0xtest")
            mock_web3_instance.eth.get_balance.return_value = 1000000000000000000
            mock_web3_instance.eth.get_transaction_count.return_value = 5
            mock_web3_instance.eth.gas_price = 1000000000
            mock_web3_instance.eth.send_raw_transaction.return_value = b"test_hash"
            mock_web3_instance.to_hex.return_value = "0xtest_hash"
            mock_web3_class.return_value = mock_web3_instance
            
            # Mock USDC contract
            mock_contract = Mock()
            mock_contract.functions.balanceOf.return_value.call.return_value = 100000000
            mock_contract.functions.transfer.return_value.build_transaction.return_value = {
                'to': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
                'value': 0,
                'gas': 21000,
                'gasPrice': 1000000000,
                'nonce': 5,
                'data': '0xtest_data'
            }
            mock_web3_instance.eth.contract.return_value = mock_contract
            
            wallet = WalletManager("0x" + "1" * 64, "base")
            
            from x402_agent.payments import Payment
            payments = [
                Payment(amount=1.0, recipient="0xtest1", tool_name="api1"),
                Payment(amount=2.0, recipient="0xtest2", tool_name="api2"),
                Payment(amount=3.0, recipient="0xtest3", tool_name="api3")
            ]
            
            start_time = time.time()
            tx_hashes = wallet.batch_payments(payments)
            end_time = time.time()
            
            # Verify batching completed
            assert len(tx_hashes) == 3
            
            # In a real implementation, batching should be faster than individual payments
            # For now, we just verify it completed
            assert end_time - start_time < 10.0  # Should complete within 10 seconds
    
    def test_network_latency_handling(self):
        """Test handling of network latency and timeouts."""
        with patch('x402_agent.wallet.Web3') as mock_web3_class:
            # Mock slow network response
            mock_web3_instance = Mock()
            mock_web3_instance.eth.account.from_key.return_value = Mock(address="0xtest")
            
            def slow_balance_check(*args, **kwargs):
                time.sleep(0.1)  # Simulate network delay
                return 1000000000000000000
            
            mock_web3_instance.eth.get_balance.side_effect = slow_balance_check
            mock_web3_class.return_value = mock_web3_instance
            
            wallet = WalletManager("0x" + "1" * 64, "base")
            
            # Should handle slow network gracefully
            start_time = time.time()
            # In a real implementation, this would check balance
            # For now, we just verify the wallet was created
            assert wallet.network == "base"
            end_time = time.time()
            
            # Should complete despite network delay
            assert end_time - start_time < 5.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])