# Basic Usage Examples

This document provides practical examples of using the x402-Agent Framework for common tasks.

## Prerequisites

Before running these examples, ensure you have:

```bash
pip install x402-agent
export WALLET_PRIVATE_KEY="your_private_key_here"
export OPENAI_API_KEY="your_openai_key_here"
```

## Example 1: Simple Weather Agent

Create an agent that can fetch weather data with automatic payments.

```python
# weather_agent.py
import os
from x402_agent import X402Agent
from langchain_openai import ChatOpenAI

def create_weather_agent():
    """Create a simple weather data agent."""
    
    # Initialize LLM
    llm = ChatOpenAI(
        model="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Create agent
    agent = X402Agent(
        llm=llm,
        wallet_key=os.getenv("WALLET_PRIVATE_KEY"),
        network="base",
        max_spend_per_hour=5.0
    )
    
    # Register weather API tool
    agent.register_tool(
        name="weather",
        endpoint="https://api.weather.com/v1/current",
        description="Get current weather data for any location"
    )
    
    return agent

def main():
    # Create agent
    agent = create_weather_agent()
    
    print(f"🤖 Weather Agent created!")
    print(f"💰 Current balance: ${agent.get_balance():.2f} USDC")
    
    # Get weather for different cities
    cities = ["San Francisco", "New York", "London", "Tokyo"]
    
    for city in cities:
        try:
            result = agent.run(f"What's the current weather in {city}?")
            print(f"\n🌤️  {city}: {result}")
            
        except Exception as e:
            print(f"❌ Error getting weather for {city}: {e}")
    
    # Check final balance
    final_balance = agent.get_balance()
    print(f"\n💰 Final balance: ${final_balance:.2f} USDC")

if __name__ == "__main__":
    main()
```

**Expected Output:**
```
🤖 Weather Agent created!
💰 Current balance: $10.00 USDC

🌤️  San Francisco: The current weather in San Francisco is 68°F with partly cloudy skies...
🌤️  New York: The current weather in New York is 72°F with clear skies...
🌤️  London: The current weather in London is 15°C with light rain...
🌤️  Tokyo: The current weather in Tokyo is 25°C with sunny skies...

💰 Final balance: $9.96 USDC
```

## Example 2: Stock Price Monitor

Create an agent that monitors stock prices and provides analysis.

```python
# stock_monitor.py
import os
import time
from datetime import datetime
from x402_agent import X402Agent
from langchain_openai import ChatOpenAI

class StockMonitor:
    def __init__(self):
        self.agent = self._create_agent()
        self.watchlist = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]
    
    def _create_agent(self):
        """Create stock monitoring agent."""
        llm = ChatOpenAI(
            model="gpt-4",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        agent = X402Agent(
            llm=llm,
            wallet_key=os.getenv("WALLET_PRIVATE_KEY"),
            network="base",
            max_spend_per_hour=20.0
        )
        
        # Register financial data tools
        agent.register_tool(
            name="stock_price",
            endpoint="https://api.stocks.com/v1/price",
            description="Get real-time stock prices"
        )
        
        agent.register_tool(
            name="stock_analysis",
            endpoint="https://api.stocks.com/v1/analysis",
            description="Get technical analysis for stocks"
        )
        
        agent.register_tool(
            name="market_news",
            endpoint="https://api.news.com/v1/financial",
            description="Get latest financial news"
        )
        
        return agent
    
    def check_stock_price(self, symbol):
        """Get current price for a stock symbol."""
        try:
            result = self.agent.run(f"Get the current price for {symbol} stock")
            return result
        except Exception as e:
            print(f"Error getting price for {symbol}: {e}")
            return None
    
    def analyze_stock(self, symbol):
        """Get technical analysis for a stock."""
        try:
            result = self.agent.run(
                f"Provide technical analysis for {symbol} including "
                f"price trends, support/resistance levels, and trading recommendation"
            )
            return result
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            return None
    
    def monitor_watchlist(self):
        """Monitor all stocks in watchlist."""
        print(f"📊 Stock Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        for symbol in self.watchlist:
            print(f"\n📈 {symbol}:")
            
            # Get current price
            price_info = self.check_stock_price(symbol)
            if price_info:
                print(f"   Price: {price_info}")
            
            # Get analysis (for first 3 stocks to manage costs)
            if symbol in self.watchlist[:3]:
                analysis = self.analyze_stock(symbol)
                if analysis:
                    print(f"   Analysis: {analysis}")
        
        # Show spending summary
        balance = self.agent.get_balance()
        print(f"\n💰 Remaining balance: ${balance:.2f} USDC")
    
    def run_continuous_monitoring(self, interval_minutes=30):
        """Run continuous monitoring with specified interval."""
        print(f"🚀 Starting continuous stock monitoring (every {interval_minutes} minutes)")
        
        try:
            while True:
                self.monitor_watchlist()
                print(f"\n⏰ Next update in {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")

def main():
    monitor = StockMonitor()
    
    # Single monitoring run
    monitor.monitor_watchlist()
    
    # Uncomment for continuous monitoring
    # monitor.run_continuous_monitoring(interval_minutes=15)

if __name__ == "__main__":
    main()
```

