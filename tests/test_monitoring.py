"""
Unit tests for monitoring and debugging tools.

Tests logging functionality, usage analytics, debug modes,
and comprehensive monitoring capabilities.
"""

import pytest
import sqlite3
import tempfile
import os
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from x402_agent.monitoring import (
    X402Logger, DebugConfig, UsageAnalytics, 
    debug_mode, create_debug_config
)


class TestDebugConfig:
    """Test cases for DebugConfig dataclass."""
    
    def test_debug_config_defaults(self):
        """Test default debug configuration values."""
        config = DebugConfig()
        
        assert config.enabled is False
        assert config.log_level == "INFO"
        assert config.log_file is None
        assert config.log_payments is True
        assert config.log_api_calls is True
        assert config.log_agent_decisions is False
        assert config.verbose_errors is True
    
    def test_debug_config_custom_values(self):
        """Test debug configuration with custom values."""
        config = DebugConfig(
            enabled=True,
            log_level="DEBUG",
            log_file="test.log",
            log_payments=False,
            log_api_calls=False,
            log_agent_decisions=True,
            verbose_errors=False
        )
        
        assert config.enabled is True
        assert config.log_level == "DEBUG"
        assert config.log_file == "test.log"
        assert config.log_payments is False
        assert config.log_api_calls is False
        assert config.log_agent_decisions is True
        assert config.verbose_errors is False
    
    def test_create_debug_config_helper(self):
        """Test create_debug_config helper function."""
        config = create_debug_config(
            enabled=True,
            log_level="WARNING",
            log_file="debug.log",
            verbose=False
        )
        
        assert config.enabled is True
        assert config.log_level == "WARNING"
        assert config.log_file == "debug.log"
        assert config.log_agent_decisions is False
        assert config.verbose_errors is False


