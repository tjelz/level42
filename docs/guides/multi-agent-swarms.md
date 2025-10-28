# Multi-Agent Swarms Guide

This guide covers creating and managing collaborative multi-agent systems using the x402-Agent Framework.

## Overview

Multi-agent swarms enable multiple AI agents to work together on complex tasks, sharing costs and leveraging specialized capabilities. The x402-Agent Framework provides built-in coordination, cost-splitting, and communication features for seamless collaboration.

## Key Concepts

### Agent Specialization

Different agents can be optimized for specific tasks:

- **Data Collectors**: Gather information from various sources
- **Analyzers**: Process and analyze collected data
- **Reporters**: Generate summaries and reports
- **Coordinators**: Manage workflow and task distribution

### Collaboration Strategies

- **Parallel**: All agents work simultaneously on the same task
- **Sequential**: Agents work in order, building on previous results
- **Divide and Conquer**: Task is split into subtasks for different agents

### Cost Management

- **Shared Wallets**: All agents use a common funding source
- **Individual Wallets**: Each agent manages its own funds
- **Cost Splitting**: Automatic distribution of expenses among agents

## Creating Your First Swarm

### 1. Basic Swarm Setup

```python
from x402_agent import X402Agent
from x402_agent.swarm import AgentSwarm
from langchain_openai import ChatOpenAI

# Initialize LLM
llm = ChatOpenAI(model="gpt-4")

# Create specialized agents
researcher = X402Agent(
    llm=llm,
    wallet_key="0xresearcher_key...",
    network="base",
    max_spend_per_hour=15.0
)

analyst = X402Agent(
    llm=llm,
    wallet_key="0xanalyst_key...",
    network="base",
    max_spend_per_hour=20.0
)

writer = X402Agent(
    llm=llm,
    wallet_key="0xwriter_key...",
    network="base",
    max_spend_per_hour=10.0
)

# Create swarm
swarm = AgentSwarm(shared_wallet=False, cost_splitting="proportional")

# Add agents with roles
swarm.add_agent(researcher, "researcher", "Data collection and research")
swarm.add_agent(analyst, "analyst", "Data analysis and insights")
swarm.add_agent(writer, "writer", "Report writing and summarization")

print(f"Swarm created with {len(swarm.agents)} agents")
```

### 2. Register Specialized Tools

```python
# Researcher tools - data collection
researcher.register_tool("arxiv", "https://api.arxiv.org/search", "Academic papers")
researcher.register_tool("patents", "https://api.patents.com/search", "Patent database")
researcher.register_tool("news", "https://api.news.com/search", "News articles")

# Analyst tools - data processing
analyst.register_tool("sentiment", "https://api.sentiment.com/analyze", "Sentiment analysis")
analyst.register_tool("trends", "https://api.trends.com/analyze", "Trend analysis")
analyst.register_tool("statistics", "https://api.stats.com/compute", "Statistical analysis")

# Writer tools - content generation
writer.register_tool("grammar", "https://api.grammar.com/check", "Grammar checking")
writer.register_tool("style", "https://api.style.com/improve", "Style improvement")
writer.register_tool("translate", "https://api.translate.com/convert", "Translation")

print("All agents equipped with specialized tools")
```

## Collaboration Strategies

### 1. Parallel Collaboration

All agents work on the same task simultaneously, providing diverse perspectives.

```python
# Parallel research on AI developments
result = swarm.collaborate(
    task="Research the latest developments in artificial intelligence",
    strategy="parallel",
    max_agents=3
)

print(f"Parallel collaboration result:")
print(f"Summary: {result.summary}")
print(f"Total cost: ${result.total_cost:.2f}")
print(f"Execution time: {result.execution_time:.2f}s")
print(f"Participating agents: {result.participating_agents}")
```

**Benefits of Parallel Strategy:**
- Fast execution
- Multiple perspectives
- Redundancy for reliability
- Good for research and opinion gathering

### 2. Sequential Collaboration

Agents work in order, each building on the previous agent's work.

```python
# Sequential workflow: Research → Analyze → Report
result = swarm.collaborate(
    task="Create a comprehensive market analysis report",
    strategy="sequential",
    agent_order=["researcher", "analyst", "writer"]
)

print(f"Sequential collaboration completed:")
print(f"Final report: {result.final_output}")
print(f"Stage results: {result.stage_results}")
```

**Benefits of Sequential Strategy:**
- Builds on previous work
- Maintains consistency
- Quality refinement at each stage
- Good for reports and analysis pipelines

