"""
Debugging and monitoring tools for Level42 Framework.

This module provides comprehensive logging, debugging modes, and usage analytics
for monitoring agent behavior and payment activities.
"""

import logging
import json
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from contextlib import contextmanager


@dataclass
class DebugConfig:
    """Configuration for debug mode."""
    enabled: bool = False
    log_level: str = "INFO"
    log_file: Optional[str] = None
    log_payments: bool = True
    log_api_calls: bool = True
    log_agent_decisions: bool = False
    verbose_errors: bool = True


class Level42Logger:
    """
    Centralized logging system for Level42 Framework.
    
    Provides structured logging with different levels and categories
    for comprehensive monitoring and debugging.
    """
    
    def __init__(self, debug_config: DebugConfig = None):
        """
        Initialize logger with debug configuration.
        
        Args:
            debug_config: Debug configuration settings
        """
        self.debug_config = debug_config or DebugConfig()
        self.logger = self._setup_logger()
        self._log_session_start()
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration based on debug settings."""
        logger = logging.getLogger("level42")
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Set log level
        log_level = getattr(logging, self.debug_config.log_level.upper(), logging.INFO)
        logger.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler if specified
        if self.debug_config.log_file:
            try:
                file_handler = logging.FileHandler(self.debug_config.log_file)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                logger.warning(f"Failed to create file handler: {str(e)}")
        
        return logger
    
    def _log_session_start(self):
        """Log session start information."""
        self.logger.info("=" * 50)
        self.logger.info("Level42 Framework Session Started")
        self.logger.info(f"Debug Mode: {'ENABLED' if self.debug_config.enabled else 'DISABLED'}")
        self.logger.info(f"Log Level: {self.debug_config.log_level}")
        self.logger.info("=" * 50)
    
    def log_payment(self, amount: float, recipient: str, tool_name: str, 
                   status: str, tx_hash: str = "", error: str = ""):
        """
        Log payment activity.
        
        Args:
            amount: Payment amount
            recipient: Payment recipient
            tool_name: Tool requiring payment
            status: Payment status
            tx_hash: Transaction hash
            error: Error message if failed
        """
        if not self.debug_config.log_payments:
            return
        
        log_data = {
            "type": "payment",
            "amount": amount,
            "recipient": recipient,
            "tool_name": tool_name,
            "status": status,
            "tx_hash": tx_hash,
            "timestamp": datetime.now().isoformat()
        }
        
        if status == "completed":
            self.logger.info(f"Payment completed: {amount} USDC to {recipient} for {tool_name} (tx: {tx_hash})")
        elif status == "failed":
            self.logger.error(f"Payment failed: {amount} USDC to {recipient} for {tool_name} - {error}")
            log_data["error"] = error
        else:
            self.logger.info(f"Payment {status}: {amount} USDC to {recipient} for {tool_name}")
        
        if self.debug_config.enabled:
            self.logger.debug(f"Payment details: {json.dumps(log_data, indent=2)}")
    
    def log_api_call(self, url: str, method: str, status_code: int, 
                    response_time: float, tool_name: str = ""):
        """
        Log API call activity.
        
        Args:
            url: API endpoint URL
            method: HTTP method
            status_code: Response status code
            response_time: Response time in seconds
            tool_name: Tool name if applicable
        """
        if not self.debug_config.log_api_calls:
            return
        
        log_data = {
            "type": "api_call",
            "url": url,
            "method": method,
            "status_code": status_code,
            "response_time": response_time,
            "tool_name": tool_name,
            "timestamp": datetime.now().isoformat()
        }
        
        if status_code == 402:
            self.logger.info(f"HTTP 402 received from {url} - payment required")
        elif 200 <= status_code < 300:
            self.logger.info(f"API call successful: {method} {url} ({status_code}) - {response_time:.3f}s")
        else:
            self.logger.warning(f"API call failed: {method} {url} ({status_code}) - {response_time:.3f}s")
        
        if self.debug_config.enabled:
            self.logger.debug(f"API call details: {json.dumps(log_data, indent=2)}")
    
    def log_agent_decision(self, agent_id: str, decision: str, context: Dict[str, Any]):
        """
        Log agent decision-making process.
        
        Args:
            agent_id: Agent identifier
            decision: Decision made by agent
            context: Context information for the decision
        """
        if not self.debug_config.log_agent_decisions:
            return
        
        log_data = {
            "type": "agent_decision",
            "agent_id": agent_id,
            "decision": decision,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"Agent {agent_id} decision: {decision}")
        
        if self.debug_config.enabled:
            self.logger.debug(f"Decision context: {json.dumps(log_data, indent=2)}")
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """
        Log error with context information.
        
        Args:
            error: Exception that occurred
            context: Additional context information
        """
        context = context or {}
        
        log_data = {
            "type": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
        if self.debug_config.verbose_errors:
            self.logger.error(f"Error occurred: {type(error).__name__}: {str(error)}")
            if context:
                self.logger.error(f"Error context: {json.dumps(context, indent=2)}")
        else:
            self.logger.error(f"Error: {str(error)}")
        
        if self.debug_config.enabled:
            import traceback
            self.logger.debug(f"Full error details: {json.dumps(log_data, indent=2)}")
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
    
    def log_debug(self, message: str, data: Dict[str, Any] = None):
        """
        Log debug information.
        
        Args:
            message: Debug message
            data: Additional debug data
        """
        if not self.debug_config.enabled:
            return
        
        self.logger.debug(message)
        if data:
            self.logger.debug(f"Debug data: {json.dumps(data, indent=2)}")


class UsageAnalytics:
    """
    Usage analytics and reporting system for Level42 Framework.
    
    Provides comprehensive analytics on agent spending, tool usage,
    and performance metrics.
    """
    
    def __init__(self, db_path: str = "level42_analytics.db"):
        """
        Initialize analytics system.
        
        Args:
            db_path: Path to analytics database
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize analytics database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Agent sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    session_start DATETIME NOT NULL,
                    session_end DATETIME,
                    total_spent REAL DEFAULT 0,
                    api_calls_count INTEGER DEFAULT 0,
                    payments_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tool usage table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tool_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    tool_name TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 1,
                    total_spent REAL DEFAULT 0,
                    avg_response_time REAL DEFAULT 0,
                    success_rate REAL DEFAULT 1.0,
                    last_used DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metric_unit TEXT,
                    timestamp DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_sessions_agent_id ON agent_sessions(agent_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tool_usage_agent_tool ON tool_usage(agent_id, tool_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance_metrics_agent ON performance_metrics(agent_id)')
            
            conn.commit()
    
    def start_session(self, agent_id: str) -> int:
        """
        Start a new agent session.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Session ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO agent_sessions (agent_id, session_start)
                VALUES (?, ?)
            ''', (agent_id, datetime.now()))
            return cursor.lastrowid
    
    def end_session(self, session_id: int):
        """
        End an agent session.
        
        Args:
            session_id: Session ID to end
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE agent_sessions 
                SET session_end = ?
                WHERE id = ?
            ''', (datetime.now(), session_id))
            conn.commit()
    
    def record_tool_usage(self, agent_id: str, tool_name: str, cost: float, 
                         response_time: float, success: bool):
        """
        Record tool usage statistics.
        
        Args:
            agent_id: Agent identifier
            tool_name: Tool name
            cost: Cost of tool usage
            response_time: Response time in seconds
            success: Whether the call was successful
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if record exists
            cursor.execute('''
                SELECT id, usage_count, total_spent, avg_response_time, success_rate
                FROM tool_usage 
                WHERE agent_id = ? AND tool_name = ?
            ''', (agent_id, tool_name))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                record_id, usage_count, total_spent, avg_response_time, success_rate = existing
                
                new_usage_count = usage_count + 1
                new_total_spent = total_spent + cost
                new_avg_response_time = ((avg_response_time * usage_count) + response_time) / new_usage_count
                new_success_rate = ((success_rate * usage_count) + (1.0 if success else 0.0)) / new_usage_count
                
                cursor.execute('''
                    UPDATE tool_usage 
                    SET usage_count = ?, total_spent = ?, avg_response_time = ?, 
                        success_rate = ?, last_used = ?
                    WHERE id = ?
                ''', (new_usage_count, new_total_spent, new_avg_response_time, 
                      new_success_rate, datetime.now(), record_id))
            else:
                # Create new record
                cursor.execute('''
                    INSERT INTO tool_usage 
                    (agent_id, tool_name, usage_count, total_spent, avg_response_time, 
                     success_rate, last_used)
                    VALUES (?, ?, 1, ?, ?, ?, ?)
                ''', (agent_id, tool_name, cost, response_time, 
                      1.0 if success else 0.0, datetime.now()))
            
            conn.commit()
    
    def record_performance_metric(self, agent_id: str, metric_name: str, 
                                value: float, unit: str = ""):
        """
        Record a performance metric.
        
        Args:
            agent_id: Agent identifier
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO performance_metrics 
                (agent_id, metric_name, metric_value, metric_unit, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (agent_id, metric_name, value, unit, datetime.now()))
            conn.commit()
    
    def get_agent_summary(self, agent_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive agent usage summary.
        
        Args:
            agent_id: Agent identifier
            days: Number of days to analyze
            
        Returns:
            Dictionary with agent summary
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Session statistics
            cursor.execute('''
                SELECT COUNT(*) as session_count,
                       AVG(CASE WHEN session_end IS NOT NULL 
                           THEN (julianday(session_end) - julianday(session_start)) * 24 * 60
                           ELSE NULL END) as avg_session_minutes,
                       SUM(total_spent) as total_spent,
                       SUM(api_calls_count) as total_api_calls,
                       SUM(payments_count) as total_payments
                FROM agent_sessions 
                WHERE agent_id = ? AND session_start >= ?
            ''', (agent_id, cutoff_date))
            
            session_stats = cursor.fetchone()
            
            # Tool usage statistics
            cursor.execute('''
                SELECT tool_name, usage_count, total_spent, avg_response_time, success_rate
                FROM tool_usage 
                WHERE agent_id = ? AND last_used >= ?
                ORDER BY usage_count DESC
            ''', (agent_id, cutoff_date))
            
            tool_stats = [
                {
                    'tool_name': row[0],
                    'usage_count': row[1],
                    'total_spent': row[2],
                    'avg_response_time': row[3],
                    'success_rate': row[4]
                }
                for row in cursor.fetchall()
            ]
            
            # Performance trends
            cursor.execute('''
                SELECT metric_name, AVG(metric_value) as avg_value, 
                       MIN(metric_value) as min_value, MAX(metric_value) as max_value
                FROM performance_metrics 
                WHERE agent_id = ? AND timestamp >= ?
                GROUP BY metric_name
            ''', (agent_id, cutoff_date))
            
            performance_stats = {
                row[0]: {
                    'avg': row[1],
                    'min': row[2],
                    'max': row[3]
                }
                for row in cursor.fetchall()
            }
            
            return {
                'agent_id': agent_id,
                'period_days': days,
                'session_count': session_stats[0] or 0,
                'avg_session_minutes': session_stats[1] or 0,
                'total_spent': session_stats[2] or 0,
                'total_api_calls': session_stats[3] or 0,
                'total_payments': session_stats[4] or 0,
                'tool_usage': tool_stats,
                'performance_metrics': performance_stats
            }
    
    def get_spending_report(self, agent_id: str = None, days: int = 30) -> Dict[str, Any]:
        """
        Generate spending report.
        
        Args:
            agent_id: Agent identifier (None for all agents)
            days: Number of days to analyze
            
        Returns:
            Dictionary with spending report
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Base query conditions
            where_clause = "WHERE last_used >= ?"
            params = [cutoff_date]
            
            if agent_id:
                where_clause += " AND agent_id = ?"
                params.append(agent_id)
            
            # Total spending by tool
            cursor.execute(f'''
                SELECT tool_name, SUM(total_spent) as total, SUM(usage_count) as count
                FROM tool_usage 
                {where_clause}
                GROUP BY tool_name
                ORDER BY total DESC
            ''', params)
            
            tool_spending = [
                {
                    'tool_name': row[0],
                    'total_spent': row[1],
                    'usage_count': row[2],
                    'avg_cost_per_use': row[1] / row[2] if row[2] > 0 else 0
                }
                for row in cursor.fetchall()
            ]
            
            # Daily spending trend
            cursor.execute(f'''
                SELECT DATE(last_used) as date, SUM(total_spent) as daily_total
                FROM tool_usage 
                {where_clause}
                GROUP BY DATE(last_used)
                ORDER BY date DESC
                LIMIT 30
            ''', params)
            
            daily_spending = [
                {'date': row[0], 'amount': row[1]}
                for row in cursor.fetchall()
            ]
            
            # Overall totals
            total_spent = sum(item['total_spent'] for item in tool_spending)
            total_usage = sum(item['usage_count'] for item in tool_spending)
            
            return {
                'period_days': days,
                'agent_id': agent_id,
                'total_spent': total_spent,
                'total_usage': total_usage,
                'avg_cost_per_use': total_spent / total_usage if total_usage > 0 else 0,
                'tool_spending': tool_spending,
                'daily_spending': daily_spending
            }


@contextmanager
def debug_mode(config: DebugConfig = None):
    """
    Context manager for enabling debug mode.
    
    Args:
        config: Debug configuration
        
    Usage:
        with debug_mode(DebugConfig(enabled=True, log_level="DEBUG")):
            # Debug mode is enabled for this block
            agent.run("some task")
    """
    config = config or DebugConfig(enabled=True)
    logger = Level42Logger(config)
    
    try:
        yield logger
    finally:
        logger.logger.info("Debug session ended")


def create_debug_config(enabled: bool = True, log_level: str = "DEBUG", 
                       log_file: str = None, verbose: bool = True) -> DebugConfig:
    """
    Create a debug configuration with common settings.
    
    Args:
        enabled: Enable debug mode
        log_level: Logging level
        log_file: Optional log file path
        verbose: Enable verbose error reporting
        
    Returns:
        DebugConfig instance
    """
    return DebugConfig(
        enabled=enabled,
        log_level=log_level,
        log_file=log_file,
        log_payments=True,
        log_api_calls=True,
        log_agent_decisions=verbose,
        verbose_errors=verbose
    )# Analytics enhancements
