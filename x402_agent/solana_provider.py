"""
Solana network provider for x402-Agent Framework.

This module provides Solana blockchain integration for micropayments
using SOL and SPL tokens.
"""

from typing import List, Dict, Any
from .wallet import NetworkProvider
import base58


class SolanaNetworkProvider(NetworkProvider):
    """Solana Network provider implementation."""
    
    # Solana network configuration
    SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
    USDC_MINT_ADDRESS = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC on Solana
    
    def __init__(self):
        """Initialize Solana network provider."""
        try:
            from solana.rpc.api import Client
            from solana.publickey import PublicKey
            from solana.keypair import Keypair
            from solana.transaction import Transaction
            from solana.system_program import transfer, TransferParams
            from spl.token.client import Token
            from spl.token.constants import TOKEN_PROGRAM_ID
        except ImportError:
            raise ImportError(
                "Solana dependencies not installed. "
                "Install with: pip install solana-py spl-token"
            )
        
        self.client = Client(self.SOLANA_RPC_URL)
        self.PublicKey = PublicKey
        self.Keypair = Keypair
        self.Transaction = Transaction
        self.transfer = transfer
        self.TransferParams = TransferParams
        self.Token = Token
        self.TOKEN_PROGRAM_ID = TOKEN_PROGRAM_ID
        
        # Test connection
        try:
            self.client.get_health()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Solana network: {str(e)}")
    
    def get_balance(self, address: str) -> float:
        """Get USDC balance on Solana network (primary balance for payments)."""
        # For consistency with Base network, return USDC balance as primary balance
        return self.get_usdc_balance(address)
    
    def get_sol_balance(self, address: str) -> float:
        """Get SOL balance on Solana network."""
        try:
            # Validate address format
            try:
                pubkey = self.PublicKey(address)
            except Exception:
                raise ValueError(f"Invalid Solana address format: {address}")
            
            # Get SOL balance (in lamports, 1 SOL = 1e9 lamports)
            response = self.client.get_balance(pubkey)
            balance_lamports = response['result']['value']
            balance_sol = balance_lamports / 1e9
            return balance_sol
        except Exception as e:
            raise RuntimeError(f"Failed to get SOL balance: {str(e)}")
    
    def get_usdc_balance(self, address: str) -> float:
        """Get USDC balance on Solana network."""
        try:
            # Validate address format
            try:
                pubkey = self.PublicKey(address)
            except Exception:
                raise ValueError(f"Invalid Solana address format: {address}")
            
            # Get USDC token accounts
            usdc_mint = self.PublicKey(self.USDC_MINT_ADDRESS)
            token_accounts = self.client.get_token_accounts_by_owner(
                pubkey, 
                {"mint": usdc_mint}
            )
            
            if not token_accounts['result']['value']:
                return 0.0
            
            # Get balance from first USDC token account
            token_account = token_accounts['result']['value'][0]['pubkey']
            balance_response = self.client.get_token_account_balance(token_account)
            balance_info = balance_response['result']['value']
            
            # USDC has 6 decimals
            balance_usdc = float(balance_info['amount']) / (10 ** balance_info['decimals'])
            return balance_usdc
        except Exception as e:
            raise RuntimeError(f"Failed to get USDC balance: {str(e)}")
    
    def send_payment(self, private_key: str, recipient: str, amount: float) -> str:
        """Send USDC payment on Solana network (primary payment method)."""
        # For consistency with Base network, use USDC as primary payment method
        return self.send_usdc_payment(private_key, recipient, amount)
        # For consistency with Base network, use USDC as primary payment method
        return self.send_usdc_payment(private_key, recipient, amount)
    
    def send_sol_payment(self, private_key: str, recipient: str, amount: float) -> str:
        """Send SOL payment on Solana network."""
        try:
            # Validate inputs
            if amount <= 0:
                raise ValueError("Payment amount must be positive")
            
            try:
                recipient_pubkey = self.PublicKey(recipient)
            except Exception:
                raise ValueError(f"Invalid recipient address: {recipient}")
            
            # Create keypair from private key
            try:
                # Decode base58 private key
                private_key_bytes = base58.b58decode(private_key)
                sender_keypair = self.Keypair.from_secret_key(private_key_bytes)
            except Exception:
                raise ValueError("Invalid private key format for Solana")
            
            # Convert amount to lamports
            amount_lamports = int(amount * 1e9)
            
            # Create transfer transaction
            transaction = self.Transaction()
            transfer_instruction = self.transfer(
                self.TransferParams(
                    from_pubkey=sender_keypair.public_key,
                    to_pubkey=recipient_pubkey,
                    lamports=amount_lamports
                )
            )
            transaction.add(transfer_instruction)
            
            # Get recent blockhash
            recent_blockhash = self.client.get_recent_blockhash()
            transaction.recent_blockhash = recent_blockhash['result']['value']['blockhash']
            
            # Sign and send transaction
            transaction.sign(sender_keypair)
            response = self.client.send_transaction(transaction)
            
            if 'error' in response:
                raise RuntimeError(f"Transaction failed: {response['error']}")
            
            tx_hash = response['result']
            
            # Wait for confirmation
            self._wait_for_confirmation(tx_hash)
            
            return tx_hash
        except Exception as e:
            raise RuntimeError(f"Failed to send SOL payment: {str(e)}")
    
    def send_usdc_payment(self, private_key: str, recipient: str, amount: float) -> str:
        """Send USDC payment on Solana network."""
        try:
            # Validate inputs
            if amount <= 0:
                raise ValueError("Payment amount must be positive")
            
            try:
                recipient_pubkey = self.PublicKey(recipient)
            except Exception:
                raise ValueError(f"Invalid recipient address: {recipient}")
            
            # Create keypair from private key
            try:
                private_key_bytes = base58.b58decode(private_key)
                sender_keypair = self.Keypair.from_secret_key(private_key_bytes)
            except Exception:
                raise ValueError("Invalid private key format for Solana")
            
            # Initialize USDC token
            usdc_mint = self.PublicKey(self.USDC_MINT_ADDRESS)
            token = self.Token(
                self.client,
                usdc_mint,
                self.TOKEN_PROGRAM_ID,
                sender_keypair
            )
            
            # Convert amount to token units (USDC has 6 decimals)
            amount_tokens = int(amount * (10 ** 6))
            
            # Send USDC transfer
            response = token.transfer(
                recipient_pubkey,
                amount_tokens,
                sender_keypair
            )
            
            tx_hash = response['result']
            
            # Wait for confirmation
            self._wait_for_confirmation(tx_hash)
            
            return tx_hash
        except Exception as e:
            raise RuntimeError(f"Failed to send USDC payment: {str(e)}")
    
    def batch_payments(self, private_key: str, payments: List[Dict]) -> List[str]:
        """Process multiple USDC payments in batch."""
        if not payments:
            return []
        
        tx_hashes = []
        
        # Process payments individually (Solana doesn't have native batch transfers)
        for payment in payments:
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    tx_hash = self.send_usdc_payment(
                        private_key,
                        payment['recipient'],
                        payment['amount']
                    )
                    tx_hashes.append(tx_hash)
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        # After max retries, record the failure
                        error_msg = f"FAILED after {max_retries} retries: {str(e)}"
                        tx_hashes.append(error_msg)
                    else:
                        # Wait before retry
                        import time
                        time.sleep(2 ** retry_count)
        
        return tx_hashes
    
    def _wait_for_confirmation(self, tx_hash: str, timeout: int = 60):
        """Wait for transaction confirmation."""
        import time
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.client.get_signature_statuses([tx_hash])
                status = response['result']['value'][0]
                
                if status is not None:
                    if status.get('err') is not None:
                        raise RuntimeError(f"Transaction failed: {status['err']}")
                    return  # Transaction confirmed
                
                time.sleep(1)  # Wait 1 second before checking again
            except Exception:
                time.sleep(1)
                continue
        
        raise RuntimeError(f"Transaction confirmation timeout after {timeout} seconds")
    
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
                
            response = self.client.get_signature_statuses([tx_hash])
            status = response['result']['value'][0]
            
            if status is None:
                return False  # Transaction not found
            
            return status.get('err') is None  # No error means success
        except Exception:
            return False