## Example 3: Research Assistant

Create an agent that can research topics using multiple data sources.

```python
# research_assistant.py
import os
from x402_agent import X402Agent
from langchain_openai import ChatOpenAI

class ResearchAssistant:
    def __init__(self):
        self.agent = self._create_agent()
    
    def _create_agent(self):
        """Create research assistant agent."""
        llm = ChatOpenAI(
            model="gpt-4",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        agent = X402Agent(
            llm=llm,
            wallet_key=os.getenv("WALLET_PRIVATE_KEY"),
            network="base",
            max_spend_per_hour=15.0
        )
        
        # Register research tools
        research_tools = [
            ("arxiv", "https://api.arxiv.org/search", "Academic papers and research"),
            ("wikipedia", "https://api.wikipedia.org/search", "General knowledge and facts"),
            ("news", "https://api.news.com/search", "Current news and events"),
            ("patents", "https://api.patents.com/search", "Patent database"),
            ("web_search", "https://api.search.com/web", "General web search")
        ]
        
        for name, endpoint, description in research_tools:
            agent.register_tool(name, endpoint, description)
        
        return agent
    
    def research_topic(self, topic, depth="comprehensive"):
        """Research a topic with specified depth."""
        
        if depth == "quick":
            prompt = f"""
            Provide a quick overview of {topic}:
            1. Brief definition and key concepts
            2. Current status or recent developments
            3. Main applications or implications
            
            Use web search and news sources for current information.
            """
        
        elif depth == "comprehensive":
            prompt = f"""
            Conduct comprehensive research on {topic}:
            1. Search academic papers for theoretical background
            2. Check recent news for current developments
            3. Look up patents for technological innovations
            4. Gather general information from reliable sources
            5. Synthesize findings into a detailed report
            
            Provide sources and citations for all information.
            """
        
        elif depth == "academic":
            prompt = f"""
            Conduct academic research on {topic}:
            1. Search ArXiv for recent research papers
            2. Find key researchers and institutions
            3. Identify research trends and methodologies
            4. Summarize key findings and future directions
            
            Focus on peer-reviewed sources and academic credibility.
            """
        
        try:
            print(f"🔍 Researching: {topic} ({depth} analysis)")
            result = self.agent.run(prompt)
            return result
            
        except Exception as e:
            print(f"❌ Research failed: {e}")
            return None
    
    def compare_topics(self, topic1, topic2):
        """Compare two topics side by side."""
        prompt = f"""
        Compare and contrast {topic1} and {topic2}:
        
        1. Research both topics using available sources
        2. Identify similarities and differences
        3. Analyze advantages and disadvantages of each
        4. Provide use cases where one might be preferred over the other
        5. Include recent developments for both
        
        Present findings in a structured comparison format.
        """
        
        try:
            print(f"⚖️  Comparing: {topic1} vs {topic2}")
            result = self.agent.run(prompt)
            return result
            
        except Exception as e:
            print(f"❌ Comparison failed: {e}")
            return None
    
    def trend_analysis(self, topic, timeframe="1 year"):
        """Analyze trends for a topic over specified timeframe."""
        prompt = f"""
        Analyze trends for {topic} over the past {timeframe}:
        
        1. Search for news articles and developments
        2. Look for research papers and citations
        3. Check patent filings and innovations
        4. Identify key milestones and events
        5. Predict future trends based on current data
        
        Focus on quantifiable metrics and timeline of developments.
        """
        
        try:
            print(f"📈 Analyzing trends: {topic} ({timeframe})")
            result = self.agent.run(prompt)
            return result
            
        except Exception as e:
            print(f"❌ Trend analysis failed: {e}")
            return None

def main():
    assistant = ResearchAssistant()
    
    print("🤖 Research Assistant Ready!")
    print(f"💰 Initial balance: ${assistant.agent.get_balance():.2f} USDC")
    
    # Example research tasks
    research_tasks = [
        ("Quantum Computing", "comprehensive"),
        ("Artificial Intelligence in Healthcare", "academic"),
        ("Blockchain vs Traditional Databases", "comparison"),
        ("Electric Vehicle Market", "trends")
    ]
    
    for i, task in enumerate(research_tasks, 1):
        print(f"\n{'='*60}")
        print(f"Research Task {i}")
        print('='*60)
        
        if len(task) == 2:
            topic, depth = task
            result = assistant.research_topic(topic, depth)
        elif "vs" in task[0]:
            topics = task[0].split(" vs ")
            result = assistant.compare_topics(topics[0].strip(), topics[1].strip())
        elif "trends" in task[1].lower():
            result = assistant.trend_analysis(task[0])
        
        if result:
            print(f"\n📋 Research Results:\n{result}")
        
        # Show current balance
        balance = assistant.agent.get_balance()
        print(f"\n💰 Current balance: ${balance:.2f} USDC")
    
    print(f"\n🎉 Research session completed!")

if __name__ == "__main__":
    main()
```

