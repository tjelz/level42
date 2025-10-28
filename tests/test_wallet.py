"""
Unit tests for wallet management system.

Tests wallet initialization, balance checking, payment execution,
and batch payment processing.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from web3 import Web3
from eth_account import Account

from x402_agent.wallet import WalletManager, BaseNetworkProvider, Payment


class TestWalletManager:
    """Test cases for WalletManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Valid test private key (never use in production)
        self.valid_private_key = "0x" + "1" * 64
        self.invalid_private_key = "invalid_key"
        self.test_address = "0x742d35Cc6634C0532925a3b8D4C9db96C4b5Da5e"
        self.recipient_address = "0x8ba1f109551bD432803012645Hac136c5C1b5A5e"
    
    def test_wallet_initialization_valid_key(self):
        """Test wallet initialization with valid private key."""
        with patch.object(BaseNetworkProvider, '__init__', return_value=None), \
             patch.object(BaseNetworkProvider, 'get_balance', return_value=100.0):
            
            wallet = WalletManager(self.valid_private_key)
            
            assert wallet.private_key == self.valid_private_key
            assert wallet.network == "base"
            assert wallet.address is not None
    
    def test_wallet_initialization_invalid_key(self):
        """Test wallet initialization with invalid private key."""
        with pytest.raises(ValueError, match="Private key must be a 64-character hex string"):
            WalletManager(self.invalid_private_key)
    
    def test_wallet_initialization_empty_key(self):
        """Test wallet initialization with empty private key."""
        with pytest.raises(ValueError, match="Private key cannot be empty"):
            WalletManager("")
    
    def test_wallet_initialization_connection_failure(self):
        """Test wallet initialization with network connection failure."""
        with patch.object(BaseNetworkProvider, '__init__', side_effect=ConnectionError("Network error")):
            with pytest.raises(ConnectionError, match="Network error"):
                WalletManager(self.valid_private_key)
    
    def test_private_key_validation_with_prefix(self):
        """Test private key validation with 0x prefix."""
        with patch.object(BaseNetworkProvider, '__init__', return_value=None), \
             patch.object(BaseNetworkProvider, 'get_balance', return_value=100.0):
            
            wallet = WalletManager("0x" + "a" * 64)
            assert wallet.private_key == "0x" + "a" * 64
    
    def test_private_key_validation_without_prefix(self):
        """Test private key validation without 0x prefix."""
        with patch.object(BaseNetworkProvider, '__init__', return_value=None), \
             patch.object(BaseNetworkProvider, 'get_balance', return_value=100.0):
            
            wallet = WalletManager("a" * 64)
            assert wallet.private_key == "0x" + "a" * 64
    
    def test_get_balance_success(self):
        """Test successful balance retrieval."""
        with patch.object(BaseNetworkProvider, '__init__', return_value=None), \
             patch.object(BaseNetworkProvider, 'get_balance', return_value=150.5):
            
            wallet = WalletManager(self.valid_private_key)
            balance = wallet.get_balance()
            
            assert balance == 150.5
    
    def test_get_balance_failure(self):
        """Test balance retrieval failure."""
        with patch.object(BaseNetworkProvider, '__init__', return_value=None), \
             patch.object(BaseNetworkProvider, 'get_balance', side_effect=RuntimeError("Network error")):
            
            with pytest.raises(ConnectionError, match="Failed to initialize wallet"):
                WalletManager(self.valid_private_key)
    
    def test_make_payment_success(self):
        """Test successful payment execution."""
        with patch.object(BaseNetworkProvider, '__init__', return_value=None), \
             patch.object(BaseNetworkProvider, 'get_balance', return_value=100.0), \
             patch.object(BaseNetworkProvider, 'send_payment', return_value="0xabc123"):
            
            wallet = WalletManager(self.valid_private_key)
            tx_hash = wallet.make_payment(50.0, self.recipient_address)
            
            assert tx_hash == "0xabc123"
    
    def test_make_payment_insufficient_balance(self):
        """Test payment with insufficient balance."""
        with patch.object(BaseNetworkProvider, '__init__', return_value=None), \
             patch.object(BaseNetworkProvider, 'get_balance', return_value=10.0):
            
            wallet = WalletManager(self.valid_private_key)
            
            with pytest.raises(ValueError, match="Insufficient balance"):
                wallet.make_payment(50.0, self.recipient_address)
    
    def test_make_payment_invalid_amount(self):
        """Test payment with invalid amount."""
        with patch.object(BaseNetworkProvider, '__init__', return_value=None), \
             patch.object(BaseNetworkProvider, 'get_balance', return_value=100.0):
            
            wallet = WalletManager(self.valid_private_key)
            
            with pytest.raises(ValueError, match="Payment amount must be positive"):
                wallet.make_payment(-10.0, self.recipient_address)
    
    def test_batch_payments_success(self):
        """Test successful batch payment processing."""
        payments = [
            Payment(10.0, self.recipient_address, "tool1", datetime.now(), "pending"),
            Payment(20.0, self.recipient_address, "tool2", datetime.now(), "pending")
        ]
        
        with patch.object(BaseNetworkProvider, '__init__', return_value=None), \
             patch.object(BaseNetworkProvider, 'get_balance', return_value=100.0), \
             patch.object(BaseNetworkProvider, 'batch_payments', return_value=["0xabc123", "0xdef456"]):
            
            wallet = WalletManager(self.valid_private_key)
            tx_hashes = wallet.batch_payments(payments)
            
            assert len(tx_hashes) == 2
            assert tx_hashes == ["0xabc123", "0xdef456"]
    
    def test_batch_payments_insufficient_balance(self):
        """Test batch payments with insufficient balance."""
        payments = [
            Payment(50.0, self.recipient_address, "tool1", datetime.now(), "pending"),
            Payment(60.0, self.recipient_address, "tool2", datetime.now(), "pending")
        ]
        
        with patch.object(BaseNetworkProvider, '__init__', return_value=None), \
             patch.object(BaseNetworkProvider, 'get_balance', return_value=100.0):
            
            wallet = WalletManager(self.valid_private_key)
            
            with pytest.raises(ValueError, match="Insufficient balance for batch"):
                wallet.batch_payments(payments)
    
    def test_batch_payments_empty_list(self):
        """Test batch payments with empty payment list."""
        with patch.object(BaseNetworkProvider, '__init__', return_value=None), \
             patch.object(BaseNetworkProvider, 'get_balance', return_value=100.0):
            
            wallet = WalletManager(self.valid_private_key)
            tx_hashes = wallet.batch_payments([])
            
            assert tx_hashes == []
    
    def test_batch_payments_invalid_amount(self):
        """Test batch payments with invalid payment amount."""
        payments = [
            Payment(-10.0, self.recipient_address, "tool1", datetime.now(), "pending")
        ]
        
        with patch.object(BaseNetworkProvider, '__init__', return_value=None), \
             patch.object(BaseNetworkProvider, 'get_balance', return_value=100.0):
            
            wallet = WalletManager(self.valid_private_key)
            
            with pytest.raises(ValueError, match="Invalid payment amount"):
                wallet.batch_payments(payments)
    
    def test_get_address(self):
        """Test wallet address retrieval."""
        with patch.object(BaseNetworkProvider, '__init__', return_value=None), \
             patch.object(BaseNetworkProvider, 'get_balance', return_value=100.0):
            
            wallet = WalletManager(self.valid_private_key)
            address = wallet.get_address()
            
            assert address is not None
            assert address.startswith("0x")
            assert len(address) == 42


