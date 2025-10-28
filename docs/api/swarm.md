# AgentSwarm API Reference

The `AgentSwarm` class enables coordination and collaboration between multiple x402-Agent instances for complex multi-agent tasks.

## Class Definition

```python
class AgentSwarm:
    """
    Coordinates multiple X402Agent instances for collaborative task execution.
    
    Provides shared wallet management, cost-splitting, task distribution,
    and inter-agent communication for complex multi-agent workflows.
    """
```

## Constructor

### `__init__(shared_wallet=False, cost_splitting="equal")`

Initialize a new AgentSwarm instance.

**Parameters:**
- `shared_wallet` (bool, optional): Whether agents share a common wallet. Defaults to False
- `cost_splitting` (str, optional): Cost distribution method. Options: "equal", "proportional", "custom". Defaults to "equal"

**Example:**
```python
from x402_agent.swarm import AgentSwarm

# Create swarm with shared wallet
swarm = AgentSwarm(shared_wallet=True, cost_splitting="equal")

# Create swarm with individual wallets
swarm = AgentSwarm(shared_wallet=False, cost_splitting="proportional")
```

## Properties

### `agents`
Dictionary of agents in the swarm, keyed by agent ID.

**Type:** `Dict[str, X402Agent]`

### `shared_wallet`
Whether the swarm uses a shared wallet for all agents.

**Type:** `bool`

### `cost_splitting`
The cost distribution method being used.

**Type:** `str`

### `collaboration_history`
History of collaborative tasks and their outcomes.

**Type:** `List[CollaborationRecord]`

## Methods

### `add_agent(agent, agent_id=None, role=None)`

Add an agent to the swarm.

**Parameters:**
- `agent` (X402Agent): Agent instance to add
- `agent_id` (str, optional): Unique identifier for the agent. Auto-generated if None
- `role` (str, optional): Role description for the agent

**Returns:**
- `str`: The assigned agent ID

**Raises:**
- `ValueError`: If agent_id already exists or agent is invalid

**Example:**
```python
from x402_agent import X402Agent
from langchain_openai import ChatOpenAI

# Create specialized agents
researcher = X402Agent(ChatOpenAI(), "0xkey1...", network="base")
analyst = X402Agent(ChatOpenAI(), "0xkey2...", network="base")

# Add to swarm
swarm.add_agent(researcher, agent_id="researcher", role="Data collection and research")
swarm.add_agent(analyst, agent_id="analyst", role="Data analysis and insights")
```

### `remove_agent(agent_id)`

Remove an agent from the swarm.

**Parameters:**
- `agent_id` (str): ID of the agent to remove

**Raises:**
- `ValueError`: If agent_id doesn't exist

**Example:**
```python
swarm.remove_agent("researcher")
```

### `collaborate(task, strategy="parallel", max_agents=None)`

Execute a collaborative task across multiple agents.

**Parameters:**
- `task` (str): Task description for the agents to collaborate on
- `strategy` (str, optional): Collaboration strategy. Options: "parallel", "sequential", "divide_and_conquer". Defaults to "parallel"
- `max_agents` (int, optional): Maximum number of agents to use. Uses all if None

**Returns:**
- `CollaborationResult`: Results from the collaborative task

**Raises:**
- `SwarmError`: If collaboration fails
- `InsufficientAgentsError`: If not enough agents available

**Example:**
```python
# Parallel collaboration
result = swarm.collaborate(
    task="Research the latest developments in quantum computing",
    strategy="parallel",
    max_agents=3
)

print(f"Collaboration result: {result.summary}")
print(f"Total cost: ${result.total_cost}")
```

### `divide_task(task, num_subtasks=None)`

Divide a complex task into subtasks for different agents.

**Parameters:**
- `task` (str): Main task to divide
- `num_subtasks` (int, optional): Number of subtasks to create. Uses agent count if None

**Returns:**
- `List[str]`: List of subtask descriptions

**Example:**
```python
subtasks = swarm.divide_task(
    task="Analyze the cryptocurrency market trends for Q4 2024",
    num_subtasks=4
)

for i, subtask in enumerate(subtasks):
    print(f"Subtask {i+1}: {subtask}")
```

### `assign_tasks(tasks, assignment_strategy="round_robin")`

Assign tasks to specific agents in the swarm.

**Parameters:**
- `tasks` (List[str]): List of tasks to assign
- `assignment_strategy` (str, optional): Assignment method. Options: "round_robin", "capability_based", "load_balanced". Defaults to "round_robin"

**Returns:**
- `Dict[str, List[str]]`: Mapping of agent IDs to assigned tasks

**Example:**
```python
tasks = [
    "Collect stock market data",
    "Analyze sentiment from news",
    "Generate trading signals",
    "Create summary report"
]

assignments = swarm.assign_tasks(tasks, assignment_strategy="capability_based")
for agent_id, agent_tasks in assignments.items():
    print(f"Agent {agent_id}: {len(agent_tasks)} tasks")
```

