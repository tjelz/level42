# Production Deployment Guide

This guide covers deploying x402-Agent Framework applications in production environments with security, scalability, and reliability best practices.

## Overview

Production deployment of x402-Agent applications requires careful consideration of:

- **Security**: Private key management, network security, access controls
- **Scalability**: Load balancing, auto-scaling, resource management
- **Reliability**: Error handling, monitoring, backup strategies
- **Cost Management**: Spending controls, budget alerts, optimization
- **Compliance**: Audit trails, regulatory requirements, data protection

## Architecture Patterns

### 1. Single Agent Deployment

Simple deployment for individual agents with basic requirements.

```python
# production_agent.py
import os
import logging
from x402_agent import X402Agent
from x402_agent.monitoring import AgentMonitor
from langchain_openai import ChatOpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/x402-agent/agent.log'),
        logging.StreamHandler()
    ]
)

class ProductionAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize with environment variables
        self.agent = X402Agent(
            llm=ChatOpenAI(
                model=os.getenv("LLM_MODEL", "gpt-4"),
                api_key=os.getenv("OPENAI_API_KEY")
            ),
            wallet_key=os.getenv("WALLET_PRIVATE_KEY"),
            network=os.getenv("NETWORK", "base"),
            max_spend_per_hour=float(os.getenv("MAX_SPEND_PER_HOUR", "10.0"))
        )
        
        # Set up monitoring
        self.monitor = AgentMonitor(
            agent_id=os.getenv("AGENT_ID", "prod_agent"),
            storage_backend="postgresql",
            config={
                "connection_string": os.getenv("DATABASE_URL"),
                "retention_days": 90
            }
        )
        
        # Configure alerts
        self._setup_alerts()
        
        # Register production tools
        self._register_tools()
    
    def _setup_alerts(self):
        """Configure production alerts."""
        # Spending alerts
        self.monitor.set_alert_threshold("hourly_spending", 8.0)
        self.monitor.set_alert_threshold("daily_spending", 50.0)
        
        # Performance alerts
        self.monitor.set_alert_threshold("error_rate", 0.05)
        self.monitor.set_alert_threshold("response_time", 10.0)
        
        # Add alert handlers
        self.monitor.add_alert_callback(self._handle_alert)
    
    def _handle_alert(self, alert):
        """Handle production alerts."""
        self.logger.warning(f"Production alert: {alert}")
        
        # Send to monitoring system (e.g., PagerDuty, Slack)
        # self.send_to_monitoring_system(alert)
    
    def _register_tools(self):
        """Register production API tools."""
        tools = [
            ("market_data", os.getenv("MARKET_API_URL"), "Market data API"),
            ("weather", os.getenv("WEATHER_API_URL"), "Weather data API"),
            ("news", os.getenv("NEWS_API_URL"), "News API")
        ]
        
        for name, url, description in tools:
            if url:
                self.agent.register_tool(name, url, description)
    
    def run_task(self, task):
        """Execute task with production error handling."""
        try:
            self.logger.info(f"Starting task: {task}")
            result = self.agent.run(task)
            self.logger.info(f"Task completed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Task failed: {e}")
            raise
    
    def health_check(self):
        """Production health check endpoint."""
        try:
            balance = self.agent.get_balance()
            return {
                "status": "healthy",
                "balance": balance,
                "agent_id": self.agent.agent_id,
                "network": self.agent.network
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

if __name__ == "__main__":
    agent = ProductionAgent()
    
    # Example usage
    result = agent.run_task("Get current market data")
    print(result)
```

### 2. Multi-Agent Swarm Deployment

Scalable deployment for collaborative agent systems.

