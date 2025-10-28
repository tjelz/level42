"""
x402-Agent Framework

A lightweight Python framework for building autonomous AI agents that can pay for tools, 
APIs, and other agents in real-time using x402 micropayments.
"""

__version__ = "0.1.0"
__author__ = "x402-Agent Framework Team"

from .agent import X402Agent
from .wallet import WalletManager
from .payments import PaymentProcessor
from .tools import Tool, ToolRegistry
from .swarm import AgentSwarm
from .exceptions import (
    X402AgentError,
    PaymentError,
    InsufficientFundsError,
    NetworkError,
    TransactionError,
    PaymentValidationError,
    ToolError,
    ToolRegistrationError,
    ToolExecutionError,
    AgentError,
    AgentConfigurationError,
    SwarmError,
    SwarmCoordinationError,
    WalletError,
    WalletConnectionError,
    InvalidPrivateKeyError,
    HTTP402Error,
    ConfigurationError,
    AuthenticationError,
    RateLimitError
)

__all__ = [
    "X402Agent",
    "WalletManager", 
    "PaymentProcessor",
    "Tool",
    "ToolRegistry",
    "AgentSwarm",
    # Exceptions
    "X402AgentError",
    "PaymentError",
    "InsufficientFundsError",
    "NetworkError",
    "TransactionError",
    "PaymentValidationError",
    "ToolError",
    "ToolRegistrationError",
    "ToolExecutionError",
    "AgentError",
    "AgentConfigurationError",
    "SwarmError",
    "SwarmCoordinationError",
    "WalletError",
    "WalletConnectionError",
    "InvalidPrivateKeyError",
    "HTTP402Error",
    "ConfigurationError",
    "AuthenticationError",
    "RateLimitError"
]