## Example 4: Content Creator Agent

Create an agent that generates and optimizes content.

```python
# content_creator.py
import os
from x402_agent import X402Agent
from langchain_openai import ChatOpenAI

class ContentCreator:
    def __init__(self):
        self.agent = self._create_agent()
    
    def _create_agent(self):
        """Create content creation agent."""
        llm = ChatOpenAI(
            model="gpt-4",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        agent = X402Agent(
            llm=llm,
            wallet_key=os.getenv("WALLET_PRIVATE_KEY"),
            network="base",
            max_spend_per_hour=12.0
        )
        
        # Register content tools
        content_tools = [
            ("grammar_check", "https://api.grammar.com/check", "Grammar and spell checking"),
            ("seo_optimize", "https://api.seo.com/optimize", "SEO optimization"),
            ("readability", "https://api.readability.com/analyze", "Readability analysis"),
            ("plagiarism", "https://api.plagiarism.com/check", "Plagiarism detection"),
            ("keyword_research", "https://api.keywords.com/research", "Keyword research"),
            ("image_gen", "https://api.images.com/generate", "Image generation")
        ]
        
        for name, endpoint, description in content_tools:
            agent.register_tool(name, endpoint, description)
        
        return agent
    
    def create_blog_post(self, topic, target_audience="general", word_count=800):
        """Create a complete blog post with SEO optimization."""
        
        prompt = f"""
        Create a comprehensive blog post about {topic}:
        
        Target audience: {target_audience}
        Target word count: {word_count} words
        
        Process:
        1. Research keywords related to {topic}
        2. Create an engaging title and outline
        3. Write the full blog post with proper structure
        4. Check grammar and readability
        5. Optimize for SEO
        6. Suggest relevant images
        
        Ensure the content is original, engaging, and optimized for search engines.
        """
        
        try:
            print(f"✍️  Creating blog post: {topic}")
            result = self.agent.run(prompt)
            return result
            
        except Exception as e:
            print(f"❌ Blog post creation failed: {e}")
            return None
    
    def optimize_existing_content(self, content):
        """Optimize existing content for better performance."""
        
        prompt = f"""
        Optimize the following content:
        
        {content}
        
        Optimization process:
        1. Check grammar and spelling
        2. Analyze readability and suggest improvements
        3. Optimize for SEO (keywords, meta descriptions, headers)
        4. Check for plagiarism
        5. Suggest structural improvements
        6. Recommend images or media
        
        Provide the optimized version with explanations for changes.
        """
        
        try:
            print("🔧 Optimizing content...")
            result = self.agent.run(prompt)
            return result
            
        except Exception as e:
            print(f"❌ Content optimization failed: {e}")
            return None
    
    def create_social_media_campaign(self, product, platforms=["twitter", "linkedin", "instagram"]):
        """Create social media content for multiple platforms."""
        
        prompt = f"""
        Create a social media campaign for {product}:
        
        Platforms: {', '.join(platforms)}
        
        For each platform, create:
        1. 3-5 posts with appropriate tone and format
        2. Relevant hashtags and keywords
        3. Engagement strategies
        4. Visual content suggestions
        5. Posting schedule recommendations
        
        Ensure content is platform-optimized and engaging.
        """
        
        try:
            print(f"📱 Creating social media campaign: {product}")
            result = self.agent.run(prompt)
            return result
            
        except Exception as e:
            print(f"❌ Social media campaign creation failed: {e}")
            return None
    
    def generate_product_descriptions(self, products):
        """Generate optimized product descriptions."""
        
        product_list = '\n'.join([f"- {product}" for product in products])
        
        prompt = f"""
        Create compelling product descriptions for:
        
        {product_list}
        
        For each product:
        1. Research relevant keywords
        2. Write engaging, benefit-focused description
        3. Include technical specifications if relevant
        4. Optimize for e-commerce SEO
        5. Check readability and grammar
        6. Suggest product images
        
        Make descriptions persuasive and search-engine friendly.
        """
        
        try:
            print(f"🛍️  Generating product descriptions for {len(products)} products")
            result = self.agent.run(prompt)
            return result
            
        except Exception as e:
            print(f"❌ Product description generation failed: {e}")
            return None

def main():
    creator = ContentCreator()
    
    print("🤖 Content Creator Agent Ready!")
    print(f"💰 Initial balance: ${creator.agent.get_balance():.2f} USDC")
    
    # Example 1: Create blog post
    print("\n" + "="*60)
    print("Creating Blog Post")
    print("="*60)
    
    blog_result = creator.create_blog_post(
        topic="The Future of Artificial Intelligence in Business",
        target_audience="business professionals",
        word_count=1000
    )
    
    if blog_result:
        print(f"📝 Blog Post Created:\n{blog_result[:500]}...")
    
    # Example 2: Social media campaign
    print("\n" + "="*60)
    print("Creating Social Media Campaign")
    print("="*60)
    
    social_result = creator.create_social_media_campaign(
        product="AI-Powered Project Management Tool",
        platforms=["twitter", "linkedin", "instagram"]
    )
    
    if social_result:
        print(f"📱 Social Media Campaign:\n{social_result[:500]}...")
    
    # Example 3: Product descriptions
    print("\n" + "="*60)
    print("Generating Product Descriptions")
    print("="*60)
    
    products = [
        "Wireless Bluetooth Headphones with Noise Cancellation",
        "Smart Home Security Camera with AI Detection",
        "Ergonomic Standing Desk Converter"
    ]
    
    product_result = creator.generate_product_descriptions(products)
    
    if product_result:
        print(f"🛍️  Product Descriptions:\n{product_result[:500]}...")
    
    # Show final balance and summary
    final_balance = creator.agent.get_balance()
    print(f"\n💰 Final balance: ${final_balance:.2f} USDC")
    print("🎉 Content creation session completed!")

if __name__ == "__main__":
    main()
```