```python
# production_swarm.py
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from x402_agent import X402Agent
from x402_agent.swarm import AgentSwarm
from x402_agent.monitoring import AgentMonitor

class ProductionSwarm:
    def __init__(self):
        self.swarm = AgentSwarm(
            shared_wallet=True,
            shared_wallet_key=os.getenv("SHARED_WALLET_KEY"),
            cost_splitting="proportional"
        )
        
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.monitor = AgentMonitor("production_swarm")
        
        # Initialize agents
        self._create_agents()
        
        # Set up load balancing
        self._setup_load_balancing()
    
    def _create_agents(self):
        """Create specialized production agents."""
        agent_configs = [
            ("data_collector", "Data collection specialist", 5),
            ("analyzer", "Data analysis specialist", 3),
            ("reporter", "Report generation specialist", 2)
        ]
        
        for agent_type, description, count in agent_configs:
            for i in range(count):
                agent_id = f"{agent_type}_{i}"
                agent = self._create_agent(agent_id, agent_type)
                self.swarm.add_agent(agent, agent_id, description)
    
    def _create_agent(self, agent_id, agent_type):
        """Create individual agent with type-specific configuration."""
        # Agent-specific configuration
        config = self._get_agent_config(agent_type)
        
        agent = X402Agent(
            llm=config["llm"],
            wallet_key=config["wallet_key"],
            network=config["network"],
            max_spend_per_hour=config["max_spend"]
        )
        
        # Register type-specific tools
        for tool_name, tool_url, tool_desc in config["tools"]:
            agent.register_tool(tool_name, tool_url, tool_desc)
        
        return agent
    
    def _get_agent_config(self, agent_type):
        """Get configuration for specific agent type."""
        base_config = {
            "llm": ChatOpenAI(model="gpt-4"),
            "network": "base",
            "max_spend": 10.0
        }
        
        if agent_type == "data_collector":
            base_config.update({
                "wallet_key": os.getenv("DATA_COLLECTOR_WALLET_KEY"),
                "max_spend": 15.0,
                "tools": [
                    ("web_search", os.getenv("SEARCH_API_URL"), "Web search"),
                    ("database", os.getenv("DATABASE_API_URL"), "Database access")
                ]
            })
        elif agent_type == "analyzer":
            base_config.update({
                "wallet_key": os.getenv("ANALYZER_WALLET_KEY"),
                "max_spend": 20.0,
                "tools": [
                    ("analytics", os.getenv("ANALYTICS_API_URL"), "Analytics engine"),
                    ("ml_models", os.getenv("ML_API_URL"), "ML models")
                ]
            })
        elif agent_type == "reporter":
            base_config.update({
                "wallet_key": os.getenv("REPORTER_WALLET_KEY"),
                "max_spend": 8.0,
                "tools": [
                    ("formatting", os.getenv("FORMAT_API_URL"), "Document formatting"),
                    ("visualization", os.getenv("VIZ_API_URL"), "Data visualization")
                ]
            })
        
        return base_config
    
    async def collaborate_async(self, task, **kwargs):
        """Asynchronous collaboration for better performance."""
        loop = asyncio.get_event_loop()
        
        # Run collaboration in thread pool
        result = await loop.run_in_executor(
            self.executor,
            self.swarm.collaborate,
            task,
            **kwargs
        )
        
        return result
    
    def scale_agents(self, agent_type, target_count):
        """Dynamically scale agent count based on load."""
        current_agents = [
            agent_id for agent_id in self.swarm.agents
            if agent_id.startswith(agent_type)
        ]
        
        current_count = len(current_agents)
        
        if target_count > current_count:
            # Scale up
            for i in range(current_count, target_count):
                agent_id = f"{agent_type}_{i}"
                agent = self._create_agent(agent_id, agent_type)
                self.swarm.add_agent(agent, agent_id)
        
        elif target_count < current_count:
            # Scale down
            for i in range(target_count, current_count):
                agent_id = f"{agent_type}_{i}"
                self.swarm.remove_agent(agent_id)
```

### 3. Microservices Architecture

Enterprise-grade deployment with microservices pattern.

