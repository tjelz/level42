"""
Utility functions and helpers for Level42 Framework.

This module provides common utilities, validation functions,
and helper classes used throughout the framework.
"""

import re
import hashlib
import secrets
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from enum import Enum


class PaymentStatus(Enum):
    """Payment transaction status."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NetworkType(Enum):
    """Supported blockchain networks."""
    BASE = "base"
    ETHEREUM = "ethereum"
    SOLANA = "solana"


def validate_private_key(private_key: str) -> bool:
    """
    Validate private key format.
    
    Args:
        private_key: Private key string to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not private_key:
        return False
    
    # Remove 0x prefix if present
    if private_key.startswith('0x'):
        private_key = private_key[2:]
    
    # Check if it's a valid hex string of correct length (64 characters for 32 bytes)
    if len(private_key) != 64:
        return False
    
    try:
        int(private_key, 16)
        return True
    except ValueError:
        return False


def validate_address(address: str, network: NetworkType = NetworkType.BASE) -> bool:
    """
    Validate blockchain address format.
    
    Args:
        address: Address string to validate
        network: Network type for validation
        
    Returns:
        True if valid format, False otherwise
    """
    if not address:
        return False
    
    if network in [NetworkType.BASE, NetworkType.ETHEREUM]:
        # Ethereum-style address validation
        if not address.startswith('0x'):
            return False
        
        if len(address) != 42:  # 0x + 40 hex characters
            return False
        
        try:
            int(address[2:], 16)
            return True
        except ValueError:
            return False
    
    elif network == NetworkType.SOLANA:
        # Solana address validation (base58, ~44 characters)
        if len(address) < 32 or len(address) > 44:
            return False
        
        # Basic character set validation for base58
        base58_chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        return all(c in base58_chars for c in address)
    
    return False


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if valid URL format, False otherwise
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None


def generate_transaction_id() -> str:
    """
    Generate unique transaction ID.
    
    Returns:
        Unique transaction ID string
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    random_bytes = secrets.token_bytes(16)
    combined = f"{timestamp}{random_bytes.hex()}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


def format_currency(amount: float, currency: str = "USDC", decimals: int = 6) -> str:
    """
    Format currency amount for display.
    
    Args:
        amount: Amount to format
        currency: Currency symbol
        decimals: Number of decimal places
        
    Returns:
        Formatted currency string
    """
    return f"{amount:.{decimals}f} {currency}"


def parse_http_402_headers(headers: Dict[str, str]) -> Dict[str, Any]:
    """
    Parse HTTP 402 response headers for payment information.
    
    Args:
        headers: HTTP response headers
        
    Returns:
        Dictionary with payment information
    """
    payment_info = {}
    
    # Standard L42 headers
    if 'X-Payment-Required' in headers:
        payment_info['required'] = True
    
    if 'X-Payment-Amount' in headers:
        try:
            payment_info['amount'] = float(headers['X-Payment-Amount'])
        except ValueError:
            payment_info['amount'] = 0.0
    
    if 'X-Payment-Address' in headers:
        payment_info['address'] = headers['X-Payment-Address']
    
    if 'X-Payment-Currency' in headers:
        payment_info['currency'] = headers['X-Payment-Currency']
    
    if 'X-Payment-Network' in headers:
        payment_info['network'] = headers['X-Payment-Network']
    
    return payment_info


def calculate_gas_estimate(network: NetworkType, transaction_type: str = "transfer") -> float:
    """
    Estimate gas costs for transactions.
    
    Args:
        network: Blockchain network
        transaction_type: Type of transaction
        
    Returns:
        Estimated gas cost in network's native currency
    """
    # Basic gas estimates - will be enhanced with real-time data in later tasks
    gas_estimates = {
        NetworkType.BASE: {
            "transfer": 0.0001,  # ETH
            "batch": 0.0005,
        },
        NetworkType.ETHEREUM: {
            "transfer": 0.002,  # ETH
            "batch": 0.01,
        },
        NetworkType.SOLANA: {
            "transfer": 0.000005,  # SOL
            "batch": 0.00002,
        }
    }
    
    return gas_estimates.get(network, {}).get(transaction_type, 0.001)


def retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        
    Returns:
        Decorated function
    """
    import time
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries:
                    raise e
                
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
        
        return None
    
    return wrapper