# Monitoring API Reference

The monitoring module provides comprehensive logging, analytics, and performance tracking capabilities for the x402-Agent Framework.

## Classes

### AgentMonitor

The main monitoring class for tracking agent activities and performance.

```python
class AgentMonitor:
    """
    Comprehensive monitoring and analytics for x402-Agent instances.
    
    Tracks agent activities, payments, tool usage, and performance metrics
    with real-time alerts and historical analytics.
    """
```

#### Constructor

##### `__init__(agent_id, storage_backend="sqlite", config=None)`

Initialize a new AgentMonitor instance.

**Parameters:**
- `agent_id` (str): Unique identifier for the agent being monitored
- `storage_backend` (str, optional): Storage backend for metrics. Options: "sqlite", "postgresql", "memory". Defaults to "sqlite"
- `config` (dict, optional): Configuration options for the monitor

**Example:**
```python
from x402_agent.monitoring import AgentMonitor

monitor = AgentMonitor(
    agent_id="agent_001",
    storage_backend="sqlite",
    config={
        "db_path": "./agent_metrics.db",
        "retention_days": 30,
        "enable_real_time_alerts": True
    }
)
```

#### Methods

##### `log_payment(payment_data)`

Log a payment transaction for tracking and analytics.

**Parameters:**
- `payment_data` (dict): Payment transaction details

**Example:**
```python
payment_data = {
    "amount": 0.05,
    "recipient": "0xapi_provider...",
    "tool_name": "weather_api",
    "transaction_hash": "0xtx123...",
    "timestamp": datetime.now(),
    "network": "base"
}

monitor.log_payment(payment_data)
```

##### `log_tool_usage(tool_name, execution_time, success, cost=0.0)`

Log tool usage statistics.

**Parameters:**
- `tool_name` (str): Name of the tool used
- `execution_time` (float): Time taken to execute the tool in seconds
- `success` (bool): Whether the tool execution was successful
- `cost` (float, optional): Cost of the tool execution. Defaults to 0.0

**Example:**
```python
monitor.log_tool_usage(
    tool_name="weather_api",
    execution_time=1.25,
    success=True,
    cost=0.01
)
```

##### `log_agent_activity(activity_type, details)`

Log general agent activities.

**Parameters:**
- `activity_type` (str): Type of activity (e.g., "task_start", "task_complete", "error")
- `details` (dict): Additional details about the activity

**Example:**
```python
monitor.log_agent_activity(
    activity_type="task_start",
    details={
        "task_id": "task_123",
        "description": "Analyze market data",
        "estimated_cost": 0.50
    }
)
```

##### `get_spending_analytics(period="24h")`

Get spending analytics for a specified time period.

**Parameters:**
- `period` (str, optional): Time period for analytics. Options: "1h", "24h", "7d", "30d". Defaults to "24h"

**Returns:**
- `dict`: Spending analytics data

**Example:**
```python
analytics = monitor.get_spending_analytics(period="7d")
print(f"Total spent (7 days): ${analytics['total_amount']:.2f}")
print(f"Number of transactions: {analytics['transaction_count']}")
print(f"Average transaction: ${analytics['average_amount']:.4f}")
print(f"Most expensive tool: {analytics['top_tool']}")
```

##### `get_performance_metrics()`

Get comprehensive performance metrics for the agent.

**Returns:**
- `dict`: Performance metrics data

**Example:**
```python
metrics = monitor.get_performance_metrics()
print(f"Average response time: {metrics['avg_response_time']:.2f}s")
print(f"Success rate: {metrics['success_rate']:.2%}")
print(f"Tasks completed: {metrics['tasks_completed']}")
print(f"Uptime: {metrics['uptime_hours']:.1f} hours")
```

##### `get_tool_analytics()`

Get detailed analytics for tool usage.

**Returns:**
- `dict`: Tool usage analytics