```python
# agent_service.py
from flask import Flask, request, jsonify
from x402_agent import X402Agent
import redis
import json

app = Flask(__name__)
redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"))

class AgentService:
    def __init__(self):
        self.agents = {}
        self._load_agents()
    
    def _load_agents(self):
        """Load agents from configuration."""
        # Load from database or configuration service
        pass
    
    def get_agent(self, agent_id):
        """Get or create agent instance."""
        if agent_id not in self.agents:
            # Create agent from configuration
            config = self._get_agent_config(agent_id)
            self.agents[agent_id] = X402Agent(**config)
        
        return self.agents[agent_id]

service = AgentService()

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})

@app.route('/agents/<agent_id>/execute', methods=['POST'])
def execute_task(agent_id):
    """Execute task on specific agent."""
    try:
        data = request.get_json()
        task = data.get('task')
        
        if not task:
            return jsonify({"error": "Task is required"}), 400
        
        agent = service.get_agent(agent_id)
        result = agent.run(task)
        
        return jsonify({
            "success": True,
            "result": result,
            "agent_id": agent_id
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/agents/<agent_id>/balance')
def get_balance(agent_id):
    """Get agent balance."""
    try:
        agent = service.get_agent(agent_id)
        balance = agent.get_balance()
        
        return jsonify({
            "agent_id": agent_id,
            "balance": balance
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## Security Best Practices

### 1. Private Key Management

```python
# secure_key_manager.py
import os
import boto3
from cryptography.fernet import Fernet
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

class SecureKeyManager:
    """Secure private key management for production."""
    
    def __init__(self, provider="aws"):
        self.provider = provider
        self._setup_provider()
    
    def _setup_provider(self):
        """Initialize key management provider."""
        if self.provider == "aws":
            self.client = boto3.client('secretsmanager')
        elif self.provider == "azure":
            credential = DefaultAzureCredential()
            vault_url = os.getenv("AZURE_VAULT_URL")
            self.client = SecretClient(vault_url=vault_url, credential=credential)
        elif self.provider == "local":
            # For development only
            self.encryption_key = os.getenv("ENCRYPTION_KEY").encode()
            self.cipher = Fernet(self.encryption_key)
    
    def get_private_key(self, key_name):
        """Retrieve private key securely."""
        if self.provider == "aws":
            response = self.client.get_secret_value(SecretId=key_name)
            return response['SecretString']
        
        elif self.provider == "azure":
            secret = self.client.get_secret(key_name)
            return secret.value
        
        elif self.provider == "local":
            encrypted_key = os.getenv(f"ENCRYPTED_{key_name}")
            return self.cipher.decrypt(encrypted_key.encode()).decode()
    
    def rotate_key(self, key_name, new_key):
        """Rotate private key securely."""
        if self.provider == "aws":
            self.client.update_secret(
                SecretId=key_name,
                SecretString=new_key
            )
        elif self.provider == "azure":
            self.client.set_secret(key_name, new_key)

# Usage in production
key_manager = SecureKeyManager("aws")
private_key = key_manager.get_private_key("agent_wallet_key")

agent = X402Agent(
    llm=llm,
    wallet_key=private_key,
    network="base"
)
```

### 2. Network Security

```python
# network_security.py
import ssl
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class SecureHTTPAdapter(HTTPAdapter):
    """Secure HTTP adapter with SSL verification and retries."""
    
    def __init__(self, *args, **kwargs):
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = True
        self.ssl_context.verify_mode = ssl.CERT_REQUIRED
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        super().__init__(max_retries=retry_strategy, *args, **kwargs)
    
    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super().init_poolmanager(*args, **kwargs)

# Configure secure session for agents
def create_secure_session():
    session = requests.Session()
    session.mount("https://", SecureHTTPAdapter())
    
    # Add security headers
    session.headers.update({
        'User-Agent': 'x402-agent/1.0',
        'X-Requested-With': 'x402-agent'
    })
    
    return session

# Use in agent configuration
secure_session = create_secure_session()
```

### 3. Access Control

```python
# access_control.py
import jwt
import functools
from flask import request, jsonify

class AccessControl:
    """JWT-based access control for agent APIs."""
    
    def __init__(self, secret_key):
        self.secret_key = secret_key
    
    def require_auth(self, f):
        """Decorator to require authentication."""
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            
            if not token:
                return jsonify({'error': 'No token provided'}), 401
            
            try:
                # Remove 'Bearer ' prefix
                token = token.replace('Bearer ', '')
                payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
                request.user = payload
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Invalid token'}), 401
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def require_role(self, required_role):
        """Decorator to require specific role."""
        def decorator(f):
            @functools.wraps(f)
            def decorated_function(*args, **kwargs):
                user_role = request.user.get('role')
                
                if user_role != required_role:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                return f(*args, **kwargs)
            
            return decorated_function
        
        return decorator

