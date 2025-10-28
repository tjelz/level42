"""
Core agent functionality for Level42 Framework.

This module provides the main Level42Agent class that orchestrates AI agents
with automatic micropayment capabilities.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from .wallet import WalletManager
from .payments import PaymentProcessor
from .tools import ToolRegistry
from .monitoring import Level42Logger, DebugConfig, UsageAnalytics


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate_response(self, prompt: str, tools: Optional[List[Dict]] = None) -> str:
        """Generate response from LLM with optional tool calling."""
        pass


class Level42Agent:
    """
    Main agent class that provides autonomous AI agents with micropayment capabilities.
    
    This class integrates LLM providers with wallet management and payment processing
    to enable agents that can automatically pay for API access.
    """
    
    def __init__(self, llm: LLMProvider, wallet_key: str, network: str = "base", 
                 debug_config: DebugConfig = None):
        """
        Initialize agent with LLM and wallet.
        
        Args:
            llm: LLM provider instance
            wallet_key: Private key for wallet
            network: Blockchain network to use (default: "base")
            debug_config: Debug configuration for monitoring
        """
        self.llm = llm
        self.wallet_manager = WalletManager(wallet_key, network)
        self.payment_processor = PaymentProcessor(self.wallet_manager, debug_config=debug_config)
        self.tool_registry = ToolRegistry()
        self.agent_id = f"agent_{id(self)}"
        self.logger = Level42Logger(debug_config or DebugConfig())
        self.analytics = UsageAnalytics()
        self.session_id = self.analytics.start_session(self.agent_id)
    
    def register_tool(self, name: str, endpoint: str, description: str = "") -> None:
        """
        Register an external API as a tool.
        
        Args:
            name: Tool name
            endpoint: API endpoint URL
            description: Tool description
        """
        # Implementation will be added in later tasks
        pass
    
    def run(self, prompt: str) -> str:
        """
        Execute agent task with automatic payment handling.
        
        Args:
            prompt: Task prompt for the agent
            
        Returns:
            Agent response
        """
        # Implementation will be added in later tasks
        pass
    
    def get_balance(self) -> float:
        """
        Get current wallet balance in USDC.
        
        Returns:
            Current balance in USDC
        """
        return self.wallet_manager.get_balance()
    
    def transfer_to_agent(self, agent_id: str, amount: float) -> str:
        """
        Transfer funds to another agent in swarm.
        
        Args:
            agent_id: Target agent ID
            amount: Amount to transfer
            
        Returns:
            Transaction hash
        """
        # Implementation will be added in later tasks
        pass
    
    def enable_debug_mode(self, debug_config: DebugConfig = None):
        """
        Enable debug mode for comprehensive logging.
        
        Args:
            debug_config: Debug configuration (uses default if None)
        """
        if debug_config is None:
            debug_config = DebugConfig(enabled=True, log_level="DEBUG", verbose_errors=True)
        
        self.logger = Level42Logger(debug_config)
        self.payment_processor.enable_debug_mode(debug_config)
        
        self.logger.log_debug("Debug mode enabled for Level42Agent", {
            'agent_id': self.agent_id,
            'wallet_address': self.wallet_manager.get_address(),
            'network': self.wallet_manager.network
        })
    
    def get_usage_analytics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive usage analytics for this agent.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with usage analytics
        """
        return self.analytics.get_agent_summary(self.agent_id, days)
    
    def get_spending_report(self, days: int = 30) -> Dict[str, Any]:
        """
        Get spending report for this agent.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with spending report
        """
        return self.analytics.get_spending_report(self.agent_id, days)
    
    def get_debug_info(self) -> Dict[str, Any]:
        """
        Get comprehensive debug information.
        
        Returns:
            Dictionary with debug information
        """
        return {
            'agent_id': self.agent_id,
            'session_id': self.session_id,
            'wallet_info': self.wallet_manager.get_network_info(),
            'balance': self.get_balance(),
            'payment_processor': self.payment_processor.get_debug_info(),
            'registered_tools': len(self.tool_registry.tools) if hasattr(self.tool_registry, 'tools') else 0
        }
    
    def __del__(self):
        """Clean up resources when agent is destroyed."""
        try:
            if hasattr(self, 'analytics') and hasattr(self, 'session_id'):
                self.analytics.end_session(self.session_id)
        except:
            pass  # Ignore cleanup errors