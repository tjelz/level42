"""
Multi-agent swarm coordination system.

This module provides capabilities for multiple agents to collaborate,
share costs, and coordinate tasks.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum


class CostSplittingMethod(Enum):
    """Methods for splitting costs among swarm agents."""
    EQUAL = "equal"
    USAGE_BASED = "usage_based"
    MANUAL = "manual"


@dataclass
class SwarmConfig:
    """Configuration for agent swarm."""
    shared_wallet: bool = False
    cost_splitting_method: CostSplittingMethod = CostSplittingMethod.EQUAL
    max_agents: int = 10


class AgentSwarm:
    """
    Coordinates multiple x402-Agents for collaborative tasks.
    
    Enables multiple agents to work together, share costs, and
    coordinate their activities for complex multi-agent scenarios.
    """
    
    def __init__(self, shared_wallet: Optional[bool] = None, config: Optional[SwarmConfig] = None):
        """
        Initialize swarm with shared/individual wallet options.
        
        Args:
            shared_wallet: Whether agents share a single wallet (overrides config if provided)
            config: Swarm configuration, uses defaults if None
        """
        if config is None:
            config = SwarmConfig(shared_wallet=shared_wallet if shared_wallet is not None else False)
        else:
            # Only override shared_wallet if it was explicitly provided
            if shared_wallet is not None:
                config.shared_wallet = shared_wallet
            
        self.config = config
        self.agents: Dict[str, Any] = {}  # Will be X402Agent instances
        self.agent_spending: Dict[str, float] = {}
        self.swarm_id = f"swarm_{id(self)}"
        self.shared_wallet_manager = None
        
        # Initialize shared wallet if requested
        if self.config.shared_wallet:
            # Shared wallet will be set when first agent is added
            pass
    
    def add_agent(self, agent: Any) -> None:  # agent: X402Agent
        """
        Add agent to swarm membership.
        
        Args:
            agent: X402Agent instance to add
            
        Raises:
            ValueError: If swarm is at capacity or agent already exists
        """
        if len(self.agents) >= self.config.max_agents:
            raise ValueError(f"Swarm at maximum capacity ({self.config.max_agents})")
        
        agent_id = agent.agent_id
        if agent_id in self.agents:
            raise ValueError(f"Agent {agent_id} already in swarm")
        
        # Set up shared wallet if this is the first agent and shared wallet is enabled
        if self.config.shared_wallet and not self.shared_wallet_manager:
            self.shared_wallet_manager = agent.wallet_manager
        
        # If using shared wallet, replace agent's wallet manager
        if self.config.shared_wallet and self.shared_wallet_manager:
            agent.wallet_manager = self.shared_wallet_manager
            agent.payment_processor.wallet_manager = self.shared_wallet_manager
        
        self.agents[agent_id] = agent
        self.agent_spending[agent_id] = 0.0
        
        # Set swarm reference in agent for communication
        agent._swarm = self
    
    def remove_agent(self, agent_id: str) -> bool:
        """
        Remove agent from swarm.
        
        Args:
            agent_id: ID of agent to remove
            
        Returns:
            True if agent was removed, False if not found
        """
        if agent_id in self.agents:
            # Remove swarm reference from agent
            if hasattr(self.agents[agent_id], '_swarm'):
                delattr(self.agents[agent_id], '_swarm')
            
            del self.agents[agent_id]
            del self.agent_spending[agent_id]
            return True
        return False
    
    def discover_agents(self, query: Optional[str] = None) -> List[str]:
        """
        Discover agents in the swarm with optional query filtering.
        
        Args:
            query: Optional query to filter agents
            
        Returns:
            List of agent IDs matching query
        """
        if query is None:
            return list(self.agents.keys())
        
        # Simple query matching against agent IDs
        matching_agents = []
        for agent_id in self.agents.keys():
            if query.lower() in agent_id.lower():
                matching_agents.append(agent_id)
        
        return matching_agents
    
    def get_agent(self, agent_id: str) -> Optional[Any]:
        """
        Get agent instance by ID.
        
        Args:
            agent_id: Agent ID to retrieve
            
        Returns:
            Agent instance or None if not found
        """
        return self.agents.get(agent_id)
    
    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        """
        List all agents with their basic information.
        
        Returns:
            Dictionary mapping agent IDs to agent info
        """
        agent_info = {}
        for agent_id, agent in self.agents.items():
            agent_info[agent_id] = {
                'agent_id': agent_id,
                'balance': agent.get_balance(),
                'spending': self.agent_spending[agent_id],
                'tools_registered': len(getattr(agent.tool_registry, 'tools', {}))
            }
        return agent_info
    
    def send_message(self, from_agent_id: str, to_agent_id: str, message: str) -> bool:
        """
        Send message between agents in swarm for communication.
        
        Args:
            from_agent_id: Sender agent ID
            to_agent_id: Recipient agent ID
            message: Message content
            
        Returns:
            True if message sent successfully
            
        Raises:
            ValueError: If agents not found in swarm
        """
        if from_agent_id not in self.agents:
            raise ValueError(f"Sender agent {from_agent_id} not in swarm")
        if to_agent_id not in self.agents:
            raise ValueError(f"Recipient agent {to_agent_id} not in swarm")
        
        # Simple message passing - in a real implementation this could be more sophisticated
        recipient_agent = self.agents[to_agent_id]
        
        # Add message to agent's message queue if it exists
        if not hasattr(recipient_agent, '_message_queue'):
            recipient_agent._message_queue = []
        
        recipient_agent._message_queue.append({
            'from': from_agent_id,
            'message': message,
            'timestamp': __import__('datetime').datetime.now()
        })
        
        return True
    
    def broadcast_message(self, from_agent_id: str, message: str) -> int:
        """
        Broadcast message to all agents in swarm.
        
        Args:
            from_agent_id: Sender agent ID
            message: Message content
            
        Returns:
            Number of agents that received the message
        """
        if from_agent_id not in self.agents:
            raise ValueError(f"Sender agent {from_agent_id} not in swarm")
        
        recipients = 0
        for agent_id in self.agents:
            if agent_id != from_agent_id:  # Don't send to self
                try:
                    self.send_message(from_agent_id, agent_id, message)
                    recipients += 1
                except Exception:
                    # Continue broadcasting even if one fails
                    pass
        
        return recipients
    
    def collaborate(self, task: str, distribution_strategy: str = "parallel") -> str:
        """
        Execute collaborative task across agents with task distribution and result aggregation.
        
        Args:
            task: Task description for collaborative execution
            distribution_strategy: How to distribute task ("parallel", "sequential", "divide")
            
        Returns:
            Aggregated result from all agents
            
        Raises:
            ValueError: If no agents in swarm or invalid strategy
        """
        if not self.agents:
            raise ValueError("No agents in swarm for collaboration")
        
        results = {}
        errors = {}
        
        try:
            if distribution_strategy == "parallel":
                # All agents work on the same task simultaneously
                results = self._execute_parallel_collaboration(task)
            
            elif distribution_strategy == "sequential":
                # Agents work on task one after another, building on previous results
                results = self._execute_sequential_collaboration(task)
            
            elif distribution_strategy == "divide":
                # Divide task among agents
                results = self._execute_divided_collaboration(task)
            
            else:
                raise ValueError(f"Unknown distribution strategy: {distribution_strategy}")
        
        except Exception as e:
            errors['collaboration_error'] = str(e)
        
        # Aggregate results
        return self._aggregate_results(results, errors)
    
    def _execute_parallel_collaboration(self, task: str) -> Dict[str, str]:
        """Execute task in parallel across all agents."""
        results = {}
        
        for agent_id, agent in self.agents.items():
            try:
                # Each agent works on the full task
                result = agent.run(task)
                results[agent_id] = result
            except Exception as e:
                results[agent_id] = f"ERROR: {str(e)}"
        
        return results
    
    def _execute_sequential_collaboration(self, task: str) -> Dict[str, str]:
        """Execute task sequentially, with each agent building on previous results."""
        results = {}
        current_context = task
        
        for agent_id, agent in self.agents.items():
            try:
                # Each agent gets the task plus context from previous agents
                enhanced_task = f"{current_context}\n\nPrevious results: {results}"
                result = agent.run(enhanced_task)
                results[agent_id] = result
                
                # Update context for next agent
                current_context = f"{task}\n\nBuilding on: {result}"
                
            except Exception as e:
                results[agent_id] = f"ERROR: {str(e)}"
                # Continue with other agents even if one fails
        
        return results
    
    def _execute_divided_collaboration(self, task: str) -> Dict[str, str]:
        """Divide task among agents based on their capabilities."""
        results = {}
        
        # Simple task division - split by sentences or logical parts
        task_parts = self._divide_task(task, len(self.agents))
        
        for i, (agent_id, agent) in enumerate(self.agents.items()):
            try:
                if i < len(task_parts):
                    subtask = task_parts[i]
                    result = agent.run(f"Work on this part of the task: {subtask}")
                    results[agent_id] = result
                else:
                    results[agent_id] = "No subtask assigned"
            except Exception as e:
                results[agent_id] = f"ERROR: {str(e)}"
        
        return results
    
    def _divide_task(self, task: str, num_parts: int) -> List[str]:
        """Divide task into parts for distributed execution."""
        # Simple division by sentences
        sentences = task.split('. ')
        if len(sentences) <= num_parts:
            return sentences
        
        # Group sentences into roughly equal parts
        part_size = len(sentences) // num_parts
        parts = []
        
        for i in range(num_parts):
            start_idx = i * part_size
            if i == num_parts - 1:  # Last part gets remaining sentences
                end_idx = len(sentences)
            else:
                end_idx = (i + 1) * part_size
            
            part = '. '.join(sentences[start_idx:end_idx])
            if part and not part.endswith('.'):
                part += '.'
            parts.append(part)
        
        return parts
    
    def _aggregate_results(self, results: Dict[str, str], errors: Dict[str, str]) -> str:
        """Aggregate results from multiple agents into final response."""
        if not results and not errors:
            return "No results from collaboration"
        
        aggregated = "=== SWARM COLLABORATION RESULTS ===\n\n"
        
        # Add successful results
        if results:
            for agent_id, result in results.items():
                aggregated += f"Agent {agent_id}:\n{result}\n\n"
        
        # Add error summary if any
        if errors:
            aggregated += "=== ERRORS ===\n"
            for error_type, error_msg in errors.items():
                aggregated += f"{error_type}: {error_msg}\n"
        
        # Add summary
        successful_agents = len([r for r in results.values() if not r.startswith("ERROR:")])
        total_agents = len(self.agents)
        
        aggregated += f"\n=== SUMMARY ===\n"
        aggregated += f"Successful agents: {successful_agents}/{total_agents}\n"
        aggregated += f"Swarm ID: {self.swarm_id}\n"
        
        return aggregated
    
    def collaborate_with_recovery(self, task: str, max_retries: int = 2) -> str:
        """
        Execute collaborative task with swarm-level error handling and recovery.
        
        Args:
            task: Task description
            max_retries: Maximum number of retry attempts
            
        Returns:
            Aggregated result with recovery information
        """
        attempt = 0
        last_error = None
        
        while attempt <= max_retries:
            try:
                result = self.collaborate(task)
                
                # Check if we got meaningful results
                if "ERROR:" not in result or "Successful agents: 0/" not in result:
                    return result
                
                # If we got errors, try recovery
                if attempt < max_retries:
                    self._attempt_recovery()
                    attempt += 1
                    continue
                else:
                    break
                    
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    self._attempt_recovery()
                    attempt += 1
                else:
                    break
        
        # Final attempt failed
        recovery_msg = f"\n=== RECOVERY ATTEMPTED ===\nFailed after {max_retries + 1} attempts."
        if last_error:
            recovery_msg += f"\nLast error: {str(last_error)}"
        
        return f"COLLABORATION FAILED{recovery_msg}"
    
    def _attempt_recovery(self) -> None:
        """Attempt to recover from collaboration failures."""
        # Simple recovery strategies
        
        # 1. Check agent balances and redistribute if needed
        low_balance_agents = []
        high_balance_agents = []
        
        for agent_id, agent in self.agents.items():
            balance = agent.get_balance()
            if balance < 0.01:  # Less than 1 cent
                low_balance_agents.append(agent_id)
            elif balance > 1.0:  # More than $1
                high_balance_agents.append(agent_id)
        
        # Transfer funds from high balance to low balance agents
        if low_balance_agents and high_balance_agents:
            for low_agent in low_balance_agents:
                if high_balance_agents:
                    high_agent = high_balance_agents[0]
                    try:
                        self.transfer_to_agent(high_agent, low_agent, 0.1)  # Transfer 10 cents
                    except Exception:
                        pass  # Continue recovery even if transfer fails
        
        # 2. Clear any message queues that might be causing issues
        for agent in self.agents.values():
            if hasattr(agent, '_message_queue'):
                agent._message_queue = []
    
    def split_costs(self, total_cost: float, method: Optional[CostSplittingMethod] = None) -> Dict[str, float]:
        """
        Distribute costs among swarm agents with equal and usage-based options.
        
        Args:
            total_cost: Total cost to split
            method: Override default cost splitting method
            
        Returns:
            Dictionary mapping agent_id to cost share
        """
        if not self.agents:
            return {}
        
        splitting_method = method or self.config.cost_splitting_method
        cost_distribution = {}
        
        if splitting_method == CostSplittingMethod.EQUAL:
            cost_per_agent = total_cost / len(self.agents)
            for agent_id in self.agents:
                cost_distribution[agent_id] = cost_per_agent
        
        elif splitting_method == CostSplittingMethod.USAGE_BASED:
            total_spending = sum(self.agent_spending.values())
            if total_spending > 0:
                for agent_id, spending in self.agent_spending.items():
                    ratio = spending / total_spending
                    cost_distribution[agent_id] = total_cost * ratio
            else:
                # Fallback to equal split if no usage data
                cost_per_agent = total_cost / len(self.agents)
                for agent_id in self.agents:
                    cost_distribution[agent_id] = cost_per_agent
        
        else:  # MANUAL
            # Manual cost splitting returns empty dict - caller handles distribution
            pass
        
        return cost_distribution
    
    def execute_cost_split(self, total_cost: float, method: Optional[CostSplittingMethod] = None) -> Dict[str, str]:
        """
        Execute cost splitting by actually transferring funds between agents.
        
        Args:
            total_cost: Total cost to split and transfer
            method: Override default cost splitting method
            
        Returns:
            Dictionary mapping agent_id to transaction hash
        """
        cost_distribution = self.split_costs(total_cost, method)
        transaction_hashes = {}
        
        if not cost_distribution:
            return transaction_hashes
        
        # Find agent with highest balance to be the payer
        payer_agent_id = max(self.agents.keys(), 
                           key=lambda aid: self.agents[aid].get_balance())
        
        # Transfer each agent's share from the payer
        for agent_id, cost_share in cost_distribution.items():
            if agent_id != payer_agent_id and cost_share > 0:
                try:
                    tx_hash = self.transfer_to_agent(agent_id, payer_agent_id, cost_share)
                    transaction_hashes[agent_id] = tx_hash
                except Exception as e:
                    transaction_hashes[agent_id] = f"FAILED: {str(e)}"
        
        return transaction_hashes
    
    def transfer_to_agent(self, from_agent_id: str, to_agent_id: str, amount: float) -> str:
        """
        Transfer funds between agents in the swarm.
        
        Args:
            from_agent_id: Source agent ID
            to_agent_id: Destination agent ID
            amount: Amount to transfer
            
        Returns:
            Transaction hash
            
        Raises:
            ValueError: If agents not found in swarm or insufficient funds
        """
        if from_agent_id not in self.agents:
            raise ValueError(f"Agent {from_agent_id} not in swarm")
        if to_agent_id not in self.agents:
            raise ValueError(f"Agent {to_agent_id} not in swarm")
        
        from_agent = self.agents[from_agent_id]
        to_agent = self.agents[to_agent_id]
        
        # Check if sender has sufficient balance
        if from_agent.get_balance() < amount:
            raise ValueError(f"Agent {from_agent_id} has insufficient funds for transfer")
        
        # If using shared wallet, this is just an accounting operation
        if self.config.shared_wallet:
            # Update spending tracking to reflect the transfer
            self.agent_spending[from_agent_id] += amount
            if to_agent_id in self.agent_spending:
                self.agent_spending[to_agent_id] -= amount
            
            # Return a mock transaction hash for shared wallet transfers
            return f"shared_wallet_transfer_{from_agent_id}_to_{to_agent_id}_{amount}"
        
        # For individual wallets, perform actual blockchain transfer
        to_agent_address = to_agent.wallet_manager.get_address()
        tx_hash = from_agent.wallet_manager.make_payment(amount, to_agent_address)
        
        # Update spending tracking
        self.agent_spending[from_agent_id] += amount
        
        return tx_hash
    
    def transfer_between_agents(self, from_agent_id: str, to_agent_id: str, amount: float) -> str:
        """
        Legacy method - use transfer_to_agent instead.
        """
        return self.transfer_to_agent(from_agent_id, to_agent_id, amount)
    
    def get_swarm_balance(self) -> float:
        """
        Get total balance across all agents in swarm.
        
        Returns:
            Total swarm balance
        """
        total_balance = 0.0
        for agent in self.agents.values():
            total_balance += agent.get_balance()
        return total_balance
    
    def get_agent_spending(self, agent_id: str) -> float:
        """
        Get spending for specific agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent spending amount
        """
        return self.agent_spending.get(agent_id, 0.0)
    
    def update_agent_spending(self, agent_id: str, amount: float, tool_name: Optional[str] = None) -> None:
        """
        Update spending tracking for agent with detailed tracking.
        
        Args:
            agent_id: Agent ID
            amount: Amount to add to spending
            tool_name: Optional tool name for detailed tracking
        """
        if agent_id in self.agent_spending:
            self.agent_spending[agent_id] += amount
            
            # Track detailed spending per tool if provided
            if not hasattr(self, 'detailed_spending'):
                self.detailed_spending = {}
            
            if agent_id not in self.detailed_spending:
                self.detailed_spending[agent_id] = {}
            
            if tool_name:
                if tool_name not in self.detailed_spending[agent_id]:
                    self.detailed_spending[agent_id][tool_name] = 0.0
                self.detailed_spending[agent_id][tool_name] += amount
    
    def get_agent_spending_breakdown(self, agent_id: str) -> Dict[str, float]:
        """
        Get detailed spending breakdown for an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Dictionary mapping tool names to spending amounts
        """
        if not hasattr(self, 'detailed_spending'):
            return {}
        
        return self.detailed_spending.get(agent_id, {})
    
    def get_swarm_spending_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive spending summary for the entire swarm.
        
        Returns:
            Dictionary with total spending, per-agent spending, and tool breakdown
        """
        total_spending = sum(self.agent_spending.values())
        
        summary = {
            'total_spending': total_spending,
            'agent_spending': dict(self.agent_spending),
            'average_spending': total_spending / len(self.agents) if self.agents else 0,
            'detailed_breakdown': getattr(self, 'detailed_spending', {})
        }
        
        return summary
    
    def reset_spending_tracking(self) -> None:
        """
        Reset all spending tracking for the swarm.
        """
        for agent_id in self.agent_spending:
            self.agent_spending[agent_id] = 0.0
        
        if hasattr(self, 'detailed_spending'):
            self.detailed_spending = {}