# Usage
auth = AccessControl(os.getenv('JWT_SECRET'))

@app.route('/admin/agents', methods=['POST'])
@auth.require_auth
@auth.require_role('admin')
def create_agent():
    # Only admins can create agents
    pass
```

## Monitoring and Observability

### 1. Comprehensive Monitoring Stack

```python
# monitoring_stack.py
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge
import structlog
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Prometheus metrics
TASK_COUNTER = Counter('agent_tasks_total', 'Total agent tasks', ['agent_id', 'status'])
TASK_DURATION = Histogram('agent_task_duration_seconds', 'Task duration', ['agent_id'])
WALLET_BALANCE = Gauge('agent_wallet_balance_usdc', 'Wallet balance', ['agent_id'])
API_CALLS = Counter('agent_api_calls_total', 'API calls', ['agent_id', 'tool_name', 'status'])

# Structured logging
logger = structlog.get_logger()

# Distributed tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    agent_host_name=os.getenv("JAEGER_HOST", "localhost"),
    agent_port=int(os.getenv("JAEGER_PORT", "6831")),
)

span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

class MonitoredAgent(X402Agent):
    """Agent with comprehensive monitoring."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent_id = kwargs.get('agent_id', 'unknown')
    
    def run(self, task):
        """Run task with monitoring."""
        with tracer.start_as_current_span("agent_task") as span:
            span.set_attribute("agent.id", self.agent_id)
            span.set_attribute("task.description", task)
            
            start_time = time.time()
            
            try:
                logger.info("Task started", agent_id=self.agent_id, task=task)
                
                result = super().run(task)
                
                # Record success metrics
                TASK_COUNTER.labels(agent_id=self.agent_id, status='success').inc()
                duration = time.time() - start_time
                TASK_DURATION.labels(agent_id=self.agent_id).observe(duration)
                
                # Update balance metric
                balance = self.get_balance()
                WALLET_BALANCE.labels(agent_id=self.agent_id).set(balance)
                
                logger.info("Task completed", 
                           agent_id=self.agent_id, 
                           duration=duration,
                           balance=balance)
                
                span.set_attribute("task.status", "success")
                span.set_attribute("task.duration", duration)
                
                return result
                
            except Exception as e:
                # Record failure metrics
                TASK_COUNTER.labels(agent_id=self.agent_id, status='failure').inc()
                
                logger.error("Task failed", 
                           agent_id=self.agent_id, 
                           error=str(e))
                
                span.set_attribute("task.status", "failure")
                span.set_attribute("error.message", str(e))
                
                raise
```

### 2. Health Checks and Readiness Probes

```python
# health_checks.py
from flask import Flask, jsonify
import time
import threading

app = Flask(__name__)

class HealthChecker:
    """Comprehensive health checking for agents."""
    
    def __init__(self, agent):
        self.agent = agent
        self.last_check = 0
        self.health_status = {"status": "unknown"}
        self.check_interval = 30  # seconds
        
        # Start background health checking
        self.start_background_checks()
    
    def start_background_checks(self):
        """Start background health checking thread."""
        def check_loop():
            while True:
                self.perform_health_check()
                time.sleep(self.check_interval)
        
        thread = threading.Thread(target=check_loop, daemon=True)
        thread.start()
    
    def perform_health_check(self):
        """Perform comprehensive health check."""
        try:
            checks = {
                "wallet_connection": self._check_wallet_connection(),
                "balance_sufficient": self._check_balance(),
                "network_connectivity": self._check_network(),
                "tool_availability": self._check_tools()
            }
            
            all_healthy = all(checks.values())
            
            self.health_status = {
                "status": "healthy" if all_healthy else "unhealthy",
                "timestamp": time.time(),
                "checks": checks
            }
            
        except Exception as e:
            self.health_status = {
                "status": "unhealthy",
                "timestamp": time.time(),
                "error": str(e)
            }
    
    def _check_wallet_connection(self):
        """Check wallet connectivity."""
        try:
            self.agent.wallet_manager.get_balance()
            return True
        except:
            return False
    
    def _check_balance(self):
        """Check if balance is sufficient."""
        try:
            balance = self.agent.get_balance()
            return balance > 1.0  # Minimum threshold
        except:
            return False
    
    def _check_network(self):
        """Check network connectivity."""
        try:
            import requests
            response = requests.get("https://api.base.org", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _check_tools(self):
        """Check tool availability."""
        try:
            # Test a sample of registered tools
            for tool_name in list(self.agent.tools.keys())[:3]:
                tool = self.agent.tools[tool_name]
                # Perform basic connectivity check
                import requests
                response = requests.head(tool.endpoint, timeout=5)
                if response.status_code >= 400:
                    return False
            return True
        except:
            return False

# Health check endpoints
health_checker = None

@app.route('/health')
def health():
    """Kubernetes liveness probe."""
    if health_checker and health_checker.health_status["status"] == "healthy":
        return jsonify(health_checker.health_status), 200
    else:
        return jsonify({"status": "unhealthy"}), 503

@app.route('/ready')
def ready():
    """Kubernetes readiness probe."""
    if health_checker:
        status = health_checker.health_status
        if status["status"] == "healthy":
            return jsonify({"status": "ready"}), 200
    
    return jsonify({"status": "not ready"}), 503

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint."""
    return prometheus_client.generate_latest()