### 3. Divide and Conquer

Task is automatically divided into subtasks for different agents.

```python
# Divide complex analysis task
result = swarm.collaborate(
    task="Analyze the cryptocurrency market across Bitcoin, Ethereum, and Solana",
    strategy="divide_and_conquer",
    division_method="automatic"  # or "manual" with custom subtasks
)

print(f"Divide and conquer results:")
for subtask, agent_result in result.subtask_results.items():
    print(f"  {subtask}: {agent_result.summary}")
```

**Benefits of Divide and Conquer:**
- Efficient resource utilization
- Specialized expertise application
- Parallel processing of subtasks
- Good for large, complex problems

## Advanced Swarm Features

### 1. Custom Task Division

```python
# Manually define subtasks
subtasks = swarm.divide_task(
    task="Comprehensive AI market analysis",
    num_subtasks=3
)

# Customize subtasks
custom_subtasks = {
    "researcher": "Collect data on AI companies and funding",
    "analyst": "Analyze market trends and growth patterns",
    "writer": "Create executive summary and recommendations"
}

# Execute with custom assignment
result = swarm.execute_custom_collaboration(custom_subtasks)
```

### 2. Dynamic Agent Assignment

```python
# Assign tasks based on agent capabilities
def assign_by_capability(task, agents):
    """Custom assignment logic based on agent capabilities."""
    assignments = {}
    
    if "research" in task.lower():
        assignments["researcher"] = task
    elif "analyze" in task.lower():
        assignments["analyst"] = task
    elif "write" in task.lower():
        assignments["writer"] = task
    else:
        # Default to round-robin
        assignments = swarm.assign_tasks([task], "round_robin")
    
    return assignments

# Use custom assignment
swarm.set_assignment_strategy(assign_by_capability)
```

### 3. Inter-Agent Communication

```python
# Enable agent-to-agent messaging
swarm.enable_inter_agent_communication()

# Agents can now send messages during collaboration
def collaboration_with_communication():
    # Researcher finds interesting data
    swarm.send_message(
        from_agent="researcher",
        to_agent="analyst",
        message="Found unusual pattern in AI funding data",
        data={"pattern_type": "seasonal", "confidence": 0.85}
    )
    
    # Analyst requests more data
    swarm.send_message(
        from_agent="analyst",
        to_agent="researcher",
        message="Need more data on Q4 funding rounds",
        request_type="data_collection"
    )

# Monitor inter-agent communication
def message_handler(message):
    print(f"Message: {message.from_agent} → {message.to_agent}: {message.content}")

swarm.add_message_callback(message_handler)
```

## Cost Management

### 1. Shared Wallet Configuration

```python
# Create swarm with shared wallet
shared_swarm = AgentSwarm(
    shared_wallet=True,
    shared_wallet_key="0xshared_wallet_key...",
    cost_splitting="equal"
)

# All agents use the same wallet
shared_swarm.add_agent(researcher, "researcher")
shared_swarm.add_agent(analyst, "analyst")
shared_swarm.add_agent(writer, "writer")

# Check shared balance
total_balance = shared_swarm.get_swarm_balance()
print(f"Shared wallet balance: ${total_balance['total']:.2f}")
```

### 2. Cost Splitting Methods

```python
# Equal splitting (default)
equal_swarm = AgentSwarm(cost_splitting="equal")

# Proportional splitting based on usage
proportional_swarm = AgentSwarm(cost_splitting="proportional")

# Custom splitting logic
def custom_cost_split(total_cost, agents, usage_data):
    """Custom cost splitting based on agent roles."""
    splits = {}
    
    # Researcher pays 40%, analyst 35%, writer 25%
    splits["researcher"] = total_cost * 0.40
    splits["analyst"] = total_cost * 0.35
    splits["writer"] = total_cost * 0.25
    
    return splits

custom_swarm = AgentSwarm(cost_splitting="custom")
custom_swarm.set_custom_split_function(custom_cost_split)
```

### 3. Fund Transfers Between Agents

```python
# Transfer funds between agents
tx_hash = swarm.transfer_funds(
    from_agent="researcher",
    to_agent="analyst",
    amount=5.0,
    memo="Funding for additional analysis"
)

print(f"Transfer completed: {tx_hash}")

# Check individual agent balances
for agent_id in swarm.agents:
    agent = swarm.agents[agent_id]
    balance = agent.get_balance()
    print(f"{agent_id} balance: ${balance:.2f}")
```