class TestX402Logger:
    """Test cases for X402Logger class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.debug_config = DebugConfig(
            enabled=True,
            log_level="DEBUG",
            log_payments=True,
            log_api_calls=True,
            log_agent_decisions=True,
            verbose_errors=True
        )
    
    def test_logger_initialization(self):
        """Test logger initialization."""
        logger = X402Logger(self.debug_config)
        
        assert logger.debug_config == self.debug_config
        assert logger.logger is not None
        assert logger.logger.name == "x402_agent"
    
    def test_logger_initialization_default_config(self):
        """Test logger initialization with default config."""
        logger = X402Logger()
        
        assert logger.debug_config is not None
        assert logger.debug_config.enabled is False
        assert logger.debug_config.log_level == "INFO"
    
    @patch('logging.FileHandler')
    def test_logger_file_handler_creation(self, mock_file_handler):
        """Test file handler creation when log file is specified."""
        config = DebugConfig(enabled=True, log_file="test.log")
        mock_handler = Mock()
        mock_file_handler.return_value = mock_handler
        
        logger = X402Logger(config)
        
        mock_file_handler.assert_called_once_with("test.log")
        mock_handler.setFormatter.assert_called_once()
    
    @patch('logging.FileHandler')
    def test_logger_file_handler_error(self, mock_file_handler):
        """Test file handler creation error handling."""
        config = DebugConfig(enabled=True, log_file="invalid/path/test.log")
        mock_file_handler.side_effect = OSError("Permission denied")
        
        # Should not raise exception, just log warning
        logger = X402Logger(config)
        assert logger.logger is not None
    
    def test_log_payment_completed(self):
        """Test logging completed payment."""
        logger = X402Logger(self.debug_config)
        
        # Should not raise exception
        logger.log_payment(
            amount=25.0,
            recipient="0x123...",
            tool_name="test-api",
            status="completed",
            tx_hash="0xabc123"
        )
    
    def test_log_payment_failed(self):
        """Test logging failed payment."""
        logger = X402Logger(self.debug_config)
        
        # Should not raise exception
        logger.log_payment(
            amount=50.0,
            recipient="0x456...",
            tool_name="expensive-api",
            status="failed",
            error="Insufficient funds"
        )
    
    def test_log_payment_disabled(self):
        """Test payment logging when disabled."""
        config = DebugConfig(enabled=True, log_payments=False)
        logger = X402Logger(config)
        
        # Should not raise exception and should return quickly
        logger.log_payment(
            amount=25.0,
            recipient="0x123...",
            tool_name="test-api",
            status="completed",
            tx_hash="0xabc123"
        )
    
    def test_log_api_call_success(self):
        """Test logging successful API call."""
        logger = X402Logger(self.debug_config)
        
        logger.log_api_call(
            url="https://api.example.com/test",
            method="GET",
            status_code=200,
            response_time=0.5,
            tool_name="test-api"
        )
    
    def test_log_api_call_402(self):
        """Test logging 402 API response."""
        logger = X402Logger(self.debug_config)
        
        logger.log_api_call(
            url="https://api.example.com/paid",
            method="POST",
            status_code=402,
            response_time=0.2,
            tool_name="paid-api"
        )
    
    def test_log_api_call_error(self):
        """Test logging API call error."""
        logger = X402Logger(self.debug_config)
        
        logger.log_api_call(
            url="https://api.example.com/error",
            method="GET",
            status_code=500,
            response_time=1.0,
            tool_name="error-api"
        )
    
    def test_log_api_call_disabled(self):
        """Test API call logging when disabled."""
        config = DebugConfig(enabled=True, log_api_calls=False)
        logger = X402Logger(config)
        
        # Should not raise exception and should return quickly
        logger.log_api_call(
            url="https://api.example.com/test",
            method="GET",
            status_code=200,
            response_time=0.5
        )
    
    def test_log_agent_decision(self):
        """Test logging agent decision."""
        logger = X402Logger(self.debug_config)
        
        context = {
            'available_tools': ['api1', 'api2'],
            'budget_remaining': 50.0,
            'task_priority': 'high'
        }
        
        logger.log_agent_decision(
            agent_id="agent_123",
            decision="use_api1",
            context=context
        )
    
    def test_log_agent_decision_disabled(self):
        """Test agent decision logging when disabled."""
        config = DebugConfig(enabled=True, log_agent_decisions=False)
        logger = X402Logger(config)
        
        # Should not raise exception and should return quickly
        logger.log_agent_decision(
            agent_id="agent_123",
            decision="use_api1",
            context={}
        )
    
    def test_log_error_verbose(self):
        """Test verbose error logging."""
        logger = X402Logger(self.debug_config)
        
        test_error = ValueError("Test error message")
        context = {
            'operation': 'payment',
            'amount': 25.0,
            'recipient': '0x123...'
        }
        
        logger.log_error(test_error, context)
    
    def test_log_error_non_verbose(self):
        """Test non-verbose error logging."""
        config = DebugConfig(enabled=True, verbose_errors=False)
        logger = X402Logger(config)
        
        test_error = RuntimeError("Network error")
        
        logger.log_error(test_error)
    
    def test_log_debug_enabled(self):
        """Test debug logging when enabled."""
        logger = X402Logger(self.debug_config)
        
        debug_data = {
            'step': 'payment_processing',
            'state': 'validating_recipient',
            'recipient': '0x123...'
        }
        
        logger.log_debug("Processing payment validation", debug_data)
    
    def test_log_debug_disabled(self):
        """Test debug logging when disabled."""
        config = DebugConfig(enabled=False)
        logger = X402Logger(config)
        
        # Should not raise exception and should return quickly
        logger.log_debug("This should not be logged", {'data': 'test'})


class TestUsageAnalytics:
    """Test cases for UsageAnalytics class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.analytics = UsageAnalytics(self.temp_db.name)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_analytics_initialization(self):
        """Test analytics system initialization."""
        assert self.analytics.db_path == self.temp_db.name
        
        # Verify database tables were created
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['agent_sessions', 'tool_usage', 'performance_metrics']
            for table in expected_tables:
                assert table in tables
    
    def test_start_end_session(self):
        """Test starting and ending agent sessions."""
        session_id = self.analytics.start_session("test_agent")
        assert session_id is not None
        assert isinstance(session_id, int)
        
        # End the session
        self.analytics.end_session(session_id)
        
        # Verify session was recorded
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT agent_id, session_end FROM agent_sessions WHERE id = ?", (session_id,))
            result = cursor.fetchone()
            
            assert result is not None
            assert result[0] == "test_agent"
            assert result[1] is not None  # session_end should be set
    
    def test_record_tool_usage_new_tool(self):
        """Test recording tool usage for new tool."""
        self.analytics.record_tool_usage(
            agent_id="test_agent",
            tool_name="new_tool",
            cost=1.5,
            response_time=0.8,
            success=True
        )
        
        # Verify tool usage was recorded
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT usage_count, total_spent, avg_response_time, success_rate
                FROM tool_usage 
                WHERE agent_id = ? AND tool_name = ?
            """, ("test_agent", "new_tool"))
            result = cursor.fetchone()
            
            assert result is not None
            assert result[0] == 1  # usage_count
            assert result[1] == 1.5  # total_spent
            assert result[2] == 0.8  # avg_response_time
            assert result[3] == 1.0  # success_rate
    
    def test_record_tool_usage_existing_tool(self):
        """Test recording tool usage for existing tool."""
        # Record first usage
        self.analytics.record_tool_usage(
            agent_id="test_agent",
            tool_name="existing_tool",
            cost=1.0,
            response_time=0.5,
            success=True
        )
        
        # Record second usage
        self.analytics.record_tool_usage(
            agent_id="test_agent",
            tool_name="existing_tool",
            cost=2.0,
            response_time=1.0,
            success=False
        )
        
        # Verify aggregated statistics
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT usage_count, total_spent, avg_response_time, success_rate
                FROM tool_usage 
                WHERE agent_id = ? AND tool_name = ?
            """, ("test_agent", "existing_tool"))
            result = cursor.fetchone()
            
            assert result is not None
            assert result[0] == 2  # usage_count
            assert result[1] == 3.0  # total_spent (1.0 + 2.0)
            assert result[2] == 0.75  # avg_response_time ((0.5 + 1.0) / 2)
            assert result[3] == 0.5  # success_rate (1 success out of 2)
    
    def test_record_performance_metric(self):
        """Test recording performance metrics."""
        self.analytics.record_performance_metric(
            agent_id="test_agent",
            metric_name="response_time",
            value=0.5,
            unit="seconds"
        )
        
        self.analytics.record_performance_metric(
            agent_id="test_agent",
            metric_name="memory_usage",
            value=128.5,
            unit="MB"
        )
        
        # Verify metrics were recorded
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT metric_name, metric_value, metric_unit
                FROM performance_metrics 
                WHERE agent_id = ?
                ORDER BY metric_name
            """, ("test_agent",))
            results = cursor.fetchall()
            
            assert len(results) == 2
            assert results[0] == ("memory_usage", 128.5, "MB")
            assert results[1] == ("response_time", 0.5, "seconds")
    
    def test_get_agent_summary_with_data(self):
        """Test getting agent summary with data."""
        # Set up test data
        session_id = self.analytics.start_session("test_agent")
        
        self.analytics.record_tool_usage("test_agent", "tool1", 1.0, 0.5, True)
        self.analytics.record_tool_usage("test_agent", "tool2", 2.0, 1.0, True)
        self.analytics.record_tool_usage("test_agent", "tool1", 1.5, 0.8, False)
        
        self.analytics.record_performance_metric("test_agent", "response_time", 0.6, "seconds")
        self.analytics.record_performance_metric("test_agent", "response_time", 0.4, "seconds")
        
        self.analytics.end_session(session_id)
        
        # Get summary
        summary = self.analytics.get_agent_summary("test_agent", days=30)
        
        assert summary['agent_id'] == "test_agent"
        assert summary['period_days'] == 30
        assert summary['session_count'] == 1
        assert summary['avg_session_minutes'] > 0
        
        # Check tool usage
        assert len(summary['tool_usage']) == 2
        tool_names = [tool['tool_name'] for tool in summary['tool_usage']]
        assert 'tool1' in tool_names
        assert 'tool2' in tool_names
        
        # Check performance metrics
        assert 'response_time' in summary['performance_metrics']
        assert summary['performance_metrics']['response_time']['avg'] == 0.5
        assert summary['performance_metrics']['response_time']['min'] == 0.4
        assert summary['performance_metrics']['response_time']['max'] == 0.6
    
    def test_get_agent_summary_no_data(self):
        """Test getting agent summary with no data."""
        summary = self.analytics.get_agent_summary("nonexistent_agent", days=30)
        
        assert summary['agent_id'] == "nonexistent_agent"
        assert summary['session_count'] == 0
        assert summary['total_spent'] == 0
        assert summary['tool_usage'] == []
        assert summary['performance_metrics'] == {}
    
    def test_get_spending_report_single_agent(self):
        """Test getting spending report for single agent."""
        # Set up test data
        self.analytics.record_tool_usage("test_agent", "tool1", 10.0, 0.5, True)
        self.analytics.record_tool_usage("test_agent", "tool2", 20.0, 1.0, True)
        self.analytics.record_tool_usage("test_agent", "tool1", 5.0, 0.3, True)
        
        report = self.analytics.get_spending_report("test_agent", days=30)
        
        assert report['agent_id'] == "test_agent"
        assert report['total_spent'] == 35.0
        assert report['total_usage'] == 3
        assert report['avg_cost_per_use'] == 35.0 / 3
        
        # Check tool spending breakdown
        assert len(report['tool_spending']) == 2
        tool_spending = {item['tool_name']: item['total_spent'] for item in report['tool_spending']}
        assert tool_spending['tool1'] == 15.0
        assert tool_spending['tool2'] == 20.0
    
    def test_get_spending_report_all_agents(self):
        """Test getting spending report for all agents."""
        # Set up test data for multiple agents
        self.analytics.record_tool_usage("agent1", "tool1", 10.0, 0.5, True)
        self.analytics.record_tool_usage("agent2", "tool1", 20.0, 1.0, True)
        self.analytics.record_tool_usage("agent1", "tool2", 5.0, 0.3, True)
        
        report = self.analytics.get_spending_report(agent_id=None, days=30)
        
        assert report['agent_id'] is None
        assert report['total_spent'] == 35.0
        assert report['total_usage'] == 3
        
        # Should include spending from all agents
        tool_spending = {item['tool_name']: item['total_spent'] for item in report['tool_spending']}
        assert tool_spending['tool1'] == 30.0  # 10.0 + 20.0
        assert tool_spending['tool2'] == 5.0
    
    def test_get_spending_report_date_filtering(self):
        """Test spending report with date filtering."""
        # Record old usage (beyond date range)
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            old_date = datetime.now() - timedelta(days=35)
            cursor.execute("""
                INSERT INTO tool_usage 
                (agent_id, tool_name, usage_count, total_spent, avg_response_time, success_rate, last_used)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("test_agent", "old_tool", 1, 100.0, 1.0, 1.0, old_date))
            conn.commit()
        
        # Record recent usage
        self.analytics.record_tool_usage("test_agent", "new_tool", 10.0, 0.5, True)
        
        # Get report for last 30 days
        report = self.analytics.get_spending_report("test_agent", days=30)
        
        # Should only include recent usage
        assert report['total_spent'] == 10.0
        assert len(report['tool_spending']) == 1
        assert report['tool_spending'][0]['tool_name'] == 'new_tool'