## Example 5: Data Analysis Agent

Create an agent that performs data analysis and generates insights.

```python
# data_analyst.py
import os
from x402_agent import X402Agent
from langchain_openai import ChatOpenAI

class DataAnalyst:
    def __init__(self):
        self.agent = self._create_agent()
    
    def _create_agent(self):
        """Create data analysis agent."""
        llm = ChatOpenAI(
            model="gpt-4",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        agent = X402Agent(
            llm=llm,
            wallet_key=os.getenv("WALLET_PRIVATE_KEY"),
            network="base",
            max_spend_per_hour=25.0
        )
        
        # Register data analysis tools
        analysis_tools = [
            ("data_processing", "https://api.dataproc.com/process", "Data cleaning and processing"),
            ("statistics", "https://api.stats.com/analyze", "Statistical analysis"),
            ("visualization", "https://api.viz.com/create", "Data visualization"),
            ("ml_models", "https://api.ml.com/predict", "Machine learning models"),
            ("database_query", "https://api.db.com/query", "Database queries"),
            ("report_gen", "https://api.reports.com/generate", "Report generation")
        ]
        
        for name, endpoint, description in analysis_tools:
            agent.register_tool(name, endpoint, description)
        
        return agent
    
    def analyze_sales_data(self, data_source):
        """Analyze sales data and generate insights."""
        
        prompt = f"""
        Analyze sales data from {data_source}:
        
        Analysis tasks:
        1. Query and process the sales data
        2. Calculate key metrics (revenue, growth, trends)
        3. Perform statistical analysis
        4. Identify patterns and anomalies
        5. Create visualizations (charts, graphs)
        6. Generate actionable insights and recommendations
        7. Create executive summary report
        
        Focus on revenue trends, customer segments, and growth opportunities.
        """
        
        try:
            print(f"📊 Analyzing sales data from: {data_source}")
            result = self.agent.run(prompt)
            return result
            
        except Exception as e:
            print(f"❌ Sales analysis failed: {e}")
            return None
    
    def customer_segmentation(self, customer_data):
        """Perform customer segmentation analysis."""
        
        prompt = f"""
        Perform customer segmentation analysis on {customer_data}:
        
        Segmentation process:
        1. Process and clean customer data
        2. Apply statistical clustering methods
        3. Use ML models for advanced segmentation
        4. Analyze segment characteristics
        5. Create segment profiles and personas
        6. Visualize segments with charts
        7. Recommend targeted strategies for each segment
        
        Provide detailed segment analysis with actionable recommendations.
        """
        
        try:
            print(f"👥 Performing customer segmentation: {customer_data}")
            result = self.agent.run(prompt)
            return result
            
        except Exception as e:
            print(f"❌ Customer segmentation failed: {e}")
            return None
    
    def predictive_analysis(self, historical_data, prediction_target):
        """Perform predictive analysis using ML models."""
        
        prompt = f"""
        Perform predictive analysis for {prediction_target} using {historical_data}:
        
        Prediction process:
        1. Process and prepare historical data
        2. Perform exploratory data analysis
        3. Select appropriate ML models
        4. Train and validate models
        5. Generate predictions with confidence intervals
        6. Create trend visualizations
        7. Provide interpretation and business implications
        
        Include model accuracy metrics and uncertainty analysis.
        """
        
        try:
            print(f"🔮 Performing predictive analysis: {prediction_target}")
            result = self.agent.run(prompt)
            return result
            
        except Exception as e:
            print(f"❌ Predictive analysis failed: {e}")
            return None
    
    def market_research_analysis(self, market_topic):
        """Analyze market research data and trends."""
        
        prompt = f"""
        Conduct comprehensive market analysis for {market_topic}:
        
        Research and analysis:
        1. Gather market data from multiple sources
        2. Analyze market size, growth, and trends
        3. Identify key players and competitors
        4. Perform SWOT analysis
        5. Calculate market metrics and KPIs
        6. Create market visualization dashboards
        7. Generate strategic recommendations
        
        Provide data-driven insights for business decision making.
        """
        
        try:
            print(f"🏪 Analyzing market: {market_topic}")
            result = self.agent.run(prompt)
            return result
            
        except Exception as e:
            print(f"❌ Market analysis failed: {e}")
            return None

def main():
    analyst = DataAnalyst()
    
    print("🤖 Data Analyst Agent Ready!")
    print(f"💰 Initial balance: ${analyst.agent.get_balance():.2f} USDC")
    
    # Example analyses
    analyses = [
        ("sales_data", "Q4 2024 E-commerce Sales Database"),
        ("customer_segmentation", "Customer Transaction History"),
        ("predictive", "Revenue Forecasting for 2025"),
        ("market", "Electric Vehicle Market Analysis")
    ]
    
    for i, (analysis_type, data_source) in enumerate(analyses, 1):
        print(f"\n{'='*60}")
        print(f"Analysis {i}: {analysis_type.replace('_', ' ').title()}")
        print('='*60)
        
        if analysis_type == "sales_data":
            result = analyst.analyze_sales_data(data_source)
        elif analysis_type == "customer_segmentation":
            result = analyst.customer_segmentation(data_source)
        elif analysis_type == "predictive":
            result = analyst.predictive_analysis("Historical Revenue Data", "2025 Revenue")
        elif analysis_type == "market":
            result = analyst.market_research_analysis("Electric Vehicle Market")
        
        if result:
            print(f"📈 Analysis Results:\n{result[:500]}...")
        
        # Show current balance
        balance = analyst.agent.get_balance()
        print(f"\n💰 Current balance: ${balance:.2f} USDC")
    
    print(f"\n🎉 Data analysis session completed!")

if __name__ == "__main__":
    main()
```