**Example:**
```python
tool_analytics = monitor.get_tool_analytics()
for tool_name, stats in tool_analytics.items():
    print(f"{tool_name}:")
    print(f"  Usage count: {stats['usage_count']}")
    print(f"  Success rate: {stats['success_rate']:.2%}")
    print(f"  Average cost: ${stats['avg_cost']:.4f}")
    print(f"  Total cost: ${stats['total_cost']:.2f}")
```

##### `set_alert_threshold(metric, threshold, condition="greater_than")`

Set up alerts for specific metrics.

**Parameters:**
- `metric` (str): Metric to monitor (e.g., "hourly_spending", "error_rate")
- `threshold` (float): Threshold value for the alert
- `condition` (str, optional): Alert condition. Options: "greater_than", "less_than", "equals". Defaults to "greater_than"

**Example:**
```python
# Alert when hourly spending exceeds $10
monitor.set_alert_threshold("hourly_spending", 10.0, "greater_than")

# Alert when success rate drops below 95%
monitor.set_alert_threshold("success_rate", 0.95, "less_than")
```

##### `add_alert_callback(callback)`

Add a callback function for alert notifications.

**Parameters:**
- `callback` (Callable): Function to call when alerts are triggered

**Example:**
```python
def alert_handler(alert_data):
    print(f"ALERT: {alert_data['metric']} = {alert_data['value']}")
    # Send notification to monitoring system

monitor.add_alert_callback(alert_handler)
```

##### `export_metrics(format="json", start_date=None, end_date=None)`

Export metrics data for external analysis.

**Parameters:**
- `format` (str, optional): Export format. Options: "json", "csv", "xlsx". Defaults to "json"
- `start_date` (datetime, optional): Start date for export
- `end_date` (datetime, optional): End date for export

**Returns:**
- `str`: Exported data in the specified format

**Example:**
```python
from datetime import datetime, timedelta

# Export last 7 days as CSV
start = datetime.now() - timedelta(days=7)
csv_data = monitor.export_metrics(
    format="csv",
    start_date=start
)

with open("agent_metrics.csv", "w") as f:
    f.write(csv_data)
```

### PaymentTracker

Specialized class for tracking payment-related metrics.

```python
class PaymentTracker:
    """
    Tracks payment transactions and provides payment-specific analytics.
    """
```

#### Methods

##### `track_payment(payment_result)`

Track a completed payment transaction.

**Parameters:**
- `payment_result` (PaymentResult): Result of a payment transaction

**Example:**
```python
from x402_agent.monitoring import PaymentTracker

tracker = PaymentTracker()
tracker.track_payment(payment_result)
```

##### `get_payment_summary(period="24h")`

Get a summary of payment activity.

**Parameters:**
- `period` (str, optional): Time period for summary. Defaults to "24h"

**Returns:**
- `dict`: Payment summary data

**Example:**
```python
summary = tracker.get_payment_summary(period="7d")
print(f"Total payments: {summary['count']}")
print(f"Total amount: ${summary['total_amount']:.2f}")
print(f"Average payment: ${summary['average_amount']:.4f}")
```

### PerformanceProfiler

Class for detailed performance profiling of agent operations.

```python
class PerformanceProfiler:
    """
    Profiles agent performance and identifies bottlenecks.
    """
```

#### Methods

##### `start_profiling(operation_name)`

Start profiling an operation.

**Parameters:**
- `operation_name` (str): Name of the operation being profiled

**Returns:**
- `str`: Profile session ID

**Example:**
```python
from x402_agent.monitoring import PerformanceProfiler

profiler = PerformanceProfiler()
session_id = profiler.start_profiling("api_call_batch")
```

##### `end_profiling(session_id)`

End a profiling session and record results.

**Parameters:**
- `session_id` (str): Profile session ID from start_profiling

**Returns:**
- `dict`: Profiling results

**Example:**
```python
results = profiler.end_profiling(session_id)
print(f"Operation took: {results['duration']:.2f}s")
print(f"Memory usage: {results['memory_mb']:.1f} MB")
```

## Monitoring Configuration

### Database Configuration