```

## Deployment Configurations

### 1. Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash agent
RUN chown -R agent:agent /app
USER agent

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run application
CMD ["python", "production_agent.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  agent:
    build: .
    ports:
      - "5000:5000"
    environment:
      - WALLET_PRIVATE_KEY=${WALLET_PRIVATE_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=x402_agent
      - POSTGRES_USER=agent
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped
    
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped

volumes:
  postgres_data:
  grafana_data:
```

### 2. Kubernetes Configuration

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: x402-agent
  labels:
    app: x402-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: x402-agent
  template:
    metadata:
      labels:
        app: x402-agent
    spec:
      containers:
      - name: agent
        image: x402-agent:latest
        ports:
        - containerPort: 5000
        env:
        - name: WALLET_PRIVATE_KEY
          valueFrom:
            secretKeyRef:
              name: agent-secrets
              key: wallet-private-key
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: agent-secrets
              key: openai-api-key
        - name: DATABASE_URL
          valueFrom:
            configMapKeyRef:
              name: agent-config
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: x402-agent-service
spec:
  selector:
    app: x402-agent
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: agent-config
data:
  database-url: "postgresql://user:pass@postgres:5432/x402_agent"
  redis-url: "redis://redis:6379"
  network: "base"
  max-spend-per-hour: "10.0"
---
apiVersion: v1
kind: Secret
metadata:
  name: agent-secrets
type: Opaque
data:
  wallet-private-key: <base64-encoded-key>
  openai-api-key: <base64-encoded-key>
```

### 3. Terraform Infrastructure

```hcl
# main.tf
provider "aws" {
  region = var.aws_region
}

# VPC and networking
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "x402-agent-vpc"
  }
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "x402-agent-private-${count.index + 1}"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "x402-agent-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "agent" {
  family                   = "x402-agent"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "x402-agent"
      image = "${aws_ecr_repository.agent.repository_url}:latest"
      
      portMappings = [
        {
          containerPort = 5000
          protocol      = "tcp"
        }
      ]
      
      environment = [
        {
          name  = "NETWORK"
          value = "base"
        }
      ]
      
      secrets = [
        {
          name      = "WALLET_PRIVATE_KEY"
          valueFrom = aws_secretsmanager_secret.wallet_key.arn
        },
        {
          name      = "OPENAI_API_KEY"
          valueFrom = aws_secretsmanager_secret.openai_key.arn
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.agent.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
      
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:5000/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])
}