## Running the Examples

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv x402_examples
source x402_examples/bin/activate  # On Windows: x402_examples\Scripts\activate

# Install dependencies
pip install x402-agent python-dotenv

# Create .env file
cat > .env << EOF
WALLET_PRIVATE_KEY=your_private_key_here
OPENAI_API_KEY=your_openai_key_here
EOF
```

### 2. Run Individual Examples

```bash
# Weather agent
python weather_agent.py

# Stock monitor
python stock_monitor.py

# Research assistant
python research_assistant.py

# Content creator
python content_creator.py

# Data analyst
python data_analyst.py
```

### 3. Customize for Your Needs

Each example can be customized by:

- **Changing API endpoints**: Replace mock URLs with real API endpoints
- **Adjusting spending limits**: Modify `max_spend_per_hour` parameter
- **Adding new tools**: Register additional APIs using `agent.register_tool()`
- **Modifying prompts**: Customize the task descriptions for different outputs

## Best Practices

1. **Start Small**: Begin with simple tasks and gradually increase complexity
2. **Monitor Spending**: Always check balance before and after operations
3. **Handle Errors**: Implement proper error handling for production use
4. **Use Real APIs**: Replace example endpoints with actual API services
5. **Secure Keys**: Never hardcode private keys or API keys in source code

## Next Steps

- Explore [Multi-Agent Swarms](../guides/multi-agent-swarms.md) for collaborative agents
- Learn about [Payment Optimization](../guides/payment-optimization.md) for cost efficiency
- Check out [Production Deployment](../guides/production-deployment.md) for scaling

These examples provide a solid foundation for building your own x402-Agent applications. Experiment with different combinations of tools and tasks to create powerful AI agents that can autonomously handle complex workflows! 🚀