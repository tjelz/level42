#!/usr/bin/env python3
"""
Trading Bot Example

This example demonstrates advanced Level42 Framework features:
- Deferred payment batching with multiple API calls
- Portfolio management and spending tracking
- Stock/crypto API integration with automatic payments

Requirements: 3.1, 3.2, 7.3
"""

import os
import time
from typing import Dict, List
from level42 import Level42Agent


class TradingLLMProvider:
    """Mock LLM provider for trading decisions."""
    
    def generate_response(self, prompt: str, tools=None) -> str:
        """Generate trading-focused responses."""
        if "price" in prompt.lower():
            return "Based on market analysis, I recommend checking multiple data sources."
        elif "portfolio" in prompt.lower():
            return "Current portfolio shows good diversification. Consider rebalancing."
        else:
            return f"Trading analysis: {prompt}"


class TradingBot:
    """
    Advanced trading bot that demonstrates deferred payment batching
    and portfolio management with spending tracking.
    """
    
    def __init__(self, private_key: str):
        """Initialize trading bot with wallet."""
        self.llm = TradingLLMProvider()
        self.agent = Level42Agent(self.llm, private_key, network="base")
        self.portfolio = {}
        self.spending_log = []
        
        # Register multiple trading APIs
        self._register_trading_tools()
    
    def _register_trading_tools(self):
        """Register various trading and market data APIs."""
        trading_apis = [
            {
                "name": "stock_prices",
                "endpoint": "https://api.stockdata.com/v1/prices",
                "description": "Real-time stock price data"
            },
            {
                "name": "crypto_prices", 
                "endpoint": "https://api.cryptodata.com/v1/prices",
                "description": "Real-time cryptocurrency prices"
            },
            {
                "name": "market_news",
                "endpoint": "https://api.marketnews.com/v1/news",
                "description": "Latest market news and analysis"
            },
            {
                "name": "technical_analysis",
                "endpoint": "https://api.techanalysis.com/v1/indicators",
                "description": "Technical analysis indicators"
            },
            {
                "name": "sentiment_analysis",
                "endpoint": "https://api.sentiment.com/v1/analyze",
                "description": "Market sentiment analysis"
            }
        ]
        
        for api in trading_apis:
            self.agent.register_tool(**api)
            print(f"🔧 Registered {api['name']} API")
    
    def analyze_market(self, symbols: List[str]) -> Dict:
        """
        Perform comprehensive market analysis using multiple APIs.
        Demonstrates deferred payment batching with multiple API calls.
        """
        print(f"📊 Starting market analysis for {symbols}")
        initial_balance = self.agent.get_balance()
        
        analysis_results = {}
        
        # Make multiple API calls - these will be batched for payment
        for symbol in symbols:
            print(f"🔍 Analyzing {symbol}...")
            
            # Multiple API calls per symbol (demonstrates batching)
            try:
                # Stock/crypto price data
                price_response = self.agent.run(f"Get current price for {symbol}")
                
                # Technical analysis
                tech_response = self.agent.run(f"Get technical indicators for {symbol}")
                
                # Market sentiment
                sentiment_response = self.agent.run(f"Analyze sentiment for {symbol}")
                
                # News analysis
                news_response = self.agent.run(f"Get latest news for {symbol}")
                
                analysis_results[symbol] = {
                    "price": price_response,
                    "technical": tech_response,
                    "sentiment": sentiment_response,
                    "news": news_response
                }
                
            except Exception as e:
                print(f"❌ Error analyzing {symbol}: {e}")
                analysis_results[symbol] = {"error": str(e)}
        
        # Track spending for this analysis session
        final_balance = self.agent.get_balance()
        session_cost = initial_balance - final_balance
        
        self.spending_log.append({
            "timestamp": time.time(),
            "operation": "market_analysis",
            "symbols": symbols,
            "cost": session_cost,
            "api_calls": len(symbols) * 4  # 4 API calls per symbol
        })
        
        print(f"💰 Analysis cost: ${session_cost:.4f} USDC")
        print(f"📈 Processed {len(symbols) * 4} API calls")
        
        return analysis_results
    
    def update_portfolio(self, symbol: str, action: str, amount: float):
        """Update portfolio tracking."""
        if symbol not in self.portfolio:
            self.portfolio[symbol] = {"shares": 0, "avg_cost": 0}
        
        if action == "buy":
            current_shares = self.portfolio[symbol]["shares"]
            current_avg = self.portfolio[symbol]["avg_cost"]
            
            new_shares = current_shares + amount
            new_avg = ((current_shares * current_avg) + (amount * amount)) / new_shares
            
            self.portfolio[symbol] = {"shares": new_shares, "avg_cost": new_avg}
            
        elif action == "sell":
            self.portfolio[symbol]["shares"] -= amount
            if self.portfolio[symbol]["shares"] <= 0:
                del self.portfolio[symbol]
    
    def get_portfolio_summary(self) -> Dict:
        """Get current portfolio and spending summary."""
        total_spent = sum(log["cost"] for log in self.spending_log)
        total_api_calls = sum(log["api_calls"] for log in self.spending_log)
        
        return {
            "portfolio": self.portfolio,
            "current_balance": self.agent.get_balance(),
            "total_spent": total_spent,
            "total_api_calls": total_api_calls,
            "spending_history": self.spending_log[-5:]  # Last 5 operations
        }
    
    def run_trading_session(self):
        """Run a complete trading session with multiple market analyses."""
        print("🚀 Starting trading bot session...")
        print(f"💰 Initial balance: ${self.agent.get_balance():.2f} USDC")
        
        # Analyze different market segments
        market_segments = [
            ["AAPL", "GOOGL", "MSFT"],  # Tech stocks
            ["BTC", "ETH", "SOL"],      # Cryptocurrencies  
            ["SPY", "QQQ", "IWM"]       # ETFs
        ]
        
        for i, symbols in enumerate(market_segments, 1):
            print(f"\n📊 Market Analysis Session {i}")
            analysis = self.analyze_market(symbols)
            
            # Simulate some trading decisions
            for symbol in symbols:
                if "error" not in analysis[symbol]:
                    self.update_portfolio(symbol, "buy", 10.0)
                    print(f"📈 Simulated buy: 10 shares of {symbol}")
            
            # Small delay between sessions
            time.sleep(1)
        
        # Final summary
        summary = self.get_portfolio_summary()
        print(f"\n📋 Trading Session Summary:")
        print(f"💰 Final balance: ${summary['current_balance']:.2f} USDC")
        print(f"💸 Total spent: ${summary['total_spent']:.4f} USDC")
        print(f"📞 Total API calls: {summary['total_api_calls']}")
        print(f"📊 Portfolio positions: {len(summary['portfolio'])}")
        
        return summary


def main():
    """Demonstrate trading bot with deferred payment batching."""
    
    # Get wallet private key from environment
    private_key = os.getenv("WALLET_PRIVATE_KEY")
    if not private_key:
        print("Please set WALLET_PRIVATE_KEY environment variable")
        return
    
    # Create and run trading bot
    bot = TradingBot(private_key)
    
    try:
        summary = bot.run_trading_session()
        
        print("\n🎯 Key Features Demonstrated:")
        print("✅ Deferred payment batching (multiple API calls)")
        print("✅ Portfolio management and tracking")
        print("✅ Comprehensive spending analytics")
        print("✅ Multi-API integration with automatic payments")
        
    except Exception as e:
        print(f"❌ Trading session error: {e}")


if __name__ == "__main__":
    main()