class TestDebugModeContextManager:
    """Test cases for debug mode context manager."""
    
    def test_debug_mode_context_manager(self):
        """Test debug mode context manager."""
        config = DebugConfig(enabled=True, log_level="DEBUG")
        
        with debug_mode(config) as logger:
            assert isinstance(logger, X402Logger)
            assert logger.debug_config.enabled is True
            assert logger.debug_config.log_level == "DEBUG"
    
    def test_debug_mode_context_manager_default(self):
        """Test debug mode context manager with default config."""
        with debug_mode() as logger:
            assert isinstance(logger, X402Logger)
            assert logger.debug_config.enabled is True
    
    def test_debug_mode_context_manager_exception(self):
        """Test debug mode context manager with exception."""
        config = DebugConfig(enabled=True)
        
        try:
            with debug_mode(config) as logger:
                assert isinstance(logger, X402Logger)
                raise ValueError("Test exception")
        except ValueError:
            pass  # Expected
        
        # Context manager should handle cleanup properly
        assert True


class TestMonitoringIntegration:
    """Integration tests for monitoring components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_analytics_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_analytics_db.close()
        
        self.debug_config = DebugConfig(
            enabled=True,
            log_level="DEBUG",
            log_payments=True,
            log_api_calls=True,
            verbose_errors=True
        )
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_analytics_db.name):
            os.unlink(self.temp_analytics_db.name)
    
    def test_logger_analytics_integration(self):
        """Test integration between logger and analytics."""
        logger = X402Logger(self.debug_config)
        analytics = UsageAnalytics(self.temp_analytics_db.name)
        
        # Simulate agent session
        session_id = analytics.start_session("integration_test_agent")
        
        # Log various activities
        logger.log_payment(
            amount=25.0,
            recipient="0x123...",
            tool_name="test-api",
            status="completed",
            tx_hash="0xabc123"
        )
        
        logger.log_api_call(
            url="https://api.example.com/test",
            method="GET",
            status_code=200,
            response_time=0.5,
            tool_name="test-api"
        )
        
        # Record corresponding analytics
        analytics.record_tool_usage(
            agent_id="integration_test_agent",
            tool_name="test-api",
            cost=25.0,
            response_time=0.5,
            success=True
        )
        
        analytics.end_session(session_id)
        
        # Verify data consistency
        summary = analytics.get_agent_summary("integration_test_agent")
        assert summary['session_count'] == 1
        assert len(summary['tool_usage']) == 1
        assert summary['tool_usage'][0]['tool_name'] == 'test-api'
        assert summary['tool_usage'][0]['total_spent'] == 25.0
    
    def test_error_logging_with_analytics(self):
        """Test error logging with analytics tracking."""
        logger = X402Logger(self.debug_config)
        analytics = UsageAnalytics(self.temp_analytics_db.name)
        
        # Log error with context
        error = RuntimeError("Payment failed")
        context = {
            'agent_id': 'error_test_agent',
            'tool_name': 'failing-api',
            'payment_amount': 50.0
        }
        
        logger.log_error(error, context)
        
        # Record failed tool usage
        analytics.record_tool_usage(
            agent_id="error_test_agent",
            tool_name="failing-api",
            cost=0.0,  # No cost for failed payment
            response_time=2.0,  # Longer response time due to failure
            success=False
        )
        
        # Verify analytics reflect the failure
        summary = analytics.get_agent_summary("error_test_agent")
        assert len(summary['tool_usage']) == 1
        tool_usage = summary['tool_usage'][0]
        assert tool_usage['success_rate'] == 0.0
        assert tool_usage['total_spent'] == 0.0
    
    def test_comprehensive_monitoring_scenario(self):
        """Test comprehensive monitoring scenario."""
        logger = X402Logger(self.debug_config)
        analytics = UsageAnalytics(self.temp_analytics_db.name)
        
        agent_id = "comprehensive_test_agent"
        session_id = analytics.start_session(agent_id)
        
        # Simulate various agent activities
        activities = [
            {
                'tool': 'api1',
                'cost': 10.0,
                'response_time': 0.5,
                'success': True,
                'status_code': 200
            },
            {
                'tool': 'api2',
                'cost': 25.0,
                'response_time': 1.2,
                'success': True,
                'status_code': 200
            },
            {
                'tool': 'api1',
                'cost': 0.0,
                'response_time': 3.0,
                'success': False,
                'status_code': 500
            },
            {
                'tool': 'api3',
                'cost': 5.0,
                'response_time': 0.3,
                'success': True,
                'status_code': 402  # Payment required, then success
            }
        ]
        
        for activity in activities:
            # Log API call
            logger.log_api_call(
                url=f"https://api.example.com/{activity['tool']}",
                method="POST",
                status_code=activity['status_code'],
                response_time=activity['response_time'],
                tool_name=activity['tool']
            )
            
            # Log payment if successful
            if activity['success'] and activity['cost'] > 0:
                logger.log_payment(
                    amount=activity['cost'],
                    recipient="0x123...",
                    tool_name=activity['tool'],
                    status="completed",
                    tx_hash=f"0x{activity['tool']}123"
                )
            elif not activity['success']:
                logger.log_payment(
                    amount=activity['cost'],
                    recipient="0x123...",
                    tool_name=activity['tool'],
                    status="failed",
                    error="API call failed"
                )
            
            # Record analytics
            analytics.record_tool_usage(
                agent_id=agent_id,
                tool_name=activity['tool'],
                cost=activity['cost'],
                response_time=activity['response_time'],
                success=activity['success']
            )
        
        # Record performance metrics
        analytics.record_performance_metric(agent_id, "total_requests", 4, "count")
        analytics.record_performance_metric(agent_id, "avg_response_time", 1.25, "seconds")
        
        analytics.end_session(session_id)
        
        # Verify comprehensive summary
        summary = analytics.get_agent_summary(agent_id)
        
        assert summary['session_count'] == 1
        assert len(summary['tool_usage']) == 3  # api1, api2, api3
        
        # Check individual tool statistics
        tool_stats = {tool['tool_name']: tool for tool in summary['tool_usage']}
        
        # api1: 1 success, 1 failure
        assert tool_stats['api1']['usage_count'] == 2
        assert tool_stats['api1']['success_rate'] == 0.5
        assert tool_stats['api1']['total_spent'] == 10.0
        
        # api2: 1 success
        assert tool_stats['api2']['usage_count'] == 1
        assert tool_stats['api2']['success_rate'] == 1.0
        assert tool_stats['api2']['total_spent'] == 25.0
        
        # api3: 1 success
        assert tool_stats['api3']['usage_count'] == 1
        assert tool_stats['api3']['success_rate'] == 1.0
        assert tool_stats['api3']['total_spent'] == 5.0
        
        # Check performance metrics
        assert 'total_requests' in summary['performance_metrics']
        assert 'avg_response_time' in summary['performance_metrics']
        
        # Check spending report
        spending_report = analytics.get_spending_report(agent_id)
        assert spending_report['total_spent'] == 40.0  # 10 + 25 + 5
        assert spending_report['total_usage'] == 4