```python
# SQLite configuration (default)
config = {
    "storage_backend": "sqlite",
    "db_path": "./agent_metrics.db",
    "retention_days": 30
}

# PostgreSQL configuration
config = {
    "storage_backend": "postgresql",
    "connection_string": "postgresql://user:pass@localhost/metrics",
    "retention_days": 90
}

# In-memory configuration (for testing)
config = {
    "storage_backend": "memory",
    "retention_days": 1
}
```

### Alert Configuration

```python
alert_config = {
    "enable_real_time_alerts": True,
    "alert_cooldown_minutes": 15,
    "max_alerts_per_hour": 10,
    "alert_channels": ["console", "webhook", "email"]
}
```

### Metrics Collection Configuration

```python
metrics_config = {
    "collect_system_metrics": True,
    "collect_network_metrics": True,
    "sample_rate": 1.0,  # Collect 100% of metrics
    "batch_size": 100,
    "flush_interval_seconds": 60
}
```

## Real-time Monitoring

### Live Dashboard Data

```python
def get_live_dashboard_data(monitor):
    """Get real-time data for monitoring dashboard."""
    return {
        "current_balance": monitor.get_current_balance(),
        "active_tasks": monitor.get_active_tasks_count(),
        "recent_payments": monitor.get_recent_payments(limit=10),
        "system_health": monitor.get_system_health(),
        "performance_metrics": monitor.get_performance_metrics()
    }
```

### WebSocket Monitoring

```python
import asyncio
import websockets

async def monitoring_websocket(monitor):
    """Stream monitoring data via WebSocket."""
    async def handler(websocket, path):
        while True:
            data = get_live_dashboard_data(monitor)
            await websocket.send(json.dumps(data))
            await asyncio.sleep(5)  # Update every 5 seconds
    
    return websockets.serve(handler, "localhost", 8765)
```

## Analytics and Reporting

### Custom Analytics Queries

```python
def custom_analytics_query(monitor, query_params):
    """Execute custom analytics queries."""
    
    # Example: Get tool usage by hour
    if query_params["type"] == "tool_usage_by_hour":
        return monitor.query_metrics(
            metric="tool_usage",
            group_by="hour",
            filters=query_params.get("filters", {})
        )
    
    # Example: Get cost efficiency trends
    elif query_params["type"] == "cost_efficiency":
        return monitor.query_metrics(
            metric="cost_per_task",
            time_range=query_params["time_range"]
        )
```

### Report Generation

```python
def generate_daily_report(monitor):
    """Generate a comprehensive daily report."""
    
    report = {
        "date": datetime.now().date(),
        "summary": monitor.get_spending_analytics(period="24h"),
        "performance": monitor.get_performance_metrics(),
        "tools": monitor.get_tool_analytics(),
        "alerts": monitor.get_alerts_summary(),
        "recommendations": generate_recommendations(monitor)
    }
    
    return report

def generate_recommendations(monitor):
    """Generate optimization recommendations."""
    recommendations = []
    
    # Check for high-cost tools
    tool_analytics = monitor.get_tool_analytics()
    for tool_name, stats in tool_analytics.items():
        if stats["avg_cost"] > 0.10:  # High cost threshold
            recommendations.append({
                "type": "cost_optimization",
                "message": f"Consider optimizing {tool_name} usage (avg cost: ${stats['avg_cost']:.4f})"
            })
    
    # Check success rates
    performance = monitor.get_performance_metrics()
    if performance["success_rate"] < 0.95:
        recommendations.append({
            "type": "reliability",
            "message": f"Success rate is {performance['success_rate']:.2%}, consider investigating failures"
        })
    
    return recommendations
```

## Integration Examples

### Integration with Agent