## Monitoring and Analytics

### 1. Swarm Performance Monitoring

```python
from x402_agent.monitoring import AgentMonitor

# Set up swarm-level monitoring
swarm_monitor = AgentMonitor(
    agent_id="research_swarm",
    storage_backend="postgresql"
)

# Monitor collaboration events
def collaboration_monitor(event):
    print(f"Swarm event: {event.type}")
    print(f"Agents involved: {event.agents}")
    print(f"Cost: ${event.cost:.2f}")
    print(f"Duration: {event.duration:.2f}s")

swarm.add_event_callback(collaboration_monitor)

# Get swarm analytics
analytics = swarm.get_collaboration_summary()
print(f"Total collaborations: {analytics['total_count']}")
print(f"Success rate: {analytics['success_rate']:.2%}")
print(f"Average cost: ${analytics['avg_cost']:.2f}")
```

### 2. Individual Agent Performance

```python
# Monitor each agent's contribution
for agent_id, agent in swarm.agents.items():
    performance = agent.get_performance_metrics()
    print(f"\n{agent_id} Performance:")
    print(f"  Tasks completed: {performance['tasks_completed']}")
    print(f"  Success rate: {performance['success_rate']:.2%}")
    print(f"  Average response time: {performance['avg_response_time']:.2f}s")
    print(f"  Total spent: ${performance['total_spent']:.2f}")
```

### 3. Cost Efficiency Analysis

```python
def analyze_cost_efficiency(swarm):
    """Analyze swarm cost efficiency."""
    
    # Get collaboration history
    history = swarm.get_collaboration_history()
    
    efficiency_metrics = {
        "cost_per_task": [],
        "time_per_task": [],
        "agents_per_task": []
    }
    
    for collaboration in history:
        efficiency_metrics["cost_per_task"].append(collaboration.total_cost)
        efficiency_metrics["time_per_task"].append(collaboration.execution_time)
        efficiency_metrics["agents_per_task"].append(len(collaboration.participating_agents))
    
    # Calculate averages
    avg_cost = sum(efficiency_metrics["cost_per_task"]) / len(efficiency_metrics["cost_per_task"])
    avg_time = sum(efficiency_metrics["time_per_task"]) / len(efficiency_metrics["time_per_task"])
    avg_agents = sum(efficiency_metrics["agents_per_task"]) / len(efficiency_metrics["agents_per_task"])
    
    print(f"Swarm Efficiency Analysis:")
    print(f"  Average cost per task: ${avg_cost:.2f}")
    print(f"  Average time per task: {avg_time:.2f}s")
    print(f"  Average agents per task: {avg_agents:.1f}")
    print(f"  Cost efficiency: ${avg_cost/avg_time:.4f} per second")

analyze_cost_efficiency(swarm)
```

## Real-World Examples

### 1. Market Research Swarm

```python
# Create specialized market research team
market_swarm = AgentSwarm(shared_wallet=True, cost_splitting="equal")

# Data collector agent
data_collector = X402Agent(llm, "0xdata_key...", network="base")
data_collector.register_tool("market_data", "https://api.market.com/data", "Market data")
data_collector.register_tool("competitor", "https://api.competitor.com/analysis", "Competitor analysis")

# Trend analyzer agent
trend_analyzer = X402Agent(llm, "0xtrend_key...", network="base")
trend_analyzer.register_tool("trends", "https://api.trends.com/analyze", "Trend analysis")
trend_analyzer.register_tool("forecasting", "https://api.forecast.com/predict", "Market forecasting")

# Report generator agent
report_generator = X402Agent(llm, "0xreport_key...", network="base")
report_generator.register_tool("visualization", "https://api.viz.com/create", "Data visualization")
report_generator.register_tool("formatting", "https://api.format.com/style", "Report formatting")

# Add to swarm
market_swarm.add_agent(data_collector, "data_collector")
market_swarm.add_agent(trend_analyzer, "trend_analyzer")
market_swarm.add_agent(report_generator, "report_generator")

# Execute market research
result = market_swarm.collaborate(
    task="Conduct comprehensive market research for electric vehicle industry",
    strategy="sequential"
)

print(f"Market research completed:")
print(f"Report: {result.final_output}")
print(f"Total cost: ${result.total_cost:.2f}")
```

### 2. Content Creation Swarm