### `split_costs(total_cost, method=None)`

Distribute costs among agents in the swarm.

**Parameters:**
- `total_cost` (float): Total cost to distribute
- `method` (str, optional): Splitting method. Uses swarm default if None

**Returns:**
- `Dict[str, float]`: Cost allocation per agent

**Raises:**
- `InsufficientFundsError`: If agents don't have enough combined balance

**Example:**
```python
# Split $10 cost among agents
cost_allocation = swarm.split_costs(10.0, method="equal")
for agent_id, cost in cost_allocation.items():
    print(f"Agent {agent_id} owes: ${cost:.2f}")
```

### `transfer_funds(from_agent, to_agent, amount)`

Transfer funds between agents in the swarm.

**Parameters:**
- `from_agent` (str): Source agent ID
- `to_agent` (str): Destination agent ID
- `amount` (float): Amount to transfer in USDC

**Returns:**
- `str`: Transaction hash of the transfer

**Raises:**
- `InsufficientFundsError`: If source agent has insufficient funds
- `ValueError`: If agent IDs are invalid

**Example:**
```python
# Transfer $5 from researcher to analyst
tx_hash = swarm.transfer_funds("researcher", "analyst", 5.0)
print(f"Transfer completed: {tx_hash}")
```

### `get_swarm_balance()`

Get the total balance across all agents in the swarm.

**Returns:**
- `dict`: Balance information for the swarm

**Example:**
```python
balance_info = swarm.get_swarm_balance()
print(f"Total swarm balance: ${balance_info['total']:.2f}")
print(f"Average per agent: ${balance_info['average']:.2f}")
print(f"Lowest balance: ${balance_info['min']:.2f}")
```

### `get_collaboration_summary()`

Get a summary of recent collaboration activities.

**Returns:**
- `dict`: Summary of collaboration statistics

**Example:**
```python
summary = swarm.get_collaboration_summary()
print(f"Total collaborations: {summary['total_count']}")
print(f"Success rate: {summary['success_rate']:.2%}")
print(f"Average cost per collaboration: ${summary['avg_cost']:.2f}")
```

## Collaboration Strategies

### Parallel Strategy

All agents work on the same task simultaneously and results are combined.

```python
result = swarm.collaborate(
    task="Research AI developments",
    strategy="parallel"
)
```

**Benefits:**
- Fast execution
- Diverse perspectives
- Redundancy for reliability

**Use Cases:**
- Research tasks
- Data collection
- Opinion gathering

### Sequential Strategy

Agents work on the task one after another, building on previous results.

```python
result = swarm.collaborate(
    task="Write a comprehensive report",
    strategy="sequential"
)
```

**Benefits:**
- Builds on previous work
- Maintains consistency
- Quality refinement

**Use Cases:**
- Report writing
- Data processing pipelines
- Quality assurance

### Divide and Conquer Strategy

Task is divided into subtasks, each handled by different agents.

```python
result = swarm.collaborate(
    task="Analyze market data across multiple sectors",
    strategy="divide_and_conquer"
)
```

**Benefits:**
- Efficient resource utilization
- Specialized expertise
- Parallel processing

**Use Cases:**
- Large data analysis
- Multi-domain research
- Complex problem solving

## Cost Splitting Methods

### Equal Splitting

Costs are divided equally among all participating agents.

```python
swarm = AgentSwarm(cost_splitting="equal")
```

### Proportional Splitting

Costs are split based on each agent's contribution or usage.

```python
swarm = AgentSwarm(cost_splitting="proportional")
```

### Custom Splitting

Costs are split according to custom rules defined by the user.

```python
def custom_split_function(total_cost, agents, usage_data):
    # Custom logic here
    return cost_allocation

swarm = AgentSwarm(cost_splitting="custom")
swarm.set_custom_split_function(custom_split_function)
```

## Inter-Agent Communication

### Message Passing

```python
# Send message between agents
swarm.send_message(
    from_agent="researcher",
    to_agent="analyst",
    message="Found interesting data pattern",
    data={"pattern": "seasonal_trend"}
)
```

### Broadcast Messages

```python
# Broadcast to all agents
swarm.broadcast_message(
    from_agent="coordinator",
    message="Task priority has changed",
    priority="high"
)
```

### Agent Coordination

```python
# Coordinate agent actions
coordination_plan = swarm.create_coordination_plan(
    task="Multi-step analysis",
    dependencies={
        "step2": ["step1"],
        "step3": ["step1", "step2"]
    }
)

swarm.execute_coordination_plan(coordination_plan)
```

## Monitoring and Analytics

### Real-time Monitoring

