"""
Wallet management system for Level42 Framework.

This module provides cryptocurrency wallet integration and management
for autonomous micropayments.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import re
import time
from web3 import Web3
from eth_account import Account
from cryptography.fernet import Fernet
import os

# Optional imports for Solana support
try:
    import base58
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False


@dataclass
class Payment:
    """Represents a payment transaction."""
    amount: float
    recipient: str
    tool_name: str
    timestamp: datetime
    status: str
    tx_hash: str = ""


class NetworkProvider(ABC):
    """Abstract base class for blockchain network providers."""
    
    @abstractmethod
    def get_balance(self, address: str) -> float:
        """Get wallet balance."""
        pass
    
    @abstractmethod
    def send_payment(self, private_key: str, recipient: str, amount: float) -> str:
        """Send payment and return transaction hash."""
        pass
    
    @abstractmethod
    def batch_payments(self, private_key: str, payments: List[Dict]) -> List[str]:
        """Process multiple payments in batch."""
        pass


class BaseNetworkProvider(NetworkProvider):
    """Base Network provider implementation."""
    
    # Base network configuration
    BASE_RPC_URL = "https://mainnet.base.org"
    BASE_CHAIN_ID = 8453
    USDC_CONTRACT_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    
    # USDC contract ABI (minimal for balance and transfer)
    USDC_ABI = [
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function"
        },
        {
            "constant": False,
            "inputs": [
                {"name": "_to", "type": "address"},
                {"name": "_value", "type": "uint256"}
            ],
            "name": "transfer",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "type": "function"
        }
    ]
    
    def __init__(self):
        """Initialize Base network provider."""
        self.web3 = Web3(Web3.HTTPProvider(self.BASE_RPC_URL))
        if not self.web3.is_connected():
            raise ConnectionError("Failed to connect to Base network")
        
        self.usdc_contract = self.web3.eth.contract(
            address=self.USDC_CONTRACT_ADDRESS,
            abi=self.USDC_ABI
        )
    
    def get_balance(self, address: str) -> float:
        """Get USDC balance on Base network."""
        try:
            # Validate address format
            if not self.web3.is_address(address):
                raise ValueError(f"Invalid address format: {address}")
            
            # Get USDC balance (6 decimals)
            balance_wei = self.usdc_contract.functions.balanceOf(address).call()
            balance_usdc = balance_wei / (10 ** 6)  # USDC has 6 decimals
            return balance_usdc
        except Exception as e:
            raise RuntimeError(f"Failed to get balance: {str(e)}")
    
    def send_payment(self, private_key: str, recipient: str, amount: float) -> str:
        """Send USDC payment on Base network with comprehensive error handling."""
        max_retries = 3
        base_delay = 1
        
        for attempt in range(max_retries):
            try:
                # Validate inputs
                if not self.web3.is_address(recipient):
                    raise ValueError(f"Invalid recipient address: {recipient}")
                
                if amount <= 0:
                    raise ValueError("Payment amount must be positive")
                
                # Get account from private key
                account = Account.from_key(private_key)
                
                # Convert amount to wei (USDC has 6 decimals)
                amount_wei = int(amount * (10 ** 6))
                
                # Get current nonce with retry logic
                nonce = None
                for nonce_attempt in range(3):
                    try:
                        nonce = self.web3.eth.get_transaction_count(account.address, 'pending')
                        break
                    except Exception as e:
                        if nonce_attempt == 2:
                            raise RuntimeError(f"Failed to get transaction nonce: {str(e)}")
                        time.sleep(0.5)
                
                # Estimate gas for the transaction with fallback
                gas_limit = 100000  # Default fallback
                try:
                    gas_estimate = self.usdc_contract.functions.transfer(
                        recipient, amount_wei
                    ).estimate_gas({'from': account.address})
                    # Add 20% buffer to gas estimate
                    gas_limit = int(gas_estimate * 1.2)
                except Exception as e:
                    # Log gas estimation failure but continue with fallback
                    import logging
                    logging.warning(f"Gas estimation failed, using fallback: {str(e)}")
                
                # Get current gas price with retry and fallback
                gas_price = None
                for gas_attempt in range(3):
                    try:
                        base_gas_price = self.web3.eth.gas_price
                        gas_price = int(base_gas_price * 1.1)  # 10% buffer for faster confirmation
                        break
                    except Exception as e:
                        if gas_attempt == 2:
                            # Use fallback gas price (20 gwei)
                            gas_price = 20 * 10**9
                            import logging
                            logging.warning(f"Gas price fetch failed, using fallback: {str(e)}")
                        else:
                            time.sleep(0.5)
                
                # Build transaction
                transaction = self.usdc_contract.functions.transfer(
                    recipient, amount_wei
                ).build_transaction({
                    'from': account.address,
                    'gas': gas_limit,
                    'gasPrice': gas_price,
                    'nonce': nonce,
                    'chainId': self.BASE_CHAIN_ID
                })
                
                # Sign and send transaction
                signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key)
                tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
                
                # Wait for transaction receipt to verify success
                try:
                    tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
                    
                    if tx_receipt.status != 1:
                        raise RuntimeError(f"Transaction failed on blockchain (status: {tx_receipt.status})")
                    
                    return tx_hash.hex()
                    
                except Exception as e:
                    if "timeout" in str(e).lower():
                        # Transaction might still be pending, return hash but log warning
                        import logging
                        logging.warning(f"Transaction receipt timeout, but transaction may still succeed: {tx_hash.hex()}")
                        return tx_hash.hex()
                    else:
                        raise
                
            except ValueError:
                # Don't retry validation errors
                raise
            except Exception as e:
                error_msg = str(e).lower()
                
                # Don't retry certain errors
                if any(term in error_msg for term in ["insufficient funds", "invalid", "nonce too low"]):
                    raise RuntimeError(f"Payment failed: {str(e)}")
                
                # Retry network-related errors
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    import logging
                    logging.warning(f"Payment attempt {attempt + 1} failed, retrying in {delay}s: {str(e)}")
                    time.sleep(delay)
                else:
                    raise RuntimeError(f"Payment failed after {max_retries} attempts: {str(e)}")
    
    def batch_payments(self, private_key: str, payments: List[Dict]) -> List[str]:
        """Process multiple USDC payments in batch."""
        if not payments:
            return []
        
        tx_hashes = []
        account = Account.from_key(private_key)
        
        # Get starting nonce
        base_nonce = self.web3.eth.get_transaction_count(account.address, 'pending')
        
        # Process payments with sequential nonces for better reliability
        for i, payment in enumerate(payments):
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # Validate payment
                    if not self.web3.is_address(payment['recipient']):
                        raise ValueError(f"Invalid recipient address: {payment['recipient']}")
                    
                    if payment['amount'] <= 0:
                        raise ValueError("Payment amount must be positive")
                    
                    # Convert amount to wei (USDC has 6 decimals)
                    amount_wei = int(payment['amount'] * (10 ** 6))
                    
                    # Use sequential nonce for batch processing
                    nonce = base_nonce + i
                    
                    # Estimate gas for this specific transaction
                    try:
                        gas_estimate = self.usdc_contract.functions.transfer(
                            payment['recipient'], amount_wei
                        ).estimate_gas({'from': account.address})
                        gas_limit = int(gas_estimate * 1.2)
                    except Exception:
                        gas_limit = 100000
                    
                    # Get current gas price
                    base_gas_price = self.web3.eth.gas_price
                    gas_price = int(base_gas_price * 1.1)
                    
                    # Build transaction
                    transaction = self.usdc_contract.functions.transfer(
                        payment['recipient'], amount_wei
                    ).build_transaction({
                        'from': account.address,
                        'gas': gas_limit,
                        'gasPrice': gas_price,
                        'nonce': nonce,
                        'chainId': self.BASE_CHAIN_ID
                    })
                    
                    # Sign and send transaction
                    signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key)
                    tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
                    
                    tx_hashes.append(tx_hash.hex())
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        # After max retries, record the failure
                        error_msg = f"FAILED after {max_retries} retries: {str(e)}"
                        tx_hashes.append(error_msg)
                    else:
                        # Wait before retry (exponential backoff)
                        import time
                        time.sleep(2 ** retry_count)
        
        return tx_hashes
    
    def verify_transaction(self, tx_hash: str) -> bool:
        """
        Verify if a transaction was successful.
        
        Args:
            tx_hash: Transaction hash to verify
            
        Returns:
            True if transaction was successful, False otherwise
        """
        try:
            if tx_hash.startswith("FAILED"):
                return False
                
            tx_receipt = self.web3.eth.get_transaction_receipt(tx_hash)
            return tx_receipt.status == 1
        except Exception:
            return False


class WalletManager:
    """
    Manages cryptocurrency wallet operations for agents.
    
    Provides secure wallet management with support for multiple blockchain networks
    and automatic payment processing.
    """
    
    def __init__(self, private_key: str, network: str = "base"):
        """
        Initialize wallet with private key and network.
        
        Args:
            private_key: Wallet private key (hex string with or without 0x prefix)
            network: Blockchain network to use
            
        Raises:
            ValueError: If private key is invalid or network is unsupported
            ConnectionError: If unable to connect to blockchain network
        """
        # Set network first so validation can use it
        self.network = network.lower()
        
        # Validate and normalize private key
        self.private_key = self._validate_private_key(private_key)
        self.network_provider = self._get_network_provider(network)
        self.address = self._derive_address(self.private_key)
        
        # Verify wallet can connect and get balance
        try:
            self.get_balance()
        except Exception as e:
            raise ConnectionError(f"Failed to initialize wallet: {str(e)}")
    
    def _validate_private_key(self, private_key: str) -> str:
        """
        Validate and normalize private key format.
        
        Args:
            private_key: Private key string
            
        Returns:
            Normalized private key
            
        Raises:
            ValueError: If private key is invalid
        """
        if not private_key:
            raise ValueError("Private key cannot be empty")
        
        # For Solana networks, keep base58 format
        if self.network == "solana":
            if not SOLANA_AVAILABLE:
                raise ValueError("Solana support not available. Install with: pip install base58")
            try:
                # Validate base58 format and length
                decoded = base58.b58decode(private_key)
                if len(decoded) != 64:  # Solana private keys are 64 bytes
                    raise ValueError("Solana private key must be 64 bytes when decoded")
                return private_key
            except Exception:
                raise ValueError("Invalid Solana private key format (must be base58)")
        
        # For Ethereum-based networks (Base, etc.)
        # Remove 0x prefix if present
        key = private_key.lower()
        if key.startswith('0x'):
            key = key[2:]
        
        # Validate hex format and length (64 characters for 32 bytes)
        if not re.match(r'^[0-9a-f]{64}$', key):
            raise ValueError("Private key must be a 64-character hex string")
        
        # Add 0x prefix back
        return '0x' + key
    
    def _get_network_provider(self, network: str) -> NetworkProvider:
        """Get network provider for specified network."""
        network = network.lower()
        
        if network == "base":
            return BaseNetworkProvider()
        elif network == "solana":
            try:
                from .solana_provider import SolanaNetworkProvider
                return SolanaNetworkProvider()
            except ImportError:
                raise ValueError("Solana support not available. Install solana dependencies.")
        else:
            raise ValueError(f"Unsupported network: {network}. Supported networks: base, solana")
    
    @classmethod
    def get_supported_networks(cls) -> List[str]:
        """Get list of supported blockchain networks."""
        networks = ["base"]
        
        # Check if optional Solana support is available
        if SOLANA_AVAILABLE:
            try:
                import solana
                networks.append("solana")
            except ImportError:
                pass
            
        return networks
    
    def _derive_address(self, private_key: str) -> str:
        """
        Derive wallet address from private key.
        
        Args:
            private_key: Validated private key
            
        Returns:
            Wallet address (format depends on network)
        """
        try:
            if self.network == "solana":
                if not SOLANA_AVAILABLE:
                    raise ValueError("Solana support not available")
                try:
                    from solana.keypair import Keypair
                    
                    # Decode base58 private key
                    private_key_bytes = base58.b58decode(private_key)
                    keypair = Keypair.from_secret_key(private_key_bytes)
                    return str(keypair.public_key)
                except ImportError:
                    raise ValueError("Solana dependencies not installed")
            else:
                # Ethereum-based networks
                account = Account.from_key(private_key)
                return account.address
        except Exception as e:
            raise ValueError(f"Failed to derive address from private key: {str(e)}")
    
    def get_balance(self) -> float:
        """
        Get current USDC balance.
        
        Returns:
            Current balance in USDC
            
        Raises:
            RuntimeError: If balance check fails
        """
        return self.network_provider.get_balance(self.address)
    
    def make_payment(self, amount: float, recipient: str) -> str:
        """
        Execute payment and return transaction hash.
        
        Args:
            amount: Payment amount in USDC (must be positive)
            recipient: Recipient address (must be valid Ethereum address)
            
        Returns:
            Transaction hash
            
        Raises:
            ValueError: If amount or recipient is invalid or insufficient funds
            RuntimeError: If payment fails due to network or transaction issues
        """
        if amount <= 0:
            raise ValueError("Payment amount must be positive")
        
        # Check sufficient balance with retry logic for network issues
        max_balance_retries = 3
        current_balance = None
        
        for attempt in range(max_balance_retries):
            try:
                current_balance = self.get_balance()
                break
            except Exception as e:
                if attempt == max_balance_retries - 1:
                    raise RuntimeError(f"Failed to check balance after {max_balance_retries} attempts: {str(e)}")
                time.sleep(1 * (2 ** attempt))  # Exponential backoff
        
        if current_balance < amount:
            raise ValueError(f"Insufficient balance: {current_balance} USDC, need {amount} USDC")
        
        # Attempt payment with error handling
        try:
            return self.network_provider.send_payment(self.private_key, recipient, amount)
        except Exception as e:
            error_msg = str(e).lower()
            if "insufficient" in error_msg or "balance" in error_msg:
                # Re-check balance in case it changed
                try:
                    updated_balance = self.get_balance()
                    raise ValueError(f"Insufficient balance: {updated_balance} USDC, need {amount} USDC")
                except:
                    raise ValueError(f"Insufficient balance for payment: {str(e)}")
            else:
                raise RuntimeError(f"Payment failed: {str(e)}")
    
    def batch_payments(self, payments: List[Payment]) -> List[str]:
        """
        Process multiple payments in single transaction with comprehensive error handling.
        
        Args:
            payments: List of payments to process
            
        Returns:
            List of transaction hashes (may contain "FAILED: reason" for failed payments)
            
        Raises:
            ValueError: If any payment is invalid or insufficient funds
            RuntimeError: If batch processing fails completely
        """
        if not payments:
            return []
        
        # Validate all payments first
        total_amount = 0
        for i, payment in enumerate(payments):
            if payment.amount <= 0:
                raise ValueError(f"Invalid payment amount at index {i}: {payment.amount}")
            if not payment.recipient:
                raise ValueError(f"Invalid recipient at index {i}: empty recipient")
            total_amount += payment.amount
        
        # Check sufficient balance for all payments with retry logic
        max_balance_retries = 3
        current_balance = None
        
        for attempt in range(max_balance_retries):
            try:
                current_balance = self.get_balance()
                break
            except Exception as e:
                if attempt == max_balance_retries - 1:
                    raise RuntimeError(f"Failed to check balance for batch payment after {max_balance_retries} attempts: {str(e)}")
                time.sleep(1 * (2 ** attempt))  # Exponential backoff
        
        if current_balance < total_amount:
            raise ValueError(f"Insufficient balance for batch: {current_balance} USDC, need {total_amount} USDC")
        
        payment_data = [
            {"recipient": p.recipient, "amount": p.amount}
            for p in payments
        ]
        
        try:
            return self.network_provider.batch_payments(self.private_key, payment_data)
        except Exception as e:
            error_msg = str(e).lower()
            if "insufficient" in error_msg or "balance" in error_msg:
                # Re-check balance in case it changed during processing
                try:
                    updated_balance = self.get_balance()
                    raise ValueError(f"Insufficient balance for batch: {updated_balance} USDC, need {total_amount} USDC")
                except:
                    raise ValueError(f"Insufficient balance for batch payment: {str(e)}")
            else:
                raise RuntimeError(f"Batch payment failed: {str(e)}")
    
    def get_address(self) -> str:
        """
        Get wallet address.
        
        Returns:
            Wallet address
        """
        return self.address
    
    def switch_network(self, network: str):
        """
        Switch to a different blockchain network.
        
        Args:
            network: Network name to switch to
            
        Raises:
            ValueError: If network is unsupported
            ConnectionError: If unable to connect to new network
        """
        if network.lower() == self.network.lower():
            return  # Already on this network
        
        # Create new network provider
        new_provider = self._get_network_provider(network)
        
        # Test connection by getting balance
        try:
            new_provider.get_balance(self.address)
        except Exception as e:
            raise ConnectionError(f"Failed to connect to {network} network: {str(e)}")
        
        # Switch to new network
        self.network = network.lower()
        self.network_provider = new_provider
    
    def get_network_info(self) -> Dict[str, Any]:
        """
        Get information about current network.
        
        Returns:
            Dictionary with network information
        """
        return {
            "network": self.network,
            "address": self.address,
            "provider_type": type(self.network_provider).__name__,
            "supported_networks": self.get_supported_networks()
        }