# ECS Service
resource "aws_ecs_service" "agent" {
  name            = "x402-agent-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.agent.arn
  desired_count   = 3
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.agent.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.agent.arn
    container_name   = "x402-agent"
    container_port   = 5000
  }

  depends_on = [aws_lb_listener.agent]
}

# Application Load Balancer
resource "aws_lb" "agent" {
  name               = "x402-agent-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = false
}

# RDS Database
resource "aws_db_instance" "postgres" {
  identifier     = "x402-agent-db"
  engine         = "postgres"
  engine_version = "15.3"
  instance_class = "db.t3.micro"
  
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_encrypted     = true
  
  db_name  = "x402_agent"
  username = "agent"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = true
}

# Secrets Manager
resource "aws_secretsmanager_secret" "wallet_key" {
  name = "x402-agent/wallet-private-key"
}

resource "aws_secretsmanager_secret" "openai_key" {
  name = "x402-agent/openai-api-key"
}
```

## Cost Optimization

### 1. Spending Controls

```python
# cost_controls.py
import time
from datetime import datetime, timedelta
from x402_agent.monitoring import AgentMonitor

class CostController:
    """Advanced cost control and optimization."""
    
    def __init__(self, agent, budget_config):
        self.agent = agent
        self.budget_config = budget_config
        self.monitor = AgentMonitor(agent.agent_id)
        
        # Set up budget alerts
        self._setup_budget_alerts()
    
    def _setup_budget_alerts(self):
        """Configure budget-based alerts."""
        hourly_budget = self.budget_config.get("hourly", 10.0)
        daily_budget = self.budget_config.get("daily", 100.0)
        monthly_budget = self.budget_config.get("monthly", 2000.0)
        
        # Set alert thresholds at 80% of budget
        self.monitor.set_alert_threshold("hourly_spending", hourly_budget * 0.8)
        self.monitor.set_alert_threshold("daily_spending", daily_budget * 0.8)
        self.monitor.set_alert_threshold("monthly_spending", monthly_budget * 0.8)
    
    def check_budget_before_task(self, estimated_cost):
        """Check if task fits within budget."""
        current_spending = self._get_current_spending()
        
        # Check hourly budget
        if current_spending["hourly"] + estimated_cost > self.budget_config["hourly"]:
            raise BudgetExceededError("Hourly budget would be exceeded")
        
        # Check daily budget
        if current_spending["daily"] + estimated_cost > self.budget_config["daily"]:
            raise BudgetExceededError("Daily budget would be exceeded")
        
        return True
    
    def _get_current_spending(self):
        """Get current spending across different time periods."""
        now = datetime.now()
        
        return {
            "hourly": self._get_spending_since(now - timedelta(hours=1)),
            "daily": self._get_spending_since(now - timedelta(days=1)),
            "monthly": self._get_spending_since(now - timedelta(days=30))
        }
    
    def _get_spending_since(self, since_time):
        """Get spending since specific time."""
        analytics = self.monitor.get_spending_analytics(
            start_date=since_time,
            end_date=datetime.now()
        )
        return analytics.get("total_amount", 0.0)
    
    def optimize_tool_usage(self):
        """Suggest optimizations based on usage patterns."""
        tool_analytics = self.monitor.get_tool_analytics()
        suggestions = []
        
        for tool_name, stats in tool_analytics.items():
            # High cost tools
            if stats["avg_cost"] > 0.10:
                suggestions.append({
                    "type": "high_cost_tool",
                    "tool": tool_name,
                    "suggestion": f"Consider alternatives to {tool_name} (avg cost: ${stats['avg_cost']:.4f})"
                })
            
            # Low success rate tools
            if stats["success_rate"] < 0.90:
                suggestions.append({
                    "type": "unreliable_tool",
                    "tool": tool_name,
                    "suggestion": f"Investigate {tool_name} reliability (success rate: {stats['success_rate']:.2%})"
                })
        
        return suggestions

class BudgetExceededError(Exception):
    pass
```

### 2. Resource Optimization

```python
# resource_optimizer.py
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