class TestBaseNetworkProvider:
    """Test cases for BaseNetworkProvider class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.valid_private_key = "0x" + "1" * 64
        self.test_address = "0x742d35Cc6634C0532925a3b8D4C9db96C4b5Da5e"
        self.recipient_address = "0x8ba1f109551bD432803012645Hac136c5C1b5A5e"
    
    @patch('x402_agent.wallet.Web3')
    def test_provider_initialization_success(self, mock_web3_class):
        """Test successful provider initialization."""
        mock_web3 = Mock()
        mock_web3.is_connected.return_value = True
        mock_web3.eth.contract.return_value = Mock()
        mock_web3_class.return_value = mock_web3
        
        provider = BaseNetworkProvider()
        
        assert provider.web3 == mock_web3
        mock_web3.is_connected.assert_called_once()
    
    @patch('x402_agent.wallet.Web3')
    def test_provider_initialization_connection_failure(self, mock_web3_class):
        """Test provider initialization with connection failure."""
        mock_web3 = Mock()
        mock_web3.is_connected.return_value = False
        mock_web3_class.return_value = mock_web3
        
        with pytest.raises(ConnectionError, match="Failed to connect to Base network"):
            BaseNetworkProvider()
    
    def test_get_balance_success(self):
        """Test successful balance retrieval."""
        with patch.object(BaseNetworkProvider, '__init__', return_value=None):
            provider = BaseNetworkProvider()
            
            # Mock the contract and web3 objects
            mock_contract = Mock()
            mock_contract.functions.balanceOf.return_value.call.return_value = 1000000  # 1 USDC
            provider.usdc_contract = mock_contract
            
            mock_web3 = Mock()
            mock_web3.is_address.return_value = True
            provider.web3 = mock_web3
            
            balance = provider.get_balance(self.test_address)
            
            assert balance == 1.0  # 1000000 / 10^6
    
    def test_get_balance_invalid_address(self):
        """Test balance retrieval with invalid address."""
        with patch.object(BaseNetworkProvider, '__init__', return_value=None):
            provider = BaseNetworkProvider()
            
            mock_web3 = Mock()
            mock_web3.is_address.return_value = False
            provider.web3 = mock_web3
            
            with pytest.raises(RuntimeError, match="Failed to get balance: Invalid address format"):
                provider.get_balance("invalid_address")
    
    def test_verify_transaction_success(self):
        """Test successful transaction verification."""
        with patch.object(BaseNetworkProvider, '__init__', return_value=None):
            provider = BaseNetworkProvider()
            
            mock_web3 = Mock()
            mock_receipt = Mock()
            mock_receipt.status = 1
            mock_web3.eth.get_transaction_receipt.return_value = mock_receipt
            provider.web3 = mock_web3
            
            result = provider.verify_transaction("0xabc123")
            
            assert result is True
    
    def test_verify_transaction_failure(self):
        """Test failed transaction verification."""
        with patch.object(BaseNetworkProvider, '__init__', return_value=None):
            provider = BaseNetworkProvider()
            
            mock_web3 = Mock()
            mock_receipt = Mock()
            mock_receipt.status = 0
            mock_web3.eth.get_transaction_receipt.return_value = mock_receipt
            provider.web3 = mock_web3
            
            result = provider.verify_transaction("0xabc123")
            
            assert result is False
    
    def test_verify_transaction_failed_hash(self):
        """Test verification of failed transaction hash."""
        with patch.object(BaseNetworkProvider, '__init__', return_value=None):
            provider = BaseNetworkProvider()
            
            result = provider.verify_transaction("FAILED: Network error")
            
            assert result is False


class TestNetworkProviders:
    """Test cases for network provider functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.valid_private_key = "0x" + "1" * 64
        self.solana_private_key = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtrzVHpcXkg"  # Example base58 key
        self.test_address = "0x742d35Cc6634C0532925a3b8D4C9db96C4b5Da5e"
        self.recipient_address = "0x8ba1f109551bD432803012645Hac136c5C1b5A5e"
    
    def test_get_supported_networks_base_only(self):
        """Test getting supported networks when only Base is available."""
        with patch('x402_agent.wallet.SOLANA_AVAILABLE', False):
            networks = WalletManager.get_supported_networks()
            assert "base" in networks
            assert "solana" not in networks
    
    def test_get_supported_networks_with_solana(self):
        """Test getting supported networks when Solana is available."""
        with patch('x402_agent.wallet.SOLANA_AVAILABLE', True), \
             patch('builtins.__import__', return_value=Mock()):
            networks = WalletManager.get_supported_networks()
            assert "base" in networks
            assert "solana" in networks
    
    def test_network_selection_base(self):
        """Test network selection for Base network."""
        with patch.object(BaseNetworkProvider, '__init__', return_value=None), \
             patch.object(BaseNetworkProvider, 'get_balance', return_value=100.0):
            
            wallet = WalletManager(self.valid_private_key, network="base")
            assert wallet.network == "base"
            assert isinstance(wallet.network_provider, BaseNetworkProvider)
    
    def test_network_selection_invalid(self):
        """Test network selection with invalid network."""
        with pytest.raises(ValueError, match="Unsupported network: invalid"):
            WalletManager(self.valid_private_key, network="invalid")
    
    def test_switch_network_success(self):
        """Test successful network switching."""
        with patch.object(BaseNetworkProvider, '__init__', return_value=None), \
             patch.object(BaseNetworkProvider, 'get_balance', return_value=100.0):
            
            wallet = WalletManager(self.valid_private_key, network="base")
            
            # Mock switching to same network (should be no-op)
            wallet.switch_network("base")
            assert wallet.network == "base"
    
    def test_switch_network_connection_failure(self):
        """Test network switching with connection failure."""
        with patch.object(BaseNetworkProvider, '__init__', return_value=None), \
             patch.object(BaseNetworkProvider, 'get_balance', return_value=100.0):
            
            wallet = WalletManager(self.valid_private_key, network="base")
            
            # Mock network provider that fails connection
            with patch.object(wallet, '_get_network_provider') as mock_get_provider:
                mock_provider = Mock()
                mock_provider.get_balance.side_effect = RuntimeError("Connection failed")
                mock_get_provider.return_value = mock_provider
                
                with pytest.raises(ConnectionError, match="Failed to connect to invalid network"):
                    wallet.switch_network("invalid")
    
    def test_get_network_info(self):
        """Test getting network information."""
        with patch.object(BaseNetworkProvider, '__init__', return_value=None), \
             patch.object(BaseNetworkProvider, 'get_balance', return_value=100.0):
            
            wallet = WalletManager(self.valid_private_key, network="base")
            info = wallet.get_network_info()
            
            assert info["network"] == "base"
            assert info["address"] == wallet.address
            assert info["provider_type"] == "BaseNetworkProvider"
            assert "supported_networks" in info
    
    def test_solana_private_key_validation(self):
        """Test Solana private key validation."""
        with patch('x402_agent.wallet.SOLANA_AVAILABLE', True), \
             patch('x402_agent.wallet.base58') as mock_base58:
            mock_base58.b58decode.return_value = b'x' * 64  # 64 bytes
            
            wallet = WalletManager.__new__(WalletManager)
            wallet.network = "solana"
            
            # Test validation
            result = wallet._validate_private_key(self.solana_private_key)
            assert result == self.solana_private_key
    
    def test_solana_private_key_validation_invalid(self):
        """Test Solana private key validation with invalid key."""
        with patch('x402_agent.wallet.SOLANA_AVAILABLE', True), \
             patch('x402_agent.wallet.base58') as mock_base58:
            mock_base58.b58decode.side_effect = Exception("Invalid base58")
            
            wallet = WalletManager.__new__(WalletManager)
            wallet.network = "solana"
            
            with pytest.raises(ValueError, match="Invalid Solana private key format"):
                wallet._validate_private_key("invalid_key")
    
    def test_solana_address_derivation(self):
        """Test Solana address derivation."""
        with patch('x402_agent.wallet.SOLANA_AVAILABLE', True), \
             patch('x402_agent.wallet.base58') as mock_base58, \
             patch('builtins.__import__') as mock_import:
            
            # Mock the solana.keypair module
            mock_keypair_class = Mock()
            mock_keypair = Mock()
            mock_keypair.public_key = "SolanaAddress123"
            mock_keypair_class.from_secret_key.return_value = mock_keypair
            
            # Mock the import to return our mock keypair class
            def import_side_effect(name, *args, **kwargs):
                if name == 'solana.keypair':
                    mock_module = Mock()
                    mock_module.Keypair = mock_keypair_class
                    return mock_module
                return Mock()
            
            mock_import.side_effect = import_side_effect
            mock_base58.b58decode.return_value = b'x' * 64
            
            wallet = WalletManager.__new__(WalletManager)
            wallet.network = "solana"
            
            address = wallet._derive_address(self.solana_private_key)
            assert address == "SolanaAddress123"
    
    def test_solana_address_derivation_missing_deps(self):
        """Test Solana address derivation with missing dependencies."""
        wallet = WalletManager.__new__(WalletManager)
        wallet.network = "solana"
        
        with patch('builtins.__import__', side_effect=ImportError):
            with pytest.raises(ValueError, match="Solana dependencies not installed"):
                wallet._derive_address(self.solana_private_key)


class TestSolanaNetworkProvider:
    """Test cases for SolanaNetworkProvider class (optional)."""
    
    def test_solana_provider_import_available(self):
        """Test that SolanaNetworkProvider can be imported when dependencies are available."""
        # This is a basic test to ensure the module structure is correct
        # More detailed testing would require actual Solana dependencies
        try:
            from x402_agent.solana_provider import SolanaNetworkProvider
            # If we get here, the import worked
            assert True
        except ImportError as e:
            # Expected when Solana dependencies are not installed
            assert "Solana dependencies not installed" in str(e)