```python
# Create content creation pipeline
content_swarm = AgentSwarm(shared_wallet=False, cost_splitting="proportional")

# Research agent
researcher = X402Agent(llm, "0xresearch_key...", network="base")
researcher.register_tool("web_search", "https://api.search.com/web", "Web search")
researcher.register_tool("fact_check", "https://api.factcheck.com/verify", "Fact checking")

# Writer agent
writer = X402Agent(llm, "0xwriter_key...", network="base")
writer.register_tool("grammar", "https://api.grammar.com/check", "Grammar checking")
writer.register_tool("style", "https://api.style.com/improve", "Style improvement")

# Editor agent
editor = X402Agent(llm, "0xeditor_key...", network="base")
editor.register_tool("plagiarism", "https://api.plagiarism.com/check", "Plagiarism detection")
editor.register_tool("seo", "https://api.seo.com/optimize", "SEO optimization")

# Add to swarm
content_swarm.add_agent(researcher, "researcher")
content_swarm.add_agent(writer, "writer")
content_swarm.add_agent(editor, "editor")

# Create content collaboratively
result = content_swarm.collaborate(
    task="Create a comprehensive blog post about blockchain technology trends",
    strategy="sequential",
    quality_checks=True
)
```

### 3. Trading Analysis Swarm

```python
# Create trading analysis team
trading_swarm = AgentSwarm(shared_wallet=True, cost_splitting="custom")

# Market data agent
market_agent = X402Agent(llm, "0xmarket_key...", network="base")
market_agent.register_tool("prices", "https://api.prices.com/realtime", "Real-time prices")
market_agent.register_tool("volume", "https://api.volume.com/data", "Trading volume")

# Technical analysis agent
technical_agent = X402Agent(llm, "0xtech_key...", network="base")
technical_agent.register_tool("indicators", "https://api.indicators.com/calculate", "Technical indicators")
technical_agent.register_tool("patterns", "https://api.patterns.com/detect", "Chart patterns")

# Sentiment analysis agent
sentiment_agent = X402Agent(llm, "0xsentiment_key...", network="base")
sentiment_agent.register_tool("news_sentiment", "https://api.news.com/sentiment", "News sentiment")
sentiment_agent.register_tool("social_sentiment", "https://api.social.com/sentiment", "Social sentiment")

# Risk management agent
risk_agent = X402Agent(llm, "0xrisk_key...", network="base")
risk_agent.register_tool("risk_calc", "https://api.risk.com/calculate", "Risk calculation")
risk_agent.register_tool("portfolio", "https://api.portfolio.com/analyze", "Portfolio analysis")

# Custom cost splitting for trading swarm
def trading_cost_split(total_cost, agents, usage_data):
    return {
        "market_agent": total_cost * 0.30,
        "technical_agent": total_cost * 0.25,
        "sentiment_agent": total_cost * 0.25,
        "risk_agent": total_cost * 0.20
    }

trading_swarm.set_custom_split_function(trading_cost_split)

# Add agents
trading_swarm.add_agent(market_agent, "market_agent")
trading_swarm.add_agent(technical_agent, "technical_agent")
trading_swarm.add_agent(sentiment_agent, "sentiment_agent")
trading_swarm.add_agent(risk_agent, "risk_agent")

# Perform comprehensive trading analysis
result = trading_swarm.collaborate(
    task="Analyze Bitcoin trading opportunity with full risk assessment",
    strategy="parallel",
    consolidation_strategy="weighted_average"
)
```

## Best Practices

### 1. Agent Design

```python
# ✅ Good: Specialized agents with clear roles
researcher = X402Agent(llm, key, network="base")
researcher.register_tool("arxiv", "https://api.arxiv.org/search")

analyst = X402Agent(llm, key, network="base")
analyst.register_tool("statistics", "https://api.stats.com/analyze")

# ❌ Bad: Generic agents with overlapping capabilities
generic_agent = X402Agent(llm, key, network="base")
generic_agent.register_tool("everything", "https://api.everything.com")
```

### 2. Cost Management

```python
# ✅ Good: Set appropriate spending limits per agent
high_usage_agent = X402Agent(llm, key, max_spend_per_hour=25.0)
low_usage_agent = X402Agent(llm, key, max_spend_per_hour=5.0)

# ✅ Good: Monitor swarm costs
def cost_monitor(collaboration_result):
    if collaboration_result.total_cost > 10.0:
        print(f"High cost alert: ${collaboration_result.total_cost:.2f}")

swarm.add_collaboration_callback(cost_monitor)
```

### 3. Error Handling