class ResourceOptimizer:
    """Optimize resource usage for cost efficiency."""
    
    def __init__(self, swarm):
        self.swarm = swarm
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.optimization_history = []
    
    async def optimize_agent_allocation(self, tasks):
        """Optimize agent allocation for multiple tasks."""
        # Analyze task requirements
        task_analysis = await self._analyze_tasks(tasks)
        
        # Get agent capabilities and current load
        agent_status = self._get_agent_status()
        
        # Optimize allocation
        allocation = self._optimize_allocation(task_analysis, agent_status)
        
        return allocation
    
    async def _analyze_tasks(self, tasks):
        """Analyze tasks to determine resource requirements."""
        analysis = []
        
        for task in tasks:
            # Estimate cost and complexity
            estimated_cost = self._estimate_task_cost(task)
            complexity = self._estimate_complexity(task)
            required_tools = self._identify_required_tools(task)
            
            analysis.append({
                "task": task,
                "estimated_cost": estimated_cost,
                "complexity": complexity,
                "required_tools": required_tools
            })
        
        return analysis
    
    def _optimize_allocation(self, task_analysis, agent_status):
        """Optimize task allocation to minimize costs."""
        allocation = {}
        
        # Sort tasks by cost efficiency (high value, low cost first)
        sorted_tasks = sorted(
            task_analysis,
            key=lambda x: x["complexity"] / max(x["estimated_cost"], 0.001),
            reverse=True
        )
        
        for task_info in sorted_tasks:
            # Find best agent for this task
            best_agent = self._find_best_agent(task_info, agent_status)
            
            if best_agent:
                if best_agent not in allocation:
                    allocation[best_agent] = []
                allocation[best_agent].append(task_info["task"])
                
                # Update agent status
                agent_status[best_agent]["current_load"] += task_info["complexity"]
        
        return allocation
    
    def _find_best_agent(self, task_info, agent_status):
        """Find the best agent for a specific task."""
        best_agent = None
        best_score = float('-inf')
        
        for agent_id, status in agent_status.items():
            # Check if agent has required tools
            has_tools = all(
                tool in status["available_tools"]
                for tool in task_info["required_tools"]
            )
            
            if not has_tools:
                continue
            
            # Calculate efficiency score
            load_factor = 1.0 / (1.0 + status["current_load"])
            cost_factor = 1.0 / max(status["cost_per_hour"], 0.001)
            capability_factor = status.get("capability_match", 1.0)
            
            score = load_factor * cost_factor * capability_factor
            
            if score > best_score:
                best_score = score
                best_agent = agent_id
        
        return best_agent
    
    def enable_auto_scaling(self, min_agents=1, max_agents=10):
        """Enable automatic scaling based on load."""
        async def scaling_loop():
            while True:
                current_load = self._calculate_swarm_load()
                current_count = len(self.swarm.agents)
                
                if current_load > 0.8 and current_count < max_agents:
                    # Scale up
                    await self._scale_up()
                elif current_load < 0.3 and current_count > min_agents:
                    # Scale down
                    await self._scale_down()
                
                await asyncio.sleep(60)  # Check every minute
        
        # Start scaling loop
        asyncio.create_task(scaling_loop())
```

## Disaster Recovery

### 1. Backup Strategies

```python
# backup_manager.py
import boto3
import json
from datetime import datetime
import os

