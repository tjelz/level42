#!/usr/bin/env python3
"""
Multi-Agent Research Swarm Example

This example demonstrates advanced swarm coordination features:
- Collaborative agents working on research tasks
- Cost-splitting for shared research tasks
- Agent-to-agent fund transfers
- Swarm-level coordination and communication

Requirements: 4.1, 4.3, 4.4
"""

import os
import time
from typing import Dict, List, Any
from x402_agent import X402Agent, AgentSwarm


class ResearchLLMProvider:
    """Mock LLM provider specialized for research tasks."""
    
    def __init__(self, specialty: str):
        """Initialize with research specialty."""
        self.specialty = specialty
    
    def generate_response(self, prompt: str, tools=None) -> str:
        """Generate research-focused responses based on specialty."""
        if self.specialty == "data_analysis":
            return f"Data Analysis: {prompt} - Analyzing datasets and statistical patterns."
        elif self.specialty == "literature_review":
            return f"Literature Review: {prompt} - Reviewing academic papers and sources."
        elif self.specialty == "market_research":
            return f"Market Research: {prompt} - Analyzing market trends and consumer behavior."
        elif self.specialty == "technical_research":
            return f"Technical Research: {prompt} - Investigating technical specifications and implementations."
        else:
            return f"General Research ({self.specialty}): {prompt}"