```python
# ✅ Good: Robust error handling for swarm operations
def safe_collaboration(swarm, task, **kwargs):
    try:
        result = swarm.collaborate(task, **kwargs)
        return result
    except InsufficientAgentsError:
        print("Not enough agents available")
        return None
    except CollaborationTimeoutError:
        print("Collaboration timed out")
        return None
    except Exception as e:
        print(f"Collaboration failed: {e}")
        return None

result = safe_collaboration(swarm, "Complex analysis task")
```

### 4. Performance Optimization

```python
# ✅ Good: Optimize agent assignment
def optimize_agent_assignment(task, available_agents):
    """Assign agents based on current load and capabilities."""
    
    # Check agent availability and current load
    agent_loads = {}
    for agent_id, agent in available_agents.items():
        current_tasks = agent.get_active_tasks_count()
        agent_loads[agent_id] = current_tasks
    
    # Assign to least loaded, most capable agent
    best_agent = min(agent_loads.keys(), key=lambda x: agent_loads[x])
    return best_agent

swarm.set_assignment_optimizer(optimize_agent_assignment)
```

## Troubleshooting

### 1. Communication Issues

```python
# Debug inter-agent communication
def debug_communication(swarm):
    print("Testing inter-agent communication...")
    
    for sender_id in swarm.agents:
        for receiver_id in swarm.agents:
            if sender_id != receiver_id:
                try:
                    swarm.send_message(sender_id, receiver_id, "Test message")
                    print(f"✅ {sender_id} → {receiver_id}: OK")
                except Exception as e:
                    print(f"❌ {sender_id} → {receiver_id}: {e}")

debug_communication(swarm)
```

### 2. Cost Splitting Issues

```python
# Debug cost splitting
def debug_cost_splitting(swarm, test_cost=10.0):
    print(f"Testing cost splitting for ${test_cost:.2f}...")
    
    try:
        allocation = swarm.split_costs(test_cost)
        total_allocated = sum(allocation.values())
        
        print(f"Cost allocation:")
        for agent_id, cost in allocation.items():
            print(f"  {agent_id}: ${cost:.2f}")
        
        print(f"Total allocated: ${total_allocated:.2f}")
        
        if abs(total_allocated - test_cost) > 0.01:
            print("⚠️  Warning: Cost allocation doesn't sum to total")
        else:
            print("✅ Cost allocation is correct")
            
    except Exception as e:
        print(f"❌ Cost splitting failed: {e}")

debug_cost_splitting(swarm)
```

### 3. Performance Issues

```python
# Monitor swarm performance
def monitor_swarm_performance(swarm):
    """Monitor and report swarm performance issues."""
    
    performance_issues = []
    
    # Check individual agent performance
    for agent_id, agent in swarm.agents.items():
        metrics = agent.get_performance_metrics()
        
        if metrics['success_rate'] < 0.90:
            performance_issues.append(f"{agent_id}: Low success rate ({metrics['success_rate']:.2%})")
        
        if metrics['avg_response_time'] > 10.0:
            performance_issues.append(f"{agent_id}: Slow response time ({metrics['avg_response_time']:.2f}s)")
    
    # Check swarm-level metrics
    swarm_metrics = swarm.get_performance_analytics()
    
    if swarm_metrics['avg_collaboration_time'] > 60.0:
        performance_issues.append(f"Swarm: Slow collaborations ({swarm_metrics['avg_collaboration_time']:.2f}s)")
    
    if performance_issues:
        print("Performance Issues Detected:")
        for issue in performance_issues:
            print(f"  ⚠️  {issue}")
    else:
        print("✅ No performance issues detected")

monitor_swarm_performance(swarm)
```

## Next Steps

After mastering multi-agent swarms:

1. **Advanced Coordination**: Implement complex workflow patterns
2. **Dynamic Scaling**: Add/remove agents based on workload
3. **Cross-Network Swarms**: Agents on different blockchain networks
4. **AI-Driven Optimization**: Use ML to optimize agent assignment
5. **Enterprise Integration**: Connect swarms to existing business systems

### Related Guides

- [Payment Optimization Guide](./payment-optimization.md)
- [Production Deployment Guide](./production-deployment.md)
- [Monitoring and Analytics Guide](./monitoring-analytics.md)

Multi-agent swarms unlock the full potential of the x402-Agent Framework, enabling sophisticated AI systems that can tackle complex, multi-faceted problems efficiently and cost-effectively. 🤖🚀