```python
def collaboration_monitor(event):
    print(f"Swarm event: {event.type} - {event.description}")

swarm.add_event_callback(collaboration_monitor)
```

### Performance Analytics

```python
analytics = swarm.get_performance_analytics()
print(f"Average task completion time: {analytics['avg_completion_time']:.2f}s")
print(f"Agent utilization rate: {analytics['utilization_rate']:.2%}")
print(f"Cost efficiency: ${analytics['cost_per_task']:.4f} per task")
```

### Collaboration Metrics

```python
metrics = swarm.get_collaboration_metrics()
print(f"Successful collaborations: {metrics['success_count']}")
print(f"Failed collaborations: {metrics['failure_count']}")
print(f"Average agents per task: {metrics['avg_agents_per_task']:.1f}")
```

## Error Handling

### Swarm Errors

#### `SwarmError`
Base exception for swarm-related errors.

#### `InsufficientAgentsError`
Raised when not enough agents are available for a task.

```python
try:
    result = swarm.collaborate("Complex task", max_agents=10)
except InsufficientAgentsError as e:
    print(f"Need more agents: {e}")
```

#### `CollaborationTimeoutError`
Raised when collaboration takes too long to complete.

```python
try:
    result = swarm.collaborate("Long task", timeout=300)
except CollaborationTimeoutError as e:
    print(f"Collaboration timed out: {e}")
```

#### `AgentCommunicationError`
Raised when agents cannot communicate properly.

```python
try:
    swarm.send_message("agent1", "agent2", "Hello")
except AgentCommunicationError as e:
    print(f"Communication failed: {e}")
```

## Configuration

### Swarm Configuration

```python
# Configure swarm behavior
swarm.configure({
    "max_collaboration_time": 600,  # 10 minutes
    "retry_failed_tasks": True,
    "enable_agent_communication": True,
    "cost_splitting_precision": 6  # decimal places
})
```

### Agent Roles and Capabilities

```python
# Define agent capabilities
swarm.set_agent_capabilities("researcher", {
    "data_collection": 0.9,
    "analysis": 0.6,
    "writing": 0.4
})

swarm.set_agent_capabilities("analyst", {
    "data_collection": 0.4,
    "analysis": 0.9,
    "writing": 0.7
})
```

## Best Practices

1. **Agent Specialization**: Assign specific roles to agents based on their capabilities
2. **Cost Management**: Monitor and optimize cost splitting for fairness
3. **Task Decomposition**: Break complex tasks into manageable subtasks
4. **Error Handling**: Implement robust error handling for collaboration failures
5. **Performance Monitoring**: Track swarm performance and optimize accordingly

## Examples

### Basic Multi-Agent Collaboration

```python
from x402_agent import X402Agent
from x402_agent.swarm import AgentSwarm
from langchain_openai import ChatOpenAI

# Create agents
llm = ChatOpenAI(model="gpt-4")
agent1 = X402Agent(llm, "0xkey1...", network="base")
agent2 = X402Agent(llm, "0xkey2...", network="base")

# Create swarm
swarm = AgentSwarm(shared_wallet=True)
swarm.add_agent(agent1, "researcher")
swarm.add_agent(agent2, "analyst")

# Collaborate on task
result = swarm.collaborate(
    task="Research and analyze cryptocurrency market trends",
    strategy="parallel"
)

print(f"Collaboration result: {result.summary}")
```

### Advanced Swarm with Cost Splitting

```python
# Create swarm with proportional cost splitting
swarm = AgentSwarm(cost_splitting="proportional")

# Add agents with different capabilities
agents = [
    ("data_collector", "Specializes in data collection"),
    ("analyzer", "Focuses on data analysis"),
    ("reporter", "Creates reports and summaries")
]

for agent_id, role in agents:
    agent = X402Agent(llm, f"0x{agent_id}_key...", network="base")
    swarm.add_agent(agent, agent_id, role)

# Execute complex collaboration
result = swarm.collaborate(
    task="Complete market analysis report",
    strategy="divide_and_conquer",
    max_agents=3
)

# Check cost allocation
cost_allocation = swarm.split_costs(result.total_cost)
for agent_id, cost in cost_allocation.items():
    print(f"{agent_id}: ${cost:.2f}")
```

### Swarm with Custom Coordination

```python
# Create coordination plan
coordination_plan = {
    "phase1": {
        "agents": ["data_collector"],
        "task": "Collect market data",
        "dependencies": []
    },
    "phase2": {
        "agents": ["analyzer"],
        "task": "Analyze collected data",
        "dependencies": ["phase1"]
    },
    "phase3": {
        "agents": ["reporter"],
        "task": "Create final report",
        "dependencies": ["phase2"]
    }
}

# Execute coordinated workflow
result = swarm.execute_coordination_plan(coordination_plan)
print(f"Coordinated workflow completed in {result.execution_time:.2f}s")
```