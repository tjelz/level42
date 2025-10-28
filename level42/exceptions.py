"""
Custom exceptions for Level42 Framework.

This module defines all custom exceptions used throughout the framework
for consistent error handling and reporting.
"""


class Level42Error(Exception):
    """Base exception for all Level42 Framework errors."""
    pass


class PaymentError(Level42Error):
    """Base exception for payment-related errors."""
    pass


class InsufficientFundsError(PaymentError):
    """Raised when wallet has insufficient funds for payment."""
    
    def __init__(self, required: float, available: float, message: str = None):
        self.required = required
        self.available = available
        if message is None:
            message = f"Insufficient funds: need {required} USDC, have {available} USDC (short by {required - available:.6f} USDC)"
        super().__init__(message)


class NetworkError(PaymentError):
    """Raised when network operations fail."""
    
    def __init__(self, message: str, retry_count: int = 0, max_retries: int = 3):
        self.retry_count = retry_count
        self.max_retries = max_retries
        super().__init__(f"Network error after {retry_count}/{max_retries} retries: {message}")


class TransactionError(PaymentError):
    """Raised when blockchain transaction fails."""
    
    def __init__(self, message: str, tx_hash: str = None):
        self.tx_hash = tx_hash
        if tx_hash:
            message = f"Transaction {tx_hash} failed: {message}"
        super().__init__(message)


class PaymentValidationError(PaymentError):
    """Raised when payment parameters are invalid."""
    pass


class ToolError(Level42Error):
    """Base exception for tool-related errors."""
    pass


class ToolRegistrationError(ToolError):
    """Raised when tool registration fails."""
    pass


class ToolExecutionError(ToolError):
    """Raised when tool execution fails."""
    
    def __init__(self, message: str = "Tool execution failed", tool_name: str = None):
        super().__init__(message)
        self.tool_name = tool_name


class AgentError(Level42Error):
    """Base exception for agent-related errors."""
    pass


class AgentConfigurationError(AgentError):
    """Raised when agent configuration is invalid."""
    pass


class SwarmError(Level42Error):
    """Base exception for swarm-related errors."""
    pass


class SwarmCoordinationError(SwarmError):
    """Raised when swarm coordination fails."""
    pass


class WalletError(Level42Error):
    """Base exception for wallet-related errors."""
    pass


class WalletConnectionError(WalletError):
    """Raised when wallet connection fails."""
    pass


class InvalidPrivateKeyError(WalletError):
    """Raised when private key is invalid."""
    pass


class HTTP402Error(Level42Error):
    """Raised when HTTP 402 response cannot be processed."""
    
    def __init__(self, message: str = "HTTP 402 processing failed", status_code: int = 402, headers: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.headers = headers or {}


class ConfigurationError(Level42Error):
    """Raised when configuration is invalid or missing."""
    pass


class AuthenticationError(Level42Error):
    """Raised when authentication fails."""
    pass


class RateLimitError(Level42Error):
    """Raised when rate limits are exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after