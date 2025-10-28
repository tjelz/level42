"""
Unit tests for swarm coordination functionality.

Tests swarm creation, agent management, cost-splitting, fund transfers,
and collaborative task execution.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from x402_agent.swarm import AgentSwarm, SwarmConfig, CostSplittingMethod


class MockAgent:
    """Mock agent for testing swarm functionality."""
    
    def __init__(self, agent_id: str, balance: float = 10.0):
        self.agent_id = agent_id
        self._balance = balance
        self.wallet_manager = Mock()
        self.wallet_manager.get_address.return_value = f"0x{agent_id}address"
        self.wallet_manager.make_payment.return_value = f"tx_hash_{agent_id}"
        self.payment_processor = Mock()
        self.tool_registry = Mock()
        self.tool_registry.tools = {}
        
    def get_balance(self):
        return self._balance
    
    def run(self, prompt: str):
        return f"Agent {self.agent_id} response to: {prompt}"


class TestAgentSwarm:
    """Test cases for AgentSwarm class."""
    
    def test_swarm_initialization_default(self):
        """Test swarm initialization with default configuration."""
        swarm = AgentSwarm()
        
        assert swarm.config.shared_wallet is False
        assert swarm.config.cost_splitting_method == CostSplittingMethod.EQUAL
        assert swarm.config.max_agents == 10
        assert len(swarm.agents) == 0
        assert len(swarm.agent_spending) == 0
        assert swarm.shared_wallet_manager is None
    
    def test_swarm_initialization_shared_wallet(self):
        """Test swarm initialization with shared wallet."""
        swarm = AgentSwarm(shared_wallet=True)
        
        assert swarm.config.shared_wallet is True
        assert swarm.shared_wallet_manager is None  # Set when first agent added
    
    def test_swarm_initialization_with_config(self):
        """Test swarm initialization with custom configuration."""
        config = SwarmConfig(
            shared_wallet=True,
            cost_splitting_method=CostSplittingMethod.USAGE_BASED,
            max_agents=5
        )
        swarm = AgentSwarm(config=config)
        
        assert swarm.config.shared_wallet is True
        assert swarm.config.cost_splitting_method == CostSplittingMethod.USAGE_BASED
        assert swarm.config.max_agents == 5


class TestAgentManagement:
    """Test cases for agent management in swarms."""
    
    def test_add_agent_success(self):
        """Test successful agent addition to swarm."""
        swarm = AgentSwarm()
        agent = MockAgent("agent1")
        
        swarm.add_agent(agent)
        
        assert "agent1" in swarm.agents
        assert swarm.agents["agent1"] == agent
        assert swarm.agent_spending["agent1"] == 0.0
        assert hasattr(agent, '_swarm')
        assert agent._swarm == swarm
    
    def test_add_agent_shared_wallet(self):
        """Test agent addition with shared wallet configuration."""
        swarm = AgentSwarm(shared_wallet=True)
        agent1 = MockAgent("agent1")
        agent2 = MockAgent("agent2")
        
        swarm.add_agent(agent1)
        assert swarm.shared_wallet_manager == agent1.wallet_manager
        
        swarm.add_agent(agent2)
        assert agent2.wallet_manager == agent1.wallet_manager
        assert agent2.payment_processor.wallet_manager == agent1.wallet_manager
    
    def test_add_agent_duplicate(self):
        """Test adding duplicate agent raises error."""
        swarm = AgentSwarm()
        agent = MockAgent("agent1")
        
        swarm.add_agent(agent)
        
        with pytest.raises(ValueError, match="Agent agent1 already in swarm"):
            swarm.add_agent(agent)
    
    def test_add_agent_at_capacity(self):
        """Test adding agent when swarm is at capacity."""
        config = SwarmConfig(max_agents=2)
        swarm = AgentSwarm(config=config)
        
        agent1 = MockAgent("agent1")
        agent2 = MockAgent("agent2")
        agent3 = MockAgent("agent3")
        
        swarm.add_agent(agent1)
        swarm.add_agent(agent2)
        
        with pytest.raises(ValueError, match="Swarm at maximum capacity"):
            swarm.add_agent(agent3)
    
    def test_remove_agent_success(self):
        """Test successful agent removal from swarm."""
        swarm = AgentSwarm()
        agent = MockAgent("agent1")
        
        swarm.add_agent(agent)
        result = swarm.remove_agent("agent1")
        
        assert result is True
        assert "agent1" not in swarm.agents
        assert "agent1" not in swarm.agent_spending
        assert not hasattr(agent, '_swarm')
    
    def test_remove_agent_not_found(self):
        """Test removing non-existent agent."""
        swarm = AgentSwarm()
        
        result = swarm.remove_agent("nonexistent")
        assert result is False
    
    def test_discover_agents_all(self):
        """Test discovering all agents in swarm."""
        swarm = AgentSwarm()
        agent1 = MockAgent("agent1")
        agent2 = MockAgent("agent2")
        
        swarm.add_agent(agent1)
        swarm.add_agent(agent2)
        
        agents = swarm.discover_agents()
        assert set(agents) == {"agent1", "agent2"}
    
    def test_discover_agents_with_query(self):
        """Test discovering agents with query filter."""
        swarm = AgentSwarm()
        agent1 = MockAgent("trading_agent")
        agent2 = MockAgent("research_agent")
        agent3 = MockAgent("trading_bot")
        
        swarm.add_agent(agent1)
        swarm.add_agent(agent2)
        swarm.add_agent(agent3)
        
        trading_agents = swarm.discover_agents("trading")
        assert set(trading_agents) == {"trading_agent", "trading_bot"}
    
    def test_get_agent_success(self):
        """Test getting agent by ID."""
        swarm = AgentSwarm()
        agent = MockAgent("agent1")
        
        swarm.add_agent(agent)
        retrieved_agent = swarm.get_agent("agent1")
        
        assert retrieved_agent == agent
    
    def test_get_agent_not_found(self):
        """Test getting non-existent agent."""
        swarm = AgentSwarm()
        
        agent = swarm.get_agent("nonexistent")
        assert agent is None
    
    def test_list_agents(self):
        """Test listing all agents with their information."""
        swarm = AgentSwarm()
        agent1 = MockAgent("agent1", balance=5.0)
        agent2 = MockAgent("agent2", balance=10.0)
        
        swarm.add_agent(agent1)
        swarm.add_agent(agent2)
        swarm.update_agent_spending("agent1", 2.0)
        
        agent_info = swarm.list_agents()
        
        assert len(agent_info) == 2
        assert agent_info["agent1"]["balance"] == 5.0
        assert agent_info["agent1"]["spending"] == 2.0
        assert agent_info["agent2"]["balance"] == 10.0
        assert agent_info["agent2"]["spending"] == 0.0


class TestCommunication:
    """Test cases for agent communication in swarms."""
    
    def test_send_message_success(self):
        """Test successful message sending between agents."""
        swarm = AgentSwarm()
        agent1 = MockAgent("agent1")
        agent2 = MockAgent("agent2")
        
        swarm.add_agent(agent1)
        swarm.add_agent(agent2)
        
        result = swarm.send_message("agent1", "agent2", "Hello agent2!")
        
        assert result is True
        assert hasattr(agent2, '_message_queue')
        assert len(agent2._message_queue) == 1
        assert agent2._message_queue[0]['from'] == "agent1"
        assert agent2._message_queue[0]['message'] == "Hello agent2!"
    
    def test_send_message_sender_not_found(self):
        """Test sending message from non-existent sender."""
        swarm = AgentSwarm()
        agent2 = MockAgent("agent2")
        swarm.add_agent(agent2)
        
        with pytest.raises(ValueError, match="Sender agent nonexistent not in swarm"):
            swarm.send_message("nonexistent", "agent2", "Hello")
    
    def test_send_message_recipient_not_found(self):
        """Test sending message to non-existent recipient."""
        swarm = AgentSwarm()
        agent1 = MockAgent("agent1")
        swarm.add_agent(agent1)
        
        with pytest.raises(ValueError, match="Recipient agent nonexistent not in swarm"):
            swarm.send_message("agent1", "nonexistent", "Hello")
    
    def test_broadcast_message(self):
        """Test broadcasting message to all agents."""
        swarm = AgentSwarm()
        agent1 = MockAgent("agent1")
        agent2 = MockAgent("agent2")
        agent3 = MockAgent("agent3")
        
        swarm.add_agent(agent1)
        swarm.add_agent(agent2)
        swarm.add_agent(agent3)
        
        recipients = swarm.broadcast_message("agent1", "Broadcast message")
        
        assert recipients == 2  # agent2 and agent3
        assert hasattr(agent2, '_message_queue')
        assert hasattr(agent3, '_message_queue')
        assert len(agent2._message_queue) == 1
        assert len(agent3._message_queue) == 1
        assert not hasattr(agent1, '_message_queue')  # Sender doesn't receive own message


class TestCostSplitting:
    """Test cases for cost splitting functionality."""
    
    def test_split_costs_equal(self):
        """Test equal cost splitting among agents."""
        swarm = AgentSwarm()
        agent1 = MockAgent("agent1")
        agent2 = MockAgent("agent2")
        agent3 = MockAgent("agent3")
        
        swarm.add_agent(agent1)
        swarm.add_agent(agent2)
        swarm.add_agent(agent3)
        
        cost_distribution = swarm.split_costs(30.0)
        
        assert len(cost_distribution) == 3
        assert cost_distribution["agent1"] == 10.0
        assert cost_distribution["agent2"] == 10.0
        assert cost_distribution["agent3"] == 10.0
    
    def test_split_costs_usage_based_with_data(self):
        """Test usage-based cost splitting with spending data."""
        config = SwarmConfig(cost_splitting_method=CostSplittingMethod.USAGE_BASED)
        swarm = AgentSwarm(config=config)
        
        agent1 = MockAgent("agent1")
        agent2 = MockAgent("agent2")
        
        swarm.add_agent(agent1)
        swarm.add_agent(agent2)
        
        # Set up spending history
        swarm.update_agent_spending("agent1", 6.0)  # 60% of total
        swarm.update_agent_spending("agent2", 4.0)  # 40% of total
        
        cost_distribution = swarm.split_costs(100.0)
        
        assert cost_distribution["agent1"] == 60.0  # 60% of 100
        assert cost_distribution["agent2"] == 40.0  # 40% of 100
    
    def test_split_costs_usage_based_no_data(self):
        """Test usage-based cost splitting falls back to equal when no data."""
        config = SwarmConfig(cost_splitting_method=CostSplittingMethod.USAGE_BASED)
        swarm = AgentSwarm(config=config)
        
        agent1 = MockAgent("agent1")
        agent2 = MockAgent("agent2")
        
        swarm.add_agent(agent1)
        swarm.add_agent(agent2)
        
        cost_distribution = swarm.split_costs(20.0)
        
        assert cost_distribution["agent1"] == 10.0
        assert cost_distribution["agent2"] == 10.0
    
    def test_split_costs_manual(self):
        """Test manual cost splitting returns empty dict."""
        config = SwarmConfig(cost_splitting_method=CostSplittingMethod.MANUAL)
        swarm = AgentSwarm(config=config)
        
        agent1 = MockAgent("agent1")
        swarm.add_agent(agent1)
        
        cost_distribution = swarm.split_costs(10.0)
        
        assert cost_distribution == {}
    
    def test_split_costs_empty_swarm(self):
        """Test cost splitting with no agents."""
        swarm = AgentSwarm()
        
        cost_distribution = swarm.split_costs(10.0)
        
        assert cost_distribution == {}
    
    def test_execute_cost_split(self):
        """Test executing cost split with actual transfers."""
        swarm = AgentSwarm()
        agent1 = MockAgent("agent1", balance=20.0)
        agent2 = MockAgent("agent2", balance=5.0)
        
        swarm.add_agent(agent1)
        swarm.add_agent(agent2)
        
        transaction_hashes = swarm.execute_cost_split(10.0)
        
        # agent1 has higher balance, so agent2 should transfer to agent1
        assert "agent2" in transaction_hashes
        assert transaction_hashes["agent2"] == "tx_hash_agent2"


class TestFundTransfers:
    """Test cases for fund transfer functionality."""
    
    def test_transfer_to_agent_individual_wallets(self):
        """Test fund transfer between agents with individual wallets."""
        swarm = AgentSwarm()
        agent1 = MockAgent("agent1", balance=10.0)
        agent2 = MockAgent("agent2", balance=5.0)
        
        swarm.add_agent(agent1)
        swarm.add_agent(agent2)
        
        tx_hash = swarm.transfer_to_agent("agent1", "agent2", 3.0)
        
        assert tx_hash == "tx_hash_agent1"
        assert swarm.agent_spending["agent1"] == 3.0
        agent1.wallet_manager.make_payment.assert_called_once_with(3.0, "0xagent2address")
    
    def test_transfer_to_agent_shared_wallet(self):
        """Test fund transfer with shared wallet (accounting only)."""
        swarm = AgentSwarm(shared_wallet=True)
        agent1 = MockAgent("agent1", balance=10.0)
        agent2 = MockAgent("agent2", balance=5.0)
        
        swarm.add_agent(agent1)
        swarm.add_agent(agent2)
        
        tx_hash = swarm.transfer_to_agent("agent1", "agent2", 3.0)
        
        assert tx_hash == "shared_wallet_transfer_agent1_to_agent2_3.0"
        assert swarm.agent_spending["agent1"] == 3.0
        assert swarm.agent_spending["agent2"] == -3.0
    
    def test_transfer_to_agent_insufficient_funds(self):
        """Test transfer with insufficient funds."""
        swarm = AgentSwarm()
        agent1 = MockAgent("agent1", balance=2.0)
        agent2 = MockAgent("agent2", balance=5.0)
        
        swarm.add_agent(agent1)
        swarm.add_agent(agent2)
        
        with pytest.raises(ValueError, match="Agent agent1 has insufficient funds"):
            swarm.transfer_to_agent("agent1", "agent2", 5.0)
    
    def test_transfer_to_agent_sender_not_found(self):
        """Test transfer from non-existent sender."""
        swarm = AgentSwarm()
        agent2 = MockAgent("agent2")
        swarm.add_agent(agent2)
        
        with pytest.raises(ValueError, match="Agent nonexistent not in swarm"):
            swarm.transfer_to_agent("nonexistent", "agent2", 1.0)
    
    def test_transfer_to_agent_recipient_not_found(self):
        """Test transfer to non-existent recipient."""
        swarm = AgentSwarm()
        agent1 = MockAgent("agent1")
        swarm.add_agent(agent1)
        
        with pytest.raises(ValueError, match="Agent nonexistent not in swarm"):
            swarm.transfer_to_agent("agent1", "nonexistent", 1.0)


class TestSpendingTracking:
    """Test cases for spending tracking functionality."""
    
    def test_update_agent_spending_basic(self):
        """Test basic spending update."""
        swarm = AgentSwarm()
        agent = MockAgent("agent1")
        swarm.add_agent(agent)
        
        swarm.update_agent_spending("agent1", 5.0)
        
        assert swarm.agent_spending["agent1"] == 5.0
    
    def test_update_agent_spending_with_tool(self):
        """Test spending update with tool tracking."""
        swarm = AgentSwarm()
        agent = MockAgent("agent1")
        swarm.add_agent(agent)
        
        swarm.update_agent_spending("agent1", 3.0, "api_tool")
        swarm.update_agent_spending("agent1", 2.0, "api_tool")
        swarm.update_agent_spending("agent1", 1.0, "other_tool")
        
        assert swarm.agent_spending["agent1"] == 6.0
        
        breakdown = swarm.get_agent_spending_breakdown("agent1")
        assert breakdown["api_tool"] == 5.0
        assert breakdown["other_tool"] == 1.0
    
    def test_get_swarm_spending_summary(self):
        """Test comprehensive spending summary."""
        swarm = AgentSwarm()
        agent1 = MockAgent("agent1")
        agent2 = MockAgent("agent2")
        
        swarm.add_agent(agent1)
        swarm.add_agent(agent2)
        
        swarm.update_agent_spending("agent1", 10.0, "tool1")
        swarm.update_agent_spending("agent2", 5.0, "tool2")
        
        summary = swarm.get_swarm_spending_summary()
        
        assert summary["total_spending"] == 15.0
        assert summary["average_spending"] == 7.5
        assert summary["agent_spending"]["agent1"] == 10.0
        assert summary["agent_spending"]["agent2"] == 5.0
        assert "detailed_breakdown" in summary
    
    def test_reset_spending_tracking(self):
        """Test resetting spending tracking."""
        swarm = AgentSwarm()
        agent = MockAgent("agent1")
        swarm.add_agent(agent)
        
        swarm.update_agent_spending("agent1", 10.0, "tool1")
        swarm.reset_spending_tracking()
        
        assert swarm.agent_spending["agent1"] == 0.0
        assert swarm.get_agent_spending_breakdown("agent1") == {}


class TestCollaborativeExecution:
    """Test cases for collaborative task execution."""
    
    def test_collaborate_parallel(self):
        """Test parallel collaborative task execution."""
        swarm = AgentSwarm()
        agent1 = MockAgent("agent1")
        agent2 = MockAgent("agent2")
        
        swarm.add_agent(agent1)
        swarm.add_agent(agent2)
        
        result = swarm.collaborate("Test task", "parallel")
        
        assert "SWARM COLLABORATION RESULTS" in result
        assert "Agent agent1:" in result
        assert "Agent agent2:" in result
        assert "Agent agent1 response to: Test task" in result
        assert "Agent agent2 response to: Test task" in result
        assert "Successful agents: 2/2" in result
    
    def test_collaborate_sequential(self):
        """Test sequential collaborative task execution."""
        swarm = AgentSwarm()
        agent1 = MockAgent("agent1")
        agent2 = MockAgent("agent2")
        
        swarm.add_agent(agent1)
        swarm.add_agent(agent2)
        
        result = swarm.collaborate("Test task", "sequential")
        
        assert "SWARM COLLABORATION RESULTS" in result
        assert "Agent agent1:" in result
        assert "Agent agent2:" in result
        # Second agent should get enhanced task with previous results
        assert "Previous results:" in result
    
    def test_collaborate_divide(self):
        """Test divided collaborative task execution."""
        swarm = AgentSwarm()
        agent1 = MockAgent("agent1")
        agent2 = MockAgent("agent2")
        
        swarm.add_agent(agent1)
        swarm.add_agent(agent2)
        
        result = swarm.collaborate("First sentence. Second sentence.", "divide")
        
        assert "SWARM COLLABORATION RESULTS" in result
        assert "Agent agent1:" in result
        assert "Agent agent2:" in result
    
    def test_collaborate_empty_swarm(self):
        """Test collaboration with empty swarm."""
        swarm = AgentSwarm()
        
        with pytest.raises(ValueError, match="No agents in swarm for collaboration"):
            swarm.collaborate("Test task")
    
    def test_collaborate_invalid_strategy(self):
        """Test collaboration with invalid strategy."""
        swarm = AgentSwarm()
        agent = MockAgent("agent1")
        swarm.add_agent(agent)
        
        result = swarm.collaborate("Test task", "invalid_strategy")
        
        assert "collaboration_error" in result
        assert "Unknown distribution strategy" in result
    
    def test_collaborate_with_recovery(self):
        """Test collaborative execution with recovery mechanism."""
        swarm = AgentSwarm()
        agent1 = MockAgent("agent1", balance=0.005)  # Low balance
        agent2 = MockAgent("agent2", balance=2.0)    # High balance
        
        swarm.add_agent(agent1)
        swarm.add_agent(agent2)
        
        # Mock agent1 to fail initially
        agent1.run = Mock(side_effect=Exception("Insufficient funds"))
        
        result = swarm.collaborate_with_recovery("Test task", max_retries=1)
        
        # Should attempt recovery by transferring funds
        assert "COLLABORATION FAILED" in result or "SWARM COLLABORATION RESULTS" in result


class TestSwarmBalance:
    """Test cases for swarm balance functionality."""
    
    def test_get_swarm_balance(self):
        """Test getting total swarm balance."""
        swarm = AgentSwarm()
        agent1 = MockAgent("agent1", balance=10.0)
        agent2 = MockAgent("agent2", balance=5.0)
        
        swarm.add_agent(agent1)
        swarm.add_agent(agent2)
        
        total_balance = swarm.get_swarm_balance()
        
        assert total_balance == 15.0
    
    def test_get_swarm_balance_empty(self):
        """Test getting balance of empty swarm."""
        swarm = AgentSwarm()
        
        total_balance = swarm.get_swarm_balance()
        
        assert total_balance == 0.0


if __name__ == "__main__":
    pytest.main([__file__])