```python
from x402_agent import X402Agent
from x402_agent.monitoring import AgentMonitor

class MonitoredX402Agent(X402Agent):
    """X402Agent with built-in monitoring."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.monitor = AgentMonitor(
            agent_id=f"agent_{id(self)}",
            storage_backend="sqlite"
        )
        
        # Set up monitoring callbacks
        self.payment_processor.add_payment_callback(self._on_payment)
        self.tool_registry.add_execution_callback(self._on_tool_execution)
    
    def _on_payment(self, payment_result):
        """Handle payment events."""
        self.monitor.log_payment({
            "amount": payment_result.amount,
            "recipient": payment_result.recipient,
            "transaction_hash": payment_result.transaction_hash,
            "timestamp": payment_result.timestamp,
            "network": payment_result.network
        })
    
    def _on_tool_execution(self, tool_name, execution_time, success, cost):
        """Handle tool execution events."""
        self.monitor.log_tool_usage(tool_name, execution_time, success, cost)
    
    def get_monitoring_dashboard(self):
        """Get monitoring dashboard data."""
        return {
            "spending": self.monitor.get_spending_analytics(),
            "performance": self.monitor.get_performance_metrics(),
            "tools": self.monitor.get_tool_analytics()
        }
```

### Integration with Swarm

```python
from x402_agent.swarm import AgentSwarm
from x402_agent.monitoring import AgentMonitor

class MonitoredAgentSwarm(AgentSwarm):
    """AgentSwarm with comprehensive monitoring."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.swarm_monitor = AgentMonitor(
            agent_id=f"swarm_{id(self)}",
            storage_backend="postgresql"
        )
    
    def collaborate(self, task, **kwargs):
        """Collaborate with monitoring."""
        start_time = time.time()
        
        # Log task start
        self.swarm_monitor.log_agent_activity("collaboration_start", {
            "task": task,
            "agent_count": len(self.agents),
            "strategy": kwargs.get("strategy", "parallel")
        })
        
        try:
            result = super().collaborate(task, **kwargs)
            
            # Log successful completion
            execution_time = time.time() - start_time
            self.swarm_monitor.log_agent_activity("collaboration_complete", {
                "task": task,
                "execution_time": execution_time,
                "total_cost": result.total_cost,
                "success": True
            })
            
            return result
            
        except Exception as e:
            # Log failure
            execution_time = time.time() - start_time
            self.swarm_monitor.log_agent_activity("collaboration_failed", {
                "task": task,
                "execution_time": execution_time,
                "error": str(e),
                "success": False
            })
            raise
```

## Best Practices

1. **Selective Monitoring**: Monitor critical metrics without overwhelming the system
2. **Alert Tuning**: Set appropriate thresholds to avoid alert fatigue
3. **Data Retention**: Configure appropriate retention periods for different metrics
4. **Performance Impact**: Monitor the monitoring system's own performance impact
5. **Security**: Ensure monitoring data doesn't expose sensitive information

## Examples

### Basic Monitoring Setup

```python
from x402_agent.monitoring import AgentMonitor

# Initialize monitor
monitor = AgentMonitor("my_agent")

# Set up alerts
monitor.set_alert_threshold("hourly_spending", 5.0)
monitor.set_alert_threshold("error_rate", 0.10)

# Add alert handler
def handle_alert(alert):
    print(f"Alert: {alert['message']}")

monitor.add_alert_callback(handle_alert)

# Log some activities
monitor.log_payment({
    "amount": 0.05,
    "recipient": "0xapi...",
    "tool_name": "weather_api"
})

# Get analytics
analytics = monitor.get_spending_analytics()
print(f"Total spent: ${analytics['total_amount']}")
```

### Advanced Monitoring with Custom Metrics

```python
from x402_agent.monitoring import AgentMonitor, PerformanceProfiler

# Initialize components
monitor = AgentMonitor("advanced_agent")
profiler = PerformanceProfiler()

# Custom metric tracking
def track_custom_metric(name, value, tags=None):
    monitor.log_custom_metric(name, value, tags or {})

# Profile a complex operation
session_id = profiler.start_profiling("batch_api_calls")

# ... perform operations ...

results = profiler.end_profiling(session_id)
track_custom_metric("batch_processing_time", results["duration"])

# Generate comprehensive report
report = monitor.generate_report(
    include_recommendations=True,
    export_format="json"
)

print(f"Report generated: {len(report)} metrics collected")
```