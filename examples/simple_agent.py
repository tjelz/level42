#!/usr/bin/env python3
"""
Simple Agent Example

This example demonstrates basic usage of the x402-Agent Framework:
- One-line agent creation
- Tool registration
- Automatic payment handling for API calls

Requirements: 5.3, 5.4
"""

import os
from x402_agent import X402Agent


class MockLLMProvider:
    """Mock LLM provider for demonstration purposes."""
    
    def generate_response(self, prompt: str, tools=None) -> str:
        """Generate a simple mock response."""
        return f"Mock response to: {prompt}"


def main():
    """Demonstrate simple agent usage."""
    
    # Get wallet private key from environment (for security)
    private_key = os.getenv("WALLET_PRIVATE_KEY")
    if not private_key:
        print("Please set WALLET_PRIVATE_KEY environment variable")
        return
    
    # One-line agent creation with LLM and wallet
    llm = MockLLMProvider()
    agent = X402Agent(llm, private_key, network="base")
    
    print("🤖 Simple x402-Agent created successfully!")
    print(f"💰 Current balance: ${agent.get_balance():.2f} USDC")
    
    # Register a tool (API endpoint that accepts x402 payments)
    agent.register_tool(
        name="weather_api",
        endpoint="https://api.weather.com/v1/current",
        description="Get current weather data with automatic payment"
    )
    
    print("🔧 Weather API tool registered")
    
    # Example API call with automatic payment handling
    # The agent will automatically handle HTTP 402 responses and make payments
    try:
        response = agent.run("What's the weather like in San Francisco?")
        print(f"🌤️  Agent response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"💰 Balance after API call: ${agent.get_balance():.2f} USDC")


if __name__ == "__main__":
    main()