class BackupManager:
    """Manage backups for agent data and configurations."""
    
    def __init__(self, s3_bucket):
        self.s3_client = boto3.client('s3')
        self.s3_bucket = s3_bucket
    
    def backup_agent_state(self, agent):
        """Backup complete agent state."""
        timestamp = datetime.now().isoformat()
        
        backup_data = {
            "timestamp": timestamp,
            "agent_id": agent.agent_id,
            "network": agent.network,
            "wallet_address": agent.wallet_manager.address,
            "tools": self._serialize_tools(agent.tools),
            "configuration": agent.get_configuration(),
            "spending_history": agent.get_spending_summary(),
            "performance_metrics": agent.get_performance_metrics()
        }
        
        # Upload to S3
        backup_key = f"agent-backups/{agent.agent_id}/{timestamp}.json"
        
        self.s3_client.put_object(
            Bucket=self.s3_bucket,
            Key=backup_key,
            Body=json.dumps(backup_data, indent=2),
            ServerSideEncryption='AES256'
        )
        
        return backup_key
    
    def restore_agent_state(self, agent_id, backup_timestamp):
        """Restore agent from backup."""
        backup_key = f"agent-backups/{agent_id}/{backup_timestamp}.json"
        
        response = self.s3_client.get_object(
            Bucket=self.s3_bucket,
            Key=backup_key
        )
        
        backup_data = json.loads(response['Body'].read())
        
        # Restore agent configuration
        return self._restore_from_backup_data(backup_data)
    
    def schedule_automatic_backups(self, agent, interval_hours=24):
        """Schedule automatic backups."""
        import threading
        import time
        
        def backup_loop():
            while True:
                try:
                    self.backup_agent_state(agent)
                    print(f"Backup completed for agent {agent.agent_id}")
                except Exception as e:
                    print(f"Backup failed: {e}")
                
                time.sleep(interval_hours * 3600)
        
        thread = threading.Thread(target=backup_loop, daemon=True)
        thread.start()
```

### 2. Failover Mechanisms

```python
# failover_manager.py
import time
import threading
from typing import List, Dict

class FailoverManager:
    """Manage failover between agent instances."""
    
    def __init__(self, primary_agents: List, backup_agents: List):
        self.primary_agents = primary_agents
        self.backup_agents = backup_agents
        self.active_agents = primary_agents.copy()
        self.failed_agents = set()
        
        # Start health monitoring
        self._start_health_monitoring()
    
    def _start_health_monitoring(self):
        """Start continuous health monitoring."""
        def monitor_loop():
            while True:
                self._check_agent_health()
                time.sleep(30)  # Check every 30 seconds
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
    
    def _check_agent_health(self):
        """Check health of all active agents."""
        for agent in self.active_agents.copy():
            if not self._is_agent_healthy(agent):
                self._handle_agent_failure(agent)
    
    def _is_agent_healthy(self, agent):
        """Check if agent is healthy."""
        try:
            # Perform health check
            health = agent.health_check()
            return health.get("status") == "healthy"
        except:
            return False
    
    def _handle_agent_failure(self, failed_agent):
        """Handle agent failure with automatic failover."""
        print(f"Agent failure detected: {failed_agent.agent_id}")
        
        # Remove from active agents
        if failed_agent in self.active_agents:
            self.active_agents.remove(failed_agent)
        
        self.failed_agents.add(failed_agent)
        
        # Activate backup agent
        if self.backup_agents:
            backup_agent = self.backup_agents.pop(0)
            self.active_agents.append(backup_agent)
            
            print(f"Activated backup agent: {backup_agent.agent_id}")
            
            # Transfer state if possible
            self._transfer_agent_state(failed_agent, backup_agent)
    
    def _transfer_agent_state(self, source_agent, target_agent):
        """Transfer state from failed agent to backup."""
        try:
            # Transfer tool registrations
            for tool_name, tool in source_agent.tools.items():
                target_agent.register_tool(
                    tool_name,
                    tool.endpoint,
                    tool.description
                )
            
            print(f"State transferred from {source_agent.agent_id} to {target_agent.agent_id}")
            
        except Exception as e:
            print(f"State transfer failed: {e}")
    
    def get_active_agents(self):
        """Get list of currently active agents."""
        return self.active_agents.copy()
```

This comprehensive production deployment guide covers all the essential aspects of running x402-Agent Framework applications in production environments. The configurations and best practices provided ensure security, scalability, reliability, and cost-effectiveness for enterprise deployments.

## Next Steps

1. **Start Small**: Begin with single agent deployment
2. **Monitor Closely**: Implement comprehensive monitoring from day one
3. **Scale Gradually**: Add complexity as you gain operational experience
4. **Automate Everything**: Use infrastructure as code and CI/CD pipelines
5. **Plan for Failure**: Implement robust backup and disaster recovery procedures

For additional support with production deployments, consult the [troubleshooting guide](./troubleshooting.md) or reach out to the community on [Discord](https://discord.gg/x402-agent). 🚀