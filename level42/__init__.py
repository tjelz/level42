"""
Level42 Framework

A lightweight Python framework for building autonomous AI agents that can pay for tools, 
APIs, and other agents in real-time using L42 micropayments.
"""

__version__ = "0.1.0"
__author__ = "Level42 Framework Team"

from .agent import Level42Agent
from .wallet import WalletManager
from .payments import PaymentProcessor
from .tools import Tool, ToolRegistry
from .swarm import AgentSwarm
from .exceptions import (
    Level42Error,
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
    "Level42Agent",
    "WalletManager", 
    "PaymentProcessor",
    "Tool",
    "ToolRegistry",
    "AgentSwarm",
    # Exceptions
    "Level42Error",
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