class ResearchSwarm:
    """
    Multi-agent research swarm that demonstrates collaborative research,
    cost-splitting, and agent-to-agent fund transfers.
    """
    
    def __init__(self, private_key: str, shared_wallet: bool = True):
        """Initialize research swarm with specialized agents."""
        self.swarm = AgentSwarm(shared_wallet=shared_wallet)
        self.research_results = {}
        self.collaboration_history = []
        
        # Create specialized research agents
        self._create_research_agents(private_key)
        
        # Register research tools for all agents
        self._register_research_tools()
    
    def _create_research_agents(self, private_key: str):
        """Create specialized research agents with different capabilities."""
        
        research_specialties = [
            ("data_analyst", "data_analysis", "Specializes in data analysis and statistics"),
            ("literature_reviewer", "literature_review", "Focuses on academic literature and sources"),
            ("market_researcher", "market_research", "Analyzes market trends and consumer behavior"),
            ("tech_researcher", "technical_research", "Investigates technical implementations")
        ]
        
        for agent_name, specialty, description in research_specialties:
            # Create LLM provider with specialty
            llm = ResearchLLMProvider(specialty)
            
            # Create agent
            agent = X402Agent(llm, private_key, network="base")
            
            # Add custom attributes for research specialization
            agent.specialty = specialty
            agent.description = description
            agent.research_history = []
            
            # Add to swarm
            self.swarm.add_agent(agent)
            
            print(f"🔬 Created {agent_name} agent: {description}")
    
    def _register_research_tools(self):
        """Register research-specific APIs for all agents."""
        
        research_apis = [
            {
                "name": "academic_search",
                "endpoint": "https://api.academic.com/v1/search",
                "description": "Search academic papers and publications"
            },
            {
                "name": "data_sources",
                "endpoint": "https://api.datasources.com/v1/datasets",
                "description": "Access to various research datasets"
            },
            {
                "name": "market_intelligence",
                "endpoint": "https://api.marketintel.com/v1/reports",
                "description": "Market intelligence and industry reports"
            },
            {
                "name": "patent_search",
                "endpoint": "https://api.patents.com/v1/search",
                "description": "Patent database search and analysis"
            },
            {
                "name": "survey_platform",
                "endpoint": "https://api.surveys.com/v1/responses",
                "description": "Survey data collection and analysis"
            }
        ]
        
        # Register tools for all agents in swarm
        for agent in self.swarm.agents.values():
            for api in research_apis:
                agent.register_tool(**api)
        
        print(f"🔧 Registered {len(research_apis)} research APIs for all agents")
    
    def conduct_collaborative_research(self, research_topic: str) -> Dict[str, Any]:
        """
        Conduct collaborative research with cost-splitting and coordination.
        
        Args:
            research_topic: Topic to research collaboratively
            
        Returns:
            Comprehensive research results from all agents
        """
        print(f"🔍 Starting collaborative research on: {research_topic}")
        
        # Track initial balances for cost analysis
        initial_balances = {}
        for agent_id, agent in self.swarm.agents.items():
            initial_balances[agent_id] = agent.get_balance()
        
        # Phase 1: Parallel research by all agents
        print("\n📊 Phase 1: Parallel Research")
        parallel_results = self.swarm.collaborate(
            task=f"Research the topic: {research_topic}",
            distribution_strategy="parallel"
        )
        
        # Phase 2: Sequential deep-dive building on initial findings
        print("\n🔬 Phase 2: Sequential Deep-Dive")
        deep_dive_prompt = f"""
        Based on initial research on {research_topic}, conduct a deeper analysis.
        Focus on your specialty and build upon the initial findings.
        """
        sequential_results = self.swarm.collaborate(
            task=deep_dive_prompt,
            distribution_strategy="sequential"
        )
        
        # Phase 3: Divided specialized analysis
        print("\n🎯 Phase 3: Specialized Analysis")
        specialized_tasks = [
            f"Analyze data patterns and statistics for {research_topic}",
            f"Review academic literature and citations for {research_topic}",
            f"Assess market implications and opportunities for {research_topic}",
            f"Evaluate technical feasibility and implementation for {research_topic}"
        ]
        
        specialized_results = {}
        agent_ids = list(self.swarm.agents.keys())
        
        for i, (agent_id, task) in enumerate(zip(agent_ids, specialized_tasks)):
            agent = self.swarm.agents[agent_id]
            try:
                result = agent.run(task)
                specialized_results[agent_id] = result
                print(f"✅ {agent.specialty} completed specialized analysis")
            except Exception as e:
                specialized_results[agent_id] = f"ERROR: {str(e)}"
                print(f"❌ {agent.specialty} failed: {e}")
        
        # Calculate total research costs
        final_balances = {}
        total_cost = 0.0
        
        for agent_id, agent in self.swarm.agents.items():
            final_balances[agent_id] = agent.get_balance()
            agent_cost = initial_balances[agent_id] - final_balances[agent_id]
            total_cost += agent_cost
            
            # Update swarm spending tracking
            self.swarm.update_agent_spending(agent_id, agent_cost, "collaborative_research")
        
        # Demonstrate cost-splitting
        print(f"\n💰 Total research cost: ${total_cost:.4f} USDC")
        cost_distribution = self.swarm.split_costs(total_cost)
        
        print("💸 Cost distribution among agents:")
        for agent_id, cost_share in cost_distribution.items():
            print(f"  {agent_id}: ${cost_share:.4f} USDC")
        
        # Compile comprehensive results
        research_results = {
            "topic": research_topic,
            "timestamp": time.time(),
            "phases": {
                "parallel_research": parallel_results,
                "sequential_deep_dive": sequential_results,
                "specialized_analysis": specialized_results
            },
            "cost_analysis": {
                "total_cost": total_cost,
                "cost_distribution": cost_distribution,
                "initial_balances": initial_balances,
                "final_balances": final_balances
            },
            "participating_agents": len(self.swarm.agents)
        }
        
        # Store results
        self.research_results[research_topic] = research_results
        self.collaboration_history.append({
            "topic": research_topic,
            "timestamp": time.time(),
            "cost": total_cost,
            "agents": len(self.swarm.agents)
        })
        
        return research_results
    
    def demonstrate_fund_transfers(self) -> Dict[str, Any]:
        """
        Demonstrate agent-to-agent fund transfers within the swarm.
        
        Returns:
            Transfer results and balance changes
        """
        print("\n💸 Demonstrating Agent-to-Agent Fund Transfers")
        
        agent_ids = list(self.swarm.agents.keys())
        if len(agent_ids) < 2:
            return {"error": "Need at least 2 agents for transfers"}
        
        # Get initial balances
        initial_balances = {}
        for agent_id, agent in self.swarm.agents.items():
            initial_balances[agent_id] = agent.get_balance()
        
        transfer_results = {}
        
        # Transfer 1: From highest balance agent to lowest balance agent
        balances = [(aid, self.swarm.agents[aid].get_balance()) for aid in agent_ids]
        balances.sort(key=lambda x: x[1], reverse=True)
        
        highest_balance_agent = balances[0][0]
        lowest_balance_agent = balances[-1][0]
        transfer_amount = 0.05  # Transfer 5 cents
        
        try:
            tx_hash = self.swarm.transfer_to_agent(
                highest_balance_agent, 
                lowest_balance_agent, 
                transfer_amount
            )
            transfer_results["balance_equalization"] = {
                "from": highest_balance_agent,
                "to": lowest_balance_agent,
                "amount": transfer_amount,
                "tx_hash": tx_hash,
                "status": "success"
            }
            print(f"✅ Transferred ${transfer_amount} from {highest_balance_agent} to {lowest_balance_agent}")
            
        except Exception as e:
            transfer_results["balance_equalization"] = {
                "error": str(e),
                "status": "failed"
            }
            print(f"❌ Transfer failed: {e}")
        
        # Transfer 2: Circular transfers (each agent sends to next)
        circular_transfers = []
        for i in range(len(agent_ids)):
            from_agent = agent_ids[i]
            to_agent = agent_ids[(i + 1) % len(agent_ids)]  # Circular
            
            try:
                tx_hash = self.swarm.transfer_to_agent(from_agent, to_agent, 0.01)  # 1 cent
                circular_transfers.append({
                    "from": from_agent,
                    "to": to_agent,
                    "amount": 0.01,
                    "tx_hash": tx_hash,
                    "status": "success"
                })
                print(f"✅ Circular transfer: ${0.01} from {from_agent} to {to_agent}")
                
            except Exception as e:
                circular_transfers.append({
                    "from": from_agent,
                    "to": to_agent,
                    "amount": 0.01,
                    "error": str(e),
                    "status": "failed"
                })
                print(f"❌ Circular transfer failed: {e}")
        
        transfer_results["circular_transfers"] = circular_transfers
        
        # Get final balances
        final_balances = {}
        for agent_id, agent in self.swarm.agents.items():
            final_balances[agent_id] = agent.get_balance()
        
        transfer_results["balance_changes"] = {
            "initial": initial_balances,
            "final": final_balances,
            "changes": {
                aid: final_balances[aid] - initial_balances[aid] 
                for aid in agent_ids
            }
        }
        
        return transfer_results
    
    def get_swarm_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics for the research swarm."""
        
        # Agent information
        agent_info = self.swarm.list_agents()
        
        # Spending summary
        spending_summary = self.swarm.get_swarm_spending_summary()
        
        # Research history
        research_summary = {
            "total_research_projects": len(self.research_results),
            "collaboration_history": self.collaboration_history,
            "topics_researched": list(self.research_results.keys())
        }
        
        # Swarm health metrics
        total_balance = self.swarm.get_swarm_balance()
        avg_balance = total_balance / len(self.swarm.agents) if self.swarm.agents else 0
        
        health_metrics = {
            "total_swarm_balance": total_balance,
            "average_agent_balance": avg_balance,
            "active_agents": len(self.swarm.agents),
            "balance_distribution": {
                aid: agent.get_balance() 
                for aid, agent in self.swarm.agents.items()
            }
        }
        
        return {
            "agent_info": agent_info,
            "spending_summary": spending_summary,
            "research_summary": research_summary,
            "health_metrics": health_metrics,
            "swarm_config": {
                "shared_wallet": self.swarm.config.shared_wallet,
                "cost_splitting_method": self.swarm.config.cost_splitting_method.value,
                "max_agents": self.swarm.config.max_agents
            }
        }
    
    def run_research_session(self, topics: List[str]) -> Dict[str, Any]:
        """
        Run a complete research session with multiple topics.
        
        Args:
            topics: List of research topics to investigate
            
        Returns:
            Session results and analytics
        """
        print("🚀 Starting Multi-Agent Research Session")
        print(f"📋 Topics to research: {topics}")
        print(f"🤖 Active agents: {len(self.swarm.agents)}")
        print(f"💰 Initial swarm balance: ${self.swarm.get_swarm_balance():.2f} USDC")
        
        session_results = {
            "topics": topics,
            "research_results": {},
            "transfer_demo": {},
            "session_analytics": {}
        }
        
        # Conduct research on each topic
        for i, topic in enumerate(topics, 1):
            print(f"\n{'='*50}")
            print(f"Research Project {i}/{len(topics)}: {topic}")
            print(f"{'='*50}")
            
            try:
                research_result = self.conduct_collaborative_research(topic)
                session_results["research_results"][topic] = research_result
                
                # Small delay between research projects
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Research failed for {topic}: {e}")
                session_results["research_results"][topic] = {"error": str(e)}
        
        # Demonstrate fund transfers
        print(f"\n{'='*50}")
        print("Fund Transfer Demonstration")
        print(f"{'='*50}")
        
        try:
            transfer_results = self.demonstrate_fund_transfers()
            session_results["transfer_demo"] = transfer_results
        except Exception as e:
            print(f"❌ Fund transfer demo failed: {e}")
            session_results["transfer_demo"] = {"error": str(e)}
        
        # Generate session analytics
        session_results["session_analytics"] = self.get_swarm_analytics()
        
        # Session summary
        print(f"\n{'='*50}")
        print("Research Session Summary")
        print(f"{'='*50}")
        
        successful_research = len([r for r in session_results["research_results"].values() 
                                 if "error" not in r])
        total_cost = sum(
            r.get("cost_analysis", {}).get("total_cost", 0) 
            for r in session_results["research_results"].values()
            if "error" not in r
        )
        
        print(f"✅ Successful research projects: {successful_research}/{len(topics)}")
        print(f"💸 Total session cost: ${total_cost:.4f} USDC")
        print(f"💰 Final swarm balance: ${self.swarm.get_swarm_balance():.2f} USDC")
        print(f"🤖 Agents participated: {len(self.swarm.agents)}")
        
        return session_results


def main():
    """Demonstrate multi-agent research swarm capabilities."""
    
    # Get wallet private key from environment
    private_key = os.getenv("WALLET_PRIVATE_KEY")
    if not private_key:
        print("Please set WALLET_PRIVATE_KEY environment variable")
        return
    
    # Create research swarm with shared wallet
    swarm = ResearchSwarm(private_key, shared_wallet=True)
    
    # Research topics for demonstration
    research_topics = [
        "Artificial Intelligence in Healthcare",
        "Blockchain Scalability Solutions",
        "Sustainable Energy Technologies"
    ]
    
    try:
        # Run complete research session
        session_results = swarm.run_research_session(research_topics)
        
        print("\n🎯 Key Features Demonstrated:")
        print("✅ Multi-agent collaborative research")
        print("✅ Cost-splitting for shared research tasks")
        print("✅ Agent-to-agent fund transfers")
        print("✅ Swarm coordination and communication")
        print("✅ Specialized agent roles and capabilities")
        print("✅ Comprehensive spending analytics")
        
        # Optional: Save results to file
        import json
        with open("research_session_results.json", "w") as f:
            # Convert any non-serializable objects to strings
            serializable_results = json.loads(json.dumps(session_results, default=str))
            json.dump(serializable_results, f, indent=2)
        
        print("\n📄 Session results saved to research_session_results.json")
        
    except Exception as e:
        print(f"❌ Research session error: {e}")


if __name__ == "__main__":
    main()